# 1. Problem — strict-judge review (29 Sep 2026)

## Verdict (current status, and what a judge would score it /10 and why)
Status: ✅ Defined. I'd hold it there, but the problem needs these fixes before submission. My strict score is **7/10**. What works: a one-sentence problem with a named user, an honest before/after, careful labelling of the estimate, a limit stated for CSDR, and "why now" tied to a regulatory event only weeks old. What costs points: (a) the core cost, meaning the timing gap and reconciliation labour, has no number or source; (b) one cited rule has been repealed; (c) the DTCC "launched" claim goes further than DTCC itself says; (d) a paraphrase is shown in quote marks as if it were the SEC's words; (e) the evidence covers Lux UCIs and US registered transfer agents, but the ICP is private-fund administrators.

## Gaps
1. **Core cost has no source.** Line 14 says "A gap of hours to days… Period end is a multi-day manual exercise per fund." Nothing supports it. The two sourced numbers cover NAV errors, which is a nearby problem, not the cash-to-register gap.
2. **Stale rule.** Line 26 cites "CSSF Circular 02/77 governs…". [CSSF 24/856](https://www.cssf.lu/wp-content/uploads/CSSF24_856eng.pdf) repealed 02/77, and the replacement has applied since 1 Jan 2025 ([CSSF](https://www.cssf.lu/fr/2024/03/la-cssf-publie-la-reforme-de-la-circulaire-cssf-02-77-concernant-les-erreurs-de-calcul-de-la-vni-et-linobservation-des-regles-de-placement/), [EY](https://www.ey.com/en_lu/insights/wealth-asset-management/circular-24-856-nav-calculation-errors)). The asset uses the present tense for a repealed circular.
3. **Wrong source.** Line 26 says "The same source notes an 'increase in the number of normal procedures'". That line is in the Deloitte deck, not the circular (docs/DATA-SOURCES.md §2).
4. **"Rising" is simplified.** The series runs 251, 245, 238, 444, 352, 462 for 2017–2022 ([Deloitte](https://www.deloitte.com/content/dam/assets-zone2/lu/en/docs/industries/financial-services/2023/lnl-13092023.pdf)). Starting at 2019, the low point, flatters the trend, and the data stops in 2022. The asset never links NAV errors to the settlement gap.
5. **Paraphrase shown as a quote.** Line 46 puts "for uncertificated securities, prompt posting and turnaround are effectively the same event" in quote marks. In [Morgan Lewis](https://www.morganlewis.com/pubs/2026/09/sec-proposes-comprehensive-modernization-of-transfer-agent-rules-signals-further-progress-on-framework-for-tokenized-securities) it is their summary ("The SEC emphasizes that…"), not quoted SEC text. README line 42 repeats it.
6. **Headline claims too much.** Line 42 says "A regulator has just proposed requiring what we built." The proposal sets T+1 turnaround and posting. It does not require atomic DvP.
7. **DTCC claim is wrong.** Line 54 says "DTCC launched a tokenization service on Canton on 13 September 2026." The only source for that date is a forum repost of a Canton marketing page ([forum](https://forum.canton.network/t/dtcc-tokenization-service-launches-on-canton/9132)). DTCC's own releases say the service launches in **October 2026** ([Morningstar/BusinessWire](https://www.morningstar.com/news/business-wire/20260715664564/dtcc-turns-tokenization-into-reality-us-trades-successfully-processed-using-dtc-tokenized-assets)). The published use cases are Treasuries and collateral, not fund units ([canton.network](https://www.canton.network/dtcc-tokenization-service-on-canton)). README line 39 repeats it.
8. **Unsourced claim.** Line 54 says tokenized funds are "among the most active build categories on the network". No source is given.
9. **Scope mismatch is never stated.** Rule 17ad-4 covers *registered* US transfer agents, including those for *registered* open-end funds. Many private-fund administrators are not registered transfer agents. The ~200 figure and the "precisely the fund products in scope for us" wording (line 50) need that caveat.
10. **Missing "why now" fact.** Comments on the proposal are due **3 Nov 2026** ([NatLawReview](https://natlawreview.com/article/sec-proposes-sweeping-modernization-transfer-agent-rules)). The asset doesn't mention it.

## Actions
1. Replace 02/77 with 24/856 and fix the "same source" attribution. Owner: agent can do now (text below); founder pastes. Effort: 10 min. Effect: removes a stale-fact deduction.
2. Rewrite the DTCC line using the dates DTCC itself gives, and remove "most active build categories". Owner: agent can do now; the same fix is needed in README line 39 (founder, since I can't edit the repo). Effort: 10 min. Effect: removes the highest-risk overclaim.
3. Remove the quote marks from the Morgan Lewis paraphrase and soften the "requiring what we built" headline. Owner: agent can do now; README line 42 is founder only. Effort: 5 min.
4. Add the scope caveat and the 3 Nov comment deadline. Owner: agent can do now. Effort: 5 min.
5. Mark the line 14 cost figures as a hypothesis until an interview confirms them. Owner: founder only. Script: *"From the wire landing to the register update, how long is the gap on a typical subscription, and how many days does period-end reconciliation take per fund?"* Ask this in the first 3 ICP calls. Effort: in the calls already planned. Effect: the only route to a sourced core-cost number, and the main thing standing between this section and a 9/10.
6. Read the SEC release (Federal Register 2026-18190) in a browser and confirm the Morgan Lewis figures against it. Owner: founder only. Effort: 30 min. Effect: moves the citation from secondary to primary.

## Drop-in text
**Replace the line 26 bullet:**
- **A NAV error triggers a correction and compensation procedure.** In Luxembourg, errors in NAV calculation are handled under CSSF Circular 24/856, which replaced Circular 02/77 from 1 January 2025 ([CSSF](https://www.cssf.lu/wp-content/uploads/CSSF24_856eng.pdf)). Deloitte Luxembourg's summary of CSSF activity reports also records an increase in "normal procedures (including compensation to investors)" ([Deloitte](https://www.deloitte.com/content/dam/assets-zone2/lu/en/docs/industries/financial-services/2023/lnl-13092023.pdf)).

**Replace the line 25 lead-in:** "**NAV errors, counted by a regulator, rose over the period.** Notifications to the CSSF went from 251 (2017) to 462 (2022), dipping to 238 in 2019, while investment compliance breaches fell from 1,540 to 1,382 over the same years."

**Replace line 42:** "**A regulator has just proposed collapsing the register update into the settlement cycle.**"

**Replace lines 45–46:** "Morgan Lewis summarises the SEC's view: for uncertificated securities, prompt posting and turnaround are effectively the same event. Comments are due 3 November 2026."

**Add after line 50:** "Caveat: Rule 17ad-4 applies to registered US transfer agents. Many private-fund administrators are not registered as transfer agents, so this marks the direction of regulation, not a mandate on our ICP."

**Replace line 54:** "**The register is also moving on chain.** DTCC processed its first US trades using DTC-tokenized assets on 15 July 2026 and says its Tokenization Service launches in October 2026, with Canton as one of the supported networks ([BusinessWire via Morningstar](https://www.morningstar.com/news/business-wire/20260715664564/dtcc-turns-tokenization-into-reality-us-trades-successfully-processed-using-dtc-tokenized-assets)). The first published use is Treasuries as collateral, not fund units."

**Line 14, Today cell:** add "*(working assumption from desk research, not yet confirmed by practitioners)*" after "multi-day manual exercise per fund."

## Journal update
I re-checked the Problem section's citations against public sources today. Circular CSSF 02/77 was replaced by 24/856 on 1 January 2025, so the value asset will cite 24/856. DTCC's own releases put its Tokenization Service launch in October 2026, so "launched 13 September" comes out of the asset and the README. The "same event" line comes from Morgan Lewis's summary of the SEC proposal and will be attributed that way. The cost of the cash-to-register gap is still a working assumption until practitioner interviews happen, and none have happened yet.

## Overclaim risks
- "DTCC launched a tokenization service on Canton on 13 September 2026" (asset line 54, README line 39). DTCC itself says October 2026.
- "A regulator has just proposed requiring what we built." It hasn't. Nothing in the proposal requires atomic DvP.
- A Morgan Lewis paraphrase presented as a quote from the SEC.
- 02/77 described as the rule that "governs" NAV errors. It was repealed and replaced by 24/856.
- "Hours to days" and "multi-day per fund" presented as fact, with no source.
- "Most active build categories", with no source.
- "Precisely the fund products in scope for us": the ICP is private-fund administrators, who are often not registered transfer agents.
