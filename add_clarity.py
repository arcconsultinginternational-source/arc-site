#!/usr/bin/env python3
"""
Add Microsoft Clarity tracking code to all HTML pages.

USAGE:
  cd /Users/anies/Downloads/arc-site
  cp ~/Downloads/add_clarity.py .
  python3 add_clarity.py
"""
import re, subprocess, sys, pathlib

REPO = pathlib.Path.cwd()
SKIP = {"Arc_Innovate_Reference", ".git", "consulting"}

CLARITY_CODE = '''<script type="text/javascript">
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "xy283s92pl");
</script>'''

def sh(cmd):
    r = subprocess.run(cmd, cwd=REPO)
    if r.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        sys.exit(1)

def add_clarity(fp):
    text = fp.read_text(encoding="utf-8", errors="ignore")
    
    # Already has Clarity — skip
    if "clarity.ms/tag" in text:
        return False
    
    # Insert before </head>
    if "</head>" in text:
        new_text = text.replace("</head>", CLARITY_CODE + "\n</head>", 1)
        fp.write_text(new_text, encoding="utf-8")
        return True
    
    # Fallback: insert after <head> if no </head>
    if "<head>" in text:
        new_text = text.replace("<head>", "<head>\n" + CLARITY_CODE, 1)
        fp.write_text(new_text, encoding="utf-8")
        return True
    
    return False

def main():
    print("=== Add Microsoft Clarity ===\n")
    
    if not (REPO / "vercel.json").exists():
        print("ERROR: Run from /Users/anies/Downloads/arc-site")
        sys.exit(1)
    
    count = 0
    for p in sorted(REPO.rglob("*.html")):
        rel = p.relative_to(REPO)
        if any(x in SKIP for x in rel.parts) or rel.name.endswith(".bak"):
            continue
        if add_clarity(p):
            print(f"  {rel}")
            count += 1
    
    if count == 0:
        print("No pages found or Clarity already installed.")
        sys.exit(0)
    
    print(f"\nClarity added to {count} page(s).")
    print("\nCommitting and pushing...")
    sh(["git", "add", "-A"])
    sh(["git", "commit", "-m", "Add Microsoft Clarity tracking"])
    sh(["git", "push"])
    
    print("\n=== DONE ===")
    print("Clarity is now live on all pages.")
    print("Check https://clarity.microsoft.com → your project → Sessions in 2-5 minutes.")

if __name__ == "__main__":
    main()
