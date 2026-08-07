# ATHENA NOCTUA — STATE (living document)

Last updated: 29 July 2026 (repository restructure, LOG H-010).
Read order every session: this file top-to-bottom, then the tail of `LOG.md`, then `lab/PLAN.md` for the next action.
This file is EDITABLE. `LOG.md` is APPEND-ONLY. When they disagree, LOG is the record of what happened; STATE is the current interpretation.

**Where things live** (restructure of 29 Jul, H-010). This file holds current status, the claim, and the locked rules. It POINTS at the other registers rather than duplicating them:

| File | Question it answers |
|---|---|
| `lab/STATE.md` (this file) | What is currently true? |
| `lab/LOG.md` | What actually happened? (append-only) |
| `lab/PLAN.md` | What happens next? (R0–R7 gates in full) |
| `lab/DECISIONS.md` | Why were major choices made? (decision register) |
| `lab/IDEAS.md` | What should not be forgotten? (F1–F38, references) |
| `docs/concept/` | Why the project exists; what synthetic silence is |
| `docs/method/` | Architecture, mathematics, algorithms, methodology, evaluation |
| `docs/related_work/` | What has already been done |
| `experiments/` | One folder per run, failures included |
| `runs/` | Machine output. Untracked, disposable, never cited |

---

## 0. STATUS NOW

Architecture and cover both committed (LOG H-007, H-008). Repository restructured 29 Jul (H-010); no experimental claim, metric, or gate was altered by that work.

- **Cover:** defined synthetic silence (F35), a specified mathematical noise floor, not a recorded room and not a matched recorder. The named-distribution fork is closed on the synthetic side. Physical and acoustic silence is deferred to a forthcoming companion project, working title *Silent Signal*.
- **Architecture:** the reverse learned lossless codec (F29). The payload selects one valid draw of the declared floor. It is recovered bit-exact and is statistically indistinguishable from an ordinary draw of the same declared distribution. This is Level-3 security: nothing to detect, up to a measurable model gap, rather than "beats one trained detector".
- **Carrier:** integer-reversible transform over 24-bit PCM (F30/F20). No float STFT on the conceal/reveal path.
- **Retired / frozen:** owl cover retired (23 Jul). Phase 1 (1-D time-domain coupling INN) frozen at tag `phase1-coupling-inn-frozen`, proven unable to relocate energy between bands. The old phase-coding channel (F1) is demoted to an ablation.

**Route committed (D-MODEL resolved): fully learned, no key.** The concealment map is an integer-reversible learned flow (F20/F30 as the integer route for F29). A normalising flow is trained by maximum likelihood to model the declared floor; its weights are the exact invertible map between the floor and a simple latent, and those weights are the only object that can read a produced file. There is no encryption key and no stored side information. Whitening is retained but is a public, keyless step that only makes the bitstream uniform. Fresh randomness at conceal (F36) makes every encoding of the same image a different valid silence. See the pipeline diagram (`PIPELINE.mermaid`).

**Next single action:** the synthetic oracle codec (`oracle_distribution_codec.py`), gate R2. It proves the coding path (matcher plus integer transform plus checksum, survived across a file save and reload) before the flow is trained. See §3 R2/R3.

Cover specification is in §8. Committed idea stack: F3, F20, F25, F29, F30, F31, F32, F35 (target/architecture); F15, F33, F34, F36 (mechanism); F5, F18 (payload); F6/F31 (verdict instrument).

## 1. THE CLAIM — what "it worked" means (two proofs, both required)

> Migration note (H-010): this section is the source text for `docs/method/EVALUATION.md`. Copy it there when writing that document up; keep the short form here.

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

## 3. PLAN — pointer

The full R0–R7 plan, with every pass/fail criterion written before the run, now lives in `lab/PLAN.md`. It is not duplicated here. A gate is passed only when its criterion, **as written in PLAN.md**, is met; moving a criterion after seeing results is forbidden.

**Current position:** R0 and R1 not yet closed out in writing; the next single action is **R2**, the synthetic oracle codec (`oracle_distribution_codec.py`), which proves the coding path before the flow is trained. Phase 1 (the coupling INN) is frozen and outside this ladder.

## 4. DECISIONS — pointer

The full register, with the reasoning and consequences of each choice, lives in `lab/DECISIONS.md`. Status summary only, here:

| ID | Decision | Status |
|---|---|---|
| D-COVER | Cover is defined synthetic silence, not a matched recorder | RESOLVED 24 Jul |
| D-FLOAT/EXPORT | 24-bit PCM, no dither, mono default | RESOLVED 24 Jul |
| D-THESIS | Machine perception; security rests on the trained weights; no key | RESOLVED 28 Jul |
| D-MODEL | Fully learned integer-reversible flow, not an analytic sampler | RESOLVED 28 Jul |
| D-REPO | Repository and document structure | RESOLVED 29 Jul |
| D-COLOUR | Declared PSD / spectral shape | **OPEN** — pending R1 |
| D-HYPHEN | Write-up hyphenation (minor) | **OPEN** |
| D-F26 | Fingerprinting / misdirection: the origin idea, undocumented | **OPEN** — Tessa to write 2–3 lines | 
| D-DISTRIBUTION | The WAV is the artefact; published media is documentation | RESOLVED 30 Jul |
| D-WRITEUP | Repo-first, concept-led, technical strand visible | RESOLVED 30 Jul |

## 5. IDEAS — pointer

The full register (F1–F38, statuses, leads, grounding) is in `IDEAS.md`. Current build-driving ideas:

- Lead 10: F3 (floor as the target distribution), F18 (grayscale), F20 (integer-reversible carrier), F25 (generative/transport reframe, now governing), F29 (reverse codec), F30 (integer PCM backbone), F31 (detector decomposition + instrument), F32 (named distribution, synthetic committed), F35 (silence defined).
- Lead 9: F15 (encryption-to-uniform, resurrected, load-bearing), F33 (distribution matcher), F34 (bit-plane/ADC realism), F36 (fresh-randomness fill).
- Ablation / exhibition, kept but off the main line: F1 (phase-coding baseline), F37 (spread-spectrum develop-in-spectrogram), F38 (Fork-A as display).

## 6. ENVIRONMENT — a lever, not a fixture

If a run is blocked purely by hardware, escalate compute (rent A100/H100 by the hour) rather than shrink the experiment. "Binding on the 2080" describes the current machine, not a limit.

**Two machines, one repository.** Authoring, documents and repository work happen on the MacBook Pro (`~/Dropbox/GITHUB/Athena_Noctua_Steg_INN_ODE`). Training happens on the Windows laptop (`C:\Users\tessa\Dropbox\GITHUB\Athena_Noctua_Steg_INN_ODE`), RTX 2080 Max-Q 8.6 GB, CUDA 12.9, PyTorch 2.5.1+cu121, Python 3.11.6, float32 / AMP off. The codec's conceal/reveal path is integer and deterministic (L14); floats appear only on a training or critic path.

*Caution (added 29 Jul):* the repository lives inside Dropbox and is opened on both machines. Dropbox syncing a live `.git` directory while both machines are awake can corrupt the index. Work on one machine at a time, let the sync settle before switching, and if the repository ever reports a corrupt or locked index, stop and re-clone rather than repairing in place. Moving the repository out of Dropbox and pushing to a remote instead is the durable fix.

**Layout after the restructure (H-010):** `docs/{concept,method,related_work,figures}`, `lab/`, `experiments/`, `src/athena/` (flat package), `configs/`, `data/{raw,processed,generated}`, `models/`, `runs/` (gitignored), `media/`, `notebooks/`, `tests/`. The old `outputs/` folder is deleted; its contents are in `runs/` and are disposable.

`src/athena/coupling_inn.py` belongs to frozen Phase 1. Next artifact: `oracle_distribution_codec.py` (R2). Files: `data/raw/AN_30sec_raw_cover_v2.aif` (owl, retired), `data/generated/moloch_secret_30s.wav`. Verification: Sonic Visualiser plus the R5 detector battery. Write-up style: neutral, plain, per the Wikipedia AI-tells guide.

## 7. REFERENCES — pointer

Full list (refs 1–27, with verification status) is in `IDEAS.md`. Refs 26–27 were added on 29 Jul and are UNREAD — reading and integrating them is the first item of the next session. Anchors for the current build: MEC / perfectly secure steganography (14), Meteor (15), Neural Linguistic Steganography (16), DPL-COT (17), Physics-Aware Arithmetic Coding (18), Integer Discrete Flows (9), WaveNet (19), Classifier Two-Sample Tests (20), Cachin (21), Sallee (22). Fridrich & Goljan (6) still grounds the noise-mimicking pivot.

## 8. COVER — Silence specification (defined synthetic)

> Migration note (H-010): this section is the source text for `docs/concept/ON_SYNTHETIC_SILENCE.md`. Copy it there when writing that document up; keep the parameter table here.

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
