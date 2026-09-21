# Metrics

**Status honestly stated up front.** Technical validation is credible and evidenced below. Market validation is not yet credible. Problem validation is unproven, because practitioner interviews have not been held. Nothing in this document dresses desk research or a passing test suite up as market evidence. The interview programme, its instrument and its pre-committed falsification test are in section 4.

---

## 1. North Star metric

- **Metric:** fund trades settled through Privity per week, where a trade is a subscription, a redemption or a secondary transfer that commits both legs in a single transaction.
- **Why this one:** it cannot be gamed by interest. It only moves if an administrator has actually stopped recording units separately from confirming cash, which is the exact behaviour change the product exists to cause. Sign-ups, demo views and stars can all rise while the old process continues untouched. This number cannot.
- **How you measure it:** count committed `SettleDvP`, `SettleSubscription` and `SettleRedemption` exercises on the ledger, by fund, per week. It is read from the transaction stream rather than self-reported.

---

## 2. What we needed to validate

| Assumption | Why it matters | Status |
| --- | --- | --- |
| Both legs can settle atomically across parties who cannot see each other's books | The entire premise. If it cannot be done, there is no product | ✅ confirmed by test, see section 3 |
| A counterparty can verify a trade without seeing the seller's full position | Without this, the privacy claim is false and the product is unsellable to this user | ✅ confirmed by test, which forced a redesign |
| A failed leg cannot leave a partial settlement | This is the difference between real DvP and two hopeful payments | ✅ confirmed by test |
| Fund administrators have the timing-gap problem acutely enough to change process | Determines whether the wedge is settlement or audit evidence | ⏳ testing, zero interviews held |
| The economic buyer is operations leadership rather than the auditor | Determines the whole GTM motion | ⏳ testing, reasoned not validated |
| They would pay or switch | Determines whether this is a business | ⏳ not started |
| NAV errors are a growing operational cost | Supports urgency | ✅ supported by regulator-counted data, see section 3 |

Three of the four confirmed rows are confirmed by our own tests, which proves the system works rather than that the market wants it. That distinction is the honest reading of this table.

---

## 3. Tests and results

### 3a. Ledger tests, 15 of 15 passing

Run with `dpm test`. 11 of 11 templates created. Two tests are written to **fail if the product claim is false**, which is the only kind of test that counts as evidence rather than demonstration.

| Test | The claim it would break |
| --- | --- |
| `testBuyerCannotSeeSellersRemainingPosition` | Asserts a buyer can read the parcel it bought and **cannot** read the units the seller kept, checked before and after settlement. If this passes falsely, the confidentiality claim is void |
| `testDvpFailsWhenBuyerCannotPay` | Buyer is short of cash, the whole transaction is rejected, leaving the parcel still the seller's and undelivered. Proves no partial settlement |
| `testDvpSettlesAtomically` | Both legs commit, originals archived, each side keeps exact change |
| `testCannotSettleParcelEarmarkedForAnother` | A parcel disclosed to one buyer cannot be settled by a different buyer |
| `testParcelSizeMustMatchProposal` | A seller cannot earmark a small parcel then claim to be selling a large one |
| `testCannotPayWithAnothersCash` | Cannot pay with cash you do not own |
| `testSubscriptionSettlesAtomically` / `testRedemptionSettlesAtomically` | Primary issuance and redemption are atomic, not just secondary trades |
| `testMandateLifecycle`, `testAuditorCannotSelfGrantMandate`, `testInvertedWindowRejected` | An auditor cannot manufacture visibility over an unwilling subject, revocation needs a stated reason, malformed windows are refused |
| `testDisclosureOutsideWindowFails` | Disclosure inside a mandate window records, outside it is refused |
| `testNavAttestation` | The administrator signs, the manager and a named auditor see it, a non-positive NAV is refused |

**What we changed because of a test.** The most valuable result was a failure. The first implementation had the buyer verify the trade by reading the seller's share holding. Canton rejected it because the buyer is not a stakeholder on that contract. The obvious repair, adding the buyer as an observer, would have disclosed the seller's whole position while still passing every happy-path test. We redesigned so the unit of disclosure is a parcel rather than a holding, then added four tests to hold that line. **Both versions compiled and both settled correctly, so only a test written to falsify the claim distinguishes them.**

### 3b. Reproducibility, measured

| What | Result |
| --- | --- |
| LocalNet from nothing to healthy | about 2 minutes on warm images, Splice 0.8.1, full stack |
| Packages vetted on the participant | 2 of 2 (`privity-disclosure` 1.0.0, `privity` 1.0.0) |
| Production DARs carrying a `daml-script` dependency | **0**, verified with `dpm inspect-dar` after splitting tests into their own package |
| Host preflight | all checks pass via `canton-devkit localnet doctor` |

### 3c. Market signal, desk research, verified but not validation

- **NAV calculation error notifications to Luxembourg's CSSF rose from 238 in 2019 to 462 in 2022**, while investment compliance breach notifications *fell* over the same window (1,497 to 1,382). The operational failure mode is the one growing. *Reported by Deloitte Luxembourg from CSSF activity reports 2017 to 2022.*
- CSSF Circular 02/77 requires that investors who suffered a loss from a NAV error are protected. The same source records an "increase in the number of normal procedures (including compensation to investors)". So the error has a cash consequence, not only a reputational one.
- Under CSDR Article 7, "cash penalties shall be calculated on a daily basis for each business day that a transaction fails to be settled". Supporting context for why regulated markets price the gap between two legs. **Not a claim that our ICP pays CSDR penalties**, since CSDR covers CSD-settled securities rather than private fund flows.
- DTCC launched a tokenization service on Canton on 13 September 2026, which is the timing signal for why this decision is live now.

Full sourcing, including what we refused to cite and why, is in `DATA-SOURCES.md`. Two figures were deliberately left out: a settlement fail percentage we could not attribute to a column with confidence, plus generic accounts-payable cost-per-document statistics that describe an unrelated workflow.

---

## 4. Conversations and documentary evidence

### 4a. Interviews

| # | Who (role, company type) | Date | Key takeaway |
| --- | --- | --- | --- |
| n/a | none held yet | n/a | n/a |

**There is no strongest quote, because there are no conversations.** Stating that plainly is more useful to a judge than a padded table. A padded table would discredit section 3, which is real.

### 4b. Documentary evidence from the public record

Interviews are not the only form of evidence about what practitioners experience. Regulators publish their own characterisation of how an industry operates. That characterisation is on the record, checkable and not subject to the interviewee-politeness problem. Where we could not yet obtain practitioner conversations, we went to the documentary record instead. It turned out to say something stronger than a quote would have.

**The SEC's September 2026 transfer agent modernization proposal.** The single most relevant piece of external evidence we hold.

| What the proposal says | Why it is evidence for us |
| --- | --- |
| The framework being replaced has core processing, recordkeeping and safeguarding requirements dating to the late 1970s and early 1980s, built for "a market where securities were represented by physical certificates and transactions and related records were processed manually" | The regulator, not us, describes the current operating model as manual. This is the problem statement in the regulator's own words |
| Proposed Rules 17ad-2 and 17ad-10 move transfer and register posting to a **one-business-day** framework tied to the settlement cycle, replacing a 90%-within-three-business-days standard | The timing gap we remove is a gap a regulator is actively moving to close. Our hypothesis about its importance no longer rests on our judgment |
| "for uncertificated securities, prompt posting and turnaround are effectively the same event" | The strongest sentence we have found anywhere. The regulator's position is that transfer and register update should be one event. Privity makes them one transaction |
| The definition of "item" is extended to cover "an electronic system controlled, operated, or enabled by the transfer agent", expressly to capture instructions sent through "blockchains and other distributed ledger-based platforms" | Our infrastructure choice is contemplated rather than tolerated |
| Proposed Rule 17ad-31 requires maintaining a current list of authorized issuer employees, acting only on instructions from that list, then memorialising written determinations with supporting facts and approval | Independent regulatory validation of the shape of our `DisclosureMandate`: authority recorded in advance, exercised only by an entitled party, with retained evidence |
| Rescission of Rule 17ad-4 removes exemptions for transfer agents processing limited partnership interests, DRIPs and redeemable open-end fund securities, a population the SEC estimates at **approximately 200 registered transfer agents** | A regulator-sourced count of firms in our product scope about to face accelerated standards. Better grounded than our own estimate |

*All of the above is cited from Morgan Lewis's published analysis of the proposing release, dated 8 September 2026, which gives release page numbers. We have not read the release directly because sec.gov returns 403 to scripted access. Upgrading that citation is a tracked task.*

**What this evidence can and cannot do.** It establishes that the problem is real, that it is recognised by a regulator and that the timing is now. It does **not** establish that a specific administrator will change process, pay or prefer our approach to a cheaper workflow tool. Only interviews do that. Documentary evidence moves problem validation, not market validation. We are not going to claim otherwise.

**Deliberately not done: synthetic interviews.** We considered generating simulated practitioner interviews and rejected it. The programme's code of conduct prohibits misrepresenting work, the mentor guidance explicitly rejects "interviews that are actually pitches". A fabricated quote in front of a judge would invalidate every real number on this page. Sections 3 and 4b are real precisely because section 4a is empty.

### 4c. The interview programme, instrument built and ready

- **Target:** 5 to 8 interviews held, **at least 3 from the exact ICP** (fund accounting, transfer agency or fund operations lead at a third-party administrator or a self-administering manager). Adjacent conversations with auditors, lawyers and vendors are logged separately and do not count toward the 3.
- **Instrument:** `VALIDATION-GUIDE.md`. Six sections, product not described until section 5 so answers are not bent toward it, every question asks what happened last month rather than what they would hypothetically use.
- **Outreach:** `submit/OUTREACH-privity.html`, with a named target list of 10 mid-tier administrators. 8 requests sent to yield 5 held.
- **A new and better channel.** The SEC comment period on the transfer agent proposal is open, comments due 60 days after Federal Register publication. The SEC has asked specifically for "concrete data on item volumes and time-of-day receipt patterns, exception and rejection rates, investment company and other specialized workflows, systems-upgrade costs". Comment letters on that docket will be named practitioners describing this exact workflow with numbers attached, in public. Reading them as they are filed is now part of the validation plan. It is a route to practitioner voice that does not depend on anyone answering our email.

### Pre-committed falsification test

> The wedge is wrong if **3 or more ICP interviews** say the timing gap between cash and register is already handled well enough by their existing bank and reconciliation workflow, then say they would not change process for it.

If that happens, the stated response is to move the product rather than defend it: the pain worth solving becomes the audit trail and disclosure evidence, the buyer moves to the auditor or the manager, then the disclosure package becomes the product with atomic DvP as a feature of it. **We will publish this result whichever way it goes.**

Secondary falsifier: if nobody volunteers a confidentiality refusal unprompted, the privacy half of the thesis solves a problem this user does not feel, so the positioning should lead on atomicity alone.

### Scorecard to be filled honestly

| Measure | Target | Actual |
| --- | --- | --- |
| Interviews held | 5 to 8 | 0 |
| From the exact ICP | at least 3 | 0 |
| Named the same workflow unprompted | majority | not yet |
| Produced a hard number | at least 2 | not yet |
| Produced a strong confidentiality refusal | at least 1 | not yet |
| Falsification test result | support / break | not yet run |

---

## 5. Product and on-ledger metrics

| Metric | How we measure it | Now | Target by submission |
| --- | --- | --- | --- |
| Ledger tests passing | `dpm test` | 15 of 15 | 15 or more, all passing |
| Templates exercised | `dpm test` coverage report | 11 of 11 created | 11 of 11, choice coverage above 70% |
| Packages vetted on a participant | `localnet dar list` | 2 | 2, plus the same flow over the JSON Ledger API |
| Atomic settlements executed over the real Ledger API | count committed settle exercises | 0, tests run on the IDE ledger | at least 3, one of each settlement type |
| Users who tried the demo | unique visitors completing the core flow | 0, no UI exists yet | a working hosted demo, plus 5 or more walkthroughs |
| Transactions on DevNet or MainNet | ledger query | 0 | LocalNet is the committed target, DevNet a stretch |
| Active parties | allocated parties in a demo run | 6 in tests (manager, administrator, cash issuer, auditor, two investors) | same 6 over the real Ledger API |

Two rows deliberately read zero. There is no UI, so nobody has tried a demo. Tests run against the IDE ledger, which proves the model but not the same behaviour over the real Ledger API with allocated parties. Claiming otherwise would be the easiest lie on this page to tell and the easiest for a judge to catch.

---

## 6. Success criteria after the hackathon

| Metric | Target in 90 days |
| --- | --- |
| ICP interviews completed and synthesised | 15 |
| Administrators running a sandbox against their own fund parameters | 2 |
| Funds with a live settlement flow, any volume | 1 |
| Other Canton teams depending on `privity-disclosure` | 3 |
| Atomic settlements on DevNet or MainNet | 50 |
| Falsification test run and published | yes, whatever the outcome |

The disclosure package row matters as much as the fund rows. If the primitive is adopted by teams building something other than a fund, that is independent evidence the disclosure problem is real, from people with no reason to be polite to us.

---

## 7. What we still don't know

- **Whether the timing gap is acute enough to change process.** The single biggest open question. Answer: the interview programme above, with a falsification test that can kill the wedge.
- **Whether the pain owner can actually authorise a change.** The economic buyer is reasoned to be operations leadership, not tested. Answer: ask who signed off the last process change, in every interview.
- **What confidentiality floor is genuinely acceptable.** We know a buyer must see the parcel and must not see the book. We do not know whether an administrator will accept the fund manager being a signatory on every share holding, which our current model requires. Answer: walk the actual stakeholder list past three practitioners and record objections.
- **Whether the holdings digest design is meaningful to an auditor.** It is currently a placeholder string rather than a computed commitment, so we do not claim verifiable NAV. Answer: compute it from real holdings, then show it to a fund auditor.
- **Whether behaviour matches the model over the real Ledger API.** Answer: run all three settlement types over the JSON Ledger API with allocated parties before submission.

---

## Checklist

- [x] One North Star metric with a clear definition
- [ ] At least 3 conversations with potential users. **0 held. Instrument and target list ready. This is the known gap**
- [x] Assumptions are marked confirmed, rejected or still testing
- [x] At least one test with a number attached
- [x] Current values and targets are filled in
- [x] You show what changed because of what you learned
