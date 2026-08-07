# EXP-0003 — [alpha sweep]

- **Date:** 2026-07
- **Status:**  failed 
- **Code:** before restructure (train.py v5 through v8, coupling_inn_det.pt)

## Question
Can hyperperameter, depth alpha, get the coupling INN to both inaudible and recoverable at the same time? And if not, is the random z at reveal the thing holding recovery back?

## Setup
Cover: AN_30sec_raw_cover_v2.aif (owl, all energy below ~900 Hz). Secret: moloch_secret_30s.wav (sparse, 74% of energy above 9 kHz). 8 coupling blocks, no scrambling, reveal from sampled z, Gaussian prior on r.

Alpha scales the secret down before embedding and back up at reveal, so a smaller alpha means a quieter added signal. Swept alpha over 0.5, 0.2, 0.1 at 120 epochs each (v7), then a single follow-up at alpha = 0.1 with the random z at reveal replaced by a fixed zero, a deterministic decode, at 200 epochs (v8). Verdict metric was spectrogram correlation between recovered and original, which is scale-free. Reveal error alone was discarded as misleading on a sparse target.

## What happened
The sweep recovered nothing. Spectrogram correlation stayed near zero at every alpha (-0.003, -0.014, -0.002), and the reveal error held at ~0.065 across a fivefold change in amplitude. A constant error that ignores signal scale is a fixed noise floor. The added signal did get quieter as expected, down to -50.7 dBFS at alpha = 0.1.

A follow-up with deterministic zero reveal is written up separately as EXP-0004

## Verdict
nope.Alpha on its own cannot deliver inaudible and recoverable together. The only amplitude where the image survived was alpha = 1, loud enough to whir. The random z was part of the wall and removing it helped the concealment a lot and the recovery a little, but a second wall sits behind it. The coupling INN cannot finish this task.

## Why
Two causes. First, the random z at reveal injected a fixed noise floor of about 0.065 in image terms, independent of alpha, so as the signal got quieter it dropped below the floor. That z is a WavInWav device for surviving MP3 and resampling, and this pipeline has neither, so it was pure cost. Removing it cleared that floor.

Second, and the real limit: the coupling blocks operate sample by sample in the time domain with small 1-D convolutions. They have no mechanism to move energy from Blake's 15 kHz band into the owl's sub-900 Hz band and back. With the two signals never sharing a band, there is no masker where the secret lives and no learned route down to one. The flat 0.09 reveal loss is a network with no way to represent the answer, not one short on training. This is why the deterministic fix stalled at +0.05.

## What this changed
Concealment is now solved and no longer the open question: -75.9 dBFS is inaudible with margin. The failure is isolated to the reveal, and specifically to the architecture, on measured evidence rather than a hunch. Deterministic zero reveal replaces random z going forward, since there is no channel that needs the noise. Spectrogram correlation is now the standard verdict metric. The next branch moves hiding into the frequency domain (STFT in, iSTFT out) so the network can place the secret inside the owl's occupied bands, with a stereo L minus R side-channel as the alternative.