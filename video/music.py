"""Original background score, synthesised from scratch (no samples, no third-party audio).

Warm ambient-tech bed at 96 BPM in A minor: detuned-saw pad, sine sub bass, plucked arpeggio
with stereo delay, and soft drums. Arranged to the scene timeline: pad-only intro, build under
the product story, lift for the proof, breakdown under the code, resolve on the outro.

Output: <work>/audio/bgm.wav (48 kHz stereo) and sfx_*.wav
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import timeline  # noqa: E402

SR = 48000
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
OUT = timeline.WORK / "audio"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def onepole_lp(x, fc):
    """One-pole low-pass; fc may be an array (time-varying)."""
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    # vectorised in blocks: coefficient changes slowly so hold it per block
    B = 256
    for i in range(0, len(x), B):
        ai = a[i]
        seg = x[i:i + B]
        out = np.empty_like(seg)
        for j, v in enumerate(seg):
            acc = (1 - ai) * v + ai * acc
            out[j] = acc
        y[i:i + B] = out
    return y


def lp_fast(x, fc):
    """Static low-pass by FFT brickwall-with-slope, cheap for long signals."""
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(x.shape[0], 1 / SR)
    g = 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X * (g[:, None] if x.ndim == 2 else g), n=x.shape[0], axis=0)


def hp_fast(x, fc):
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(x.shape[0], 1 / SR)
    g = 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X * (g[:, None] if x.ndim == 2 else g), n=x.shape[0], axis=0)


def saw(freq, n, phase=0.0):
    t = np.arange(n) / SR
    # band-limited-ish saw from 10 harmonics
    y = np.zeros(n)
    for k in range(1, 11):
        if freq * k > 12000:
            break
        y += np.sin(2 * np.pi * freq * k * t + phase * k) / k
    return y * 0.55


def env_adsr(n, a, d, s, r):
    e = np.full(n, s)
    na, nd, nr = min(int(a * SR), n), int(d * SR), min(int(r * SR), n)
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, s, len(e[na:na + nd]))
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


# A minor-ish progression, each chord 2 bars: Am9, Fmaj7, Cadd9, G6
CHORDS = [
    [57, 60, 64, 67, 71],   # A C E G B
    [53, 57, 60, 64, 67],   # F A C E G
    [48, 55, 60, 62, 64],   # C G C D E
    [55, 59, 62, 64, 67],   # G B D E G
]
ROOTS = [33, 29, 36, 31]
ARP = [[69, 72, 76, 79], [65, 69, 72, 76], [67, 72, 74, 76], [67, 71, 74, 79]]


def section_levels(scenes, total):
    """Per-layer gain curves over time following the arrangement."""
    n = int(total * SR)
    t = np.arange(n) / SR
    start = {s["id"]: s["start"] for s in scenes}

    def ramp(points):
        xs, ys = zip(*points)
        return np.interp(t, xs, ys)

    end = total
    pad = ramp([(0, 0), (2.5, 1), (end - 4, 1), (end, 0)])
    bass = ramp([(0, 0), (start["hero"] - 1, 0), (start["hero"] + 1, 1),
                 (start["code"] - 1, 1), (start["code"] + 1, 0.35), (start["repro"] - 1, .35),
                 (start["repro"] + 1, 1), (start["outro"] + 2, 1), (end - 2, 0), (end, 0)])
    arp = ramp([(0, 0.25), (start["hero"], 0.6), (start["stepper"], 1), (start["code"], 0.8),
                (start["outro"] + 3, 0.8), (end - 1, 0), (end, 0)])
    drums = ramp([(0, 0), (start["stepper"] - 2, 0), (start["stepper"] + 2, 0.8),
                  (start["banner"], 1), (start["code"] - 1.5, 1), (start["code"] + 0.5, 0),
                  (start["repro"] - 1, 0), (start["repro"] + 1.5, 1), (start["outro"] + 1, 1),
                  (start["outro"] + 4, 0), (end, 0)])
    return pad, bass, arp, drums


def render(total, scenes):
    n = int(total * SR)
    L = np.zeros(n)
    R = np.zeros(n)
    nbars = int(np.ceil(total / BAR)) + 1
    # --- pad
    for b in range(0, nbars, 2):
        ci = (b // 2) % 4
        s0 = int(b * BAR * SR)
        ln = int(2 * BAR * SR + 1.5 * SR)
        if s0 >= n:
            break
        ln = min(ln, n - s0)
        seg_l, seg_r = np.zeros(ln), np.zeros(ln)
        for note in CHORDS[ci]:
            f = midi(note)
            for det, pan in ((-0.09, 0.8), (0.0, 0.5), (0.1, 0.2)):
                v = saw(f * 2 ** (det / 12), ln, rng.uniform(0, 6))
                seg_l += v * pan
                seg_r += v * (1 - pan)
        e = env_adsr(ln, 1.2, 0.5, 0.85, 1.6)
        L[s0:s0 + ln] += seg_l * e * 0.05
        R[s0:s0 + ln] += seg_r * e * 0.05
    # slow filter motion on the pad
    L, R = lp_fast(L, 1400), lp_fast(R, 1400)
    pad = np.stack([L, R], 1)

    # --- bass: root on beat 1 and the "and" of 3
    bass = np.zeros(n)
    for b in range(nbars):
        ci = (b // 2) % 4
        for off, ln_b in ((0, 2.3), (2.5, 1.3)):
            s0 = int((b * BAR + off * BEAT) * SR)
            ln = int(ln_b * BEAT * SR)
            if s0 >= n:
                continue
            ln = min(ln, n - s0)
            tt = np.arange(ln) / SR
            f = midi(ROOTS[ci] + 12)
            v = np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)
            v = np.tanh(1.6 * v) * env_adsr(ln, 0.01, 0.2, 0.6, 0.12)
            bass[s0:s0 + ln] += v * 0.16
    bass = lp_fast(bass, 500)

    # --- arp: 8th-note plucks through chord tones, octave jumps, stereo delay
    arp = np.zeros((n, 2))
    patt = [0, 1, 2, 3, 2, 1, 3, 2]
    for b in range(nbars):
        ci = (b // 2) % 4
        for k in range(8):
            s0 = int((b * BAR + k * BEAT / 2) * SR)
            if s0 >= n:
                continue
            note = ARP[ci][patt[k]] + (12 if (k == 6 and b % 2) else 0)
            ln = min(int(0.9 * SR), n - s0)
            tt = np.arange(ln) / SR
            f = midi(note)
            v = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 18)
                 + 0.12 * np.sin(6 * np.pi * f * tt) * np.exp(-tt * 30))
            v *= np.exp(-tt * 6.5) * (0.9 if k % 2 == 0 else 0.7)
            pan = 0.5 + 0.25 * np.sin(k * 0.8 + b)
            arp[s0:s0 + ln, 0] += v * pan * 0.05
            arp[s0:s0 + ln, 1] += v * (1 - pan) * 0.05
    d1, d2 = int(BEAT * 0.75 * SR), int(BEAT * 1.5 * SR)
    dl = np.zeros_like(arp)
    dl[d1:, 1] += arp[:-d1, 0] * 0.35
    dl[d1:, 0] += arp[:-d1, 1] * 0.35
    dl[d2:] += arp[:-d2] * 0.18
    arp = lp_fast(arp + dl, 5000)

    # --- drums
    drums = np.zeros(n)
    kick_len = int(0.35 * SR)
    tt = np.arange(kick_len) / SR
    kick = np.sin(2 * np.pi * (45 * tt + 60 * (1 - np.exp(-tt * 30)) / 30)) * np.exp(-tt * 9)
    hat_len = int(0.06 * SR)
    snr_len = int(0.22 * SR)
    for b in range(nbars):
        for beat in range(4):
            s0 = int((b * BAR + beat * BEAT) * SR)
            if s0 + kick_len < n and beat in (0, 2):
                drums[s0:s0 + kick_len] += kick * 0.33
            if s0 + snr_len < n and beat in (1, 3):
                nz = rng.standard_normal(snr_len) * np.exp(-np.arange(snr_len) / SR * 22)
                drums[s0:s0 + snr_len] += nz * 0.032
            h0 = int((b * BAR + (beat + 0.5) * BEAT) * SR)
            if h0 + hat_len < n:
                nz = rng.standard_normal(hat_len) * np.exp(-np.arange(hat_len) / SR * 70)
                drums[h0:h0 + hat_len] += nz * 0.02
    drums = lp_fast(hp_fast(drums, 30), 8500)

    g_pad, g_bass, g_arp, g_dr = section_levels(scenes, total)
    mix = pad * g_pad[:, None] + (bass * g_bass)[:, None] + arp * g_arp[:, None] \
        + (drums * g_dr)[:, None] * np.array([0.95, 1.0])

    # --- reverb: FFT convolution with a decaying stereo noise tail
    irn = int(2.4 * SR)
    ti = np.arange(irn) / SR
    ir = rng.standard_normal((irn, 2)) * np.exp(-ti * 2.6)[:, None]
    ir = lp_fast(ir, 6000)
    ir /= np.sqrt((ir ** 2).sum(0))
    N = 1 << int(np.ceil(np.log2(n + irn)))
    wet = np.fft.irfft(np.fft.rfft(mix, N, axis=0) * np.fft.rfft(ir, N, axis=0), N, axis=0)[:n]
    out = mix * 0.8 + wet * 0.45
    out = np.tanh(out * 1.4) / 1.4
    out /= np.abs(out).max() / 0.8
    return out


def sfx():
    def save(name, x):
        write(OUT / f"sfx_{name}.wav", np.stack([x, x], 1) if x.ndim == 1 else x)
    # click: short tick + tiny body
    n = int(0.08 * SR)
    tt = np.arange(n) / SR
    click = (rng.standard_normal(n) * np.exp(-tt * 400) * 0.5 +
             np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 120) * 0.35)
    save("click", hp_fast(click, 600) * 0.8)
    # whoosh: band-passed noise sweep with a swell
    n = int(0.7 * SR)
    tt = np.arange(n) / SR
    nz = rng.standard_normal(n)
    env = np.sin(np.pi * np.clip(tt / 0.7, 0, 1)) ** 2
    lo = lp_fast(nz, 2500) - lp_fast(nz, 300)
    wh = np.stack([lo * env * np.linspace(1, .4, n), lo * env * np.linspace(.4, 1, n)], 1)
    save("whoosh", wh / np.abs(wh).max() * 0.35)
    # key: soft keyboard tap
    n = int(0.05 * SR)
    tt = np.arange(n) / SR
    key = rng.standard_normal(n) * np.exp(-tt * 250)
    save("key", hp_fast(key, 1500) * 0.35)
    # pop: highlight appear
    n = int(0.18 * SR)
    tt = np.arange(n) / SR
    pop = np.sin(2 * np.pi * (660 + 500 * tt) * tt) * np.exp(-tt * 28)
    save("pop", pop * 0.16)


def write(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    scenes, total = timeline.build()
    write(OUT / "bgm.wav", render(total + 0.5, scenes))
    sfx()
    print("bgm", round(total + 0.5, 1), "s")
