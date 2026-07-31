#!/usr/bin/env python3
"""
Arc Innovate site restructuring migration script.

WHAT IT DOES
  1. Backs up the entire repo to a sibling folder before touching anything.
  2. Uses `git mv` to move files/folders (preserves git history AND means
     the Meta Pixel snippet inside arc-innovate/index.html <head> travels
     with the file automatically — nothing is retyped or reconstructed).
       arc-innovate/subjects/  -> programs/
       arc-innovate/insights/  -> insights/
       arc-innovate/index.html -> index.html   (old hub index.html backed
                                                  up as index-old-hub.html.bak)
       any other top-level file directly inside arc-innovate/ (e.g. the-arc.html,
       design-thinking-guide.html) -> moved to root with the same name
     arc-innovate/images/ is left exactly where it is — pages already
     reference it with an absolute path, so nothing breaks by leaving it.
  3. Rewrites href/src attributes across every .html file in the repo
     that pointed at the old /arc-innovate/... paths.
  4. Adds <link rel="canonical"> to every page (skips pages that already
     have one).
  5. Adds the three required 301 redirect rules to vercel.json (creates
     the file if missing, merges into it if present, does not remove any
     existing rules).
  6. Regenerates sitemap.xml from the files that actually exist post-move.
  7. Checks whether the Meta Pixel ID is present in the new root index.html
     and tells you plainly if it is not.
  8. Finds every place "/consulting" is linked from a <nav> or <li> so you
     can manually confirm what to remove — this one step is intentionally
     NOT automatic, because blindly regex-deleting nav markup is how sites
     end up with broken HTML. You review the short list and remove by hand,
     or paste it back to me and I'll do it precisely.
  9. Never touches /Arc_Innovate_Reference/.

USAGE (run from inside the repo folder):
  cd /Users/anies/Downloads/arc-site
  cp ~/Downloads/migrate.py .
  python3 migrate.py --dry-run      # shows every planned change, changes nothing
  python3 migrate.py --apply        # makes the changes for real (auto-backup first)

After --apply, review with `git status` / `git diff`, do the one manual
nav cleanup step it reports, then commit and push (commands printed at
the end).
"""
import argparse, json, re, shutil, subprocess, sys, datetime, pathlib

REPO = pathlib.Path.cwd()
DOMAIN = "https://www.arc-international-edu.com"
SKIP_DIRS = {"Arc_Innovate_Reference", ".git", "node_modules"}


def run(cmd, dry):
    print("  $", " ".join(cmd))
    if not dry:
        subprocess.run(cmd, check=True, cwd=REPO)


def in_skip_dir(path):
    return any(part in SKIP_DIRS for part in path.parts)


def backup():
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = REPO.parent / f"arc-site-backup-{ts}"
    print(f"Backing up repo to {dest} ...")
    shutil.copytree(REPO, dest, ignore=shutil.ignore_patterns(".git"))
    print("Backup complete.\n")
    return dest


def git_mv(src, dst, dry):
    src_p, dst_p = REPO / src, REPO / dst
    if not src_p.exists():
        print(f"  ! skip (not found): {src}")
        return False
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "mv", src, dst], dry)
    return True


def discover_top_level_pages():
    base = REPO / "arc-innovate"
    out = []
    if not base.exists():
        return out
    for item in sorted(base.iterdir()):
        if item.name in ("subjects", "insights", "images", "index.html"):
            continue
        out.append(item.name)
    return out


def apply_link_rewrites(dry):
    replacements = [
        (r'(href|src)="/arc-innovate/subjects/images/', r'\1="/programs/images/'),
        (r'(href|src)="/arc-innovate/subjects/', r'\1="/programs/'),
        (r'(href|src)="/arc-innovate/insights/', r'\1="/insights/'),
        (r'(href)="/arc-innovate/insights"', r'\1="/insights"'),
        (r'(href)="/arc-innovate/index\.html"', r'\1="/"'),
        (r'(href)="/arc-innovate/"', r'\1="/"'),
        (r'(href)="/arc-innovate"(?!/)', r'\1="/"'),
    ]
    changed = set()
    for path in REPO.rglob("*.html"):
        if in_skip_dir(path.relative_to(REPO)):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        for pattern, repl in replacements:
            text = re.sub(pattern, repl, text)
        if text != original:
            changed.add(str(path.relative_to(REPO)))
            if not dry:
                path.write_text(text, encoding="utf-8")
    return changed


def rewrite_extra_page_links(extra_pages, dry):
    reps = []
    for name in extra_pages:
        slug = name[:-5] if name.endswith(".html") else name
        reps.append((rf'(href)="/arc-innovate/{re.escape(slug)}', rf'\1="/{slug}'))
    changed = set()
    if not reps:
        return changed
    for path in REPO.rglob("*.html"):
        if in_skip_dir(path.relative_to(REPO)):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        for pattern, repl in reps:
            text = re.sub(pattern, repl, text)
        if text != original:
            changed.add(str(path.relative_to(REPO)))
            if not dry:
                path.write_text(text, encoding="utf-8")
    return changed


def url_for(rel_path):
    p = str(rel_path).replace("\\", "/")
    if p == "index.html":
        return DOMAIN + "/"
    if p.endswith("/index.html"):
        return DOMAIN + "/" + p[: -len("index.html")]
    if p.endswith(".html"):
        return DOMAIN + "/" + p[: -len(".html")]
    return DOMAIN + "/" + p


def add_canonicals(dry):
    changed = {}
    for path in REPO.rglob("*.html"):
        rel = path.relative_to(REPO)
        if in_skip_dir(rel) or "consulting" in rel.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if 'rel="canonical"' in text:
            continue
        url = url_for(rel)
        tag = f'<link rel="canonical" href="{url}">\n'
        if "<head>" in text:
            new_text = text.replace("<head>", "<head>\n" + tag, 1)
        else:
            new_text = tag + text
        changed[str(rel)] = url
        if not dry:
            path.write_text(new_text, encoding="utf-8")
    return changed


def update_vercel_json(dry):
    vf = REPO / "vercel.json"
    data = {}
    if vf.exists():
        data = json.loads(vf.read_text())
    redirects = data.get("redirects", [])
    existing = {r.get("source") for r in redirects}
    new_rules = [
        {"source": "/arc-innovate", "destination": "/", "permanent": True},
        {"source": "/arc-innovate/", "destination": "/", "permanent": True},
        {"source": "/arc-innovate/insights/:path*", "destination": "/insights/:path*", "permanent": True},
        {"source": "/arc-innovate/subjects/:path*", "destination": "/programs/:path*", "permanent": True},
    ]
    added = []
    for rule in new_rules:
        if rule["source"] not in existing:
            redirects.append(rule)
            added.append(rule["source"])
    data["redirects"] = redirects
    if not dry:
        vf.write_text(json.dumps(data, indent=2) + "\n")
    return added


def regenerate_sitemap(dry):
    urls = []
    for path in sorted(REPO.rglob("*.html")):
        rel = path.relative_to(REPO)
        if in_skip_dir(rel) or "consulting" in rel.parts:
            continue
        if rel.name.endswith(".bak"):
            continue
        urls.append(url_for(rel))
    urls = sorted(set(urls))
    today = datetime.date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>")
    lines.append("</urlset>")
    content = "\n".join(lines) + "\n"
    if not dry:
        (REPO / "sitemap.xml").write_text(content)
    return urls


def check_pixel():
    idx = REPO / "index.html"
    if not idx.exists():
        return None
    text = idx.read_text(encoding="utf-8", errors="ignore")
    return "1337977120778599" in text


def find_consulting_nav_refs():
    hits = []
    for path in REPO.rglob("*.html"):
        rel = path.relative_to(REPO)
        if in_skip_dir(rel):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'<(a|li)[^>]*href="/consulting[^"]*"[^>]*>.{0,120}', text, re.S):
            hits.append((str(rel), m.group(0)[:140].replace("\n", " ")))
    return hits


def main():
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true")
    grp.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    dry = args.dry_run

    print(f"=== Arc Innovate migration ({'DRY RUN — nothing will change' if dry else 'APPLYING'}) ===\n")

    if not dry:
        backup()

    print("Step 1: find extra top-level arc-innovate pages to move to root")
    extra_pages = discover_top_level_pages()
    print("  found:", extra_pages or "(none)", "\n")

    print("Step 2: move files/folders with git mv")
    if (REPO / "index.html").exists():
        run(["git", "mv", "index.html", "index-old-hub.html.bak"], dry)
    git_mv("arc-innovate/subjects", "programs", dry)
    git_mv("arc-innovate/insights", "insights", dry)
    for name in extra_pages:
        git_mv(f"arc-innovate/{name}", name, dry)
    git_mv("arc-innovate/index.html", "index.html", dry)
    print()

    print("Step 3: rewrite internal links across all .html files")
    changed1 = apply_link_rewrites(dry)
    changed2 = rewrite_extra_page_links(extra_pages, dry)
    all_changed = sorted(changed1 | changed2)
    for f in all_changed:
        print("  link-updated:", f)
    print(f"  total files with link updates: {len(all_changed)}\n")

    print("Step 4: add <link rel=canonical> to every page (skips consulting/)")
    canon = add_canonicals(dry)
    for f, u in canon.items():
        print(f"  canonical added: {f} -> {u}")
    print(f"  total pages with canonical added: {len(canon)}\n")

    print("Step 5: update vercel.json redirects")
    added = update_vercel_json(dry)
    print("  redirect rules added:", added or "(all already present)", "\n")

    print("Step 6: regenerate sitemap.xml (excludes /consulting)")
    urls = regenerate_sitemap(dry)
    print(f"  sitemap now lists {len(urls)} urls\n")

    print("Step 7: verify Meta Pixel in new root index.html")
    if dry:
        print("  (skipped in dry run — index.html hasn't moved yet)\n")
    else:
        ok = check_pixel()
        if ok is None:
            print("  !! root index.html not found — something went wrong in Step 2\n")
        else:
            print("  Meta Pixel (1337977120778599) present:", "YES ✓" if ok else "NO — STOP AND CHECK MANUALLY", "\n")

    print("Step 8: find Arc Consulting nav links for you to review manually")
    hits = find_consulting_nav_refs()
    if hits:
        for f, snippet in hits:
            print(f"  {f}: {snippet}...")
    else:
        print("  none found")
    print(f"  -> {len(hits)} match(es). Remove these from <nav>, keep exactly one in <footer>.\n")

    print("=== Done ===")
    if dry:
        print("This was a DRY RUN. Nothing was changed. Re-run with --apply to make it real.")
    else:
        print("Changes applied. A full backup of the pre-migration repo is next to this folder.")
        print("Next: `git status` / `git diff` to review, do the manual nav cleanup above,")
        print("then commit and push.")


if __name__ == "__main__":
    main()
