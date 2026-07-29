"""
coupling_inn.py  --  Athena_Noctua_Steg_INN_ODE   (Stage 1: the control)

A reversible network built from affine coupling blocks (RealNVP / WavInWav
lineage). Two streams flow through: cover and secret.

  forward (HIDE):    (cover, secret) -> (stego, r)
  inverse (REVEAL):  (stego, z)      -> (cover_hat, secret_hat)

Invertibility is by construction -- every block undoes itself algebraically,
so there is NO separately-learned decoder. The little conv nets (phi, rho, eta)
can be as complex as we like; only the coupling structure must be reversible.
"""

import torch
import torch.nn as nn


# ----------------------------------------------------------------------
class ConvNet(nn.Module):
    """Small 1-D conv net used inside a coupling block (need not be invertible)."""
    def __init__(self, ch=32, k=7):
        super().__init__()
        p = k // 2
        self.net = nn.Sequential(
            nn.Conv1d(1, ch, k, padding=p), nn.GELU(),
            nn.Conv1d(ch, ch, k, padding=p), nn.GELU(),
            nn.Conv1d(ch, 1, k, padding=p),
        )
        # start near zero so the block begins close to identity (stable training)
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(self, x):                     # [B, L] -> [B, L]
        return self.net(x.unsqueeze(1)).squeeze(1)


# ----------------------------------------------------------------------
class CouplingBlock(nn.Module):
    """
    One affine coupling block (WavInWav eqs. 5-6), with a clamped scale so the
    exp() can't blow up (the numerical-stability point from Chang et al.).
    """
    def __init__(self, ch=32, clamp=2.0):
        super().__init__()
        self.phi = ConvNet(ch)   # cover  += phi(secret)
        self.rho = ConvNet(ch)   # secret *= exp(scale(cover)) ...
        self.eta = ConvNet(ch)   #          ... + eta(cover)
        self.clamp = clamp

    def _scale(self, x):
        return self.clamp * torch.tanh(self.rho(x))      # bounded in (-clamp, clamp)

    def forward(self, cover, secret):
        cover = cover + self.phi(secret)
        secret = secret * torch.exp(self._scale(cover)) + self.eta(cover)
        return cover, secret

    def inverse(self, cover, secret):
        secret = (secret - self.eta(cover)) * torch.exp(-self._scale(cover))
        cover = cover - self.phi(secret)
        return cover, secret


# ----------------------------------------------------------------------
class CouplingINN(nn.Module):
    """Stack of M coupling blocks. forward = hide, inverse = reveal."""
    def __init__(self, n_blocks=8, ch=32, clamp=2.0):
        super().__init__()
        self.blocks = nn.ModuleList(CouplingBlock(ch, clamp) for _ in range(n_blocks))

    def forward(self, cover, secret):         # HIDE
        for b in self.blocks:
            cover, secret = b(cover, secret)
        return cover, secret                  # (stego, r)

    def inverse(self, stego, z):              # REVEAL
        for b in reversed(self.blocks):
            stego, z = b.inverse(stego, z)
        return stego, z                       # (cover_hat, secret_hat)


# ----------------------------------------------------------------------
if __name__ == "__main__":
    torch.manual_seed(0)
    B, L = 29, 16384
    cover  = torch.randn(B, L) * 0.1
    secret = torch.randn(B, L) * 0.1

    net = CouplingINN(n_blocks=8)
    n_params = sum(p.numel() for p in net.parameters())
    print(f"model: {n_params:,} parameters, 8 coupling blocks")

    # core test: forward then inverse must return the inputs (invertibility)
    with torch.no_grad():
        stego, r = net(cover, secret)
        cover_hat, secret_hat = net.inverse(stego, r)
    e_cover  = (cover_hat  - cover ).abs().max()
    e_secret = (secret_hat - secret).abs().max()
    print(f"round-trip error  cover: {e_cover:.2e}   secret: {e_secret:.2e}")
    ok = max(e_cover, e_secret) < 1e-4
    print("OK -- network is invertible" if ok else "WARNING -- not invertible")