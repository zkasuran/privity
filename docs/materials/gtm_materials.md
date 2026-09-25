# GTM: Go-to-Market

## 1. Positioning

**In one sentence:**
For **fund accounting and transfer agency leads at mid-tier fund administrators** who **record units separately from confirming cash and reconcile the two by hand**, **Privity** is **settlement infrastructure for tokenized funds** that **commits both legs of a trade in one Canton transaction**. Unlike **a bank wire plus a manual register update**, **each counterparty is shown only the parcel it is buying, never the other side's book**.

- **What do users do today instead?** A document and wire workflow. Signed subscription PDF, investor wires cash, administrator watches the bank feed and then types units into the admin system, with period-end reconciliation across register, bank and custodian records by hand. Secondary transfers are a signed form plus a manual register edit.
- **Why Canton rather than any other chain?** Because this needs two properties at once that no other ledger offers together. Atomic multi-party settlement exists on any public chain, but only alongside broadcast visibility that publishes every investor's position to every other investor, which ends the conversation with this buyer. Confidentiality exists off-chain, but only by keeping cash and register as separate events, which is the problem itself. Canton's sub-transaction privacy means one transaction can commit across parties while each participant validates only the views its own parties are stakeholders on. We did not take this on trust: our first design was rejected by the ledger for trying to read a contract the buyer was not a stakeholder on, which is the property working against our own code.

---

## 2. First customers

- **Segment:** mid-tier third-party fund administrators, 20 to 60 funds under administration, with a dedicated transfer agency or fund accounting function. Plus, as a distinct second pool, Canton-native issuers already tokenizing fund products.
- **Why them first:** the mid-tier administrator holds the register **and** produces NAV, so both legs of the problem land on one desk and one person can describe the whole workflow. They are also large enough to have the pain and small enough to buy rather than build. The Canton-native pool matters for a different reason: they have no legacy register to replace, so they can adopt in days rather than quarters.
- **First targets:** Gen II Fund Services, Standish Management, Aduro Advisors, Langham Hall, Bolder Group, plus Trident Trust, Ocorian, Waystone, IQ-EQ and Alter Domus behind them. **These are targets, not contacts. None has been approached.** Pool B is teams building on Canton around the DTCC tokenization service launched on 13 September 2026, plus HackCanton entrants working on fund and RWA workflows. Pool B are reference logos and product signal, explicitly **not** a revenue story.

---

## 3. Distribution channels

| Channel | Why it reaches our users | First concrete action | Effort / cost |
| --- | --- | --- | --- |
| **Direct outbound on LinkedIn by role title** | The role is unusually title-searchable: "fund accounting", "transfer agency", "head of fund operations" plus a firm filter returns the exact person | Send 8 requests from the prepared outreach pack to yield 5 held conversations, at least 3 from the exact ICP | Low cost, high time per contact. Already built |
| **SEC comment docket on the transfer agent proposal** | Named practitioners are publishing descriptions of this exact workflow, with numbers, because the SEC asked for quantitative data | Read letters as filed, synthesise the repeated operational language, approach the firms that filed | Low cost. Public record. Reading only |
| **Canton ecosystem channels** | Reaches Pool B directly, where adoption is fastest and reference value is highest | Post the working demo in the Canton forum and developer channels, ask for introductions rather than attention | Low cost. Warm audience |
| **The disclosure package as a developer channel** | `privity-disclosure` is a standalone Daml package any Canton app can depend on. No other entry is offering reusable infrastructure to other builders | Release it for Apache-2.0 adoption after the competition, with the privacy test as the reason to trust it | Low cost, plus it compounds |
| **Fund operations and transfer agency conferences** | Where the buyer and the influencer are in one room | Identify one event per quarter, lead with the regulatory deadline rather than the technology | Higher cost, slower. Not first |

Deliberately **not** first: a channel play through the incumbent admin software vendors. They sit inside the workflow, which is exactly why they are slow, political and procurement-heavy. That is a later-stage move once there is a customer to point at.

---

## 4. Acquisition hypotheses

| Hypothesis | How we test it | Success metric | Status |
| --- | --- | --- | --- |
| We believe **mid-tier fund administrators** will **give 20 minutes to a stranger asking about subscription settlement** because **the workflow frustration is chronic and nobody asks them about it** | 8 outreach messages from the prepared pack, warm where the ecosystem allows | 5 conversations held, at least 3 from the exact ICP | ⏳ not started, instrument and target list ready |
| We believe the **timing gap between cash and register** is felt as a real cost rather than an accepted fact of life | Ask for the last specific instance and the worst gap in the last year, never "would you use this" | 3 or more unprompted descriptions of the gap, with at least 2 hard numbers | ⏳ this is the falsification test, see below |
| We believe **confidentiality is a hard constraint rather than a feature** | Ask what would be unacceptable if the register moved onto a shared ledger, without prompting | At least 1 unprompted strong refusal, captured verbatim | ⏳ not started |
| We believe **Canton-native issuers will adopt faster than administrators** because they have no legacy register | Offer a LocalNet walkthrough against their own fund parameters | 2 teams run the demo with their own numbers inside a week | ⏳ not started |
| We believe **other Canton teams will adopt the disclosure package** if it is standalone and tested | Release it permissively after the competition and watch dependents | 3 projects depending on `privity-disclosure` in 90 days | ⏳ blocked until the competition ends |

**The falsification test, committed in advance.** If 3 or more ICP interviews say the timing gap is already handled well enough by their bank and reconciliation workflow and they would not change process for it, the wedge is wrong. The stated response is to move the product rather than defend it: the pain becomes the audit trail and disclosure evidence, the buyer becomes the auditor or the manager, then the disclosure package becomes the product with atomic settlement as a feature of it. We will publish the result either way.

---

## 5. Business model

- **Who pays, against what unit:** the administrator pays, per fund per year, for settlement and disclosure infrastructure applied to the funds it services. The unit is the fund because that is how administrators already price their own service to managers, so it needs no new mental model on their side.
- **Pricing hypothesis:** a platform fee plus a per-fund deployment fee. **Not per seat**, because the value is process containment rather than user productivity. Not per settlement either, because transaction pricing reads as a utility rather than compliance-grade infrastructure and makes the buyer's cost unpredictable in exactly the way procurement hates. All three of those are hypotheses and none has been tested on a buyer.
- **Building the savings estimate honestly.** Four components, to be filled from interviews rather than invented: reconciliation hours saved per fund per period, exception handling and escalation cost avoided, timing-risk reduction, plus the control and compliance benefit. We do not yet have a **validated** per-administrator figure and we will not present one as validated until the inputs come from practitioners. What we can show, fenced off as illustrative and built only from public data with every assumption on the table, is the order of magnitude:

```text
Illustrative annual savings per fund administrator
(public-data model, no practitioner validation yet, shown separately from validated metrics)

Assumptions
- Administrator services: 30 funds
- Avoided exception reviews per fund/year: 2 / 4 / 6
- Time per review: 0.5 / 1.0 / 1.5 hours
- Loaded hourly cost: $50 / $70 / $90
- Avoided escalations per fund/year: 0.2 / 0.5 / 1.0
- Time per escalation: 2 / 3 / 4 hours

Labor savings
- Low:  (30 x 2 x 0.5 x $50) + (30 x 0.2 x 2 x $50) = $2,100
- Base: (30 x 4 x 1.0 x $70) + (30 x 0.5 x 3 x $70) = $11,550
- High: (30 x 6 x 1.5 x $90) + (30 x 1.0 x 4 x $90) = $35,100

Illustrative range: $2,100 to $35,100 per administrator per year

Softest assumption: avoided exception reviews per fund per year. Public sources establish that
exception handling is a recurring activity but give no universal per-fund frequency, so 2 to 6 is
a deliberately conservative proxy calibrated to public commentary, not a measured count.
```

  This is an illustrative public-data model, not a field-proven result. It counts only labour saved on avoided exception reviews and escalations. It excludes timing-risk reduction plus audit benefit, which are real but not quantifiable from public data. It exists to show plausible order of magnitude, not to claim ROI. The validated figure still waits on the interview programme in the Metrics material.
- **Revenue on Canton:** B2B licensing to administrators is the core. Featured App status is a realistic post-hackathon milestone and is credibility rather than revenue. The disclosure package is deliberately not monetised: it is released to be adopted, because a primitive other teams depend on is worth more as distribution than as a licence line.
- **Why now:** in September 2026 the SEC proposed moving transfer agent register posting to a one-business-day standard tied to the settlement cycle, observing that for uncertificated securities prompt posting and turnaround are effectively the same event. DTCC launched a tokenization service on Canton on 13 September 2026. The register is moving on chain and the timing rules are tightening in the same quarter.

---

## 6. First 90 days after the hackathon

| Period | Milestone | How we'll know it's done |
| --- | --- | --- |
| Weeks 1–4 | Close the validation gap. 15 ICP interviews, synthesised, with the falsification test run and published whatever it says | Written synthesis with verbatim pain language, at least 4 hard numbers, plus a stated verdict on the wedge |
| Weeks 1–4 | Show the verifiable NAV commitment to a fund auditor for feedback. The commitment is already built and tested, an entitled party recomputes the digest from the book and matches the attestation, so the open question is auditor acceptance not engineering | A fund auditor confirms whether an on-ledger recompute maps to how they evidence NAV support today |
| Weeks 5–8 | Two administrators running a sandbox against their own fund parameters | Each has completed a subscription and a secondary transfer with their own numbers |
| Weeks 5–8 | Release `privity-disclosure` under Apache-2.0 and land the first external dependent | One project outside ours depending on the package |
| Weeks 9–12 | Deploy to DevNet or MainNet and run real settlements | 50 atomic settlements on a public network |
| Weeks 9–12 | First pilot with a live fund, any volume, plus a Featured App application | One fund settling through Privity, application submitted |

---

## 7. Risks and what you need

- **What could block adoption.** Integration with the incumbent admin system is the largest practical risk and the one we have done least about. Regulatory acceptance of a ledger record as the register is second. The SEC proposal cuts both ways: it creates urgency but it also raises the recordkeeping bar. Trust in a small vendor near the share register is third. The honest mitigation is that the disclosure layer is open and independently testable rather than a promise. Fourth, the buyer population is small, so a slow sales cycle is a bigger threat than competition.
- **A rival in the same track, addressed directly.** Alluvren is building a Canton-native redemption desk for tokenized funds. Rather than assert we are different, the accurate framing is that we operate at different layers: Alluvren solves the front-end redemption decisioning layer, Privity solves the back-end bilateral settlement and disclosure layer, so they may coexist in the same fund workflow. Separately, Canton Privacy CI is building privacy regression testing for Canton, which is our own design finding turned into a product. We cite that as independent evidence the disclosure problem is real rather than pretending we noticed it alone. A fourth in-track entry, Baseline, applies the same privacy primitive to subscription credit facilities rather than fund settlement. We read that as evidence the disclosure constraint recurs across regulated Canton workflows rather than as a competing product, because the asset class, the user, the state that changes plus the failure mode removed are all different.
- **What we need from the ecosystem.** Three introductions to fund administrators for validation interviews, which is the single highest-value thing anyone can give us. A design review on whether the disclosure package should be upstreamed as an ecosystem primitive. And guidance on what a Canton participant operator considers acceptable for holding a share register in production.

---

## Checklist

- [x] Positioning fits in one sentence
- [x] First segment is specific, with named target firms and an explicit note that none has been contacted
- [x] At least two channels with a concrete first action
- [x] At least three hypotheses, each with a metric and an honest status
- [x] It's clear who pays and what for, with pricing labelled as hypothesis
