"""YouTube upload package: captions, chapters, title, description, tags, thumbnail, metadata.

Output: video/youtube/
"""
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import timeline  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "youtube"
OUT.mkdir(exist_ok=True)
CAP = timeline.WORK / "cap"

TITLE = "Privity: fund trades that cannot half-settle | Atomic DvP + need-to-know privacy on Canton"
ALT_TITLES = [
    "Atomic delivery-versus-payment for tokenized funds on Canton (Daml demo)",
    "Settling a tokenized fund trade in ONE Canton transaction, and proving who can see what",
    "Privity | HackCanton S3 demo: atomic settlement, calibrated disclosure, verifiable NAV",
]
TAGS = [
    "Canton", "Canton Network", "Daml", "tokenized funds", "tokenization", "delivery versus payment",
    "DvP", "atomic settlement", "RWA", "real world assets", "privacy", "sub-transaction privacy",
    "fund administration", "transfer agent", "NAV", "blockchain", "smart contracts", "HackCanton",
    "Global Synchronizer", "Digital Asset", "fintech", "institutional DeFi", "Privity",
]


def ts(t, srt=True):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    return f"{int(m)}:{int(s):02d}" if h < 1 else f"{int(h)}:{int(m):02d}:{int(s):02d}"


def captions(scenes):
    """Cues of at most ~42 chars per line, two lines, split on punctuation where possible."""
    cues = []
    for sc in scenes:
        words = [dict(w, t=w["t"] + sc["start"]) for w in sc["words"]]
        text_tokens = sc["vo"].split()
        # map boundary words to the original tokens so punctuation is kept
        toks, j = [], 0
        for w in words:
            tok = text_tokens[j] if j < len(text_tokens) else w["w"]
            toks.append(dict(w, tok=tok))
            j += 1
        cur, start = [], None
        for i, w in enumerate(toks):
            if start is None:
                start = w["t"]
            cur.append(w)
            line = " ".join(x["tok"] for x in cur)
            end_punct = w["tok"][-1] in ".,:;?!"
            last = i == len(toks) - 1
            if last or len(line) > 70 or (end_punct and len(line) > 34) or w["tok"][-1] in ".?!":
                end = w["t"] + w["d"] + 0.15
                if not last:
                    end = min(end, toks[i + 1]["t"] - 0.02)
                cues.append((start, end, line))
                cur, start = [], None
    out = []
    for k, (a, b, text) in enumerate(cues, 1):
        if len(text) > 42:  # wrap into two balanced lines
            words = text.split()
            best = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(text) / 2))
            text = " ".join(words[:best]) + "\n" + " ".join(words[best:])
        out.append(f"{k}\n{ts(a)} --> {ts(b)}\n{text}\n")
    (OUT / "captions.en.srt").write_text("\n".join(out))
    return len(out)


def chapters(scenes):
    rows = [f"{ts(0 if i == 0 else sc['start'], srt=False)} {sc['chapter']}" for i, sc in enumerate(scenes)]
    return "\n".join(rows)


def description(ch):
    return f"""Privity is settlement infrastructure for tokenized funds on Canton. Both legs of a fund trade, units and cash, commit in one atomic Daml transaction, so delivery and payment can never separate. Each counterparty sees only the parcel it is buying, never the other side's book, and an independent administrator attests NAV with a sha256 commitment that an entitled auditor can verify on ledger.

Everything on screen comes from a real run on a Canton LocalNet participant (Ledger API 3.5.17), captured through the JSON Ledger API and shown as a labelled replay. The terminal receipt is the output of reproduce.sh for that same recorded run.

▶ Verified run (replay): https://zkasuran.github.io/privity-demo/demo/
▶ Project site: https://zkasuran.github.io/privity-demo/
▶ Code: https://github.com/zkasuran/privity

Chapters
{ch}

What you'll see
• Atomic delivery versus payment: shares and cash move in one transaction, 8 events, one commit
• Calibrated disclosure: the seller earmarks exactly the parcel being sold; the buyer can verify it and never sees the retained units
• Need-to-know, read back from the ledger: active contract queries issued as each of the four parties
• Verifiable NAV: an on-ledger sha256 commitment over the book, recomputed by an entitled auditor
• One-command reproduction with a pass/fail receipt

Built for HackCanton Season 3, Investment Infrastructure track.

Narration is AI-generated text-to-speech. The background music is an original piece composed for this video, made with code. Built with Daml on Canton.

#Canton #Daml #Tokenization"""


def thumbnail():
    from playwright.sync_api import sync_playwright
    logo = (HERE.parent / "site/logo-512.png").resolve().as_uri()
    shot = (CAP / "demo.png").resolve().as_uri()
    meta = json.loads((CAP / "meta.json").read_text())
    x, y, w, h = meta["demo"]["boxes"]["#matrix"]
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1280px;height:720px;overflow:hidden;font-family:Inter,sans-serif}}
body{{background:radial-gradient(900px 600px at 10% 10%,#2b4fbf 0,transparent 60%),
  radial-gradient(700px 500px at 100% 100%,#127a52 0,transparent 60%),#0a0c16;color:#fff}}
.win{{position:absolute;right:-150px;top:170px;width:720px;height:430px;border-radius:18px;overflow:hidden;
  box-shadow:0 30px 80px rgba(0,0,0,.6);border:2px solid #3a4260;transform:rotate(-4deg);
  background:#0b0d12 url('{shot}') no-repeat;background-size:1150px auto;
  background-position:-{x * 1150 / 1600 - 10:.0f}px -{y * 1150 / 1600 - 30:.0f}px}}
.bar{{height:34px;background:#1d212c;display:flex;gap:8px;align-items:center;padding-left:14px}}
.bar i{{width:12px;height:12px;border-radius:50%;display:block}}
.logo{{position:absolute;left:64px;top:56px;width:96px;border-radius:22px}}
.brand{{position:absolute;left:180px;top:70px;font:800 60px/1 Inter;letter-spacing:-.02em}}
h1{{position:absolute;left:64px;top:200px;margin:0;font:900 84px/1.0 Inter;letter-spacing:-.035em;text-shadow:0 6px 30px rgba(0,0,0,.5)}}
h1 span{{text-shadow:none;background:linear-gradient(90deg,#7aa6ff,#26d68a);-webkit-background-clip:text;color:transparent}}
.chip{{position:absolute;left:64px;bottom:64px;font:800 30px Inter;background:#20c47c;color:#04160d;
  padding:14px 24px;border-radius:14px}}
.chip2{{position:absolute;left:390px;bottom:64px;font:700 30px Inter;border:2px solid #4c7dff;color:#dce6ff;
  padding:12px 22px;border-radius:14px;background:rgba(76,125,255,.15)}}
.ring{{position:absolute;right:46px;top:300px;width:230px;height:62px;border:5px solid #6f9bff;border-radius:14px;
  box-shadow:0 0 30px #4c7dff;transform:rotate(-4deg)}}
</style></head><body>
<div class="win"><div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i></div></div>
<img class="logo" src="{logo}"><div class="brand">Privity<span style="color:#4c7dff">.</span></div>
<h1>Fund trades<br>that <span>can't</span><br><span>half-settle</span></h1>
<div class="chip">1 TX · 8 EVENTS</div><div class="chip2">on Canton</div>
</body></html>"""
    p = timeline.WORK / "thumb.html"
    p.write_text(html)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport=dict(width=1280, height=720))
        pg.goto(p.as_uri())
        pg.wait_for_timeout(500)
        pg.screenshot(path=str(OUT / "thumbnail.png"))
        pg.screenshot(path=str(OUT / "thumbnail.jpg"), type="jpeg", quality=92)
        b.close()


def main():
    scenes, total = timeline.build()
    n = captions(scenes)
    ch = chapters(scenes)
    desc = description(ch)
    (OUT / "description.txt").write_text(desc)
    (OUT / "title.txt").write_text(TITLE + "\n\nAlternatives:\n" + "\n".join("- " + t for t in ALT_TITLES) + "\n")
    (OUT / "tags.txt").write_text(", ".join(TAGS) + "\n")
    (OUT / "chapters.txt").write_text(ch + "\n")
    (OUT / "pinned-comment.txt").write_text(
        "Try it without installing anything: https://zkasuran.github.io/privity-demo/demo/ (a labelled replay "
        "of a real Canton run). To run it yourself: clone the repo and run ./reproduce.sh, it exits 0 only if "
        "settlement, digest verification and the privacy check all pass.\n")
    meta = dict(
        snippet=dict(title=TITLE, description=desc, tags=TAGS, categoryId="28", defaultLanguage="en",
                     defaultAudioLanguage="en"),
        status=dict(privacyStatus="unlisted", selfDeclaredMadeForKids=False, license="youtube",
                    embeddable=True),
        recordingDetails=dict(recordingDate="2026-09-29"),
        files=dict(video="../out/privity-demo.mp4", thumbnail="thumbnail.jpg", captions="captions.en.srt"),
        durationSeconds=round(total, 2),
    )
    (OUT / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    assert len(TITLE) <= 100, len(TITLE)
    assert len(desc) <= 5000, len(desc)
    assert len(", ".join(TAGS)) <= 500
    thumbnail()
    print(f"captions {n} cues, title {len(TITLE)} chars, description {len(desc)} chars, "
          f"tags {len(', '.join(TAGS))} chars")


if __name__ == "__main__":
    main()
