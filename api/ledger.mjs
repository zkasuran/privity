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
 *   demo               run the full flow: fund, cash issue, earmark, settle DvP, mandate, NAV attest + verify
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
// Templates live in two packages, so the package name is derived from the module: the
// disclosure library owns Privity.Disclosure, the app owns everything else.
const pkgFor = (mod) => (mod === "Privity.Disclosure" ? "privity-disclosure" : "privity");
const tid = (mod, ent) => `#${pkgFor(mod)}:${mod}:${ent}`;

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

// Replay capture. Every step of a verified run is recorded so the UI can show real
// ledger data to someone who has no Docker and no participant. Nothing is synthesised:
// each entry is the actual request made and the actual response received.
const TRACE = { capturedAt: null, network: {}, steps: [], views: {} };
const step = (n, title, detail) => {
  TRACE.steps.push({ n, title, ...detail });
  return detail;
};

// The portfolio the NAV is struck from.
//
// Deliberately no digest is computed here. The ledger computes both the NAV and the
// commitment inside Fund.AttestNav, so there is exactly one canonicalisation. An earlier
// version hashed the book in JavaScript and it did not verify on ledger, because Daml's
// `show` for Decimal trims trailing zeros (5000.0, not 5000.0000000000). Two
// canonicalisations is one too many.
const HOLDINGS = [
  { instrument: "US912828YY01", quantity: "5000.0000000000",   unitPrice: "99.2500000000" },
  { instrument: "DE0001102580", quantity: "3000.0000000000",   unitPrice: "101.4000000000" },
  { instrument: "CASH-USD",     quantity: "250000.0000000000", unitPrice: "1.0000000000" },
];
async function main() {
  const cmd = process.argv[2] || "demo";
  const capturing = cmd === "capture";
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
  if (capturing) {
    const v = await api("/v2/version");
    TRACE.capturedAt = new Date().toISOString();
    TRACE.network = { ledgerApiVersion: v.version, jsonApi: BASE, packageId: PKG };
    TRACE.parties = P;
  }

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
  step(1, "Fund created jointly by manager and administrator", {
    note: "Both sign. An administrator cannot be named as the party striking NAV without having agreed.",
    updateId: tx?.transactionTree?.updateId,
    contracts: [{ template: "Fund", cid: fundCid }],
  });

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
  step(2, "Cash issued to the buyer through offer and accept", {
    note: "The issuer cannot push a holding onto an unwilling recipient.",
    updateId: tx?.transactionTree?.updateId,
    contracts: [{ template: "CashHolding", cid: bobCash, amount: "150000", instrument: INSTRUMENT }],
  });

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
  step(3, "Seller on the register with 1,000 units", {
    note: "Stakeholders are manager, administrator and investor. No other investor appears.",
    updateId: tx?.transactionTree?.updateId,
    contracts: [{ template: "ShareHolding", cid: aliceShares, units: "1000" }],
  });

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
  step(4, "Seller earmarks exactly the parcel being sold", {
    note: "This is the calibrated-disclosure step. Only the parcel becomes visible to the buyer. The retained units never do.",
    updateId: tx?.transactionTree?.updateId,
    contracts: [
      { template: "ShareHolding", cid: parcel.cid, units: parcel.args.units, disclosedTo: "buyer" },
      { template: "ShareHolding", cid: retained.cid, units: retained.args.units, disclosedTo: "seller only" },
    ],
  });

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
  step(5, "Atomic delivery versus payment, one transaction", {
    note: "The share leg needs the seller's authority and the cash leg needs the buyer's. The proposal is signed by the seller and exercised by the buyer, so one transaction carries both. It commits whole or not at all.",
    updateId,
    eventCount,
    events: Object.values(tx?.transactionTree?.eventsById || {}).map((e) => {
      const c = e.CreatedTreeEvent?.value;
      const x = e.ExercisedTreeEvent?.value;
      if (c) return { kind: "created", template: (c.templateId || "").split(":").slice(-1)[0], cid: c.contractId };
      if (x) return { kind: "exercised", template: (x.templateId || "").split(":").slice(-1)[0], choice: x.choice, cid: x.contractId };
      return { kind: "other" };
    }),
  });

  console.log("\n6. Supervision: mandate offered, accepted, then NAV attested");
  tx = await submit(
    [P.manager],
    [
      exerciseCmd("Privity.Fund", "Fund", fundCid, "OfferSupervision", {
        auditor: P.auditor,
        basis: "StatutoryAudit",
        legalReference: "Engagement 2026/PRIV-I/AUD-004",
        window: { from: "2026-01-01T00:00:00Z", until: "2027-01-01T00:00:00Z" },
      }),
    ]
  );
  const mandateOffer = created(tx, "DisclosureMandateOffer")[0].cid;
  tx = await submit(
    [P.auditor],
    [
      exerciseCmd("Privity.Disclosure", "DisclosureMandateOffer", mandateOffer, "AcceptMandate", {}),
    ]
  );
  const mandateCid = created(tx, "DisclosureMandate")[0].cid;
  console.log("   mandate accepted by auditor, time bounded and revocable");
  step(6, "Supervision mandate: offered by the fund, accepted by the auditor", {
    note: "Both sides sign. An auditor cannot self-grant visibility and a firm cannot fake having been audited. The mandate is time bounded and either side can revoke it with a stated reason.",
    updateId: tx?.transactionTree?.updateId,
    contracts: [{ template: "DisclosureMandate", cid: mandateCid, basis: "StatutoryAudit" }],
  });

  tx = await submit(
    [P.administrator],
    [
      exerciseCmd("Privity.Fund", "Fund", fundCid, "AttestNav", {
        holdings: HOLDINGS,
        unitsOutstanding: "10000.0000000000",
        asOf: "2026-09-21T17:00:00Z",
        auditor: P.auditor,
      }),
    ]
  );
  const navEvent = created(tx, "NavAttestation")[0];
  const navCid = navEvent.cid;
  const ledgerDigest = navEvent.args?.holdingsDigest;
  const ledgerNav = navEvent.args?.navPerUnit;
  console.log(`   NAV struck on ledger from the book: ${ledgerNav} per unit`);
  console.log(`   commitment computed on ledger:      ${ledgerDigest}`);
  step(7, "NAV attested by the independent administrator", {
    note: "The administrator submits the book and the ledger derives both the NAV per unit and a canonical sha256 commitment over the holdings. Nothing off ledger computes the digest, so there is only one canonicalisation and it cannot drift.",
    updateId: tx?.transactionTree?.updateId,
    contracts: [{ template: "NavAttestation", cid: navCid, navPerUnit: ledgerNav, unitsOutstanding: "10000" }],
  });

  // The auditor recomputes the commitment from a book it already holds and compares it with
  // the attestation. A true here means the attested number is tied to that exact book, which
  // is what makes the attestation checkable rather than merely signed.
  const verifyTx = await submit(
    [P.auditor],
    [
      exerciseCmd("Privity.Fund", "NavAttestation", navCid, "VerifyHoldings", {
        holdings: HOLDINGS,
        verifier: P.auditor,
      }),
    ]
  );
  const verified = Object.values(verifyTx?.transactionTree?.eventsById || {})
    .map((e) => e.ExercisedTreeEvent?.value?.exerciseResult)
    .find((r) => r !== undefined);
  console.log(`   auditor recomputed the digest inside Daml: ${verified}`);

  const navTx = await submit(
    [P.auditor],
    [
      exerciseCmd("Privity.Fund", "NavAttestation", navCid, "VerifyNav", {
        holdings: HOLDINGS,
        verifier: P.auditor,
      }),
    ]
  );
  const navOk = Object.values(navTx?.transactionTree?.eventsById || {})
    .map((e) => e.ExercisedTreeEvent?.value?.exerciseResult)
    .find((r) => r !== undefined);
  console.log(`   auditor recomputed NAV per unit inside Daml:  ${navOk}`);

  step(8, "Auditor verifies the NAV against the book, on ledger", {
    note: "The auditor recomputes the commitment and the NAV from a book it already holds. Both match, so the attested figure is provably tied to that portfolio without the portfolio being disclosed to anyone not entitled to it. An investor holding the same book cannot run this check at all, because entitlement is enforced in the choice.",
    updateId: verifyTx?.transactionTree?.updateId,
    digestVerified: verified === true,
    navVerified: navOk === true,
    holdingsDigest: ledgerDigest,
  });
  if (verified !== true || navOk !== true) {
    console.error("\nFAIL: the digest or the NAV did not verify on ledger.");
    process.exit(1);
  }

  console.log("\n7. Privacy check, read as each party");
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

  if (capturing) {
    // The active contract set accumulates across runs on a long-lived LocalNet, so the
    // captured views are scoped to contracts this run actually produced. Both the scoped
    // and total counts are recorded, so the number shown is never quietly a subset.
    const thisRun = new Set();
    for (const st of TRACE.steps) {
      for (const c of st.contracts || []) thisRun.add(c.cid);
      for (const e of st.events || []) if (e.cid) thisRun.add(e.cid);
    }
    const scope = (all) => ({
      fromThisRun: all.filter((c) => thisRun.has(c.cid)),
      totalVisible: all.length,
    });
    const adminView = await acs(P.administrator);
    const auditorView = await acs(P.auditor);
    TRACE.views = {
      seller: { party: P.alice, ...scope(aliceView) },
      buyer: { party: P.bob, ...scope(bobView) },
      administrator: { party: P.administrator, ...scope(adminView) },
      auditor: { party: P.auditor, ...scope(auditorView) },
    };
    TRACE.privacyCheck = {
      retainedParcelCid: retained.cid,
      sellerCanSeeRetained: aliceSeesRetained,
      buyerCanSeeRetained: bobSeesRetained,
      verdict: !bobSeesRetained && aliceSeesRetained ? "PASS" : "FAIL",
    };
    const { writeFileSync, mkdirSync } = await import("node:fs");
    mkdirSync("ui", { recursive: true });
    writeFileSync("ui/replay.json", JSON.stringify(TRACE, null, 1));
    console.log(`\n   captured verified run -> ui/replay.json (${TRACE.steps.length} steps)`);
  }
}

main().catch((e) => {
  console.error("\nERROR:", e.message);
  process.exit(1);
});
