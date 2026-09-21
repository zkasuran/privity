# Privity validation: interview guide and falsification test

Built to the standard the programme's own mentor said it would accept: 5 to 8 structured
interviews, at least 3 from the exact ICP, synthesis of repeated patterns rather than a pile
of public documents, one falsification test, and at least one of (repeated pain language, a
named workflow they all recognise, a hard number, a strong refusal).

**The point of this document is to make the result usable whether it confirms us or kills
us.** A guide that can only produce agreement is not research, it is a pitch with question
marks.

---

## Who counts as the exact ICP

Counts (need at least 3):
- fund accounting lead, transfer agency lead, or head of fund operations at a **third-party
  fund administrator**
- the same function in-house at a **private fund manager** that self-administers

Adjacent, useful but does not count toward the 3:
- fund auditor
- fund lawyer or company secretary
- fund ops software vendor
- a Canton or tokenization team without a live fund

Record which bucket each person is in. Do not quietly upgrade an adjacent conversation into
an ICP one to hit the number.

---

## Rules for running these

1. **Do not describe Privity until section 5.** Everything before that is about their world.
   If the product is on the table early, every answer bends toward it.
2. **Never ask "would you use this".** Stated intent from a friendly conversation is worth
   nothing. Ask what they did last month.
3. **Ask for the last real instance, not the general case.** "Tell me about the most recent
   subscription that went wrong" beats "do subscriptions go wrong".
4. **Chase numbers, then stop.** One number they actually know beats five they estimate to be
   polite. If they do not know, write "did not know" rather than a guess.
5. **Write down their words verbatim** for anything that sounds like pain. Repeated pain
   language is the evidence, and paraphrase destroys it.
6. **Let silence do the work.** The most useful sentence usually comes after the pause.

---

## Section 1. Their world (5 min, no product)

- Walk me through what happens from an investor signing a subscription to units appearing in
  the register. Who touches it?
- Which systems hold the register, the cash record and the investor record?
- How many funds are you responsible for? How many people on the team?

## Section 2. The gap (the core hypothesis)

Hypothesis under test: *cash movement and register update are separate events, and the gap
between them is a real cost.*

- When cash arrives, how do you know? How long until the units are recorded?
- Has that ever gone the other way round, units recorded before the cash cleared?
- What happens over a weekend, a quarter end, or when a wire arrives without a reference?
- **Number to chase:** typical gap, and worst gap in the last year.
- Who carries the risk in the gap, the fund, the administrator or the investor?

## Section 3. Reconciliation and NAV

- Describe period end. How many days, how many people?
- **Number to chase:** person-days per month end, per fund or across the book.
- What is the most common break you find, and where does it come from?
- Have you had a NAV error that required a correction or investor compensation?
  (Regulator-reported NAV error notifications in Luxembourg roughly doubled from 238 in 2019
  to 462 in 2022, per Deloitte's summary of CSSF activity reports. Do not quote this at them
  before they answer, it will lead them.)
- What does producing evidence for the annual audit actually involve?

## Section 4. Secondary transfers and confidentiality

- How often do investors transfer units between themselves? What does that process look like?
- Who is allowed to see the share register? Could one investor ever learn another's position?
- If a register moved onto a shared ledger, what would be unacceptable to you?
- **Listen for the strong refusal.** A sentence like "we could never have other investors able
  to see positions" is high-value evidence. Capture it word for word.

## Section 5. Only now, the product (3 min max)

Describe it in one breath, no slides:

> Both legs of a fund trade settle in a single transaction, so units and cash cannot separate.
> Each counterparty is shown only the parcel it is buying, never the other side's whole
> position. An auditor can be given time-bounded, revocable visibility under a recorded
> mandate.

Then ask:
- Which of those three, if any, is the one you would care about?
- What did I get wrong about your workflow?
- What would have to be true for you to pilot something like this?
- Who else should I be talking to?

## Section 6. Close

- What is the single worst part of your month?
- May I come back with a working version?

---

## The falsification test, committed to in advance

**The wedge is wrong if 3 or more ICP interviews say the timing gap between cash and register
is already handled well enough by their existing bank and reconciliation workflow, and that
they would not change process for it.**

If that happens, the honest response is not to defend the wedge. It is:

1. The pain worth solving is the **audit trail and disclosure evidence**, not settlement timing.
2. The buyer moves to the **auditor or the manager** rather than the administrator.
3. The disclosure package becomes the product and atomic DvP becomes a feature of it, which
   is the reverse of the current framing.

The mentor's own warning applies here: do not switch to the auditor early just because it is
convenient. Switch only if the interviews actually say the ops pain is soft.

**Secondary falsifier.** If nobody produces a strong confidentiality refusal in section 4,
then the privacy half of the thesis is a solution to a problem this ICP does not feel, and the
positioning should lead on atomicity alone.

---

## Synthesis template (fill after each call, same day)

```
Interview  : #N
Date       :
Role/title :
Firm type  : third-party administrator | self-administering manager | adjacent (which)
ICP?       : yes / no
Funds under their responsibility :
Team size  :

Gap between cash and register, typical / worst :
Period-end person-days :
NAV error or correction in the last 24 months? :
Secondary transfer process :

Verbatim pain quotes (their words, not mine):
  -
Strong refusal, if any (verbatim):
  -
Numbers they actually knew :
Numbers they guessed (mark as guesses) :

Which of the three value props landed, if any :
What I got wrong :
Falsification signal? (does this call support or break the wedge) :
Referrals given :
```

## Scorecard to publish in the Metrics material

Report these honestly whatever they say:

| Measure | Target | Actual |
| --- | --- | --- |
| Interviews held | 5 to 8 | |
| From the exact ICP | at least 3 | |
| Named the same workflow unprompted | majority | |
| Produced a hard number | at least 2 | |
| Produced a strong confidentiality refusal | at least 1 | |
| Falsification test result | support / break | |

If the actual column is thin, the material says so. A small honest sample beats a padded one,
and a judge who catches padding discounts everything else on the page.
