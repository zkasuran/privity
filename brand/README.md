# Brand and pitch assets

| File | What it is |
| --- | --- |
| `logo.svg` | Source mark. A register of holdings with exactly one parcel lit. The dim tiles are the book a counterparty never sees, the lit row is the parcel it is buying |
| `logo-1024/512/256/128.png` | Rendered sizes. Checked at 128px, where the single lit row still reads |
| `pitch.html` | The deck source. Twelve slides at 1280x720 |
| `Privity-pitch.pdf` | The deck, rendered. Regenerate with the command below |

Regenerate the PDF:

```bash
cd brand && python3 -m http.server 8877 &
google-chrome --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=Privity-pitch.pdf --virtual-time-budget=8000 http://localhost:8877/pitch.html
```

Two things that went wrong the first time and are worth not repeating. The `font` shorthand
with `inherit` for the family silently drops the size, so the stat numbers rendered at body
size; use explicit `font-size` and `font-weight`. And slides need
`display:flex; justify-content:center` or the content sits top-heavy with half the slide empty.

Every figure in the deck traces to a real ledger run or a cited public source, and the slide
on what is not done is deliberate rather than modest.
