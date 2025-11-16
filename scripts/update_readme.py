#!/usr/bin/env python3
"""
README Screenshot Injection Script
Updates README.md with generated screenshot gallery
"""

import os
import re
from datetime import datetime

README_PATH = "README.md"
SCREENSHOTS_DIR = "docs/screenshots"

# Screenshot files in order
SCREENSHOTS = [
    ("front.png", "Front View"),
    ("back.png", "Back View"),
    ("face.png", "Face Detail (Mechanical Eye)"),
    ("pose1.png", "Emote: Mechanical Unfold"),
    ("pose2.png", "Emote: The Stare"),
]

def generate_screenshot_gallery():
    """Generate HTML/Markdown gallery for screenshots"""

    gallery_lines = [
        "<!-- AUTO-GENERATED-SCREENSHOTS -->",
        f"<!-- Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} -->",
        "",
    ]

    # Check which screenshots exist
    existing_screenshots = []
    for filename, caption in SCREENSHOTS:
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        if os.path.exists(filepath):
            existing_screenshots.append((filename, caption))
        else:
            print(f"Warning: Screenshot not found: {filepath}")

    if not existing_screenshots:
        gallery_lines.append("⚠️ *Screenshots are being generated... Check back after the build completes!*")
        gallery_lines.append("")
        gallery_lines.append("<!-- END-AUTO-GENERATED-SCREENSHOTS -->")
        return "\n".join(gallery_lines)

    # Create gallery table (2 columns)
    gallery_lines.append("| | |")
    gallery_lines.append("|:---:|:---:|")

    for i in range(0, len(existing_screenshots), 2):
        row_items = []

        for j in range(2):
            idx = i + j
            if idx < len(existing_screenshots):
                filename, caption = existing_screenshots[idx]
                img_path = f"docs/screenshots/{filename}"
                row_items.append(
                    f"**{caption}**<br/><img src=\"{img_path}\" alt=\"{caption}\" width=\"400\"/>"
                )
            else:
                row_items.append("")

        gallery_lines.append(f"| {row_items[0]} | {row_items[1] if len(row_items) > 1 else ''} |")

    gallery_lines.append("")
    gallery_lines.append("<!-- END-AUTO-GENERATED-SCREENSHOTS -->")

    return "\n".join(gallery_lines)

def update_readme():
    """Update README.md with generated gallery"""

    if not os.path.exists(README_PATH):
        print(f"Error: {README_PATH} not found!")
        return False

    # Read current README
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Generate new gallery
    new_gallery = generate_screenshot_gallery()

    # Replace content between markers
    pattern = r'<!-- AUTO-GENERATED-SCREENSHOTS -->.*?<!-- END-AUTO-GENERATED-SCREENSHOTS -->'

    if re.search(pattern, content, re.DOTALL):
        # Replace existing gallery
        updated_content = re.sub(pattern, new_gallery, content, flags=re.DOTALL)
        print("Updated existing screenshot gallery in README.md")
    else:
        print("Warning: Screenshot markers not found in README.md")
        print("Gallery was not inserted. Please add markers manually:")
        print("<!-- AUTO-GENERATED-SCREENSHOTS -->")
        print("<!-- END-AUTO-GENERATED-SCREENSHOTS -->")
        return False

    # Write updated README
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"README.md updated successfully!")
    print(f"Gallery contains {len([s for s in SCREENSHOTS if os.path.exists(os.path.join(SCREENSHOTS_DIR, s[0]))])} screenshots")

    return True

def main():
    print("=" * 60)
    print("README SCREENSHOT INJECTION")
    print("=" * 60)

    success = update_readme()

    if success:
        print("\n✅ README update complete!")
    else:
        print("\n❌ README update failed!")
        exit(1)

if __name__ == "__main__":
    main()
