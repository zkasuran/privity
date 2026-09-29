# Journey review, 29 Sep 2026

Seven agents reviewed one journey section each. Their full reports are next to this file
(`1-problem.md` … `7-pitch.md`). This page is the combined plan.

## Where each section stands

| Section | Digest status | Agent score | What holds it back |
|---|---|---|---|
| 1 Problem | ✅ | 7/10 | The core cost ("hours to days") has no source; some citations were stale (fixed today) |
| 2 ICP | ✅ | 6/10 | Named firms are far larger than the stated size band; the budget holder isn't identified |
| 3 Solution | ✅ | 7/10 | Settlement never checks the cash issuer or the share manager (a real code gap) |
| 4 Validation | ⚠️ Weak | – | **Zero practitioner conversations.** Nothing else can move this |
| 5 MVP | 🔄 | – | Build done. Open: repo private, project unpublished, video not public, no journal entry closing it |
| 6 GTM | ✅ | 7/10 | No price point, sales cycle or path to 10; per-fund ROI below any plausible fee (caveat added) |
| 7 Pitch | 🔄 Draft | 7/10 | Stale facts (fixed today), no video link, no journal entry marking it final |

## Fixed today (verified against primary sources)

- **DTCC**: "launched on Canton 13 Sep 2026" was wrong. DTCC says its Tokenization Service
  launches **October 2026** ([release](https://www.morningstar.com/news/business-wire/20260715664564/dtcc-turns-tokenization-into-reality-us-trades-successfully-processed-using-dtc-tokenized-assets)).
  Corrected in 3 platform assets, the README, the landing page and the deck.
- **CSSF 02/77** was repealed by **24/856** from 1 Jan 2025 ([CSSF](https://www.cssf.lu/wp-content/uploads/CSSF24_856eng.pdf)).
- **"Same event" line** was a Morgan Lewis paraphrase shown as an SEC quote; it is now attributed to Morgan Lewis.
- Overclaims softened: "regulator has written our spec", "requiring what we built", "no other ledger".
- Metrics §5 table said "15 of 15" and "no UI exists yet". It now reflects 19 tests, the JSON Ledger
  API run and the public replay, and states that subscription and redemption are still Daml Script only.
- "8 requests sent" corrected to "planned, none sent".
- `ledger.mjs`, `reproduce.sh` and the README no longer claim the live flow subscribes and redeems.
- Deck: 18 → 19 tests, the verified-run URL, and the edits above. PDF re-rendered.

## Founder-only actions, in order

1. **Make the repo public** (the code link returns 404 everywhere). 2 min.
2. **Upload the video** (unlisted, with `captions.en.srt`), then send me the URL. I'll add it to
   the deck, README and platform.
3. **Publish the project** on the platform (MANA 1000/1000, `can-publish` is ready).
4. **Post the journal entry below** to your mentor chat today. The digest is written from the journal,
   so work that isn't journaled doesn't move the statuses.
5. **Validation, the only path from Weak:** send 8 warm and 8 cold LinkedIn requests and ask the
   Canton/BitSafe mentors for intros. Hold 3+ exact-ICP 15-minute calls by 6 Oct. Script, outreach
   text and evidence table are in `4-validation.md`. Log only what was actually said.
6. **Decide on the settlement issuer checks** (`3-solution.md` gap 1). It's a few asserts plus two
   tests, but it breaks the build freeze and needs `dpm test` on your machine. A Daml judge, or
   today's Hacken AI Daml Auditor demo, would likely find it.

## Journal entry to post today

> Day 12 update. Build is frozen; today was verification and submission hardening.
> MVP: the public demo now shows the 25 Sep verified LocalNet run with its real package id,
> clearly labelled as a replay; `./reproduce.sh` regenerates that same receipt. A 3:16 narrated
> demo video is rendered and being uploaded. The hosted URL is deliberately a labelled replay,
> not a live ledger. Open: making the repo public and publishing the project.
> Citation check: DTCC's Tokenization Service launches in October 2026 (I had wrongly written
> "launched 13 Sep"); CSSF 02/77 was replaced by 24/856 in 2025; the "same event" line is Morgan
> Lewis's summary of the SEC proposal, not SEC text. All corrected in the assets, README and deck.
> Pitch: the deck is updated to 19 tests, links the verified run, and drops three overclaims. The
> six-line pitch is final (below).
> Validation: still zero practitioner conversations. I've fixed the method, a 15-minute interview
> script with a falsification question, and demand-test thresholds before any outreach:
> ≥3 exact-ICP calls held by 6 Oct; builder post ≥3 substantive replies or ≥1 issue in 7 days.
> Outreach starts today.
>
> Six-line pitch:
> 1. Tokenized fund trades still settle like paper: cash on one rail, units typed into a register later, a person reconciling the gap.
> 2. Privity settles both legs in one Canton transaction, so units and cash cannot separate.
> 3. Each counterparty sees only the parcel it is buying; queried as the buyer, the ledger returns none of the seller's retained units, and a test fails the build if it ever does.
> 4. An entitled auditor recomputes the sha256 commitment behind a NAV attestation; change one unit and it fails, and a non-entitled party can't run the check.
> 5. Proof: 19 passing Daml tests, a labelled public replay of a verified LocalNet run, and one-command reproduction. Not yet done: practitioner interviews.
> 6. Buyer: operations at mid-tier fund administrators, per-fund pricing as a hypothesis. Ask: three administrator introductions and a design review of `privity-disclosure`.

## What will and won't change the statuses

- **MVP → Done** and **Pitch → Final** are within reach this week: steps 1–4 above.
- **Validation → Strong** needs real conversations. No document edit can get there honestly, and
  inventing evidence is the fastest way to lose the judges.
