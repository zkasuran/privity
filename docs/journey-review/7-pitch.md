# 7. Pitch — agent 7/7 (29 Sep 2026)

## Verdict
**🔄 Draft, 7/10.** Strong story and honest limits. Draft because:
- The PDF (`0218d7c`) still says **18** tests on slides 6 and 12.
- There is no video link, and "Demo" points to the landing page, not `/demo/`.
- The code link returns 404 because the repo is private.
- Three slides overclaim.

Digests 21–28 Sep repeat "six-line pitch in progress", adding the paper opening, NAV as *supporting* proof, and the three-"One" framing. No journal entry has said "final". No "placeholder"/"in progress" text remains; DAR versions are right.

## Slide audit
| Slide | Issue | Fix |
|---|---|---|
| 1 | Doesn't use the framing the digest asked for | Put the three-"One" lead in |
| 2 | Strong hook. DTCC has no citation | Add a source |
| 3 | "written our spec" overstates a *proposal*. The ~200 figure is an upper bound | Soften and qualify |
| 4 | "no other ledger" is an absolute | Limit it to what we tested |
| 6 | 18 is stale. The NAV row differs from the site | 19, and use the site's NAV row wording |
| 8 | The version sentence doesn't name the package | Name it |
| 9 | "no settlement risk" is asserted, not shown | Tie it to the docs |
| 10 | Pricing isn't labelled as a hypothesis. No GTM line | Label it and add GTM |
| 5, 7, 11 | Strong, consistent with site and assets | None |
| 12 | 18/18, wrong demo URL, no video, repo 404, no team | Rewrite |

**Missing:** GTM and team; fold into slides 10 and 12.

## Final six-line pitch
1. Tokenized fund trades still settle like paper: cash on one rail, units typed into a register later, a person reconciling the gap.
2. Privity settles both legs in one Canton transaction, so units and cash cannot separate.
3. Each counterparty sees only the parcel it is buying. Queried as the buyer, the ledger returns none of the seller's retained units, and a test fails the build if it ever does.
4. An entitled auditor recomputes the sha256 commitment behind a NAV attestation. Change one unit and it fails. A non-entitled party can't run the check.
5. Proof: 19 passing Daml tests, a labelled public replay of a verified LocalNet run, and `reproduce.sh`. Not yet done: practitioner interviews.
6. Buyer: operations at mid-tier fund administrators, with per-fund pricing as a hypothesis. Ask: three administrator introductions and a design review of `privity-disclosure`.

## 60-second spoken pitch
> Tokenized fund trades still settle like paper. Cash moves on one rail, units get typed into a register afterwards, and someone at a fund administrator reconciles the gap by hand. The SEC's September proposal says that for uncertificated securities, posting and turnaround are effectively the same event.
>
> Privity makes them one transaction on Canton. The seller earmarks exactly the parcel being sold. The buyer pays and takes it in a single commit, both legs or neither. Query the ledger as the buyer and the seller's retained units aren't there, and a test breaks the build if they ever are. An entitled auditor can also recompute the hash behind the NAV.
>
> Nineteen tests pass, the verified run is public as a labelled replay, and one command reproduces it.
>
> What we don't have is practitioner interviews. So our ask is three introductions to fund administrators, and a design review of our disclosure package.

## Exact slide edits
Edit `brand/pitch.html`, re-render per `brand/README.md`, copy the PDF to `site/`.

| # | Current | Replacement |
|---|---|---|
| 1 | lead "Both legs of a tokenized fund trade settle in one Canton transaction, and each counterparty sees only the parcel it is buying." | "Fund trades still settle like paper. **One transaction. One parcel per counterparty. One verifiable holdings commitment.**" |
| 2 | cite ends "…analysis of the proposing release." | append " DTCC launch per its 13 Sept 2026 announcement." (use the source already cited in the assets) |
| 3 | "The regulator has already written our spec." | "The regulator's proposal describes the event we built." |
| 3 | "~200 registered transfer agents in the exemption being rescinded" | "Up to ~200 registered transfer agents (SEC upper-bound estimate) in the exemption proposed for rescission" |
| 4 | "Two properties that no other ledger offers *together*." | "Two properties we needed *together*, and got on Canton." |
| 6 | `18` | `19` |
| 6 | "NAV is checkable, not just signed" | "NAV is tied to a specific book" |
| 8 | "so 1.1.0 vets as a valid upgrade of 1.0.0." | "so privity-disclosure 1.1.0 vets as a valid upgrade of 1.0.0." |
| 9 | "needs no model change, and carries no settlement risk because no value moves until the atomic step." | "is documented by Canton, and is not demonstrated here." |
| 10 | "Per fund per year, plus a platform fee" | "Hypothesis, untested: per fund per year, plus a platform fee" |
| 10 | "One sale, thirty deployments" | "Hypothesis: one sale, many funds" |
| 10 | (add) | "**GTM:** direct outbound to ten named mid-tier administrators, none approached yet. Warm paths first, then Canton ecosystem contacts. The disclosure package is a second, developer funnel." |
| 12 | Demo row `https://zkasuran.github.io/privity-demo/` | **Verified run (replay)** `https://zkasuran.github.io/privity-demo/demo/` · **Video (3:16)** `<YouTube URL once it plays logged out>` · **Site** `https://zkasuran.github.io/privity-demo/` · **Code** (make the repo public first) |
| 12 | (add) | "**Team:** zkasuran, solo builder." |
| 12 | "dpm test passes 18 of 18 … demo URL returns 200 anonymously." | "dpm test passes 19 of 19 … site, verified run, video and repo return 200 anonymously." |

**Final** when: edits re-rendered, every slide-12 URL returns 200 logged out, and a journal entry says "pitch final" with the six-line pitch.

## Journal update
The deck source still says 18 tests on slides 6 and 12, while the suite and the landing page say 19. I am fixing that, linking the verified-run replay, and softening three claims. The 3:16 demo video is rendered but has no public URL yet, so the deck will link it only once it plays logged out. The code link returns 404 until the repo is made public. The six-line pitch is now fixed, with calibrated disclosure as the centrepiece and verifiable NAV as a supporting proof.

## Overclaim risks
- **"Written our spec" / "no other ledger."** A proposal via a law-firm reading; an absolute a judge can dispute.
- **"Verified" commitment.** Say *verifiable*. It's verified by an entitled party in the one recorded run.
- **"Live participant."** Fine for the recorded LocalNet run. Never say live demo, DevNet or Canton Network.
- **Pricing, "thirty deployments", $2.1k–$35.1k.** Hypothesis/illustrative; keep fenced.
- **Apache-2.0.** Only *intended*; today source-available, no derivatives, private.
- **Interviews.** Keep "zero practitioner interviews" on slide 9. SEC comment letters are not interviews.
