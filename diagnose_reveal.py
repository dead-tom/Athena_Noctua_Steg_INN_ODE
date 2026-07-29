"""
diagnose_reveal.py -- is Blake actually in the recovered file, or is it noise?
Correlation is the verdict and it is scale-free, so the peak-normalisation in
the export cannot fool it. Also renders a side-by-side spectrogram you can open.

Run:  python diagnose_reveal.py     (from the repo root)
"""
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, stft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REC    = r"outputs\recovered_secret_30s.wav"
SECRET = r"data\Generated\moloch_secret_30s.wav"
SR     = 48000
FRAME  = 16384


def load(path):
    x, sr = sf.read(path, always_2d=False)
    x = np.asarray(x, dtype=np.float64)
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        x = resample_poly(x, SR, sr)
    return x


rec = load(REC)
sec = load(SECRET)

n = (min(len(rec), len(sec)) // FRAME) * FRAME          # match trainer framing
rec, sec = rec[:n], sec[:n]
r = rec / (np.abs(rec).max() + 1e-12)
s = sec / (np.abs(sec).max() + 1e-12)

wave_corr = float(np.corrcoef(r, s)[0, 1])

_, _, Zr = stft(r, SR, nperseg=2048)
_, _, Zs = stft(s, SR, nperseg=2048)
spec_corr = float(np.corrcoef(np.abs(Zr).ravel(), np.abs(Zs).ravel())[0, 1])

peak_rms = np.abs(rec).max() / (np.sqrt((rec**2).mean()) + 1e-12)

print(f"samples compared:        {n:,}")
print(f"WAVEFORM correlation:    {wave_corr:+.3f}")
print(f"SPECTROGRAM correlation: {spec_corr:+.3f}   <-- THE VERDICT (matches what you see)")
print(f"   > 0.7  Blake recovered")
print(f"   < 0.3  reveal is noise")
print(f"recovered peak/rms:      {peak_rms:6.1f}   (>50 = a single spike is crushing the view)")

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, x, t in ((ax[0], s, "original secret"), (ax[1], r, "recovered")):
    f, tt, Z = stft(x, SR, nperseg=2048)
    a.pcolormesh(tt, f, 20*np.log10(np.abs(Z) + 1e-6), shading="auto", vmin=-120, vmax=0)
    a.set_title(t); a.set_ylabel("Hz"); a.set_xlabel("s")
plt.tight_layout()
plt.savefig("outputs/reveal_check.png", dpi=110)
print("\nsaved outputs/reveal_check.png -- open it: do the two panels match?")
