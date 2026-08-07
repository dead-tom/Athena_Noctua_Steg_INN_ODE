# EXP-0002 — [Hiding depth for inaudibility, and a false positive]
- **Date:** 2026-07
- **Status:** partly worked
- **Code:** before restructure (train.py v5, diagnose_reveal.py)

## Question

The pipeline is fully digital, with no compression and no microphone in the loop, so the image never has to survive a perceptual channel. It can sit below the threshold of hearing instead of underneath a louder sound. Can the stego be made inaudible by scaling the added signal down, and does the reveal still recover Blake once it is that quiet?

## Setup

Added a depth control, alpha, that scales the secret down before embedding and back up at reveal. A smaller alpha means a quieter added signal. Ran at alpha = 0.05, keeping the EXP-0001 setup otherwise (reveal from sampled z, Gaussian prior on r, no scrambling, 8 blocks, full precision).

Reported the added signal level in dBFS as a concealment readout. The reveal was checked first by reveal error, then re-checked with a dedicated diagnostic (diagnose_reveal.py) that computes spectrogram correlation between recovered and original, plus a peak-to-rms ratio to catch a single dominating spike.

## What happened

At alpha = 0.05 the added signal fell to -47.8 dBFS and the whir was gone. On its own the stego sounded like the clean owl.

The reveal error read 0.064, which looked acceptable, and the run was briefly taken as a full success. The diagnostic overturned that. Spectrogram correlation came back at 0.003, meaning the recovered file had no relation to Blake. Peak-to-rms was 552, meaning one spike had dominated the peak-normalised saved file and hidden the fact that everything else was noise.

## Verdict

Partly worked. The concealment half succeeded: inaudible at -47.8 dBFS. The recovery half failed: the recovered file was noise, and the earlier apparent success was a false positive.

## Why

The reveal error was misleading because the secret is sparse, with its own average level around 0.05. An error of 0.064 against a signal that small is noise the size of the thing being measured, so a low-looking error meant nothing. Spectrogram correlation, which ignores scale, showed the real state.

The cause of the failed reveal itself, the random-z noise floor sitting under the reveal and the deeper architecture limit, was not yet isolated at this point. That came in EXP-0003.

## What this changed

Introduced alpha as the concealment control and dBFS as the concealment metric. Retired raw reveal error as a verdict on a sparse target and made spectrogram correlation the standard metric from here on. Added a working rule: do not call a run a success until the verdict metric and a picture you have actually looked at agree. Set up the systematic alpha sweep in EXP-0003.