# Demo video

A 3:16 narrated walkthrough in the Screen Studio style: a floating window over a wallpaper,
smooth zooms that follow the action, a smoothed cursor with click ripples, spotlight highlights,
typed terminal output, an original score that ducks under the narration, and UI sound effects.

The rendered file is [`out/privity-demo.mp4`](out/privity-demo.mp4) (1080p30, 40 MB). It is built entirely from code, so it
can be regenerated whenever the site changes.

## What is on screen, and where it comes from

| Scene | Source |
| --- | --- |
| Landing page and the Alice/Bob stepper | `site/index.html`, clicked through in headless Chromium |
| Verified run: banner, claims, timeline, atomic transaction, visibility matrix | `site/demo/` rendering `site/demo/replay.json`, the 25 Sep 2026 run on a LocalNet participant |
| Daml code | Real excerpts of `app/daml/Privity/Settlement.daml` and `Fund.daml`, with their real line numbers |
| Terminal receipt | The receipt block of `reproduce.sh` run against `ui/replay.json` from that same run. The window title says so |

Nothing is mocked or retyped. The terminal scene replays the receipt of the recorded run; it
does not claim to be a live LocalNet session.

## Build

Needs Python 3.9+, Node and network access for the TTS voice.

```bash
python -m venv .venv && . .venv/bin/activate
pip install numpy pillow imageio-ffmpeg playwright edge-tts pygments
python -m playwright install chromium
(cd ../site && python -m http.server 8765 &)   # capture reads the site from here

python capture.py   # screenshots at 2x + element boxes
python voice.py     # narration per scene, with word timings
python music.py     # original score + UI sound effects
python render.py    # composite, mix, loudness-normalise -> privity-demo.mp4
python package.py   # YouTube package in youtube/
```

Intermediate files go to `../../.work` (override with `WORK=`). `python render.py --still 42`
renders a single frame at 42 s for checking a shot.

| File | Role |
| --- | --- |
| `storyboard.py` | Narration and actions per scene. Actions are cued to spoken words (`"w:buyer"`), so editing the script keeps the visuals in sync |
| `timeline.py` | Scene start times and resolved cues |
| `render.py` | Compositor. Renders on a 3840x2160 canvas so zooms up to 2x stay sharp, outputs 1080p30 H.264 with AAC 320k at -14 LUFS |

## YouTube package (`youtube/`)

`title.txt` (plus alternatives), `description.txt` with chapters and links, `tags.txt`,
`chapters.txt`, `captions.en.srt`, `thumbnail.jpg` (1280x720), `pinned-comment.txt`, and
`metadata.json` in the YouTube Data API `videos.insert` shape.

Upload notes:

- Category Science & Technology, not made for kids, visibility `unlisted` until the repository
  linked in the description is public.
- Upload `captions.en.srt` as English subtitles rather than relying on auto-captions, so Daml
  and Canton terms are spelled correctly.
- The narration is AI text-to-speech (Microsoft Edge neural voice via `edge-tts`) and says so in
  the description. It is not a realistic depiction of a real person, so YouTube's altered or
  synthetic content label is not required, though turning it on is harmless.
- The music is original, synthesised in `music.py`, so there is no Content ID claim to clear.
