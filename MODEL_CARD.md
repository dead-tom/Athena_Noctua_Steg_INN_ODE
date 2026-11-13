# Model Card — Athena Noctua

**Status: not yet trained.** The current model is specified but not built (see [`lab/PLAN.md`](lab/PLAN.md), gate R3). Training is paused pending a hardware rebuild.

| | |
|---|---|
| Model | Integer-reversible normalising flow, trained by maximum likelihood on draws of a declared synthetic silence |
| Purpose | Generates a 24-bit PCM file that is a draw of the declared silence and carries a payload; the same weights recover it bit-exact |
| Key | None. The weights are the only reader. |
| Training data | Reference draws of the declared silence. No recorded audio. |
| Declared silence | Zero-mean, sign-symmetric, ≈ −80 dBFS RMS, 24-bit PCM, mono. Colour/PSD TBC (D-COLOUR). |
| Weights θ | TBC |
| Compression format C | TBC (set at R2) |
| Evaluation | Checksum-exact recovery + detector ensemble AUC within the declared equivalence region (gates R2–R6) |
| Results | TBC |
| Limitations | TBC |

## Files in `models/`

`coupling_inn.pt` and `coupling_inn_det.pt` are Phase 1 checkpoints (time-domain coupling INN), frozen at tag `phase1-coupling-inn-frozen`. They are not the current model. See [`experiments/`](experiments/) EXP-0001 to EXP-0004.
