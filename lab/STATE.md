# ATHENA NOCTUA — STATE (living document)

Last updated: 24 July 2026.
Read order every session: this file top-to-bottom, then the tail of `LOG.md`.
This file is EDITABLE. `LOG.md` is APPEND-ONLY. When they disagree, LOG is the record of what happened; STATE is the current interpretation.
Full idea register and reference list live in `IDEAS.md`; this file points there rather than duplicating them.

---

## 0. STATUS NOW

Architecture and cover both committed (LOG H-007).

- **Cover:** defined synthetic silence (F35), a specified mathematical noise floor, not a recorded room and not a matched recorder. The named-distribution fork is closed on the synthetic side. Physical and acoustic silence is deferred to a forthcoming companion project, working title *Silent Signal*.
- **Architecture:** the reverse learned lossless codec (F29). The payload selects one valid draw of the declared floor. It is recovered bit-exact and is statistically indistinguishable from an ordinary draw of the same declared distribution. This is Level-3 security: nothing to detect, up to a measurable model gap, rather than "beats one trained detector".
- **Carrier:** integer-reversible transform over 24-bit PCM (F30/F20). No float STFT on the conceal/reveal path.
- **Retired / frozen:** owl cover retired (23 Jul). Phase 1 (1-D time-domain coupling INN) frozen at tag `phase1-coupling-inn-frozen`, proven unable to relocate energy between bands. The old phase-coding channel (F1) is demoted to an ablation.

**Route committed (D-MODEL resolved): fully learned, no key.** The concealment map is an integer-reversible learned flow (F20/F30 as the integer route for F29). A normalising flow is trained by maximum likelihood to model the declared floor; its weights are the exact invertible map between the floor and a simple latent, and those weights are the only object that can read a produced file. There is no encryption key and no stored side information. Whitening is retained but is a public, keyless step that only makes the bitstream uniform. Fresh randomness at conceal (F36) makes every encoding of the same image a different valid silence. See the pipeline diagram (`PIPELINE.mermaid`).

**Next single action:** the synthetic oracle codec (`oracle_distribution_codec.py`), gate R2. It proves the coding path (matcher plus integer transform plus checksum, survived across a file save and reload) before the flow is trained. See §3 R2/R3.

Cover specification is in §8. Committed idea stack: F3, F20, F25, F29, F30, F31, F32, F35 (target/architecture); F15, F33, F34, F36 (mechanism); F5, F18 (payload); F6/F31 (verdict instrument).

## 1. THE CLAIM — what "it worked" means (two proofs, both required)

"It worked" is not one result. It is two, and neither alone counts. Under defined synthetic silence the reference is a fresh draw from the declared distribution (the oracle sampler of §8), so "genuine floor" means an independent sample of the declared law.

- **Proof 1 — recovery.** The decoder reads the stego, recovers the payload, and the checksum matches exactly. Binary pass/fail. Not reveal loss, not an eyeballed image, not spec_corr alone: a hash over the declared canonical object (F5), verified bit-exact. This is the antidote to the v5 false positive (reveal 0.064, spec_corr 0.003 = noise that looked fine).
- **Proof 2 — indistinguishability.** The same stego yields nothing to any non-decoder tool: linear, log, and high-gain magnitude spectrograms, phase and cepstral views all read as floor, AND a trained detector ensemble scores AUC within a declared equivalence region around 0.5 on declared-draw-vs-stego.

Failure modes this framing catches:
- Checksum passes but detector AUC 0.9 → working codec, but distinguishable. Fails the thesis.
- Detector at chance but no checksum → reads as silence, but no proof anything is in it. Proves nothing.

Only the pair counts: checksum-exact says the codec reads it; detector-at-chance plus blank spectrograms say nobody else can.

**Decomposition (F31).** Test three comparisons separately, because a single AUC only says "something is wrong":
- reference (declared-law draw) vs neutral (a non-payload draw of the codec) → model mismatch;
- neutral vs stego → embedding mismatch;
- reference vs stego → the claim.
Once the coding is measure-preserving over a uniform payload, embedding mismatch is ≈ 0 by construction, so the claim collapses onto model mismatch: whether the trained flow reproduces the declared floor. The residual risks are that model mismatch, low-bit realism (F34), and finite-precision coding error, all measurable by the R5 battery.

## 2. LOCKED RULES — non-negotiable, each proven by a failure

L1–L12 are retained as the record of lessons. Several (L9, L10, L11) bind the retired phase-coding channel; they remain true but are superseded as the main channel by the integer-PCM carrier (F30). L1's single-file intent is now met a different way: reveal is a deterministic decode from the file, and fresh randomness is consumed at conceal (F36), not sampled at reveal.

| # | Rule | Proof |
|---|------|-------|
| L1 | Reveal runs from fresh sampled z, never the real residual r. Storing r = two-file trap = not steganography. (Now: no stored residual; reveal decodes the file, fresh randomness is at conceal, F36/L20.) | real-r err 0.0 vs random-z err 0.80 (24 Jun) |
| L2 | L_z Gaussian prior on r is mandatory when a flow with a residual is in the loop. | 24 Jun zero-loss run (all losses 0.0000 from epoch 1) |
| L3 | spec_corr / checksum is the verdict metric. Reveal loss alone lies. | v5: err 0.064 looked fine, spec_corr 0.003 = noise |
| L4 | One axis at a time. Never stack multipliers. | 91s scrambled flatline vs 4s converging to 0.003 |
| L5 | float32, AMP off, on any training path. No dead GradScaler. | precision for sub-threshold work |
| L6 | Discussion/design before code. Direct verdicts, no dressing up failures. | working method |
| L7 | Git tags freeze phases, not archive folders. Phase 1 tag: `phase1-coupling-inn-frozen`. | repo practice |
| L8 | Any salience/stratum split must be derivable from the stego itself. A shipped map = two-file trap (L1). | 2 Jul design session |
| L9 | The decisive round trip is STFT → iSTFT → STFT, not disk read/write. (Context: binds the phase-coding channel; the integer carrier F30 avoids the projection entirely.) | this chat, 24 Jul |
| L10 | Carrier selection must be fixed / key-seeded, independent of the values modulated. | this chat, 24 Jul |
| L11 | Phase in a near-zero-magnitude bin has no stable meaning; carrying phase means adding floor-level magnitude, so F1 and F3 are the same operation. (Context: dissolved under synthesis; magnitude and phase are jointly generated, not perturbed.) | this chat, 24 Jul |
| L12 | "It worked" requires BOTH proofs of §1. Neither alone. | this chat, 24 Jul |

Added at the H-007 pivot:

| # | Rule | Proof / ground |
|---|------|----------------|
| L13 | The final stego is GENERATED, not modified. No privileged original cover, no meaningful payload residual. | H-007; MEC (14), DPL-COT (17) |
| L14 | Integer samples are authoritative. Float transforms may train critics; they must not determine bit-exact conceal or reveal. | integer-exactness; IDF (9), Fanelli (18) |
| L15 | Capacity comes from the floor's entropy rate, not an STFT-bin count. | Ziegler/Sallee: H(q) is the bound (16, 22) |
| L16 | Separate model mismatch from embedding mismatch. Always evaluate reference/neutral, neutral/stego, reference/stego. | Fanelli codelength decomposition (18) |
| L17 | Name the cover distribution. "Ambient silence" without a full specification is not an experimental population. Here it is DECLARED SYNTHETIC (F35), committed. | H-007; DPL-COT (17) |
| L18 | Message-randomisation assumptions are explicit; compression, encryption, random padding, and homophonic coding are not interchangeable. Encryption-to-uniform (F15) is load-bearing for the distribution match. | Meteor (15), DPL-COT (17) |
| L19 | If a trained model is used, the neutral generator must pass reference-vs-neutral before any payload training. A detectable neutral floor cannot be made secure by adding a decoder loss. | design |
| L20 | The same payload must produce a different stego file each run (fresh conceal randomness, F36), disposable without side information. | H-007; single-file constraint |

The map is a trained flow (D-MODEL resolved), so L16 and L19 bind in full: model mismatch is a real, measurable quantity and the neutral generator must pass reference-vs-neutral before any payload training.

## 3. CURRENT PLAN + GATES (R0–R7)

Every gate has a pass/fail criterion written BEFORE the run. A gate is passed only when its criterion, as written here, is met. Moving a criterion after seeing results is forbidden. This replaces the old Phase 0/A/B/C/D/E.

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

## 4. OPEN DECISIONS — resolve, do not let them rot

- **D-COVER — RESOLVED (24 Jul).** Cover is defined synthetic silence (F35). Matched-recorder claim deferred to the *Silent Signal* companion project.
- **D-FLOAT/EXPORT — RESOLVED.** 24-bit PCM, no dither, channel count declared in R0 (mono default). Committed in the §8 spec. 16-bit is excluded: its LSB sits near −96 dBFS and would destroy the floor.
- **D-THESIS — RESOLVED.** The concept is machine perception: the trained flow is the only object that can read a produced file. Security is provable (a payload-selects-output map is perfectly secure exactly when it is a coupling; refs 14, 16) and rests on the learned weights themselves, not on a key or on the secrecy of the algorithm. No key is used. Anyone holding the exact trained weights can read the file, which is the intended stance for a work about machine perception; privacy on top would be an optional add-on and is out of scope.
- **D-MODEL — RESOLVED: fully learned, integer-reversible flow.** The map is a trained normalising flow, not an analytic sampler. Learning carries the whole system: the flow both models the floor and folds the message into a valid floor draw reversibly. The integer-reversible form (F20/F30) is required, because a plain floating-point flow would not invert bit-exactly and the sub-threshold payload cannot survive inverse error. The coding steps around the flow (whiten, inverse-CDF, checksum) are exact, deterministic, and keyless; the intelligence is in the weights.
- **D-COLOUR — OPEN.** The declared PSD / spectral shape is unset, pending R1/Phase 0 measurement of what reads cleanest (flat, or a gentle low-frequency tilt).
- **D-HYPHEN — OPEN (minor).** Write-up hyphenation of "time-frequency" / "encoder-decoder"; plain hyphen used pending decision.
- **F26 fingerprinting/misdirection — OPEN.** Origin seed idea, under-documented; write 2–3 lines so it is not lost.

## 5. IDEAS — pointer

The full register (F1–F38, statuses, leads, grounding) is in `IDEAS.md`. Current build-driving ideas:

- Lead 10: F3 (floor as the target distribution), F18 (grayscale), F20 (integer-reversible carrier), F25 (generative/transport reframe, now governing), F29 (reverse codec), F30 (integer PCM backbone), F31 (detector decomposition + instrument), F32 (named distribution, synthetic committed), F35 (silence defined).
- Lead 9: F15 (encryption-to-uniform, resurrected, load-bearing), F33 (distribution matcher), F34 (bit-plane/ADC realism), F36 (fresh-randomness fill).
- Ablation / exhibition, kept but off the main line: F1 (phase-coding baseline), F37 (spread-spectrum develop-in-spectrogram), F38 (Fork-A as display).

## 6. ENVIRONMENT — a lever, not a fixture

If a run is blocked purely by hardware, escalate compute (rent A100/H100 by the hour) rather than shrink the experiment. "Binding on the 2080" describes the current machine, not a limit.

Current machine (reproducibility only): Windows laptop, RTX 2080 Max-Q 8.6 GB, CUDA 12.9, PyTorch 2.5.1+cu121, Python 3.11.6, float32 / AMP off. Note the codec's conceal/reveal path is integer and deterministic (L14); floats appear only on any training/critic path.
Repo `C:\Users\tessa\Dropbox\GITHUB\Athena_Noctua_Steg_INN_ODE` → `src/`, `data/`, `docs/`, `outputs/`, `models/`. `coupling_inn.py` belongs to frozen Phase 1. Next artifact: `oracle_distribution_codec.py` (R2). Files: `AN_30sec_raw_cover_v2.aif` (owl, retired), `moloch_secret_30s.wav`. Verification: Sonic Visualiser plus the R5 detector battery. Write-up style: neutral, plain, per the Wikipedia AI-tells guide.

## 7. REFERENCES — pointer

Full list (refs 1–25, with verification status) is in `IDEAS.md`. Anchors for the current build: MEC / perfectly secure steganography (14), Meteor (15), Neural Linguistic Steganography (16), DPL-COT (17), Physics-Aware Arithmetic Coding (18), Integer Discrete Flows (9), WaveNet (19), Classifier Two-Sample Tests (20), Cachin (21), Sallee (22). Fridrich & Goljan (6) still grounds the noise-mimicking pivot.

## 8. COVER — Silence specification (defined synthetic)

**Definition.** The cover is a defined synthetic noise floor: a low-amplitude, sign-symmetric signal specified by the parameters below and instantiated by drawing a sample that satisfies them. It is constructed, not recorded. Perceptually it reads as nothing on a normal listen and on a standard magnitude spectrogram; structure is audible only under extreme gain.

**Sample statistics.**
- Zero mean; no DC offset.
- Sign-symmetric distribution about zero (positive and negative sample values in equal measure).
- Samples represent air-pressure deviation about the ambient level.

**Parameters.**

| Property | Definition | Setting |
|---|---|---|
| Level | RMS amplitude of the floor | ≈ −80 dBFS |
| Colour | Power spectral density / spectral shape | Declared shape; UNSET pending Phase 0 (D-COLOUR) |
| Low-bit behaviour | Statistics of the least-significant bits per sample | Explicitly specified, not uniform-random (F34) |
| Stationarity | Time-variation of the statistics | Stationary, or a declared slow drift |
| Format | Container and quantisation | 24-bit PCM, no dither, declared channel count (mono default) |

**Format rationale.** The payload occupies structure far below the threshold of hearing. The pipeline is lossless end to end so that structure is preserved. Bit depth is 24-bit; 16-bit quantisation places the least-significant bit near −96 dBFS and would destroy the floor.

**Success criterion.** The floor is fully determined by the parameters above. A generated file is required to be statistically indistinguishable from an independent draw of the same declared distribution. No comparison against an external recording applies; none exists.

**Scope note.** This is the digital, defined case. Real recorded silence, and silence transmitted as an actual acoustic signal, are the subject of the forthcoming companion project *Silent Signal* and are out of scope here.
