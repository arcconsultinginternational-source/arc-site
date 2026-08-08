#!/usr/bin/env python3
"""
Add "Our Workshop Program" section with 4 workshop cards, placed right
after the existing Programs section (Our Program - Full Course).

USAGE:
  cd /Users/anies/Downloads/arc-site
  cp ~/Downloads/add_workshop_section.py .
  python3 add_workshop_section.py
"""
import subprocess, sys, pathlib

REPO = pathlib.Path.cwd()
TARGET = REPO / "index.html"

ANCHOR = '<!-- THE ARC — 3 LEVELS -->'

NEW_SECTION = '''<!-- OUR WORKSHOP PROGRAM -->
<section class="section" id="workshops">
  <div class="wrap">
    <div class="section-label">Short-Form Workshops</div>
    <h2>Our Workshop Program</h2>
    <p class="section-sub">Four focused workshops, each built around a different way of thinking. Kids can start with one and build toward the others — every workshop stands on its own.</p>

    <div class="workshops-grid">

      <div class="workshop-card">
        <div class="workshop-icon" style="background:linear-gradient(135deg,#2B6CB0,#63B3ED);">🖨️</div>
        <div class="workshop-tag">Technology Discovery</div>
        <h3>3D Printing Starter</h3>
        <p class="workshop-purpose">Discover the technology</p>
        <p class="workshop-learn">What 3D printing is, how a printer works, and a first hands-on printing experience.</p>
        <p class="workshop-quote">"What is 3D printing and what can I do with it?"</p>
      </div>

      <div class="workshop-card">
        <div class="workshop-icon" style="background:linear-gradient(135deg,#1A4A80,#2B6CB0);">🛠️</div>
        <div class="workshop-tag">Making &amp; Digital Skills</div>
        <h3>3D Printing Basic</h3>
        <p class="workshop-purpose">Learn to create</p>
        <p class="workshop-learn">Basic 3D modeling, preparing a file, and printing their own original design.</p>
        <p class="workshop-quote">"How do I turn my idea into a 3D object?"</p>
      </div>

      <div class="workshop-card">
        <div class="workshop-icon" style="background:linear-gradient(135deg,#BE185D,#EC4899);">🧸</div>
        <div class="workshop-tag">Creative Experimentation</div>
        <h3>Toy Lab</h3>
        <p class="workshop-purpose">Learn through creating and experimentation</p>
        <p class="workshop-learn">Design, movement and cause-and-effect, and hands-on prototyping.</p>
        <p class="workshop-quote">"How can I make something fun, interesting, or functional?"</p>
      </div>

      <div class="workshop-card">
        <div class="workshop-icon" style="background:linear-gradient(135deg,#5B21B6,#7C3AED);">🧩</div>
        <div class="workshop-tag">Problem Solving &amp; Systems Thinking</div>
        <h3>Maze World</h3>
        <p class="workshop-purpose">Learn through problem-solving</p>
        <p class="workshop-learn">Logic, spatial thinking, strategy under constraints, and testing &amp; optimization.</p>
        <p class="workshop-quote">"How can I find, design, test, and improve a solution?"</p>
      </div>

    </div>
  </div>
</section>

<style>
.workshops-grid{
  display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:40px;
}
.workshop-card{
  background:white;border-radius:20px;padding:28px 22px;
  border:1px solid #e8eef6;box-shadow:0 2px 16px rgba(43,108,176,0.06);
  transition:transform 0.25s ease,box-shadow 0.25s ease;
}
.workshop-card:hover{transform:translateY(-4px);box-shadow:0 12px 32px rgba(43,108,176,0.12);}
.workshop-icon{
  width:48px;height:48px;border-radius:14px;
  display:flex;align-items:center;justify-content:center;
  font-size:1.5rem;margin-bottom:16px;
}
.workshop-tag{
  font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
  color:var(--deep-blue);margin-bottom:8px;
}
.workshop-card h3{
  font-size:1.1rem;color:var(--ink);margin-bottom:6px;
}
.workshop-purpose{
  font-size:0.85rem;font-weight:700;color:var(--forest-green);margin-bottom:10px;
}
.workshop-learn{
  font-size:0.85rem;color:var(--mid);line-height:1.6;margin-bottom:14px;
}
.workshop-quote{
  font-size:0.8rem;font-style:italic;color:#888;
  padding-top:12px;border-top:1px solid #f0f4f8;line-height:1.5;
}
@media(max-width:900px){.workshops-grid{grid-template-columns:1fr 1fr;}}
@media(max-width:600px){.workshops-grid{grid-template-columns:1fr;}}
</style>

'''


def sh(cmd):
    r = subprocess.run(cmd, cwd=REPO)
    if r.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        sys.exit(1)


def main():
    print("=== Add Our Workshop Program Section ===\n")

    if not TARGET.exists():
        print("ERROR: index.html not found. Run from /Users/anies/Downloads/arc-site")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8", errors="ignore")

    if "Our Workshop Program" in text:
        print("Section already exists — nothing to do.")
        sys.exit(0)

    if ANCHOR not in text:
        print(f"ERROR: could not find anchor '{ANCHOR}' in index.html")
        print("The file structure may have changed. Aborting without modifying anything.")
        sys.exit(1)

    text = text.replace(ANCHOR, NEW_SECTION + ANCHOR, 1)
    TARGET.write_text(text, encoding="utf-8")

    print("Section inserted after Programs, before The Arc.\n")
    print("Committing and pushing...")
    sh(["git", "add", "index.html"])
    sh(["git", "commit", "-m", "Add Our Workshop Program section (4 workshop cards)"])
    sh(["git", "push"])

    print("\n=== DONE ===")
    print("Live in ~1 minute. Hard refresh (Cmd+Shift+R) to see it.")


if __name__ == "__main__":
    main()
