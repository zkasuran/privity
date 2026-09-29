# 6. GTM — strict-judge review (29 Sep 2026)

## Verdict (status, score /10, why)
**✅ Defined holds. Score 7/10.** Every checklist item is met, the targets are honestly marked "not contacted", and the falsification test is pre-committed. Points are lost because there is no price point, no sales-cycle estimate, no path to the first 10 customers, no partner channel, and no way to measure the developer funnel. The DTCC date is wrong, and the illustrative ROI works out per fund to less than any plausible fee.

## Gaps
1. **The ROI undercuts the pricing.** $2,100–$35,100 across 30 funds is about **$70–$1,170 per fund per year**. I checked the arithmetic and it is correct. A per-fund fee would cost more than the labour saving, and the asset never says so.
2. **There is no price number or pricing test.**
3. **No sales cycle is given.** A weeks 9–12 "live fund pilot" ignores vendor due diligence. EU fund-manager clients are under DORA from 17 Jan 2025, including a register of all ICT third-party arrangements ([MFSA](https://www.mfsa.mt/wp-content/uploads/2024/11/Regulation-EU-20222554-on-Digital-Operational-Resilience-for-the-Financial-Sector.pdf), [Goodwin](https://www.goodwinlaw.com/en/insights/publications/2024/01/alerts-finance-fs-what-dora-means-for-fund-managers)).
4. **There is no path to the first 10 customers.** The plan stops at one pilot.
5. **No partners are named.** Custodians and transfer agents are missing. DTCC's service covers assets in DTC participant accounts, and its first published use is Treasuries as collateral ([Markets Media](https://www.marketsmedia.com/dtcc-tokenization-service-will-improve-balance-sheet-efficiency/), [canton.network](https://www.canton.network/dtcc-tokenization-service-on-canton)). It is a "why now" signal, not a channel.
6. **The DTCC date is wrong.** The asset says "launched 13 September 2026". DTCC says it **launches October 2026** ([BusinessWire/Morningstar](https://www.morningstar.com/news/business-wire/20260715664564/dtcc-turns-tokenization-into-reality-us-trades-successfully-processed-using-dtc-tokenized-assets)). The same claim appears in README l.39, site/index.html l.217 and pitch.html l.99.
7. **The developer funnel can't be measured.** Daml has no package registry, so there is nothing to count "3 dependents" from. The repo is also private, so the funnel is at zero.
8. **The post-hackathon path is vague.** The asset has no AppsFactory step, and I found no public page with Season 3 accelerator terms. Featured App status needs a live DevNet, TestNet or MainNet deployment and the token standard "where applicable" ([docs](https://docs.canton.network/overview/understand/getting-app-featured)). It also earns usage rewards ([docs](https://docs.canton.network/appdev/app-rewards)), so "not revenue" is slightly wrong.
9. **The dated trigger is unused.** SEC comments close **3 Nov 2026** ([Federal Register](https://www.federalregister.gov/documents/2026/09/04/2026-18190/transfer-agent-rules)).

## Actions (ranked)
1. **Add the per-fund reconciliation and an honest caveat.** Owner: agent can do now (text below). Effort: 10 min. Effect: closes the worst logic hole before a judge finds it.
2. **Fix the DTCC date.** Owner: GTM text is agent now; README, site and pitch are founder only. Effort: 10 min. Effect: removes a checkable false claim.
3. **Add sales cycle, path to 10 and partners.** Owner: agent now (below). Effort: 15 min.
4. **Make the repo public and adopt the funnel metrics below.** Owner: founder only. Effort: 5 min. Effect: the funnel can't start before this.
5. **Price question in the first 3 interviews.** Owner: founder only. Script: *"What do you pay per fund per year for register or reconciliation tooling? At what per-fund price is removing cash-to-register breaks a non-decision, and at what price a procurement fight?"* Effect: the first real pricing data.
6. **Confirm AppsFactory post-hackathon terms in writing before citing them.** Owner: founder only.

## Drop-in text
**Section 5, replace the DTCC sentence:** "DTCC processed its first US trades with DTC-tokenized assets on 15 July 2026 and says its Tokenization Service launches in October 2026, with Canton among supported networks ([source](https://www.morningstar.com/news/business-wire/20260715664564/dtcc-turns-tokenization-into-reality-us-trades-successfully-processed-using-dtc-tokenized-assets)). SEC comments on the transfer agent proposal close 3 November 2026 ([Federal Register](https://www.federalregister.gov/documents/2026/09/04/2026-18190/transfer-agent-rules))."

**Append under the ROI block:** "Per fund, this is roughly $70–$1,170 a year. Labour saving alone does **not** justify a per-fund fee. The pricing hypothesis holds only if the excluded components, timing risk and audit evidence, carry most of the value. That is the first thing the interviews must test."

**New subsection, "Sales cycle and path to 10" (illustrative plan, not evidence):**
- *Cycle:* assume multi-quarter. Vendor risk review, assurance requests and, for EU clients, DORA third-party registers come before a live-fund pilot. The committed 90-day goal is a sandbox run on the administrator's own parameters. A live fund is a stretch goal.
- *Path to 10:* 10 named administrators → 15 interviews → 3 sandbox runs → 1 paid single-fund pilot → expand fund by fund inside that account. Canton-native issuers fill reference slots in parallel.
- *Partners (none contacted):* Canton registry app providers, fund custodians (cash leg), registered transfer agents (register of record).

**Developer funnel, how it's measured:** "Public signals only: GitHub stars and forks, release DAR download counts from the GitHub API, external issues and PRs, and teams confirming in writing that they depend on `privity-disclosure`. The target stays at 3 confirmed dependents in 90 days."

**Weeks 1–4, add:** "Apply to the AppsFactory post-hackathon track if offered *(terms to be confirmed)*."

## Journal update
GTM passes every template checklist item and names ten target administrators, none contacted. The illustrative ROI is correctly fenced, but per fund it comes to only about $70–$1,170 a year, so labour alone cannot carry a per-fund price. DTCC's Tokenization Service launches in October 2026, so the "launched 13 September" wording needs correcting in four places. There is still no price point, sales-cycle estimate or measurable developer-funnel metric, and the repo is still private.

## Overclaim risks
- "DTCC launched… 13 September 2026": false according to DTCC.
- "No other ledger offers [both] together" is absolute. Say "no public chain".
- Any AppsFactory acceptance or terms stated without written confirmation.
- The $2,100–$35,100 range shown anywhere without its "illustrative" fence. Today it appears only in the GTM doc.
