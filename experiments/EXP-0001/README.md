# EXP-0001 — Getting the secret into the stego, not the r stream

- **Date:** 2026-07
- **Status:** worked
- **Code:** before restructure (train.py v4)

## Question

Does the coupling INN actually hide the image in the stego, or is it storing it in the redundant r stream that the hide produces and handing it back at reveal? Can single-file hide-and-reveal work at all, where only the stego is kept?

## Setup

Starting point was a clean pair: a fresh 30-second sparse secret (moloch_secret_30s, an outline painted into high frequencies) and the 30-second owl cover, time-matched. The training script in place was the "keep r as key" version, which revealed using the real r and saved r as a second file. That is two-file steganography wearing a single-file label, and it produced a perfect-looking recovery that meant nothing.

The fix had three parts, applied together. Reveal from a freshly sampled z rather than from r, so r is never available at reveal. Add a loss term pushing r toward Gaussian noise, so it cannot be used as storage. Remove the sample scrambling from the pipeline. Eight coupling blocks, full precision (AMP off, since the secret lives in small values), 400 epochs, secret at full scale.

Verdict metric was the random-z reveal error, the error when the reveal is fed noise in place of r. Under the old scheme this sat near 0.80, meaning the reveal from the stego alone was noise.

## What happened

Random-z reveal error dropped from 0.80 to 0.0157. For the first time the recovered file showed Blake in the spectrogram when revealed from the stego alone, with no side file. Stego versus owl SNR came in around 14.9 dB.

The stego was clearly audible. A whirring layer sat over the owl recording, present through the whole 30 seconds.

## Verdict

Worked, with a caveat. This was the first run where the secret genuinely lived in the stego and could be pulled back out of the stego by itself. The concealment was audible though, so it was a working hide-and-reveal rather than a usable stego.

## Why

The earlier failure was the network taking the easy path: dump the image into r, which is handed back at reveal, and leave the stego clean. Constraining r toward Gaussian noise and revealing from a fresh z closed that path, so the only place left to carry the image was the stego.

The audibility had a separate, spectral cause. The owl holds all its energy below about 900 Hz. The secret, placed high so the network could separate it cleanly, holds 74% of its energy above 9 kHz. With no shared band, the owl cannot mask the image, and the added signal is exposed.

## What this changed

Fixed the training setup that every later run built on: reveal from sampled z, Gaussian prior on r, no scrambling. Confirmed the coupling INN can hide and reveal in principle. Surfaced the next problem, audibility from spectral non-overlap, which set up the hiding-depth work in EXP-0002.
