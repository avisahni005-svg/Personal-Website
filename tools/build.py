#!/usr/bin/env python3
"""Generates the static site (index/about/project pages) into public/.

Run from anywhere:  python3 tools/build.py
Media paths come from tools/media-index.json (name -> {src, w, h, poster}).
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = json.load(open(os.path.join(ROOT, "tools", "media-index.json")))
E = html.escape

NAV = [
    ("stfc", "Street Football Club"),
    ("rah", "Royal Albert Hall"),
    ("hyperyouth", "Hyperyouth"),
    ("right-to-resist", "Right to Resist"),
    ("dekho", "Dekho Magar Pyaar Se"),
    ("playground", "Playground :)"),
]
PROFILE = [
    "Ever driven up a mountain on a one-lane road with traffic coming both ways, horns blaring, Punjabi music blasting, and a full-blown debate about dream cars in the back seat? That was just a normal day growing up in Dehradun, India. Nothing seemed to fit together, and somehow it all worked.",
    "This chaos shaped my design practice today. I'm at my best when a project feels scattered, with too many moving pieces and no obvious thread. That's where I find my footing, pulling it all together into work that's layered and intricate but, in the end, feels clear and inevitable.",
]

MISSING = set()
AUDIO_PAGE = False        # Hyperyouth only: its videos get an unmute button

# --------------------------------------------------------------------------- media
def m(key):
    if key not in IDX:
        MISSING.add(key)
        return {"src": "", "poster": "", "w": 1, "h": 1}
    return IDX[key]

def pick(key, variant):
    """Return the file entry for a size variant: 'thumb' (560w), 'hero' (1280w), 'side' (900w) or the full file."""
    d = m(key)
    v = {"thumb": "t", "hero": "m", "side": "s"}.get(variant)
    return d[v] if v and v in d else d

def media(key, cls="", alt="", eager=False, variant="full", style="", sizes="(max-width: 720px) 100vw, 65vw"):
    d = m(key)
    if d["src"].endswith(".mp4"):
        poster = d.get("poster_t") if variant == "thumb" and d.get("poster_t") else d["poster"]
        if AUDIO_PAGE and d.get("audio"):
            st = f' style="{style}"' if style else ""
            return (f'<div class="vwrap"{st}><video class="{cls}" src="{d["audio"]}" poster="{poster}" width="{d["w"]}" height="{d["h"]}" '
                    f'muted loop playsinline preload="none" data-autoplay data-audio></video>'
                    f'<button type="button" class="unmute" data-unmute aria-pressed="false" aria-label="Unmute video">'
                    f'<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path class="spk" d="M3 9v6h4l5 4V5L7 9H3z"/>'
                    f'<path class="wave" d="M15.5 8.5a5 5 0 0 1 0 7M18 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>'
                    f'<path class="slash" d="M16 9l6 6M22 9l-6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button></div>')
        st = f' style="{style}"' if style else ""
        return (f'<video class="{cls}"{st} src="{d["src"]}" poster="{poster}" width="{d["w"]}" height="{d["h"]}" '
                f'muted loop playsinline preload="none" data-autoplay></video>')
    f = pick(key, variant)
    srcset = ""
    if variant == "full":     # let the browser pick the smallest file that still looks sharp
        opts = [(d[v]["w"], d[v]["src"]) for v in ("t", "m") if v in d] + [(d["w"], d["src"])]
        if len(opts) > 1:
            srcset = ' srcset="' + ", ".join(f"{u} {w}w" for w, u in opts) + f'" sizes="{sizes}"'
    load = 'fetchpriority="high"' if eager == "high" else ('' if eager else 'loading="lazy"')
    st = f' style="{style}"' if style else ""
    if d.get("alpha"):
        cls = (cls + " alpha").strip()      # transparent images: no grey placeholder behind them
    return f'<img class="{cls}"{st} src="{f["src"]}"{srcset} width="{d["w"]}" height="{d["h"]}" alt="{E(alt)}" {load} decoding="async">'

def ratio(key):
    d = m(key)
    return d["h"] / d["w"]

def paras(texts):
    return "".join(f"<p>{E(t)}</p>" for t in texts)

# --------------------------------------------------------------------------- shell
def shell(title, body, *, kind, current=None, extra_cls="", desc="Avi Sahni — graphic designer working across branding, typography and creative coding."):
    cls = f"{kind} {extra_cls}".strip()
    top_link = '<a class="about-link" href="about.html">↗ About</a>' if kind == "home" else ""
    # the same Contents on every page; the current page is marked
    home_a = f'<a href="index.html"{" aria-current=page" if kind == "home" else ""}>Home</a>'
    about_a = f'<a href="about.html"{" aria-current=page" if kind == "about" else ""}>About</a>'
    first = home_a + about_a
    nav_items = "".join(
        f'<a href="{s}.html"{" aria-current=page" if s == current else ""}>{E(n)}</a>' for s, n in NAV
    )
    profile = ""
    if kind != "about":
        profile = f'''
    <div class="side-photo">{media("ffea1552-cc6b-43ba-bbca-f2bf9564a1c2", alt="Avi Sahni on set beside a film camera", eager="high", variant="side")}</div>
    <div class="side-row profile"><h3>Profile</h3><div class="txt">{paras(PROFILE)}</div></div>'''
    side_preload = ""
    if kind != "about":
        side_preload = f'\n<link rel="preload" href="{pick("ffea1552-cc6b-43ba-bbca-f2bf9564a1c2", "side")["src"]}" as="image" fetchpriority="high">'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#ffffff">
<script>
/* Opening a page from a link always starts at the top (back/forward keep their own scroll position) */
(function () {{
  var nav = performance.getEntriesByType && performance.getEntriesByType("navigation")[0];
  if (location.hash || (nav && nav.type !== "navigate")) return;
  var top = function () {{ window.scrollTo({{ top: 0, left: 0, behavior: "instant" }}); }};
  top();
  document.addEventListener("DOMContentLoaded", top);
  window.addEventListener("load", top);
  window.addEventListener("pageshow", top);
}})();
</script>
<link rel="icon" href="img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="fonts/Satoshi-Variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="img/wordmark.png" as="image" fetchpriority="high">{side_preload}
<link rel="stylesheet" href="css/style.css">
<script src="js/main.js" defer></script>
</head>
<body class="{cls}">
<header class="mast">
  <img class="wordmark" src="img/wordmark.png" width="2000" height="515" alt="Avi Sahni">
  <p class="role">Graphic Designer</p>
  <p class="tagline">Branding, Typography &amp; Creative Coding</p>
  <p class="contact"><b>(M)</b> <a href="mailto:hello@avisahni.design">hello@avisahni.design</a><br><b>(IG)</b> <a href="https://www.instagram.com/avisahni.design/" rel="noopener">avisahni.design</a></p>
  {top_link}
</header>
<a class="wm-link" href="index.html" aria-label="Home"></a>
<main>
{body}
<footer class="foot">
  <a class="top" href="#" data-top>Top ↑</a>
  <p>Everything is a reflection of the chaos around it :)</p>
</footer>
</main>
<aside class="side">{profile}
  <div class="side-row contents"><h3>Contents</h3><nav>{first}<span class="gap"></span>{nav_items}</nav></div>
</aside>
</body>
</html>
'''

# --------------------------------------------------------------------------- home
def masonry(items, cols=3):
    """Place each item in the currently shortest column (matches Cargo's gallery)."""
    heights = [0.0] * cols
    columns = [[] for _ in range(cols)]
    for it in items:
        i = heights.index(min(heights))
        columns[i].append(it)
        heights[i] += ratio(it[1]) + 0.37  # caption + row gap, in thumbnail widths
    return columns

def thumb(cap, key, href):
    return (f'<figure class="thumb"><a href="{href}">{media(key, alt=cap, eager=True, variant="thumb")}</a>'
            f'<figcaption>{E(cap)}</figcaption></figure>')

HOME = [
    dict(slug="stfc", num="01", title="Street Football Club",
         lead="As someone who has played soccer all my life, Street Football Club has always been an intriguing entity to me. A pick up football community aimed at bringing the speed and chaos of street football culture to America. This project was particularly challenging as the community spans across 13 cities, and it was important to let each cities individual personality shine.",
         tags="Branding, Motion, Creative Direction",
         hero="stfc-hero-video",
         copy=["The rebrand goal was to create a strong base system for STFC the organisation, with individual and unique identities for each city that convey speed and chaos.",
               "There are 13 cities that STFC is in at the moment, and they expand every year. The goal for this part was to create a set of wordmarks for each city that fall in the same system. This resulted in every city having a unique identity with a wide color palette."],
         thumbs=[("Stationary", "stfc-aviportfoliogx-8"), ("Stickers", "stfc-artboard-26-1"),
                 ("Spatial Application_1", "stfc-arena"), ("Posters_1", "stfc-poster"),
                 ("Business Cards", "stfc-aviportfoliogx-1"), ("Billboard", "austin-poster-stfc"),
                 ("Spatial Application_2", "arena-stfc"), ("Website", "stfc-laptop-video"),
                 ("Spatial Application_3", "stfc-arena-3"),
                 ("Merch", "artboard-26-from-stfc"), ("Motion", "motion-video"),
                 ("Posters_2", "free-poster-mockup-4"), ("Marketing", "stfc-aviportfoliogx-2")]),
    dict(slug="rah", num="02", title="Royal Albert Hall",
         lead="The sheer range of events Royal Albert Hall does is what initially sparked my interest in this project. Today, with a capacity exceeding 5,000, the Hall presents more than 400 events annually, encompassing music, sport, community gatherings, and much more. The challenge was creating an identity that would leverage the 155 year heritage of the space, but also create a space receptive to modern and experimental ideas. In the end the goal was to create a nimble and flexible identity that caters to the varying interests of those in South Kensington and beyond. Creating a community that is larger than the brand itself.",
         tags="Branding, Creative Direction",
         hero="rah-aviportfoliogx",
         copy=["The rebrand goal was to create a nimble and flexible identity that caters to the varying interests of those in South Kensington and beyond. Creating a community that is larger than the brand itself, being proud of their history while still allowing innovation, making them a sanctuary for the arts.",
               "The principle for this identity system is based within the frame created in the stem of the H in RAH. The metaphor lies in the idea of being and creating the space for culture and knowledge to emerge. The serif type, rooted in elegance and royalty, adds gravitas to the system, but the flexibility of the frame creates a contrasting language of modernity and experimentation.",
               "For special events, a modular font created using the frame within the logo can be used. This typeface allows for stretching and squashing. This frame can also be distorted in different ways for events that are less classical."],
         thumbs=[("Spatial Application_1", "royal-albert-hall-nov-2012"), ("Poster_1", "rah-aviportfoliogx-1"),
                 ("Stationary", "rah-1"), ("Banners", "royal-albert-hall"),
                 ("Modular Font", "freight-video-8"), ("Brand Micro_1", "iphone-16-pro-mockups-front-view"),
                 ("Brand Micro_2_Billboard_1", "rah-aviportfoliogx-uk23-lon-0403"), ("Brand Micro_2_Vinyl", "vinyl-template"),
                 ("Brand Micro_2_Poster_1", "rah-aviportfoliogx-4"), ("Brand Micro_2_Tickets", "free-ticket-mockup-3"),
                 ("Brand Micro_2_Poster_2", "rah-aviportfoliogx-3"), ("Brand Micro_2_Billboard_2", "outdoor-screen-mockup"),
                 ("Brand Micro_2_Bus", "rah-aviportfoliogx-2")]),
    dict(slug="hyperyouth", num="03", title="Hyperyouth",
         lead="Initially starting as a way of learning generative design I took an album from rap duo Joey Valence & Brae and created a creative identity for its release. Hyperyouth is an introspective album at large but it still lets the duo's fun and goofy side shine at times.",
         tags="Generative design, Branding",
         hero="avi-portfolio",
         copy=["Built in p5.js, using wave functions, randomness, and real-time audio-reactive input, the design translates the record's sample-heavy chaos and youthful energy into an evolving, interactive visual language."],
         thumbs=[("Vinyl", "hyperyouth-portfolio"), ("Billboard", "hyperyouth-banner"),
                 ("Motion_1", "hy-motion-1"), ("Code Demo_1", "hy-code-demo"),
                 ("Motion_2", "hy-motion-2")]),
    dict(slug="right-to-resist", num="04", title="Right to Resist",
         lead="Revolution and rebellion are complex, from the French Revolution to the Bolsheviks, to January 6th in the USA. Where does one draw the line between right and wrong and who decides on a collective morality? \"Right to Resist\" explores this and more, covering the ethics and philosophies, as well as the function and process of revolutions and resistance. It is in no way an unbiased commentary, but instead a collection of thoughts meant to inspire change.",
         tags="Publication",
         hero="avi-portfolio-video",
         copy=["Primarily featuring Baby Blue and Black, the book's color scheme creates a play of light emerging from the dark. The blue emulates a clear blue sky as a symbol of freedom.",
               "Pressato is used for the headline type, which fills the page with large titles, creating visuals inspired by protest posters."],
         thumbs=[("Opening", "right-to-resist"), ("Table of Contents", "right-to-resist-1"),
                 ("Chapter Divider", "right-to-resist-20"), ("Chapter_1", "right-to-resist-18"),
                 ("Endnotes", "right-to-resist-2"), ("Art and Design in Rebellion", "right-to-resist-43"),
                 ("Chapter_3", "right-to-resist-65"), ("Chapter_4", "right-to-resist-80"),
                 ("Pull Quotes", "right-to-resist-68")]),
    dict(slug="dekho", num="05", title="Dekho Magar Pyaar Se",
         cols=[["Cover", "Table of Contents", "Motion_2"],
               ["Motion_1", "Detail_1", "Detail_2", "Backmatter_2"],
               ["Posters", "Chapter_1", "Backmatter_1", "Chapter_5"]],
         lead="An homage to Indian trucks and truck drivers, as these trucks were my introduction to typography and visual design. The book delves into the creation and history of truck art, the lives of truck drivers, and the connection between the drivers and the art across India.",
         tags="Publication, Posters, Motion",
         hero="aviportfoliogx-img-1739",
         copy=["During the design process, I aimed to emulate life on an Indian road, an organized chaos. The bold colors and typography are a clear homage to Indian trucks and the rich culture one experiences while traveling across India. Within the book's content, all non-English words are typeset in Hindi (India's national language), with pronunciations and definitions provided below and in the glossary at the end. This compels non-Hindi readers to take a detour while reading. This combined with the book's various layouts and complex grid, creates a reading experience akin to driving on an Indian road, where one is always alert and engaged."],
         thumbs=[("Cover", "dekho-magr-pyaar-se-2"), ("Motion_1", "freight-cargo-video"),
                 ("Posters", "free-billboard-mockup"), ("Table of Contents", "dekho-magr-pyaar-se-5"),
                 ("Chapter_1", "dekho-magr-pyaar-se-4"), ("Detail_1", "dekho-magr-pyaar-se-3"),
                 ("Motion_2", "mp2-video"), ("Backmatter_1", "dekho-magr-pyaar-se"),
                 ("Detail_2", "dekho-magr-pyaar-se-1"), ("Chapter_5", "215a0089"),
                 ("Backmatter_2", "215a0104-8192x5464")]),
    dict(slug="playground", num="06", title="Playground :)",
         cols=[["Limbo_Title Card", "Symbiosis_Branding Posters", "Other Futures_Event Poster", "Rathole_Letterpress Poster",
                "Untitled_1", "Untitled_3", "Insane!Me?_Poster"],
               ["Inklingroom_Event Poster_1", "Inklingroom_Brand Posters", "Other Futures_Brochure_1", "Other Futures_Brochure_3",
                "Aphonik_Motion Poster", "Untitled_5"],
               ["Seven Samurai_Movie Poster", "Inklingroom_Event Poster_2", "Other Futures_Brochure_2",
                "Divide & Rule_Letterpress Poster", "Untitled_2", "Iksh_Packaging"]],
         lead="A collection of various projects, posters, graphic studies, photography and just having fun as a Designer and Artist.",
         tags="Having fun...",
         hero="playground-dick-2-copy",
         copy=[],
         thumbs=[("Limbo_Title Card", "limbo"), ("Inklingroom_Event Poster_1", "untitled-19"),
                 ("Seven Samurai_Movie Poster", "free-poster-set-mockup-2"), ("Symbiosis_Branding Posters", "digital-billboard-mockup"),
                 ("Inklingroom_Event Poster_2", "posters-copy-2-page-0001"), ("Other Futures_Event Poster", "new-wave-poster-copy-01"),
                 ("Inklingroom_Brand Posters", "posters-under-the-bridge-copy-2"), ("Other Futures_Brochure_1", "avi-13"),
                 ("Other Futures_Brochure_2", "avi-26"), ("Other Futures_Brochure_3", "avi-25"),
                 ("Rathole_Letterpress Poster", "scan-2406x2977"), ("Divide & Rule_Letterpress Poster", "scan-2700x3573"),
                 ("Aphonik_Motion Poster", "aphonik-video"), ("Untitled_2", "img-0309"),
                 ("Untitled_1", "img-0294"), ("Untitled_5", "img-0582"),
                 ("Untitled_3", "img-0757-5472x3648"), ("Insane!Me?_Poster", "10-copy-4"),
                 ("Iksh_Packaging", "gravity-cardboard-boxes-mockup")]),
]

def home_section(p):
    href = f'{p["slug"]}.html'
    if p.get("cols"):                      # column layout copied from the Cargo site
        by_cap = dict(p["thumbs"])
        cols = [[(c, by_cap[c]) for c in col] for col in p["cols"]]
    else:
        cols = masonry([(c, k) for c, k in p["thumbs"]])
    colhtml = "".join(
        '<div class="col">' + "".join(thumb(c, k, href) for c, k in col) + "</div>" for col in cols
    )
    return f'''
<section class="proj{" cropped" if p.get("crop") else ""}" id="{p["slug"]}">
  <div class="phead">
    <a class="num" href="{href}" aria-label="{E(p["title"])}">{p["num"]}</a>
    <h2><a href="{href}">{E(p["title"])}</a></h2>
    <p class="lead">{E(p["lead"])}</p>
  </div>
  <a class="hero" href="{href}" aria-label="{E(p["title"])}">{media(p["hero"], alt=p["title"], eager=True, variant="hero")}</a>
  <div class="trow">
    <p class="tags">{E(p["tags"])}</p>
    <div class="masonry">{colhtml}</div>
    <div class="copy">{paras(p["copy"])}<a class="more" href="{href}">↗ See More</a></div>
  </div>
</section>'''

def build_home():
    body = '<div class="intro-gap"></div>\n' + "\n".join(home_section(p) for p in HOME)
    return shell("Avi Sahni — Graphic Designer", body, kind="home")

# --------------------------------------------------------------------------- about
RESUME = [
    ("Education", [
        dict(date="Sept 2023 — Dec 2026", head="ArtCenter College of Design", line="Bachelor of Fine Arts in Graphic Design with Distinction"),
        dict(date="Oct 2025", head="Pacific Edge Hotel Design Storm", line="A 3-day sprint with an interdisciplinary team of graphic, spatial, and industrial designers, where we developed a branding and spatial identity proposal for the Pacific Edge Hotel in Laguna Beach.", indent=True),
        dict(date="June 2026", head="Typographics Conference 2026", line="Attendance sponsored by the Hoffmitz Milken Center for Typography"),
        dict(date="Aug 2024", head="Adobe Creative Retreat", line="Attended, sponsored by the ArtCenter Graphic Design Department"),
    ]),
    ("Experience", [
        dict(date="Oct 2025 — Dec 2026", head="Lead Designer", head2="Freelance: Iksh Optometry, Defence Cart, Trunk, and GSSK",
             line="Developed visual identities and campaign systems for companies working across e-commerce, optometry, defence, consulting, and suppliments. Led teams of web, brand, and packaging designers to create brand identities that work across multiple mediums."),
        dict(date="Oct 2024 — Dec 2025", head="Graphic Design Assistant", meta="Pasadena, California", head2="Hoffmitz Milken Center for Typography (HMCT)",
             line="Designed publications, exhibitions, and graphics focused on typography, design history, and education, including ECAL: A Typographic Atlas, Primarium: A Case for Cursive, and Poski Projekt. Managed social media and newsletters to promote collections, workshops, and public programming."),
        dict(date="May 2024 — Dec 2026", head="Teaching Assistant", meta="Pasadena, California", head2="ArtCenter College of Design",
             lines=["Assisted Professor Brad Bartlett with his Advanced Transmedia Studio course. Led critiques of project ideas, typography layouts, and design systems. Helped students develop research driven projects culminating in a visually compelling, narrative-driven publication.",
                    "Assisted Professors Petrula Vrontikis and Sheharazad Fleming with their Grad Thesis 1: Portfolio Lab course. Provided critiques of student projects and web design. Helped students develop visually strong branding systems and strategies for their own identity.",
                    "Assisted Professor Pamela Olecki with her Communication Design 1 and 2 courses through project critiques, conceptual development, and technical guidance across branding, editorial, and exhibition-based assignments."]),
        dict(date="Aug 2026", head="Assistant Director", meta="Pasadena, California", head2="Levi Libre Freestyler",
             line="Managed all logistics, scheduling, and on-set operations of the production. Directed background actors, handled crew communication, and ensured safety regulations were met. The project received the following awards: Gold and Best of Show at American Advertising Federation Awards, Silver at People's Telly Awards, and Bronze at Telly Awards."),
        dict(date="Aug 2024 — Dec 2025", head="Teaching and Shop Assistant", meta="Pasadena, California", head2="Archetype Press",
             line="Supported artists in residence, workshops, and production at ArtCenter's letterpress studio, assisting with printmaking instruction, fabrication, and studio operations. Guided students through letterpress, balancing conceptual experimentation with technical production constraints. Collaborated with Amos Paul Kennedy, Jr. and Jessica Spring during their artist residencies, contributing to experimental workshops, and the production of typographic poster works including Civil Disobedience and When We Print, We Win."),
    ]),
    ("Recognition", [
        dict(date="Sept 2026", head="Finalist at Communication Arts 2027 Typography Competition", ital=["Right to Resist (Book)"]),
        dict(date="Dec 2023 — Dec 2026", head="ArtCenter Provost's List"),
        dict(date="Nov 2025", head="Awarded Outstanding Student Designer by AIGA Los Angeles"),
        dict(date="May 2024 — Ongoing", head="HMCT Gallery", ital=["Warnock Type Specimen (Poster)"]),
        dict(date="May 2024 — December 2026", head="ArtCenter Student Gallery",
             ital=["STFC Branding (Poster)", "Royal Albert Hall Branding (Posters)", "Dekho Magar Pyaar Se (Book)",
                   "Butterfly Boulder (Packaging)", "Other Futures (Poster)", "Paneer Makhni (Motion)"]),
        dict(date="November 2024", head="Featured by Cheryl D. Miller at AICAD Symposium 2024", ital=["Dekho Magar Pyaar Se (Book)"]),
    ]),
    ("ArtCenter Scholarships", [
        dict(date="Sept — Dec 2026", head="Duane and Betty Bohnstedt Endowed Scholarship"),
        dict(date="Sept 2023 — Dec 2026", head="ArtCenter Merit Scholarship"),
        dict(date="Jan — Aug 2026", head="Samsung Endowed Scholarship"),
        dict(date="May — Aug 2024", head="Kanter Scholarship for Excellence in Typography and Book Design"),
    ]),
]
SKILLS = [
    ("Strong working knowledge of", "InDesign, Photoshop, Illustrator, After Effects, MadMapper, Figma, Lightroom, Premiere Pro, and P5js"),
    ("Familiar with", "Framer, Glyphs 4, SolidWorks, Blender, KeyShot, and TouchOSC"),
    ("Skills", "Brand Identity, Typography, Editorial Design, Motion Design, Print Production, Spatial Graphics, Creative Coding, Photography, and Film Production"),
]
ABOUT_COLS = [  # column layout copied from the Cargo About page
    ["avi-sahni-portfolio-image-1", "about-a", "avi-sahni-portfolio-image-2", "about-c"],
    ["avi-sahni-portfolio-image-3", "about-b", "avi-sahni-portfolio-image-4", "other-futures-portfolio-2"],
    ["avi-sahni-portfolio-image-10", "avi-sahni-portfolio-dsc-0186", "avi-sahni-portfolio-image-9", "symbiosis-portfolio-image-5"],
]
ABOUT_BLURB = ("I like making things :) A journey through fine art, photography, film, and more has led me to graphic design. "
               "For me, it's a platform to express myself as an artist while continuing to bring others' visions to life. "
               "My design philosophy is total immersion in the project, becoming one with the history, culture, and context "
               "behind it through meticulous research and exploration.")

def entry(e):
    h = f'<div class="entry{" indent" if e.get("indent") else ""}"><p class="date">{E(e["date"])}</p>'
    h += f'<p class="b">{E(e["head"])}</p>'
    if e.get("meta"): h += f'<p>{E(e["meta"])}</p>'
    if e.get("head2"): h += f'<p class="b">{E(e["head2"])}</p>'
    for ln in ([e["line"]] if e.get("line") else []) + e.get("lines", []):
        h += f'<p class="d">{E(ln)}</p>'
    for it in e.get("ital", []):
        h += f'<p class="i">{E(it)}</p>'
    return h + "</div>"

def build_about():
    photos = "".join('<div class="col">' + "".join(thumb("", k, "#").replace('<a href="#">', '<span>').replace("</a>", "</span>") for k in col) + "</div>" for col in ABOUT_COLS)
    rows = ""
    for label, entries in RESUME:
        rows += f'<section class="rrow"><h3>{E(label)}</h3><div>{"".join(entry(e) for e in entries)}</div></section>'
    for label, text in SKILLS:
        rows += f'<section class="rrow short"><h3>{E(label)}</h3><div><p class="d">{E(text)}</p></div></section>'
    body = f'''
<div class="title-gap"></div>
<div class="phead about-head">
  <h1 class="big">Hello :)</h1>
  <h3 class="label">Nice to meet ya!</h3>
  <p class="lead">{E(PROFILE[0])}<br><span class="ind">{E(PROFILE[1])}</span></p>
</div>
<div class="wide">{media("ffea1552-cc6b-43ba-bbca-f2bf9564a1c2", alt="Avi Sahni on set beside a film camera", eager="high", variant="hero")}</div>
<div class="trow about-photos"><p class="tags">The sneak peek!</p><div class="masonry">{photos}</div><div class="copy"><p>{E(ABOUT_BLURB)}</p></div></div>
{rows}'''
    return shell("About — Avi Sahni", body, kind="about")

# --------------------------------------------------------------------------- project pages
def duo(keys, cls=""):
    """A justified row: widths follow aspect ratios so every item in the row has the same height."""
    tot = sum(ratio_w(k) for k in keys)
    items = "".join(media(k, cls, style=f"flex:{ratio_w(k):.4f} 1 0%",
                          sizes=f"(max-width: 720px) {100 * ratio_w(k) / tot:.0f}vw, {65 * ratio_w(k) / tot:.0f}vw") for k in keys)
    return f'<div class="duo">{items}</div>'

def ratio_w(key):
    d = m(key)
    return d["w"] / d["h"]

def pair_or_full(keys):
    """Lay out a run of media: landscape -> full width, portraits/squares pair up."""
    out, buf = [], []
    def flush():
        while buf:
            if len(buf) >= 2:
                a, b = buf.pop(0), buf.pop(0)
                out.append(duo([a, b]))
            else:                      # a lone image takes the whole column
                a = buf.pop(0)
                out.append(f'<div class="full">{media(a)}</div>')
    for k in keys:
        d = m(k)
        if d["w"] / d["h"] >= 1.15:
            flush()
            out.append(f'<div class="full">{media(k)}</div>')
        else:
            buf.append(k)
    flush()
    return "\n".join(out)

def sec(label, text, inner, ruled=False):
    t = ""
    if label: t += f'<h3>{E(label)}</h3>'
    if text: t += f'<p>{E(text)}</p>'
    cls = "psec ruled" if ruled else "psec"
    return f'<section class="{cls}"><div class="ptext">{t}</div><div class="pmedia">{inner}</div></section>'

def title_block(title, tags):
    return f'<div class="title-gap"></div><h1 class="big ptitle">{E(title)}</h1><hr class="rule">'

PAGES = {}

# Street Football Club — follows the recording
PAGES["stfc"] = dict(title="Street Football Club", tags="Branding, Motion, Creative Direction", body=lambda: "\n".join([
    sec("Logo Development",
        "The exploration for the main logo was divided in 2 rough categories: Badges and Typographic. The idea was to create a visual that captures the speed and chaos of the brand but also harkens back to football and street culture.",
        duo(["typographic", "badges"], cls="invert")),
    f'<div class="full">{media("aug-27-screenshot-from-aviportfoliogx")}</div>',
    sec("Core Branding",
        "The utilitarian look is for the base that shall create contrast between the identities for the cities. The green and grey are inspired by asphalt and moss as seen on the streets.",
        f'<div class="full">{media("stfc-hero-video")}</div>'),
    duo(["stfc-aviportfoliogx-1", "stfc-free-poster-mockup-4"]),
    f'<div class="full">{media("stfc-305-copy-8")}</div>',
    f'<div class="full">{media("stfc-laptop-large")}</div>',
    sec("",
        "Each city got a unique identity, with typography and colors that show the vibrance and chaos of the football scene in each city.",
        f'<div class="full">{media("cities")}</div>', ruled=True),
    f'<div class="full">{media("stfc-3artboard-26")}</div>',
    duo(["motion-video", "stfc-arena-2"]),
    pair_or_full(["stfc-insta", "stfc-3artboard-26-copy", "stfc-arena", "stfc-poster",
                  "stfc-austin-poster", "stfc-arena-3", "stfc-poster-wall"]),
]))

def gallery_page(slug, keys, extra=""):
    return lambda: "\n".join([extra, pair_or_full(keys)])

def lead_sec(slug):
    p = next(x for x in HOME if x["slug"] == slug)
    return sec("", p["lead"], "")

def copy_sec(slug, label=""):
    p = next(x for x in HOME if x["slug"] == slug)
    return f'<section class="psec"><div class="ptext">{paras(p["copy"])}</div><div class="pmedia"></div></section>'

def full(k, **kw):
    return f'<div class="full">{media(k, **kw)}</div>'

PAGES["rah"] = dict(title="Royal Albert Hall", tags="Branding, Creative Direction", body=lambda: "\n".join([
    # arrangement follows the rows of the original Cargo page
    sec("", next(x for x in HOME if x["slug"] == "rah")["copy"][0],
        full("rah-logos-black", alt="Royal Albert Hall logo explorations")),
    duo(["rah-brand-poster-expo-26", "rah-brand-poster-expo-25", "rah-brand-poster-expo-22", "rah-brand-poster-expo-2"]),
    duo(["rah-brand-poster-5", "rah-brand-poster-4", "rah-brand-poster-3", "rah-rah-brand-poster"]),
    sec("", next(x for x in HOME if x["slug"] == "rah")["copy"][1], full("rah-aviportfoliogx")),
    duo(["rah-royal-albert-hall-nov-2012-1", "rah-1"]),
    full("rah-uk23lon0175-copy"),
    duo(["rah-screenshot-2025-08-17-at-1-27-16am", "rah-screenshot-2025-08-17-at-1-27-23am"]),
    full("rah-screenshot-2025-08-17-at-1-27-30am"),
    duo(["rah-screenshot-2025-08-17-at-1-28-06am-copy", "rah-screenshot-2025-08-17-at-1-28-36am-copy",
         "rah-screenshot-2025-08-17-at-1-28-42am-copy", "rah-screenshot-2025-08-17-at-1-29-31am-copy"]),
    full("rah-royal-albert-hall"),
    sec("", next(x for x in HOME if x["slug"] == "rah")["copy"][2], full("rah-outdoor-screen-mockup-copy")),
    duo(["freight-video-8", "rah-free-ticket-mockup-3-copy"]),
    full("rah-uk24lon278-copy"),
    duo(["rah-uk23lon0554-copy", "rah-uk23lon0177-copy"]),
    full("rah-vinyl-template-c-copy"),
    full("rah-uk23lon0403-copy"),
    full("rah-scene-with-iphone-16-pro-mockups-v1-front-vew-copy"),
]))

PAGES["hyperyouth"] = dict(title="Hyperyouth", tags="Generative design, Branding", body=lambda: "\n".join([
    # arrangement follows the rows of the original Cargo page
    sec("", next(x for x in HOME if x["slug"] == "hyperyouth")["lead"], full("hyperyouth-hystage")),
    full("hy-motion-2"),
    duo(["hy-motion-1", "hyperyouth-hy-banner"]),
    full("hyperyouth-vnhy"),
    sec("", next(x for x in HOME if x["slug"] == "hyperyouth")["copy"][0], full("hy-code-demo")),
]))

R2R = json.load(open(os.path.join(ROOT, "tools", "r2r-content.json")))

def slideshow(keys, label):
    first = m(keys[0])
    imgs = []
    for i, k in enumerate(keys):
        d = m(k); f = pick(k, "hero")
        if i == 0:
            imgs.append(f'<img class="on" src="{f["src"]}" width="{d["w"]}" height="{d["h"]}" alt="{E(label)} — spread 1" decoding="async">')
        else:
            imgs.append(f'<img data-src="{f["src"]}" width="{d["w"]}" height="{d["h"]}" alt="{E(label)} — spread {i+1}" decoding="async">')
    n = len(keys)
    return (f'<div class="slides" data-slides tabindex="0" role="group" aria-roledescription="slideshow" aria-label="{E(label)}">'
            f'<div class="stage" style="aspect-ratio:{first["w"]}/{first["h"]}">{"".join(imgs)}</div>'
            f'<div class="ctl"><span class="count" aria-live="polite">1 / {n}</span>'
            f'<span class="arrows"><button type="button" data-prev aria-label="Previous">←</button>'
            f'<button type="button" data-next aria-label="Next">→</button></span></div></div>')

def trio(keys):
    return duo(keys)

def r2r_body():
    out, blocks = [], R2R[2:]       # skip the site-wide about blurb and the portrait
    it = blocks[0]["items"]
    out.append(f'<div class="full">{media("avi-portfolio-video")}</div>')
    # the colour / type paragraphs sit beside the opening spreads, under a "Frontmatter" heading
    front = f'<p>{E(it[3])}</p><p>{E(it[4])}</p>'
    pending = ("Frontmatter", '<h3>Frontmatter</h3>', None)
    for b in blocks[2:]:
        if b["type"] == "text":
            t = b["items"]
            if len(t) == 1:
                label, text = t[0], ""
                head = f'<h3>{E(label)}</h3>'
            else:
                label = t[0].replace("&2", "& 2")
                head = f'<h3>{E(label)}</h3>' + "".join(f'<p class="b">{E(x)}</p>' for x in t[1:-1])
                text = t[-1]
            pending = (label, head, text)
        elif b["type"] == "gallery-slideshow":
            if pending:
                lab, head, text = pending
                body = front if text is None else (f'<p>{E(text)}</p>' if text else "")
                out.append(f'<section class="psec"><div class="ptext">{head}{body}</div><div class="pmedia">{slideshow(b["items"], lab)}</div></section>')
                pending = None
            else:
                out.append(f'<div class="full">{slideshow(b["items"], "Spreads")}</div>')
        elif b["type"] == "gallery-justify":
            out.append(trio(b["items"]))
    return "\n".join(out)

PAGES["right-to-resist"] = dict(title="Right to Resist", tags="Publication", body=r2r_body)

DEKHO_SLIDES = ["dekho-215a0010", "dekho-215a0012", "dekho-215a0020", "dekho-215a0024", "dekho-215a0028", "dekho-215a0030", "dekho-215a0033", "dekho-215a0035", "dekho-215a0038", "dekho-215a0042", "dekho-215a0045", "dekho-215a0047", "dekho-215a0055", "dekho-215a0061", "dekho-215a0063", "dekho-215a0065", "dekho-215a0067", "dekho-215a0069", "dekho-215a0073", "dekho-215a0077", "dekho-215a0079", "dekho-215a0081", "dekho-215a0085", "dekho-215a0087", "dekho-215a0089", "dekho-215a0090", "dekho-215a0093", "dekho-215a0096", "dekho-215a0099", "dekho-215a0104", "dekho-215a0106", "dekho-215a0109", "dekho-215a0112"]

PAGES["dekho"] = dict(title="Dekho Magar Pyaar Se", tags="Publication, Posters, Motion", body=lambda: "\n".join([
    # process photos first, then the rows of the original Cargo page
    sec("", next(x for x in HOME if x["slug"] == "dekho")["copy"][0],
        full("dekho-jan-21-screenshot-from-avi-sahni")),
    duo(["dekho-jan-21-screenshot-from-avi-sahni-1", "dekho-jan-21-screenshot-from-avi-sahni-2"]),
    '<hr class="sep">',
    full("aviportfoliogx-img-1739"),
    duo(["dekho-215a0102", "dekho-215a0120"]),
    full("dekho-10-copy-2"),
    duo(["dekho-215a0124", "dekho-215a0039"]),
    f'<div class="full">{slideshow(DEKHO_SLIDES, "Dekho Magar Pyaar Se spreads")}</div>',
    '<hr class="sep">',
    full("dekho-free-billboard-mockup-1"),
    duo(["mp2-video", "freight-cargo-video", "dekho-mp3-video"]),
]))

PG_KEYS = ["playground-dick-2-copy", "limbo", "untitled-19", "new-wave-poster-copy-01", "playground-untitled-110-copy",
           "playground-insane-me-poster", "playground-posters-copy-page-0001-copy", "posters-copy-2-page-0001",
           "playground-img-8532-copy", "avi-25", "avi-26", "other-futures-portfolio-2", "avi-13",
           "scan-2700x3573", "scan-2406x2977", "aphonik-video", "posters-under-the-bridge-copy-2",
           "free-poster-set-mockup-2", "gravity-cardboard-boxes-mockup", "playground-img-0312", "playground-img-0495",
           "playground-img-0711", "img-0757-5472x3648", "img-0294", "img-0309", "img-0582", "symbiosis-portfolio-image-5",
           "playground-font-poster", "playground-font-poster-final", "playground-p301-video",
           "playground-p301-1", "playground-p301-2", "playground-p301-3", "playground-p301-4", "playground-p301-5", "playground-p301-6"]

def playground_body():
    items = []
    for k in PG_KEYS:
        d = m(k)
        f = pick(k, "hero")
        items.append({"s": f["src"], "w": d["w"], "h": d["h"], "v": d["src"].endswith(".mp4")})
        if d["src"].endswith(".mp4"):
            items[-1]["s"] = d["src"]
    data = E(json.dumps(items, separators=(",", ":")))
    return f'<div class="pg-stage" id="pg-stage" data-items="{data}" aria-label="Playground"></div>'

PAGES["playground"] = dict(title="Playground :) Press the spacebar.", tags="", cls="pg", body=playground_body)

def build_project(slug):
    p = PAGES[slug]
    global AUDIO_PAGE
    AUDIO_PAGE = slug == "hyperyouth"
    body = title_block(p["title"], p["tags"]) + "\n" + p["body"]()
    AUDIO_PAGE = False
    # Project pages load every image straight away (the files are small), the first two at high priority
    body = body.replace(' loading="lazy"', "")
    body = body.replace('<img class="', '<img fetchpriority="high" class="', 2) if "fetchpriority" not in body else body
    return shell(f'{p["title"]} — Avi Sahni', body, kind="project", current=slug, extra_cls=p.get("cls", ""))

def main():
    out = {"index.html": build_home(), "about.html": build_about()}
    for slug in PAGES:
        out[f"{slug}.html"] = build_project(slug)
    for name, text in out.items():
        open(os.path.join(ROOT, "public", name), "w", encoding="utf8").write(text)
    print("wrote", ", ".join(out))
    if MISSING:
        raise SystemExit("missing media keys: " + ", ".join(sorted(MISSING)))

if __name__ == "__main__":
    main()
