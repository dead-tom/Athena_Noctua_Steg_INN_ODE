# ATHENA NOCTUA — PLAN

**What happens next.** The gate ladder R0–R7, the current position on it, and the tasks outstanding. This file is editable and expected to change.

Last updated: 30 July 2026 (LOG H-010; experiment write-ups completed).

RULES OF THIS FILE:
1. Every gate carries a pass/fail criterion written before the run. A gate is passed when its criterion, as written here, is met.
2. Criteria are not moved after results are seen. A criterion found to be wrong is changed only alongside a DECISION entry in `LOG.md` recording that it was changed and why.
3. A passed gate is tagged in git (`git tag gate/R2`) and recorded as a GATE entry in `LOG.md`.
4. This file states what is planned. `LOG.md` states what happened. Where they diverge, LOG is the record.

---

## POSITION

Phase 1 — the 1-D time-domain coupling INN — is frozen at tag `phase1-coupling-inn-frozen` and sits outside this ladder. It failed for a documented architectural reason: 1-D time-domain convolutions could not carry energy between the cover's sub-900 Hz content and the secret's ~15 kHz content. The reveal loss was flat from the first epoch through 200, which is a network with no way to represent the answer rather than one short on training. Written up as EXP-0001 to EXP-0004.

The current architecture — distribution-preserving cover synthesis over a defined synthetic silence, via a fully learned integer-reversible flow with no key — was committed at H-007 and H-008. Nothing has yet been built against it.

**Position: inside R0.** R0's criterion is that one specification document exists, that every later metric refers to it, and that no undefined term remains. That is a writing gate. The document restructure of 29 July and the write-ups below fall inside it rather than before it.

After R0: R1 declares the colour/PSD and builds the reference sampler; R2 is the synthetic oracle codec `oracle_distribution_codec.py`, which proves the coding path before any flow is trained.

---

## SESSION TASKS

### Corrections to the Phase-1 write-ups
Four small edits, arising from the write-ups themselves.

- **Dates.** All four experiment files read 2026-07. The LOG places H-001 and H-002 at 24 June and H-003, H-004 in June. EXP-0001 to EXP-0003 read 2026-06; EXP-0004 likewise unless evidence says otherwise.
- **EXP-0003 status.** The file reads `partly worked`, the index table reads `failed`. The question asked was whether an alpha exists that is both inaudible and recoverable; the answer was no. One value, consistently.
- **Duplicate v8 reporting.** EXP-0003 and EXP-0004 both report −75.9 dBFS, +0.050 correlation and the flat 0.09 loss, leaving it ambiguous whether that is one run written twice. EXP-0003's deterministic-reveal paragraph reduces to a single cross-reference; EXP-0004 holds the detail.
- **EXP-0004's forward pointer.** Its closing section proposes a Neural ODE and frequency-domain hiding. That was accurate in July and was superseded on the 24th. A closing note records this: *"Superseded — the frequency-domain / Neural-ODE branch proposed here was not taken. On 24 July the project pivoted to distribution-preserving cover synthesis (LOG H-007, H-008). Phase 1 is frozen at tag `phase1-coupling-inn-frozen`."*

### Correction to the record
The v7 alpha sweep (0.5, 0.2, 0.1 at 120 epochs) is not individually logged, though its artefacts are in `runs/` and its write-up is EXP-0003. A LOG entry recording this corrects the record by addition, per rule 1 of that file. The same entry can carry the confirmed mapping between experiments and log entries:

| Experiment | Log entries |
|---|---|
| EXP-0001 | H-001 and H-002 together — the two-file trap, and the fix for it |
| EXP-0002 | H-003 — the v5 false positive |
| EXP-0003 | the v7 sweep, not individually logged |
| EXP-0004 | H-004 — the architectural verdict |

### Two unread references
References 26 (Generative Steganography Network) and 27 (A Content-Preserving Secure Linguistic Steganography) were added on 29 July and have not been read. For each: whether it moves an F-row's LEAD, resurrects a parked idea, or introduces a structural option warranting an F39. Any structural movement is recorded as a DECISION entry in `LOG.md`. Until then the provisional one-line summaries in `IDEAS.md` stand as unverified.

### Architecture reconciliation
`docs/method/ARCHITECTURE.md` was transcribed from H-007 and H-008 without sight of `docs/method/pipeline.mermaid`. Where the two disagree, one is right; the disagreement is resolved rather than left standing.

### Document split
`docs/_TO_SPLIT_writeup.md` divides between `docs/concept/` and `docs/method/`, after which the file is deleted.

### Closing R0
The claim contract assembles: duration, sample rate, channel count, PCM encoding, the declared silence specification (STATE §8 → `docs/concept/ON_SYNTHETIC_SILENCE.md`), the canonical image object, payload byte length, key policy (none), file-only scope. The gate turns on undefined terms — "roughly silent", "recognisable", "near chance" — none of which survive into the contract. Passing tags `gate/R0`.

---

## STANDING TASKS

Small, unassigned to a session, and prone to being lost.

- **F26.** Two or three lines on the fingerprinting / misdirection idea, the origin idea preceding the steganography build. Not a research task; it decays with memory rather than with time.
- **`data/README.md`.** Provenance for the source material: the Xeno-canto catalogue number and licence terms for the tawny owl recording, and the origin of the Moloch drawing.
- **D-HYPHEN.** Settled once at write-up with a find-and-replace.

---

## THE LADDER — R0 to R7

Copied verbatim from the version committed at H-007. Criteria are pre-registered.

**R0 — Claim contract.** Freeze: duration, sample rate, channel count, PCM encoding (24-bit, no dither), the declared silence distribution (the §8 spec; colour unset pending R1), the canonical image object (F5, raster or vector claim), payload byte length, key policy, and the file-only scope.
- GATE R0: one specification document exists; every later metric refers to it; no undefined term ("roughly silent", "recognisable", "near chance") remains. Cover fork already closed: defined synthetic (F32).

**R1 — Declare the distribution, build the reference sampler, size capacity.** There is no real corpus to collect; instead fix the declared law: colour / PSD (the unset parameter, chosen for what reads cleanest), amplitude law (discretised Gaussian default), low-bit behaviour (F34), stationarity. Build the exact reference sampler and measure its entropy rate.
- GATE R1: the reference sampler produces zero-mean, sign-symmetric draws that match the declared spec; the canonical payload is ≤ 10% of the entropy-rate capacity.

**R2 — Synthetic oracle codec (the central cheap proof).** The declared law is the known process, so the oracle and the reference sampler are the same object. Payload plus fresh randomness → measure-preserving matcher over the declared CDFs → integer-reversible transform → 24-bit PCM. Decode inverts exactly.
- GATE R2, over ≥ 1000 payloads and seeds: checksum success 100%; zero bit errors; samples in PCM range; the deterministic-CDF reveal survives a file save and reload in a FRESH process; neutral-vs-stego AUC within the declared equivalence region. If R2 fails, do not train the flow; the arithmetic or the implementation is broken. R2 uses a fixed analytic sampler as a stand-in for the floor so the coding path is proven before the flow exists; the trained flow replaces that stand-in at R3.

**R3 — Train the flow (the model).** Train the integer-reversible flow by maximum likelihood on reference draws to model the declared floor. This is the learning stage; the resulting weights are the concealment map and the only reader. Train the neutral generator (no payload) first, so model mismatch is isolated before any message is folded in (L19).
- GATE R3: neutral-generated vs reference at chance on held-out draws, with the R5 ensemble, CIs reported. The flow must invert bit-exactly on its own output (integer closure) before proceeding.

**R4 — Payload-conditioned generation, capacity ladder.** 128 b → 512 b → 1 KiB → 4 KiB → 16 KiB → full canonical image. At each level generate neutral and stego.
- GATE R4 per level: checksum-exact recovery over 100 consecutive files; reference-vs-stego within the equivalence region; no secret-correlated structure in magnitude, phase, or cepstral views. Stop at the first level that breaks; that is the empirical capacity.

**R5 — Adversarial battery.** Detector ensemble: raw-PCM 1-D residual CNN; multiresolution complex-STFT net; magnitude/phase-difference CNN; cepstral and higher-order-statistics classifier; explicit bit-plane/quantisation model; long-context temporal model; MMD over handcrafted and learned embeddings. Reference draws are unlimited (sample the oracle).
- GATE R5, every family: 95% AUC CI within the declared equivalence region (recommended [0.47, 0.53]); no single seed exceeds 0.55; the reference-vs-reference control behaves equivalently.

**R6 — Magnitude invisibility.** Secret-to-spectrogram normalised cross-correlation across scales; template matching under translation and resize; difference from the reference-draw null; detector activation maps.
- GATE R6: no secret-dependent score is distinguishable from reference controls; no stable texture survives across independent stego files carrying the same image (F36).

**R7 — Export and clean-room reveal.** Quantise once to signed 24-bit PCM. WAV PCM_24, no dither, no normalisation, no limiter, no metadata-dependent decoding, no secondary chunks; payload lives only in sample values.
- GATE R7: the PCM integer array is identical before and after export; the checksum passes from the reloaded file; the full conceal/reveal program runs in a clean environment from only the WAV, the fixed sampler/model, and the key. The declared low-bit behaviour (F34) is reproduced.

---

---

## DEFERRED / OUT OF SCOPE

- **Physical and acoustic silence** — real recorded floor, and silence transmitted as an actual acoustic signal — is deferred to the companion project *Silent Signal*. The ideas parked for it are F7, F8, F9, F10.
- **The matched-recorder claim** (counterfeit a real recording rather than a declared synthetic law) is the other side of the F32 fork, closed on the synthetic side and deferred to the same companion project.
- **Robustness to lossy channels** (resample, MP3, noise) is conceded by the digital-lossless intent. F9 returns only in the acoustic case.
- **Privacy on top of the scheme** — anyone holding the exact weights can read the file, and that is the intended stance (D-THESIS). An encryption layer is an optional add-on, out of scope.
- **Fork A exhibition path** (F27/F38) — recover bit-exact via Fork B, then paint into a fresh spectrogram for display. Meaningful only once R4 recovers bit-exact.
