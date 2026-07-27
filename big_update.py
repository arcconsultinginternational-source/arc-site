import re

with open('arc-innovate/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

# ============================================
# 1. RENAME ARC LEVEL GROUP NAMES
# ============================================
if '<h3>Experimental Arts &amp; Design</h3>' in content or '<h3>Experimental Arts & Design</h3>' in content:
    content = content.replace('<h3>Experimental Arts & Design</h3>', '<h3>Maker</h3>')
    content = content.replace('<h3>Experimental Arts &amp; Design</h3>', '<h3>Maker</h3>')
    changes.append("Level 1 -> Maker")

if '<h3>Young Innovator</h3>' in content:
    # Only replace the FIRST occurrence (arc-level card), not program cards
    content = content.replace('<h3>Young Innovator</h3>', '<h3>Solver</h3>', 1)
    changes.append("Level 2 -> Solver")

if '<h3>Creative Innovator</h3>' in content:
    content = content.replace('<h3>Creative Innovator</h3>', '<h3>Innovator</h3>')
    changes.append("Level 3 -> Innovator")

# ============================================
# 2. SIMPLIFY PROGRAMS SECTION TO 3 CARDS
# ============================================
programs_pattern = re.compile(r'(<div class="programs-grid">)(.*?)(</div>\s*</div>\s*</section>)', re.DOTALL)

new_programs_html = '''
      <a href="/arc-innovate/subjects/experimental-arts-and-design" class="program-card">
        <div class="program-card-header card-green">
          <div class="badge">MAKER • Ages 4–7</div>
          <h3>Experimental Arts & Design</h3>
          <p>Sensory exploration, open-ended making, and hands-on creative discovery. Where the design thinking habit begins.</p>
        </div>
        <img src="/arc-innovate/images/experimental-arts-and-design-logo.png" alt="Experimental Arts and Design class Bangkok kids">
        <div class="program-card-footer">
          Explore program <span>→</span>
        </div>
      </a>

      <a href="/arc-innovate/subjects/young-innovator" class="program-card">
        <div class="program-card-header card-blue">
          <div class="badge">SOLVER • Ages 7–10</div>
          <h3>Young Innovator</h3>
          <p>Design thinking + 3D printing. From empathy research to physical prototype, taken home.</p>
        </div>
        <img src="/arc-innovate/images/young-innovator-logo.png" alt="Young Innovator 3D printing class Bangkok kids">
        <div class="program-card-footer">
          Explore program <span>→</span>
        </div>
      </a>

      <a href="/arc-innovate/subjects/3d-printing" class="program-card">
        <div class="program-card-header card-purple">
          <div class="badge">INNOVATOR • Ages 10–14</div>
          <h3>3D Printing</h3>
          <p>Advanced prototyping and design innovation for complex real-world challenges.</p>
        </div>
        <img src="/arc-innovate/subjects/images/young-innovator.jpg" alt="3D Printing class Bangkok kids">
        <div class="program-card-footer">
          Explore program <span>→</span>
        </div>
      </a>
    '''

def replace_programs(match):
    return match.group(1) + new_programs_html + match.group(3)

new_content, n = programs_pattern.subn(replace_programs, content)
if n > 0:
    content = new_content
    changes.append(f"Programs section simplified to 3 cards ({n} replacement)")

with open('arc-innovate/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Changes applied:")
for c in changes:
    print(f"  ✅ {c}")
