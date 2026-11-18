#!/usr/bin/env python3
"""Builds the steady pins (1000x1500 PNG) and pins.csv.
Usage: python3 site/build_pins.py <out_csv_dir> [first_day YYYY-MM-DD]
Images go to ../pins-site (served from the repo); links point at the site's guides."""
import csv, html, subprocess, sys, tempfile
from datetime import date, timedelta
from pathlib import Path
from pin_specs import PINS

HERE = Path(__file__).resolve().parent
IMG = HERE.parent / "pins-site"
DOMAIN = HERE / "domain.txt"
BASE = f"https://{DOMAIN.read_text().strip()}/" if DOMAIN.exists() else "https://bangreedy-2.github.io/DPF/"
RAW = "https://raw.githubusercontent.com/Bangreedy-2/DPF/main/pins-site/"
TIMES = ["13:10", "15:40", "18:20", "20:30", "22:15"]
PAL = {  # dark, accent, paper, ink
    "job": ("#0f4c47", "#f2a541", "#fbf6ec", "#14302e"),
    "chronic": ("#4a2f5c", "#f3b49b", "#fbf5f8", "#2e1c3a"),
    "iep": ("#1f3a68", "#ffd166", "#f6f8fc", "#14264a"),
}
CSS = """
*{box-sizing:border-box;margin:0}body{width:1000px;height:1500px;font-family:Inter,sans-serif;overflow:hidden}
.pin{width:1000px;height:1500px;padding:84px 76px 0;display:flex;flex-direction:column;position:relative}
.dark{background:var(--d);color:#fff}.light{background:var(--p);color:var(--i)}.acc{background:var(--a);color:var(--i)}
.k{font-size:30px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin-bottom:26px}
.dark .k{color:var(--a)}.light .k{color:var(--d)}.acc .k{color:var(--d)}
h1{font-family:'Inter Display',Inter,sans-serif;font-weight:800;line-height:1.06;letter-spacing:-.025em}
.body{flex:1;display:flex;flex-direction:column;justify-content:center;gap:26px;padding:36px 0}
.row{display:flex;align-items:center;gap:26px;font-size:46px;font-weight:600;line-height:1.22}
.m{flex:0 0 72px;height:72px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:36px;font-weight:800}
.light .m{background:var(--d);color:#fff}.dark .m{background:var(--a);color:var(--i)}
.m.x{background:#c8483f;color:#fff}.m.q{background:var(--a);color:var(--i)}
.light .row{background:#fff;border-radius:22px;padding:22px 28px;box-shadow:0 2px 0 rgba(0,0,0,.06)}
.step{display:flex;align-items:stretch;border-radius:24px;overflow:hidden;background:rgba(255,255,255,.1)}
.step b{flex:0 0 230px;background:var(--a);color:var(--i);display:flex;align-items:center;justify-content:center;font-size:44px;font-weight:800;padding:10px;text-align:center}
.step b.s{flex-basis:110px;font-size:54px}.step span{padding:36px 34px;font-size:46px;font-weight:600;line-height:1.2;display:flex;align-items:center}
.sub{font-size:56px;line-height:1.3;font-weight:500;opacity:.94}
.paper{background:#fff;color:#222;border-radius:26px;padding:52px 50px;font-size:40px;line-height:1.4;box-shadow:0 18px 40px rgba(0,0,0,.18);display:flex;flex-direction:column;gap:20px}
.vs{border-radius:26px;padding:34px 40px}.vs .l{font-size:28px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px}
.vs p{font-size:48px;line-height:1.25;font-weight:600}.vs.a{background:#fff;color:#777}.vs.a .l{color:#c8483f}.vs.a p{color:#555}
.vs.b{background:var(--d);color:#fff}.vs.b .l{color:var(--a)}.vs.n{background:#fff;color:var(--i)}.vs.n .l{color:var(--d)}
.f{height:150px;display:flex;align-items:center;justify-content:space-between;font-size:30px;font-weight:700;margin:0 -76px;padding:0 76px}
.dark .f{background:rgba(0,0,0,.22)}.light .f{background:var(--d);color:#fff}.acc .f{background:var(--d);color:#fff}
.f span{white-space:nowrap}.f span.t{background:var(--a);color:var(--i);padding:16px 30px;border-radius:999px}.f .br{letter-spacing:.1em;text-transform:uppercase;font-size:26px;opacity:.9}
"""
E = html.escape

def render(tpl, n, c):
    d, a, p, i = PAL[n]
    head = E(c["head"])
    size = 104 if len(c["head"]) < 34 else 88 if len(c["head"]) < 48 else 76
    if tpl == "list":
        theme, marks = "light", c.get("mark", "c")
        rows = ""
        for j, it in enumerate(c["items"]):
            m = {"c": "✓", "x": "✕", "q": "“", "n": str(j + 1)}[marks]
            fs = 46 if len(it) < 40 else 39
            rows += f'<div class="row" style="font-size:{fs}px"><div class="m {marks}">{m}</div><div>{E(it)}</div></div>'
        body = rows
    elif tpl == "steps":
        theme = "dark"
        body = "".join(f'<div class="step"><b class="{"s" if len(k) < 3 else ""}">{E(k)}</b><span>{E(v)}</span></div>' for k, v in c["items"])
    elif tpl == "hook":
        theme, size = "dark", (128 if len(c["head"]) < 30 else 108 if len(c["head"]) < 42 else 92)
        body = f'<div style="width:140px;height:12px;background:var(--a);border-radius:6px"></div><p class="sub">{E(c["sub"])}</p>'
    elif tpl == "card":
        theme = "acc"
        body = '<div class="paper">' + "".join(f"<p>{x if x.startswith('<b>') else E(x)}</p>" for x in c["card"]) + "</div>"
    else:  # versus
        theme = "light"
        body = ""
        for key, cls in (("a", "a" if "c" not in c else "n"), ("b", "b" if "c" not in c else "n"), ("c", "n")):
            if key in c:
                body += f'<div class="vs {cls}"><div class="l">{E(c[key + "_label"])}</div>' + "".join(f"<p>{E(x)}</p>" for x in c[key]) + "</div>"
    hook_top = ' style="gap:48px"' if tpl == "hook" else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>:root{{--d:{d};--a:{a};--p:{p};--i:{i}}}{CSS}</style></head>
<body><div class="pin {theme}"><div class="k">{E(c["kicker"])}</div><h1 style="font-size:{size}px">{head}</h1>
<div class="body"{hook_top}>{body}</div><div class="f"><span class="br">Redraft Studio</span><span class="t">{E(c["foot"])} →</span></div></div></body></html>"""

SHOOT = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1000,height:1500}});
const fs=require('fs');for(const f of fs.readdirSync(process.argv[2]).filter(x=>x.endsWith('.html'))){await p.goto('file://'+process.argv[2]+'/'+f);
const o=await p.evaluate(()=>{const e=document.querySelector('.body');return e.scrollHeight-e.clientHeight});if(o>2)console.log('OVERFLOW',f,o);
await p.screenshot({path:process.argv[3]+'/'+f.replace('.html','.png')});}await b.close()})();"""

def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    day0 = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today() + timedelta(days=2)
    IMG.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    names = {}
    for pid, guide, tpl, niche, board, title, desc, kw, c in PINS:
        names[pid] = f"{pid}-{guide}-{tpl}"
        (tmp / f"{names[pid]}.html").write_text(render(tpl, niche, c))
    (tmp / "shoot.js").write_text(SHOOT)
    print(subprocess.run(["node", str(tmp / "shoot.js"), str(tmp), str(IMG)], capture_output=True, text=True, cwd="/").stdout)
    # interleave niches so each day mixes topics and never repeats a guide back to back
    by = {n: [p for p in PINS if p[3] == n] for n in PAL}
    order = [by[n][k] for k in range(10) for n in PAL]
    with open(out / "pins.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"])
        for k, (pid, guide, tpl, niche, board, title, desc, kw, c) in enumerate(order):
            when = f"{day0 + timedelta(days=k // 5)}T{TIMES[k % 5]}:00"
            link = f"{BASE}guides/{guide}/?utm_source=pinterest&utm_medium=pin&utm_content={pid}"
            w.writerow([title, RAW + names[pid] + ".png", board, "", desc, link, when, kw])
    print("pins:", len(order), "first:", day0, "base:", BASE)

if __name__ == "__main__":
    main()
