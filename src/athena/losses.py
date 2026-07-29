"""
losses.py  --  Athena_Noctua_Steg_INN_ODE
Scoring for the hide-and-reveal. Architecture-agnostic: works for both the
coupling INN and the Neural ODE.

Three parts:
  concealment   stego must look/sound like the cover (owl)   [time + STFT]
  revelation    recovered secret must match the original     [time + STFT]
  quiet-weight  multiplies the concealment penalty UP where the owl is silent,
                forcing the network to keep the gaps clean instead of leaking
                the image into them. This is the key term for THIS cover.
"""

import torch
import torch.nn.functional as F


# ----------------------------------------------------------------------
def stft_mag(x, n_fft=2048, hop=512):
    """Magnitude STFT of a batch of frames [B, L] -> [B, freq, time]."""
    win = torch.hann_window(n_fft, device=x.device)
    Z = torch.stft(x, n_fft=n_fft, hop_length=hop, window=win,
                   return_complex=True, center=True)
    return Z.abs()


# ----------------------------------------------------------------------
def quiet_weight(cover, eps=1e-4, floor=1.0, gain=25.0):
    """
    Per-sample weight that is LARGE where the cover is quiet, ~1 where it's loud.
      weight = floor + gain * (1 - normalised_local_energy)
    So silence is penalised hard; loud calls (which mask) are penalised normally.
    """
    # local energy via a short moving-average of x^2
    e = cover ** 2
    k = 256
    kernel = torch.ones(1, 1, k, device=cover.device) / k
    e = F.conv1d(e.unsqueeze(1), kernel, padding=k // 2).squeeze(1)
    e = e[..., : cover.shape[-1]]
    e = e / (e.max() + eps)                 # 0..1, 1 = loudest
    return floor + gain * (1.0 - e)         # big in silence, ~floor when loud


# ----------------------------------------------------------------------
def conceal_loss(stego, cover):
    """Stego should equal the cover. Quiet-weighted in time, plus STFT match."""
    w = quiet_weight(cover)
    time = (w * (stego - cover) ** 2).mean()
    spec = F.l1_loss(stft_mag(stego), stft_mag(cover))
    return time + spec, time.detach(), spec.detach()


def reveal_loss(secret_hat, secret):
    """Recovered secret should equal the original. Time + STFT."""
    time = F.mse_loss(secret_hat, secret)
    spec = F.l1_loss(stft_mag(secret_hat), stft_mag(secret))
    return time + spec, time.detach(), spec.detach()


def gauss_loss(r):
    """Push the discarded stream toward N(0,1) so the z-swap works at reveal."""
    return (r.mean() ** 2) + (r.var() - 1.0) ** 2


# ----------------------------------------------------------------------
def total_loss(stego, cover, secret_hat, secret, r=None,
               w_conceal=1.0, w_reveal=1.0, w_gauss=0.01):
    c, c_t, c_s = conceal_loss(stego, cover)
    v, v_t, v_s = reveal_loss(secret_hat, secret)
    g = gauss_loss(r) if r is not None else torch.zeros((), device=stego.device)
    loss = w_conceal * c + w_reveal * v + w_gauss * g
    log = dict(total=float(loss), conceal=float(c), reveal=float(v),
               conceal_time=float(c_t), conceal_spec=float(c_s),
               reveal_time=float(v_t), reveal_spec=float(v_s), gauss=float(g))
    return loss, log


# ----------------------------------------------------------------------
if __name__ == "__main__":
    torch.manual_seed(0)
    B, L = 29, 16384
    # dummy tensors of the right shape: fake cover/stego/secret, random numbers
    cover  = torch.randn(B, L) * 0.1
    cover[:, : L // 2] *= 0.001            # make half of it "silent" to test weighting
    stego  = cover + torch.randn(B, L) * 0.01
    secret = torch.randn(B, L) * 0.1
    secret_hat = secret + torch.randn(B, L) * 0.01
    r = torch.randn(B, L)

    w = quiet_weight(cover)
    print("quiet_weight: silent region avg = %.1f | loud region avg = %.1f"
          % (w[:, : L // 2].mean(), w[:, L // 2 :].mean()))
    loss, log = total_loss(stego, cover, secret_hat, secret, r)
    print("loss runs on dummy tensors. components:")
    for k, v in log.items():
        print(f"  {k:13s} {v:.5f}")
    print("OK -- losses.py plumbing works" if torch.isfinite(loss) else "WARNING nan/inf")