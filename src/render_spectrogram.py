"""
render_spectrogram.py  --  Athena_Noctua_Steg_INN_ODE
Turn the Blake drawing into the SECRET audio: paint the image into a spectrogram
and synthesise it as sound. Wide band (fills the frame), but SPARSE content
(strong edges only) so there is less information for the hide to carry.

  source : data/raw/Moloch_Drawing_07_1024h.png   (white figure on black)
  output : data/Generated/moloch_secret_30s.wav    (30 s, image fills the whole clip)
"""

from PIL import Image
import numpy as np
import soundfile as sf
import os

# ---- CONFIG ----------------------------------------------------------
INPUT_PNG  = r"data\raw\Moloch_Drawing_07_1024h.png"
OUTPUT_WAV = r"data\Generated\moloch_secret_30s.wav"

sr        = 48000
duration  = 30.0            # image fills the whole clip, no silent intro/outro
fmin, fmax = 100.0, 22000.0 # wide band (the full-frame look you liked)
fft_window = 2048           # snap partials to FFT bin centres -> crisp lines

invert_image = False        # white-on-black source: bright = signal
threshold    = 0.45         # HIGHER than before -> keeps only strong edges (sparser)
gamma        = 0.7
auto_crop    = True
# ----------------------------------------------------------------------

os.makedirs(os.path.dirname(OUTPUT_WAV), exist_ok=True)   # auto-create data\Generated

img = Image.open(INPUT_PNG).convert("L")          # greyscale
a = np.asarray(img).astype(np.float32) / 255.0
if invert_image:
    a = 1.0 - a
if auto_crop:
    m = a > threshold
    r = np.where(m.any(axis=1))[0]; c = np.where(m.any(axis=0))[0]
    a = a[r.min():r.max()+1, c.min():c.max()+1]
a = np.clip((a - threshold) / (1.0 - threshold), 0.0, 1.0) ** gamma

# partials snapped to FFT bin centres inside the band
bin_hz = sr / fft_window
klo, khi = int(np.ceil(fmin/bin_hz)), int(np.floor(fmax/bin_hz))
freqs = np.arange(klo, khi+1) * bin_hz
nrows = len(freqs)
img2 = Image.fromarray((a*255).astype(np.uint8)).resize((a.shape[1], nrows), Image.BILINEAR)
arr  = np.flipud(np.asarray(img2).astype(np.float32)/255.0)   # row0 -> lowest freq
width = arr.shape[1]

n = int(sr*duration)
t = np.arange(n)/sr
col = np.minimum((t/duration*width).astype(int), width-1)
phases = np.random.rand(nrows)*2*np.pi
env = np.sin(np.linspace(0, np.pi, n))**2          # gentle fade in/out

audio = np.zeros(n, dtype=np.float32)
chunk = 8192
for s in range(0, n, chunk):
    e = min(s+chunk, n)
    amp = arr[:, col[s:e]]
    audio[s:e] = (amp*np.sin(2*np.pi*np.outer(freqs, t[s:e]) + phases[:, None])).sum(0)
audio *= env
audio /= (np.abs(audio).max() + 1e-12)

sf.write(OUTPUT_WAV, audio, sr, subtype="PCM_24")
energy = (arr > 0.05).mean()
print(f"saved {OUTPUT_WAV} | {duration}s | band {freqs[0]:.0f}-{freqs[-1]:.0f}Hz "
      f"| {nrows} partials | active pixels {100*energy:.1f}% (lower = sparser)")