#!/usr/bin/env python3
"""
Script to generate Discord emoji codes from emoji filenames.
Outputs text in format :emoji_name: that can be pasted to get emoji codes.
"""
import sys
import os
from pathlib import Path

def generate_emoji_codes(emoji_dir: str, output_file: str = None, per_line: int = 10):
    """
    Generate Discord emoji codes from emoji files.

    Args:
        emoji_dir: Directory containing emoji files
        output_file: Optional output file path. If None, prints to stdout
        per_line: Number of emojis per line (default: 10)
    """
    emoji_path = Path(emoji_dir)

    if not emoji_path.exists():
        print(f"❌ Directory not found: {emoji_dir}", file=sys.stderr)
        return False

    # Get all image files (png, jpg, jpeg, gif, webp)
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    emoji_files = []

    for ext in image_extensions:
        emoji_files.extend(emoji_path.glob(f'*{ext}'))

    if not emoji_files:
        print(f"❌ No emoji files found in {emoji_dir}", file=sys.stderr)
        return False

    # Sort by name
    emoji_files.sort()

    print(f"📊 Found {len(emoji_files)} emoji files")
    print(f"📁 Directory: {emoji_path.absolute()}")
    print()

    # Generate emoji codes
    emoji_codes = []
    for emoji_file in emoji_files:
        # Remove extension to get emoji name
        emoji_name = emoji_file.stem
        emoji_code = f":{emoji_name}:"
        emoji_codes.append(emoji_code)

    # Format output
    output_lines = []
    for i in range(0, len(emoji_codes), per_line):
        chunk = emoji_codes[i:i + per_line]
        output_lines.append(' '.join(chunk))

    output_text = '\n'.join(output_lines)

    # Output
    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            f.write(output_text)
        print(f"✅ Saved to: {output_path.absolute()}")
    else:
        print("=" * 80)
        print("DISCORD EMOJI CODES (Copy and paste this):")
        print("=" * 80)
        print()
        print(output_text)
        print()
        print("=" * 80)

    print(f"\n📋 Total: {len(emoji_codes)} emoji codes")
    return True


def generate_emoji_list(emoji_dir: str, output_file: str = None):
    """
    Generate a formatted list of emojis with their names.

    Args:
        emoji_dir: Directory containing emoji files
        output_file: Optional output file path
    """
    emoji_path = Path(emoji_dir)

    if not emoji_path.exists():
        print(f"❌ Directory not found: {emoji_dir}", file=sys.stderr)
        return False

    # Get all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    emoji_files = []

    for ext in image_extensions:
        emoji_files.extend(emoji_path.glob(f'*{ext}'))

    if not emoji_files:
        print(f"❌ No emoji files found in {emoji_dir}", file=sys.stderr)
        return False

    # Sort by name
    emoji_files.sort()

    # Generate list
    output_lines = []
    output_lines.append(f"# Emoji List ({len(emoji_files)} emojis)")
    output_lines.append("")

    for emoji_file in emoji_files:
        emoji_name = emoji_file.stem
        emoji_code = f":{emoji_name}:"
        output_lines.append(f"- {emoji_code} → `{emoji_name}` ({emoji_file.name})")

    output_text = '\n'.join(output_lines)

    # Output
    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            f.write(output_text)
        print(f"✅ Saved list to: {output_path.absolute()}")
    else:
        print(output_text)

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Discord emoji codes from emoji files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate emoji codes from a directory
  python scripts/generate_emoji_codes.py ./emojis

  # Save to file
  python scripts/generate_emoji_codes.py ./emojis -o emoji_codes.txt

  # Control emojis per line
  python scripts/generate_emoji_codes.py ./emojis --per-line 5

  # Generate a detailed list
  python scripts/generate_emoji_codes.py ./emojis --list
        """
    )

    parser.add_argument(
        "emoji_dir",
        help="Directory containing emoji files"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: print to stdout)"
    )
    parser.add_argument(
        "--per-line",
        type=int,
        default=10,
        help="Number of emoji codes per line (default: 10)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Generate a formatted list instead of compact codes"
    )

    args = parser.parse_args()

    try:
        if args.list:
            success = generate_emoji_list(args.emoji_dir, args.output)
        else:
            success = generate_emoji_codes(args.emoji_dir, args.output, args.per_line)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
