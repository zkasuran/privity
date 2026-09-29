"""Composite the video in the style of a Screen Studio recording.

Wallpaper background, floating rounded window with a soft shadow, eased scrolling, smooth
camera zooms that follow the action, a smoothed cursor with click ripples, spotlight
highlights, typed terminal output, and slide/crossfade transitions between scenes.

Everything is rendered on a 3840x2160 canvas so a 2x zoom is still pixel-sharp, then the camera
crop is scaled to 1920x1080 and piped to ffmpeg. The audio is mixed here too (VO, ducked score,
UI sound effects) and loudness-normalised for YouTube.

    python render.py            # full video -> <work>/out/privity-demo.mp4
    python render.py --still 42 # single frame at t=42s -> <work>/out/still.png
"""
import json
import math
import multiprocessing as mp
import re
import subprocess
import sys
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
import timeline  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS = timeline.FPS
CAP = timeline.WORK / "cap"
OUTD = timeline.WORK / "out"
OUTD.mkdir(parents=True, exist_ok=True)
META = json.loads((CAP / "meta.json").read_text())

CW, CH = 3840, 2160            # canvas
OW, OH = 1920, 1080            # output
S = 2                          # page pixel scale (DPR)
VW, VH = 1600 * S, 900 * S     # content viewport in canvas px
BAR = 46 * S                   # title bar
WX = (CW - VW) // 2
WY = (CH - (VH + BAR)) // 2
CX0, CY0 = WX, WY + BAR        # content origin on canvas
RAD = 16 * S
ACCENT = (111, 155, 255)
TR = 0.7                       # transition length (s)


# ----------------------------------------------------------------------------- easing / tracks
def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * u * (u * (6 * u - 15) + 10)  # smootherstep


def lerp(a, b, u):
    if isinstance(a, tuple):
        return tuple(x + (y - x) * u for x, y in zip(a, b))
    return a + (b - a) * u


class Track:
    def __init__(self, init):
        self.init = init
        self.seg = []  # (t0, t1, v0, v1)

    def at(self, t):
        v = self.init
        for t0, t1, v0, v1 in self.seg:
            if t < t0:
                break
            v = v1 if t >= t1 else lerp(v0, v1, ease((t - t0) / max(t1 - t0, 1e-6)))
        return v

    def to(self, t0, dur, v1):
        # A later segment overrides earlier ones from its start, beginning from wherever the
        # property is at that moment, so interrupted moves stay continuous.
        v0 = self.at(t0)
        self.seg.append((t0, t0 + max(dur, 1e-6), v0, v1))

    def end(self):
        return self.at(1e9)


# ----------------------------------------------------------------------------- scene model
def page_meta(page, state="base"):
    m = META[page]
    if "states" in m:
        return m["states"][state]
    return m


def box(page, sel, state="base"):
    """Element box in page pixels (x, y, w, h)."""
    sels = sel if isinstance(sel, list) else [sel]
    pm = page_meta(page, state)
    # ["#s-1", "#s-5"] means the line range s-1..s-5, so every line's text extent counts
    if len(sels) == 2 and all(re.fullmatch(r"#[a-z]-\d+", s) for s in sels) and sels[0][1] == sels[1][1]:
        p, a, b = sels[0][1], int(sels[0][3:]), int(sels[1][3:])
        sels = [f"#{p}-{i}" for i in range(a, b + 1) if f"#{p}-{i}" in pm["boxes"] or f"#{p}-{i}" in pm.get("ext", {})]
        sels = [s for s in sels if s in pm["boxes"]] or sels[:1]
    bs = [list(pm["boxes"][s]) for s in sels]
    for b, s in zip(bs, sels):
        if s in pm.get("ext", {}):  # code/terminal rows: use the text extent, not the full row
            l, r = pm["ext"][s]
            b[0], b[2] = min(l, b[0] + b[2]), max(20, r - l)
    x0 = min(b[0] for b in bs) * S
    y0 = min(b[1] for b in bs) * S
    x1 = max(b[0] + b[2] for b in bs) * S
    y1 = max(b[1] + b[3] for b in bs) * S
    return (x0, y0, x1 - x0, y1 - y0)


def max_scroll(page):
    return max(0, page_meta(page)["height"] * S - VH)


class SceneState:
    """All animated properties of one scene, pre-built from its actions."""

    def __init__(self, sc, prev):
        self.sc = sc
        self.page = sc["page"]
        self.web = self.page in ("landing", "demo", "code", "term")
        same = prev is not None and prev.page == self.page
        self.scroll = Track(prev.scroll.end() if same else 0.0)
        self.cam = Track(prev.cam.end() if same else (1.0, CW / 2, CH / 2))
        self.cur = Track(prev.cur.end() if same else (CW * 0.62, CH * 0.78))
        self.cur_alpha = Track(prev.cur_alpha.end() if same else 0.0)
        self.hl_rect = Track(prev.hl_rect.end() if same else (0.0, 0.0, 10.0, 10.0))
        self.hl_a = Track(prev.hl_a.end() if same else 0.0)
        self.state = prev.state_end if same else "base"
        self.state_changes = []  # (t, from, to)
        self.clicks = []
        self.sfx = []  # (t, name, gain)
        self.hidden = dict(prev.hidden_end) if same else {}
        self.typing = dict(prev.typing_end) if same else {}
        if self.page == "term" and not same:
            n = META["term"]["lines"]
            self.hidden = {f"#t-{i}": 1e9 for i in range(1, n)}
            self.typing = {"#t-0": (1e9, 1.0)}
        self._build()

    def scroll_for(self, sel, align, st):
        x, y, w, h = box(self.page, sel, st)
        return float(min(max_scroll(self.page), max(0.0, y + h / 2 - align * VH)))

    def canvas_pt(self, sel, t, st, anchor=(0.5, 0.5)):
        x, y, w, h = box(self.page, sel, st)
        sy = self.scroll.at(t)
        return (CX0 + x + w * anchor[0], CY0 + y + h * anchor[1] - sy)

    def _build(self):
        st = self.state
        for a in self.sc["acts"]:
            t = a["t"]
            if "scroll" in a:
                self.scroll.to(t, a.get("dur", 1.2), self.scroll_for(a["scroll"], a.get("align", .4), st))
            if "state" in a:
                self.state_changes.append((t, st, a["state"]))
                st = a["state"]
            if "zoom" in a:
                d = a.get("dur", 1.1)
                if a["zoom"] is None:
                    self.cam.to(t, d, (1.0, CW / 2, CH / 2))
                else:
                    s = a.get("scale", 1.6)
                    bx = box(self.page, a["zoom"], st)
                    # never zoom so far that the target no longer fits in frame
                    s = max(1.0, min(s, 0.86 * CW / (bx[2] + 1), 0.8 * CH / (bx[3] + 1)))
                    # focus on where the element will be once any scroll in flight has landed
                    px, py = self.canvas_pt(a["zoom"], t + d + 2.0, st)
                    self.cam.to(t, d, (s, px, py))
            if "cursor" in a:
                x, y = self.canvas_pt(a["cursor"], a["t"] + a.get("dur", 0.8) + 0.3, st,
                                      anchor=(0.5, 0.55))
                if a.get("park"):
                    self.cur.to(t, 0.0, (CX0 + VW * 0.8, CY0 + VH * 0.8))
                    self.cur_alpha.to(t, 0.4, 1.0)
                else:
                    self.cur_alpha.to(t, 0.25, 1.0)
                    self.cur.to(t, a.get("dur", 0.8), (x, y))
            if a.get("click"):
                self.clicks.append(t)
                self.sfx.append((t, "click", 0.9))
            if "hl" in a:
                if a["hl"] is None:
                    self.hl_a.to(t, 0.35, 0.0)
                else:
                    x, y, w, h = box(self.page, a["hl"], st)
                    p = 10 * S
                    r = (x - p, y - p, w + 2 * p, h + 2 * p)
                    if self.hl_a.at(t) < 0.05:
                        self.hl_rect.to(t, 0.0, r)
                    else:
                        self.hl_rect.to(t, 0.45, r)
                    self.hl_a.to(t, 0.35, 1.0)
                    self.sfx.append((t, "pop", 0.6))
                    if "zoom" not in a:
                        self.follow(t, r)
            if "type" in a:
                self.typing[a["type"]] = (t, a.get("dur", 1.0))
                n = 14
                for k in range(n):
                    self.sfx.append((t + a.get("dur", 1.0) * k / n, "key", 0.5 + 0.3 * ((k * 7) % 3) / 2))
                self.sfx.append((t + a.get("dur", 1.0) + 0.25, "click", 0.5))
            if "reveal" in a:
                for i, sel in enumerate(a["reveal"]):
                    self.hidden[sel] = t + i * a.get("step", 0.1)
        self.state_end = st
        self.hidden_end = {k: v for k, v in self.hidden.items()}
        self.typing_end = dict(self.typing)

    def follow(self, t, r):
        """If zoomed in and the highlight is out of frame, pan the camera to it."""
        s, cx, cy = self.cam.at(t + 0.6)
        if s < 1.05:
            return
        sy = self.scroll.at(t + 0.6)
        x0, y0 = CX0 + r[0], CY0 + r[1] - sy
        x1, y1 = x0 + r[2], y0 + r[3]
        w, h = CW / s, CH / s
        vx0 = min(max(cx - w / 2, 0), CW - w)
        vy0 = min(max(cy - h / 2, 0), CH - h)
        m = 60
        if x0 >= vx0 + m and x1 <= vx0 + w - m and y0 >= vy0 + m and y1 <= vy0 + h - m:
            return
        s2 = max(1.0, min(s, 0.86 * CW / (r[2] + 1), 0.8 * CH / (r[3] + 1)))
        self.cam.to(t, 0.9, (s2, (x0 + x1) / 2, (y0 + y1) / 2))

    def page_state_at(self, t):
        """(state, other_state, mix) for crossfading page states."""
        cur, other, mix = self.state, None, 0.0
        for t0, a, b in self.state_changes:
            if t >= t0 + 0.25:
                cur = b
            elif t >= t0:
                cur, other, mix = a, b, (t - t0) / 0.25
        return cur, other, mix


def build_states(scenes):
    out, prev = [], None
    for sc in scenes:
        s = SceneState(sc, prev)
        out.append(s)
        prev = s
    return out


# ----------------------------------------------------------------------------- assets
_cache = {}


def asset(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def wallpaper():
    """Deep navy wallpaper with soft colour blooms, like a Screen Studio background."""
    w, h = 480, 270
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    img = np.zeros((h, w, 3), np.float32)
    img[:] = (10, 12, 24)
    for cx, cy, r, col, a in [
        (0.15, 0.2, 0.55, (76, 125, 255), 0.55), (0.9, 0.85, 0.6, (32, 196, 124), 0.32),
        (0.85, 0.1, 0.45, (140, 90, 255), 0.35), (0.3, 1.0, 0.5, (40, 90, 200), 0.35),
    ]:
        d = np.sqrt(((xx / w - cx) * 1.6) ** 2 + (yy / h - cy) ** 2) / r
        g = np.exp(-d * d * 2.2)[..., None] * a
        img = img * (1 - g) + np.array(col, np.float32) * g
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((CW, CH), Image.BICUBIC)
    im = im.filter(ImageFilter.GaussianBlur(20))
    arr = np.asarray(im).astype(np.int16)
    noise = np.random.default_rng(3).integers(-3, 4, (CH, CW, 1), dtype=np.int16)
    return np.clip(arr + noise, 0, 255).astype(np.uint8)


def rounded_mask(w, h, r, top=True, bottom=True):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    a = np.asarray(m).copy()
    if not top:
        a[: h // 2] = 255
    if not bottom:
        a[h // 2:] = 255
    return a


def base_frame(page):
    """Wallpaper + shadow + window chrome for a page. Content area left for per-frame paste."""
    bg = wallpaper_img().astype(np.float32)
    # shadow
    sh = Image.new("L", (CW // 4, CH // 4), 0)
    ImageDraw.Draw(sh).rounded_rectangle(
        (WX // 4, (WY + 40) // 4, (WX + VW) // 4, (WY + BAR + VH + 40) // 4), RAD // 4, fill=190)
    sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(22)).resize((CW, CH), Image.BILINEAR),
                    np.float32)[..., None] / 255
    bg = bg * (1 - sh * 0.85)
    # window body + chrome
    win = np.zeros((BAR + VH, VW, 3), np.float32)
    chrome = np.asarray(Image.open(CAP / f"chrome_{page}.png").convert("RGB").resize((VW, BAR)),
                        np.float32)
    win[:BAR] = chrome
    m = rounded_mask(VW, BAR + VH, RAD)[..., None].astype(np.float32) / 255
    region = bg[WY:WY + BAR + VH, WX:WX + VW]
    bg[WY:WY + BAR + VH, WX:WX + VW] = region * (1 - m) + win * m
    # hairline border
    out = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))
    ImageDraw.Draw(out).rounded_rectangle((WX - 1, WY - 1, WX + VW, WY + BAR + VH), RAD + 1,
                                          outline=(70, 78, 100), width=2)
    return np.asarray(out).copy()


def wallpaper_img():
    return asset("wall", wallpaper)


def page_img(page, state="base"):
    name = page + ("" if state == "base" else f"@{state}")
    return asset(("page", name), lambda: np.asarray(Image.open(CAP / f"{name}.png").convert("RGB")))


def content_mask():
    return asset("cmask", lambda: rounded_mask(VW, VH, RAD, top=False)[..., None] > 0)


def cursor_sprite():
    def mk():
        k = 4
        pts = [(0, 0), (0, 17), (4.2, 13.2), (7, 19.6), (9.6, 18.5), (6.9, 12.3), (12.2, 12.1)]
        sc = 2.9 * S * k / 2
        size = (int(16 * sc), int(24 * sc))
        im = Image.new("RGBA", size, (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        P = [(x * sc + 2 * k, y * sc + 2 * k) for x, y in pts]
        shadow = Image.new("RGBA", size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).polygon([(x + 1.5 * k, y + 3 * k) for x, y in P], fill=(0, 0, 0, 120))
        shadow = shadow.filter(ImageFilter.GaussianBlur(3 * k))
        im = Image.alpha_composite(shadow, im)
        d = ImageDraw.Draw(im)
        d.polygon(P, fill=(255, 255, 255, 255))
        inner = [(x * sc * 0.82 + 2 * k + 1.1 * sc * 0.9, y * sc * 0.82 + 2 * k + 2.2 * sc * 0.9)
                 for x, y in pts]
        d.polygon(inner, fill=(12, 12, 14, 255))
        return im.resize((size[0] // k, size[1] // k), Image.LANCZOS)
    return asset("cursor", mk)


def dim_lut(a):
    k = 1 - 0.5 * a
    return asset(("lut", round(a, 2)), lambda: (np.arange(256) * k).astype(np.uint8))


# ----------------------------------------------------------------------------- drawing
def draw_content(st, t):
    page = st.page
    sy = int(round(st.scroll.at(t)))
    cur, other, mix = st.page_state_at(t)
    img = page_img(page, cur)
    view = img[sy:sy + VH, :VW]
    if view.shape[0] < VH:
        view = np.vstack([view, np.repeat(view[-1:], VH - view.shape[0], 0)])
    view = view.copy()
    if other is not None and mix > 0:
        o = page_img(page, other)[sy:sy + VH, :VW]
        if o.shape[0] == VH:
            view = (view * (1 - mix) + o * mix).astype(np.uint8)
    # sticky nav on the landing page
    if page == "landing" and sy > 0:
        nav = asset("nav", lambda: np.asarray(Image.open(CAP / "landing_nav.png").convert("RGB")))
        view[:nav.shape[0], :nav.shape[1]] = (nav * 0.94).astype(np.uint8)
    # terminal: hidden lines and typing
    if page == "term":
        bgc = view[4, 4].copy()
        for sel, t_rev in st.hidden.items():
            x, y, w, h = box("term", sel)
            a = 1.0 if t < t_rev else max(0.0, 1 - (t - t_rev) / 0.08)
            if a > 0:
                y0, y1 = int(y) - sy, int(y + h) - sy
                reg = view[max(0, y0):max(0, y1)]
                view[max(0, y0):max(0, y1)] = (reg * (1 - a) + bgc * a).astype(np.uint8)
        for sel, (t0, d) in st.typing.items():
            x0, x1 = (v * S for v in META["term"]["text"][sel])
            u = min(1.0, max(0.0, (t - t0) / d))
            xs = int(x0 + (x1 - x0) * u)
            _, y, _, h = box("term", sel)
            view[int(y) - sy:int(y + h) - sy, xs:] = bgc
            if u < 1 or (int(t * 2) % 2 == 0 and t - t0 < d + 1.5):
                view[int(y) - sy + 8:int(y + h) - sy - 8, xs + 2:xs + 2 + 12 * S] = (215, 220, 230)
    # spotlight highlight
    a = st.hl_a.at(t)
    if a > 0.01:
        x, y, w, h = st.hl_rect.at(t)
        y -= sy
        x0, y0 = int(max(0, x)), int(max(0, y))
        x1, y1 = int(min(VW, x + w)), int(min(VH, y + h))
        keep = view[y0:y1, x0:x1].copy()
        view = dim_lut(a)[view]
        view[y0:y1, x0:x1] = keep
        pil = Image.fromarray(view)
        ov = Image.new("RGBA", (int(w) + 40, int(h) + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.rounded_rectangle((20, 20, int(w) + 19, int(h) + 19), 12 * S,
                            outline=ACCENT + (int(110 * a),), width=10)
        ov = ov.filter(ImageFilter.GaussianBlur(8))
        d = ImageDraw.Draw(ov)
        d.rounded_rectangle((20, 20, int(w) + 19, int(h) + 19), 12 * S,
                            outline=ACCENT + (int(255 * a),), width=4)
        pil.paste(ov, (int(x) - 20, int(y) - 20), ov)
        view = np.asarray(pil)
    return view


def draw_cursor(canvas, st, t):
    a = st.cur_alpha.at(t)
    if a <= 0.01:
        return canvas
    x, y = st.cur.at(t)
    # arc the path slightly, like a hand-moved mouse
    for t0, t1, v0, v1 in st.cur.seg:
        if t0 <= t < t1 and t1 - t0 > 0.01:
            u = (t - t0) / (t1 - t0)
            dx, dy = v1[0] - v0[0], v1[1] - v0[1]
            k = math.sin(math.pi * ease(u)) * 0.08
            x, y = x - dy * k, y + dx * k
    pil = Image.fromarray(canvas)
    for tc in st.clicks:
        dt = t - tc
        if 0 <= dt < 0.55:
            u = dt / 0.55
            r = 16 * S + 38 * S * ease(u)
            ov = Image.new("RGBA", (int(2 * r) + 8, int(2 * r) + 8), (0, 0, 0, 0))
            ImageDraw.Draw(ov).ellipse((4, 4, 4 + 2 * r, 4 + 2 * r), fill=ACCENT + (int(70 * (1 - u)),),
                                       outline=ACCENT + (int(230 * (1 - u)),), width=5)
            pil.paste(ov, (int(x - r - 4), int(y - r - 4)), ov)
    spr = cursor_sprite()
    sc = 1.0
    for tc in st.clicks:
        if 0 <= t - tc < 0.2:
            sc = 1 - 0.18 * math.sin(math.pi * (t - tc) / 0.2)
    if sc != 1.0:
        spr = spr.resize((int(spr.width * sc), int(spr.height * sc)), Image.BILINEAR)
    if a < 1:
        spr = spr.copy()
        spr.putalpha(Image.eval(spr.getchannel("A"), lambda v: int(v * a)))
    pil.paste(spr, (int(x - 4), int(y - 4)), spr)
    return np.asarray(pil)


def camera(canvas, st, t):
    s, cx, cy = st.cam.at(t)
    w, h = CW / s, CH / s
    x0 = min(max(cx - w / 2, 0), CW - w)
    y0 = min(max(cy - h / 2, 0), CH - h)
    pil = Image.fromarray(canvas)
    if abs(s - 1) < 1e-3:
        return pil.reduce(2)
    return pil.resize((OW, OH), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


def title_frame(kind, t, dur):
    wall = Image.fromarray(wallpaper_img())
    z = 1.0 + 0.035 * (t / dur)  # slow push-in
    w, h = CW / z, CH / z
    bg = wall.resize((OW, OH), Image.BICUBIC, box=((CW - w) / 2, (CH - h) / 2, (CW + w) / 2, (CH + h) / 2))
    bg = bg.convert("RGBA")
    lay = META[kind]["layers"]
    order = list(lay)
    for i, name in enumerate(order):
        t0 = 0.25 + i * 0.35
        u = ease((t - t0) / 0.9)
        if u <= 0:
            continue
        im = asset(("layer", kind, name), lambda n=name: Image.open(CAP / f"{kind}_{n}.png").convert("RGBA"))
        x, y, bw, bh = lay[name]
        sc = (0.86 + 0.14 * u) if name == "logo" else 1.0
        tw, th = int(bw * sc), int(bh * sc)
        im2 = im.resize((tw, th), Image.LANCZOS)
        if u < 1:
            im2.putalpha(Image.eval(im2.getchannel("A"), lambda v, u=u: int(v * u)))
        px = int(x + (bw - tw) / 2)
        py = int(y + (bh - th) / 2 + (1 - u) * 26)
        bg.alpha_composite(im2, (px, py))
    img = bg.convert("RGB")
    if kind == "outro" and t > dur - 1.2:
        k = ease((t - (dur - 1.2)) / 1.2)
        img = Image.fromarray((np.asarray(img) * (1 - k)).astype(np.uint8))
    if kind == "title" and t < 0.6:
        img = Image.fromarray((np.asarray(img) * ease(t / 0.6)).astype(np.uint8))
    return img


def scene_frame(st, t):
    if not st.web:
        return title_frame(st.page, t, st.sc["dur"])
    canvas = asset(("base", st.page), lambda: base_frame(st.page)).copy()
    view = draw_content(st, t)
    reg = canvas[CY0:CY0 + VH, CX0:CX0 + VW]
    canvas[CY0:CY0 + VH, CX0:CX0 + VW] = np.where(content_mask(), view, reg)
    canvas = draw_cursor(canvas, st, t)
    return camera(canvas, st, t)


# ----------------------------------------------------------------------------- frame driver
STATES = None
SCENES = None


def init():
    global STATES, SCENES
    SCENES, _ = timeline.build()
    STATES = build_states(SCENES)


def frame_at(T):
    idx = max(i for i, s in enumerate(SCENES) if s["start"] <= T + 1e-9)
    sc, st = SCENES[idx], STATES[idx]
    t = T - sc["start"]
    img = scene_frame(st, t)
    if idx > 0 and t < TR:
        pst = STATES[idx - 1]
        prev = scene_frame(pst, SCENES[idx - 1]["dur"] - 1 / FPS)
        u = ease(t / TR)
        kind = sc.get("transition", "fade" if pst.page != st.page else None)
        if kind == "slide":
            out = Image.new("RGB", (OW, OH))
            wall = asset("wall_small", lambda: Image.fromarray(wallpaper_img()).reduce(2))
            out.paste(wall)
            dx = int(OW * u)
            out.paste(prev, (-dx, 0))
            out.paste(img, (OW - dx, 0))
            img = out
        elif kind == "fade":
            img = Image.blend(prev, img, u)
    return img


def render_frame(i):
    return np.asarray(frame_at(i / FPS).convert("RGB")).tobytes()


def worker_init():
    init()


# ----------------------------------------------------------------------------- audio
SR = 48000


def read_wav(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768
        x = x.reshape(-1, w.getnchannels())
    if x.shape[1] == 1:
        x = np.repeat(x, 2, 1)
    return x


def mix_audio(total):
    n = int((total + 0.5) * SR)
    vo = np.zeros((n, 2), np.float32)
    fx = np.zeros((n, 2), np.float32)
    A = timeline.WORK / "audio"
    for sc, st in zip(SCENES, STATES):
        x = read_wav(timeline.WORK / "vo" / f"{sc['id']}.wav")
        s0 = int((sc["start"] + sc["lead"]) * SR)
        vo[s0:s0 + len(x)] += x[: n - s0]
        evs = list(st.sfx)
        if sc.get("transition") == "slide":
            evs.append((0.0, "whoosh", 0.8))
        for t, name, g in evs:
            y = read_wav(A / f"sfx_{name}.wav") * g
            s0 = int((sc["start"] + t) * SR)
            if s0 < n:
                fx[s0:s0 + len(y)] += y[: n - s0]
    bgm = read_wav(A / "bgm.wav")[:n]
    bgm = np.vstack([bgm, np.zeros((n - len(bgm), 2), np.float32)])
    # duck the score under the voice: smoothed envelope, fast attack, slow release
    env = np.abs(vo[:, 0])
    hop = 480
    e = env[: len(env) // hop * hop].reshape(-1, hop).max(1)
    sm = np.zeros_like(e)
    acc = 0.0
    for i, v in enumerate(e):
        acc = max(v, acc * 0.93)  # ~140 ms release per 10 ms hop
        sm[i] = acc
    speaking = np.clip(sm / 0.05, 0, 1)
    g = np.interp(np.arange(n) / hop, np.arange(len(sm)), 1 - 0.62 * speaking).astype(np.float32)
    # smooth the gain curve itself (moving average, 120 ms)
    k = int(0.12 * SR)
    c = np.cumsum(np.concatenate([[0], g]))
    g = ((c[k:] - c[:-k]) / k)
    g = np.concatenate([g, np.full(n - len(g), g[-1])]).astype(np.float32)
    mix = vo * 1.0 + bgm[:n] * (0.32 * g)[:, None] + fx * 0.55
    raw = OUTD / "mix_raw.wav"
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
    # two-pass loudness normalisation to YouTube's -14 LUFS, -1.5 dBTP
    r = subprocess.run([FF, "-hide_banner", "-i", str(raw), "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    out = OUTD / "mix.wav"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(raw), "-af",
                    f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
                    f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:"
                    f"offset={js['target_offset']}:linear=true,aresample=48000", str(out)], check=True)
    return out


# ----------------------------------------------------------------------------- main
def main():
    init()
    total = SCENES[-1]["start"] + SCENES[-1]["dur"]
    if "--still" in sys.argv:
        T = float(sys.argv[sys.argv.index("--still") + 1])
        frame_at(T).save(OUTD / "still.png")
        print("still", T)
        return
    nfr = int(total * FPS)
    if "--frames" in sys.argv:  # quick partial render: --frames a b (seconds)
        a, b = (float(v) for v in sys.argv[sys.argv.index("--frames") + 1:][:2])
        rng = range(int(a * FPS), int(b * FPS))
        vout = OUTD / "preview.mp4"
    else:
        rng = range(nfr)
        vout = OUTD / "video_only.mp4"
    enc = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-movflags", "+faststart", str(vout)], stdin=subprocess.PIPE)
    with mp.Pool(8, initializer=worker_init) as pool:
        for k, buf in enumerate(pool.imap(render_frame, rng, chunksize=6)):
            enc.stdin.write(buf)
            if k % 300 == 0:
                print(f"frame {k}/{len(rng)}", flush=True)
    enc.stdin.close()
    enc.wait()
    if "--frames" in sys.argv:
        print("preview", vout)
        return
    audio = mix_audio(total)
    final = OUTD / "privity-demo.mp4"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(vout), "-i", str(audio),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest",
                    "-movflags", "+faststart", str(final)], check=True)
    print("done", final)


if __name__ == "__main__":
    main()
