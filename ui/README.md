# Privity web

Two pages, both dependency-free and buildless.

| File | Serves as | Audience |
| --- | --- | --- |
| `landing.html` | the root of the public site | a fund operations lead or a judge: problem, how it works, proof, limits, ask |
| `index.html` | `/demo/` on the public site | an engineer: the verified ledger run rendered from `replay.json` |

Published at https://zkasuran.github.io/privity-demo/ from a separate public repo holding only
these static files, so the demo has a URL while the source repo stays private until submission.


One self-contained page. No build step, no framework, no dependencies, so there is nothing
to install and no supply chain to defend.

Two modes:

- **Replay** (default) loads `replay.json`, a recording of a verified run against a real
  Canton participant. It exists so a reader with no Docker still sees genuine ledger data.
  It is labelled as a replay on the page and is never presented as live.
- **Live** confirms a participant is reachable on this machine and reports its Ledger API
  version. It deliberately does not re-run the trade, because a page that implied a
  settlement happened when none did would be worse than no live mode at all.

Regenerate the recording after any model change:

```bash
canton-devkit localnet up privity
eval "$(canton-devkit localnet env privity)"
export PRIVITY_PACKAGE_ID=$(canton-devkit localnet dar list --instance privity | awk '/ privity /{print $1}')
node api/ledger.mjs capture     # writes ui/replay.json

cd ui && python3 -m http.server 8899   # then open http://localhost:8899
```

`replay.json` records, for every step, the real `updateId`, the contracts created and the
active contract set as each of the four parties. The visibility table on the page is
rendered from those queries rather than from a hand-drawn permissions diagram.

Expected visibility is asserted per role rather than globally. The administrator is a
stakeholder on the register by design, because it cannot strike NAV otherwise. The auditor
is entitled to the mandate and the attestation rather than to individual positions. The
buyer is the party that must never see the seller's retained units and that is the claim
the page and the test suite both check.
