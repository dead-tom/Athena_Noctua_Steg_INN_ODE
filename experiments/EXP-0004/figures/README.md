# EXP-0004 — Deterministic reveal, and the wall that forced a redesign

- **Date:** 2026-07
- **Status:** failed
- **Code:** before restructure (train.py v8, coupling_inn_det.pt)

## Question

EXP-0003 found a fixed noise floor sitting under the reveal, independent of alpha, and pointed at the random z drawn at reveal as the cause. With that random z replaced by a fixed zero, a deterministic decode, does the reveal recover Blake when the signal is buried quiet? And if it still fails, is the reveal fixable inside the coupling INN, or is the architecture itself the limit?

## Setup

Replaced the random z at reveal with a fixed zero, so the decode is deterministic and no noise is injected. Ran at alpha = 0.1 for 200 epochs, with spectrogram correlation printed every 40 epochs to watch the reveal form. Everything else held from before: eight coupling blocks in the time domain, small 1-D convolutions, no scrambling.

The direct comparison is the alpha = 0.1 run from EXP-0003, which gave spectrogram correlation -0.002 with the random z. Only the reveal noise changed.

## What happened

Two numbers moved. The added signal dropped a further 25 dB, from -50.7 dBFS to -75.9 dBFS, inaudible by a wide margin. Spectrogram correlation rose off the floor, climbing from -0.002 to +0.050 over the run.

The reveal loss sat at about 0.09 and never came down, flat from the first epoch through all 200.

## Verdict

Failed as a recovery, decisive as a diagnosis. Removing the random z helped the concealment a great deal and the recovery only a little. Blake is still not readable at +0.05. The reveal cannot learn inside this architecture, and that is now measured rather than guessed.

## Why

A reveal loss that is flat from the first epoch means the network has no way to represent the answer. More epochs would not help. The coupling blocks work sample by sample in the time domain with small 1-D convolutions, and nothing in them can carry energy from the secret's 15 kHz band down into the owl's sub-900 Hz band and back. The image stays stranded up high, where there is no owl to hide under and no learned route to a band where there is. Removing the random z cleared the EXP-0003 floor, which then exposed this deeper structural limit underneath it.

## What this changed

This is the run that turned the project toward a redesign. Concealment is now solved and closed as a question at -75.9 dBFS. The remaining failure is architectural, on measured evidence. The next branch moves to a continuous flow (a Neural ODE, for a more expressive invertible transform than fixed discrete blocks) and to frequency-domain hiding (STFT in, iSTFT out), so the network can place the secret inside the owl's occupied bands instead of above them. Deterministic zero reveal stays, since there is no channel that needs the noise. Spectrogram correlation remains the verdict metric.
