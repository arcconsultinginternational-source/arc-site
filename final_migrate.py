#!/usr/bin/env python3
"""
ALL-IN-ONE Arc Innovate migration.
Recovers Meta Pixel → moves files → rewrites links → adds redirects →
fixes canonicals → regenerates sitemap → commits → pushes.

One command. Rolls back on any failure.

USAGE:
  cd /Users/anies/Downloads/arc-site
  cp ~/Downloads/final_migrate.py .
  python3 final_migrate.py
"""
import json, re, shutil, subprocess, sys, datetime, pathlib

REPO = pathlib.Path.cwd()
DOMAIN = "https://www.arc-international-edu.com"
PIXEL_ID = "1337977120778599"
SKIP_DIRS = {"Arc_Innovate_Reference", ".git", "node_modules", "consulting"}
VERIFY_RE = re.compile(r"^google[0-9a-f]+\.html$")
HEAD = None


class Abort(Exception):
    pass


def sh(cmd, check=True, capture=False):
    if capture:
        return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True).stdout.strip()
    r = subprocess.run(cmd, cwd=REPO)
    if check and r.returncode != 0:
        raise Abort(f"Command failed: {' '.join(cmd)}")


def rollback():
    if HEAD:
        print(f"\n!! Rolling back to {HEAD[:8]}")
        subprocess.run(["git", "reset", "--hard", HEAD], cwd=REPO)
        subprocess.run(["git", "clean", "-fd"], cwd=REPO)
        print("!! Restored. Nothing was changed.\n")


def skip(rel):
    return any(p in SKIP_DIRS for p in rel.parts)


def htmls(exclude_target=None):
    for p in sorted(REPO.rglob("*.html")):
        rel = p.relative_to(REPO)
        if skip(rel) or VERIFY_RE.match(rel.name) or rel.name.endswith(".bak"):
            continue
        if exclude_target and p == exclude_target:
            continue
        yield p, rel


def url_for(rel):
    p = str(rel).replace("\\", "/")
    if p == "index.html":
        return DOMAIN + "/"
    if p.endswith("/index.html"):
        return DOMAIN + "/" + p[:-len("/index.html")]
    if p.endswith(".html"):
        return DOMAIN + "/" + p[:-len(".html")]
    return DOMAIN + "/" + p


# ── STEP 0: PRECONDITIONS ──

def step0():
    global HEAD
    print("Step 0: Preconditions")

    if not (REPO / "vercel.json").exists() or not (REPO / "arc-innovate").is_dir():
        raise Abort("Not the right repo. Run from /Users/anies/Downloads/arc-site")

    if sh(["git", "rev-parse", "--is-inside-work-tree"], capture=True) != "true":
        raise Abort("Not a git repo")

    dirty = sh(["git", "status", "--porcelain", "--untracked-files=no"], capture=True)
    if dirty:
        raise Abort(f"Working tree not clean. Commit or stash first.\n{dirty}")

    HEAD = sh(["git", "rev-parse", "HEAD"], capture=True)
    print(f"   HEAD: {HEAD[:8]} (rollback target)")

    src = REPO / "arc-innovate" / "index.html"
    if not src.exists():
        raise Abort("arc-innovate/index.html not found")

    # Clean leftover empty dirs from previous attempts
    for d in ("programs", "insights"):
        dp = REPO / d
        if dp.exists():
            try:
                for junk in dp.rglob(".DS_Store"):
                    junk.unlink()
                shutil.rmtree(dp)
                print(f"   cleaned leftover {d}/")
            except Exception as e:
                raise Abort(f"Can't clean leftover {d}/: {e}")

    print("   OK\n")


# ── STEP 1: RECOVER META PIXEL ──

def step1():
    print("Step 1: Recover Meta Pixel")
    target = REPO / "arc-innovate" / "index.html"
    text = target.read_text(encoding="utf-8", errors="ignore")

    if PIXEL_ID in text:
        print("   Already present — skip\n")
        return

    # Find it on another page
    snippet = None
    source = None
    for p, rel in htmls(exclude_target=target):
        t = p.read_text(encoding="utf-8", errors="ignore")
        if PIXEL_ID not in t:
            continue
        m = re.search(
            r'<!--\s*Meta Pixel Code\s*-->.*?<!--\s*End Meta Pixel Code\s*-->',
            t, re.S | re.I)
        if m:
            snippet, source = m.group(0), str(rel)
            break
        m = re.search(
            r'<script\b[^>]*>(?:(?!</script>).)*?fbq\([^)]*\)(?:(?!</script>).)*?</script>'
            r'(\s*<noscript>.*?</noscript>)?',
            t, re.S | re.I)
        if m and PIXEL_ID in m.group(0):
            snippet, source = m.group(0), str(rel)
            break

    if not snippet:
        # Try backup
        backups = sorted((REPO.parent).glob("arc-site-backup-*"))
        for bk in backups:
            bf = bk / "arc-innovate" / "index.html"
            if bf.exists():
                bt = bf.read_text(encoding="utf-8", errors="ignore")
                if PIXEL_ID in bt:
                    m = re.search(
                        r'<!--\s*Meta Pixel Code\s*-->.*?<!--\s*End Meta Pixel Code\s*-->',
                        bt, re.S | re.I)
                    if m:
                        snippet, source = m.group(0), f"backup:{bf}"
                        break
                    m = re.search(
                        r'<script\b[^>]*>(?:(?!</script>).)*?fbq\([^)]*\)(?:(?!</script>).)*?</script>'
                        r'(\s*<noscript>.*?</noscript>)?',
                        bt, re.S | re.I)
                    if m and PIXEL_ID in m.group(0):
                        snippet, source = m.group(0), f"backup:{bf}"
                        break

    if not snippet:
        # Last resort: check git history
        old_text = sh(["git", "show", "HEAD~5:arc-innovate/index.html"], capture=True)
        if old_text and PIXEL_ID in old_text:
            m = re.search(
                r'<!--\s*Meta Pixel Code\s*-->.*?<!--\s*End Meta Pixel Code\s*-->',
                old_text, re.S | re.I)
            if m:
                snippet, source = m.group(0), "git history (HEAD~5)"
            else:
                m = re.search(
                    r'<script\b[^>]*>(?:(?!</script>).)*?fbq\([^)]*\)(?:(?!</script>).)*?</script>'
                    r'(\s*<noscript>.*?</noscript>)?',
                    old_text, re.S | re.I)
                if m and PIXEL_ID in m.group(0):
                    snippet, source = m.group(0), "git history (HEAD~5)"

    if not snippet:
        raise Abort("Cannot find Meta Pixel snippet anywhere — pages, backups, or git history.")

    print(f"   Found pixel in: {source}")
    block = "\n" + snippet.strip() + "\n"
    if "</head>" in text:
        text = text.replace("</head>", block + "</head>", 1)
    elif "<head>" in text:
        text = text.replace("<head>", "<head>" + block, 1)
    else:
        text = block + text

    target.write_text(text, encoding="utf-8")
    if PIXEL_ID not in target.read_text(encoding="utf-8", errors="ignore"):
        raise Abort("Pixel insertion failed — not found after write")
    print("   Pixel recovered and inserted\n")


# ── STEP 2: MOVE FILES ──

def step2():
    print("Step 2: Move files with git mv")

    for src, dst in [("arc-innovate/subjects", "programs"),
                     ("arc-innovate/insights", "insights"),
                     ("arc-innovate/images", "images")]:
        sp = REPO / src
        dp = REPO / dst
        if not sp.exists():
            print(f"   skip (missing): {src}")
            continue
        if dp.exists():
            raise Abort(f"Destination {dst}/ already exists — clean it first")
        sh(["git", "mv", src, dst])

    moved_pages = []
    base = REPO / "arc-innovate"
    if base.exists():
        for item in sorted(base.iterdir()):
            if item.name == "index.html" or item.suffix.lower() != ".html":
                continue
            tracked = sh(["git", "ls-files", "--error-unmatch",
                          f"arc-innovate/{item.name}"], check=False, capture=True)
            if not tracked:
                continue
            if (REPO / item.name).exists():
                raise Abort(f"Root file {item.name} already exists")
            sh(["git", "mv", f"arc-innovate/{item.name}", item.name])
            moved_pages.append(item.name)

    print(f"   Extra pages moved: {moved_pages or '(none)'}")

    # Swap homepage LAST (safe ordering)
    if (REPO / "index.html").exists():
        sh(["git", "mv", "index.html", "index-old-hub.html.bak"])
    sh(["git", "mv", "arc-innovate/index.html", "index.html"])

    # Verify pixel survived
    if PIXEL_ID not in (REPO / "index.html").read_text(encoding="utf-8", errors="ignore"):
        raise Abort("Meta Pixel MISSING after homepage move")
    print("   Meta Pixel confirmed in new root index.html: YES")

    # Clean empty arc-innovate/
    leftover = REPO / "arc-innovate"
    if leftover.exists():
        for junk in leftover.rglob(".DS_Store"):
            junk.unlink()
        try:
            for d in sorted(leftover.rglob("*"), reverse=True):
                if d.is_dir():
                    d.rmdir()
            leftover.rmdir()
            print("   Removed empty arc-innovate/")
        except OSError:
            remaining = [str(p.relative_to(REPO)) for p in leftover.rglob("*") if not p.name.startswith(".")]
            print(f"   arc-innovate/ not empty, left in place: {remaining[:10]}")

    print()
    return moved_pages


# ── STEP 3: REWRITE LINKS ──

def step3(moved_pages):
    print("Step 3: Rewrite all internal links")

    reps = [
        (r'/arc-innovate/subjects/images/', '/programs/images/'),
        (r'/arc-innovate/subjects/', '/programs/'),
        (r'/arc-innovate/insights/', '/insights/'),
        (r'/arc-innovate/images/', '/images/'),
        (r'/arc-innovate/insights\b', '/insights'),
        (r'/arc-innovate/index\.html', '/'),
    ]
    for name in moved_pages:
        slug = name[:-5] if name.endswith(".html") else name
        reps.append((rf'/arc-innovate/{re.escape(slug)}\b', f'/{slug}'))
    reps += [
        (r'/arc-innovate/', '/'),
        (r'/arc-innovate\b', '/'),
    ]

    changed = []
    for p, rel in htmls():
        text = p.read_text(encoding="utf-8", errors="ignore")
        orig = text
        for pat, repl in reps:
            text = re.sub(pat, repl, text)
        text = re.sub(r'(href|src)="//+', r'\1="/', text)
        if text != orig:
            p.write_text(text, encoding="utf-8")
            changed.append(str(rel))

    for c in changed:
        print(f"   {c}")
    print(f"   {len(changed)} file(s) updated\n")


# ── STEP 4: CANONICALS ──

def step4():
    print("Step 4: Fix canonical tags")
    count = 0
    for p, rel in htmls():
        text = p.read_text(encoding="utf-8", errors="ignore")
        want = url_for(rel)
        new_tag = f'<link rel="canonical" href="{want}">'
        m = re.search(r'<link[^>]*rel="canonical"[^>]*>', text)
        if m:
            if m.group(0) != new_tag:
                text = text.replace(m.group(0), new_tag, 1)
                p.write_text(text, encoding="utf-8")
                count += 1
        else:
            tag = f'  {new_tag}\n'
            if "<head>" in text:
                text = text.replace("<head>", "<head>\n" + tag, 1)
            else:
                text = tag + text
            p.write_text(text, encoding="utf-8")
            count += 1
    print(f"   {count} pages updated\n")


# ── STEP 5: VERCEL REDIRECTS ──

def step5():
    print("Step 5: Add 301 redirects to vercel.json")
    vf = REPO / "vercel.json"
    data = json.loads(vf.read_text())
    redirects = data.get("redirects", [])
    have = {r.get("source") for r in redirects}
    rules = [
        {"source": "/arc-innovate", "destination": "/", "permanent": True},
        {"source": "/arc-innovate/insights/:path*", "destination": "/insights/:path*", "permanent": True},
        {"source": "/arc-innovate/subjects/:path*", "destination": "/programs/:path*", "permanent": True},
        {"source": "/arc-innovate/images/:path*", "destination": "/images/:path*", "permanent": True},
        {"source": "/arc-innovate/:path*", "destination": "/:path*", "permanent": True},
    ]
    added = 0
    for r in rules:
        if r["source"] not in have:
            redirects.append(r)
            added += 1
    data["redirects"] = redirects
    vf.write_text(json.dumps(data, indent=2) + "\n")
    print(f"   {added} redirect rules added\n")


# ── STEP 6: SITEMAP ──

def step6():
    print("Step 6: Regenerate sitemap.xml")
    urls = sorted({url_for(rel) for _, rel in htmls()})
    today = datetime.date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        out.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>")
    out.append("</urlset>")
    (REPO / "sitemap.xml").write_text("\n".join(out) + "\n")
    print(f"   {len(urls)} URLs\n")


# ── STEP 7: FINAL SWEEP ──

def step7():
    print("Step 7: Final sweep for /arc-innovate references")
    hits = []
    for p, rel in htmls():
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'/arc-innovate(?!/images)', text):
            ctx = text[max(0, m.start()-30):m.end()+30].replace("\n", " ")
            hits.append((str(rel), ctx))
    if hits:
        print("   !! Still referencing old paths:")
        for f, s in hits[:20]:
            print(f"     {f}: ...{s}...")
    else:
        print("   Clean — no old references remain")
    print()


# ── STEP 8: COMMIT + PUSH ──

def step8():
    print("Step 8: Commit and push")
    sh(["git", "add", "-A"])
    sh(["git", "commit", "-m", "Restructure: Arc Innovate becomes root site"])

    stat = sh(["git", "show", "--stat", "HEAD"], capture=True)
    lines = [l for l in stat.split("\n") if "file" in l.lower() or "changed" in l.lower()]
    for l in lines:
        print(f"   {l.strip()}")

    if PIXEL_ID not in (REPO / "index.html").read_text(encoding="utf-8", errors="ignore"):
        raise Abort("Meta Pixel missing in final commit — aborting push")
    print("   Meta Pixel confirmed: YES")

    sh(["git", "push"])
    print("   Pushed to GitHub — Vercel will auto-deploy\n")


# ── STEP 9: VERIFY LIVE ──

def step9():
    print("Step 9: Verify live site (wait ~60s for Vercel)")
    import time
    print("   Waiting 60 seconds for deployment...")
    time.sleep(60)

    checks = [
        ("/", "root"),
        ("/arc-innovate", "redirect"),
        ("/programs/3d-printing", "program"),
        ("/insights", "insights"),
    ]
    all_ok = True
    for path, label in checks:
        code = sh(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                    f"{DOMAIN}{path}"], capture=True)
        status = "OK" if code in ("200", "301", "308") else "FAIL"
        if status == "FAIL":
            all_ok = False
        print(f"   {label:12s} {path:40s} {code} {status}")

    print()
    if all_ok:
        print("=== ALL GOOD ===")
        print("NEXT: Go to Google Search Console:")
        print("  1. Sitemaps → Resubmit sitemap.xml")
        print("  2. URL Inspection → Request Indexing for https://www.arc-international-edu.com/")
    else:
        print("!! Some checks failed. Check Vercel dashboard → Deployments → Build Logs")


# ── MAIN ──

def main():
    print("=" * 60)
    print("  ARC INNOVATE — FULL SITE RESTRUCTURE")
    print("  One script. Automatic rollback on any failure.")
    print("=" * 60 + "\n")

    try:
        step0()

        # Backup
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = REPO.parent / f"arc-site-backup-{ts}"
        print(f"Backing up to {dest}")
        shutil.copytree(REPO, dest, ignore=shutil.ignore_patterns(".git"))
        print("Backup complete.\n")

        step1()  # Recover pixel
        step2_pages = step2()  # Move files
        step3(step2_pages)  # Rewrite links
        step4()  # Canonicals
        step5()  # Redirects
        step6()  # Sitemap
        step7()  # Final sweep
        step8()  # Commit + push
        step9()  # Verify

    except Abort as e:
        print(f"\nABORTED: {e}")
        rollback()
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {type(e).__name__}: {e}")
        rollback()
        sys.exit(1)


if __name__ == "__main__":
    main()
