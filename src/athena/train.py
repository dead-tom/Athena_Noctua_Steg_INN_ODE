"""
train.py  (v8, DETERMINISTIC REVEAL TEST)  --  Athena_Noctua_Steg_INN_ODE
Hypothesis: the random z at reveal was a fixed noise floor (~0.065 Blake-domain)
with no benefit -- you have no compression channel, so you never needed it.
Change: reveal from a FIXED ZERO, not fresh noise. Deterministic decode.

Single test: alpha=0.1 (inaudible, ~-50 dBFS), 200 epochs.
Prints spec_corr every 40 epochs so you SEE Blake emerge (or not) live.
  spec_corr climbs toward >0.7 -> random z WAS the wall, we cracked it.
  spec_corr stays ~0           -> deterministic isn't enough -> real architecture.

Run:  python src\train.py
"""

import os, time
import numpy as np
import torch
import soundfile as sf
from scipy.signal import stft

import data as D
import losses as L
from coupling_inn import CouplingINN


# ---- CONFIG ----------------------------------------------------------
COVER  = r"data\raw\AN_30sec_raw_cover_v2.aif"
SECRET = r"data\Generated\moloch_secret_30s.wav"
OUT, MODELS = "outputs", "models"

ALPHA  = 0.1
EPOCHS = 200
COVER_T0, SECRET_T0 = 0.0, 0.0
BATCH, LR, N_BLOCKS = 16, 2e-4, 8
USE_AMP, SAVE_24BIT = False, True
W_CONCEAL, W_REVEAL, W_GAUSS = 1.0, 2.0, 0.01   # gauss now vestigial (z=0), kept tiny
# ----------------------------------------------------------------------


def spec_corr(a, b, sr):
    _, _, Za = stft(a, sr, nperseg=2048)
    _, _, Zb = stft(b, sr, nperseg=2048)
    return float(np.corrcoef(np.abs(Za).ravel(), np.abs(Zb).ravel())[0, 1])


def robust_norm(x):
    p = np.percentile(np.abs(x), 99.5) + 1e-12
    return np.clip(x / p, -1.0, 1.0)


def reveal_all(net, cover, secret, B, dev):
    """Deterministic reveal: feed ZEROS, not noise. Returns stego, recovered frames."""
    net.eval()
    stego_f = torch.empty_like(cover); sh_f = torch.empty_like(secret)
    with torch.no_grad():
        for i in range(0, B, BATCH):
            cb = cover[i:i+BATCH].to(dev); sb = secret[i:i+BATCH].to(dev)
            stego, r = net(cb, sb)
            _, sh = net.inverse(stego, torch.zeros_like(r))   # <-- ZERO, deterministic
            stego_f[i:i+BATCH] = stego.float().cpu()
            sh_f[i:i+BATCH] = sh.float().cpu()
    net.train()
    return stego_f, sh_f


def main():
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    use_amp = USE_AMP and dev == "cuda"
    print(f"device: {dev} | AMP: {use_amp} | DETERMINISTIC reveal (z=0) | ALPHA={ALPHA}", flush=True)
    os.makedirs(OUT, exist_ok=True); os.makedirs(MODELS, exist_ok=True)

    sr0, sx = D.load_wav(SECRET)
    d = D.prep(COVER, SECRET, seg_seconds=len(sx)/sr0,
               cover_start=COVER_T0, secret_start=SECRET_T0, use_scramble=False)
    cover = torch.from_numpy(d["cover_frames"])
    secret = torch.from_numpy(d["secret_frames"]) * ALPHA
    sr, B = d["meta"]["sr"], d["meta"]["B"]
    cov_audio, ref_audio = D.unframe(cover.numpy()), d["secret_clean"]
    print(f"total frames: {B} | {EPOCHS} epochs\n", flush=True)

    net = CouplingINN(n_blocks=N_BLOCKS).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=LR)
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    t0 = time.time()

    for ep in range(1, EPOCHS + 1):
        perm = torch.randperm(B); run_rev, nb = 0.0, 0
        for i in range(0, B, BATCH):
            idx = perm[i:i + BATCH]
            cb = cover[idx].to(dev); sb = secret[idx].to(dev)
            with torch.autocast(device_type="cuda", enabled=use_amp):
                stego, r = net(cb, sb)
                z = torch.zeros_like(r)                       # <-- ZERO, not randn
                _, secret_hat = net.inverse(stego, z)
                loss, log = L.total_loss(stego, cb, secret_hat, sb, r,
                                         W_CONCEAL, W_REVEAL, W_GAUSS)
            opt.zero_grad(); scaler.scale(loss).backward()
            scaler.step(opt); scaler.update()
            run_rev += log["reveal"]; nb += 1
        if ep == 1 or ep % 40 == 0:
            _, sh_f = reveal_all(net, cover, secret, B, dev)
            rec = D.unframe(sh_f.numpy()) / ALPHA
            sc = spec_corr(ref_audio[:len(rec)], rec, sr)
            print(f"  epoch {ep:3d}/{EPOCHS} | reveal {run_rev/nb:.4f} | "
                  f"spec_corr {sc:+.3f} | {time.time()-t0:5.1f}s", flush=True)

    # final export
    stego_f, sh_f = reveal_all(net, cover, secret, B, dev)
    stego_audio = D.unframe(stego_f.numpy())
    rec = D.unframe(sh_f.numpy()) / ALPHA
    ref = ref_audio[:len(rec)]

    pert = stego_audio - cov_audio
    rms_dbfs = 20*np.log10(np.sqrt((pert**2).mean()) + 1e-20)
    sc = spec_corr(ref, rec, sr)
    err = float(np.abs(rec - ref).mean())

    subtype = "PCM_24" if SAVE_24BIT else "PCM_16"
    sf.write(os.path.join(OUT, "stego_owl_det.wav"), stego_audio, sr, subtype=subtype)
    sf.write(os.path.join(OUT, "recovered_det.wav"), robust_norm(rec), sr, subtype=subtype)
    torch.save(net.state_dict(), os.path.join(MODELS, "coupling_inn_det.pt"))

    print(f"\n========== DETERMINISTIC REVEAL RESULT ==========")
    print(f"ALPHA {ALPHA} | perturbation {rms_dbfs:.1f} dBFS")
    print(f"spec_corr {sc:+.3f} | reveal_err {err:.4f}")
    print("compare: random-z at alpha=0.1 gave spec_corr -0.002, err 0.0652")
    if sc > 0.7:
        print(">>> RECOVERED and inaudible. random z was the wall. saved *_det.wav")
    elif sc < 0.3:
        print(">>> still noise. deterministic alone is not enough -> architecture next.")
    else:
        print(">>> partial. promising but not clean -> tune or go deeper.")


if __name__ == "__main__":
    main()