"""Shared timeline: scene start times and resolved action cues, from storyboard + VO timings."""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import storyboard  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(os.environ.get("WORK", ROOT.parent / ".work"))
FPS = 30


def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def resolve(at, words, lead, sid):
    if isinstance(at, (int, float)):
        return float(at)
    m = re.fullmatch(r"w:([^#+-]+)(?:#(\d+))?([+-][\d.]+)?", at)
    if not m:
        raise ValueError(f"{sid}: bad cue {at}")
    target, nth, off = _norm(m.group(1)), int(m.group(2) or 1), float(m.group(3) or 0)
    hits = [w for w in words if _norm(w["w"]) == target]
    if len(hits) < nth:
        raise ValueError(f"{sid}: cue word '{m.group(1)}' #{nth} not in VO")
    return lead + hits[nth - 1]["t"] + off


def build():
    vo = json.loads((WORK / "vo/words.json").read_text())
    t, scenes = 0.0, []
    for sc in storyboard.SCENES:
        v = vo[sc["id"]]
        dur = sc["lead"] + v["dur"] + sc["tail"]
        acts = []
        for a in sc["actions"]:
            a = dict(a)
            a["t"] = max(0.0, resolve(a["at"], v["words"], sc["lead"], sc["id"]))
            acts.append(a)
        acts.sort(key=lambda a: a["t"])
        scenes.append(dict(sc, start=t, dur=dur, acts=acts, vo_dur=v["dur"],
                           words=[dict(w, t=w["t"] + sc["lead"]) for w in v["words"]]))
        t += dur
    return scenes, t


if __name__ == "__main__":
    sc, total = build()
    for s in sc:
        print(f"{s['id']:9s} start {s['start']:6.2f}  dur {s['dur']:5.2f}  acts {len(s['acts'])}")
    print("total", round(total, 2))
