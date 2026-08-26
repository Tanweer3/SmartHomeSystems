#!/usr/bin/env python3
"""
Simple test version of metadata extractor
Only uses OS stats, no ffprobe dependency
# This is Run on Home - PI ONLY
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def extract_basic_metadata(config_path="config/config.yaml"):
    """Extract basic metadata without ffprobe"""

    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    base_path = Path(config['video_sources']['base_path'])
    cameras = config['video_sources']['cameras']

    metadata_records = []
    stats = {'processed': 0, 'errors': 0, 'skipped': 0}

    for cam in cameras:
        cam_path = base_path / cam['path']
        if not cam_path.exists():
            logger.warning(f"Path not found: {cam_path}")
            continue

        # Get all mp4 files
        video_files = list(cam_path.glob("*.mp4"))
        logger.info(f"📹 Found {len(video_files)} files in {cam['name']}")

        # Process files from last 7 days
        cutoff = datetime.now() - timedelta(days=7)

        for video_file in video_files[:10]:  # Limit to 10 for testing
            try:
                # Check age
                mtime = datetime.fromtimestamp(video_file.stat().st_mtime)
                if mtime < cutoff:
                    stats['skipped'] += 1
                    continue

                # Basic metadata
                record = {
                    'camera_name': cam['name'],
                    'filename': video_file.name,
                    'file_path': str(video_file),
                    'file_size_bytes': video_file.stat().st_size,
                    'file_creation_time': datetime.fromtimestamp(
                        video_file.stat().st_ctime
                    ).isoformat(),
                    'file_modification_time': datetime.fromtimestamp(
                        video_file.stat().st_mtime
                    ).isoformat(),
                    'extraction_timestamp': datetime.now().isoformat(),
                    'file_exists': True,
                    'is_corrupt': video_file.stat().st_size < 1024,  # Simple check
                    'test_metadata': True  # Flag to identify test data
                }

                metadata_records.append(record)
                stats['processed'] += 1

            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error processing {video_file}: {e}")

    # Save test output
    output_dir = Path("data/test_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"test_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(metadata_records, f, indent=2)

    logger.info("\n" + "=" * 50)
    logger.info("📊 EXTRACTION TEST SUMMARY")
    logger.info("=" * 50)
    logger.info(f"✅ Processed: {stats['processed']}")
    logger.info(f"❌ Errors: {stats['errors']}")
    logger.info(f"⏭️  Skipped: {stats['skipped']}")
    logger.info(f"📁 Output: {output_file}")

    return metadata_records, stats


if __name__ == "__main__":
    # Run the test
    logger.info("🧪 Running metadata extractor test...")
    records, stats = extract_basic_metadata()

    if records:
        # Show first record as sample
        logger.info("\n📋 Sample record:")
        logger.info(json.dumps(records[0], indent=2))

        # Check if we need ffprobe
        if stats['processed'] > 0:
            logger.info("\n✅ Test successful! Ready for full ffprobe implementation.")
        else:
            logger.info("\n⚠️ No files processed. Check base_path and file age.")