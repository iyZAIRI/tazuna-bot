#!/usr/bin/env python3
"""
Script to download item icons from GameTora.
Downloads icons with rate limiting to avoid overwhelming the server.
"""
import sys
import os
import time
import requests
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db_reader import MasterDBReader

# Configuration
ICON_BASE_URL = "https://gametora.com/images/umamusume/items/item_icon_{icon_id:05d}.png"
OUTPUT_DIR = "./data/item_icons"
DELAY_BETWEEN_DOWNLOADS = 1.5  # seconds (adjust as needed - 1.5s = ~40 per minute)
REQUEST_TIMEOUT = 10  # seconds
BATCH_SIZE = 50  # Download this many, then take a longer break
BATCH_DELAY = 5  # seconds - longer break after each batch

def download_item_icons(db_path: str = "./data/master.mdb", start_from: int = 0, max_item_id: int = 500):
    """
    Download item icons from GameTora.

    Args:
        db_path: Path to the master database
        start_from: Skip the first N items (useful for resuming)
        max_item_id: Maximum item ID to try downloading (default: 500)
    """
    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    # Connect to database to get item information
    db = MasterDBReader(db_path)
    if not db.connect():
        print("❌ Failed to connect to database")
        return

    # Try to get item names from text_data (category may vary)
    # Common item categories: 11, 21, 30, 34, 40, 51, 90, 91, 93, 94, 97, 100, 103, 150
    print("📊 Fetching item information from database...")

    # Get item IDs that appear in various tables
    item_ids = set()

    # From story_event_point_reward
    rewards = db.query("""
        SELECT DISTINCT item_id
        FROM story_event_point_reward
        WHERE item_id > 0
    """)
    for r in rewards:
        item_ids.add(r['item_id'])

    # From mission_data
    missions = db.query("""
        SELECT DISTINCT item_id
        FROM mission_data
        WHERE item_id > 0
    """)
    for m in missions:
        item_ids.add(m['item_id'])

    db.close()

    # Sort item IDs
    item_ids = sorted(item_ids)

    # Extend range to max_item_id if specified
    if max_item_id > 0:
        for i in range(1, max_item_id + 1):
            item_ids.append(i)
        item_ids = sorted(set(item_ids))

    if not item_ids:
        print("❌ No items found in database")
        return

    print(f"📊 Found {len(item_ids)} item IDs to check")
    print(f"💾 Saving to: {output_path.absolute()}")
    print(f"⏱️  Delay between downloads: {DELAY_BETWEEN_DOWNLOADS}s")
    print(f"📦 Batch size: {BATCH_SIZE} (then {BATCH_DELAY}s pause)")
    print()

    # Track statistics
    downloaded = 0
    skipped = 0
    failed = 0

    # Download icons
    for idx, item_id in enumerate(item_ids, 1):
        # Skip if resuming
        if idx <= start_from:
            skipped += 1
            continue

        # Check if already exists
        icon_filename = f"item_icon_{item_id:05d}.png"
        icon_path = output_path / icon_filename

        if icon_path.exists():
            print(f"[{idx}/{len(item_ids)}] ⏭️  Skip (exists): {icon_filename}")
            skipped += 1
            continue

        # Build URL
        url = ICON_BASE_URL.format(icon_id=item_id)

        print(f"[{idx}/{len(item_ids)}] 📥 Downloading item icon {item_id:05d}...")

        try:
            # Download with timeout
            response = requests.get(url, timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                # Save to file
                with open(icon_path, 'wb') as f:
                    f.write(response.content)
                print(f"    ✅ Saved: {icon_filename} ({len(response.content)} bytes)")
                downloaded += 1
            elif response.status_code == 404:
                print(f"    ⏭️  Not found (404) - item icon doesn't exist")
                failed += 1
            else:
                print(f"    ❌ Failed: HTTP {response.status_code}")
                failed += 1

        except requests.exceptions.Timeout:
            print(f"    ⏰ Timeout after {REQUEST_TIMEOUT}s")
            failed += 1

        except requests.exceptions.RequestException as e:
            print(f"    ❌ Error: {e}")
            failed += 1

        except Exception as e:
            print(f"    ❌ Unexpected error: {e}")
            failed += 1

        # Rate limiting
        if idx < len(item_ids):  # Don't delay after last one
            # Check if we should take a batch break
            if downloaded > 0 and downloaded % BATCH_SIZE == 0:
                print(f"\n⏸️  Batch complete ({downloaded} downloaded). Pausing for {BATCH_DELAY}s...\n")
                time.sleep(BATCH_DELAY)
            else:
                time.sleep(DELAY_BETWEEN_DOWNLOADS)

    # Summary
    print("\n" + "="*60)
    print("📊 Download Summary")
    print("="*60)
    print(f"✅ Downloaded: {downloaded}")
    print(f"⏭️  Skipped:    {skipped}")
    print(f"❌ Failed:     {failed}")
    print(f"📁 Total:      {len(item_ids)}")
    print(f"💾 Location:   {output_path.absolute()}")
    print("="*60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download item icons from GameTora")
    parser.add_argument(
        "--db",
        default="./data/master.mdb",
        help="Path to master database (default: ./data/master.mdb)"
    )
    parser.add_argument(
        "--start-from",
        type=int,
        default=0,
        help="Skip first N items (useful for resuming)"
    )
    parser.add_argument(
        "--max-id",
        type=int,
        default=500,
        help="Maximum item ID to try (default: 500)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Delay between downloads in seconds (default: 1.5)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of downloads per batch (default: 50)"
    )
    parser.add_argument(
        "--batch-delay",
        type=int,
        default=5,
        help="Delay between batches in seconds (default: 5)"
    )

    args = parser.parse_args()

    # Update configuration from arguments
    DELAY_BETWEEN_DOWNLOADS = args.delay
    BATCH_SIZE = args.batch_size
    BATCH_DELAY = args.batch_delay

    print("🎁 Item Icon Downloader")
    print("="*60)

    try:
        download_item_icons(args.db, args.start_from, args.max_id)
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user")
        print("💡 Tip: Use --start-from to resume from where you left off")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
