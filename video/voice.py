"""Voiceover: one neural TTS clip per scene, with word timings for cueing and captions.

Output: <work>/vo/<scene>.wav (48 kHz mono) and <work>/vo/words.json
"""
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import edge_tts
import imageio_ffmpeg

sys.path.insert(0, str(Path(__file__).parent))
import storyboard  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.environ.get("WORK", ROOT.parent / ".work")) / "vo"
OUT.mkdir(parents=True, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()


async def one(sc):
    com = edge_tts.Communicate(sc["vo"], storyboard.VOICE, rate=storyboard.RATE,
                               boundary="WordBoundary")
    audio, words = bytearray(), []
    async for ch in com.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            words.append(dict(w=ch["text"], t=ch["offset"] / 1e7, d=ch["duration"] / 1e7))
    mp3 = OUT / f"{sc['id']}.mp3"
    mp3.write_bytes(bytes(audio))
    wav = OUT / f"{sc['id']}.wav"
    # Light voice polish: high-pass rumble, gentle presence lift, de-harsh, then compress.
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(mp3), "-af",
                    "highpass=f=80,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1.2:g=2,"
                    "equalizer=f=7500:t=q:w=2:g=-2,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
                    "aresample=48000", "-ac", "1", str(wav)], check=True)
    dur = float(subprocess.run([FF, "-i", str(wav)], capture_output=True, text=True).stderr
                .split("Duration: ")[1].split(",")[0].split(":")[-1])
    return sc["id"], dict(words=words, dur=dur)


async def main():
    res = {}
    for sc in storyboard.SCENES:
        k, v = await one(sc)
        res[k] = v
        print(f"{k:10s} {v['dur']:5.2f}s {len(v['words'])} words")
    (OUT / "words.json").write_text(json.dumps(res, indent=1))
    print("total VO", round(sum(v["dur"] for v in res.values()), 1), "s")


if __name__ == "__main__":
    asyncio.run(main())
