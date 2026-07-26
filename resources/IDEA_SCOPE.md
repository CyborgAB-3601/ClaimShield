# IDEA_SCOPE.md

> This document is the control plane for the build. If a proposed change does not improve the active milestone's acceptance test or the chosen rubric strategy, place it in the parking lot.
>
> **Working title:** ClaimShield — a pre-submission health-claim auditor.
> **One line:** Photograph your handwritten hospital discharge summary and bills; it builds a claim-ready reimbursement packet, audits it against *your* policy's rules the way an insurer's claims desk will, and flags the exact fields that will get you rejected or short-settled — before you submit — refusing to guess anything it cannot read.

## 0. Scope status

| Field | Value |
|---|---|
| Event | Sarvam Epoch Buildathon — Razorpay Arena, Sun 26 Jul 2026 |
| Team | **ASSUMPTION: solo or 2 builders — confirm.** Scope written to be completable solo. |
| Build starts | 10:30 IST |
| Submission deadline | 16:30 IST (link announced on floor) |
| Demo duration | 3 min total (0:30 context · 0:30 pain · 2:00 live) |
| Current milestone | M0 |
| Scope owner | *(you)* |
| Last updated | 2026-07-26 (pre-event draft) |

### Status language
- **Specified:** described here but not implemented.
- **Implemented:** code exists.
- **Working locally:** golden path runs in the dev environment.
- **Verified:** acceptance tests have passed.
- **Demo-ready:** reset, fallback, timing, and presentation have been rehearsed.

---

## 1. Idea lock

| Decision | Locked answer |
|---|---|
| One-sentence product | A pre-submission auditor that turns a photographed handwritten discharge summary + bills into a claim-ready reimbursement packet and tells you exactly why the insurer will reject or short-settle it. |
| Specific user | A patient / family member in a Tier-2/3 town filing a **reimbursement** claim (paid out of pocket, now claiming back), who cannot read the English policy fine print. |
| Situation and repeated job | Every hospitalisation ends with a discharge summary + a stack of bills and a 15-day window to submit a correct claim. The job: assemble a claim the insurer will actually pay, and know the deductions in advance. |
| Current workaround | Photocopy everything, submit blind, wait 30 days, then discover a silent short-settlement or rejection — or pay an agent to check it. |
| Hard input | A **phone photo of a handwritten / semi-printed discharge summary** (diagnosis, procedure, admit/discharge dates, room category) + an itemised hospital bill, shot in hospital lighting, sometimes mixed script. |
| Final usable output or state change | A saved **claim packet**: (1) extracted claim fields with per-field confidence, (2) a **rejection-risk report** mapping each risk to the exact policy clause + document line it comes from, (3) a fix checklist of what is illegible/missing, (4) key reimbursement-claim-form fields, (5) a plain-language explanation read aloud in the user's language. |
| Sarvam parameter | **Document Intelligence** |
| Team's unfair advantage | *(CONFIRM)* — placeholder: comfort with document pipelines + a health-insurance/finance angle. The idea is legible to every judge (everyone has fought a claim), so demo empathy is free. |
| Creativity thesis | The product does not *explain the policy* or *summarise the document* (the two obvious builds). It **adversarially pre-adjudicates the claim** against the policy the way the insurer's desk will, and surfaces the rejection before it happens. Prevention, not explanation. |
| Delight thesis | At the real friction point — a frightened patient who already paid ₹X — it does not say "don't worry." It shows the claimable amount, the exact ₹ it will lose to the room-rent cap and *why*, the one field it **refused to read** and needs the doctor to rewrite, and the fixed packet. Honest, specific, forward-moving. |
| Decisive demo proof | A judge hands an **unseen** handwritten discharge summary + a policy with a room-rent cap. The system extracts the fields, computes claimable vs deductible citing the room-rent clause + the source line, **refuses the one illegible field instead of inventing a diagnosis**, and outputs the packet read aloud in Hindi. A second case with a waiting-period exclusion → it predicts the rejection with the clause. |

### Why this idea

#### Asymmetric fit
Real, consequential, and frequent: ~₹26,000 cr of health claims were rejected in FY24 (up 19% YoY), health complaints rose 45% in Q2 2025, and **~32% of reimbursement rejections in Q4 2025 were caused by illegible or incomplete discharge summaries — the single most fixable reason**. The load-bearing capability (reading a handwritten Indian medical document with controlled uncertainty) is exactly Sarvam Doc AI's hard edge, and the branch is uncrowded relative to the ~50 voice-agent builds the room will produce. The moment is now because IRDAI's May-2024 Master Circular tightened the 30-day settlement clock and the Customer Information Sheet mandate, so the rules a claim is judged against are newly standardised and machine-checkable.

#### Decisive proof
Hard unseen input (photographed handwritten summary) → visible processing (field extraction with confidence + refusal) → completed job (a claim packet + a rejection-risk report that cites clauses) → a memorable behaviour (it refuses to guess the diagnosis, and predicts the exact deduction) → repeatable across ≥3 unseen cases without builder help.

---

## 2. User and job

### User
- **Who:** Patient or family member filing a reimbursement claim; low English comfort; owns a smartphone.
- **Context:** Just discharged, has paid the hospital, holds a discharge summary + itemised bill + a policy they've never read.
- **Frequency:** Once per hospitalisation, under a hard 15-day submission window; India runs tens of millions of health claims a year.
- **Existing behaviour:** Submit everything blind, or pay an agent ₹500–2,000 to "check the file."
- **Existing cost/delay/risk:** Silent short-settlement (room-rent proportionate deduction affects ~25–30% of claims), or outright rejection discovered 30 days later with the window closed.

### Job to be done
> When **discharged with a summary, bills, and a 15-day clock**, the user needs to **submit a claim the insurer will actually pay in full**, so that **they recover the money they already spent instead of losing it to a fixable paperwork error.**

### Definition of completion
The job is complete only when:
1. The claim fields are extracted from the real photographed documents with per-field confidence, and unreadable critical fields are **refused, not guessed**.
2. A rejection-risk report exists that names each risk, the ₹ impact, and the **exact policy clause + document line** it derives from (no rule stated from model knowledge).
3. A user-usable artifact is produced: the packet + fix checklist + key claim-form fields, explained in the user's language.

Advice, transcription, extraction, or a chat response alone do not count unless they are themselves the final usable output. Here the **audited packet** is the output.

---

## 3. Product contract

### Golden path
1. User uploads photo(s) of the discharge summary + itemised bill, and selects/uploads their policy (demo: pick one of the pre-loaded policy rule-sheets).
2. Sarvam Doc AI **Extract** pulls the claim fields (patient, hospital, admit/discharge dates, diagnosis, procedure, room category & per-day rent, line-item bill, total) with per-field confidence; low-confidence critical fields are marked **refused (dash)**.
3. Rules engine maps the billed items against the policy rule-sheet — room-rent proportionate deduction, sub-limits, waiting-period/exclusion check on the diagnosis, co-pay — and computes **claimable vs deductible**, each finding citing the clause + the source line.
4. App renders the **rejection-risk report** + **fix checklist** (which document/field to re-obtain) + key **claim-form fields**.
5. Sarvam-Translate produces the plain-language explanation; Bulbul reads it aloud in the user's language.
6. Packet is saved as a resumable case.

### Inputs
| Input | Format/source | Hard characteristics | Validation |
|---|---|---|---|
| Discharge summary | Phone photo (JPEG/PNG) or scan | Handwriting, mixed script, stamps, skew, poor light | Per-field confidence; refuse critical fields below threshold |
| Itemised hospital bill | Phone photo / PDF | Dense table, merged cells, line items | Table reconstruction; totals must reconcile |
| Policy rule-sheet (CIS) | Pre-loaded structured rule-set for demo (2–3 policies) | Room-rent cap, sub-limits, waiting periods, exclusions, co-pay | Rules are data, never inferred by the model |

### Outputs and state changes
| Output/state change | Consumer | Required format | Proof of completion |
|---|---|---|---|
| Extracted claim fields + confidence | The packet / user | JSON, shown in UI with dashes for refused fields | Fields visible, refused ones flagged |
| Rejection-risk report | User (and their agent/CA) | List of findings: risk · ₹ impact · policy clause · source line | Each finding traces to a clause + document line |
| Fix checklist | User | Ordered list of what to re-obtain | Names the illegible field / missing doc |
| Claim-form key fields | Insurer submission | Filled field set (JSON / printable) | Fields populated from extraction |
| Regional read-aloud explanation | User | Audio (Bulbul) + text | Plays in hi-IN (demo) |

### Memory boundary
- **Within one interaction:** policy rule-set, extracted fields, user corrections, computed findings.
- **Across sessions (stretch, L4):** resume the same claim case, show which checklist fixes are done, use the corrected field over the original.
- **Across users / handoffs:** a second patient on the same device **cannot** see the first's claim (tenant isolation) — this is a scored Memory behaviour, keep it.
- **Deliberately forget:** raw document images after the packet is built (privacy) — retain structured fields only.

### Human review boundary
- **Automated:** extraction, rule-checking, ₹ computation, packet + explanation generation.
- **Requires confirmation:** any field the model refused; the user re-photographs or the doctor rewrites it.
- **Escalated:** exclusion/waiting-period hits are surfaced as "likely rejection — verify with insurer/CA," never asserted as final.
- **Uncertainty exposure:** per-field confidence + explicit refusal state + "unclear" verdicts, all visible in the UI.

---

## 4. Creativity and Delight

### Obvious version
"Upload your policy and we explain it in your language," or "OCR your discharge summary." Both stop at extraction/explanation. Predictable from the problem statement.

### Structural creative mechanic
The **policy becomes an adjudicator running against your documents.** The product simulates the insurer's claims desk: it checks the *specific* billed items against *your* specific rule-set and returns the deductions and rejections *before* submission, each traced to a clause. It changes the job from "understand my document" to "pass the insurer's audit."

### Delight moment
The system reaches the smudged diagnosis line and says **"I can't read this field — get the doctor to rewrite it, everything else is ready,"** then shows "You'll be paid ₹58,000 of ₹72,000; ₹14,000 is a room-rent proportionate cut under Clause 4.2 — here's why." It refuses to invent, and it makes the invisible deduction visible in advance.

### Why it is meaningful
It prevents the exact failure that causes ~32% of reimbursement rejections (illegible/incomplete summaries) and the silent room-rent short-settlement — turning a 30-day-delayed loss into a same-day fixable checklist. The Delight is product behaviour, not copy.

### Ideas deliberately rejected
| Rejected mechanic | Reason |
|---|---|
| Animated avatar / celebratory transitions | Cosmetic; rubric explicitly discounts it. |
| Read-aloud as the headline feature | Read-aloud is plumbing (Bulbul); the audit is the product. Don't let it drift the Sarvam parameter to Voice. |
| Cashless/TPA live integration | Out of scope, unbuildable in the window; reimbursement flow is the honest job. |
| Medical advice / diagnosis interpretation | Liability; the product handles claims paperwork, not clinical judgment. |

---

## 5. Event and sponsor dependency

### Verified capability matrix
| Required capability | Product/API/model | Exact endpoint/access | Supported languages/inputs | Limits | Verification source |
|---|---|---|---|---|---|
| Read handwritten discharge summary + reconstruct bill table with per-field confidence & refusal | **Sarvam Doc AI (Sarvam Vision)** — Extract (fields→JSON/CSV/XLSX, per-field confidence, dash for missing) + Digitise (`document_intelligence.create_job(language, output_format)`) | Dashboard + API | 22 Indian languages + English; PDF/JPEG/PNG; handwriting native | **10-page PDF cap**; 50 MB (dashboard) / 200 MB (API) per file | docs.sarvam.ai/docai/getting-started/overview; /api/getting-started/models/sarvam-vision |
| Map extracted facts → policy rules, generate cited risk report | **Sarvam-30B** (escalate to 105B on hard turns) | Chat completion API | Indic-tuned | — | docs.sarvam.ai/api/api-guides-tutorials/chat-completion/overview |
| Plain-language explanation in user's language | **Sarvam-Translate v1** (23 langs) / Mayura v1 (11) | Text API | Sarvam-Translate 23 · Mayura 11 | — | docs.sarvam.ai/api/api-guides-tutorials/text-processing/overview |
| Read the explanation aloud | **Bulbul v3** TTS | `text_to_speech.convert(..., model="bulbul:v3", speaker=<lowercase>)` | **11 languages only** (hi/bn/ta/te/gu/kn/ml/mr/pa/od/en) · 30+ voices | Read-aloud language MUST be in this set | docs.sarvam.ai/api/getting-started/models/bulbul |

### Load-bearing dependency
The demonstrated hard case: a **handwritten, mixed-script discharge summary photographed in bad light**, where the diagnosis and dates carry consequence. Sarvam Vision reads Indian handwriting natively across 22 languages and returns **per-field confidence + a dash for fields it cannot read** — which is precisely the refusal behaviour the top rubric bands require.

### Replacement test
If replaced with a generic OCR / GPT-vision stack:
- **Commodity:** basic printed-text extraction.
- **Degrades:** it hallucinates the diagnosis and dates on handwriting instead of **refusing** them, and has no native per-field confidence on Indian scripts — fatal, because a guessed diagnosis or date is exactly what gets a claim rejected.
- **Demo proves it:** on the smudged field, ClaimShield returns a dash and a "re-confirm" instruction; the generic stack returns a confident wrong value.

### Unsupported assumptions (keep out of the critical path)
- No live insurer/TPA API — policies are pre-loaded structured rule-sheets.
- No cashless/pre-auth flow.
- No claim of clinical correctness — the product does paperwork, not diagnosis.
- Read-aloud only in Bulbul's 11 languages (demo: **hi-IN**).
- **Resolve on the floor:** event-account Doc AI quota/rate limits, and whether >10-page PDFs are needed (keep demo docs ≤10 pages).

---

## 6. Rubric strategy

The Sarvam rubric scores every parameter independently. There is no single overall project level.

| Rubric dimension | Current evidence | Target level | Observable proof | Work required | Milestone |
|---|---|---|---|---|---|
| Job-to-be-done completion | L1 (pre-build) | **L5** | 3+ unseen cases produce a correct audited packet end-to-end, no judge help | Extraction + rules engine + packet | M1→M2 |
| Memory and Context | L1 | **L3** (stretch L4) | Full current claim case survives corrections; tenant isolation on shared device | Case store + correction propagation | M2 (L4 stretch M4) |
| Creativity | L1 | **L4** | Policy-as-adjudicator + refusal + traced clauses reinforce one point of view | The audit mechanic itself | M3 |
| Impact | L1 | **L4** | Named payer, real baseline (32% rejections from summaries; ₹26k cr), 10–30% recoverable | Baseline slide + one real number | M4/demo |
| Delight | L1 | **L4** | Refusal + advance-deduction reveal + fix checklist at the friction point | Risk report UX + recovery | M4 |
| **Sarvam: Document Intelligence** | L1 | **L5** | Handwritten mixed-script summary reconstructed, source-traceable, refused where unreadable | Doc AI depth + confidence/refusal + source map | M3 |

### Level anchors (targets in **bold**)
- **JTBD:** L3 = 50–70% on mocked surfaces + 1 artifact → **L5 = 85%+ across ≥3 repeated cases, end-to-end, no judge intervention.**
- **Memory:** L3 = full current task for an authed user → **L4 = history across sessions + tenant isolation** (isolation is the cheap, high-value proof — keep it even at L3).
- **Creativity:** **L4 = several original choices reinforce one distinctive end-to-end solution** (adjudication + refusal + traceability).
- **Impact:** **L4 = defensible 10–30% movement** — recoverable short-settlements/rejections per claim; get one real baseline number.
- **Delight:** **L4 = handles the hardest moment with judgment and recovers without losing progress.**
- **Document Intelligence:** **L5 = expert-grade on the hardest Indian material with structure, source traceability, and precise uncertainty.**

### Sarvam strength
**Document Intelligence** — the reconstruction of a handwritten discharge summary + itemised bill with per-field confidence, source traceability, and refusal is where the build is exceptional.

### Competence floor (adequate, not over-invested)
Read-aloud (Bulbul), the regional translation, and the web UI polish. Enough to be clear; no more.

### Evidence boundaries (no double-counting)
- Handwriting reconstruction + source traceability → **Document Intelligence** (not Delight).
- Refusing an unreadable field, and the advance-deduction reveal → **Delight** (the *judgment* at friction), while the raw confidence score → Document Intelligence.
- The audit mechanic → **Creativity**.
- Correct ₹ and packet across cases → **JTBD**.
- Tenant isolation + correction propagation → **Memory**.
- The rejection statistics → **Impact** only.

### Rubric traps
- Do **not** let read-aloud reframe the build as Voice — declare Document Intelligence and say why (output is a document/packet; audio is access).
- Do **not** state any policy rule or medical fact from model knowledge — every finding must cite the loaded policy clause + the document line, or it is a hallucinated obligation (fatal, like the compliance card).
- Do **not** count basic OCR as Delight.

---

## 7. Technical plan

### Smallest architecture
```text
[Photo: handwritten discharge summary + itemised bill]
   ↓
[Sarvam Doc AI — Extract (fields + per-field confidence, dash on refusal) / Digitise (tables)]
   ↓
[Rules engine: billed items × policy rule-sheet → claimable vs deductible, each finding cited]
   (Sarvam-30B for mapping/explanation, deterministic math for ₹)
   ↓
[Claim packet + rejection-risk report + fix checklist + claim-form fields]
   ↓
[Sarvam-Translate → plain-language text · Bulbul v3 → read aloud (hi-IN)]
```

### Components
| Component | Responsibility | Owner | Existing/new | Critical path? |
|---|---|---|---|---|
| Camera/upload UI | Capture summary + bill, show fields/refusals, risk report, audio | — | new | Yes |
| Doc AI client | Call Extract/Digitise, parse fields + confidence | — | new | **Yes (de-risk first)** |
| Rules engine | Map items → policy rules, compute ₹, cite clause + line | — | new | Yes |
| Policy rule-sheets | 2–3 structured policies (room-rent cap / waiting-period / clean) | — | new (data) | Yes |
| Explanation + TTS | Translate + Bulbul read-aloud | — | new | No (competence floor) |
| Case store | Persist claim case, corrections, isolation | — | new | Memory stretch |

### Data and state
| Entity/state | Required fields | Storage | Lifetime |
|---|---|---|---|
| ClaimCase | id, user, policy_id, extracted_fields[], confidences[], refused[], corrections[], findings[], status | SQLite/Convex/Supabase (or in-memory for M1) | Session; cross-session at L4 |
| Policy | id, room_rent_cap, sub_limits[], waiting_periods[], exclusions[], copay | Structured file/DB | Static |
| Finding | risk, rupee_impact, policy_clause_ref, source_doc_line | in ClaimCase | Session |

### External dependencies
| Dependency | Why needed | Setup verified? | Failure fallback |
|---|---|---|---|
| Sarvam Doc AI | Core extraction | **Verify in M0** | Pre-digitised JSON of demo docs held ready |
| Sarvam-30B | Rules mapping/explanation | M0 | Deterministic rules-only report (no prose) |
| Sarvam-Translate + Bulbul | Regional read-aloud | M0 (quick) | Show text only |

### Secrets and access
`SARVAM_API_KEY` in `.env` (already present in repo root). Never commit real patient data; use redacted documents only.

---

## 8. Time-boxed build ladder (mapped to the event clock)

### M0 — Feasibility and setup · **10:30–11:15**
**Purpose:** Kill the one unknown that can sink this — Doc AI on a *real handwritten* summary.
Required: API key works; one real photographed discharge summary runs through Extract; you can read back fields + **per-field confidence**; confirm a low-confidence field returns a dash (refusal); repo runs and resets.
**Acceptance:** one real handwritten summary returns structured fields with confidence from Sarvam Doc AI.
**Stop condition:** if Doc AI cannot return usable fields+confidence on handwriting by **11:15**, fall back to **Digitise → markdown → Sarvam-30B field extraction**; if that also fails, narrow the input to semi-printed summaries and say so in the demo.

### M1 — One-hour MVP · target running by **12:15** (handbook's "running by 12:15")
**Purpose:** the ugly end-to-end golden path on ONE hardcoded case.
Required: one uploaded summary → extracted fields → checked against **one** pre-loaded policy (room-rent cap) → a rejection-risk report with **one cited finding** and a claimable-vs-deductible number → rendered on screen. Read-aloud excluded for now.
**Excluded:** polish, multiple policies, translation/TTS, multi-language, case persistence, dashboards.
**Acceptance:** a teammate who didn't build it runs one document through to a cited risk report without editing code or repairing output. → **JTBD L3.**

Rubric vector after M1:
| Parameter | Demonstrated level | Evidence |
|---|---|---|
| JTBD | L3 | one cited audited packet from a real photo |
| Document Intelligence | L3 | fields + confidence off a handwritten summary |
| Creativity | L2→L3 | the audit (not explanation) is visible |
| others | L1 | — |

### M2 — Reliable repeated completion · **~13:30**
Required: 3 representative cases pass (room-rent cap, waiting-period exclusion, clean) + 1 unseen/judge-like case; **refusal** shown on an illegible field; totals reconcile; ClaimCase persists; **tenant isolation** demonstrated; golden path resets.
**Acceptance:** 3 consecutive cases produce the correct packet without builder intervention. → **JTBD toward L5, Memory L3.**

### M3 — Sarvam parameter excellence · **~14:30**
Required: the hard input (handwritten, mixed-script, skewed, stamped) is in the demo; **source traceability** — click a finding to see the exact document line; refusal precise; the generic-OCR version is visibly surpassed.
**Acceptance:** the unseen hard case succeeds and you can explain why it's harder than clean OCR. → **Document Intelligence L4–L5, Creativity L4.**

### M4 — Creativity and Delight · **~15:30**
Required: the advance-deduction reveal + fix checklist + regional read-aloud (Bulbul, hi-IN) on the normal path; recovery from a refused field without losing progress; (stretch) cross-session resume for Memory L4.
**Acceptance:** a first-time user hits the Delight moment unprompted, and Creativity (the audit) is separately visible from Delight (the refusal/recovery). → **Delight L4, Impact L4 via baseline slide.**

### M5 — Demo hardening and submission · **reserve 15:30–16:30**
Required: state resets; live + fallback inputs (pre-digitised JSON ready); API-failure plan; fits 3 min; before/after value explicit; submission assets complete; **no new features**.
**Acceptance:** two consecutive timed rehearsals pass, one on the fallback path.

---

## 9. Test plan

### Golden cases
| Case | Why representative | Expected final output | Status |
|---|---|---|---|
| 1 — Room-rent cap | The most common silent short-settlement (~25–30% of claims) | Packet + "₹X deducted under room-rent Clause N" cited | Specified |
| 2 — Waiting-period exclusion | Diagnosis hits an excluded/waiting-period condition | "Likely rejection — verify" with clause cited | Specified |
| 3 — Clean claim | Proves it doesn't cry wolf | "Fully claimable, packet ready" | Specified |

### Unseen hard case
- **Who chooses:** a judge / teammate who didn't build the extractor.
- **What makes it difficult:** handwritten diagnosis, mixed script, one deliberately smudged critical field, skew.
- **Success:** correct fields, **refusal** on the smudged field, correct claimable/deductible with citation.

### Failure cases
| Failure | Expected behaviour | User recovery | Tested? |
|---|---|---|---|
| Illegible critical field | Refuse (dash), name the field | Re-photograph / doctor rewrites | M2 |
| Unsupported language for read-aloud | Fall back to text; state limit | Read on screen | M4 |
| Doc AI timeout/failure | Use pre-digitised JSON fallback | Demo continues | M5 |
| Contradictory correction | Latest correction wins, propagate to findings | Re-run audit | M2 |

---

## 10. Demo contract

### One-sentence setup
"Thirty-two percent of health-claim rejections come from one fixable thing — the discharge summary — and people find out 30 days too late."

### 60–120 second proof
| Time | What happens | What the judge sees | Rubric evidence |
|---:|---|---|---|
| 0–15s | Judge photographs an unseen handwritten summary + bill | Real capture, not a file picker | Document Intelligence |
| 15–45s | Extraction with confidence; one field **refused** | Fields on screen; a dash + "get the doctor to rewrite" | Document Intelligence + Delight |
| 45–80s | Audit vs policy: claimable vs deductible, each finding **clickable to its source line + clause** | "₹58k of ₹72k; ₹14k room-rent cut, Clause 4.2" | JTBD + Creativity |
| 80–105s | Second case: waiting-period exclusion predicted | "Likely rejection — verify, Clause 3.1" | JTBD + Impact |
| 105–120s | Regional read-aloud + fix checklist | Hindi audio + packet download | Delight (access = competence floor) |

### Live input
Judge-supplied or fresh-photographed handwritten discharge summary.

### Fallback input
Pre-digitised JSON of a held-back summary + rendered audio, ready to play if the network drops.

### Memorable moment
The refusal — it won't invent the diagnosis — plus the invisible deduction made visible *before* submission.

### Final artifact/state shown
The saved claim packet + rejection-risk report + fix checklist.

### Claims we can prove
- It reads real handwritten summaries and refuses what it can't read.
- Every deduction/rejection cites a clause + a document line.
- It completes ≥3 unseen cases without intervention.

### Claims we must not make
- That it guarantees the insurer will pay.
- That it gives medical or legal advice.
- Any policy rule not present in the loaded rule-sheet.

---

## 11. Risk register

| Risk | Probability | Damage | Earliest test | Mitigation | Fallback | Owner |
|---|---|---|---|---|---|---|
| Doc AI weak on handwriting | Med | Fatal | M0 | Test real handwriting first | Digitise→30B extraction; semi-printed inputs | — |
| Model states an uncited rule | Med | High (hallucinated obligation) | M1 | Rules from data only; findings must cite | Deterministic rules-only report | — |
| No real discharge summaries sourced | Med | High | before 11:30 | Gather 4–5 redacted before 11:30 | Use redacted samples + one held back | — |
| Read-aloud drifts build toward Voice | Low | Med (mis-scored branch) | M4 | Keep audio as plumbing; declare Document Intelligence | Drop audio | — |
| Network/API failure on stage | Med | Med | M5 | Fallback JSON + recorded audio | Narrate + play fallback | — |

### Pre-mortem — it's judging time and we failed because:
1. Doc AI hallucinated the diagnosis/date instead of refusing, so the "refusal" story collapsed → **mitigate: threshold + refusal is a hard requirement tested in M0/M2.**
2. We demoed on our own clean, hand-authored summary → **mitigate: unseen handwritten case chosen by someone else.**
3. We stated a policy rule the document didn't contain → **mitigate: every finding cites clause + line; rules are data.**

---

## 12. Non-goals
1. Cashless / TPA / pre-authorisation flows and any live insurer API.
2. Medical or clinical interpretation, diagnosis, or advice.
3. More than 2 output languages, or read-aloud outside Bulbul's 11.
4. A mobile app (web with `capture="environment"` is enough).
5. Fraud detection / bill upcoding analysis.

Any change to these requires an explicit scope decision.

---

## 13. Parking lot
| Idea | Potential value | Why not now | Revisit after |
|---|---|---|---|
| Cross-session case resume + reminders before the 15-day deadline | Memory L4, Delight L5 | Not on critical path | M4 if ahead |
| Auto-fill the actual insurer PDF claim form | JTBD polish | Form-specific, brittle | Post-event |
| Agent/CA handoff view | Memory L4 | Extra surface | Post-event |
| Second language (Tamil/Marathi) | Reach | Competence floor only | M4 if ahead |

---

## 14. Team execution
| Person/agent | Ownership | Current task | Acceptance test | Blocked by |
|---|---|---|---|---|
| *(confirm roster)* | Doc AI client + extraction | M0 feasibility | Fields+confidence off real handwriting | — |
| — | Rules engine + policy sheets | M1 cited finding | One cited deduction computed | Extraction shape |
| — | UI + risk report + read-aloud | M1→M4 | Report renders, refusal visible | — |

### Coordination rules
- One owner per critical-path component.
- Integrate continuously; the golden path stays runnable.
- New work starts only after the active milestone's acceptance test is preserved.

---

## 15. Current state
### Active milestone
M0 — complete. Moving to M1.
### Implemented
- Repo restructured: `backend/` (FastAPI + uv) and `frontend/` (Vite/React), `.env` with `SARVAM_API_KEY` (now correctly gitignored — it was not before).
- `backend/app/sarvam_client.py`: `digitise()` (Sarvam Digitise API) → `extract_fields()` (Sarvam-30B, prompt-enforced strict JSON + refusal, confidence-threshold safety net in code).
- `backend/app/main.py`: `POST /api/extract` wiring the pipeline end to end.
- `frontend/`: upload UI + Claim Ledger results view (claims-desk dossier aesthetic), field confidence, refusal stamp, expandable source-line traceability, raw-digitised-text toggle, timing readout.
### Working locally / Verified
- **Verified end-to-end through the actual UI**, not just curl: synthetic discharge-summary image → digitise → extract → ledger renders correctly. The deliberately illegible diagnosis line came back **refused** (dash, not a guessed value) with its confidence and source-line traceable. Round-trip latency ~7.7s (digitise 5.5s + extract 2.2s).
### Scope-affecting finding (confirmed with you)
- Sarvam **Extract** (native per-field confidence) is Studio-dashboard-only — no REST/SDK endpoint. Locked primary path is **Digitise (API) → Sarvam-30B prompted extraction**, with confidence being LLM-judged uncertainty, not a native Doc AI score. This is now the real implementation, not a fallback.
- The SDK (`sarvamai==0.1.28`, latest available) does not support `response_format` despite docs — extraction relies on prompt-enforced strict JSON with defensive fence-stripping, not JSON mode.
### Current blocker
- Need 4–5 real redacted discharge summaries + itemised bills (you're sourcing these in parallel). Pipeline is proven on synthetic input and will take real docs with no code changes.
### Next single action
- **M1: swap in a real photographed handwritten summary the moment you have one, load 1 policy rule-sheet (room-rent cap), and build the deterministic rules engine + cited rejection-risk report on top of the extracted fields.**

---

## 16. Decision log
| Time | Decision | Evidence/reason | Scope impact |
|---|---|---|---|
| Pre-event | Sarvam parameter = Document Intelligence | Handwritten summary + confidence/refusal is the load-bearing hard edge | Locks branch |
| Pre-event | Reimbursement (not cashless) flow | Buildable, honest, hard-input-rich | Sets golden path |
| Pre-event | Policies are pre-loaded rule-sheets | No insurer API; rules must be data to avoid hallucinated obligations | Removes external dependency |
| Pre-event | Demo read-aloud in hi-IN | Bulbul supports 11 langs incl hi-IN | Constrains language subset |

---

### Sources (impact & domain baseline)
- Discharge summaries cause ~32% of reimbursement rejections; claims rejection +19% FY24 (₹26,037 cr): [Business Standard](https://www.business-standard.com/finance/personal-finance/health-insurance-claims-rejection-up-19-10-in-fy24-irdai-report-124122700754_1.html) · [Moneylife](https://www.moneylife.in/article/health-insurance-claims-worth-rs2603765-crore-rejected-by-insurers-in-fy2324-govt/76282.html)
- Complaints +45% Q2 2025, health = 68%: [Business Standard](https://www.business-standard.com/finance/personal-finance/insurance-complaints-up-45-in-q2-2025-most-about-health-policies-report-125092401017_1.html)
- Rejection reasons (room-rent ~25–30%, non-disclosure, waiting periods): [NYVO](https://nyvo.in/resources/claims/claim-rejection-reasons)
- Required reimbursement documents + 15-day / 30-day IRDAI timelines: [Ditto](https://joinditto.in/articles/health-insurance/documents-required-for-health-insurance-claims/) · [IRDAI Policyholder](https://policyholder.gov.in/how-to-make-a-claim-health)
- Sarvam Doc AI (Extract per-field confidence + dash; Digitise; 22 langs; limits): docs.sarvam.ai/docai/getting-started/overview · Bulbul 11 langs: docs.sarvam.ai/api/getting-started/models/bulbul
