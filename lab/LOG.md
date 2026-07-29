# ATHENA NOCTUA — BUILD LOG (append-only)

RULES OF THIS FILE:
1. Never edit or delete a past entry. Wrong later? Append a new entry that corrects it and reference the old ID. The mistake stays visible on purpose — drift you can't see is drift you repeat.
2. Newest entry at the BOTTOM. Read the tail for current state.
3. One entry per RUN, per DECISION, or per GATE result. No silent runs.
4. For a RUN: the GATE criterion is written into the entry BEFORE you look at the numbers. If it isn't written first, the result doesn't count. This is the whole point — it is what stops "the loss looked fine so I called it done" (v5).
5. A phase GATE is passed only when its STATE §3 criterion, as written, is met. Then tag it in git.

---

## ENTRY TEMPLATE — copy this block, fill top-down, do not skip fields

```
### [ID e.g. A-003] — YYYY-MM-DD — TYPE: RUN | DECISION | GATE
QUESTION:      one line. what does this entry decide?
PRE-RUN CHECK: (RUN only — tick before running; do not run with an unticked box)
  [ ] reveal from fresh z, not real r (L1)
  [ ] L_z prior present if flow is in the loop (L2)
  [ ] verdict metric is checksum / spec_corr, NOT reveal loss (L3, L12)
  [ ] exactly ONE axis changed vs the last run — name it: ____ (L4)
  [ ] float32, AMP off, no dead GradScaler (L5)
  [ ] round trip under test is STFT→iSTFT→STFT, not disk read/write (L9)
  [ ] carrier bins fixed / key-seeded, not magnitude-thresholded (L10)
  [ ] perturbation tracked in dBFS; floor-stats match to be measured (L11)
  [ ] running the file version I think I am (git status clean / hash noted)
  [ ] GATE criterion below is written BEFORE seeing results
GATE (the pre-registered pass/fail):  metric + threshold. e.g. "BER=0 (checksum pass) at ≤ −70 dBFS perturbation AND spectral-flatness diff < X"
SETUP:         files, seed, FFT N / hop / window, params. exact enough to rerun.
RESULT:        the numbers. no interpretation here.
VERDICT:       PASS / FAIL against the GATE line above. one line.
CHANGES:       which L / F / gate / STATE section this updates. or "none".
```

---

## SEEDED HISTORY (Phase 1, reconstructed from run logs — treat as immutable record)

### [H-001] — 2026-06-24 — TYPE: RUN
QUESTION: does the secret live in the stego or the residual?
GATE: (retro) invert untrained net from real r vs random z; if err differs, secret is in r.
SETUP: untrained coupling INN, time domain.
RESULT: real-r err 0.0 vs random-z err 0.7982.
VERDICT: FAIL — secret lives in r, not the stego.
CHANGES: established L1 (two-file trap).

### [H-002] — 2026-06-24 — TYPE: RUN
QUESTION: does reveal-from-r wiring train at all without a prior on r?
GATE: (retro) losses should be non-zero and decreasing.
SETUP: reveal-from-r, no L_z prior, epochs 1–80.
RESULT: all losses 0.0000 from epoch 1.
VERDICT: FAIL — trivial zero-cost solution, no gradient.
CHANGES: established L2 (L_z prior mandatory).

### [H-003] — 2026-06 — TYPE: RUN
QUESTION: (v5) α=0.05 — is it hidden and recoverable?
GATE: (retro, and the lesson) reveal loss looked acceptable — but the honest metric is spec_corr.
SETUP: α=0.05.
RESULT: reveal err 0.064, spec_corr 0.003, −47.8 dBFS.
VERDICT: FAIL — inaudible but reveal = noise. False positive caught.
CHANGES: established L3 (spec_corr is verdict). This is the entry that justifies rule 4 of this file.

### [H-004] — 2026-06 — TYPE: RUN
QUESTION: (v8) deterministic reveal, α=0.1, 200 ep — can the time-domain net relocate energy between bands?
GATE: (retro) spec_corr should climb toward 1 and reveal err should fall.
SETUP: z=0 reveal, α=0.1, 200 epochs.
RESULT: spec_corr −0.013→+0.050 monotonic, reveal err stuck 0.064, conceal −75.9 dBFS.
VERDICT: FAIL on reveal (conceal side excellent). Architecture is the wall.
CHANGES: Phase 1 verdict — 1-D time-domain convs cannot move energy between owl <900 Hz and Blake ~15 kHz. Frozen at tag `phase1-coupling-inn-frozen`.

### [H-005] — 2026-07-23 — TYPE: DECISION
QUESTION: keep owl as cover?
RESULT: owl retired; cover = near-total silence (noise floor only).
VERDICT: pivot committed.
CHANGES: reframes whole plan; F1+F3 become the channel; F5 becomes required.

### [H-006] — 2026-07-24 — TYPE: DECISION
QUESTION: what does "it worked" mean, and what did this chat's review change?
RESULT: "worked" = two proofs (checksum recovery + detector AUC≈0.5). Added L9 (round trip is STFT∘iSTFT, not disk), L10 (carrier bins fixed/key-seeded), L11 (phase needs floor-level magnitude → F1=F3), L12 (both proofs). Corrected the incoming plan's "magnitude stays untouched" assumption and its float-disk round-trip test.
VERDICT: STATE §1–3 updated.
CHANGES: L9–L12 added; GATE A reframed as BER-vs-dBFS + floor match; D-THESIS opened.

---

### [H-007] — 2026-07-24 — TYPE: DECISION
QUESTION: modify selected floor coefficients, or generate the whole floor from a learned distribution? And which silence?
RESULT: Architecture pivoted to distribution-preserving cover-synthesis (F29): the stego is a sampled draw of a declared noise floor whose coordinates encode the payload. No cover, no residual, no salience map. Carrier is an integer-reversible transform over 24-bit PCM (F30/F20); complex STFT (F4) retained as observer/critic domain only. Security bar set to Level 3: indistinguishable from a genuine draw of the declared floor to any distinguisher (Cachin / minimum-entropy-coupling theorem), not "beats one trained detector". Detector evaluation decomposed into reference/neutral/stego (F31). Cover committed to DEFINED SYNTHETIC SILENCE (F35): a specified zero-mean, sign-symmetric noise floor, colour/PSD unset pending Phase 0, not a matched real recorder. Physical and acoustic silence deferred to a companion project (working title Silent Signal).
VERDICT: cover-synthesis and defined synthetic silence committed. Phase-coding channel (F1) demoted to ablation.
CHANGES: promotes F3/F6/F20/F25; resurrects F15; reassigns F1/F4/F22/F23; adds F29–F38 and L13–L20; closes the cover fork (F32) on the synthetic side; replaces STATE §3 Phases 0/A/D with the R0–R7 plan; opens D-MODEL and D-COLOUR.

### [H-008] — 2026-07-28 — TYPE: DECISION
QUESTION: does concealment rest on a key, or on the learned model itself?
RESULT: No key. The concealment map is a single integer-reversible learned flow (F29 via F20/F30): a normalising flow trained by maximum likelihood to model the declared floor, whose weights are the exact invertible map and the only object that can read a produced file. D-THESIS resolved: the concept is machine perception; security rests on the trained weights, not a key or algorithm secrecy; anyone holding the exact weights can read the file, which is the intended stance. D-MODEL resolved: fully learned, not an analytic sampler; the integer-reversible form is required because a floating-point flow will not invert bit-exactly and the sub-threshold payload cannot survive inverse error. Whitening retained but public and keyless (uniformity only). Fresh randomness at conceal (F36) kept: the same image yields a different valid file each run, discarded at reveal.
VERDICT: fully learned, integer-reversible flow, no key. D-THESIS and D-MODEL closed.
CHANGES: resolves D-THESIS and D-MODEL in STATE §4; updates STATE §0 (route committed) and §3 R3 (train the flow); pipeline recorded in PIPELINE.mermaid.

### [H-009] — 2026-07-29 — TYPE: PROJECT STRUCTURE, RESEARCH
Summary: Incorporated new research references; revised algorithm definitions and symbol/terms table; initiated project-wide restructuring.
Details:
Added research references: Yu, C. et al., Generative Steganography Network, arXiv:2207.13867v3 [cs.CV], 14 Aug 2022
A Content-Preserving Secure Linguistic Steganography, arXiv:2511.12565 [cs.CR]
Updated algorithm definitions and redefined the symbols and terms table for consistency with current model direction
Noted alignment with advanced generative steganography approaches (as opposed to prior methods)
Began restructuring overall project structure and model architecture to unify and reconcile prior design ideas
Status: In progress — architecture restructuring ongoing

