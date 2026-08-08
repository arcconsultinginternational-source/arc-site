#!/usr/bin/env python3
"""
Four edits to the Thai homepage:
1. Hero H1 rewritten to focus on Design Thinking + 3D Printing for real-world
   problem solving (Thai)
2. Fix "2x per week" -> "1x per week" (once a week is correct)
3. Partners section H2 -> "Arc Innovate Partnership Program" (English, as given)
4. Unify all section headline (h2) font sizes -- fixes CSS gap where
   .section-alt headings (Programs, The Arc, Formats, About, Articles) were
   never getting the same font-size rule as .section headings

USAGE:
  cd /Users/anies/Downloads/arc-site
  cp ~/Downloads/fix_thai_homepage.py .
  python3 fix_thai_homepage.py
"""
import subprocess, sys, pathlib

REPO = pathlib.Path.cwd()
TARGET = REPO / "index.html"


def sh(cmd):
    r = subprocess.run(cmd, cwd=REPO)
    if r.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        sys.exit(1)


def main():
    print("=== Fix Thai Homepage (4 edits) ===\n")

    if not TARGET.exists():
        print("ERROR: index.html not found. Run from /Users/anies/Downloads/arc-site")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8", errors="ignore")
    original = text
    changes = []

    # 1. Hero H1 rewrite
    old_h1 = '<h1>\u0e40\u0e27\u0e34\u0e23\u0e4c\u0e01\u0e0a\u0e47\u0e2d\u0e1b\u0e2a\u0e23\u0e49\u0e32\u0e07\u0e2a\u0e23\u0e23\u0e04\u0e4c\u0e41\u0e25\u0e30\u0e04\u0e25\u0e32\u0e2a STEAM \u0e2a\u0e33\u0e2b\u0e23\u0e31\u0e1a\u0e19\u0e31\u0e01\u0e40\u0e23\u0e35\u0e22\u0e19\u0e43\u0e19\u0e01\u0e23\u0e38\u0e07\u0e40\u0e17\u0e1e\u0e2f</h1>'
    new_h1 = '<h1>Design Thinking \u0e41\u0e25\u0e30 3D Printing \u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e01\u0e32\u0e23\u0e41\u0e01\u0e49\u0e1b\u0e31\u0e0d\u0e2b\u0e32\u0e43\u0e19\u0e42\u0e25\u0e01\u0e08\u0e23\u0e34\u0e07 \u0e2a\u0e33\u0e2b\u0e23\u0e31\u0e1a\u0e19\u0e31\u0e01\u0e40\u0e23\u0e35\u0e22\u0e19\u0e43\u0e19\u0e01\u0e23\u0e38\u0e07\u0e40\u0e17\u0e1e\u0e2f</h1>'
    if old_h1 in text:
        text = text.replace(old_h1, new_h1)
        changes.append("Hero H1 -> Design Thinking + 3D Printing / real-world problem solving")
    else:
        print("  ! Hero H1 string not found -- may already differ")

    # 2. Fix weekly frequency: 2x -> 1x per week
    old_freq = '\u0e2a\u0e31\u0e1b\u0e14\u0e32\u0e2b\u0e4c\u0e25\u0e30 2 \u0e04\u0e23\u0e31\u0e49\u0e07 \u0e17\u0e38\u0e01\u0e04\u0e32\u0e1a\u0e40\u0e23\u0e35\u0e22\u0e19\u0e43\u0e0a\u0e49\u0e01\u0e23\u0e30\u0e1a\u0e27\u0e19\u0e01\u0e32\u0e23\u0e04\u0e34\u0e14\u0e40\u0e0a\u0e34\u0e07\u0e2d\u0e2d\u0e01\u0e41\u0e1a\u0e1a'
    new_freq = '\u0e2a\u0e31\u0e1b\u0e14\u0e32\u0e2b\u0e4c\u0e25\u0e30 1 \u0e04\u0e23\u0e31\u0e49\u0e07 \u0e17\u0e38\u0e01\u0e04\u0e32\u0e1a\u0e40\u0e23\u0e35\u0e22\u0e19\u0e43\u0e0a\u0e49\u0e01\u0e23\u0e30\u0e1a\u0e27\u0e19\u0e01\u0e32\u0e23\u0e04\u0e34\u0e14\u0e40\u0e0a\u0e34\u0e07\u0e2d\u0e2d\u0e01\u0e41\u0e1a\u0e1a'
    if old_freq in text:
        text = text.replace(old_freq, new_freq)
        changes.append("'2x per week' -> '1x per week' in program description")
    else:
        print("  ! Weekly frequency string not found -- may already differ")

    old_wk = '\u0e2a\u0e31\u0e1b\u0e14\u0e32\u0e2b\u0e4c\u0e25\u0e30 2 \u0e04\u0e23\u0e31\u0e49\u0e07 \u0e01\u0e25\u0e38\u0e48\u0e21\u0e40\u0e25\u0e47\u0e01\u0e44\u0e21\u0e48\u0e40\u0e01\u0e34\u0e19 10\u201312 \u0e04\u0e19'
    new_wk = '\u0e2a\u0e31\u0e1b\u0e14\u0e32\u0e2b\u0e4c\u0e25\u0e30 1 \u0e04\u0e23\u0e31\u0e49\u0e07 \u0e01\u0e25\u0e38\u0e48\u0e21\u0e40\u0e25\u0e47\u0e01\u0e44\u0e21\u0e48\u0e40\u0e01\u0e34\u0e19 10\u201312 \u0e04\u0e19'
    if old_wk in text:
        text = text.replace(old_wk, new_wk)
        changes.append("'2x per week' -> '1x per week' in Weekend Studio Classes card")

    # 3. Partners section H2
    old_partners = '<h2>\u0e19\u0e33 Arc Innovate \u0e44\u0e1b\u0e2a\u0e39\u0e48\u0e42\u0e23\u0e07\u0e40\u0e23\u0e35\u0e22\u0e19\u0e02\u0e2d\u0e07\u0e17\u0e48\u0e32\u0e19</h2>'
    new_partners = '<h2>Arc Innovate Partnership Program</h2>'
    if old_partners in text:
        text = text.replace(old_partners, new_partners)
        changes.append("Partners H2 -> 'Arc Innovate Partnership Program'")
    else:
        print("  ! Partners H2 string not found -- may already differ")

    # 4. Unify headline sizes
    old_css = '.section h2{font-size:2.2rem;margin-bottom:16px;line-height:1.2;}'
    new_css = '.section h2,.section-alt h2{font-size:2.2rem;margin-bottom:16px;line-height:1.2;}'
    if old_css in text:
        text = text.replace(old_css, new_css)
        changes.append("CSS: unified h2 font-size across .section AND .section-alt")
    else:
        print("  ! .section h2 CSS rule not found -- may already differ")

    if text == original:
        print("\nNo changes applied -- none of the target strings matched.")
        sys.exit(1)

    TARGET.write_text(text, encoding="utf-8")

    print("Changes applied:")
    for c in changes:
        print(f"  - {c}")

    print("\nCommitting and pushing...")
    sh(["git", "add", "index.html"])
    sh(["git", "commit", "-m", "Thai homepage: rewrite hero headline, fix weekly frequency, partnership heading, unify headline sizes"])
    sh(["git", "push"])

    print("\n=== DONE ===")
    print("Live in ~1 minute. Hard refresh (Cmd+Shift+R) to see it.")


if __name__ == "__main__":
    main()
