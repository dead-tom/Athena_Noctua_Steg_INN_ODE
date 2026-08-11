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

### [H-010] — 2026-07-29 — TYPE: DECISION
QUESTION: where does each kind of writing live, and what is the repository layout?
RESULT: Whole-project restructure executed and committed. Layout now:
  - `docs/concept/` — ATHENA_NOCTUA (why the project exists), ON_SYNTHETIC_SILENCE (what silence is here).
  - `docs/method/` — ARCHITECTURE, FORMULATION (mathematics, losses folded in), ALGORITHMS, METHODOLOGY, EVALUATION, GLOSSARY, pipeline.mermaid.
  - `docs/related_work/` — RELATED_WORK, references.bib, papers/.
  - `lab/` — STATE (current truth, editable), LOG (this file, append-only), DECISIONS (decision register), PLAN (roadmap and gates), IDEAS (idea register F1–F38 + references).
  - `experiments/` — one folder per experiment, `_TEMPLATE/` and an index README. EXP-0001–EXP-0004 created for the frozen Phase-1 coupling-INN runs.
  - `src/athena/` — flat package (previously `src/`, five-subpackage plan rejected as premature).
  - `runs/` — machine output, GITIGNORED and disposable. Replaces the old `outputs/` junk drawer, which is deleted.
  - `configs/`, `data/{raw,processed,generated}`, `models/`, `media/`, `notebooks/`, `tests/`.
  Two consequences worth recording. (1) The Phase-1 audio artefacts (`stego_owl*.wav`, `recovered_*.wav`) now sit in untracked `runs/` and are disposable by design: the record of Phase 1 is H-001–H-004 plus the EXP write-ups, not the WAVs. (2) `lab/DECISIONS.md` and `lab/PLAN.md` were empty and are now populated from STATE §4 and STATE §3 respectively; those two STATE sections become pointers, on the same principle by which STATE §5 already points at IDEAS. Nothing was deleted in the move — content was relocated, and STATE §1 (the claim) and §8 (the cover spec) are marked for later migration to `docs/method/EVALUATION.md` and `docs/concept/ON_SYNTHETIC_SILENCE.md`.
  `docs/method/ARCHITECTURE.md` written up from H-007 and H-008; it is a transcription of decisions already taken, not a new design. It must be reconciled against `docs/method/pipeline.mermaid` at the next session.
  Two references added and NOT yet read: 26 (Generative Steganography Network, arXiv:2207.13867v3) and 27 (A Content-Preserving Secure Linguistic Steganography, arXiv:2511.12565v2). Logged in IDEAS with an unread flag; reading and integration is the first item of the next session.
  Proposed mapping of the new experiment folders onto this log, to be confirmed when they are written up: EXP-0001←H-001, EXP-0002←H-002, EXP-0003←H-003, EXP-0004←H-004.
VERDICT: structure complete. No experimental claim, metric, or gate criterion was touched by this entry — R0–R7 stand exactly as written at H-007. Next single action is unchanged: the synthetic oracle codec (`oracle_distribution_codec.py`), gate R2.
CHANGES: updates STATE §0, §3, §4, §6, §7; creates lab/DECISIONS.md and lab/PLAN.md; adds refs 26–27 and a dated note to IDEAS; creates docs/method/ARCHITECTURE.md. Opens D-REPO (recorded as resolved in DECISIONS). No change to L1–L20, to §1, or to R0–R7.

[H-011] — 2026-07-30 — TYPE: DECISION

QUESTION: what was written today; what is the work as against documentation of it; and in what order does the remaining project run? RESULT: Written. EXP-0001 to EXP-0004 written up retrospectively from this log and from the run artefacts, with the index table in experiments/README.md filled. Confirmed mapping: EXP-0001 ← H-001 and H-002 together (the two-file trap and its fix); EXP-0002 ← H-003 (the v5 false positive); EXP-0003 ← the v7 alpha sweep; EXP-0004 ← H-004 (the architectural verdict). Correction by addition (rule 1). The v7 alpha sweep — α = 0.5, 0.2, 0.1 at 120 epochs each, spectrogram correlation −0.003, −0.014, −0.002, reveal error holding near 0.065 across a fivefold amplitude change — was never given its own entry at the time. It happened, its artefacts are in runs/, and it is written up as EXP-0003. Recorded here so the log accounts for it. lab/COLLAB.md created. A record of notable moments in working with AI on this project, good and bad, kept by Tessa with a dated section written by Claude. The project concerns machine perception, so how the machine was used to build it is material rather than a footnote. It feeds docs/90_meta/AI_USE.md at write-up. First entry, C-001, covers the Phase-1 stretch in which several cycles of parameter search preceded the architecture question being accepted. D-DISTRIBUTION resolved. The artefact is the lossless WAV, distributed from the repository. Video, screen recordings, social posts and any live presentation are documentation and carry nothing; platform re-encoding destroys a payload sitting below −80 dBFS in exact sample values. Captions state this. The split is stated as the thesis rather than as a caveat. D-WRITEUP resolved. Repo-first, concept-led, technical strand fully visible. Not a paper with a statement attached, and not an essay with the working hidden. Sequencing. Write-up before further experiment. The current state is published — repository, essays, Fork A material, the Phase-1 negative results, the architecture specification and the gate ladder — and R2 onward is revisited after. This is a deliberate ordering, not a deferral: what the project can already show is the reasoning, and the reasoning is complete enough to present. Rule 6 added to this file's header: every entry ends with a next-session prompt. Recorded here because the header was edited. VERDICT: the written record now stands on its own. No experimental claim, metric or gate criterion changed. STATE unchanged except for one row in the §4 decision table. CHANGES: adds D-DISTRIBUTION and D-WRITEUP to DECISIONS; creates lab/COLLAB.md; adds rule 6 above; PLAN's session tasks are superseded by the prompt below. R0–R7 and L1–L20 untouched.
- also wrote a claude.md log. so that ithe is optimised for LLM/AI reading 

### [H-012] — 2026-08-06 — TYPE: PROJECT STRUCTURE, DECISION

QUESTION: does the concept folder hold two essays or one document, and what is the standing of the March abstract now that it exists as a laid-out artefact?

RESULT: One document. `docs/concept/ATHENA_NOCTUA.md` and `docs/concept/ON_SYNTHETIC_SILENCE.md` are deleted and replaced by `docs/concept/PROJECT_CONCEPT.md`, a full transcription of `Athena_Noctua_Abstract_v1.pdf`. The two essays were never independent pieces: *On Synthetic Silence* sits inside the abstract's own flow, between the Moloch section and Part II, and holding it separately meant maintaining the same prose twice. The abstract is the concept statement; the split was a layout decision imported from the H-010 folder plan and it did not survive contact with the source.

The PDF is kept alongside the markdown as the laid-out version. The rule is that nothing lives only in the PDF — all writing is in the `.md`, and the PDF carries only typography, image placement and the pull-quote spreads. This is the same split already committed at H-011 for the WAV and its documentation, applied to the concept text: the readable record is the repository file, the designed object is documentation of it.

Transcription method recorded because it bears on trust in the file. The Pages bundle (`abstract_to_md.pages`) was decoded directly — a `.pages` file is a zip of Snappy-compressed protobuf, so the text and the full-resolution images came out of `Index/Document.iwa` rather than being re-typed — then checked line by line against the PDF export. The five equations of the Algorithm Architecture were recovered from the document's embedded equation objects and confirmed against the PDF's flow-chart page. Corrections were limited to unambiguous slips and are listed in the file's own transcription note.

Content the earlier drafts did not have, now in: the steganography etymology paragraph (*steganos* / *graphein*); the *Metropolis* stills; the Synthetic Silence Sample statistics block (480000 samples, 10 s @ 48 kHz, RMS −60.00 dBFS, positive/negative difference 0); the "proposed architecture" paragraph; the full Sequential Steps I–IV with the training loss and the embedding/recovery pseudocode; the With Thanks page. Part III is *Silent Signal*, which the three-box structure diagram states and the earlier transcription had missed.

References added and linked in the document: Owl of Athena; *Athene noctua*; **Hegel, *Elements of the Philosophy of Right* (1820), and the Preface itself, where the owl passage sits (Berlin, 25 June 1820), plus the Oxford Dictionary of Philosophy gloss** — the Hegel line had been quoted since March without a source; Munich Cosmic Circle; Rationalism; *Metropolis* (1927); Blake's illustrations of *On the Morning of Christ's Nativity* and the Huntington catalogue entry for Illustration 5; Ginsberg's *Howl* and the Allen Ginsberg Project page on the Moloch section.

TWO OPEN ITEMS, both flagged in the file and neither resolved here.

(1) NOTATION. The abstract's notation is provisional and predates H-008. `H` for host examples and `S` for the secret both belong to the pre-pivot framing; under cover-synthesis (F29) there is no host to hide inside, and a reader moving from `PROJECT_CONCEPT.md` to `FORMULATION.md` will meet two different vocabularies for the same system. Left as written, because the file is the record of the abstract as presented in March, not a restatement of current method. Two operator glyphs did not survive extraction from the PDF and appear as `C` (lossless compression) and `M` (assembly of payload bits, fresh randomness and padding into the latent vector); the surrounding comments are verbatim and fix what the operators do, but the letters are inferred. **Check both against `FORMULATION.md` and correct the file.**

(2) ARCHITECTURE. `docs/method/ARCHITECTURE.md` was reconciled against `docs/method/pipeline.mermaid` this session — the two agree, and the header now records the reconciliation as resolved with the diagram governing. But the abstract's Sequential Steps are a *third* statement of the same pipeline, and the process schematic reproduced in the concept document already contains most of what H-007 and H-008 later committed (SHA-256, lossless compression, whitening, measure-preserving CDF, fresh randomness, same weights both directions). **ARCHITECTURE needs updating to account for the Sequential Steps, and the three statements need to agree or the disagreement needs recording.**

MEDIA. Six image slots in `PROJECT_CONCEPT.md` are `TODO` placeholders: the tree still, the Part II card, the synthetic-silence-sample spectrogram, the Algorithm Flow Chart, the Process Schematic, and the owl-eye still. **All media to be normalised to PNG rather than JPEG tomorrow** — the process schematic in particular came out of the Pages bundle as a JPEG and should not be carrying generation loss in a document about bit-exact recovery. Note also that the supplied path `media/refernces/` is misspelt; rename or leave deliberately, but decide.

VERDICT: concept folder restructured to a single document. No experimental claim, metric or gate criterion was touched. R0–R7 and L1–L20 stand exactly as written at H-007. The next single action is unchanged: the synthetic oracle codec (`oracle_distribution_codec.py`), gate R2.

CHANGES: deletes `docs/concept/ATHENA_NOCTUA.md` and `docs/concept/ON_SYNTHETIC_SILENCE.md`; creates `docs/concept/PROJECT_CONCEPT.md` and adds `Athena_Noctua_Abstract_v1.pdf` alongside it; updates STATE §0 and §6. Supersedes the H-010 instruction that STATE §8 (the cover spec) migrate to `ON_SYNTHETIC_SILENCE.md` — the destination is now `PROJECT_CONCEPT.md`, and the migration is still outstanding. Adds the Hegel, Blake/Huntington, Ginsberg and owl references to the concept document; these are not yet in `references.bib`. No change to §1, to R0–R7, or to L1–L20.

NEXT SESSION: convert all concept media to PNG and fill the six TODO slots. Then resolve the notation question — decide whether `PROJECT_CONCEPT.md` keeps March notation with a pointer to `FORMULATION.md`, or is annotated in place; if the latter, that is a D-entry. Then bring `ARCHITECTURE.md` into agreement with the Sequential Steps. Refs 26 and 27 (Generative Steganography Network; A Content-Preserving Secure Linguistic Steganography) remain unread and were first flagged at H-010 — they have now been carried across two sessions.

### [H-013] — 2026-08-11 — TYPE: DECISION
QUESTION: PIPELINE.mermaid C4/R8 carry a lossless compression stage that FORMULATION §6 omits. Which is correct?
RESULT: Compression kept. FORMULATION and ARCHITECTURE corrected to include it; PIPELINE.mermaid unchanged and confirmed governing. Symbol is C, restoring the operator glyph lost in the abstract's PDF extraction and flagged for checking at H-011 — that open item is now closed for C. M (assembly of payload bits, fresh randomness and padding into the latent vector) is Φ in FORMULATION and remains to be confirmed against the abstract.
The reconciliation recorded at the concept-restructure entry stated that ARCHITECTURE.md and pipeline.mermaid agree. They did not: ARCHITECTURE's inline diagram omitted both lossless compression and the integer analysis/synthesis transform. Correction by addition — the reconciliation was recorded in the header but not carried into the diagram body. The integer analysis/synthesis transform remains absent from ARCHITECTURE's inline diagram and is not addressed here.
Repository: `runs/` was not in fact gitignored, though D-REPO records it as such. Rule added (`runs/*`, `!runs/.gitkeep`) and verified with git check-ignore. Only `.gitkeep` had been tracked, so no machine output entered the repository.
Repository moved from ~/Dropbox/GITHUB/ to ~/Projects/Athena_Noctua_Steg_INN_ODE and pushed to GitHub. STATE §6 updated.
D-COMPRESS opened and resolved. R.5 added to FORMULATION §9. Concrete form of C set at R2.
VERDICT: compression retained as capacity headroom, not as a security component. It reduces m only; it does not change Q. Reversible if R1 shows ample margin.
Windows training machine not yet re-cloned — Dropbox folder removed, fresh clone from GitHub to C:\Users\tessa\Projects\ outstanding; STATE §6 Windows path is stale until then.