#!/usr/bin/env python3
"""
Script to download skill icons from GameTora.
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
ICON_BASE_URL = "https://gametora.com/images/umamusume/skill_icons/utx_ico_skill_{icon_id}.png"
OUTPUT_DIR = "./data/skill_icons"
DELAY_BETWEEN_DOWNLOADS = 1.5  # seconds (adjust as needed - 1.5s = ~40 per minute)
REQUEST_TIMEOUT = 10  # seconds
BATCH_SIZE = 50  # Download this many, then take a longer break
BATCH_DELAY = 5  # seconds - longer break after each batch

def download_skill_icons(db_path: str = "./data/master.mdb", start_from: int = 0):
    """
    Download all skill icons from the database.

    Args:
        db_path: Path to the master database
        start_from: Skip the first N skills (useful for resuming)
    """
    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    # Connect to database
    db = MasterDBReader(db_path)
    if not db.connect():
        print("❌ Failed to connect to database")
        return

    # Get all skills with icon_ids
    query = """
    SELECT DISTINCT
        s.id as skill_id,
        s.icon_id,
        t.text as skill_name
    FROM skill_data s
    LEFT JOIN text_data t ON t.category = 47 AND t.[index] = s.id
    WHERE s.icon_id > 0
    ORDER BY s.icon_id
    """

    skills = db.query(query)
    db.close()

    if not skills:
        print("❌ No skills found")
        return

    print(f"📊 Found {len(skills)} skills with icons")
    print(f"💾 Saving to: {output_path.absolute()}")
    print(f"⏱️  Delay between downloads: {DELAY_BETWEEN_DOWNLOADS}s")
    print(f"📦 Batch size: {BATCH_SIZE} (then {BATCH_DELAY}s pause)")
    print()

    # Track statistics
    downloaded = 0
    skipped = 0
    failed = 0

    # Group skills by icon_id (some skills share icons)
    icon_skills = {}
    for skill in skills:
        icon_id = skill['icon_id']
        if icon_id not in icon_skills:
            icon_skills[icon_id] = []
        icon_skills[icon_id].append(skill['skill_name'] or f"Skill {skill['skill_id']}")

    unique_icons = list(icon_skills.keys())
    print(f"🎨 {len(unique_icons)} unique icons to download\n")

    # Download icons
    for idx, icon_id in enumerate(unique_icons, 1):
        # Skip if resuming
        if idx <= start_from:
            skipped += 1
            continue

        # Check if already exists
        icon_filename = f"utx_ico_skill_{icon_id}.png"
        icon_path = output_path / icon_filename

        if icon_path.exists():
            print(f"[{idx}/{len(unique_icons)}] ⏭️  Skip (exists): {icon_filename}")
            skipped += 1
            continue

        # Build URL
        url = ICON_BASE_URL.format(icon_id=icon_id)

        # Show which skills use this icon
        skill_names = icon_skills[icon_id][:3]  # Show first 3
        skills_text = ", ".join(skill_names)
        if len(icon_skills[icon_id]) > 3:
            skills_text += f" (+{len(icon_skills[icon_id]) - 3} more)"

        print(f"[{idx}/{len(unique_icons)}] 📥 Downloading icon {icon_id}...")
        print(f"    Skills: {skills_text}")

        try:
            # Download with timeout
            response = requests.get(url, timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                # Save to file
                with open(icon_path, 'wb') as f:
                    f.write(response.content)
                print(f"    ✅ Saved: {icon_filename} ({len(response.content)} bytes)")
                downloaded += 1
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
        if idx < len(unique_icons):  # Don't delay after last one
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
    print(f"📁 Total:      {len(unique_icons)}")
    print(f"💾 Location:   {output_path.absolute()}")
    print("="*60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download skill icons from GameTora")
    parser.add_argument(
        "--db",
        default="./data/master.mdb",
        help="Path to master database (default: ./data/master.mdb)"
    )
    parser.add_argument(
        "--start-from",
        type=int,
        default=0,
        help="Skip first N icons (useful for resuming)"
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

    print("🎨 Skill Icon Downloader")
    print("="*60)

    try:
        download_skill_icons(args.db, args.start_from)
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user")
        print("💡 Tip: Use --start-from to resume from where you left off")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
