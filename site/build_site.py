#!/usr/bin/env python3
"""Builds the Redraft Studio site into ../docs (served by GitHub Pages).
Usage: python3 site/build_site.py [/mnt/project-files]
Reads listing copy and store images from the project folders, so one run
refreshes every landing page."""
import html, json, sys, shutil
from pathlib import Path
from PIL import Image

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files")
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "docs"
BASE = "https://bangreedy-2.github.io/DPF/"
G = "https://redraftstudio.gumroad.com/l/"
UTM = "?utm_source=site&utm_medium=landing&utm_campaign="

# slug, folder, title, one-line pitch, price, paid permalink, free-kit name, free permalink
P = [
 ("job-search-planner", "job-seeker-planner", "Job Search Planner & Application Tracker",
  "A printable planner and Google Sheets tracker that works out your follow-ups for you.", "9.49", "muiyav",
  "Free Job Application Follow-Up Kit", "rciznr"),
 ("notion-job-search-tracker", "job-search-notion", "Job Search HQ: Notion Job Application Tracker",
  "A Notion job tracker with automatic follow-up reminders, interview prep and a cover letter builder.", "12.00", "evbys",
  "Free Job Application Follow-Up Kit", "rciznr"),
 ("chronic-illness-symptom-tracker", "chronic-illness-tracker", "Chronic Illness Symptom Tracker & Doctor Visit Planner",
  "Log symptoms in 30 seconds and hand your doctor a one-page summary.", "8.99", "lynufk",
  "Free Doctor Visit Kit", "kyngij"),
 ("iep-binder-for-parents", "iep-binder", "IEP Binder for Parents",
  "Track service minutes, follow every goal and walk into IEP meetings prepared.", "9.49", "rpvfgr",
  "Free IEP Meeting Prep Kit", "fpcuin"),
 ("diabetic-meal-planner", "diabetic-meal-planner", "Diabetic Meal Planner with 60 Recipes & Carb Counts",
  "60 diabetes-friendly recipes with carb counts and a planner that builds your grocery list.", "9.90", "teuxho",
  "Free Diabetes Label-Reading Cheat Sheet", "hxxhuc"),
 ("adhd-daily-planner", "adhd-daily-planner", "One-Page ADHD Daily Planner",
  "An undated one-page daily planner built for ADHD brains, with digital and Notion versions.", "9.99", "xtbgbv",
  "Free ADHD Overwhelm Kit", "rntgg"),
 ("homeschool-planner", "homeschool-planner", "Homeschool Planner & Record Keeper",
  "Plan a week for 1 to 4 kids on one page and keep the records your state asks for.", "9.99", "jaxtn",
  "Free Homeschool Records Starter Kit", "uzjftr"),
 ("glp1-tracker", "glp1-tracker", "GLP-1 Weight Loss Tracker",
  "Shot log, injection site rotation, protein and water planner in one tracker.", "8.99", "cocqmv",
  "Free GLP-1 Shot Day Kit", "rhdvd"),
 ("aging-parent-care-binder", "aging-parent-caregiver-binder", "Aging Parent Care Binder",
  "A fillable caregiver binder, sibling task sheet and family tracker for looking after a parent.", "12.99", "mcjvn",
  "Free Parent Emergency Info Kit", "avkexu"),
 ("sourdough-baking-log", "sourdough-baking-log", "Sourdough Baking Log & Starter Guide",
  "A printable sourdough journal with a troubleshooting chart and baker's percentage cheat sheet.", "6.99", "ivopdz",
  "Free Sourdough Starter Rescue Kit", "zftaxl"),
]

CSS = """
:root{--ink:#1d2433;--mut:#5b6475;--bg:#faf8f4;--card:#fff;--acc:#1f5f5b;--acc2:#e9a23b;--line:#e6e1d8}
*{box-sizing:border-box}body{margin:0;font:17px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--acc)}header.top{border-bottom:1px solid var(--line);background:var(--card)}
.wrap{max-width:980px;margin:0 auto;padding:0 16px}.top .wrap{display:flex;justify-content:space-between;align-items:center;height:56px}
.brand{font-weight:800;text-decoration:none;color:var(--ink);letter-spacing:-.01em}
h1{font-size:clamp(28px,5vw,42px);line-height:1.15;margin:28px 0 10px;letter-spacing:-.02em}
h2{font-size:24px;margin:32px 0 8px}h3{font-size:19px;margin:24px 0 6px}
.lead{font-size:20px;color:var(--mut);margin:0 0 18px}
.btn{display:inline-block;background:var(--acc);color:#fff;text-decoration:none;font-weight:700;padding:14px 22px;border-radius:10px}
.btn.alt{background:transparent;color:var(--acc);border:2px solid var(--acc)}
.cta{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0 8px}.small{font-size:14px;color:var(--mut)}
img{max-width:100%;height:auto;border-radius:12px;border:1px solid var(--line);display:block}
.hero{margin:20px 0}.shots{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;margin:20px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:18px;margin:24px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;text-decoration:none;color:inherit;display:flex;flex-direction:column}
.card img{border:0;border-radius:0}.card div{padding:14px 16px}.card b{display:block;line-height:1.3}.card span{color:var(--mut);font-size:15px}
.free{background:#fff7e6;border:1px solid #f1d9a6;border-radius:14px;padding:18px 20px;margin:28px 0}
.body{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:6px 22px 18px;margin:20px 0}
footer{border-top:1px solid var(--line);margin-top:48px;padding:24px 0;color:var(--mut);font-size:14px}
"""

def page(path, title, desc, body, extra_head=""):
    depth = path.count("/")
    root = "../" * depth
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{BASE}{path.replace('index.html','')}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Redraft Studio">{extra_head}
<link rel="stylesheet" href="{root}style.css"></head><body>
<header class="top"><div class="wrap"><a class="brand" href="{root}">Redraft Studio</a><a href="{root}#free">Free kits</a></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap">Redraft Studio. Every product is a second, better draft. Instant digital downloads, sold through Gumroad.
Planning tools only, not medical, legal or financial advice.</div></footer></body></html>"""
    f = OUT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(doc)

def jpg(src, dst, w=1200):
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(dst, "JPEG", quality=82, optimize=True)

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "style.css").write_text(CSS)
    (OUT / ".nojekyll").write_text("")
    urls, cards, frees = [""], [], []
    for slug, folder, title, pitch, price, pid, fname, fid in P:
        store = SRC / folder / "marketing" / "store"
        shots = sorted(store.glob("gumroad-0*.png")) or [store / "payhip-cover-1280x720.png"]
        names = []
        for s in shots[:6]:
            n = s.stem + ".jpg"
            jpg(s, OUT / slug / n)
            names.append(n)
        jpg(store / "payhip-cover-1280x720.png", OUT / slug / "cover.jpg", 900)
        d = SRC / folder / "listing" / "gumroad-description.html"
        if not d.exists():
            d = HERE / "desc" / f"{folder}.html"
        desc = d.read_text() if d.exists() else f"<p>{html.escape(pitch)}</p>"
        buy = f"{G}{pid}{UTM}{slug}"
        free = f"{G}{fid}{UTM}{slug}-free"
        ld = json.dumps({"@context": "https://schema.org", "@type": "Product", "name": title, "description": pitch,
                         "image": f"{BASE}{slug}/{names[0]}", "brand": {"@type": "Brand", "name": "Redraft Studio"},
                         "offers": {"@type": "Offer", "price": price, "priceCurrency": "USD",
                                    "availability": "https://schema.org/InStock", "url": buy}})
        head = f'<meta property="og:image" content="{BASE}{slug}/{names[0]}"><script type="application/ld+json">{ld}</script>'
        gal = "".join(f'<img loading="lazy" src="{n}" alt="{html.escape(title)} preview {i+2}">' for i, n in enumerate(names[1:]))
        body = f"""<h1>{html.escape(title)}</h1><p class="lead">{html.escape(pitch)}</p>
<div class="cta"><a class="btn" href="{buy}">Get it for ${price}</a><a class="btn alt" href="{free}">Try the free kit first</a></div>
<p class="small">Instant download. Pay once, print as often as you like.</p>
<img class="hero" src="{names[0]}" alt="{html.escape(title)}">
<div class="body">{desc}</div><div class="shots">{gal}</div>
<div class="free"><h2 style="margin-top:0">Not sure yet? Start with the free kit.</h2>
<p>{html.escape(fname)}: a few pages from the same system, free to download and print.</p>
<a class="btn" href="{free}">Download the free kit</a></div>
<div class="cta"><a class="btn" href="{buy}">Get the full version for ${price}</a></div>"""
        page(f"{slug}/index.html", f"{title} | Redraft Studio", pitch, body, head)
        urls.append(slug + "/")
        cards.append(f'<a class="card" href="{slug}/"><img loading="lazy" src="{slug}/cover.jpg" alt="{html.escape(title)}"><div><b>{html.escape(title)}</b><span>{html.escape(pitch)} ${price}</span></div></a>')
        if fid not in [x[0] for x in frees]:
            frees.append((fid, fname, slug))
    fl = "".join(f'<li><a href="{G}{fid}{UTM}home-free">{html.escape(n)}</a></li>' for fid, n, s in frees)
    home = f"""<h1>Planners and trackers that fix what the others get wrong.</h1>
<p class="lead">We read what people say isn't working in popular planners and trackers, then build the second, better draft.</p>
<div class="grid">{''.join(cards)}</div>
<div class="free" id="free"><h2 style="margin-top:0">Free kits</h2><p>Free printable starter kits. No card needed.</p><ul>{fl}</ul></div>"""
    page("index.html", "Redraft Studio: printable planners and trackers, redone properly",
         "Printable and digital planners and trackers for job search, chronic illness, IEP, ADHD, homeschool and more. Free starter kits.", home)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{BASE}{u}</loc></url>" for u in urls) + "</urlset>")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
    print("built", len(urls), "pages")

if __name__ == "__main__":
    main()
