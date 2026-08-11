# ATHENA NOCTUA — DECISIONS

**Why the major choices were made.** One entry per decision that would be expensive to reverse. This is the file that answers "why is it like this?" six months later, and the file a reader of the write-up will want.

Last updated: 29 July 2026 (LOG H-010).

HOW THIS FILE WORKS:
1. A decision gets an ID (`D-NAME`) and keeps it forever. Statuses change; IDs and rows do not.
2. Status is OPEN or RESOLVED. A RESOLVED decision can be reopened — add a new dated block underneath the old one, marked SUPERSEDES, and leave the original visible. Reversals are part of the record.
3. Every RESOLVED entry names the LOG entry that committed it. If a decision is not in the LOG, it did not happen.
4. Small decisions do not belong here. If it can be undone in an afternoon, it is a note in `LOG.md`.

Entry format: **Question → Decision → Why → Consequences → Status**.

---

## RESOLVED

### D-ARCH — What kind of system is this?
- **Question.** Modify selected coefficients of an existing cover, or generate the whole file from a learned distribution?
- **Decision.** Distribution-preserving **cover synthesis** (F29). The stego file *is* a sampled draw of a declared noise floor whose coordinates encode the payload. There is no cover, no residual, no salience map, and nothing sits "under" anything.
- **Why.** It attacks the correct statistical problem — equality of distributions rather than stealth of a delta — and it is provably secure rather than empirically secure: a payload-selects-output map is perfectly secure exactly when it is a coupling (minimum-entropy-coupling theorem, ref 14; Cachin, ref 21). The security bar is set at **Level 3**: indistinguishable from a genuine draw of the declared floor to *any* distinguisher, not "beats the one detector we trained".
- **Consequences.** Promotes F3, F6, F20, F25, F30, F31; resurrects F15 as load-bearing; demotes the phase-coding channel F1 to an ablation; makes L13 ("the final stego is GENERATED, not modified") a locked rule. Capacity now comes from the floor's entropy rate, not from an STFT bin count (L15). The whole security claim rests on model fidelity, which is why the reference/neutral/stego decomposition (F31, L16) is mandatory rather than optional.
- **Status.** RESOLVED 24 Jul 2026 — LOG H-007.

### D-COVER — What is the cover?
- **Question.** Keep the tawny owl recording as cover? And if not, is the replacement a *matched real recorder* or a *defined synthetic* silence?
- **Decision.** Owl retired (23 Jul). Cover is **defined synthetic silence** (F35): a specified zero-mean, sign-symmetric noise floor at roughly −80 dBFS RMS, 24-bit PCM, with declared amplitude law, low-bit behaviour and stationarity. Colour/PSD declared but unset (see D-COLOUR). Not a matched real recorder.
- **Why.** "Ambient silence" is not one distribution, and an unnamed cover distribution is not an experimental population (L17). Declaring the law collapses the model-fidelity problem: the declared distribution *is* the target, so the claim becomes "indistinguishable from a fresh draw of this declared silence", which is testable without any external recording. The matched-recorder version is roughly ten times harder at gate R3.
- **Consequences.** Closes the F32 fork on the synthetic side. There is no corpus to collect; R1 builds an exact reference sampler instead. Real recorded silence and acoustically transmitted silence move to the companion project *Silent Signal*, taking F7, F8, F9 and F10 with them.
- **Status.** RESOLVED 23–24 Jul 2026 — LOG H-005, H-007.

### D-CARRIER — What is the authoritative signal domain?
- **Question.** Complex STFT, or integer PCM?
- **Decision.** The carrier is **24-bit signed integer PCM through an integer-to-integer reversible transform** (F30, the concrete form of F20). The complex STFT (F4) is retained as observer and critic domain only, never on the conceal/reveal path.
- **Why.** An integer path removes two failure modes at once: the STFT consistency projection that leaks phase into magnitude (L9), and float non-determinism. Recovery becomes bit-exact by construction rather than by error correction. Integer-CDF arithmetic coding is both Shannon-optimal and exactly invertible (ref 18).
- **Consequences.** L14 locked: integer samples are authoritative, floats may train critics but must never determine conceal or reveal. Kills F13 (overcomplete STFT redundancy) permanently. Makes F16 (error-correction) probably unnecessary. Requires deterministic integer CDFs on the coding path and exactly invertible block-edge handling.
- **Status.** RESOLVED 24 Jul 2026 — LOG H-007.

### D-FLOAT/EXPORT — What is the file format?
- **Question.** Bit depth, dither, channel count.
- **Decision.** 24-bit PCM, no dither, no normalisation, no limiter, mono by default; WAV PCM_24 with no secondary chunks. The payload lives only in sample values.
- **Why.** 16-bit places the least-significant bit near −96 dBFS, which would destroy a floor sitting at −80 dBFS. Dither would add uncontrolled randomness on top of a distribution the whole claim depends on specifying exactly.
- **Consequences.** Fixes gate R7. Removes any metadata-dependent decoding route.
- **Status.** RESOLVED 24 Jul 2026 — LOG H-006, H-007.

### D-THESIS — Does concealment rest on a key, or on the model?
- **Question.** Is there a secret key, or is the trained model itself the secret?
- **Decision.** **No key.** The concealment map is the trained flow. Its weights are the exact invertible map and the only object that can read a produced file. Whitening is retained but is public and keyless — it exists to make the bitstream uniform, not to keep anything secret.
- **Why.** The concept of the work is machine perception, and a key would make the piece about cryptography instead. Security is still provable: a payload-selects-output map is perfectly secure exactly when it is a coupling (refs 14, 16), and that property does not depend on key secrecy. Anyone holding the exact weights can read the file, which is the intended stance.
- **Consequences.** Privacy is explicitly out of scope; an encryption layer would be an optional add-on. Whitening (F15) stays load-bearing for the *distribution match*, not for secrecy — uniformity of the payload is what makes the latent match its prior, which is what makes the stego match the floor. Fresh randomness at conceal (F36) is retained, so the same image yields a different valid file every run.
- **Status.** RESOLVED 28 Jul 2026 — LOG H-008.

### D-MODEL — Analytic sampler, or learned model?
- **Question.** Is the concealment map hand-derived from the declared distribution, or learned?
- **Decision.** **Fully learned**: a single integer-reversible normalising flow, trained by maximum likelihood to model the declared floor. Not an analytic sampler.
- **Why.** Learning carries the whole system — the flow both models the floor and folds the message into a valid draw of it, reversibly. The integer-reversible form is not a preference but a requirement: a floating-point flow will not invert bit-exactly, and a sub-threshold payload cannot survive inverse error.
- **Consequences.** Model mismatch becomes a real, measurable quantity, so L16 and L19 bind in full: the neutral generator must pass reference-vs-neutral (gate R3) before any payload is folded in. A detectable neutral floor cannot be rescued by adding a decoder loss. The coding steps around the flow — whiten, inverse-CDF, checksum — stay exact, deterministic and keyless; the intelligence is in the weights.
- **Status.** RESOLVED 28 Jul 2026 — LOG H-008.

### D-REPO — How is the project laid out?
- **Question.** Where does each kind of writing live?
- **Decision.** Four registers in `lab/` (STATE, LOG, DECISIONS, PLAN, IDEAS), the written argument in `docs/{concept,method,related_work}`, one folder per run in `experiments/`, a flat `src/athena/` package, and a gitignored `runs/` for machine output. The old `outputs/` folder is deleted.
- **Why.** The previous layout let one folder serve as artefact store, evidence store and memory at once, so nothing in it could be trusted or thrown away. Separating disposable machine output (`runs/`) from written evidence (`experiments/`) makes both usable: `runs/` can be deleted at any time without losing the record.
- **Consequences.** Phase-1 audio is now untracked and disposable by design; the record of Phase 1 is H-001–H-004 plus the EXP write-ups. STATE §3 and §4 become pointers to PLAN and this file. A subpackage layout for `src/` (flow/crypto/embedding/audio/evaluation) was considered and rejected as premature — promote a module to a folder only when it genuinely needs three files.
- **Status.** RESOLVED 29 Jul 2026 — LOG H-010.

### D-COMPRESS — Is the payload losslessly compressed before whitening?
- **Question.** `PIPELINE.mermaid` C4/R8 carry a lossless compression stage; FORMULATION §6 omitted it. Keep or drop?
- **Decision.** Keep. Compression sits between checksum and whitening, with the checksum computed over the declared object before compression.
- **Why.** It reduces $m$ only; it does not affect $Q$, since freed capacity is taken by fresh randomness $r$ (C.1) and both streams are uniform. It is therefore capacity headroom, retained against the possibility that R1 measures the canonical object large relative to $N$. It does no uniformity work — W.1 is $W$'s job, and L18 forbids treating the two as interchangeable.
- **Consequences.** $C$ and $C^{-1}$ enter the bit-exact recovery contract as R.5: the format must be declared and frozen, pinned in `MODEL_CARD.md` alongside $\theta$. The concrete form of $C$ is set at R2. Revisit if R1 shows the payload well inside the 10% operating point, in which case the component earns nothing and can be removed.
- **Status.** RESOLVED 11 Aug 2026 — LOG H-0XX.
---

## OPEN

### D-COLOUR — What is the declared spectral shape?
- **Question.** What PSD / colour does the declared floor have: flat, or a gentle low-frequency tilt?
- **Blocking.** Gate R1. Everything downstream refers to it, so it cannot stay unset past R1.
- **How it gets decided.** Phase 0 / R1 measurement of what reads cleanest — generate candidates, inspect on linear, log and high-gain spectrograms, and choose. This is a listening-and-looking decision as much as a statistical one, and it is legitimate for it to be.
- **Status.** OPEN.

### D-F26 — What was the fingerprinting / misdirection idea?
- **Question.** F26 is the origin idea that preceded the steganography build, and it is not documented anywhere reachable.
- **Blocking.** Nothing technical. It blocks the write-up's lineage section, and it decays every week it stays unwritten.
- **How it gets decided.** Tessa writes 2–3 lines from memory into the F26 row of `IDEAS.md`. Not a research task.
- **Status.** OPEN.

### D-HYPHEN — Write-up hyphenation (minor)
- **Question.** "time-frequency" or "time–frequency"; "encoder-decoder" or "encoder–decoder".
- **Status.** OPEN. Plain hyphen used throughout pending a decision. Settle it once, at write-up, with a find-and-replace.
