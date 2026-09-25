# Privity

**Settlement infrastructure for tokenized funds on Canton.** Both legs of a fund trade commit
in one transaction and each counterparty is shown only the parcel it is buying.

HackCanton Season 3 entry, Investment Infrastructure track.

---

## The problem

A tokenized fund has two legs that must not separate. Units move one way, cash moves the
other. Today they are two events in two systems: an investor wires cash, somebody watches a
bank feed and units get recorded in the register afterwards. The gap between those events is
carried by whoever is exposed when it breaks and closing it is a manual reconciliation task
every month end.

You can make both legs atomic on any public ledger, but only by publishing every investor's
position to every other investor, which a regulated fund cannot accept. You can keep it
private off-ledger, but only by keeping the two events separate, which is the problem.

Canton is the one place both properties hold at once, because a single transaction can commit
across parties while each participant validates only the views its own parties are
stakeholders on.

One precondition, stated up front rather than buried. A Daml transaction can only consume
contracts assigned to the same synchronizer, so the atomicity here is demonstrated on a single
synchronizer topology, which is what the Global Synchronizer provides. Where cash and register
live on different synchronizers, Canton's reassignment protocol moves both to a common one
first and that preparation carries no settlement risk because no value changes hands until
the atomic step. The full analysis, including what is verified and what is not, is in
[docs/SYNCHRONIZER-TOPOLOGY.md](docs/SYNCHRONIZER-TOPOLOGY.md).

Two independent signals that this is live now rather than speculative. DTCC launched a
tokenization service on Canton on 13 September 2026. And in September 2026 the SEC proposed
moving transfer agent register posting to a one-business-day standard tied to the settlement
cycle, observing that "for uncertificated securities, prompt posting and turnaround are
effectively the same event". Privity makes them literally one event.

## What it does

Three layers, deliberately split into separate packages.

| Package | Contents |
| --- | --- |
| `privity-disclosure` | Need-to-know disclosure primitives. No fund logic, no settlement logic, so any Canton application can depend on it |
| `privity` | Fund, share register, cash holdings, NAV attestation and the atomic settlement choices |
| `privity-tests` | Daml Script suite. Separate so the production DARs carry no test tooling |

### The disclosure layer

Canton gives you sub-transaction privacy as a mechanism. What applications rebuild by hand is
the policy on top, where they usually get one of two things wrong: they widen disclosure
permanently by adding an auditor as an observer on everything or they grant access out of band
so nobody can later prove what was shown and under what authority.

`DisclosureMandate` makes the entitlement a contract. **Both the subject and the observer are
signatories**, on purpose: if only the observer signed, any party could assert supervision over
anyone. If only the subject signed, a firm could manufacture evidence of having been audited
by a regulator that never agreed. Mandates are time-bounded and revocable by either side with a stated
reason. Disclosures recorded against them carry a digest of what was shown rather than the
content, so the audit log does not become a second copy of the private data it describes.

### Atomic delivery versus payment

A share transfer needs the seller's authority. A cash transfer needs the buyer's. Settlement is
atomic only if both happen in one committed transaction, because any ordering of two
transactions leaves a window where one leg has moved and the other has not. That window is
principal risk. Removing it is the entire point of delivery versus payment.

`DvpProposal` is signed by the seller and exercised by the buyer, so inside the choice body the
transaction carries both authorities at once. Subscription and redemption work the same way:
cash reaches the fund in the same transaction the units are created and redeemed units are
cancelled in the same transaction the investor is paid.

### Verifiable NAV

A fund has to publish a number everyone relies on while the holdings behind it stay
confidential. `Fund.AttestNav` takes the book, derives NAV per unit **and** a canonical
sha256 commitment over the holdings, then creates the attestation. `VerifyHoldings` and
`VerifyNav` let an entitled party recompute both from a book it already holds.

The digest is computed **only on ledger, deliberately**. An earlier version hashed the book in
JavaScript and it did not verify, because Daml renders `Decimal` with trailing zeros trimmed
(`5000.0`, not `5000.0000000000`). Two canonicalisations is one too many: the first time they
drift by a separator the commitment silently stops verifying. One implementation cannot
disagree with itself.

Canonical means order-independent and content-sensitive: lines are sorted before hashing, so
the order a book happens to be listed in cannot change the result and a single altered price
changes it. Entitlement is enforced in the choice, so an investor holding the same book cannot
run the check.

### Calibrated disclosure and why the design changed

The first implementation had the buyer verify the trade by reading the seller's share holding.
**The ledger rejected it**, because the buyer is not a stakeholder on that contract. Canton
enforced the confidentiality property against our own code.

The tempting repair is to add the buyer as an observer on the seller's holding. That would have
disclosed the seller's entire position and quietly destroyed the product. Both versions
compile. Both settle correctly. Only a test written to falsify the claim distinguishes them.

So the unit of disclosure is a parcel, not a holding. `EarmarkForSale` splits off exactly the
quantity being sold and discloses only that parcel to the named buyer. The buyer can verify
what it is paying for and learns nothing about the rest of the book and `TransferShares`
clears the earmark so the new holding is not still readable by its counterparty.

The lesson generalises: **this is calibrated disclosure, not maximum secrecy.** Hide everything
and the trade cannot be verified. Disclose the holding and the product is pointless. The
engineering is finding the floor between them.

## Tests

`dpm test` from `tests/`. 18 scripts, all passing. The two that matter are
written to **fail if the product claim is false**, which is the only kind that counts as
evidence rather than demonstration.

| Test | What it would break |
| --- | --- |
| `testBuyerCannotSeeSellersRemainingPosition` | Buyer can read the parcel it bought, **cannot** read the units the seller kept, checked before and after settlement |
| `testDvpFailsWhenBuyerCannotPay` | Payment short, whole transaction rejected, parcel still the seller's and undelivered. No partial settlement |
| `testDvpSettlesAtomically` | Both legs commit, originals archived, each side keeps exact change |
| `testCannotSettleParcelEarmarkedForAnother` | A parcel disclosed to one buyer cannot be settled by another |
| `testParcelSizeMustMatchProposal` | A seller cannot earmark small then claim to sell large |
| `testCannotPayWithAnothersCash` | Cannot pay with cash you do not own |
| `testCannotEarmarkMoreThanHeld` | Oversized trade dies before a proposal exists |
| `testSubscriptionSettlesAtomically`, `testRedemptionSettlesAtomically` | Primary issuance and redemption are atomic too |
| `testMandateLifecycle` | Window checks, revocation needs a reason, outsiders cannot revoke |
| `testAuditorCannotSelfGrantMandate` | Two signatures really are required |
| `testInvertedWindowRejected` | Malformed window refused at creation |
| `testNavAttestation` | Administrator signs, manager and named auditor see it, non-positive NAV refused |
| `testNavDigestIsVerifiable` | An entitled auditor recomputes the commitment from the book and it matches. One altered price breaks it. Line order does not. An investor cannot verify at all |
| `testDigestIsOrderIndependentAndSensitive` | The digest is canonical: order-independent, content-sensitive |
| `testCannotBackdateMandateCheck` | Ledger time is past expiry while the caller claims a date inside the window. It returns false |
| `testDisclosureOutsideWindowFails` | Disclosure inside a mandate window records, outside is refused |

## Reproduce it

Prerequisites: Docker with about 8 GB available to it and roughly 20 GB of disk. No Canton
node, no cloud account, no credentials.

```bash
# 1. Toolchain
curl -fsSL https://raw.githubusercontent.com/bitdynamics-ab/canton-devkit/main/install.sh | sh
curl -sSL https://get.digitalasset.com/install/install.sh | sh   # needs JDK 17+

# 2. Preflight, changes nothing
canton-devkit localnet doctor

# 3. A real Canton network, locally
canton-devkit localnet up privity

# 4. Build all three packages in dependency order
dpm build --all

# 5. Tests
cd tests && dpm test && cd ..

# 6. Put the packages on the participant
canton-devkit localnet dar upload disclosure/.daml/dist/privity-disclosure-1.0.0.dar --instance privity
canton-devkit localnet dar upload app/.daml/dist/privity-1.0.0.dar --instance privity
canton-devkit localnet dar list --instance privity
```

Measured on this machine: LocalNet from nothing to healthy in about 2 minutes on warm images,
Splice 0.8.1. Both packages vetted.

One gotcha worth knowing. Canton treats package name plus version as an identity, so
re-uploading changed content under the same version fails with
`KNOWN_PACKAGE_VERSION: Tried to vet two packages with the same name and version`. Bump the
version or rebuild the instance with `localnet remove` then `localnet up`.

## What is not built yet

Stated here rather than left for a reader to discover.

- **No UI.** Everything is exercised from Daml Script. A demo interface is in progress.
- **No app backend.** No JSON Ledger API client yet.
- **Tests run against the IDE ledger.** They prove the model. They do not yet prove the same
  behaviour over the real Ledger API with allocated parties.
- **Nothing deployed beyond LocalNet.** No DevNet, no MainNet.
- **Zero practitioner interviews.** Problem evidence is documentary and regulator-sourced. That
  moves problem validation, not market validation and the distinction is kept explicit.

## Package versions and upgrades

`privity-disclosure` is at 1.1.0 and `privity` at 1.2.0 and the version numbers are not
cosmetic. Canton treats package name plus version as an identity and **enforces upgrade
compatibility**, so a changed model needs a bump and the bump has to be a valid upgrade.

That caught a real mistake. Moving the mandate validity check from a caller-supplied timestamp
to ledger time meant deleting the `at` field from choice `CheckActive` and the participant
refused the upload: `NOT_VALID_UPGRADE_PACKAGE: The upgraded input type of choice CheckActive
on template DisclosureMandate is missing some of its original fields`. The field is therefore
retained and explicitly ignored. A vestigial argument is the price of a register that can be
migrated rather than orphaned, which matters more to an institution than a tidy signature.

## Licence

Source-available, no derivatives (`LicenseRef-zkasuran-SAND-1.0`). See `LICENSE`. You may run
it for any purpose, read it, decompile it, benchmark it and publish what you find. You may not
redistribute it or ship derivative works, because it is a competition entry.

`privity-disclosure` is intended for relicensing under Apache-2.0 once the competition
concludes, so it can be adopted as an ecosystem primitive. The reason for waiting is stated in
`LICENSE` section 4. Third-party components and their own terms are in `NOTICE`.

## AI disclosure

AI assistance (Claude, Anthropic) was used in developing this project. The design decisions,
the review and the verification are the author's. Verified before publishing: `dpm build --all`
succeeds for all three packages, `dpm test` passes all 19 tests and both production DARs
upload and vet on a live Canton LocalNet participant.
