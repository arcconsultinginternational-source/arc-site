#!/usr/bin/env python3
"""
Add GA4 event tracking to every LINE button across the Arc Innovate site.

USAGE:
  cd /Users/anies/Downloads/arc-site
  cp ~/Downloads/track_line.py .
  python3 track_line.py
"""
import re, subprocess, sys, pathlib

REPO = pathlib.Path.cwd()
LINE_URL = "https://lin.ee/TQPIVik"
SKIP = {"Arc_Innovate_Reference", ".git", "consulting"}

def sh(cmd):
    r = subprocess.run(cmd, cwd=REPO)
    if r.returncode != 0:
        print("Command failed:", " ".join(cmd))
        sys.exit(1)

def guess_location(filepath, tag):
    rel = str(filepath)
    if "insights" in rel:
        return "article"
    if "programs" in rel:
        return "program_page"
    tag = tag.lower()
    if "book a spot" in tag:   return "workshop"
    if "#00b900" in tag:       return "hero"
    if "btn-line" in tag:      return "contact"
    if "forest-green" in tag:  return "faq"
    if "background:white" in tag and "deep-blue" in tag: return "about"
    return "page"

PATTERN = re.compile(r'<a\s[^>]*href="https://lin\.ee/TQPIVik"[^>]*>', re.S)

def process(fp):
    text = fp.read_text(encoding="utf-8", errors="ignore")
    if LINE_URL not in text:
        return 0
    original = text
    hits = [0]

    def rep(m):
        tag = m.group(0)
        if "gtag" in tag:
            return tag
        loc = guess_location(str(fp), tag)
        ev = 'gtag(\'event\',\'line_click\',{\'button_location\':\'' + loc + '\'})'
        end = tag.find('>')
        hits[0] += 1
        return tag[:end] + ' onclick="' + ev + '"' + tag[end:]

    new = PATTERN.sub(rep, text)
    if new != original:
        fp.write_text(new, encoding="utf-8")
    return hits[0]

def main():
    print("=== GA4 LINE Button Tracking ===\n")
    if not (REPO / "vercel.json").exists():
        print("ERROR: Run from /Users/anies/Downloads/arc-site")
        sys.exit(1)

    total_f, total_b = 0, 0
    for p in sorted(REPO.rglob("*.html")):
        rel = p.relative_to(REPO)
        if any(x in SKIP for x in rel.parts) or rel.name.endswith(".bak"):
            continue
        n = process(p)
        if n:
            print(f"  {rel} — {n} button(s)")
            total_f += 1
            total_b += n

    if total_b == 0:
        print("No untracked LINE buttons found.")
        sys.exit(0)

    print(f"\n{total_b} button(s) across {total_f} file(s) updated.")
    print("\nCommitting and pushing...")
    sh(["git", "add", "-A"])
    sh(["git", "commit", "-m", "Track LINE button clicks in GA4"])
    sh(["git", "push"])
    print("\n=== DONE ===")
    print("Open your site → click a LINE button → GA4 Realtime → see 'line_click' live")
    print("After a week: GA4 → Explore → Events → line_click → filter by button_location")

if __name__ == "__main__":
    main()
