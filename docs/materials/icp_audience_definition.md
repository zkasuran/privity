# ICP: Ideal Customer Profile

## 1. Who they are

| | |
| --- | --- |
| **Segment** | Third-party fund administrators servicing private funds. Secondarily, private fund managers that self-administer |
| **Company size / stage** | Mid-tier. Roughly 20 to 60 funds under administration, book in the low hundreds of millions to about 2bn AUM. Large enough to run a dedicated transfer agency function, small enough to buy rather than build. The top five global administrators are explicitly out of scope, because they build in house |
| **User** | Fund accounting lead or transfer agency lead. Around 12 years in fund operations, not in crypto. Runs a team of 4 to 6. Owns the share register and produces NAV |
| **Buyer** | Head of operations or head of fund administration. The auditor is an **influencer** rather than the buyer. The fund manager is a **secondary** buyer |
| **Geography** | United States first, because the SEC's September 2026 transfer agent proposal creates a dated compliance trigger there. Then Ireland and Luxembourg, then Cayman and Singapore |

The user and the buyer are separated deliberately. An earlier version of this document collapsed them. The distinction matters: the person who feels the pain daily is not the person who signs off a process change.

---

## 2. Their pain

- **Top pain point, in their words rather than ours:** they are the person who has to certify the register is right, while the three things that determine whether it is right sit in three systems they do not control. The bank feed says cash arrived. The subscription document says what was promised. The register is theirs. Nothing links them except their team's attention, so every break is found by a human, late.
- **How often it happens:** every subscription, every redemption, every secondary transfer, so daily at the item level. Then concentrated monthly at period-end close, per fund.
- **What it costs them:** four things, in the order they would rank them. Timing risk in the gap between cash and register, hours to days wide, unpriced but understood. Reconciliation labour, a multi-day manual exercise per fund per period. NAV error risk, which is a regulatory event and not merely embarrassing: notifications of NAV calculation errors to Luxembourg's CSSF rose from 238 in 2019 to 462 in 2022 while investment compliance breaches fell. CSSF Circular 02/77 obliges compensating investors who suffered a loss. Audit evidence, assembled retrospectively because nothing in the flow was designed to record who saw what under which authority.
- **How they solve it today:** a document and wire workflow rather than a settlement workflow. Signed subscription agreement by PDF over email, investor wires cash, the administrator watches the bank feed, confirms receipt, then records units in the admin system. Investran, Allvue, Geneva and FundCount are the usual systems. Period end reconciles bank statements, custodian statements and the register by hand. Delivery versus payment is not really happening: it is free delivery with a human gate. Secondary transfers are worse, a signed transfer form plus a manual register update.

---

## 3. What they want

- **Job to be done:** "When an investor subscribes, redeems or transfers units, I want the cash movement and the register update to be one event I can point an auditor at, so I can stop reconciling two records that should never have been separate."
- **What would make them switch:** not privacy as a feature. They switch when units and cash move as a single event that removes a class of break their team currently finds by hand, plus when the evidence an auditor asks for is produced by the process rather than reconstructed afterwards.
- **What would stop them:** in this order. **Confidentiality regression**, which is an instant no: a ledger where other investors could see their funds' positions ends the conversation. Then **integration effort** against the incumbent admin system, which is where the real cost of adoption sits. Then **regulatory uncertainty** about whether a ledger record satisfies recordkeeping obligations. Then **trust in a new vendor** holding anything near the register. Price is the least of their objections, which is itself informative about the pricing model.

---

## 4. Where to find them

- **Communities, events and channels they use:** LinkedIn is the primary route because the role is title-searchable, which is unusual and useful. Beyond that, fund operations and transfer agency conference circuits, plus industry association channels. A new and better channel opened this month: the SEC comment period on the transfer agent proposal is open. The SEC asked specifically for concrete data on item volumes, exception and rejection rates plus investment company workflows. Comment letters on that docket will be named practitioners describing this exact workflow with numbers attached, in public.
- **Tools and platforms they already rely on:** Investran, Allvue, Geneva, FundCount, plus the bank portal and a great deal of Excel. Integration is with these systems, not against them.
- **Real companies that fit this profile:** Gen II Fund Services, Standish Management, Aduro Advisors, Langham Hall, Bolder Group, Trident Trust, Ocorian, Waystone, IQ-EQ, Alter Domus. Stated plainly: **these are targets we intend to approach, not firms we have spoken to.** Zero of them have been contacted.

---

## 5. Who is NOT your customer (for now)

- **Retail investors.** They feel none of this pain and cannot buy.
- **The top five global fund administrators.** They build in house and will not adopt from a hackathon. They are a partnership conversation years later, not a first customer.
- **Crypto-native funds and DAOs.** They already tolerate transparent ledgers, so the confidentiality half of the product solves nothing they feel, so the regulatory framing is irrelevant to them.
- **Public equity transfer agents.** Adjacent and larger, but the workflow is CSD-settled and governed by different rules. We would be competing with entrenched infrastructure rather than replacing a manual process.
- **Auditors, as a buyer.** They are an influencer and a beneficiary. We will not sell to them unless the interviews say the operations pain is soft, which is a documented condition for changing the wedge rather than an option we keep open for convenience.

---

## Checklist

- [x] The segment is narrow enough to name real companies or people
- [x] User and buyer are identified, then deliberately distinguished
- [x] The pain is described from their point of view
- [x] You know where to reach them
- [x] You've said who you're not targeting
