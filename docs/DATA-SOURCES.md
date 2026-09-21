# Privity: third-party sources

House rule: every third-party input gets its terms and its granting clause recorded before
it enters the build. Nothing here is redistributed. These are factual figures and legal
references cited with attribution in the submission materials, which is quotation rather
than republication of a dataset. Where a figure is reported by an intermediary rather than
read from the primary source, that is stated, because "regulator says X" and "a consultancy
says the regulator says X" are different claims.

---

## 1. SEC transfer agent modernization proposal, September 2026 (the strongest "why now")

**This is the most important source in the file.** Three weeks before our submission deadline,
the SEC proposed a comprehensive rewrite of the rules governing registered transfer agents,
explicitly to accommodate distributed-ledger technology and tokenized securities.

Verified via Morgan Lewis LawFlash, 8 September 2026, which cites the proposing release with
page numbers. Quotes below are from that analysis of the release.

**The regulator's own characterisation of the current state:**
> "The Proposal represents a significant update to a regulatory framework whose core
> processing, recordkeeping, and safeguarding requirements date back to the late 1970s and
> early 1980s, reflecting a market where securities were represented by physical certificates
> and transactions and related records were processed manually."

**Its stated objective, release page 9:**
> "The SEC's stated objective is to align those requirements with modern electronic securities
> markets, including the increasing use of distributed-ledger technology and tokenized
> securities."

**The single most relevant provision to Privity, proposed Rules 17ad-2 and 17ad-10.** The
proposal would move core transfer and record-posting to a **one-business-day framework tied to
the settlement cycle**, replacing today's standard of turning around at least 90% of routine
items within three business days. Rule 17ad-10 would apply the same one-business-day standard
to "posting debits and credits to the master securityholder file following an issuance,
purchase, transfer, or redemption". And critically:

> "The SEC emphasizes that, for uncertificated securities, prompt posting and turnaround are
> effectively the same event."

That is the regulator saying the register update and the transfer should collapse into one
event for uncertificated securities. **Privity makes them literally one transaction.** This is
the strongest available answer to "why now" and to "why does atomicity matter to this user".

**Technology neutrality written into the definition of "item", release page 73.** The
definition would be extended to include "an electronic system controlled, operated, or enabled
by the transfer agent", specifically so that "instructions transmitted by or through both
existing technologies, such as blockchains and other distributed ledger-based platforms, and
new, even unforeseen, technologies are captured".

**A regulator-sourced population number, release page 228 fn. 414.** The proposal would rescind
Rule 17ad-4, which currently exempts transfer agents processing **limited partnership
interests, DRIPs and redeemable securities of registered open-end investment companies**, plus
small transfer agents under 500 items. The SEC estimates **approximately 200 registered
transfer agents may currently fall within Rule 17ad-4**, while noting that figure includes
firms that outsource all transfer agent activity or may not be actively providing services.

**Use this number carefully.** It is a count of US registered transfer agents relying on one
exemption, not a count of our ICP, and the SEC itself qualifies it. It is still far better
grounded than our own "low thousands globally" estimate, and it says something useful: the
population of firms about to be pulled into accelerated processing standards for exactly the
fund products we target is small, named and regulated. Small buyer set, high deal value, which
is what the GTM already assumes.

**An authorization-list requirement that mirrors our mandate model, proposed Rule 17ad-31.**
A transfer agent would have to "obtain and maintain a current list of issuer employees
authorized to provide instructions concerning the issuance of securities and the placement and
removal of restrictive legends and only act on instructions from a person on that list", plus
memorialise written determinations with supporting facts and management approval. That is the
same shape as `DisclosureMandate`: authority recorded in advance, acted on only by an entitled
party, with evidence retained.

**Also relevant:** proposed Rule 17ad-12 recasts safeguarding as comprehensive risk management
and would require third-party funds held in a designated "for the benefit of" account, which
the SEC says is "intended to reduce commingling risk". Proposed Rule 17ad-30 would require a
board-approved written compliance program.

**Comment period.** Comments are due 60 days after Federal Register publication, so the window
is open now. The SEC "asks for quantitative information, not only legal or policy views",
naming "concrete data on item volumes and time-of-day receipt patterns, exception and rejection
rates, investment company and other specialized workflows, systems-upgrade costs". Comment
letters filed on this docket will be public practitioner voice on precisely our workflow, and
are worth reading as they arrive.

- Morgan Lewis analysis: https://www.morganlewis.com/fr/pubs/2026/09/sec-proposes-comprehensive-modernization-of-transfer-agent-rules-signals-further-progress-on-framework-for-tokenized-securities
- SEC statements, 1 September 2026 (Uyeda, Peirce) on sec.gov/newsroom. **Note: sec.gov returns
  403 to scripted fetches, so the proposing release has not been read directly.** Every figure
  above is therefore cited as "per Morgan Lewis's analysis of the proposing release", with the
  release page numbers they give, until the release itself is read in a browser.
- Terms: Morgan Lewis LawFlash is a public client alert, attorney advertising. Quote with
  attribution, do not reproduce wholesale. The underlying SEC release is US government work.

**TODO before submission:** open the proposing release in a browser and confirm the
one-business-day posting standard, the "prompt posting and turnaround are effectively the same
event" line, and the ~200 firm estimate against the primary text. Then upgrade the citations.

## 2. CSSF NAV calculation error notifications


**Figures, verified by extracting the source document rather than trusting a search snippet:**

| Year | NAV calculation errors notified | Investment compliance breaches | Total notifications |
| --- | --- | --- | --- |
| 2017 | 251 | 1,540 | 1,791 |
| 2018 | 245 | 1,607 | 1,852 |
| 2019 | 238 | 1,497 | 1,735 |
| 2020 | 444 | 1,800 | 2,244 |
| 2021 | 352 | 1,644 | 1,996 |
| 2022 | **462** | 1,382 | 1,844 |

**Why it matters for us.** NAV calculation errors notified to a single regulator went from
238 in 2019 to 462 in 2022, roughly doubling, while investment compliance breaches fell over
the same period. So the failure mode that is growing is the *operational* one, the production
of the number, not the portfolio one. That is precisely the surface Privity touches.

The source document's own stated conclusions, quoted:
> "Decrease of the number of notifications due to decrease in investment compliance breaches"
> "Increase in the number of notifications for NAV calculation errors"
> "Increase in the number of normal procedures (including compensation to investors)"

**Attribution, stated precisely.** The figures appear in a Deloitte Luxembourg presentation
(`lnl-13092023.pdf`, "© 2023, Deloitte Tax & Consulting, SARL"), which labels the chart
`Source : CSSF activity reports 2017 to 2022`. So the primary source is the CSSF activity
reports and Deloitte is the intermediary. **In the materials this must be cited as
"reported by Deloitte Luxembourg from CSSF activity reports 2017 to 2022", not as a direct
CSSF citation**, until the individual activity reports are read.

- Deloitte deck: https://www.deloitte.com/content/dam/assets-zone2/lu/en/docs/industries/financial-services/2023/lnl-13092023.pdf
- Terms: standard Deloitte publication, no redistribution licence granted. We quote figures
  and the three conclusion bullets with attribution. **Do not reproduce the deck or its charts.**
- TODO to upgrade the citation: pull CSSF annual activity reports 2019 and 2022 directly and
  confirm 238 and 462 in the primary text.

## 2. CSSF Circular 02/77 (the regulatory consequence)

The Luxembourg circular governing the treatment of NAV calculation errors and instances of
non-compliance with investment rules, including the obligation to compensate investors who
suffered a loss.

Quoted from the circular:
> "It is the responsibility of the UCIs' promoters to ensure that any errors are correctly
> dealt with in strictest compliance with the rules of conduct specified in this circular.
> This is of a primordial importance not only because the interests of the UCIs and/or of the
> investors having suffered a loss need to be protected, but it must be ensured that investors
> maintain their trust in the integrity of collective management professionals"

- https://www.cssf.lu/wp-content/uploads/cssf02_77eng.pdf
- Superseded/updated in part by Circular CSSF 24/856:
  https://www.cssf.lu/wp-content/uploads/CSSF24_856eng.pdf
- Terms: public regulatory text published by the CSSF. Quoting with attribution is standard.

**Why it matters for us.** A NAV error is not merely embarrassing, it triggers a compensation
procedure. That is the cash cost behind our `NavAttestation` design, and it is why an
attestation signed by the administrator with a commitment to the holdings it was computed
from is worth more than a number in a PDF.

## 3. CSDR Article 7, cash penalties for settlement fails (the DvP consequence)

Quoted from ESMA's interactive single rulebook:
> "Cash penalties shall be calculated on a daily basis for each business day that a
> transaction fails to be settled after its intended settlement date until the transaction is
> either settled or bilaterally cancelled. The cash penalties shall not be configured as a
> revenue source for the CSD."

- https://www.esma.europa.eu/publications-and-data/interactive-single-rulebook/csdr/article-7-measures-address-settlement-0
- Terms: public EU regulatory text. ESMA content is reusable with attribution.

**Why it matters for us.** In the EU, failing to settle is directly and daily financially
penalised. It establishes that "the gap between the two legs has a price" is a regulatory
fact rather than our opinion. Note the honest limit: CSDR governs CSD-settled securities,
**not** private fund subscription flows, so this is supporting context for why atomic DvP is
treated as important in regulated markets, not a claim that our specific ICP pays CSDR
penalties. Do not overstate this in the materials.

## 4. Clearstream CSDR settlement efficiency reports (measured fail rates)

Public annual CSDR settlement efficiency disclosures showing measured fail rates by count
and value, including fails "due to lack of securities or lack of cash".

- https://www.clearstream.com/resource/blob/4269614/9c9e79d9213fde47d3f5d0c7ecaf1449/cbf-sett-rep-2024-data.pdf
- and sibling CBL / CBFI reports under the same path
- Terms: public regulatory disclosure by the CSD.

**Status: NOT YET SAFE TO CITE A NUMBER.** The search snippets returned fragmentary figures
(3.09%, 4.74%, 7.33%, 3.17%) without reliable column context, so it is not currently clear
which is count versus value, nor which entity. Either read the PDF tables properly before
quoting a percentage, or cite only the existence of the measurement. **Do not put a
percentage in the materials off the back of a snippet.**

## 5. ESMA statement on the 27 February 2025 T2S/T2 incident (contagion illustration)

A hardware failure made T2S and T2 unavailable for hours, delaying participant
reconciliation and creating settlement fails on following days, with effects beyond the T2S
settlement currencies.

> "participants were also delayed in their reconciliation processes, creating settlement
> fails over the next settlement days"

- https://www.esma.europa.eu/sites/default/files/2025-03/ESMA74-2119945926-3232_Statement_on_non-application_of_cash_penalties_due_to_major_incident_affecting_T2S_and_T2.pdf
- Terms: public ESMA statement.

**Why it matters for us.** A concrete, dated, regulator-documented case where a reconciliation
delay propagated into settlement failures. Useful as the "this is not hypothetical" line.

## 6. Global Fund Media, "The Great Disconnect" (industry survey, unverified)

Reported as a Q3 2025 survey of 100+ hedge fund managers globally on the cost of manual
processes, plus expert interviews.

- http://issuu.com/globalfundmedia/docs/the_great_disconnect_the_true_cost_of_manual_pro
- **Status: UNVERIFIED.** Only the abstract was read. Do not cite any figure from it until
  the methodology and the specific numbers are read. Also note it covers hedge funds, which
  is adjacent to but not identical with our private-fund administrator ICP.

## 7. DTCC tokenization service on Canton

Announced on the Canton Network forum, 13 September 2026.

- https://forum.canton.network/t/dtcc-tokenization-service-launches-on-canton/9132
- Used as a timing signal for "why now", nothing more.

---

## Rejected or to-be-avoided sources

- Generic "manual data entry costs $X per employee" and "invoice processing costs $13"
  statistics (Ardent Partners, Parseur/QuestionPro, MineralTree). These are real numbers about
  **unrelated workflows**. Borrowing an accounts-payable figure to size a fund settlement
  problem is the kind of stretch a judge catches, and it would undermine the figures that are
  genuinely on point. Not used.
- Vendor blog assertions about NAV reconciliation pain (SimCorp, Limina, Milemarker, Caruso,
  feFundinfo). Useful for vocabulary and for confirming the workflow is recognised, but they
  are marketing for competing products, so they are not evidence. May be cited as "vendors in
  this space describe the same workflow", never as a measurement.
