#!/usr/bin/env python3
"""
Rewrite meta tags across the Arc Innovate site for parent-intent SEO.
Preserves schema.org markup and Meta Pixel. Commits and pushes.

USAGE:
  cd /Users/anies/Downloads/arc-site
  cp ~/Downloads/seo_rewrite.py .
  python3 seo_rewrite.py
"""
import re, json, subprocess, sys, pathlib

REPO = pathlib.Path.cwd()
DOMAIN = "https://www.arc-international-edu.com"
PIXEL_ID = "1337977120778599"
HEAD = None

# ── PAGE DEFINITIONS ──
# Each entry: (file_path, title, description, h1, og_image_path_or_None)
# og_image defaults to /images/design-thinking-camp-cover.jpg if None

DEFAULT_OG_IMAGE = "/images/design-thinking-camp-cover.jpg"

PAGES = {
    # HOMEPAGE
    "index.html": {
        "title": "Kids' Creative Workshops & STEAM Classes Bangkok | Arc Innovate",
        "desc": "Hands-on creative workshops for children ages 4\u201314 in Bangkok. Design thinking, 3D printing and STEAM classes that build the skills AI can\u2019t replace.",
        "h1": "Creative Workshops & STEAM Classes for Kids in Bangkok",
        "og_image": DEFAULT_OG_IMAGE,
    },

    # PROGRAM PAGES
    "programs/3d-printing.html": {
        "title": "3D Printing Workshop for Kids Bangkok | Arc Innovate",
        "desc": "A hands-on 3D printing workshop for children ages 7\u201314 in Sathorn, Bangkok. Kids design and print their own creation to take home. No experience needed.",
        "h1": "3D Printing Workshop for Kids in Bangkok",
        "og_image": "/programs/images/ux-ui-for-kids.jpg",
    },
    "programs/experimental-arts-and-design.html": {
        "title": "Creative Arts Classes for Kids Ages 4\u20137 Bangkok | Arc Innovate",
        "desc": "Hands-on arts and design workshops for young children ages 4\u20137 in Bangkok. Sensory exploration, open-ended making and early creative thinking skills.",
        "h1": "Creative Arts & Design Classes for Kids Ages 4\u20137",
        "og_image": "/programs/images/experimental-arts.jpg",
    },
    "programs/young-innovators.html": {
        "title": "Young Innovator Program for Kids Bangkok | Arc Innovate",
        "desc": "Design thinking and 3D printing program for children ages 7\u201314 in Bangkok. Kids solve real problems and build working prototypes. Small classes, big ideas.",
        "h1": "Young Innovator Program for Kids in Bangkok",
        "og_image": "/programs/images/young-innovator.jpg",
    },
    "programs/young-innovator.html": {
        "title": "Young Innovator Program for Kids Bangkok | Arc Innovate",
        "desc": "Design thinking and 3D printing program for children ages 7\u201314 in Bangkok. Kids solve real problems and build working prototypes. Small classes, big ideas.",
        "h1": "Young Innovator Program for Kids in Bangkok",
        "og_image": "/programs/images/young-innovator.jpg",
    },
    "programs/creative-inspire.html": {
        "title": "Creative Inspiration Workshops for Kids Bangkok | Arc Innovate",
        "desc": "Creative inspiration workshops for children ages 7\u201314 in Bangkok. Kids explore ideas through hands-on projects that spark curiosity and original thinking.",
        "h1": "Creative Inspiration Workshops for Kids in Bangkok",
        "og_image": DEFAULT_OG_IMAGE,
    },
    "programs/insight-and-questioning.html": {
        "title": "Critical Thinking Classes for Kids Bangkok | Arc Innovate",
        "desc": "Critical thinking and questioning workshops for children ages 7\u201314 in Bangkok. Kids learn to ask better questions, challenge assumptions and think deeper.",
        "h1": "Critical Thinking & Questioning Classes for Kids",
        "og_image": DEFAULT_OG_IMAGE,
    },
    "programs/tech-talk.html": {
        "title": "Kids Tech & Innovation Classes Bangkok | Arc Innovate",
        "desc": "Tech and innovation classes for children ages 7\u201314 in Bangkok. Kids explore emerging technology through hands-on projects and design thinking.",
        "h1": "Tech & Innovation Classes for Kids in Bangkok",
        "og_image": DEFAULT_OG_IMAGE,
    },

    # THE ARC (curriculum page)
    "the-arc.html": {
        "title": "Children\u2019s Creative Curriculum Ages 4\u201314 Bangkok | Arc Innovate",
        "desc": "A structured 3-level creative curriculum for kids ages 4\u201314 in Bangkok. From early making to advanced design thinking and 3D printing.",
        "h1": "The Arc \u2014 Creative Curriculum for Kids Ages 4\u201314",
        "og_image": DEFAULT_OG_IMAGE,
    },

    # DESIGN THINKING GUIDE
    "design-thinking-guide.html": {
        "title": "Design Thinking Classes for Kids Bangkok | Arc Innovate",
        "desc": "Design thinking courses for children ages 4\u201314 in Bangkok. Kids learn to solve real problems through hands-on creative projects. Small bilingual classes.",
        "h1": "Design Thinking Classes for Kids in Bangkok",
        "og_image": DEFAULT_OG_IMAGE,
    },

    # INSIGHTS (blog index)
    "insights/index.html": {
        "title": "Kids Activities & STEAM Learning Tips Bangkok | Arc Innovate",
        "desc": "Ideas and insights for Bangkok parents looking for creative kids activities, STEAM classes and after-school workshops. Real stories from Arc Innovate.",
        "h1": "Ideas Worth Reading",
        "og_image": DEFAULT_OG_IMAGE,
    },
    "insights/articles.html": {
        "title": "Kids Activities & STEAM Learning Tips Bangkok | Arc Innovate",
        "desc": "Ideas and insights for Bangkok parents looking for creative kids activities, STEAM classes and after-school workshops. Real stories from Arc Innovate.",
        "h1": None,  # keep existing
        "og_image": DEFAULT_OG_IMAGE,
    },

    # BLOG POSTS
    "insights/why-design-thinking-is-the-1-skill-kids-need-in-2026.html": {
        "title": "Why Design Thinking Is the #1 Skill Kids Need in 2026 | Arc Innovate",
        "desc": "Why design thinking matters more than coding for children in 2026. How Bangkok kids build problem-solving skills that transfer to every subject and career.",
        "h1": None,  # keep existing
        "og_image": DEFAULT_OG_IMAGE,
    },
    "insights/3d-printing-and-design-thinking.html": {
        "title": "3D Printing & Design Thinking for Kids Bangkok | Arc Innovate",
        "desc": "How 3D printing and design thinking work together in children\u2019s education. Real examples from Arc Innovate workshops in Bangkok.",
        "h1": None,  # keep existing
        "og_image": DEFAULT_OG_IMAGE,
    },
    "insights/design-thinking-class-recap.html": {
        "title": "Design Thinking Camp Recap \u2014 Kids Workshop Bangkok | Arc Innovate",
        "desc": "Inside a real design thinking workshop for kids in Bangkok. See what children ages 7\u201310 built, learned and took home from Arc Innovate\u2019s 4-week program.",
        "h1": None,  # keep existing
        "og_image": DEFAULT_OG_IMAGE,
    },

    # LEAD GEN
    "lead-gen.html": {
        "title": "Book a Free Trial \u2014 Kids Workshops Bangkok | Arc Innovate",
        "desc": "Book a free trial class for your child at Arc Innovate Bangkok. Creative workshops, design thinking and 3D printing for ages 4\u201314.",
        "h1": None,  # keep existing
        "og_image": DEFAULT_OG_IMAGE,
    },
}

# Paused pages — update meta but mark as paused
PAUSED = {
    "programs/creative-cooking.html": {
        "title": "Creative Cooking for Kids Bangkok | Arc Innovate",
        "desc": "Creative cooking workshops for children in Bangkok. Combining kitchen science with design thinking for a hands-on learning experience.",
        "h1": None,
        "og_image": DEFAULT_OG_IMAGE,
    },
    "programs/fashion-design.html": {
        "title": "Fashion Design Workshops for Kids Bangkok | Arc Innovate",
        "desc": "Fashion design workshops for children in Bangkok. Kids explore textile, pattern and design thinking through hands-on creative projects.",
        "h1": None,
        "og_image": DEFAULT_OG_IMAGE,
    },
    "programs/ux-ui-for-kids.html": {
        "title": "UX Design Classes for Kids Bangkok | Arc Innovate",
        "desc": "UX and UI design classes for children in Bangkok. Kids learn digital product design through hands-on creative projects and prototyping.",
        "h1": None,
        "og_image": DEFAULT_OG_IMAGE,
    },
    "programs/young-entrepreneurs.html": {
        "title": "Young Entrepreneurs Program for Kids Bangkok | Arc Innovate",
        "desc": "Entrepreneurship workshops for children in Bangkok. Kids develop business ideas through design thinking, prototyping and presentation skills.",
        "h1": None,
        "og_image": DEFAULT_OG_IMAGE,
    },
    "programs/young-entrepreneurship.html": {
        "title": "Young Entrepreneurs Program for Kids Bangkok | Arc Innovate",
        "desc": "Entrepreneurship workshops for children in Bangkok. Kids develop business ideas through design thinking, prototyping and presentation skills.",
        "h1": None,
        "og_image": DEFAULT_OG_IMAGE,
    },
}

# Merge all
ALL_PAGES = {**PAGES, **PAUSED}


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
        print("!! Restored.\n")


def url_for(rel_path):
    p = str(rel_path).replace("\\", "/")
    if p == "index.html":
        return DOMAIN + "/"
    if p.endswith("/index.html"):
        return DOMAIN + "/" + p[:-len("/index.html")] + "/"
    if p.endswith(".html"):
        return DOMAIN + "/" + p[:-len(".html")]
    return DOMAIN + "/" + p


def get_existing_title(text):
    m = re.search(r'<title>(.*?)</title>', text, re.S)
    return m.group(1).strip() if m else "(none)"


def get_existing_desc(text):
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', text, re.S)
    return m.group(1).strip() if m else "(none)"


def set_title(text, new_title):
    m = re.search(r'<title>.*?</title>', text, re.S)
    if m:
        return text.replace(m.group(0), f'<title>{new_title}</title>', 1)
    if '<head>' in text:
        return text.replace('<head>', f'<head>\n<title>{new_title}</title>', 1)
    return f'<title>{new_title}</title>\n' + text


def set_meta_desc(text, new_desc):
    m = re.search(r'<meta\s+name="description"\s+content="[^"]*"[^>]*>', text, re.S)
    if m:
        return text.replace(m.group(0),
            f'<meta name="description" content="{new_desc}">', 1)
    if '</head>' in text:
        tag = f'<meta name="description" content="{new_desc}">\n'
        return text.replace('</head>', tag + '</head>', 1)
    return text


def set_og_tags(text, title, desc, url, image):
    og_block = f'''<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}{image}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Arc Innovate">'''

    # Remove ALL existing og: tags first
    text = re.sub(r'<meta\s+property="og:[^"]*"\s+content="[^"]*"[^>]*>\s*\n?', '', text)

    # Insert before </head>
    if '</head>' in text:
        return text.replace('</head>', og_block + '\n</head>', 1)
    return text


def set_h1(text, new_h1):
    if not new_h1:
        return text
    m = re.search(r'<h1[^>]*>(.*?)</h1>', text, re.S)
    if m:
        # Preserve any inline styles or classes on the h1 tag
        full_tag = re.search(r'<h1[^>]*>', text)
        return text.replace(m.group(0), f'{full_tag.group(0)}{new_h1}</h1>', 1)
    return text


def process_page(rel_path, config):
    fp = REPO / rel_path
    if not fp.exists():
        return None

    text = fp.read_text(encoding="utf-8", errors="ignore")
    old_title = get_existing_title(text)
    old_desc = get_existing_desc(text)

    new_title = config["title"]
    new_desc = config["desc"]
    new_h1 = config.get("h1")
    og_image = config.get("og_image", DEFAULT_OG_IMAGE)
    page_url = url_for(rel_path)

    # Apply changes
    text = set_title(text, new_title)
    text = set_meta_desc(text, new_desc)
    text = set_og_tags(text, new_title, new_desc, page_url, og_image)
    if new_h1:
        text = set_h1(text, new_h1)

    fp.write_text(text, encoding="utf-8")

    return {
        "file": rel_path,
        "old_title": old_title,
        "new_title": new_title,
        "old_desc": old_desc,
        "new_desc": new_desc,
    }


def verify_pixel():
    idx = REPO / "index.html"
    if not idx.exists():
        return False
    return PIXEL_ID in idx.read_text(encoding="utf-8", errors="ignore")


def verify_schema():
    count = 0
    for p in REPO.rglob("*.html"):
        rel = p.relative_to(REPO)
        if "Arc_Innovate_Reference" in str(rel) or "consulting" in str(rel):
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if "schema.org" in text or "application/ld+json" in text:
            count += 1
    return count


def main():
    global HEAD
    print("=" * 60)
    print("  ARC INNOVATE — SEO META TAG REWRITE")
    print("  Parent-intent keywords across all pages")
    print("=" * 60 + "\n")

    try:
        # Preconditions
        if not (REPO / "vercel.json").exists():
            raise Abort("Not the right repo. Run from /Users/anies/Downloads/arc-site")

        dirty = sh(["git", "status", "--porcelain", "--untracked-files=no"], capture=True)
        if dirty:
            raise Abort(f"Working tree not clean. Commit or stash first.\n{dirty}")

        HEAD = sh(["git", "rev-parse", "HEAD"], capture=True)
        print(f"HEAD: {HEAD[:8]} (rollback target)\n")

        # Pre-checks
        schema_before = verify_schema()
        pixel_before = verify_pixel()
        print(f"Schema.org pages before: {schema_before}")
        print(f"Meta Pixel before: {'YES' if pixel_before else 'MISSING'}\n")

        # Process all pages
        results = []
        missing = []
        for rel_path, config in ALL_PAGES.items():
            r = process_page(rel_path, config)
            if r:
                results.append(r)
            else:
                missing.append(rel_path)

        # Print results table
        print("=" * 100)
        print(f"{'FILE':<50} {'STATUS'}")
        print("=" * 100)
        for r in results:
            print(f"\n{r['file']}")
            print(f"  OLD title: {r['old_title'][:70]}")
            print(f"  NEW title: {r['new_title'][:70]}")
            print(f"  OLD desc:  {r['old_desc'][:70]}")
            print(f"  NEW desc:  {r['new_desc'][:70]}")
        print("=" * 100)

        if missing:
            print(f"\nSkipped (file not found): {missing}")

        print(f"\n{len(results)} pages updated.")

        # Post-checks
        schema_after = verify_schema()
        pixel_after = verify_pixel()
        print(f"\nSchema.org pages after: {schema_after} (was {schema_before})")
        if schema_after < schema_before:
            raise Abort(f"Schema.org count dropped from {schema_before} to {schema_after}!")

        print(f"Meta Pixel after: {'YES' if pixel_after else 'MISSING'}")
        if not pixel_after:
            raise Abort("Meta Pixel was destroyed during rewrite!")

        # Check for consulting keywords that should have been replaced
        consulting_hits = []
        for rel_path in ALL_PAGES:
            fp = REPO / rel_path
            if not fp.exists():
                continue
            text = fp.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'<(title|meta)[^>]*(consulting|consultant)[^>]*>', text, re.I):
                consulting_hits.append((rel_path, m.group(0)[:80]))
        if consulting_hits:
            print("\n!! Warning — consulting keywords still in meta tags:")
            for f, s in consulting_hits:
                print(f"   {f}: {s}")
        else:
            print("No consulting keywords remain in meta tags: CLEAN")

        # Commit and push
        print("\nCommitting and pushing...")
        sh(["git", "add", "-A"])
        sh(["git", "commit", "-m", "SEO: rewrite meta tags for parent-intent keywords"])
        sh(["git", "push"])
        print("\nPushed to GitHub. Vercel will auto-deploy.\n")

        print("=" * 60)
        print("  DONE!")
        print("=" * 60)
        print("\nNEXT STEPS:")
        print("  1. Google Search Console → URL Inspection → Request Indexing")
        print("     for the homepage and each program page")
        print("  2. Wait 1-2 weeks for Google to recrawl")
        print("  3. Check Search Console → Performance for new keyword impressions")

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
