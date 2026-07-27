import os, re

BASE = os.path.expanduser("~/Downloads/arc-site")
PIXEL_ID = "1337977120778599"

pixel_script = '''<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,"script","https://connect.facebook.net/en_US/fbevents.js");fbq("init","''' + PIXEL_ID + '''");fbq("track","PageView");
</script>
<noscript><img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=''' + PIXEL_ID + '''&ev=PageView&noscript=1"/></noscript>'''

pages = {
    "arc-innovate/index.html": {
        "title": "Arc Innovate | Design Thinking & 3D Printing for Kids Bangkok",
        "description": "Creative academy for kids ages 4-14 in Bangkok. Design Thinking, 3D Printing & STEAM. The skills AI cannot replace. คอร์สเสริมทักษะเด็ก กรุงเทพ",
        "keywords": "design thinking for kids Bangkok, 3D printing for kids Bangkok, creative school Bangkok, STEAM classes Bangkok, คอร์ส design thinking เด็ก กรุงเทพ, เรียน 3d printing เด็ก, after school enrichment Bangkok",
        "og_title": "Arc Innovate | Design Thinking & 3D Printing for Kids Bangkok",
        "og_desc": "Creative academy for kids ages 4-14 in Bangkok. Design Thinking, 3D Printing & STEAM classes. The skills AI cannot replace.",
        "canonical": "https://www.arc-international-edu.com/arc-innovate",
        "schema": '{"@context":"https://schema.org","@type":"LocalBusiness","name":"Arc Innovate","description":"Creative problem-solving academy for kids ages 4-14 in Bangkok, teaching design thinking, STEAM, and creative enrichment programs.","url":"https://www.arc-international-edu.com/arc-innovate","telephone":"+66835193659","email":"arc.international.edu@gmail.com","areaServed":"Bangkok, Thailand","sameAs":["https://instagram.com/arc.innovate"]}'
    },
    "arc-innovate/subjects/3d-printing.html": {
        "title": "3D Printing Class for Kids Bangkok | Arc Innovate",
        "description": "3D Printing for kids ages 7-10 in Bangkok. Design and print real objects in 8 weeks. เรียน 3D printing กรุงเทพ คอร์ส 3D printing เด็ก เรียน 3d printing เด็ก",
        "keywords": "3D printing for kids Bangkok, 3D printing workshop Bangkok, maker class kids Bangkok, creative school Bangkok, เรียน 3D printing กรุงเทพ, คอร์ส 3D printing เด็ก กรุงเทพ, เวิร์กช็อป 3D printing กรุงเทพ, เรียน 3d printing เด็ก",
        "og_title": "3D Printing Class for Kids | Arc Innovate Bangkok",
        "og_desc": "3D Printing for kids ages 7-10 in Bangkok. Design and print real objects. เรียน 3D printing กรุงเทพ เรียน 3d printing เด็ก",
        "canonical": "https://www.arc-international-edu.com/arc-innovate/subjects/3d-printing",
        "schema": '{"@context":"https://schema.org","@type":"Course","name":"3D Printing","description":"3D printing and digital design class for kids ages 7-10 in Bangkok. Design and bring ideas to life using 3D technology.","provider":{"@type":"Organization","name":"Arc Innovate","sameAs":"https://www.arc-international-edu.com/arc-innovate"},"coursePrerequisites":"None","audience":{"@type":"EducationalAudience","educationalRole":"student"},"hasCourseInstance":{"@type":"CourseInstance","courseMode":"In-person","location":{"@type":"Place","addressLocality":"Bangkok","addressCountry":"TH"}}}'
    },
    "arc-innovate/subjects/young-innovators.html": {
        "title": "Young Innovator Class | Arc Innovate Bangkok",
        "description": "Young Innovator: Design thinking & hands-on building for kids ages 7-10 in Bangkok. Real problem-solving through making. คอร์ส design thinking เด็ก กรุงเทพ",
        "keywords": "design thinking class kids Bangkok, problem solving kids Bangkok, creative class kids Bangkok, creative school Bangkok, คอร์ส design thinking เด็ก กรุงเทพ",
        "og_title": "Young Innovator Class | Arc Innovate Bangkok",
        "og_desc": "Design thinking & hands-on building for kids ages 7-10 in Bangkok. คอร์ส design thinking เด็ก กรุงเทพ",
        "canonical": "https://www.arc-international-edu.com/arc-innovate/subjects/young-innovators",
        "schema": '{"@context":"https://schema.org","@type":"Course","name":"Young Innovator","description":"Hands-on building and design thinking for kids ages 7-10 in Bangkok. Real design challenges and creative problem-solving.","provider":{"@type":"Organization","name":"Arc Innovate","sameAs":"https://www.arc-international-edu.com/arc-innovate"},"coursePrerequisites":"None","audience":{"@type":"EducationalAudience","educationalRole":"student"},"hasCourseInstance":{"@type":"CourseInstance","courseMode":"In-person","location":{"@type":"Place","addressLocality":"Bangkok","addressCountry":"TH"}}}'
    },
    "arc-innovate/subjects/experimental-arts-and-design.html": {
        "title": "Experimental Arts for Kids Bangkok | Arc Innovate",
        "description": "Sensory art & design for kids ages 4-7 in Bangkok. Colour, texture, and hands-on making every week. คอร์สศิลปะสร้างสรรค์เด็ก กรุงเทพ",
        "keywords": "art class for kids Bangkok, sensory art kids Bangkok, creative arts children Bangkok, design thinking young kids, experimental arts Bangkok, คอร์สศิลปะเด็ก กรุงเทพ, creative school Bangkok",
        "og_title": "Experimental Arts for Kids | Arc Innovate Bangkok",
        "og_desc": "Sensory art & design for kids ages 4-7 in Bangkok. Colour, texture, hands-on making. คอร์สศิลปะสร้างสรรค์เด็ก กรุงเทพ",
        "canonical": "https://www.arc-international-edu.com/arc-innovate/subjects/experimental-arts-and-design",
        "schema": '{"@context":"https://schema.org","@type":"Course","name":"Experimental Arts","description":"Sensory art and design class for kids ages 4-7 in Bangkok. Hands-on creative exploration through colour, texture, and making.","provider":{"@type":"Organization","name":"Arc Innovate","sameAs":"https://www.arc-international-edu.com/arc-innovate"},"coursePrerequisites":"None","audience":{"@type":"EducationalAudience","educationalRole":"student"},"hasCourseInstance":{"@type":"CourseInstance","courseMode":"In-person","location":{"@type":"Place","addressLocality":"Bangkok","addressCountry":"TH"}}}'
    },
    "arc-innovate/subjects/creative-inspire.html": {
        "title": "Creative Inspire Art Class for Kids Bangkok | Arc Innovate",
        "description": "Visual arts & design for kids ages 7-10 in Bangkok. Build a real portfolio each term. Rooted in design thinking. คอร์สศิลปะเด็ก กรุงเทพ",
        "keywords": "art class kids Bangkok, visual arts children Bangkok, creative portfolio kids, design thinking for kids Bangkok, creative school Bangkok, คอร์สศิลปะเด็ก กรุงเทพ",
        "og_title": "Creative Inspire Art Class | Arc Innovate Bangkok",
        "og_desc": "Visual arts & design for kids ages 7-10 in Bangkok. Build a real portfolio each term.",
        "canonical": "https://www.arc-international-edu.com/arc-innovate/subjects/creative-inspire",
        "schema": '{"@context":"https://schema.org","@type":"Course","name":"Creative Inspire","description":"Visual arts and design class for kids ages 7-10 in Bangkok. Build a real portfolio and sketchbook every term.","provider":{"@type":"Organization","name":"Arc Innovate","sameAs":"https://www.arc-international-edu.com/arc-innovate"},"coursePrerequisites":"None","audience":{"@type":"EducationalAudience","educationalRole":"student"},"hasCourseInstance":{"@type":"CourseInstance","courseMode":"In-person","location":{"@type":"Place","addressLocality":"Bangkok","addressCountry":"TH"}}}'
    },
    "arc-innovate/subjects/insight-and-questioning.html": {
        "title": "Insight & Questioning Class for Kids Bangkok | Arc Innovate",
        "description": "Critical thinking & observation for kids ages 7-10 in Bangkok. Learn to ask better questions through design thinking.",
        "keywords": "critical thinking class kids Bangkok, design thinking for kids Bangkok, problem solving kids Bangkok, observation skills children, creative school Bangkok, คอร์ส design thinking เด็ก กรุงเทพ",
        "og_title": "Insight & Questioning | Arc Innovate Bangkok",
        "og_desc": "Critical thinking & observation for kids ages 7-10 in Bangkok. Design thinking approach.",
        "canonical": "https://www.arc-international-edu.com/arc-innovate/subjects/insight-and-questioning",
        "schema": '{"@context":"https://schema.org","@type":"Course","name":"Insight and Questioning","description":"Critical thinking class for kids ages 7-10 in Bangkok. Learn to observe, ask better questions, and find insights others miss.","provider":{"@type":"Organization","name":"Arc Innovate","sameAs":"https://www.arc-international-edu.com/arc-innovate"},"coursePrerequisites":"None","audience":{"@type":"EducationalAudience","educationalRole":"student"},"hasCourseInstance":{"@type":"CourseInstance","courseMode":"In-person","location":{"@type":"Place","addressLocality":"Bangkok","addressCountry":"TH"}}}'
    },
    "arc-innovate/subjects/young-entrepreneurship.html": {
        "title": "Young Entrepreneurship Class for Kids Bangkok | Arc Innovate",
        "description": "Business thinking & design for kids ages 7-10 in Bangkok. Spot opportunities, build ideas, and pitch live. Creative school.",
        "keywords": "entrepreneurship class kids Bangkok, business thinking children, design thinking for kids Bangkok, creative school Bangkok, problem solving kids, คอร์ส design thinking เด็ก กรุงเทพ",
        "og_title": "Young Entrepreneurship | Arc Innovate Bangkok",
        "og_desc": "Business thinking & design for kids ages 7-10 in Bangkok. Spot opportunities, build ideas, pitch live.",
        "canonical": "https://www.arc-international-edu.com/arc-innovate/subjects/young-entrepreneurship",
        "schema": '{"@context":"https://schema.org","@type":"Course","name":"Young Entrepreneurship","description":"Business thinking and design class for kids ages 7-10 in Bangkok. Learn to spot opportunities, build a business idea, and pitch.","provider":{"@type":"Organization","name":"Arc Innovate","sameAs":"https://www.arc-international-edu.com/arc-innovate"},"coursePrerequisites":"None","audience":{"@type":"EducationalAudience","educationalRole":"student"},"hasCourseInstance":{"@type":"CourseInstance","courseMode":"In-person","location":{"@type":"Place","addressLocality":"Bangkok","addressCountry":"TH"}}}'
    },
    "arc-innovate/subjects/tech-talk.html": {
        "title": "Tech Talk Digital Design for Kids Bangkok | Arc Innovate",
        "description": "UX/UI & digital design for kids ages 7-10 in Bangkok. Design apps and websites through design thinking. Creative school.",
        "keywords": "digital design class kids Bangkok, UX UI for kids Bangkok, app design children, design thinking for kids Bangkok, creative school Bangkok, tech class kids Bangkok",
        "og_title": "Tech Talk Digital Design | Arc Innovate Bangkok",
        "og_desc": "UX/UI & digital design for kids ages 7-10 in Bangkok. Design real apps and websites.",
        "canonical": "https://www.arc-international-edu.com/arc-innovate/subjects/tech-talk",
        "schema": '{"@context":"https://schema.org","@type":"Course","name":"Tech Talk","description":"UX/UI design and digital communication class for kids ages 7-10 in Bangkok. Design apps, websites, and digital tools.","provider":{"@type":"Organization","name":"Arc Innovate","sameAs":"https://www.arc-international-edu.com/arc-innovate"},"coursePrerequisites":"None","audience":{"@type":"EducationalAudience","educationalRole":"student"},"hasCourseInstance":{"@type":"CourseInstance","courseMode":"In-person","location":{"@type":"Place","addressLocality":"Bangkok","addressCountry":"TH"}}}'
    },
    "arc-innovate/design-thinking-guide.html": {
        "title": "Design Thinking for Kids: Complete Guide | Bangkok",
        "description": "Design Thinking for Kids: Learn the 5-stage process and why it matters. Arc Innovate Bangkok. design thinking คืออะไร การคิดเชิงออกแบบสำหรับเด็ก",
        "keywords": "design thinking for kids, design thinking Bangkok, design thinking education, creative school Bangkok, design thinking คืออะไร, การคิดเชิงออกแบบสำหรับเด็ก",
        "og_title": "Design Thinking for Kids: Complete Guide",
        "og_desc": "Learn the 5-stage design thinking process for kids. Arc Innovate Bangkok. design thinking คืออะไร",
        "canonical": "https://www.arc-international-edu.com/arc-innovate/design-thinking-guide",
        "schema": '{"@context":"https://schema.org","@type":"Article","headline":"Design Thinking for Kids: Complete Guide","description":"Learn the 5-stage design thinking process, why it matters for Bangkok kids, and how it is taught at Arc Innovate.","author":{"@type":"Organization","name":"Arc Innovate"},"publisher":{"@type":"Organization","name":"Arc Innovate","sameAs":"https://www.arc-international-edu.com/arc-innovate"}}'
    },
    "arc-innovate/the-arc.html": {
        "title": "The Arc — Design Thinking for Kids 4-14 | Arc Innovate",
        "description": "Arc Innovate 3-level curriculum for kids ages 4-14 in Bangkok. From Experimental Arts to Design Thinking to 3D Printing innovation.",
        "keywords": "design thinking curriculum kids Bangkok, creative learning program Bangkok, STEAM enrichment Bangkok, 3D printing for kids Bangkok, creative school Bangkok, คอร์ส design thinking เด็ก กรุงเทพ",
        "og_title": "The Arc — Design Thinking Journey | Arc Innovate Bangkok",
        "og_desc": "Arc Innovate 3-level curriculum for kids ages 4-14 in Bangkok. Design Thinking, 3D Printing and creative innovation.",
        "canonical": "https://www.arc-international-edu.com/arc-innovate/the-arc",
        "schema": '{"@context":"https://schema.org","@type":"EducationEvent","name":"The Arc: Design Thinking Curriculum","description":"Arc Innovate 3-level design thinking curriculum for kids ages 4-14 in Bangkok.","organizer":{"@type":"Organization","name":"Arc Innovate","sameAs":"https://www.arc-international-edu.com/arc-innovate"},"eventStatus":"EventScheduled","location":{"@type":"Place","addressLocality":"Bangkok","addressCountry":"TH"}}'
    },
}

print("Starting SEO fix on arc-site...\n")

for rel_path, fixes in pages.items():
    filepath = os.path.join(BASE, rel_path)

    if not os.path.exists(filepath):
        print("MISSING: " + rel_path)
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Title
    content = re.sub(r"<title>[^<]*</title>",
        "<title>" + fixes["title"] + "</title>", content)

    # Description
    content = re.sub(r'<meta name="description" content="[^"]*"',
        '<meta name="description" content="' + fixes["description"] + '"', content)

    # Keywords
    if '<meta name="keywords"' in content:
        content = re.sub(r'<meta name="keywords" content="[^"]*"',
            '<meta name="keywords" content="' + fixes["keywords"] + '"', content)
    else:
        content = content.replace("</head>",
            '<meta name="keywords" content="' + fixes["keywords"] + '">\n</head>')

    # OG Title
    if '<meta property="og:title"' in content:
        content = re.sub(r'<meta property="og:title" content="[^"]*"',
            '<meta property="og:title" content="' + fixes["og_title"] + '"', content)
    else:
        content = content.replace("</head>",
            '<meta property="og:title" content="' + fixes["og_title"] + '">\n</head>')

    # OG Description
    if '<meta property="og:description"' in content:
        content = re.sub(r'<meta property="og:description" content="[^"]*"',
            '<meta property="og:description" content="' + fixes["og_desc"] + '"', content)
    else:
        content = content.replace("</head>",
            '<meta property="og:description" content="' + fixes["og_desc"] + '">\n</head>')

    # Canonical
    if '<link rel="canonical"' in content:
        content = re.sub(r'<link rel="canonical" href="[^"]*"',
            '<link rel="canonical" href="' + fixes["canonical"] + '"', content)
    else:
        content = content.replace("</head>",
            '<link rel="canonical" href="' + fixes["canonical"] + '">\n</head>')

    # Schema
    schema_block = '<script type="application/ld+json">\n' + fixes["schema"] + '\n</script>'
    if "application/ld+json" not in content:
        content = content.replace("</head>", schema_block + "\n</head>")

    # Meta Pixel
    if "fbq(" not in content:
        content = content.replace("</head>", pixel_script + "\n</head>")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    changed = content != original
    print(("UPDATED" if changed else "NO CHANGE") + ": " + rel_path)

print("\nAll done! Now run:")
print("cd ~/Downloads/arc-site && git add -A && git commit -m 'SEO: Add schema, fix meta tags, add pixel to all pages' && git push")
