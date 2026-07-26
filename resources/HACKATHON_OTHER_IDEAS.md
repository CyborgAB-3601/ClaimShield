# Initial Idea Analysis

> Idea shortlist for the Sarvam Epoch Buildathon, combining internet research with the rubric logic.
> Event facts, rubric ladders, capability limits, and the 82-card index live in [`HACKATHON_CONTEXT.md`](./resources/HACKATHON_CONTEXT.md) — not repeated here.

Several of these are **mutations** of library cards (research-sharpened), not the cards themselves. The rubric does not reward copying a card.

---

## Strategic frame (why these, not others)

Three rubric facts drive every pick — full detail in the context doc §3:
- **Six independent ladders; the same evidence can't score twice.** Favour ideas where different behaviours naturally light up different parameters.
- **Branch crowding is uneven:** ~50 of 82 cards are Voice, ~20 Document, **1 Dubbing**. The room will be full of near-identical voice call-center bots. Voice is also the hardest branch to make robust in 6 hours in a noisy arena.
- **Document Intelligence is a rubric magnet:** source traceability + honest refusal hits JTBD, the Sarvam parameter, Delight, and Impact with *distinct* evidence each — and it's the most judge-legible format (hand it an unseen document; it works or it doesn't).

---

## Research signals

Angles researched, with the hard number that matters for the Impact score.

| Angle | Key stat | Implication |
|---|---|---|
| **Health insurance claims** | 11% of health claims rejected (₹26,000 cr, FY24, +19% YoY); complaints up 45% in Q2 2025; **32% of reimbursement rejections caused by illegible/incomplete discharge summaries — the single most fixable reason** | Sharpest, most demo-legible impact story. Every judge has fought a health claim. |
| **Land records** | 60%+ of India's litigation is land-related; two-thirds of all civil cases. "98.5% digitized" but much is deteriorating **handwritten Hindi/regional paper**; pre-computer deeds entirely in Hindi | Digitization = scanning only. The semantic + provenance layer is the real gap. High impact, hard inputs. |
| **Courts** | 55.8M pending cases; 85% in district courts; **76% of prisoners are undertrials** | Litigants can't read their own orders. Real, but the "completed job" is thinner. |
| **Creator dubbing** | ₹3,000 cr market, 22% CAGR; 60%+ YouTube watch-time is regional; 77% of Indian Gen Z watch translated formats; **YouTube already ships Auto-Dubbing** | Generic dubbing is now commoditized by the platform itself → sharpens the case for audience-aware *adaptation* over literal dub. |
| **Prescriptions / medical** | Illegible handwriting in 17–65% of prescriptions; 32.5% of medication errors trace to illegibility | Real, but patient-safety liability makes the demo claim risky. |

Insurance and land are the standouts — both bigger and more legible than most library cards, and neither is a card to copy line-for-line.

---

## Final shortlist (ranked)

### 🥇 A — "Reject-proof your health claim"  ·  Document Intelligence
*New idea; sits between cards #24 and #47.*

Patient photographs the **handwritten discharge summary + hospital bills**. The system reconstructs a structured, claim-ready packet, checks it against the policy's Customer Information Sheet (exclusions, sub-limits, waiting periods, room-rent cap), and **flags the exact fields that will get the claim rejected — before it is submitted** — marking illegible items for the doctor to re-confirm rather than guessing.

- **Obvious version everyone builds:** "upload policy, explain it."
- **Our reframe:** prevent the rejection instead of describing the policy → that is the Creativity + Delight.
- **Rubric fit (distinct proof per parameter):** Impact (razor-sharp, quantified, universally relatable) · Document Intelligence (handwritten summary = load-bearing hard input) · JTBD (the claim packet is the artifact) · Memory (policy rules persist) · Delight (honest refusal on illegible fields).
- **One risk:** source 4–5 real, redacted handwritten discharge summaries before 11:30.

### 🥈 B — "What am I actually buying?" land-deed decoder  ·  Document Intelligence
*Mutation of #87 / #30 / #89.*

Photograph an old **handwritten Hindi/regional sale deed or mutation record**. Reconstruct the ownership chain, boundaries, and encumbrances with **every claim traceable to its source line**, mark unreadable regions, and output a plain-language + regional "what could hurt you in this deal" brief for the buyer.

- **Why strong:** 60% of litigation is land — enormous impact ceiling; provenance + refusal is exactly the Document Intelligence L5 edge.
- **One risk:** real handwritten deeds are the hardest input to source on the floor — have a fallback set ready.

### 🥉 C — Regulatory circular applicability engine  ·  Document Intelligence (enterprise)
*Card #52 — the strongest asymmetric fit for an enterprise-data + agents background.*

Feed the scanned circular the day it lands; return only the paragraphs that bind **this entity** (licence category, size band, products offered), **each traceable to its source line**, with genuinely-unclear ones marked unclear. Derive a dated action list from applicable paragraphs only, push each obligation with its citation into the compliance channel, and produce a vernacular board version alongside the English.

- **Why strong for this builder:** entity-profile applicability filtering = agentic reasoning over governed data; paragraph-level traceability = enterprise provenance; the three-state verdict (applies / doesn't / unclear) = controlled uncertainty; lets you push **Memory & Context** (governed continuity + business rules) where most teams can't.
- **Impact is easy to earn honestly:** one call to a real compliance person before 11:30 gives the current turnaround baseline — that number *is* the Impact score.
- **One risk:** input must be a genuinely scanned circular (not a text-layer PDF); source two from different regulators.

### Alternate — D — Court order explained to the litigant  ·  Document Intelligence + Voice-out
*Card #12, freshly urgent given 55.8M pending cases.*

Extract next-hearing date + what you must do/bring, in the litigant's language, read aloud, with GST-style refusal on the date field. Lower ceiling but the safest scope.

---

## Ranking & the deciding factor

**Builder background (decided):** applied AI research; enterprise data problems; agent design. This is the tiebreaker.

- **Dropped for this profile:** Dubbing (media/ffmpeg pipeline + beta voice cloning is off-wheelhouse, high variance) and pure Voice agents (most crowded branch; the scored craft — prosody, barge-in, emotional read — isn't where an enterprise-data edge shows).
- **Why the remaining three fit:** the winning shape — messy document → structured, source-traceable, governed extraction → business-rule reasoning → usable artifact, orchestrated by an agent — *is* an enterprise-data problem, and lets this builder push **Memory & Context** to a level most teams can't reach.

**Chosen lead: A — Reject-proof your health claim.** Same governed-document shape, chosen for its real, relatable demo. **C (#52 compliance)** is the strongest pure-enterprise fit and closest alternative; **B (land)** is the high-ceiling option if inputs can be sourced.

**Note on internet bias:** the pre-search and post-search #1 picks (#52 and A) are the *same underlying shape* — hard scanned/handwritten doc → traceable extraction → refusal on unclear → rules check → regional output. The web research changed the example, not the thesis.

Next step: lock A and write the M0→M1 slice.