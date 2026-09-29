#!/usr/bin/env bash
# Privity: one-command reproduction of the settlement + privacy flow on a live Canton
# participant. Stands up the environment, ensures the current DARs are vetted, runs every
# flow through the JSON Ledger API, then prints a receipt a reviewer can trust without
# reading the source. Exit 0 only if every flow committed, the digest verified, and the
# privacy check passed.
#
#   ./reproduce.sh
#
# No arguments. Needs Docker, the canton-devkit LocalNet instance "privity", and node.
set -euo pipefail
cd "$(dirname "$0")"

INSTANCE=privity
say() { printf '%s\n' "$*"; }
fail() { printf 'reproduce: %s\n' "$*" >&2; exit "${2:-1}"; }

# 1. Toolchain + LocalNet env (JWT, endpoints). env.sh sits one level up, at the lane root.
[ -f ../env.sh ] && . ../env.sh
[ -f ./env.sh ] && . ./env.sh
command -v canton-devkit >/dev/null || fail "canton-devkit not on PATH (source env.sh)" 1
command -v node >/dev/null || fail "node not on PATH" 1
eval "$(canton-devkit localnet env "$INSTANCE" 2>/dev/null)" || fail "LocalNet '$INSTANCE' not running: canton-devkit localnet up $INSTANCE" 1
JWT="${CANTON_APP_PROVIDER_JWT:-}"
[ -n "$JWT" ] || fail "no app-provider JWT from localnet env" 1

# 2. Resolve the current DAR + its package id (participant-independent).
DAR="$(ls -1 app/.daml/dist/privity-*.dar 2>/dev/null | sort -V | tail -1 || true)"
if [ -z "$DAR" ]; then
  say "building DARs (dpm build --all)..."
  dpm build --all >/dev/null 2>&1 || fail "dpm build failed" 1
  DAR="$(ls -1 app/.daml/dist/privity-*.dar | sort -V | tail -1)"
fi
PKG="$(unzip -Z1 "$DAR" 2>/dev/null | sed -nE 's#^privity-[0-9.]+-([0-9a-f]{64})/.*#\1#p' | head -1)"
[ -n "$PKG" ] || fail "could not read package id from $DAR" 1
export PRIVITY_PACKAGE_ID="$PKG"

# 3. Build the candidate list of JSON Ledger APIs. Prefer the routed app-provider URL; then
#    every reachable participant port EXCEPT the sv participant. Ports shuffle across a
#    LocalNet restart and app-provider/app-user share the "participant::" namespace, so the
#    only reliable test of app-provider is that its parties can actually submit. That is
#    step 4: the first candidate whose flow commits is app-provider.
api_ok() { curl -fsS -m5 -o /dev/null -H "authorization: Bearer $JWT" "$1/v2/version" 2>/dev/null; }
pid_of() { curl -fsS -m5 -H "authorization: Bearer $JWT" "$1/v2/parties/participant-id" 2>/dev/null; }
CANDS=("${CANTON_APP_PROVIDER_JSON_LEDGER_API_URL:-}")
for hp in $(docker port "${INSTANCE}-canton" 2>/dev/null | sed -nE 's#.*-> 127.0.0.1:([0-9]+)#\1#p' | sort -u); do
  url="http://localhost:$hp"
  api_ok "$url" || continue
  case "$(pid_of "$url")" in *'"participantId":"sv::'*) continue;; esac
  CANDS+=("$url")
done

# 4. Try each candidate: vet the DAR on it, run the full flow (fund, cash issue, earmark,
#    atomic DvP, mandate, NAV attest, digest verify, privacy check), take the first that commits. `capture`
#    writes ui/replay.json as the machine-readable receipt. Delete it first so a stale file can
#    never pass for this run.
vet() {
  curl -fsS -m8 -H "authorization: Bearer $JWT" "$1/v2/packages" | grep -q "$PKG" && return 0
  curl -fsS -m60 -X POST -H "authorization: Bearer $JWT" -H "content-type: application/octet-stream" \
    --data-binary @"$DAR" "$1/v2/packages" >/dev/null 2>&1
  curl -fsS -m8 -H "authorization: Bearer $JWT" "$1/v2/packages" | grep -q "$PKG"
}
JSON_API=""
for cand in "${CANDS[@]}"; do
  [ -n "$cand" ] || continue
  api_ok "$cand" || continue
  vet "$cand" || continue
  export PRIVITY_JSON_API="$cand"
  rm -f ui/replay.json
  if node api/ledger.mjs capture >/tmp/privity-repro.log 2>&1 && [ -f ui/replay.json ]; then
    JSON_API="$cand"; break
  fi
done
[ -n "$JSON_API" ] || { tail -3 /tmp/privity-repro.log >&2 2>/dev/null; fail "no app-provider participant could commit the flow (LocalNet degraded, try: canton-devkit localnet restart $INSTANCE)" 2; }
LEDGER_VER="$(curl -fsS -m5 -H "authorization: Bearer $JWT" "$JSON_API/v2/version" | sed -nE 's/.*"version":"([^"]+)".*/\1/p')"
sed 's/^/  /' /tmp/privity-repro.log
say ""
say "participant   : $JSON_API  (ledger $LEDGER_VER, package $(basename "$DAR"))"

# 5. Receipt contract, read back from the captured run, never re-derived.
say ""
node - <<'NODE'
const fs = require("node:fs");
const t = JSON.parse(fs.readFileSync("ui/replay.json", "utf8"));
const steps = t.steps || [];
const dvp = steps.find((s) => s.eventCount);
const ver = steps.find((s) => s.digestVerified !== undefined);
const pv = t.privacyCheck || {};
const line = (k, v) => console.log("  " + k.padEnd(16) + v);
const short = (x) => (x ? String(x).slice(0, 26) + "..." : "?");
console.log("RECEIPT");
line("atomic-dvp", `OK tx=${short(dvp?.updateId)} events=${dvp?.eventCount ?? "?"}`);
line("digest-verify", `${ver?.digestVerified ? "OK" : "FAIL"} ${short(ver?.holdingsDigest)}`);
line("nav-verify", `${ver?.navVerified ? "OK" : "FAIL"}`);
line("privacy", `${pv.verdict || "?"}  buyer-cannot-read-retained=${pv.buyerCanSeeRetained === false}`);
line("artifact", `privity/ui/replay.json (${steps.length} steps)`);
const ok =
  pv.verdict === "PASS" &&
  pv.buyerCanSeeRetained === false &&
  pv.sellerCanSeeRetained === true &&
  ver?.digestVerified === true &&
  ver?.navVerified === true &&
  dvp?.eventCount > 0;
console.log(ok ? "\nREPRODUCTION OK" : "\nREPRODUCTION FAILED");
process.exit(ok ? 0 : 3);
NODE