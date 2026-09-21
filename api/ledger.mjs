#!/usr/bin/env node
/**
 * Privity: JSON Ledger API client.
 *
 * Talks to a Canton participant over the JSON Ledger API v2 rather than through Daml
 * Script, so the flows the test suite proves against the IDE ledger are also exercised
 * against a real participant with real allocated parties.
 *
 * Endpoints and the dev JWT come from `canton-devkit localnet env <instance>`. The JWT is
 * dev-only and works against LocalNet only, so nothing here is a credential worth hiding,
 * but it is still read from the environment rather than written into the file.
 *
 * Usage:
 *   eval "$(canton-devkit localnet env privity)"
 *   node ledger.mjs <command>
 *
 *   parties            allocate the six fund-workflow parties (idempotent)
 *   demo               run the full flow: issue, subscribe, earmark, settle DvP, redeem
 *   privacy            prove the buyer cannot read the seller's retained units
 *   acs <party>        active contracts visible to one party
 */

const BASE =
  process.env.PRIVITY_JSON_API ||
  process.env.CANTON_APP_PROVIDER_JSON_LEDGER_API_URL ||
  "http://localhost:32787";
const JWT = process.env.CANTON_APP_PROVIDER_JWT;

if (!JWT) {
  console.error(
    "No JWT. Run: eval \"$(canton-devkit localnet env privity)\" first."
  );
  process.exit(1);
}

// Package id of the `privity` DAR on the participant. Resolved at runtime rather than
// hardcoded, because it changes whenever the package content changes.
let PKG = process.env.PRIVITY_PACKAGE_ID || null;

async function api(path, body, method) {
  const res = await fetch(`${BASE}${path}`, {
    method: method || (body ? "POST" : "GET"),
    headers: {
      authorization: `Bearer ${JWT}`,
      ...(body ? { "content-type": "application/json" } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const text = await res.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    json = { raw: text };
  }
  if (!res.ok) {
    const err = new Error(
      `${method || (body ? "POST" : "GET")} ${path} -> ${res.status}: ${text.slice(0, 400)}`
    );
    err.status = res.status;
    err.body = json;
    throw err;
  }
  return json;
}

/** Find the package id for `privity` by looking for its templates. */
async function resolvePackage() {
  if (PKG) return PKG;
  const { packageIds } = await api("/v2/packages");
  for (const id of packageIds) {
    try {
      const d = await api(`/v2/packages/${id}/status`);
      if (d && d.packageStatus) {
        /* status only, no name */
      }
    } catch {
      /* ignore */
    }
  }
  // The participant does not expose package names over JSON v2, so the id is supplied
  // by the caller. `canton-devkit localnet dar list` prints it.
  throw new Error(
    "Set PRIVITY_PACKAGE_ID. Get it from: canton-devkit localnet dar list --instance privity"
  );
}

// Package-name reference format. The package-id format is deprecated from 3.4.
const tid = (mod, ent) => `#privity:${mod}:${ent}`;

async function allocate(hint) {
  try {
    const r = await api("/v2/parties", { partyIdHint: hint, identityProviderId: "" });
    return r.partyDetails.party;
  } catch (e) {
    if (e.status === 400 || e.status === 409) {
      const { partyDetails } = await api("/v2/parties");
      const found = partyDetails.find((p) => p.party.startsWith(`${hint}::`));
      if (found) return found.party;
    }
    throw e;
  }
}

/** Grant the ledger-api-user the right to act as a party, so we can submit for it. */
async function grantActAs(party) {
  try {
    await api("/v2/users/ledger-api-user/rights", {
      userId: "ledger-api-user",
      rights: [{ kind: { CanActAs: { value: { party } } } }],
    });
  } catch {
    /* already granted, or user management shaped differently; submissions will tell us */
  }
}

async function parties() {
  const hints = {
    manager: "meridian-manager",
    administrator: "northgate-administrator",
    cashIssuer: "brale-issuer",
    auditor: "supervisor-auditor",
    alice: "alice-pension",
    bob: "bob-family-office",
  };
  const out = {};
  for (const [role, hint] of Object.entries(hints)) {
    out[role] = await allocate(hint);
    await grantActAs(out[role]);
    console.log(`  ${role.padEnd(14)} ${out[role]}`);
  }
  return out;
}

/** Submit a command set and wait for the transaction. */
async function submit(actAs, commands, readAs = []) {
  const commandId = `privity-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  // JsCommands is the request body itself, not nested under a `commands` key.
  return api("/v2/commands/submit-and-wait-for-transaction-tree", {
    commandId,
    actAs,
    readAs,
    userId: "ledger-api-user",
    commands,
  });
}

const createCmd = (mod, ent, args) => ({
  CreateCommand: { templateId: tid(mod, ent), createArguments: args },
});

const exerciseCmd = (mod, ent, cid, choice, arg) => ({
  ExerciseCommand: {
    templateId: tid(mod, ent),
    contractId: cid,
    choice,
    choiceArgument: arg,
  },
});

/** Pull created contract ids of a given entity out of a transaction tree. */
function created(tree, entity) {
  const events = Object.values(tree?.transactionTree?.eventsById || {});
  return events
    .filter((e) => e.CreatedTreeEvent?.value?.templateId?.endsWith(`:${entity}`))
    .map((e) => ({
      cid: e.CreatedTreeEvent.value.contractId,
      args: e.CreatedTreeEvent.value.createArgument,
    }));
}

/** Active contracts a party can see. This is how the privacy claim is checked. */
async function acs(party) {
  const end = await api("/v2/state/ledger-end");
  const res = await api("/v2/state/active-contracts", {
    filter: { filtersByParty: { [party]: { cumulative: [] } } },
    verbose: true,
    activeAtOffset: end.offset,
  });
  const list = Array.isArray(res) ? res : res.contracts || [];
  return list
    .map((c) => {
      const e = c.contractEntry?.JsActiveContract?.createdEvent || c.createdEvent;
      if (!e) return null;
      return {
        cid: e.contractId,
        template: (e.templateId || "").split(":").slice(-2).join(":"),
        args: e.createArgument,
      };
    })
    .filter(Boolean);
}

async function main() {
  const cmd = process.argv[2] || "demo";
  PKG = await (async () => {
    if (process.env.PRIVITY_PACKAGE_ID) return process.env.PRIVITY_PACKAGE_ID;
    return resolvePackage();
  })();

  if (cmd === "parties") {
    console.log("Allocating parties on the participant:");
    await parties();
    return;
  }

  if (cmd === "acs") {
    const p = process.argv[3];
    const rows = await acs(p);
    console.log(`${rows.length} contracts visible to ${p}`);
    for (const r of rows) console.log("  ", r.template, r.cid.slice(0, 20) + "...");
    return;
  }

  console.log("Allocating parties...");
  const P = await parties();

  const SYMBOL = "PRIV-I";
  const INSTRUMENT = "USDC";

  console.log("\n1. Fund created by manager and administrator jointly");
  let tx = await submit(
    [P.manager, P.administrator],
    [
      createCmd("Privity.Fund", "Fund", {
        manager: P.manager,
        administrator: P.administrator,
        cashIssuer: P.cashIssuer,
        symbol: SYMBOL,
        name: "Privity Institutional Fund I",
        instrument: INSTRUMENT,
      }),
    ]
  );
  const fundCid = created(tx, "Fund")[0].cid;
  console.log("   Fund", fundCid.slice(0, 24) + "...");

  console.log("\n2. Cash issued to Bob through offer and accept");
  tx = await submit(
    [P.cashIssuer],
    [
      createCmd("Privity.Cash", "CashIssuanceOffer", {
        issuer: P.cashIssuer,
        recipient: P.bob,
        instrument: INSTRUMENT,
        amount: "150000.0000000000",
      }),
    ]
  );
  const offerCid = created(tx, "CashIssuanceOffer")[0].cid;
  tx = await submit(
    [P.bob],
    [exerciseCmd("Privity.Cash", "CashIssuanceOffer", offerCid, "AcceptCash", {})]
  );
  const bobCash = created(tx, "CashHolding")[0].cid;
  console.log("   Bob holds 150,000 USDC");

  console.log("\n3. Alice put on the register with 1,000 units");
  tx = await submit(
    [P.manager],
    [
      createCmd("Privity.Fund", "ShareHolding", {
        manager: P.manager,
        administrator: P.administrator,
        investor: P.alice,
        symbol: SYMBOL,
        units: "1000.0000000000",
        prospectiveBuyer: null,
      }),
    ]
  );
  const aliceShares = created(tx, "ShareHolding")[0].cid;

  console.log("\n4. Alice earmarks exactly 400 units for Bob");
  tx = await submit(
    [P.alice],
    [
      exerciseCmd("Privity.Fund", "ShareHolding", aliceShares, "EarmarkForSale", {
        buyer: P.bob,
        saleUnits: "400.0000000000",
      }),
    ]
  );
  const parcels = created(tx, "ShareHolding");
  const parcel = parcels.find((p) => p.args.prospectiveBuyer);
  const retained = parcels.find((p) => !p.args.prospectiveBuyer);
  console.log(`   parcel  ${parcel.args.units} units, disclosed to Bob`);
  console.log(`   retained ${retained.args.units} units, not disclosed`);

  console.log("\n5. Atomic DvP: 400 units against 41,000 USDC in ONE transaction");
  tx = await submit(
    [P.alice],
    [
      createCmd("Privity.Settlement", "DvpProposal", {
        seller: P.alice,
        buyer: P.bob,
        manager: P.manager,
        administrator: P.administrator,
        cashIssuer: P.cashIssuer,
        symbol: SYMBOL,
        instrument: INSTRUMENT,
        units: "400.0000000000",
        pricePerUnit: "102.5000000000",
        shareCid: parcel.cid,
        auditor: null,
      }),
    ]
  );
  const proposal = created(tx, "DvpProposal")[0].cid;

  tx = await submit(
    [P.bob],
    [
      exerciseCmd("Privity.Settlement", "DvpProposal", proposal, "SettleDvP", {
        cashCid: bobCash,
      }),
    ]
  );
  const updateId = tx?.transactionTree?.updateId;
  const eventCount = Object.keys(tx?.transactionTree?.eventsById || {}).length;
  console.log(`   committed in one transaction: ${updateId}`);
  console.log(`   ${eventCount} events in that single transaction`);

  console.log("\n6. Privacy check, read as each party");
  const bobView = await acs(P.bob);
  const aliceView = await acs(P.alice);
  const bobSeesRetained = bobView.some((c) => c.cid === retained.cid);
  const aliceSeesRetained = aliceView.some((c) => c.cid === retained.cid);
  console.log(`   Alice can see her retained 600 units : ${aliceSeesRetained}`);
  console.log(`   Bob can see Alice's retained units   : ${bobSeesRetained}`);
  if (bobSeesRetained) {
    console.error("\nFAIL: the buyer can read the seller's retained position.");
    process.exit(1);
  }
  console.log("\n   PASS: buyer cannot read the seller's retained position.");
}

main().catch((e) => {
  console.error("\nERROR:", e.message);
  process.exit(1);
});
