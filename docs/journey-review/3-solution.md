# 3. Solution — strict technical review
Code review only: `dpm` isn't installed here, so no tests were run.

## Verdict (status, score /10, why)
**✅ Clear, 7/10.** The core claims are real and tested: atomic DvP, parcel-level privacy, a mandate both parties sign, and an on-ledger sha256 commitment for NAV. Deductions: settlement never checks who issued the cash or shares, auditor visibility isn't tied to a mandate, and the live flow is claimed to subscribe and redeem but doesn't.

## Claim-to-code map (table: claim | where implemented | test | status)
| Claim | Where | Test | Status |
|---|---|---|---|
| Both legs in one tx | `Settlement.SettleDvP` | `testDvpSettlesAtomically`, live run (8 events) | ✅ |
| Short payment settles nothing | `SettleDvP` asserts | `testDvpFailsWhenBuyerCannotPay` | ✅ |
| Buyer sees only the parcel | `Fund.EarmarkForSale`, `TransferShares` | `testBuyerCannotSeeSellersRemainingPosition` | ✅ |
| Subscription/redemption atomic | `SubscriptionSettlement`, `RedemptionSettlement` | only the success path is tested | ⚠️ |
| Live flow "subscribe … redeem" | not in `api/ledger.mjs` | — | ❌ |
| Mandate needs both signatures | `Disclosure.DisclosureMandate` | `testAuditorCannotSelfGrantMandate` | ✅ |
| Time check uses ledger time | `CheckActive`, `discloseUnder` | `testCannotBackdateMandateCheck`, `testDisclosureOutsideWindowFails` | ✅ |
| Either side can revoke | `Revoke` | only the auditor revoking is tested | ⚠️ |
| Auditor visibility comes from a mandate | `auditor : Optional Party` field, not linked to any mandate | — | ❌ |
| Ledger derives NAV and digest | `Fund.AttestNav` | live run only; the Daml tests `createCmd NavAttestation` directly | ⚠️ |
| Digest is canonical and tamper-evident | `holdingsDigestOf` | 4 digest tests + golden value | ✅ |
| Only manager or auditor can verify | `VerifyHoldings`, `VerifyNav` | investor is refused | ✅ |
| Settlement price = verified NAV | `agreedNavPerUnit` is never checked against an attestation | — | ❌ |

## Gaps (numbered)
1. **Counterfeit cash.** None of the three settle choices checks `cash.issuer == cashIssuer`. `CashHolding` is signed only by its issuer, so a buyer can self-issue "USDC" and pay with it. The `cashIssuer` fields are never read.
2. **Counterfeit units.** `SettleDvP` never checks `parcel.manager`, and redemption never checks the share's manager or symbol.
3. The auditor field is not linked to a mandate. After the mandate expires or is revoked, the auditor can still see the attestation and still verify it.
4. NAV verification and the settlement price are disconnected.
5. The administrator can skip `AttestNav` and create an attestation directly, as the tests do (`testNavAttestation` uses a 32-hex placeholder digest).
6. README, `ledger.mjs` and `reproduce.sh` comments, and the metrics asset all say the live flow subscribes and redeems. It does neither.
7. Untested: settlement failure paths, revocation by the subject, `discloseUnder` after a revoke, `recordSettlementDisclosure`. The test header names `testDvpFailsWhenSellerShort`, which does not exist. The "seller can't see buyer's change" check ends in `pure ()` with no assertion.
8. The site's "4 claims verified on a live ledger" stat conflicts with its own table, which marks one of the four as "test suite". Metrics asset §5 is stale ("15 of 15", "no UI").
9. **Under-sold:** the ledger-time fix for mandate checks (1.0.0 allowed backdating), the upgrade check that caught a real mistake, the `Fund` co-signature, and records that store a digest, not the payload.

**BitSafe fit.** BitSafe's Decentralization Manager is about spreading control across independent operators through threshold multi-sig ([Decrypt/Chainwire, 28 Jul 2026](https://decrypt.co/374525/cantons-blockchain-just-got-easier-developers-decensurings-manager-launches-public-beta)). Privity has **no** operator decentralization. The manager alone mints units, the administrator alone signs NAV, and one issuer backs all cash. The only multi-party authority is bilateral co-signing (`Fund`, the mandate). I did not have the challenge's criteria text.

## Actions (ranked; owner = "agent can do now" or "founder only", effort, expected effect)
1. Add issuer, manager and symbol asserts to all three settle choices, add two tests (self-issued cash, self-minted units), and bump to 1.3.0. Owner: founder only. Effort: about 1h. Effect: closes the one hole a Daml judge would exploit.
2. Remove "subscribe/redeem" from the live-flow wording, or add those steps. Owner: founder only. Effort: 15min / 2h. Effect: removes a claim anyone can falsify.
3. Reword the auditor claim to: "entitlement is a signed mandate; attestation visibility is a named-auditor field." Owner: founder only. Effort: 15min.
4. BitSafe: make `ShareHolding` signatory `manager, administrator` so no single party can mint units, with a test for it. Frame the Decentralization Manager register party as roadmap only. Claim decentralization only once a threshold or multi-hosted party actually runs. Owner: founder only. Effort: about 2h. Effect: a real, testable "no single minter" property.
5. Fix the "4 claims" stat and metrics §5. Owner: founder only (agents 4/5 draft). Effort: 10min.

## Drop-in text (ready-to-paste solution paragraph, accurate to the code)
> Privity settles a tokenized-fund trade in one Canton transaction. The seller signs a `DvpProposal` and the buyer exercises `SettleDvP`, so shares and cash commit together or not at all. When the payment is short, the parcel stays with the seller. The seller first splits off the exact parcel with `EarmarkForSale`. The buyer can read that parcel and nothing else, and a test asserts it cannot see the seller's remaining units before or after settlement. Supervision is a `DisclosureMandate` that both firm and auditor sign. It is bounded by ledger time and revocable with a stated reason, and disclosures are recorded as digests, not data. The administrator strikes NAV on ledger with a sha256 commitment over the sorted book, which a named auditor can recompute and investors cannot. Proven by 19 Daml Script tests and a recorded single-synchronizer LocalNet run.

## Journal update (3-6 true sentences)
A strict code review confirmed that atomic DvP, parcel-level privacy, the two-signature mandate and the on-ledger NAV commitment are implemented and tested. Settlement never checks the cash issuer or the share manager, so self-issued "USDC" would be accepted, and the fix is a few asserts plus two tests. The auditor's view of the NAV attestation is a named field, not bound to a mandate. The live replay does not run subscription or redemption, despite what several docs say. For BitSafe, Privity has bilateral co-signing today but no multi-operator decentralization.

## Overclaim risks
The riskiest phrases: "units and cash can never separate" (the cash can be counterfeit), "auditor visibility comes from a mandate", "subscribe … redeem" in the live flow, "4 claims on a live ledger", and any "decentralized" wording for BitSafe.
