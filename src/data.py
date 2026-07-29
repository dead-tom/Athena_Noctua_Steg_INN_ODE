"""
data.py  --  Athena_Noctua_Steg_INN_ODE
Shared data pipeline (architecture-agnostic): load cover + secret, resample,
mono, normalise, optionally scramble the secret, and chunk into fixed frames.

Design notes for this project:
- Sample rate stays at 48 kHz. The secret is an image painted into HIGH
  frequencies; downsampling would destroy it. Do not lower sr below 44.1k.
- The reveal is digital + 24-bit, so the secret can live in tiny perturbations.
- Scrambling is OFF for the baseline (use_scramble=False). Establish that
  hiding works on the clean secret first, then add scrambling back if wanted.
"""

import warnings
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly, stft

warnings.filterwarnings("ignore")        # silence harmless format notices


# ----------------------------------------------------------------------
def load_wav(path, target_sr=48000):
    """Load WAV/AIFF/FLAC -> mono float32 in [-1, 1] at target_sr."""
    x, sr = sf.read(path, always_2d=False)   # soundfile reads aiff, wav, flac...
    x = np.asarray(x, dtype=np.float64)
    if x.ndim > 1:                           # stereo -> mono
        x = x.mean(axis=1)
    if sr != target_sr:                      # resample if needed
        x = resample_poly(x, target_sr, sr)
        sr = target_sr
    peak = np.abs(x).max() + 1e-12
    return sr, (x / peak).astype(np.float32)


# ----------------------------------------------------------------------
def scramble(x, key):
    """Permute samples with a key (seed). Returns scrambled signal + index."""
    rng = np.random.default_rng(key)
    idx = rng.permutation(len(x))
    return x[idx], idx


def unscramble(y, idx):
    """Invert scramble() given the saved index."""
    out = np.empty_like(y)
    out[idx] = y
    return out


# ----------------------------------------------------------------------
def frame(x, frame_len):
    """Split 1-D signal into [B, frame_len] (drops the remainder)."""
    n = len(x) // frame_len
    return x[: n * frame_len].reshape(n, frame_len)


def unframe(frames):
    """Reassemble [B, frame_len] back into a 1-D signal."""
    return frames.reshape(-1)


# ----------------------------------------------------------------------
def energy_report(x, sr, name):
    """Print where a signal's spectral energy sits (sparse-high vs full-band)."""
    f, _, Z = stft(x, sr, nperseg=2048)
    p = (np.abs(Z) ** 2).mean(axis=1)
    c = np.cumsum(p) / p.sum()
    q = lambda v: f[np.searchsorted(c, v)]
    above9k = p[f >= 9000].sum() / p.sum()
    print(f"  [{name}] dur {len(x)/sr:5.1f}s | energy band "
          f"10%={q(.10):5.0f}Hz 50%={q(.50):5.0f}Hz 90%={q(.90):5.0f}Hz "
          f"| {100*above9k:4.1f}% of energy above 9kHz")


# ----------------------------------------------------------------------
def prep(cover_path, secret_path, sr=48000, seg_seconds=10.0,
         cover_start=0.0, secret_start=0.0, frame_len=16384, key=1234,
         use_scramble=True, loop_cover=True, verbose=True):
    """
    Returns a dict of numpy arrays + metadata, ready to convert to tensors.
      cover_frames, secret_frames : [B, frame_len]
      perm_idx                    : index to unscramble after reveal
                                    (identity arange when use_scramble=False)
      secret_clean                : the unscrambled secret, for loss reference
      meta                        : sr, frame_len, seg, B, key
    loop_cover: if the cover is shorter than the segment, TILE (loop) it to
      length instead of padding with silence (better for hiding than dead air).
    """
    sr, cover = load_wav(cover_path, sr)
    _,  secret = load_wav(secret_path, sr)

    seg = int(seg_seconds * sr)
    seg = (seg // frame_len) * frame_len          # whole frames -> lossless round-trip
    cs, ss = int(cover_start * sr), int(secret_start * sr)

    if loop_cover and len(cover) < cs + seg:      # tile the cover to length
        reps = int(np.ceil((cs + seg) / len(cover)))
        cover = np.tile(cover, reps)
    cover = cover[cs: cs + seg]
    secret = secret[ss: ss + seg]
    # pad if a segment still ran short
    cover = np.pad(cover, (0, max(0, seg - len(cover))))
    secret = np.pad(secret, (0, max(0, seg - len(secret))))

    if verbose:
        print("data prep:")
        energy_report(cover, sr, "cover ")
        energy_report(secret, sr, "secret")

    if use_scramble:
        secret_s, perm_idx = scramble(secret, key)           # KEY-LOCK the secret
    else:
        secret_s, perm_idx = secret, np.arange(len(secret))  # identity: no scrambling

    cover_f = frame(cover, frame_len)
    secret_f = frame(secret_s, frame_len)
    B = min(len(cover_f), len(secret_f))
    cover_f, secret_f = cover_f[:B], secret_f[:B]

    if verbose:
        print(f"  frames: {B} x {frame_len} samples "
              f"({B*frame_len/sr:.2f}s used) | scramble={use_scramble}")

    return {
        "cover_frames": cover_f.astype(np.float32),
        "secret_frames": secret_f.astype(np.float32),
        "perm_idx": perm_idx,
        "secret_clean": secret.astype(np.float32),     # for loss reference
        "meta": dict(sr=sr, frame_len=frame_len, seg=seg, B=B, key=key),
    }


# ----------------------------------------------------------------------
if __name__ == "__main__":
    # --- EDIT THESE TWO PATHS for your machine ---
    COVER = r"data\AN_30sec_raw_cover_v2.aif"
    SECRET = r"data\Generated\moloch_secret_30s.wav"

    d = prep(COVER, SECRET, use_scramble=False)

    # ---- plumbing sanity check: chunk -> reassemble (no scramble) ----
    re_secret = unframe(d["secret_frames"])
    ref = d["secret_clean"][:len(re_secret)]
    err = np.abs(re_secret - ref).max()
    print(f"\nPASS-THROUGH CHECK (chunk round-trip): max error = {err:.2e}")
    print("OK -- plumbing is lossless" if err < 1e-6 else "WARNING -- round-trip lost data")