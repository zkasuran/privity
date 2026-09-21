# Synchronizer topology and the limits of the atomicity claim

This document exists because "both legs settle in one transaction" is the central claim of
this project and that claim has a precondition most descriptions of Canton leave out. An
institutional reviewer asks about it early, so it is answered here rather than discovered
live.

## The constraint, in Canton's own words

> "A Daml transaction can only consume contracts assigned to the same synchronizer. To settle
> the DvP atomically, cash to Bob, securities to Alice, in one indivisible step, both
> contracts must first be reassigned to a common synchronizer."
>
> Canton Network docs, *Cross-Synchronizer DvP Example*

Every active contract on Canton is assigned to exactly one synchronizer at a time. A
transaction is sequenced and mediated by one synchronizer, so every contract it consumes has
to be assigned there. Atomicity is therefore **per synchronizer**, not global.

That matters for a fund, because the realistic production topology is not one network. The
cash leg is a stablecoin or a deposit token whose issuer is a bank, which may run or connect
to a payments synchronizer. The register sits with an administrator. Canton's own example
observes that "a payments network and a securities settlement system are unlikely to share a
single synchronizer".

## What this project currently demonstrates

Verified rather than assumed. On the LocalNet used for the recorded run:

```
GET /v2/state/connected-synchronizers   (both participants)
  synchronizerAlias: global
  synchronizerId:    global-domain::12209ba9af8783f12bc74fc335f7091ec2405a94566716a88d...
```

and a party-scoped active contract query returns **exactly one** distinct `synchronizerId`
across every contract in the run, that same `global-domain`.

So the eight-event atomic settlement is real and the claim is honest, but it is demonstrated
in the **single synchronizer** case. Both participants connect to one synchronizer, all
contracts are assigned to it and the transaction commits or fails whole. That is the correct
thing to have proven first and it is exactly the topology the Global Synchronizer provides.

**What has not been demonstrated:** settlement where the cash and the register start on
different synchronizers.

## How the cross-synchronizer case works, plus why the design survives

Canton solves this with the reassignment protocol. The shape of the solution matters for
our risk story. Reassignment is a two-phase operation: unassignment on the source
synchronizer, then assignment on the target. The documented DvP flow is:

1. agree terms
2. ensure all validators connect to a common settlement synchronizer, often the Global Synchronizer
3. reassign the cash to it
4. reassign the securities to it
5. **settle atomically in one Daml transaction**
6. optionally reassign both back to their home synchronizers

The load-bearing sentence, again quoting the docs on atomicity boundaries:

> "The settlement step (5) **is atomic**. The Daml transaction either commits in full or not
> at all. There is no state where Alice has paid cash but not received securities, or vice
> versa... The reassignment consists of two separate transactions and has the possibility of a
> contract being temporarily unusable, but they do not carry settlement risk, no value changes
> hands until the atomic step executes."

Three consequences worth being precise about.

**The Daml model does not change.** Reassignment is a ledger and topology operation, not
something expressed in a template or a choice. `DvpProposal.SettleDvP` is step 5 of that flow.
Nothing in `Privity.Settlement` needs rewriting to work in a multi-synchronizer deployment,
which is the useful result: the application is topology-agnostic and the topology is an
operational concern.

**Principal risk is not reintroduced.** This is the part that could have sunk the thesis. If
reassignment moved value, the multi-synchronizer case would smuggle back the exact settlement
window this project exists to remove. It does not. A contract mid-reassignment is temporarily unusable, which is a liveness problem rather than a solvency one. Ownership does not change
until step 5.

**A new failure mode appears: liveness.** If an assignment fails, for example on a
topology change, the contract stays pending until resolved. So a production deployment needs
monitoring and a resolution path for stuck assignments. That is an operational requirement this project has not built. It belongs on the roadmap rather than in the claim.

## How the claim should be stated

Not "Privity settles atomically across any Canton deployment". Instead:

> Privity settles both legs in a single Daml transaction on a common synchronizer. Where the
> cash and the register are assigned to different synchronizers, Canton's reassignment
> protocol moves both to a common one first. That preparation carries no settlement risk
> because no value changes hands until the atomic step. Demonstrated on a single synchronizer
> topology, which is what the Global Synchronizer provides.

## The mechanism is available on the participant we already run

Not taken on faith from the docs. The JSON Ledger API on our own participant exposes the
reassignment protocol directly:

```
POST /v2/commands/submit-and-wait-for-reassignment
POST /v2/commands/async/submit-reassignment
```

with `ReassignmentCommands` carrying either an `UnassignCommand` or an `AssignCommand`, returning a `JsReassignment` whose required fields include `synchronizerId` and the
`JsUnassignedEvent` / `JsAssignmentEvent` pair. The request schema is described by the
participant itself as "This reassignment is executed as a single atomic update", which is
consistent with the two-phase account: each phase is atomic, the pair is not one transaction.

So moving to a multi-synchronizer deployment is a topology and operations exercise against an
API that already exists, not a protocol gap and not a change to the Daml model.

## Reproducing the checks in this document

```bash
eval "$(canton-devkit localnet env privity)"

# how many synchronizers is the participant connected to?
curl -s -H "Authorization: Bearer $CANTON_APP_PROVIDER_JWT" \
  http://localhost:32787/v2/state/connected-synchronizers

# which synchronizers hold the contracts a party can see?
#   party-scoped, because a wildcard read returns 403
curl -s -H "Authorization: Bearer $CANTON_APP_PROVIDER_JWT" -H 'content-type: application/json' \
  -d '{"filter":{"filtersByParty":{"<party>":{"cumulative":[]}}},"verbose":true,"activeAtOffset":<offset>}' \
  http://localhost:32787/v2/state/active-contracts | grep -o '"synchronizerId":"[^"]*"' | sort -u
```

Both returned exactly one synchronizer, `global-domain::1220...`.

## What would make this stronger

In rough order of value against effort:

1. **A second synchronizer, then reassign and settle.** This is the one that converts a
   documented argument into a demonstrated one. Checked and currently blocked: Splice LocalNet
   as shipped by `canton-devkit` runs a single synchronizer (`global`), while `localnet up` has no
   flag to add another. Doing it means hand-rolling a Canton configuration with a second
   sequencer and mediator outside the devkit, connecting both participants, then driving
   unassign and assign over the API above. That is real work with real failure modes, so it is
   recorded here as the next architectural step rather than attempted in the last two weeks
   before a deadline.
2. **A liveness test** for a failed or delayed assignment, showing the contract is pending
   rather than lost, which is the honest failure mode to document.
3. **Naming the Global Synchronizer as the settlement synchronizer** in the pitch, since that is
   the concrete answer to "where would this actually run".


## Sources

- Cross-Synchronizer DvP Example: https://docs.canton.network/overview/reference/cross-sync-dvp-example
- Reassignment Protocol: https://docs.canton.network/overview/reference/reassignment-protocol
- Multi-Synchronizer Architecture: https://docs.canton.network/overview/learn/multi-synchronizer
- Architecture Overview: https://docs.canton.network/overview/learn/architecture

Canton documentation is CC-BY-4.0, so the quotations above are used with attribution.
