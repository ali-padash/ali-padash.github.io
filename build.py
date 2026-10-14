"""Generate index.html and projects/<slug>.html from projects.json.

Usage:  python build.py
Text in projects.json is trusted HTML (it is our own content); attribute values are escaped.
"""
import json
import os
from html import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(ROOT, "projects.json"), encoding="utf-8"))
SITE = DATA["site"]
PROJECTS = DATA["projects"]
TIER_LABEL = {1: "Featured project", 2: "Course project"}


def attr(s):
    return escape(str(s), quote=True)


def grade_text(p):
    g = p.get("grade")
    if g is None or g < 17:  # grades are only shown from 17 / 20 upwards
        return None
    return f"{g:g} / 20"


def inline_svg(path):
    svg = open(os.path.join(ROOT, path), encoding="utf-8").read()
    return svg[svg.index("<svg"):]


ICONS = {
    "github": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 .5a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.53-1.33-1.28-1.69-1.28-1.69-1.05-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.56-.29-5.25-1.28-5.25-5.68 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.41-2.7 5.38-5.27 5.67.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5Z"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13ZM7.12 20.45H3.56V9h3.56v11.45ZM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0Z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M3 5h18v14H3z M3 6l9 7 9-7"/></svg>',
    "sun": '<svg class="i-sun" viewBox="0 0 24 24" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 1.5v2.5M12 20v2.5M4.6 4.6l1.8 1.8M17.6 17.6l1.8 1.8M1.5 12H4M20 12h2.5M4.6 19.4l1.8-1.8M17.6 6.4l1.8-1.8"/></g></svg>',
    "moon": '<svg class="i-moon" viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11Z"/></svg>',
    "download": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 3v12m-5-5 5 5 5-5M4 20h16"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M5 12h14m-6-6 6 6-6 6"/></svg>',
    "back": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M19 12H5m6 6-6-6 6-6"/></svg>',
    "external": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M14 4h6v6m0-6-9 9M18 14v6H4V6h6"/></svg>',
}

FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect width='64' height='64' rx='14' fill='%23012D6A'/%3E"
    "%3Ctext x='32' y='42' font-family='Georgia,serif' font-size='28' font-weight='700' "
    "fill='white' text-anchor='middle'%3EAP%3C/text%3E%3C/svg%3E"
)

# Applied before CSS loads so the page never flashes the wrong theme.
THEME_INIT = (
    "<script>try{var t=localStorage.getItem('theme');"
    "if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;}catch(e){}</script>"
)


def head(title, description, prefix, canonical):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{attr(description)}">
<meta name="author" content="{attr(SITE['name'])}">
<meta property="og:title" content="{attr(title)}">
<meta property="og:description" content="{attr(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{attr(canonical)}">
<link rel="canonical" href="{attr(canonical)}">
<link rel="icon" href="{FAVICON}">
<meta name="color-scheme" content="light dark">
{THEME_INIT}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,500;0,700;1,400&family=Roboto+Slab:wght@500;700&display=swap">
<link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""


def cv_button(prefix):
    """The Download CV button, left out until the CV file has been added."""
    if not os.path.exists(os.path.join(ROOT, SITE["cv"])):
        return ""
    return f"""<a class="btn btn-cv" href="{prefix}{SITE['cv']}" download>{ICONS['download']}<span>Download CV</span></a>"""


def topbar(prefix):
    home = f"{prefix}index.html"
    return f"""<header class="topbar">
  <div class="wrap topbar-inner">
    <a class="brand" href="{home}"><span class="brand-full">{escape(SITE['name'])}</span><span class="brand-short">{escape(SITE['short_name'])}</span></a>
    <nav class="topnav" aria-label="Main">
      <a href="{home}#projects">Projects</a>
      <a href="{home}#contact">Contact</a>
    </nav>
    <button class="theme-toggle" type="button" aria-label="Switch between light and dark theme">{ICONS['sun']}{ICONS['moon']}</button>
    {cv_button(prefix)}
  </div>
</header>"""


def footer(prefix):
    return f"""<footer class="footer">
  <div class="wrap">© {SITE['year']} {escape(SITE['name'])}</div>
</footer>
<script src="{prefix}theme.js"></script>
</body>
</html>
"""


def meta_line(p):
    bits = [p["when"]]
    if p.get("course"):
        bits.append(escape(p["course"]))
    elif p.get("kind"):
        bits.append(escape(p["kind"]))
    return " · ".join(bits)


def grade_badge(p):
    g = grade_text(p)
    label = p.get("grade_label", "Course grade")
    return f'<span class="grade" title="{attr(label)}">{g}</span>' if g else ""


def card_media(p):
    im = p.get("card_image") or (p["images"][0] if p.get("images") else None)
    if im:
        fit = " media-contain" if im.get("fit") == "contain" else ""
        pos = f' style="object-position:{attr(im["position"])}"' if im.get("position") else ""
        return (f'<div class="card-media{fit}"><img src="{attr(im["src"])}" alt="{attr(im["alt"])}" '
                f'loading="lazy" decoding="async"{pos}></div>')
    if p.get("diagram"):
        return f'<div class="card-media media-diagram" aria-hidden="true">{inline_svg(p["diagram"])}</div>'
    return ""


def card(p):
    tags = "".join(f"<li>{escape(t)}</li>" for t in p["tags"][:4])
    team = f'<span class="team">{escape(p["team"])}</span>' if p.get("team") else ""
    return f"""<article class="card card-t{p['tier']}">
  <a class="card-link" href="projects/{p['slug']}.html" aria-label="{attr(p['title'])}: read more"></a>
  {card_media(p)}
  <div class="card-body">
    <p class="card-meta">{meta_line(p)} {grade_badge(p)}</p>
    <h3 class="card-title">{escape(p['title'])}</h3>
    <p class="card-summary">{p['summary']}</p>
    <ul class="tags">{tags}</ul>
    <p class="card-foot">{team}<span class="more">Read more {ICONS['arrow']}</span></p>
  </div>
</article>"""


def minor_row(p):
    g = grade_text(p)
    grade = f'<span class="grade">{g}</span>' if g else ""
    tags = "".join(f"<li>{escape(t)}</li>" for t in p["tags"])
    return f"""<details class="minor" id="{p['slug']}">
  <summary>
    <span class="minor-title">{escape(p['title'])}</span>
    <span class="minor-meta">{escape(p['course'])} · {p['when']} {grade}</span>
  </summary>
  <div class="minor-body">
    <p>{p['details']}</p>
    <ul class="tags">{tags}</ul>
  </div>
</details>"""


GENDERS = [("der", "masculine"), ("die", "feminine"), ("das", "neuter"), ("die", "plural")]


def spotlight(p):
    s = p["spotlight"]
    points = "".join(f"<li>{pt}</li>" for pt in s["points"])
    legend = "".join(
        f'<li class="g-{i}"><span class="g-dot"></span><b>{art}</b> {label}</li>'
        for i, (art, label) in enumerate(GENDERS)
    )
    links = "".join(
        f'<a class="btn btn-light" href="{attr(l["url"])}" target="_blank" rel="noopener">{escape(l["label"])} {ICONS["external"]}</a>'
        for l in p.get("links", [])
    )
    return f"""<section id="projects" class="spotlight" aria-labelledby="spotlight-title">
    <div class="wrap spotlight-inner">
      <div class="spotlight-text">
        <p class="eyebrow">{escape(s['eyebrow'])}</p>
        <h2 id="spotlight-title">{escape(p['title'])}</h2>
        <p class="spotlight-pitch">{s['pitch']}</p>
        <ul class="gender-legend" aria-label="Noun colours">{legend}</ul>
        <ul class="spotlight-points">{points}</ul>
        <div class="spotlight-actions">
          <a class="btn btn-primary" href="projects/{p['slug']}.html">How it works {ICONS['arrow']}</a>
          {links}
        </div>
      </div>
      <a class="spotlight-media" href="projects/{p['slug']}.html" tabindex="-1" aria-hidden="true">
        <img src="{attr(s['image']['src'])}" alt="{attr(s['image']['alt'])}" width="1400" height="788" decoding="async">
      </a>
    </div>
  </section>"""


def build_index():
    spot = next((p for p in PROJECTS if p.get("spotlight")), None)
    t1 = [p for p in PROJECTS if p["tier"] == 1 and p is not spot]
    t2 = [p for p in PROJECTS if p["tier"] == 2]
    t3 = [p for p in PROJECTS if p["tier"] == 3]
    areas = []
    for p in t3:
        if p["area"] not in areas:
            areas.append(p["area"])
    minor = "".join(
        f'<div class="minor-group"><h4 class="minor-area">{escape(a)}</h4>'
        + "".join(minor_row(p) for p in t3 if p["area"] == a) + "</div>"
        for a in areas
    )
    about = "".join(f"<p>{para}</p>" for para in SITE["about"])
    email_fallback = f"{SITE['email_user']} [at] {SITE['email_domain'].replace('.', ' [dot] ')}"
    links = f"""<ul class="links">
        <li><a href="{attr(SITE['github'])}" rel="me">{ICONS['github']}<span>GitHub</span></a></li>
        <li><a href="{attr(SITE['linkedin'])}" rel="me">{ICONS['linkedin']}<span>LinkedIn</span></a></li>
        <li><a class="js-email" href="#contact" data-u="{attr(SITE['email_user'])}" data-d="{attr(SITE['email_domain'])}">{ICONS['mail']}<span>Email</span></a></li>
      </ul>"""
    desc = (f"Projects of {SITE['name']}, Computer Engineering graduate of K. N. Toosi University of Technology: "
            "machine learning, NLP, computer vision, software and hardware design.")
    html = head(f"{SITE['name']} · Projects", desc, "", SITE["url"] + "/") + topbar("") + f"""
<main id="main">
  <section class="intro">
    <div class="wrap intro-inner">
      <img class="avatar" src="img/photo.webp" alt="Portrait of {attr(SITE['name'])}" width="168" height="168">
      <div class="intro-text">
        <p class="eyebrow">{escape(SITE['tagline'])}</p>
        <h1>{escape(SITE['name'])}</h1>
        <div class="about">{about}</div>
        {links}
      </div>
    </div>
  </section>

  {spotlight(spot) if spot else ''}

  <section {'' if spot else 'id="projects" '}class="wrap section">
    <header class="section-head">
      <h2>Featured projects</h2>
      <p>The work on my CV, each with its own page.</p>
    </header>
    <div class="grid grid-t1">{''.join(card(p) for p in t1)}</div>
  </section>

  <section class="wrap section">
    <header class="section-head">
      <h2>Course projects</h2>
      <p>Larger projects from my BSc courses. Grades are course grades out of 20.</p>
    </header>
    <div class="grid grid-t2">{''.join(card(p) for p in t2)}</div>
  </section>

  <section class="wrap section">
    <header class="section-head">
      <h2>More coursework</h2>
      <p>Smaller assignments and lab series. Open a row for details.</p>
    </header>
    <div class="minor-list">{minor}</div>
  </section>

  <section id="contact" class="wrap section contact">
    <header class="section-head">
      <h2>Contact</h2>
      <p>I'm happy to share code, reports or more detail on any project.</p>
    </header>
    <p class="email-line">Email: <a class="js-email js-email-text" href="#contact" data-u="{attr(SITE['email_user'])}" data-d="{attr(SITE['email_domain'])}">{email_fallback}</a></p>
    {links}
  </section>
</main>
""" + footer("")
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8", newline="\n").write(html)


def figure(im, cls="shot"):
    fit = " fig-contain" if im.get("fit") == "contain" else ""
    cap = f"<figcaption>{im['caption']}</figcaption>" if im.get("caption") else ""
    pos = f' style="object-position:{attr(im["position"])}"' if im.get("position") else ""
    return (f'<figure class="{cls}{fit}"><a href="../{attr(im["src"])}" target="_blank" rel="noopener">'
            f'<img src="../{attr(im["src"])}" alt="{attr(im["alt"])}" loading="lazy" decoding="async"{pos}></a>{cap}</figure>')


def build_project(p, prev_p, next_p):
    facts = [("When", p["when"])]
    if p.get("course"):
        facts.append(("Course", escape(p["course"])))
    elif p.get("kind"):
        facts.append(("Type", escape(p["kind"])))
    if grade_text(p):
        facts.append((p.get("grade_label", "Course grade"), grade_text(p)))
    if p.get("team"):
        facts.append(("Team", escape(p["team"])))
    facts_html = "".join(f"<div><dt>{escape(k)}</dt><dd>{v}</dd></div>" for k, v in facts)
    tags = "".join(f"<li>{escape(t)}</li>" for t in p["tags"])

    images = list(p.get("images", []))
    if p.get("diagram"):
        hero = f'<figure class="hero hero-diagram">{inline_svg(p["diagram"])}</figure>'
    elif images:
        hero = figure(images.pop(0), "hero")
    else:
        hero = ""
    did = "".join(f"<li>{d}</li>" for d in p["did"])
    results = ""
    if p.get("results"):
        items = "".join(f"<li>{r}</li>" for r in p["results"])
        results = f'<h2>{escape(p.get("results_title", "Results"))}</h2><ul class="results">{items}</ul>'
    note = f'<p class="note">{p["note"]}</p>' if p.get("note") else ""
    gallery = (f'<h2>Gallery</h2><div class="gallery">{"".join(figure(im) for im in images)}</div>'
               if images else "")
    links = ""
    if p.get("links"):
        links = '<div class="project-links">' + "".join(
            f'<a class="btn btn-ghost" href="{attr(l["url"])}" target="_blank" rel="noopener">{escape(l["label"])} {ICONS["external"]}</a>'
            for l in p["links"]) + "</div>"

    def pager_link(q, rel, label):
        if not q:
            return "<span></span>"
        return (f'<a class="pager-{rel}" href="{q["slug"]}.html" rel="{rel}">'
                f'<span class="pager-label">{label}</span><span class="pager-title">{escape(q["title"])}</span></a>')

    html = head(f"{p['title']} · {SITE['name']}", p["summary"].replace("<em>", "").replace("</em>", ""), "../",
                f"{SITE['url']}/projects/{p['slug']}.html") + topbar("../") + f"""
<main id="main" class="wrap project">
  <a class="back" href="../index.html#projects">{ICONS['back']}All projects</a>
  <header class="project-head">
    <p class="eyebrow">{TIER_LABEL[p['tier']]}</p>
    <h1>{escape(p['title'])}</h1>
    <p class="lead">{p['summary']}</p>
    <dl class="facts">{facts_html}</dl>
    <ul class="tags">{tags}</ul>
    {links}
  </header>
  {hero}
  <div class="prose">
    <h2>Overview</h2>
    <p>{p['overview']}</p>
    <h2>What I did</h2>
    <ul>{did}</ul>
    {results}
    {note}
  </div>
  {gallery}
  <nav class="pager" aria-label="More projects">{pager_link(prev_p, 'prev', 'Previous')}{pager_link(next_p, 'next', 'Next')}</nav>
</main>
""" + footer("../")
    os.makedirs(os.path.join(ROOT, "projects"), exist_ok=True)
    open(os.path.join(ROOT, "projects", f"{p['slug']}.html"), "w", encoding="utf-8", newline="\n").write(html)


def main():
    build_index()
    paged = [p for p in PROJECTS if p["tier"] in (1, 2)]
    for i, p in enumerate(paged):
        build_project(p, paged[i - 1] if i else None, paged[i + 1] if i + 1 < len(paged) else None)
    print(f"Built index.html and {len(paged)} project pages.")
    if not os.path.exists(os.path.join(ROOT, SITE["cv"])):
        print(f"Note: {SITE['cv']} is missing; the Download CV button is hidden until you add it.")


if __name__ == "__main__":
    main()
