# Experiments

One folder per experiment. Failures are recorded the same as successes —
knowing what doesn't work is the more useful half of this table.

| ID | Date | Question | Status | Takeaway |
|----|------|----------|--------|----------|
| [EXP-0001](EXP-0001/) | 2026-06-24 | Does the secret hide in the stego, or in the discarded r stream? | worked | Reveal-from-z plus a Gaussian prior on r forced the image into the stego; random-z error fell from 0.80 to 0.0157. Readable, but audible. |
| [EXP-0002](EXP-0002/) | 2026-06 | Can scaling the signal down (alpha) make the stego inaudible and still recover? | partly worked | Inaudible at -47.8 dBFS, but the reveal was noise. A low reveal error was a false positive, caught by spectrogram correlation. |
| [EXP-0003](EXP-0003/) | 2026-06 | Is there an alpha that is both inaudible and recoverable? | failed | No. Reveal error held near 0.065 across a fivefold amplitude range, a fixed floor. Only alpha = 1 survived, and it whirred. |
| [EXP-0004](EXP-0004/) | 2026-06 | Does a deterministic zero reveal fix recovery, or is the architecture the limit? | failed | Concealment reached -75.9 dBFS but reveal loss stayed flat at 0.09. Time-domain coupling can't move energy between bands. Forced the redesign. Claude really really didnt want to...noted|

**Next ID:** EXP-0005