#!/usr/bin/env python3
"""
Update Young Innovator workshop section:
1. "Young Innovator (Short Theme Course)" -> "Young Innovator"
2. Week 1 -> Week 1&2, Week 2 -> Week 3&4, Week 3 -> Week 5&6, Week 4 -> Week 7&8

USAGE:
  cd /Users/anies/Downloads/arc-site
  cp ~/Downloads/update_workshop_weeks.py .
  python3 update_workshop_weeks.py
"""
import re, subprocess, sys, pathlib

REPO = pathlib.Path.cwd()
TARGET = REPO / "index.html"

def sh(cmd):
    r = subprocess.run(cmd, cwd=REPO)
    if r.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        sys.exit(1)

def main():
    print("=== Update Young Innovator Workshop Section ===\n")

    if not TARGET.exists():
        print("ERROR: index.html not found. Run from /Users/anies/Downloads/arc-site")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8", errors="ignore")
    original = text
    changes = []

    # 1. Title change
    if "Young Innovator (Short Theme Course)" in text:
        text = text.replace(
            "Young Innovator (Short Theme Course)",
            "Young Innovator"
        )
        changes.append("Title: 'Young Innovator (Short Theme Course)' -> 'Young Innovator'")
    else:
        print("  ! Title string not found — may already be changed")

    # 2. Week label changes — target the specific badge divs
    week_map = [
        ('>Week 1</div>', '>Week 1&amp;2</div>'),
        ('>Week 2</div>', '>Week 3&amp;4</div>'),
        ('>Week 3</div>', '>Week 5&amp;6</div>'),
        ('>Week 4</div>', '>Week 7&amp;8</div>'),
    ]
    for old, new in week_map:
        count = text.count(old)
        if count == 0:
            print(f"  ! '{old}' not found — skipped")
            continue
        text = text.replace(old, new)
        changes.append(f"'{old}' -> '{new}' ({count} occurrence)")

    if text == original:
        print("\nNo changes made — strings not found. Check file structure.")
        sys.exit(1)

    TARGET.write_text(text, encoding="utf-8")

    print("Changes applied:")
    for c in changes:
        print(f"  - {c}")

    print("\nCommitting and pushing...")
    sh(["git", "add", "index.html"])
    sh(["git", "commit", "-m", "Update Young Innovator workshop title and week labels"])
    sh(["git", "push"])

    print("\n=== DONE ===")
    print("Live in ~1 minute. Hard refresh (Cmd+Shift+R) to see it.")

if __name__ == "__main__":
    main()
