"""Capture every page the video shows, at 2x, plus element boxes for the storyboard selectors.

Pages are the real site (served locally from ../site), a code view generated from the real Daml
sources, a terminal view carrying the real receipt printed by reproduce.sh's receipt block for
the recorded run, and the title/outro layers.

Output: <work>/cap/<page>[@<state>].png and <page>.json
"""
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import HaskellLexer

sys.path.insert(0, str(Path(__file__).parent))
import storyboard  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(os.environ.get("WORK", ROOT.parent / ".work")) / "cap"
WORK.mkdir(parents=True, exist_ok=True)
BASE = os.environ.get("SITE", "http://localhost:8765")
VW, VH, DPR = 1600, 900, 2


def selectors_for(page):
    out = set(["h1"]) if page in ("landing", "demo") else set()
    for sc in storyboard.SCENES:
        if sc["page"] != page:
            continue
        for a in sc["actions"]:
            for k in ("cursor", "zoom", "hl", "scroll", "type"):
                v = a.get(k)
                if isinstance(v, str):
                    out.add(v)
                elif isinstance(v, list):
                    out.update(v)
            out.update(a.get("reveal", []))
    return sorted(out)


BOX_JS = """(sels) => { const r = {}; for (const s of sels) { const e = document.querySelector(s);
  if (!e) { r[s] = null; continue; } const b = e.getBoundingClientRect();
  r[s] = [b.left + scrollX, b.top + scrollY, b.width, b.height]; } return r; }"""


EXT_JS = """() => { const r = {}; document.querySelectorAll('.ln').forEach(e => {
  const rg = document.createRange(); rg.selectNodeContents(e); const b = rg.getBoundingClientRect();
  r['#' + e.id] = [e.getBoundingClientRect().left + 30, b.right]; }); return r; }"""


def shoot(pg, name, sels, extra=None):
    pg.evaluate("window.scrollTo(0,0)")
    pg.wait_for_timeout(300)
    boxes = pg.evaluate(BOX_JS, sels)
    missing = [s for s, v in boxes.items() if v is None]
    if missing:
        raise SystemExit(f"{name}: selectors not found: {missing}")
    pg.screenshot(path=str(WORK / f"{name}.png"), full_page=True)
    h = pg.evaluate("document.documentElement.scrollHeight")
    meta = dict(width=VW, height=h, dpr=DPR, boxes=boxes)
    if extra:
        meta.update(extra)
    return meta


def code_page():
    """Real excerpts of the Daml sources, with their real line numbers."""
    fmt = HtmlFormatter(nowrap=True, style="one-dark" if "one-dark" in _styles() else "monokai")
    css = HtmlFormatter(style=fmt.style).get_style_defs(".code")

    def block(path, ranges, prefix):
        src = (ROOT / path).read_text().split("\n")
        rows, k = [], 0
        for n, (a, b) in enumerate(ranges):
            if n:
                rows.append('<div class="fold">⋯</div>')
            chunk = "\n".join(src[a - 1:b])
            hl = highlight(chunk, HaskellLexer(), fmt).rstrip("\n").split("\n")
            for i, line in enumerate(hl):
                k += 1
                rows.append(f'<div class="ln" id="{prefix}-{k}"><span class="no">{a + i}</span>'
                            f'<span class="tx">{line or " "}</span></div>')
        return f'<div class="file"><div class="fname">{html.escape(path)}</div>' \
               f'<div class="code">{"".join(rows)}</div></div>'

    body = block("app/daml/Privity/Settlement.daml", [(86, 120)], "s") + \
        block("app/daml/Privity/Fund.daml", [(180, 182), (194, 196), (236, 244)], "f")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{css}
html,body{{margin:0;background:#1e2230;color:#d7dae0}}
body{{padding:34px 0 400px;font:21px/1.62 'JetBrains Mono',monospace}}
.file{{margin:0 0 46px}}
.fname{{font:600 15px 'Inter',sans-serif;color:#8b93a7;letter-spacing:.04em;padding:0 0 12px 104px}}
.code{{background:transparent}}
.ln{{display:flex;white-space:pre;padding:0 40px 0 0}}
.no{{width:78px;text-align:right;padding-right:26px;color:#4b5263;flex:none}}
.fold{{color:#4b5263;padding:4px 0 4px 72px}}
</style></head><body>{body}</body></html>"""


def _styles():
    from pygments.styles import get_all_styles
    return set(get_all_styles())


def term_page():
    # The receipt block is lifted from reproduce.sh and run against the artifact of the recorded
    # run (ui/replay.json), so the text below is that program's real output for that run.
    src = (ROOT / "reproduce.sh").read_text()
    js = re.search(r"node - <<'NODE'\n(.*?)\nNODE", src, re.S).group(1)
    r = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    rep = json.loads((ROOT / "ui/replay.json").read_text())
    net = rep["network"]
    part = f"participant   : {net['jsonApi']}  (ledger {net['ledgerApiVersion']}, package privity-1.2.0.dar)"
    lines = [("cmd", "./reproduce.sh"), ("out", part), ("out", "")]
    lines += [("out", l) for l in r.stdout.rstrip("\n").split("\n")]
    lines += [("cmd", "echo $?"), ("out", "0")]
    rows = []
    for i, (kind, text) in enumerate(lines):
        t = html.escape(text) or " "
        if kind == "cmd":
            t = f'<span class="p">~/privity</span> <span class="b">main</span> <span class="c">❯</span> {t}'
        elif text.startswith("RECEIPT"):
            t = f'<span class="h">{t}</span>'
        elif text.startswith("REPRODUCTION OK"):
            t = f'<span class="ok">{t}</span>'
        else:
            t = re.sub(r"\b(OK|PASS)\b", r'<span class="ok">\1</span>', t)
        rows.append(f'<div class="ln" id="t-{i}">{t}</div>')
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:#0f1117;color:#d6dbe6}}
body{{padding:40px 48px 400px;font:23px/1.75 'JetBrains Mono',monospace}}
.ln{{white-space:pre}} .p{{color:#7aa2ff}} .b{{color:#c678dd}} .c{{color:#20c47c}}
.h{{color:#fff;font-weight:700;letter-spacing:.06em}} .ok{{color:#20c47c;font-weight:700}}
</style></head><body>{''.join(rows)}</body></html>"""
    return doc, len(lines)


def chrome_page(style, label):
    dots = """<div class="dots"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i>
      <i style="background:#28c840"></i></div>"""
    if style == "browser":
        mid = f"""<div class="nav">‹ &nbsp;›</div><div class="url"><svg class="lock" width="11" height="13" viewBox="0 0 11 13"><rect x="1" y="5.5" width="9" height="7" rx="1.5" fill="#8b93a7"/><path d="M3 5.5V4a2.5 2.5 0 015 0v1.5" stroke="#8b93a7" stroke-width="1.5" fill="none"/></svg>
          {html.escape(label)}</div><div class="nav r">⟳</div>"""
    else:
        mid = f'<div class="title">{html.escape(label)}</div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;height:46px;overflow:hidden}}
body{{background:linear-gradient(#232733,#1c1f29);border-bottom:1px solid #0b0d12;display:flex;
  align-items:center;font:500 14px Inter,sans-serif;color:#9aa3b5;position:relative}}
.dots{{display:flex;gap:9px;padding-left:18px;width:120px}} .dots i{{width:13px;height:13px;border-radius:50%;display:block}}
.nav{{color:#6c7488;font-size:20px;width:60px}} .nav.r{{text-align:right;padding-right:22px;font-size:16px}}
.url{{flex:1;margin:0 150px 0 40px;height:30px;border-radius:9px;background:#12151d;border:1px solid #2a2f3d;
  display:flex;align-items:center;justify-content:center;gap:8px;color:#c7cedb;font-size:14.5px}}
.lock{{font-size:11px;opacity:.7}}
.title{{position:absolute;left:0;right:0;text-align:center;color:#9aa3b5}}
</style></head><body>{dots}{mid}</body></html>"""


def layers_page(kind):
    logo = (ROOT / "site/logo-512.png").resolve().as_uri()
    if kind == "title":
        body = f"""
<img id="logo" src="{logo}" style="position:absolute;left:840px;top:250px;width:240px">
<div id="word" style="position:absolute;left:0;right:0;top:520px;text-align:center;font:800 124px/1 Inter;letter-spacing:-.03em;color:#fff">Privity<span style="color:#4c7dff">.</span></div>
<div id="tag" style="position:absolute;left:0;right:0;top:688px;text-align:center;font:500 42px/1.2 Inter;color:#c9d2e6">Fund trades that <span style="background:linear-gradient(90deg,#6f9bff,#20c47c);-webkit-background-clip:text;color:transparent;font-weight:700">cannot half-settle</span>.</div>
<div id="eyebrow" style="position:absolute;left:0;right:0;top:790px;text-align:center"><span style="display:inline-block;font:600 22px Inter;letter-spacing:.14em;color:#93a0b4;border:1px solid #2a3350;border-radius:999px;padding:10px 26px;background:rgba(17,20,32,.6)">HACKCANTON S3 · INVESTMENT INFRASTRUCTURE</span></div>"""
        ids = ["logo", "word", "tag", "eyebrow"]
    else:
        body = f"""
<img id="logo" src="{logo}" style="position:absolute;left:880px;top:170px;width:160px">
<div id="word" style="position:absolute;left:0;right:0;top:360px;text-align:center;font:800 104px/1 Inter;letter-spacing:-.03em;color:#fff">Privity<span style="color:#4c7dff">.</span></div>
<div id="tag" style="position:absolute;left:0;right:0;top:500px;text-align:center;font:500 38px/1.3 Inter;color:#c9d2e6">Atomic settlement and need-to-know disclosure<br>for tokenized funds on Canton.</div>
<div id="links" style="position:absolute;left:0;right:0;top:680px;display:flex;gap:28px;justify-content:center;font:600 26px 'JetBrains Mono'">
  <span style="background:rgba(76,125,255,.14);border:1px solid rgba(111,155,255,.5);color:#dce6ff;border-radius:16px;padding:18px 30px">▶ zkasuran.github.io/privity-demo</span>
  <span style="background:rgba(255,255,255,.05);border:1px solid #2a3350;color:#dce6ff;border-radius:16px;padding:18px 30px">⌥ github.com/zkasuran/privity</span></div>
<div id="eyebrow" style="position:absolute;left:0;right:0;top:850px;text-align:center;font:600 22px Inter;letter-spacing:.14em;color:#93a0b4">HACKCANTON S3 · INVESTMENT INFRASTRUCTURE · BUILT ON CANTON</div>"""
        ids = ["logo", "word", "tag", "links", "eyebrow"]
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1920px;height:1080px;background:transparent;overflow:hidden}}
body *{{font-family:Inter,sans-serif}}</style></head><body>{body}</body></html>"""
    return doc, ids


def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport=dict(width=VW, height=VH), device_scale_factor=DPR,
                            reduced_motion="reduce")
        pg = ctx.new_page()
        meta = {}

        # Landing, in the three states of its stepper.
        sels = selectors_for("landing")
        states = {"": 0, "earmark": 1, "settle": 2}
        meta["landing"] = dict(states={})
        for st, idx in states.items():
            pg.goto(f"{BASE}/")
            pg.wait_for_timeout(600)
            pg.evaluate("document.querySelectorAll('.rise').forEach(e=>e.classList.add('in'))")
            pg.locator("#how .demo-box").scroll_into_view_if_needed()
            pg.wait_for_timeout(5200)  # let the auto-play finish before choosing the state
            pg.locator(f"#stepbar button:nth-child({idx + 1})").click()
            pg.wait_for_timeout(500)
            name = "landing" + (f"@{st}" if st else "")
            m = shoot(pg, name, sels)
            meta["landing"]["states"][st or "base"] = m
            if not st:
                nav = pg.evaluate("document.querySelector('#nav').getBoundingClientRect().height")
                pg.locator("#nav").screenshot(path=str(WORK / "landing_nav.png"))
                meta["landing"]["sticky"] = nav
        meta["landing"].update(meta["landing"]["states"]["base"])
        meta["landing"]["url"] = "zkasuran.github.io/privity-demo/"

        pg.goto(f"{BASE}/demo/")
        pg.wait_for_timeout(1500)
        meta["demo"] = shoot(pg, "demo", selectors_for("demo"))
        meta["demo"]["url"] = "zkasuran.github.io/privity-demo/demo/"

        (WORK / "code.html").write_text(code_page())
        pg.goto((WORK / "code.html").as_uri())
        pg.wait_for_timeout(400)
        ids = pg.evaluate("[...document.querySelectorAll('.ln')].map(e => '#' + e.id)")
        meta["code"] = shoot(pg, "code", sorted(set(selectors_for("code")) | set(ids)))
        meta["code"]["url"] = "Settlement.daml · Fund.daml — privity"
        meta["code"]["ext"] = pg.evaluate(EXT_JS)

        doc, n = term_page()
        (WORK / "term.html").write_text(doc)
        pg.goto((WORK / "term.html").as_uri())
        pg.wait_for_timeout(300)
        tsel = sorted(set(selectors_for("term")) | {f"#t-{i}" for i in range(n)})
        meta["term"] = shoot(pg, "term", tsel, extra=dict(lines=n))
        meta["term"]["url"] = "zsh — privity — receipt of the recorded run, 25 Sep 2026"
        meta["term"]["ext"] = pg.evaluate(EXT_JS)

        # Where the typed command starts and ends on each terminal line.
        meta["term"]["text"] = pg.evaluate("""() => { const r = {};
          document.querySelectorAll('.ln').forEach(e => { const rg = document.createRange();
            rg.selectNodeContents(e); const b = rg.getBoundingClientRect();
            const c = e.querySelector('.c'); const s = c ? c.getBoundingClientRect().right + 8 : b.left;
            r['#' + e.id] = [s, b.right]; }); return r; }""")

        # Window chrome for each page style, same width as the content viewport.
        cp = ctx.new_page()
        cp.set_viewport_size(dict(width=VW, height=46))
        for page in ("landing", "demo", "code", "term"):
            style = "browser" if page in ("landing", "demo") else "plain"
            (WORK / f"chrome_{page}.html").write_text(chrome_page(style, meta[page]["url"]))
            cp.goto((WORK / f"chrome_{page}.html").as_uri())
            cp.wait_for_timeout(200)
            cp.screenshot(path=str(WORK / f"chrome_{page}.png"))

        lp = ctx.new_page()
        lp.set_viewport_size(dict(width=1920, height=1080))
        for kind in ("title", "outro"):
            doc, ids = layers_page(kind)
            (WORK / f"{kind}.html").write_text(doc)
            lp.goto((WORK / f"{kind}.html").as_uri())
            lp.wait_for_timeout(400)
            lay = {}
            for i in ids:
                loc = lp.locator(f"#{i}")
                bb = loc.bounding_box()
                loc.screenshot(path=str(WORK / f"{kind}_{i}.png"), omit_background=True)
                lay[i] = [bb["x"], bb["y"], bb["width"], bb["height"]]
            meta[kind] = dict(layers=lay)
        b.close()
    (WORK / "meta.json").write_text(json.dumps(meta, indent=1))
    print("captured", ", ".join(meta))


if __name__ == "__main__":
    main()
