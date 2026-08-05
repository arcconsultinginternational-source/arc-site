#!/usr/bin/env python3
"""
Deploy the Thai 3D printing SEO article.
1. Copies the HTML file to insights/
2. Adds it to insights/index.html and insights/articles.html
3. Updates sitemap.xml
4. Commits and pushes

USAGE:
  cd /Users/anies/Downloads/arc-site
  cp ~/Downloads/3d-printing-kids-bangkok.html .
  cp ~/Downloads/deploy_article.py .
  python3 deploy_article.py
"""
import re, subprocess, sys, datetime, pathlib, shutil

REPO = pathlib.Path.cwd()
ARTICLE_SRC = REPO / "3d-printing-kids-bangkok.html"
ARTICLE_DST = REPO / "insights" / "3d-printing-kids-bangkok.html"
ARTICLE_URL = "/insights/3d-printing-kids-bangkok"
DOMAIN = "https://www.arc-international-edu.com"


def sh(cmd, check=True):
    r = subprocess.run(cmd, cwd=REPO)
    if check and r.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        sys.exit(1)


def add_article_card(filepath):
    """Insert new article card into insights index/articles pages."""
    p = pathlib.Path(filepath)
    if not p.exists():
        print(f"  skip (not found): {filepath}")
        return

    text = p.read_text(encoding="utf-8", errors="ignore")

    # Don't add twice
    if "3d-printing-kids-bangkok" in text:
        print(f"  already present: {filepath}")
        return

    new_card = '''
      <a href="/insights/3d-printing-kids-bangkok" class="card">
        <div class="card-img" style="background:linear-gradient(135deg,#2B6CB0,#3A8A4A);display:flex;align-items:center;justify-content:center;min-height:160px;">
          <span style="font-size:3rem;">🖨️</span>
        </div>
        <div class="card-body">
          <div class="card-tag">เรียน 3D Printing เด็ก · กรุงเทพ</div>
          <h3>3D Printing Isn't the Point. This Is.</h3>
          <p>พ่อแม่หลายคนคิดว่าลูกจะได้เรียน 3D printing แต่สิ่งที่ได้จริงๆ คือกระบวนการคิดแบบนักออกแบบที่ติดตัวไปตลอดชีวิต</p>
          <span class="read-more">อ่านเพิ่มเติม →</span>
        </div>
      </a>'''

    # Insert after the first existing .card or after the grid opens
    m = re.search(r'(<a\s+href="/insights/[^"]*"\s+class="card">)', text)
    if m:
        text = text.replace(m.group(0), new_card + "\n      " + m.group(0), 1)
    elif '<div class="grid">' in text:
        text = text.replace('<div class="grid">', '<div class="grid">' + new_card, 1)
    else:
        print(f"  ! Could not find insertion point in {filepath}")
        return

    p.write_text(text, encoding="utf-8")
    print(f"  updated: {filepath}")


def update_sitemap():
    sf = REPO / "sitemap.xml"
    if not sf.exists():
        return
    text = sf.read_text(encoding="utf-8", errors="ignore")
    new_url = f"{DOMAIN}{ARTICLE_URL}"
    if new_url in text:
        print("  sitemap already has this URL")
        return
    today = datetime.date.today().isoformat()
    entry = f"  <url><loc>{new_url}</loc><lastmod>{today}</lastmod></url>"
    text = text.replace("</urlset>", entry + "\n</urlset>")
    sf.write_text(text, encoding="utf-8")
    print("  sitemap.xml updated")


def main():
    print("=== Deploy Thai 3D Printing Article ===\n")

    # Check source file exists
    if not ARTICLE_SRC.exists():
        print(f"ERROR: {ARTICLE_SRC.name} not found in repo root.")
        print("Make sure you copied it: cp ~/Downloads/3d-printing-kids-bangkok.html .")
        sys.exit(1)

    # Copy to insights/
    shutil.copy2(ARTICLE_SRC, ARTICLE_DST)
    print(f"Copied to: {ARTICLE_DST.relative_to(REPO)}")

    # Remove temp file from root
    ARTICLE_SRC.unlink()
    print(f"Removed temp file from root")

    # Update index pages
    print("\nUpdating article indexes:")
    add_article_card(REPO / "insights" / "index.html")
    add_article_card(REPO / "insights" / "articles.html")

    # Update sitemap
    print("\nUpdating sitemap:")
    update_sitemap()

    # Commit and push
    print("\nCommitting and pushing...")
    sh(["git", "add", "-A"])
    sh(["git", "commit", "-m",
        "Add Thai SEO article: 3D printing kids Bangkok (เรียน 3D printing เด็ก)"])
    sh(["git", "push"])

    print("\n=== DONE ===")
    print(f"\nArticle live at:")
    print(f"  {DOMAIN}{ARTICLE_URL}")
    print("\nNEXT:")
    print("  1. Google Search Console → URL Inspection → Request Indexing")
    print(f"     {DOMAIN}{ARTICLE_URL}")
    print("  2. Share on LINE + Instagram @arc.innovate")
    print("  3. Use keyword 'เรียน 3D printing เด็ก กรุงเทพ' in your IG caption")


if __name__ == "__main__":
    main()
