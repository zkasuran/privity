"""Storyboard for the Privity demo video.

Each scene has a voiceover line and a list of actions. An action fires at `at`, which is either
seconds from scene start or a word cue "w:<word>" / "w:<word>#<n>" (nth occurrence) resolved
against the TTS word timings, plus an optional offset `+`.

Selectors refer to elements captured by capture.py on the named page (see PAGES there).
"""

VOICE = "en-US-AndrewMultilingualNeural"
RATE = "-3%"

SCENES = [
    dict(
        id="intro", page="title", chapter="Intro",
        vo="Tokenized funds still settle like paper. Units move in one system, cash in another, "
           "and someone reconciles the gap by hand.",
        lead=0.9, tail=0.5,
        actions=[],
    ),
    dict(
        id="hero", page="landing", chapter="The idea",
        vo="Privity fixes that, on Canton. Both legs of a fund trade commit in one transaction, "
           "so units and cash can never separate. And each counterparty sees only the parcel "
           "it's buying, never the other side's book.",
        lead=0.4, tail=0.6,
        actions=[
            dict(at=0.0, cursor="h1", park=True),
            dict(at="w:Both", zoom=".lede", scale=1.75, dur=1.2),
            dict(at="w:one", hl=".lede b:nth-of-type(1)"),
            dict(at="w:only", hl=".lede b:nth-of-type(2)"),
            dict(at="w:never#2", hl=None),
            dict(at="w:book", zoom=".trust", scale=1.55, dur=1.1),
            dict(at="w:book+0.3", cursor=".trust", dur=0.9),
        ],
    ),
    dict(
        id="stepper", page="landing", chapter="Watch a trade settle",
        vo="Here's the trade. Alice sells Bob four hundred of her thousand units. First she "
           "earmarks exactly that parcel, and only the parcel is disclosed to Bob. Her remaining "
           "six hundred stay private. Then one transaction moves the units to Bob, and the cash "
           "to Alice. Both legs, or neither.",
        lead=0.3, tail=0.8,
        actions=[
            dict(at=0.0, zoom=None, dur=0.8),
            dict(at=0.1, scroll="#how .demo-box", align=0.42, dur=1.4),
            dict(at=1.4, zoom="#how .demo-box", scale=1.45, dur=1.1),
            dict(at="w:earmarks-0.9", cursor="#stepbar button:nth-child(2)", dur=0.8),
            dict(at="w:earmarks", click=True, state="earmark"),
            dict(at="w:remaining", hl="[data-lot=a-600]"),
            dict(at="w:private", hl="[data-lot=b-cannot]"),
            dict(at="w:Then-0.5", hl=None),
            dict(at="w:Then-0.5", cursor="#stepbar button:nth-child(3)", dur=0.7),
            dict(at="w:Then+0.2", click=True, state="settle"),
            dict(at="w:Both", hl="#txchip"),
        ],
    ),
    dict(
        id="banner", page="demo", chapter="The verified run",
        vo="That's the story. This is the evidence: a real run, captured from a Canton "
           "participant through the JSON Ledger API, and clearly labelled as a replay.",
        lead=0.3, tail=0.6, transition="slide",
        actions=[
            dict(at=0.0, cursor="h1", park=True),
            dict(at="w:real", zoom="#banner", scale=1.8, dur=1.2),
            dict(at="w:real", hl="#banner"),
            dict(at="w:real+0.2", cursor="#banner", dur=0.9),
        ],
    ),
    dict(
        id="claims", page="demo", chapter="Four claims",
        vo="Four claims, each checked on the ledger or by test. Settlement is atomic. Disclosure "
           "is calibrated. A failed leg settles nothing. And the NAV is checkable, not just "
           "signed.",
        lead=0.2, tail=0.6,
        actions=[
            dict(at=0.0, hl=None),
            dict(at=0.0, zoom=".grid3", scale=1.3, dur=1.1),
            dict(at=0.1, scroll=".grid3", align=0.45, dur=1.1),
            dict(at="w:atomic-0.3", hl=".grid3 .card:nth-child(1)"),
            dict(at="w:calibrated-0.3", hl=".grid3 .card:nth-child(2)"),
            dict(at="w:nothing-0.4", hl=".grid3 .card:nth-child(3)"),
            dict(at="w:checkable-0.4", hl=".grid3 .card:nth-child(4)"),
            dict(at="w:atomic-0.5", cursor=".grid3 .card:nth-child(1) .pill", dur=0.6),
            dict(at="w:calibrated-0.5", cursor=".grid3 .card:nth-child(2) .pill", dur=0.6),
            dict(at="w:nothing-0.6", cursor=".grid3 .card:nth-child(3) .pill", dur=0.6),
            dict(at="w:checkable-0.6", cursor=".grid3 .card:nth-child(4) .pill", dur=0.6),
        ],
    ),
    dict(
        id="timeline", page="demo", chapter="The settlement, step by step",
        vo="The timeline is the run itself, with real update ids. The seller earmarks four "
           "hundred units, visible to the buyer, while the retained six hundred are visible to "
           "the seller only. Then, delivery versus payment, in a single transaction.",
        lead=0.2, tail=0.5,
        actions=[
            dict(at=0.0, hl=None),
            dict(at=0.0, zoom=None, dur=0.8),
            dict(at=0.2, scroll="#timeline li:nth-child(4)", align=0.4, dur=1.4),
            dict(at="w:seller-0.2", zoom="#timeline li:nth-child(4)", scale=1.9, dur=1.2),
            dict(at="w:seller", hl="#timeline li:nth-child(4)"),
            dict(at="w:visible-0.3", cursor="#timeline li:nth-child(4) .kv span:nth-of-type(1)", dur=0.7),
            dict(at="w:retained-0.3", cursor="#timeline li:nth-child(4) .kv span:nth-of-type(2)", dur=0.7),
            dict(at="w:delivery-0.3", zoom="#timeline li:nth-child(5)", scale=1.9, dur=1.0),
            dict(at="w:delivery-0.3", hl="#timeline li:nth-child(5)"),
            dict(at="w:delivery-0.1", cursor="#timeline li:nth-child(5) h4", dur=0.7),
        ],
    ),
    dict(
        id="atomic", page="demo", chapter="One atomic transaction",
        vo="Here it is. The seller signed the proposal, and the buyer exercises it, so one "
           "transaction carries both authorities. Shares transfer. Cash splits, and pays the "
           "seller. Eight events, one commit.",
        lead=0.2, tail=0.7,
        actions=[
            dict(at=0.0, hl=None),
            dict(at=0.0, zoom=None, dur=0.9),
            dict(at=0.1, scroll=".onetx", align=0.5, dur=1.4),
            dict(at=1.2, zoom="#events", scale=1.5, dur=1.1),
            dict(at="w:Shares-0.2", hl="#events > div:nth-child(2)"),
            dict(at="w:Shares-0.3", cursor="#events > div:nth-child(2)", dur=0.6),
            dict(at="w:splits-0.3", hl="#events > div:nth-child(4)"),
            dict(at="w:splits-0.4", cursor="#events > div:nth-child(4)", dur=0.6),
            dict(at="w:pays-0.2", hl="#events > div:nth-child(7)"),
            dict(at="w:pays-0.3", cursor="#events > div:nth-child(7)", dur=0.6),
            dict(at="w:Eight-0.3", zoom=".onetx .hd", scale=2.0, dur=1.0),
            dict(at="w:Eight-0.3", hl=".onetx .hd"),
            dict(at="w:Eight-0.2", cursor="#evcount", dur=0.6),
        ],
    ),
    dict(
        id="matrix", page="demo", chapter="Who sees what",
        vo="Now the part a public chain can't do. Each row is an active contract query, issued "
           "as that party. The buyer sees its parcel and its cash, and cannot see the seller's "
           "remaining units. The auditor sees only its mandate and the NAV attestation. And the "
           "privacy check passes.",
        lead=0.2, tail=0.7,
        actions=[
            dict(at=0.0, hl=None),
            dict(at=0.0, zoom=None, dur=0.9),
            dict(at=0.1, scroll="#matrix", align=0.45, dur=1.5),
            dict(at="w:Each-0.2", zoom="#matrix", scale=1.4, dur=1.1),
            dict(at="w:buyer-0.2", hl="#matrix tbody tr:nth-child(2)"),
            dict(at="w:buyer-0.3", cursor="#matrix tbody tr:nth-child(2) td:nth-child(3)", dur=0.7),
            dict(at="w:cannot-0.1", cursor="#matrix tbody tr:nth-child(2) td:nth-child(4)", dur=0.6),
            dict(at="w:auditor-0.2", hl="#matrix tbody tr:nth-child(4)"),
            dict(at="w:auditor-0.3", cursor="#matrix tbody tr:nth-child(4) td:nth-child(3)", dur=0.7),
            dict(at="w:privacy-0.5", zoom="#verdict", scale=1.6, dur=1.0),
            dict(at="w:privacy-0.3", hl="#verdict"),
            dict(at="w:privacy-0.2", cursor="#verdict b", dur=0.7),
        ],
    ),
    dict(
        id="code", page="code", chapter="The Daml behind it",
        vo="Under the hood, it's plain Daml. Settlement is one choice, controlled by the buyer. It "
           "checks the parcel is earmarked to them, and that their cash covers the price. Then it "
           "runs the delivery leg and the payment leg together. If any check fails, nothing "
           "commits.",
        lead=0.3, tail=0.6, transition="slide",
        actions=[
            dict(at=0.0, cursor="#s-1", park=True),
            dict(at="w:Settlement-0.2", zoom="#s-1", scale=1.35, dur=1.1),
            dict(at="w:Settlement", hl=["#s-1", "#s-5"]),
            dict(at="w:earmarked-0.4", hl=["#s-14", "#s-15"]),
            dict(at="w:covers-0.4", hl=["#s-20", "#s-21"]),
            dict(at="w:delivery-0.4", zoom="#s-28", scale=1.35, dur=1.0),
            dict(at="w:delivery-0.4", hl=["#s-25", "#s-26"]),
            dict(at="w:payment-0.3", hl=["#s-28", "#s-32"]),
            dict(at="w:nothing-0.3", hl=None),
            dict(at="w:nothing-0.3", zoom=None, dur=1.0),
        ],
    ),
    dict(
        id="nav", page="code", chapter="Verifiable NAV",
        vo="NAV works the same way. The ledger commits to the book with a sha256 hash over the "
           "sorted holdings. An entitled auditor recomputes it, and the attestation verifies. "
           "Change one unit, and it doesn't. An investor can't run the check at all.",
        lead=0.2, tail=0.7,
        actions=[
            dict(at=0.0, scroll="#f-1", align=0.18, dur=1.4),
            dict(at=0.9, zoom="#f-6", scale=1.35, dur=1.1),
            dict(at="w:sha256-0.4", hl=["#f-4", "#f-6"]),
            dict(at="w:sha256-0.3", cursor="#f-6", dur=0.8),
            dict(at="w:auditor-0.4", zoom="#f-11", scale=1.35, dur=1.0),
            dict(at="w:auditor-0.4", hl=["#f-7", "#f-15"]),
            dict(at="w:investor-0.3", hl=["#f-13", "#f-14"]),
            dict(at="w:investor-0.3", cursor="#f-14", dur=0.7),
        ],
    ),
    dict(
        id="repro", page="term", chapter="Reproduce it yourself",
        vo="And you don't need to trust the page. One command runs the whole flow on your own "
           "participant, and prints a receipt: the transaction, digest and NAV verification, the "
           "privacy verdict, and the saved artifact. It exits zero only if everything passes.",
        lead=0.3, tail=0.9, transition="slide",
        actions=[
            dict(at=0.0, cursor="#t-0", park=True),
            dict(at=0.4, type="#t-0", dur=1.1),
            dict(at="w:command+0.1", reveal=["#t-%d" % k for k in range(1, 11)], step=0.12),
            dict(at="w:receipt-0.3", zoom="#t-5", scale=1.6, dur=1.1),
            dict(at="w:transaction-0.2", hl="#t-4"),
            dict(at="w:digest-0.2", hl=["#t-5", "#t-6"]),
            dict(at="w:privacy-0.2", hl="#t-7"),
            dict(at="w:artifact-0.2", hl="#t-8"),
            dict(at="w:exits-0.3", reveal=["#t-11", "#t-12"], step=0.25),
            dict(at="w:exits-0.3", hl=None),
            dict(at="w:zero-0.3", hl=["#t-10", "#t-12"]),
        ],
    ),
    dict(
        id="outro", page="outro", chapter="Wrap-up",
        vo="Privity. Fund trades that cannot half-settle, with disclosure calibrated to need to "
           "know. Built on Canton, for HackCanton Season Three.",
        lead=0.5, tail=3.2,
        actions=[],
    ),
]
