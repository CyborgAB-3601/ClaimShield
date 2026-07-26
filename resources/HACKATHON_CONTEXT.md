# Sarvam Epoch Buildathon — Context Pack

> Single reference for **ideation** and **build**.

**Canonical source (open on the floor):** https://growthx.club/docs/sarvam
The handbook is a single-page app — all 12 sections live at that one URL. It also embeds 5 machine-readable source blocks (`idea-library-source`, `rubric-source`, `hackathon-copilot-prompt-source`, `idea-scope-template-source`, `organizer-context-source`) inside `<script type="text/plain">` tags if you need the verbatim text.

---

## 1. Event facts

| | |
|---|---|
| **Event** | Sarvam Epoch Buildathon (GrowthX × Sarvam, powered by Lightspeed & Bessemer) |
| **Date** | Sunday, July 26, 2026 |
| **Venue** | Razorpay Arena (gate/floor/check-in + Wi-Fi = "coming soon", announced on floor) |
| **On-site window** | 10:00 AM – 6:30 PM IST |
| **Team size** | Solo or up to 5. Every member registers + is approved individually. |
| **Eligibility** | Registered, approved, 18+, physically present. On-site only, no remote contributors. |
| **IP** | You keep everything you build. Handbook/rubric/idea-library are GrowthX IP. |

### Schedule (the clock you build against)
| Time | Phase |
|---|---|
| 10:00 | Kickoff — context, rules, Sarvam platform walkthrough, pick your problem |
| 10:30 | Build sprint starts (6 hours) |
| **11:30** | **Commit to a problem** (self-imposed handbook deadline) |
| **12:15** | **Have something running** (self-imposed handbook deadline) |
| 16:30 | Submission locks (link + form fields announced on floor) |
| 17:30–18:30 | Top teams demo on stage → winners → top 10 present at Sarvam Epoch |

---

## 2. Rules & what qualifies

- **Build on Sarvam.** Sarvam must be *core*, not a garnish. Other LLMs/APIs (Claude, GPT, Gemini, any) may support it.
- **New build, on-site, today.** From zero. AI coding assistants, BaaS (Supabase/Firebase/Clerk/Sheets), and starter scaffolding (Next.js/Vite/FastAPI) are all fine.
- **One submission per team.** Late = not considered. Judges' decision final.
- **Does NOT qualify:** finished build with cosmetic changes · pre-built agent with minor tweaks · your existing product · remote/off-floor code · anything already demoed elsewhere · a stack that isn't Sarvam.
- **Borderline start?** Submit anyway and flag "borderline starting point." Mentors verify. Hiding origin = auto-DQ.
- **Verification consent (T&C clause 9):** submitting = consent to metric verification (read-only analytics, DB spot checks, contact checks). Refusing verification **zeroes that parameter.**

---

## 3. The rubric — how you actually win

**Six independent L1–L5 ladders. There is NO overall project level.** Score each parameter separately.

### Five product parameters (every team scored on all five)
1. **Job-to-be-done completion** — did it produce the correct, usable outcome?
2. **Memory & Context** — carries identity, task state, history, permissions, business rules; no cross-user leakage.
3. **Creativity** — non-obvious problem framing / mechanic / use of Sarvam.
4. **Impact** — value of solving the problem (named payer, baseline, frequency, one metric that moves).
5. **Delight** — at the real point of friction: confidence, clarity, honest judgment, recovery.

### One Sarvam parameter (you choose exactly ONE — OR logic)
- **Voice Experience** · **Document Intelligence** · **Dubbing**
- Judges score the single capability most central to the job. **Extra Sarvam capabilities add zero points.** Depth on one beats breadth.

### The three rules that decide close matchups
1. **The same evidence cannot raise two parameters.** Assign each proof to the one thing it demonstrates.
   - Conversational fluency inside one exchange → **Voice**, not Memory.
   - Basic document/voice/dub competence → the **Sarvam parameter**, not Delight.
   - Impact = value of the *problem*, not whether the prototype works.
2. **Depth over breadth** on the Sarvam capability.
3. **Creativity is structural, not cosmetic** — logo/persona/language/UI theme/avatar/API-count do NOT count.

### Hard numeric anchors (memorize the ones you're targeting)
| Parameter | Key thresholds |
|---|---|
| **JTBD** | L1 = 0 tasks. L2 = <30% success (broken/fake). **L3 = 50–70% on mocked/sandbox + ≥1 usable artifact** (MVP floor). L4 = 70–85% production-like, human review OK. **L5 = 85%+ across ≥3 repeated cases, end-to-end, no judge intervention.** |
| **Memory** | L1 = starts from zero. L2 = holds identifiers only. **L3 = full current task for an authed user.** L4 = history across sessions/channels/handoffs. L5 = governed continuity (task + history + business rules) + tenant isolation. |
| **Creativity** | L1 = obvious first build. L2 = cosmetic twist. **L3 = one meaningful non-obvious choice.** L4 = distinctive end-to-end. L5 = reframes what the product could be. |
| **Impact** | L1 = no case. L2 = weak/<5% or convenience metric. **L3 = defensible 5–<10% on a meaningful metric.** L4 = 10–30% on a major bottleneck. L5 = >30% / step-change. |
| **Delight** | L1 = mishandles friction. L2 = generic care. **L3 = removes obvious friction, honest status, concrete next action.** L4 = handles hardest moment w/ judgment + recovers w/o losing progress. L5 = anticipates next concern, stays with user. |

### Sarvam-branch craft (what earns the level)
- **Voice:** real Indian speech — accents, Hindi-English code-switching, noisy lines, intent under rambling, emotional read, barge-in, corrections, pacing/prosody, follow-ups that build on the last answer.
- **Document Intelligence:** real Indian docs — reading order, structure, handwriting, mixed scripts, tables, degraded/skewed/stamped capture, **source traceability, controlled uncertainty** (mark unreadable regions instead of guessing).
- **Dubbing:** audience-aware adaptation (not literal translation), speaker identity, pronunciation, emotion, pace, timing, overlaps, music, scene cuts, publication readiness.

---

## 4. Verified Sarvam capability surface

> Verify access from the **event account** before making any capability a critical dependency.

| Capability | Model / API | Notes & limits |
|---|---|---|
| **Speech-to-text** | Saaras v3 | 23 input languages. REST (clips) / Streaming (live) / Batch (long). 5 modes: transcribe, translate, verbatim, transliterate, codemix. Speaker diarization available. |
| **Text-to-speech** | Bulbul v3 | 11 output languages, 30+ voices. Tune pitch/pace/loudness. Stream over WebSocket for live agents. |
| **Chat / reasoning** | Sarvam-30B (speed) / Sarvam-105B (hard turns) | Escalate 30B→105B on hard turns. Deep Indic understanding. |
| **Translation** | Mayura (11 langs, context) / Sarvam-Translate (23 langs, long-form) | Language detection on first utterance to auto-switch. |
| **Documents (API)** | Sarvam Vision | 23 languages. **200 MB/file, 10-page PDF cap.** |
| **Documents (Studio)** | Doc AI Studio | Extract (named fields) / Digitise (printed + handwritten → structured). PDF/JPEG/PNG. **50 MB/file, 10 pages/project.** ⚠️ Don't confuse Studio's 50 MB with Vision API's 200 MB. |
| **Creative Studio** | Dubbing + voice-preservation | Voice cloning is **beta** — do not assume it exists in base APIs / event account. Verify. |
| **Voice agents / realtime** | Twilio, Exotel, LiveKit, Pipecat guides + cookbook | **Measure real latency** before promising "instant"/"realtime." Sarvam Conversations = lower-latency realtime voice. |

### Known unknowns to resolve on the floor
Submission URL/fields · which beta/Studio/telephony/realtime surfaces are enabled for the event account · live quotas/rate limits/credits · whether your chosen language pair is supported end-to-end across every input+output surface. **De-risk the hardest dependency in hour one; keep a fallback that still completes the job.**

---

## 5. Ideation guidance

### Two governing principles (from the handbook copilot)
1. **Asymmetric fit** — intersection of a real job + *your* unusual knowledge/access/speed/lived experience + a differentiated Sarvam capability + an uncrowded opportunity + a scope that fits 6 hours. Ask: *"Why are we unusually capable of building this, and why is now the moment?"*
2. **Decisive proof** — design backward from what judges can see in 60–120s: hard/unseen input → visible processing → completed job → final usable artifact/state change → one memorable delightful behaviour → repeatable without builder intervention.

### Opportunity lenses (don't over-index on B2B ops)
Living documents & cultural memory · oral/cultural/spiritual life · cross-language human communication · media adaptation & dubbing · commercial & institutional workflows.

### Guardrails
- Cultural/spiritual ≠ low impact (measure access, preservation, comprehension, reach, time, error).
- Don't claim theological/cultural authority without a source + review boundary.
- Don't assume speaker cloning / same-speaker dub / realtime latency — **verify APIs first.**
- A doc product must do more than OCR (reconstruct, trace, explain, preserve, compare, complete a job).
- A cross-language product must preserve corrections, names, numbers, intent, shared task state — not just translate sentences.

### ⚠️ Idea-library vs rubric mismatch (real trap)
The 82-card library predates the final rubric. ~11 cards are tagged with branches the rubric **abolishes**:
- "Language and Media Quality" → cards 04, 19, 27, 28, 54, 55, 86
- "API Quality and Developer Experience" → cards 34, 81, 82, 83

There is **no such branch.** If you pick one of these, you must remap its declared capability to **Voice / Document / Dubbing** yourself. Also: **only card #94 declares Dubbing** — by far the least-crowded scored branch (Voice is ~50 of 82).

---

## 6. Idea library index (82 cards)

> Sparks, not specs. The rubric does **not** reward copying a card. Each names *the one hard thing* it's scored on. `Starter` = clear demo path · `Beast` = may not finish, defensible partial is OK. Full card text: `idea-library-source` block at the canonical URL.

### Business
| # | Title | Difficulty · Branch |
|---|---|---|
| 01 | GST notice interpretation for regional small traders | Starter · Document |
| 02 | Overdue invoice recovery for MSMEs | Challenging · Voice |
| 03 | Offline machine diagnostics for factory floors | Challenging · Voice |
| 04 | Multilingual documentation for Indian SaaS | Starter · ⚠️remap |
| 05 | Pre-signing contract comprehension for small businesses | Challenging · Document |
| 06 | Section 138 notice drafting for cheque bounces | Challenging · Voice |
| 07 | Supplier verification calls for large orders | Challenging · Voice |
| 08 | Financial report explanation for small business owners | Starter · Document |
| 09 | Handwritten wage register digitisation for informal labour | Challenging · Document |
| 10 | Regional-language customer support for consumer brands | Starter · Voice |

### Public Services
| # | Title | Difficulty · Branch |
|---|---|---|
| 11 | Voice-guided government form completion | Challenging · Voice |
| 12 | Court order interpretation for litigants | Challenging · Document |
| 13 | Voice-drafted police complaints | Challenging · Voice |
| 14 | Voice-first RTI application drafting | Starter · Voice |
| 15 | Pension continuation calls for elderly claimants | Beast · Voice |
| 16 | Generic medicine substitution at the pharmacy counter | Starter · Document |
| 17 | Pre-submission EPF claim verification for workers | Challenging · Document |
| 18 | Cybercrime complaint filing for scam victims | Challenging · Voice |
| 19 | Consumer forum complaint drafting for product disputes | Challenging · ⚠️remap |
| 20 | Voice data entry for community health workers | Beast · Voice |
| 21 | Scholarship eligibility matching for rural families | Starter · Voice |
| 22 | Bank and asset succession navigator for heirs | Beast · Document |
| 89 | Living museum for unreadable collections | Challenging · Document |
| 90 | People's archive from one government record chain | Beast · Document |

### Health and Education
| # | Title | Difficulty · Branch |
|---|---|---|
| 23 | Cross-hospital medical records digitisation for chronic patients | Beast · Document |
| 24 | Pre-purchase insurance policy comprehension | Challenging · Document |
| 25 | Cross-language interpretation between nurses and patients | Beast · Voice |
| 26 | Plain-language explanation of lab reports | Challenging · Document |
| 27 | Comparing conflicting medical opinions across languages | Challenging · ⚠️remap |
| 28 | Personalised mock tests for competitive exam students | Challenging · ⚠️remap |
| 29 | Career counselling for tier 3/4 town students | Challenging · Voice |
| 30 | Plain-language explanation of property documents | Beast · Document |
| 31 | Voice explanation of bank products for first-time customers | Challenging · Voice |
| 32 | Legal rights explainer for interstate migrant workers | Challenging · Voice |
| 33 | English interview coaching for first-generation students | Challenging · Voice |
| 34 | Online course lecture localisation for tier 3/4 students | Beast · ⚠️remap |

### Everyday
| # | Title | Difficulty · Branch |
|---|---|---|
| 35 | Voice-first UPI for feature-phone migrant workers | Beast · Voice |
| 37 | Socratic homework coach that refuses to give the answer | Challenging · Voice |
| 38 | Scam pattern detection for elderly relatives | Challenging · Voice |
| 39 | Handwritten prescription verification for patients | Beast · Document |
| 40 | Active safety check-ins during solo cab rides | Beast · Voice |
| 42 | Voice-first digital task assistant for elderly parents | Challenging · Voice |
| 47 | Post-hospital discharge instructions in patient's language | Challenging · Document |
| 48 | Traffic e-challan verification for drivers | Challenging · Document |
| 50 | Aadhaar update navigator with cascading deadlines | Challenging · Document |
| 52 | Regulatory circular translation for tier 2 compliance teams | Challenging · Document |
| 54 | YouTube video localisation for Indian creators | Challenging · ⚠️remap |
| 55 | Government scheme explainer video localisation | Challenging · ⚠️remap |
| 91 | A prayer companion that waits for you | Challenging · Voice |
| 92 | Oral tradition vault for one community | Beast · Voice |
| 93 | Instant language bridge for two people | Challenging · Voice |

### Business at scale
| # | Title | Difficulty · Branch |
|---|---|---|
| 56 | UPI dispute callback verification at payments scale | Challenging · Voice |
| 57 | Delinquent-borrower collections voice agent | Beast · Voice |
| 58 | After-hours voice support for regional bank customers | Starter · Voice |
| 59 | KYC-authenticated banking inquiries | Challenging · Voice |
| 60 | Cross-product cross-sell qualification for private banks | Challenging · Voice |
| 61 | Quick-commerce order modification (peak dinner hours) | Challenging · Voice |
| 62 | Multilingual delivery confirmation w/ mid-call language switch | Challenging · Voice |
| 63 | Dormant D2C customer reactivation, brand personality intact | Challenging · Voice |
| 64 | Driver coordination voice agent for fleets | Starter · Voice |
| 65 | High-volume candidate screening (skill, not English) | Beast · Voice |
| 66 | Dealer/distributor support voice agent for industrial OEMs | Challenging · Voice |
| 68 | Appointment scheduling for multi-location clinic chains | Challenging · Voice |
| 69 | Fraud alert callback verification for neobank cardholders | Challenging · Voice |
| 70 | Insurance first-notice-of-loss intake for distressed callers | Beast · Voice |
| 71 | Loan application status inquiry voice agent | Starter · Voice |
| 73 | Truck driver daily compliance check-in | Challenging · Voice |
| 74 | Parent counselling voice agent for K-12 EdTech admissions | Challenging · Voice |
| 75 | Post-discharge patient check-in for hospital chains | Challenging · Voice |
| 76 | Therapist pre-session intake for mental health platforms | Beast · Voice |
| 77 | Shaadi RSVP collection voice agent | Starter · Voice |
| 79 | Murder mystery party host voice agent | Challenging · Voice |
| 80 | Bargaining buddy for practising haggling in Indian bazaars | Challenging · Voice |
| 94 | Instant dubbed video messages for a new audience | Challenging · **Dubbing** |

### Technical and infrastructure
| # | Title | Difficulty · Branch |
|---|---|---|
| 81 | Indic speech eval harness | Beast · ⚠️remap |
| 82 | Offline vernacular voice on the last mile | Challenging · ⚠️remap |
| 83 | Indic voice as a tool other agents call | Challenging · ⚠️remap |
| 84 | Live-voice verification against cloned voices | Beast · Voice |
| 85 | Three-language site meeting, one canonical record | Beast · Voice |
| 86 | Provably-correct safety notice in 22 languages | Challenging · ⚠️remap |
| 87 | Handwritten land mutation records, one district | Beast · Document |
| 88 | Crop insurance claim from handwritten sowing records | Challenging · Document |

---

## 7. Build ladder (milestones — from the IDEA_SCOPE template)

- **M0 — Feasibility:** creds work · one real hard input reaches the primary API · response shape + latency understood · repo starts & resets. *Kill unknown dependencies early.* **Stop condition:** if the critical capability can't work by a set time, switch to fallback or kill the idea.
- **M1 — One-hour MVP (build start + 60 min):** one real input → minimum Sarvam processing → minimum app logic → **one final usable output/state change** → saved evidence. Target **JTBD ≥ L3.** Excluded: polished UI, multiple personas, broad language coverage, dashboards, speculative agents.
  - *Acceptance:* a teammate who didn't build it runs one input end-to-end without editing code or repairing output.
- **M2 — Reliable repeated completion:** 3 representative cases pass + 1 unseen/judge-like case + 1 recoverable failure handled + uncertainty visible + state persists + golden path still resets.
- **M3 — Sarvam parameter excellence:** the selected hard input is in the demo, capability is visibly load-bearing, branch hits target level, generic version surpassed.
- **M4 — Creativity & Delight:** structural creative mechanic works · Delight moment observable on the normal path · improves the job · adds no new critical dependency. *Creativity evidence must be distinct from Delight evidence.*
- **M5 — Demo hardening (reserve the final block):** state resets · live + fallback inputs · API/network failure plan · fits time limit · before/after value explicit · submission assets complete · **no new features.** *Acceptance: two consecutive timed rehearsals pass, one on the fallback path.*

**Definition of completion:** advice, transcription, extraction, search results, or a chat response alone do NOT count unless they *are* the final usable output.

---

## 8. Demo contract (3 minutes)

| Time | What | Rule |
|---|---|---|
| 0:30 | **Business context** — name the problem in plain words | No tech, no jargon |
| 0:30 | **Workflow pain** — what happens manually today (people, time, friction) | Establish the baseline |
| 2:00 | **Live demo — the centerpiece** — one real interaction, narrate key moments | **Have a fallback recording.** End on the working product. |

**Do:** lead with the business problem · name the metric you're moving · one outcome not ten features · practice the cold open · close on impact.
**Avoid:** opening with the stack · "anyone can use this" · no baseline · no fallback recording · ending on architecture.
**If the demo crashes:** narrate intended behaviour, recover, move on. Don't burn 30s apologising.

---

## 9. Floor checklist

- [ ] Confirm which beta/Studio/telephony/realtime surfaces are live on the **event account**
- [ ] Confirm your language pair works end-to-end across every input+output surface
- [ ] **Source 4–5 real, redacted hard inputs before 11:30** (docs/recordings/video, whatever your branch needs)
- [ ] Hold ≥1 input **unseen** for the demo
- [ ] Commit to problem by 11:30 · something running by 12:15
- [ ] Measure a stated number on your held-back cases (accuracy / refusal rate / commitment rate)
- [ ] Fallback recording rendered before 16:30
- [ ] Two timed rehearsals, one on the fallback path

---

## 10. Reference links

**Handbook:** https://growthx.club/docs/sarvam

**Sarvam docs**
- Use the `docs-sarvam` MCP toolkit for all Sarvam API/SDK documentation lookups instead of fetching URLs.
