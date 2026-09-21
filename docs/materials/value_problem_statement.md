# Value

## 1. The problem in one sentence

**Fund administrators** struggle to **settle subscriptions, redemptions and secondary transfers as one controlled event** because **the cash movement and the share register update are two separate events in two separate systems**, which costs them **manual reconciliation, unpriced timing risk plus audit evidence that has to be reassembled after the fact**.

---

## 2. The value you create

| | Today | With Privity |
| --- | --- | --- |
| **What the user does** | Watches a bank feed for a wire, confirms receipt by eye, then records units in the admin system. Reconciles register, bank record and custodian record by hand at period end. Rebuilds an audit trail retrospectively once a year. | Settles both legs in one transaction. Units cannot move without payment and payment cannot move without units. The disclosure record is produced by the act of settling, not assembled afterwards. |
| **Time / cost / risk** | A gap of hours to days between the two legs, carried by whoever is exposed when it breaks. Period end is a multi-day manual exercise per fund. NAV errors carry a regulatory correction and compensation obligation. | No gap, because there is no interval in which one leg has moved and the other has not. Reconciliation of the two legs against each other stops being a task, because they are one record. |

- **Value proposition in one line:** both legs of a fund trade settle in a single Canton transaction, while each counterparty is shown only the parcel it is buying.
- **Why users would switch from what they do today:** not for privacy as a feature. They switch because a settlement that cannot half-complete removes a class of break they currently find by hand. It also means the evidence an auditor asks for is generated rather than reconstructed. The confidentiality position has to be at least as strong as today or the conversation ends, which is the constraint rather than the selling point.

---

## 3. Why it matters

**Cost of the problem.**

- **NAV errors are rising, counted by a regulator.** Notifications of NAV calculation errors to Luxembourg's CSSF went from **238 in 2019 to 462 in 2022**, while notifications of investment compliance breaches *fell* over the same period (1,497 to 1,382). The failure mode that is growing is the operational one, the production of the number, not the portfolio one. *Reported by Deloitte Luxembourg from CSSF activity reports 2017 to 2022.*
- **A NAV error is not just embarrassing, it triggers a compensation procedure.** CSSF Circular 02/77 governs the treatment of NAV calculation errors and requires that "the interests of the UCIs and/or of the investors having suffered a loss need to be protected". The same source notes an "increase in the number of normal procedures (including compensation to investors)".
- **Where settlement failure is measured, it is also penalised.** Under CSDR Article 7, "cash penalties shall be calculated on a daily basis for each business day that a transaction fails to be settled after its intended settlement date". The honest limit: CSDR governs CSD-settled securities rather than private fund subscription flows, so this establishes that regulated markets treat the gap between two legs as having a price, not that our specific user pays CSDR penalties.
- **Reconciliation delay propagates into settlement failure, with a dated example.** When a hardware fault took T2S and T2 down on 27 February 2025, ESMA recorded that "participants were also delayed in their reconciliation processes, creating settlement fails over the next settlement days".

**How many people or companies have it.** The best-grounded figure available is a regulator's own: the SEC estimates **approximately 200 registered transfer agents** currently fall within Rule 17ad-4, the exemption it proposes to rescind, which covers transfer agents processing limited partnership interests, DRIPs and redeemable open-end fund securities. The SEC qualifies it, noting the count includes firms that outsource all transfer agent activity or may not be actively providing services, so treat it as an upper bound on that specific US population rather than a market size. *Per Morgan Lewis's analysis of the proposing release, citing release page 228 fn. 414.*

Globally, adding Ireland, Luxembourg, Cayman and Singapore, **our own estimate is low thousands of firms** with one to three people in the exact role each. That figure is an estimate, not a citation. The reasoning: fund administration is consolidated into a few very large firms plus a long tail of small and mid administrators. The addressable person sits mostly in that tail because the largest firms build in house. We will firm it up from administrator registers in Ireland and Luxembourg, US adviser filings that name the administrator, plus published client counts of mid-tier firms.

Either way the shape is the same and it is what the go-to-market assumes: a small, named, regulated buyer set where each deal is worth a lot, not a self-serve market.

**Evidence.** Two regulator-grounded numbers carry this section: the CSSF NAV error series above plus the SEC's characterisation of an industry whose rules were built for "a market where securities were represented by physical certificates and transactions and related records were processed manually". Vendors across fund operations describe the same reconciliation workflow in their own marketing, which confirms the workflow is recognised but is not evidence, because it is promotion for competing products. **We have not yet completed practitioner interviews. We are not presenting desk research as though we had.** See the Metrics material for the documentary evidence we do hold, the interview programme and its falsification test.

---

## 4. Why now

**A regulator has just proposed requiring what we built.** In September 2026 the SEC proposed a comprehensive modernization of the rules governing registered transfer agents. Two provisions matter here.

First, proposed Rules 17ad-2 and 17ad-10 would move core transfer and record-posting onto a **one-business-day framework tied to the settlement cycle**, replacing today's standard of turning around at least 90% of routine items within three business days. Rule 17ad-10 applies that same standard to posting debits and credits to the master securityholder file following an issuance, purchase, transfer or redemption. And the SEC's own observation is the one we would have wanted to write ourselves:

> "for uncertificated securities, prompt posting and turnaround are effectively the same event"

That is the regulator saying the transfer and the register update should collapse into a single event once securities stop being pieces of paper. Privity makes them literally one transaction. The gap we remove is the gap the rule is closing.

Second, the proposal is deliberately technology-neutral in a way that names our infrastructure. The definition of "item" would be extended to cover "an electronic system controlled, operated, or enabled by the transfer agent", specifically so that instructions sent "by or through both existing technologies, such as blockchains and other distributed ledger-based platforms" are captured. The SEC's stated objective is to align requirements "with modern electronic securities markets, including the increasing use of distributed-ledger technology and tokenized securities".

The proposal also rescinds Rule 17ad-4, the exemption currently relied on by transfer agents processing limited partnership interests, DRIPs and redeemable open-end fund securities. Those are precisely the fund products in scope for us. Their operators are about to face accelerated processing standards for the first time. *All of the above is per Morgan Lewis's published analysis of the proposing release, September 2026. We have not read the release directly because sec.gov blocks scripted access. The citation will be upgraded once it is read in a browser.*

**The register is also moving on chain independently of regulation.** DTCC launched a tokenization service on Canton on 13 September 2026. Tokenization of real-world assets including funds and structured products is among the most active build categories on the network. Once units exist as ledger contracts, how they settle against cash stops being theoretical.

**Why this couldn't be solved well before.** It needs two properties at once that no previous ledger offered together. Atomic multi-party settlement is available on any public chain, but only alongside broadcast visibility that a regulated fund cannot accept, because positions and investor identities are competitively and legally sensitive. Confidentiality is available off-chain, but only by reintroducing the separation between cash and register that causes the problem. Canton's sub-transaction privacy is what removes the trade-off.


---

## 5. Why Canton

**What Canton makes possible here.** A single transaction can touch the buyer's cash, the seller's cash, the share register and the fund, then commit atomically, while each participant node validates only the views its own parties are stakeholders on. That is the exact shape of delivery versus payment between parties who must not see each other's books.

We did not take this on faith. Our first implementation had the buyer verify the trade by reading the seller's share holding. The ledger rejected it, because the buyer is not a stakeholder on that contract. Canton enforced the confidentiality property against our own code. The tempting repair, adding the buyer as an observer, would have disclosed the seller's entire position, quietly destroying the product.

That produced the design the project now rests on, plus a sharper statement of what we are building: **settlement for tokenized funds depends on calibrated disclosure, not maximum secrecy, because the buyer must be able to verify what it acquires without seeing the seller's whole book.** The seller earmarks the exact parcel being sold, which discloses that parcel and nothing else. The transfer then clears the disclosure. Four tests hold that line, including one that fails if a buyer can ever read the seller's retained units.

**Why a public chain or a plain database wouldn't do.** A public chain publishes every investor's position to every other investor, which is an immediate no for this user. A plain database can hold the register privately but cannot make a payment held at another institution and a register update it does not own commit as one event, which is the entire problem. What is needed is atomicity *across* organisational boundaries with visibility *within* them. That combination is Canton's specific contribution rather than a general blockchain property.

---

## Checklist

- [x] The problem fits in one sentence
- [x] It names a specific user, not "everyone"
- [x] The value is shown as a before and after
- [x] There is evidence the problem is real
- [x] "Why now" is answered
- [x] It's clear why this belongs on Canton
