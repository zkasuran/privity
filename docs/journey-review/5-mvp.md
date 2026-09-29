# 5. MVP State — agent 5/7 (29 Sep 2026)

## Verdict
Keep 🔄 today. It can move to ✅ Done once the repo, the video and the project are public and verified. The build is finished. What is still open is publication. "Hosted URL" is honestly met by the labelled replay of a verified LocalNet run, so no live ledger is needed. **Correction to the brief:** the site PR is already merged. privity-demo PR #1 merged 29 Sep 10:39 UTC. The live `/`, `/demo/` and `/demo/replay.json` are sha256-identical to `privity/site/`, and the replay carries the real package id `8c3a221b…19ba` (captured 25 Sep, privacy PASS). The PR still open is **privity #1** (`mvp-submission-hardening` → `main`) in the private code repo.

## Open items
| Item | Status today (checked) | Owner | Effort |
|---|---|---|---|
| Hosted demo URL (labelled replay) | ✅ `/` and `/demo/` return 200 | — | 0 |
| Replay refreshed to the 25 Sep run | ✅ Live | — | 0 |
| Site stale claims fixed | ✅ Live | — | 0 |
| README gaps and receipt contract | ✅ On branch, ⏳ not on `main` until privity PR #1 merges | Founder | 5 min |
| Video rendered with YouTube package | ✅ `video/out/privity-demo.mp4` (39 MB) | — | 0 |
| Video on YouTube | ⏳ Uploading. No URL to verify yet | Founder | 30 min |
| Code repo public | ❌ `github.com/zkasuran/privity` returns 404 (`private: true`). The landing page and video description both link to it | Founder | 2 min |
| Project published | ❌ Still "preview". The MANA prerequisite is met | Founder | 10 min |
| Live ledger / DevNet | Not built, and the README says so | — | See below |

"Replay packaging" keeps coming back in the digest because no journal entry has closed it. It is done: the replay is refreshed and labelled, and `reproduce.sh` regenerates the receipt that the replay renders. The founder has to say this in the journal, with URLs.

## Hosted/live ledger option analysis (sources with URLs)
- On DevNet, the validator's egress IP has to be allowlisted by the SVs, which "usually takes between 2-7 days". DevNet is reset every 3 months. [Canton docs, Validator Onboarding](https://docs.canton.network/global-synchronizer/deployment/onboarding-process)
- Moving from LocalNet to DevNet needs an onboarded validator and real auth in place of the default Keycloak users. [Canton docs, Deployment Progression](https://docs.canton.network/appdev/modules/m5-deployment-progression)
- A Node-as-a-Service provider is the other route. Cost and custody vary by provider. [CF Onboarding Guide](https://guide.canton.foundation/)
- The Season 3 post promises workshops and technical support but gives no DevNet details. [Canton forum](https://forum.canton.network/t/hackcanton-season-3-build-something-real-on-canton/9065)
- **I found no public page for a HackCanton/Noders DevNet sandbox or the "How to Spin Up Your Project on Canton" workshop.** They may be hub-only. Unverified.

**Options in 10 days**
- **A. Keep the labelled replay (recommended).** Effort 0, risk low. It is honest, already live, and reproducible.
- **B. Hackathon DevNet sandbox, if one exists.** `api/ledger.mjs` already reads its endpoint and JWT from env, so porting is mostly config: 1–2 days. Risks: vetting and auth on a shared node, DevNet resets during judging, and one more thing to re-verify. Only worth it if the hub confirms the sandbox by 1 Oct.
- **C. Self-hosted DevNet validator.** The 2–7 day allowlist wait plus VM and egress-IP ops use up the window and break the build freeze. Not recommended.

## Actions (ranked)
1. Merge privity PR #1, then make the repo public. Verify with `curl -I` while logged out (expect 200).
2. Finish the YouTube upload as unlisted, with `captions.en.srt`. Change visibility only after step 1. Add the URL to the README and the platform.
3. Publish the project on the platform.
4. Add a journal entry that closes "hosted URL / video / replay packaging" with the three URLs.
5. Optional: ask in the hub whether a DevNet sandbox exists. Drop it if there is no answer by 1 Oct.

## Submit-day checklist
- [ ] Clone `https://github.com/zkasuran/privity.git` while logged out. `main` contains the updated README.
- [ ] `dpm build --all` passes. `dpm test` shows 19 passing. `./reproduce.sh` prints `REPRODUCTION OK` and exits 0.
- [ ] These return 200: `/`, `/demo/`, `/demo/replay.json`, `/Privity-pitch.pdf`, the repo, and the YouTube URL (in a private window).
- [ ] Replay label is visible above the fold. The package id matches the `reproduce.sh` run, or the difference is explained.
- [ ] All links in the README, landing page, pitch PDF, video description and platform assets resolve.
- [ ] Video plays while logged out, with captions and the AI-voice disclosure.
- [ ] Status is "published", not "preview". Screenshot it before 9 Oct 23:59 UTC.

## Journal update (3-6 true sentences for today)
The public replay now shows the 25 Sep verified LocalNet run with its real package id, and the site PR is merged, so the live demo matches the repo. I fixed the stale claims on the landing and demo pages and rewrote the README's gaps section to list only real gaps. A 3:16 narrated demo video is rendered with a YouTube package and is being uploaded as unlisted. The hosted URL is deliberately a labelled replay, not a live ledger, and `./reproduce.sh` regenerates the same receipt. Still open: making the code repo public, merging the hardening PR, and publishing the project.

## Overclaim risks
- Do not call the demo "live", "on DevNet" or "on Canton Network". It is a replay of a LocalNet run.
- Do not claim the video is public before its URL plays while logged out.
- Do not call the code "open source". It is source-available, no derivatives, and it is currently private.
- The landing page and video description link to a repo that returns 404, so make it public before promoting either.
- Do not cite the hackathon DevNet sandbox or workshop. I could not verify either.
