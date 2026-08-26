#!/usr/bin/env python3
"""
Test script to validate config and file structure
Run this first before implementing the full extractor
# This is Run on Home - PI ONLY
"""

import os
import yaml
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_config(config_path="config/config.yaml"):
    """Test if config matches actual file structure"""
    logger.info("🔍 Testing configuration...")

    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    base_path = Path(config['video_sources']['base_path'])
    cameras = config['video_sources']['cameras']

    results = {
        'base_path_exists': False,
        'cameras_found': [],
        'cameras_missing': [],
        'video_files_found': 0,
        'video_extensions': config['processing']['video_extensions'],
        'errors': []
    }

    # Check base path
    if base_path.exists():
        results['base_path_exists'] = True
        logger.info(f"✅ Base path exists: {base_path}")
    else:
        results['errors'].append(f"Base path not found: {base_path}")
        logger.error(f"❌ Base path not found: {base_path}")
        logger.info("   Please update config with correct base_path")
        return results

    # Check each camera folder
    for cam in cameras:
        cam_path = base_path / cam['path']
        if cam_path.exists():
            results['cameras_found'].append(cam['name'])
            logger.info(f"✅ Camera found: {cam['name']}")

            # Check for video files
            video_files = []
            for ext in config['processing']['video_extensions']:
                video_files.extend(cam_path.glob(f'*{ext}'))

            if video_files:
                results['video_files_found'] += len(video_files)
                logger.info(f"   📹 Found {len(video_files)} video files in {cam['name']}")

                # Show sample file
                sample = video_files[0]
                size_mb = sample.stat().st_size / (1024 * 1024)
                logger.info(f"   Sample: {sample.name} ({size_mb:.1f}MB)")
            else:
                logger.warning(f"   ⚠️ No video files found in {cam['name']}")
        else:
            results['cameras_missing'].append(cam['name'])
            logger.warning(f"⚠️ Camera path not found: {cam['path']}")

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Base Path: {'✅' if results['base_path_exists'] else '❌'}")
    logger.info(f"Cameras found: {len(results['cameras_found'])}/8")
    logger.info(f"Video files: {results['video_files_found']}")
    logger.info(f"Missing cameras: {len(results['cameras_missing'])}")

    if results['errors']:
        logger.error(f"❌ Errors: {len(results['errors'])}")
        for error in results['errors']:
            logger.error(f"   - {error}")
    else:
        logger.info("✅ All checks passed!")

    # Save test results for reference
    results_file = Path("data/test_results/config_test.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, indent=2)

    return results


def test_status_file(status_file="/tmp/cam_recorder_status"):
    """Check if cam_recorder.py is running and writing status"""
    logger.info("\n" + "=" * 50)
    logger.info("🔍 Testing status file...")

    status_path = Path(status_file)
    if status_path.exists():
        logger.info(f"✅ Status file exists: {status_file}")

        try:
            with open(status_path, 'r') as f:
                content = f.read()
                # Try to parse as dict (it's stored as string representation)
                data = eval(content)

            logger.info(f"   Last update: {data.get('timestamp', 'Unknown')}")
            logger.info(f"   Cameras: {len(data.get('cameras', []))}")

            # Show first camera status
            if data.get('cameras'):
                cam = data['cameras'][0]
                logger.info(f"   Sample: {cam['name']} - {cam['status']}")
            return True
        except Exception as e:
            logger.error(f"❌ Error reading status file: {e}")
            return False
    else:
        logger.warning(f"⚠️ Status file not found: {status_file}")
        logger.info("   This is normal if cam_recorder.py is not running")
        return False


if __name__ == "__main__":
    # Run tests
    config_result = test_config()
    status_result = test_status_file()

    logger.info("\n" + "=" * 50)
    logger.info("✅ Test complete!")
    logger.info("=" * 50)

    if config_result['base_path_exists']:
        logger.info("➡️ Config looks good! Ready to implement metadata extractor.")
    else:
        logger.info("➡️ Please fix base_path in config.yaml first.")