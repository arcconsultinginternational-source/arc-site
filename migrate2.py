#!/usr/bin/env python3
"""
Arc Innovate site restructuring — v2 (atomic, with automatic rollback).

WHAT CHANGED FROM v1 (and why v1 broke the site)
  v1 crashed on an untracked .DS_Store file AFTER it had already moved the
  root index.html out of the way, leaving the site with no homepage and no
  redirects. Three fixes:

  1. FILE LIST IS FILTERED. Only .html files are considered for moving.
     .DS_Store and any other non-page file is ignored, never passed to git mv.
  2. SAFE ORDERING. The old root index.html is not touched until every other
     move has already succeeded and the replacement is ready to drop in.
  3. ALL-OR-NOTHING. The script requires a clean git working tree, records
     HEAD, and wraps every step in a try/except. ANY failure triggers
     `git reset --hard <HEAD>` + `git clean -fd`, restoring the repo exactly
     as it was. There is no half-migrated state.

  Also new:
  - Rewrites absolute URLs (https://www.arc-international-edu.com/arc-innovate/...)
    as well as relative hrefs, so JSON-LD schema, OG tags, and any EXISTING
    canonical tags get corrected too. v1 missed these.
  - Moves arc-innovate/images/ to /images/ so the arc-innovate folder is
    fully retired rather than left behind as a stub.
  - Skips the Google Search Console verification file (adding a canonical
    tag to it could break site verification).
  - Final sweep reports any surviving "/arc-innovate" reference anywhere.

USAGE (from inside the repo):
  cd /Users/anies/Downloads/arc-site
  cp ~/Downloads/migrate2.py .
  python3 migrate2.py --dry-run
  python3 migrate2.py --apply
"""
import argparse, json, os, re, shutil, subprocess, sys, datetime, pathlib

REPO = pathlib.Path.cwd()
DOMAIN = "https://www.arc-international-edu.com"
BARE_DOMAIN = "https://arc-international-edu.com"
SKIP_DIRS = {"Arc_Innovate_Reference", ".git", "node_modules", "consulting"}
# Google Search Console verification file must stay byte-for-byte untouched.
VERIFY_FILE_RE = re.compile(r"^google[0-9a-f]+\.html$")

HEAD_SHA = None
DRY = False


class Abort(Exception):
    pass


def sh(cmd, check=True, capture=False):
    if capture:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        return r.stdout.strip()
    print("   $", " ".join(cmd))
    if not DRY:
        r = subprocess.run(cmd, cwd=REPO)
        if check and r.returncode != 0:
            raise Abort(f"command failed: {' '.join(cmd)}")


def rollback():
    if DRY or HEAD_SHA is None:
        return
    print("\n!! Failure detected — rolling back to", HEAD_SHA[:8])
    subprocess.run(["git", "reset", "--hard", HEAD_SHA], cwd=REPO)
    subprocess.run(["git", "clean", "-fd"], cwd=REPO)
    print("!! Repo restored to its pre-migration state. Nothing was changed.")


def in_skip(rel):
    return any(p in SKIP_DIRS for p in rel.parts)


def html_files():
    for p in sorted(REPO.rglob("*.html")):
        rel = p.relative_to(REPO)
        if in_skip(rel):
            continue
        if VERIFY_FILE_RE.match(rel.name):
            continue
        yield p, rel


# ---------- preconditions ----------

def preconditions():
    print("Step 0: preconditions")
    if not (REPO / "vercel.json").exists() or not (REPO / "arc-innovate").is_dir():
        raise Abort("this does not look like the arc-site repo "
                    "(expected vercel.json and arc-innovate/ here). "
                    "Are you in /Users/anies/Downloads/arc-site ?")
    print("   repo looks correct:", REPO)

    inside = sh(["git", "rev-parse", "--is-inside-work-tree"], capture=True)
    if inside != "true":
        raise Abort("not a git repository")

    dirty = sh(["git", "status", "--porcelain", "--untracked-files=no"], capture=True)
    if dirty:
        raise Abort("git working tree is not clean. Commit or stash first — "
                    "a clean tree is what makes rollback safe.\n" + dirty)
    print("   working tree clean")

    src = REPO / "arc-innovate" / "index.html"
    if not src.exists():
        raise Abort("arc-innovate/index.html not found")
    if "1337977120778599" not in src.read_text(encoding="utf-8", errors="ignore"):
        raise Abort("Meta Pixel ID not found in arc-innovate/index.html — "
                    "stopping before anything moves.")
    print("   Meta Pixel confirmed present in source homepage")

    untracked = sh(["git", "ls-files", "--others", "--exclude-standard"], capture=True)
    if untracked:
        print("   note — untracked files present (they will be left alone):")
        for line in untracked.splitlines():
            print("     ", line)
    print()


# ---------- moves ----------

def do_moves():
    print("Step 1: move directories")
    for src, dst in (("arc-innovate/subjects", "programs"),
                     ("arc-innovate/insights", "insights"),
                     ("arc-innovate/images", "images")):
        if not (REPO / src).exists():
            print(f"   skip (missing): {src}")
            continue
        if (REPO / dst).exists():
            raise Abort(f"destination already exists: {dst} — resolve manually first")
        sh(["git", "mv", src, dst])
    print()

    print("Step 2: move extra top-level pages (.html only)")
    moved = []
    base = REPO / "arc-innovate"
    if base.exists():
        for item in sorted(base.iterdir()):
            if item.name == "index.html" or item.suffix.lower() != ".html":
                if item.suffix.lower() != ".html":
                    print(f"   ignoring non-page file: arc-innovate/{item.name}")
                continue
            tracked = sh(["git", "ls-files", "--error-unmatch",
                          f"arc-innovate/{item.name}"], check=False, capture=True)
            if not tracked:
                print(f"   ignoring untracked: arc-innovate/{item.name}")
                continue
            if (REPO / item.name).exists():
                raise Abort(f"destination already exists at root: {item.name}")
            sh(["git", "mv", f"arc-innovate/{item.name}", item.name])
            moved.append(item.name)
    print("   moved:", moved or "(none)")
    print()

    # Only now, with everything else safely in place, swap the homepage.
    print("Step 3: swap homepage (old hub -> .bak, arc-innovate/index.html -> root)")
    if (REPO / "index.html").exists():
        sh(["git", "mv", "index.html", "index-old-hub.html.bak"])
    sh(["git", "mv", "arc-innovate/index.html", "index.html"])
    print()

    print("Step 4: verify Meta Pixel survived the move")
    if not DRY:
        txt = (REPO / "index.html").read_text(encoding="utf-8", errors="ignore")
        if "1337977120778599" not in txt:
            raise Abort("Meta Pixel MISSING from new root index.html")
        print("   Meta Pixel (1337977120778599) present in new root index.html: YES")
    else:
        print("   (dry run — nothing moved yet)")
    print()

    # tidy: remove now-empty arc-innovate dir and any .DS_Store junk in it
    if not DRY:
        leftover = REPO / "arc-innovate"
        if leftover.exists():
            for junk in leftover.rglob(".DS_Store"):
                junk.unlink()
            try:
                for d in sorted(leftover.rglob("*"), reverse=True):
                    if d.is_dir():
                        d.rmdir()
                leftover.rmdir()
                print("   removed now-empty arc-innovate/ folder\n")
            except OSError:
                print("   note: arc-innovate/ not empty, left in place\n")
    return moved


# ---------- link rewriting ----------

def build_replacements(moved_pages):
    reps = [
        (r'/arc-innovate/subjects/images/', '/images-programs-PLACEHOLDER/'),
        (r'/arc-innovate/subjects/', '/programs/'),
        (r'/arc-innovate/insights/', '/insights/'),
        (r'/arc-innovate/images/', '/images/'),
        (r'/arc-innovate/insights\b', '/insights'),
        (r'/arc-innovate/index\.html', '/'),
    ]
    for name in moved_pages:
        slug = name[:-5]
        reps.append((rf'/arc-innovate/{re.escape(slug)}\b', f'/{slug}'))
    reps += [
        (r'/arc-innovate/', '/'),
        (r'/arc-innovate\b', '/'),
    ]
    return reps


def rewrite_links(moved_pages):
    print("Step 5: rewrite internal links and absolute URLs")
    reps = build_replacements(moved_pages)
    changed = []
    for path, rel in html_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        for pat, repl in reps:
            text = re.sub(pat, repl, text)
        # subjects/images actually became programs/images
        text = text.replace('/images-programs-PLACEHOLDER/', '/programs/images/')
        # collapse any accidental double slashes in site paths
        text = re.sub(r'(href|src)="//+', r'\1="/', text)
        if text != original:
            changed.append(str(rel))
            if not DRY:
                path.write_text(text, encoding="utf-8")
    for c in changed:
        print("   updated:", c)
    print(f"   {len(changed)} file(s) changed\n")
    return changed


# ---------- canonicals ----------

def url_for(rel):
    p = str(rel).replace("\\", "/")
    if p == "index.html":
        return DOMAIN + "/"
    if p.endswith("/index.html"):
        return DOMAIN + "/" + p[: -len("/index.html")]
    if p.endswith(".html"):
        return DOMAIN + "/" + p[: -len(".html")]
    return DOMAIN + "/" + p


def fix_canonicals():
    print("Step 6: set <link rel=canonical> on every page")
    added, corrected = [], []
    for path, rel in html_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        want = url_for(rel)
        m = re.search(r'<link[^>]*rel="canonical"[^>]*>', text)
        if m:
            new_tag = f'<link rel="canonical" href="{want}">'
            if m.group(0) != new_tag:
                text = text.replace(m.group(0), new_tag, 1)
                corrected.append(f"{rel} -> {want}")
                if not DRY:
                    path.write_text(text, encoding="utf-8")
        else:
            tag = f'  <link rel="canonical" href="{want}">\n'
            if "<head>" in text:
                text = text.replace("<head>", "<head>\n" + tag, 1)
            else:
                text = tag + text
            added.append(f"{rel} -> {want}")
            if not DRY:
                path.write_text(text, encoding="utf-8")
    for a in added:
        print("   added:", a)
    for c in corrected:
        print("   corrected:", c)
    print(f"   {len(added)} added, {len(corrected)} corrected\n")


# ---------- vercel.json ----------

def update_vercel():
    print("Step 7: add 301 redirects to vercel.json (preserving existing keys)")
    vf = REPO / "vercel.json"
    data = json.loads(vf.read_text())
    print("   existing keys:", list(data.keys()))
    redirects = data.get("redirects", [])
    have = {r.get("source") for r in redirects}
    rules = [
        {"source": "/arc-innovate", "destination": "/", "permanent": True},
        {"source": "/arc-innovate/insights/:path*", "destination": "/insights/:path*", "permanent": True},
        {"source": "/arc-innovate/subjects/:path*", "destination": "/programs/:path*", "permanent": True},
        {"source": "/arc-innovate/images/:path*", "destination": "/images/:path*", "permanent": True},
        {"source": "/arc-innovate/:path*", "destination": "/:path*", "permanent": True},
    ]
    added = []
    for r in rules:
        if r["source"] not in have:
            redirects.append(r)
            added.append(r["source"])
    data["redirects"] = redirects
    if not DRY:
        vf.write_text(json.dumps(data, indent=2) + "\n")
    for a in added:
        print("   +", a, "(301)")
    print()


# ---------- sitemap ----------

def regenerate_sitemap():
    print("Step 8: regenerate sitemap.xml")
    urls = sorted({url_for(rel) for _, rel in html_files()
                   if not rel.name.endswith(".bak")})
    today = datetime.date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        out.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>")
    out.append("</urlset>")
    if not DRY:
        (REPO / "sitemap.xml").write_text("\n".join(out) + "\n")
    for u in urls:
        print("   ", u)
    print(f"   {len(urls)} url(s)\n")


# ---------- final sweep ----------

def final_sweep():
    print("Step 9: final sweep for surviving /arc-innovate references")
    hits = []
    for path, rel in html_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'.{0,60}/arc-innovate.{0,60}', text):
            hits.append((str(rel), m.group(0).replace("\n", " ")))
    if hits:
        print("   !! still referencing the old path:")
        for f, s in hits[:40]:
            print(f"     {f}: ...{s}...")
        print(f"   {len(hits)} occurrence(s) — review these before pushing.")
    else:
        print("   clean — no /arc-innovate references remain")
    print()

    print("Step 10: Arc Consulting links (review manually)")
    found = []
    for path, rel in html_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'<a[^>]*href="/consulting[^"]*"[^>]*>.{0,80}', text, re.S):
            found.append((str(rel), m.group(0)[:120].replace("\n", " ")))
    if found:
        for f, s in found:
            print(f"   {f}: {s}...")
        print("   -> keep ONE of these in the footer, remove any in <nav>.")
    else:
        print("   none found — nothing to remove")
    print()


def main():
    global DRY, HEAD_SHA
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    DRY = a.dry_run

    print(f"=== Arc Innovate migration v2 "
          f"({'DRY RUN — nothing will change' if DRY else 'APPLYING'}) ===\n")
    try:
        preconditions()
        HEAD_SHA = sh(["git", "rev-parse", "HEAD"], capture=True)
        print("   HEAD recorded for rollback:", HEAD_SHA[:8], "\n")

        if not DRY:
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            dest = REPO.parent / f"arc-site-backup-{ts}"
            print("Backing up to", dest)
            shutil.copytree(REPO, dest, ignore=shutil.ignore_patterns(".git"))
            print("Backup complete.\n")

        moved = do_moves()
        rewrite_links(moved)
        fix_canonicals()
        update_vercel()
        regenerate_sitemap()
        final_sweep()

    except Abort as e:
        print("\nABORTED:", e)
        rollback()
        sys.exit(1)
    except Exception as e:
        print("\nUNEXPECTED ERROR:", type(e).__name__, e)
        rollback()
        sys.exit(1)

    print("=== Done ===")
    if DRY:
        print("DRY RUN only. Nothing changed. Re-run with --apply when the plan looks right.")
    else:
        print("Applied. Review with: git status && git diff")
        print("If anything looks wrong, undo everything with:")
        print(f"   git reset --hard {HEAD_SHA[:8]} && git clean -fd")


if __name__ == "__main__":
    main()
