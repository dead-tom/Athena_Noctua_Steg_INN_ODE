# FORMULATION — the system as mathematics

Status: written 7 August 2026 from the decisions recorded in LOG H-007 and H-008, `lab/DECISIONS.md`, and `pipeline.mermaid`.

---

## 1. The host

The host is the synthetic silence: a distribution over integer PCM files, declared in advance and independently samplable (`D-COVER`).

- $P$ — the host law.
- $H^{(k)}$ — host instances drawn from $P$ by the reference sampler; the training set.
- $\tilde{H}$ — the stego. A draw of $P$, of the same type as any $H^{(k)}$, distinguished by which draw it is.

The payload determines which draw. The only map into the output is $z \mapsto \tilde{H}$.

---

## 2. Symbols

| Symbol | Meaning |
|---|---|
| $N$ | samples in the file; $48000 \times$ seconds |
| $\mathcal{X}$ | $\{-2^{23},\dots,2^{23}-1\}^N$ — 24-bit signed integer PCM |
| $P$ | host law over $\mathcal{X}$ |
| $\Psi(\nu)$ | power spectral density of $P$ |
| $H^{(k)}$ | host instance $k$ |
| $f_\theta$, $f_\theta^{-1}$ | the flow, inference and generative directions; bijective on integers |
| $\theta$ | learned weights |
| $p_Z$ | base distribution in latent space |
| $p_\theta$ | model law, $f_\theta^{-1}\#p_Z$ |
| $S$, $\hat{S}$ | payload, recovered payload |
| $\Gamma$ | SHA-256 checksum appended; $\Gamma^{-1}$ strips and verifies |
| $C$ | lossless compression; $C^{-1}$ decompresses |
| $W$ | whitening |
| $b$ | whitened payload bits, length $m$ |
| $r$ | fresh randomness, redrawn per file |
| $\Phi$ | measure-preserving assembly of bits into a latent vector |
| $z$, $\hat{z}$ | latent vector |
| $\tilde{H}$ | the stego |
| $Q$ | the law of $\tilde{H}$ |

$P$, $\theta$, $p_Z$, $\Gamma$, $C$, $W$ and $\Phi$ are public. There is no key (`D-THESIS`).

---

## 3. The host law

$P$ satisfies

$$\mathbb{E}[x_i] = 0, \qquad \Pr[x_i > 0] = \Pr[x_i < 0], \qquad \mathrm{RMS} \approx -80\ \mathrm{dBFS}$$

with samples read as air-pressure deviation about ambient, in 24-bit PCM. The declaration also fixes the amplitude law (discretised Gaussian by default), low-bit behaviour (F34), and stationarity. The power spectral density $\Psi(\nu)$ is declared but unset (`D-COLOUR`, settled at R1); expressions below carry it symbolically.

Two properties are required of $P$: it is samplable without the flow, since the reference sampler supplies the draws the stego is compared against; and it has entropy, since §7 gives capacity as the entropy of $P$.

---

## 4. Security

A scheme is $\varepsilon$-secure when $D_{\mathrm{KL}}(P \Vert Q) \le \varepsilon$, and perfectly secure at $\varepsilon = 0$. The definition bounds all detectors simultaneously: for any decision rule with false-alarm rate $\alpha$ and miss rate $\beta$,

$$\mathrm{TV}(P,Q) \le \sqrt{\varepsilon/2}, \qquad \alpha + \beta \ge 1 - \mathrm{TV}(P,Q)$$

At $\varepsilon = 0$ no detector beats chance. This is the Level 3 bar of `D-ARCH`.

Let $B$ be the payload, uniform on $m$ bits. Security requires the marginal of $\tilde{H}$ to be $P$; exact recovery requires $\mathrm{H}(B \mid \tilde{H}) = 0$. A joint law on $(B, \tilde{H})$ with those marginals is a **coupling** of $\mathrm{Unif}\{0,1\}^m$ with $P$. Such a coupling with zero conditional entropy exists only if $\mathrm{H}(P) \ge m$.

---

## 5. The flow

$f_\theta$ is a bijection between integer sets (`D-CARRIER`, `D-MODEL`). Under counting measure the change of variables carries no volume term:

$$p_\theta(x) = p_Z(f_\theta(x))$$

so there is no log-determinant in the likelihood. Inversion is exact in integer arithmetic for every $x$ and every $\theta$, including at initialisation; invertibility is a property of the layer construction. Training determines only how close $p_\theta$ is to $P$.

Fitting is by maximum likelihood on host instances:

$$\theta^\star = \arg\min_\theta \ -\frac{1}{K}\sum_{k=1}^{K} \log p_Z\!\left(f_\theta(H^{(k)})\right)$$

equal to $\arg\min_\theta D_{\mathrm{KL}}(P \Vert p_\theta)$ up to an additive constant.

---

## 6. Payload and coupling

$$b = W\!\left(C(\Gamma(S))\right) \in \{0,1\}^m$$

$\Gamma$ appends a 256-bit digest over the declared object. $C$ compresses losslessly. $W$ maps the result to a uniform bitstream; it is public and keyless and provides no confidentiality (`D-THESIS`). Payload length is fixed by the claim contract at R0, not carried in the stream.

**W.1.** $b$ is indistinguishable from an i.i.d. fair-coin sequence given $W$ and the class from which $S$ is drawn.

$\Phi$ maps uniform bits to a latent vector by integer-CDF arithmetic coding over the model's conditional CDFs. Coordinate $j$ consumes bits to form a uniform $u_j$ at working precision, and

$$z_j = F_j^{-1}(u_j \mid z_{<j})$$

Correctness condition:

$$b \Vert r \sim \mathrm{Unif}\{0,1\}^L \quad \Longrightarrow \quad z \sim p_Z$$

where $L$ is the total bit budget consumed by $\Phi$.

**C.1.** $m < L$. The deficit is filled with fresh randomness $r$, redrawn per file and discarded after embedding (F36). Every coordinate consumed by $\Phi$ carries uniform bits; a coordinate carrying a constant or a repeated pattern makes $z$ atypical under $p_Z$, and $\Phi$ is public, so its position is known.

**C.2.** No fixed-position structure may occupy a coordinate consumed by $\Phi$.

$r$ is not a key: recovery reads $b$ from the payload coordinates without reference to the randomness coordinates.

---

## 7. Embedding, recovery, capacity

**Embedding.**

$$b = W(C(\Gamma(S))), \qquad z = \Phi(b \Vert r), \qquad \tilde{H} = f_\theta^{-1}(z)$$

**Recovery.**

$$\hat{z} = f_\theta(\tilde{H}), \qquad \hat{b} = \Phi^{-1}(\hat{z})\big|_{1:m}, \qquad \hat{S} = \Gamma^{-1}\!\left(C^{-1}(W^{-1}(\hat{b}))\right)$$

**Two gaps.** $f_\theta^{-1}$ is a bijection and preserves KL divergence exactly. Writing

$$\varepsilon_{\text{code}} = D_{\mathrm{KL}}(\text{law of } z \,\Vert\, p_Z), \qquad \varepsilon_{\text{model}} = D_{\mathrm{KL}}(P \Vert p_\theta)$$

Pinsker and the triangle inequality on total variation give

$$\mathrm{TV}(P, Q) \ \le\ \sqrt{\varepsilon_{\text{code}}/2} + \sqrt{\varepsilon_{\text{model}}/2}$$

$\varepsilon_{\text{code}}$ is zeroed by the construction of §6 and involves no training; it is measurable in isolation by substituting the analytic sampler for $p_\theta$, which is gate R2. $\varepsilon_{\text{model}}$ is the residual of the training objective in §5, measured against the reference sampler at gate R3. **Capacity.** From §4, exact recovery of a uniform $m$-bit payload requires

$$m \le \mathrm{H}(P)$$

Entropy is preserved by the bijection, so equivalently $m \le \mathrm{H}(p_Z)$. For an i.i.d. floor of per-sample entropy $h$ bits, $m \le Nh$. Usable payload is that bound less 256 bits for the checksum. Gate R1 sets the operating point well inside it: the canonical payload is at most 10% of the entropy-rate capacity.

The bound is linear in $N$. The square root law constrains the modified-cover setting, in which the adversary holds a better model of the cover than the embedder; under synthesis with a declared law that asymmetry is absent (L15). This holds exactly at $\varepsilon_{\text{model}} = 0$; with a model gap, secure capacity degrades toward the square-root regime in proportion to that gap.

---

## 8. Losses

$$\mathcal{L}(\theta) = -\frac{1}{K}\sum_{k=1}^{K} \log p_Z\!\left(f_\theta(H^{(k)})\right)$$

This is the entire training signal.

A reconstruction term is identically zero, since the flow is exactly invertible independent of $\theta$; round-trip equality is checked each epoch as an assertion (gate R3, integer closure).

Excluded by construction:

- Perceptual and masking losses. There is no instance for the output to resemble; audibility is a property of $P$.
- Cover-similarity and distortion losses. The output is generated, not modified (L13).
- Adversarial detector losses. Training against a distinguisher targets Level 2 and makes the evaluation circular; detectors belong in `EVALUATION.md` (L16, L19).
- Residual-prior terms. There is no residual stream (L1).

---

## 9. Exact recovery

$\hat{S} = S$ bit-exactly under four conditions:

- **R.1** Integer arithmetic throughout, with no floating-point path that can determine a sample value (L14).
- **R.2** Bit-identical $\theta$ at both ends, pinned by checksum in `MODEL_CARD.md`.
- **R.3** Verbatim storage: WAV PCM_24, no dither, no normalisation, no limiter, no secondary chunks (`D-FLOAT/EXPORT`).
- **R.4** Flow output within 24-bit signed range, or wrapping guaranteed by the layer construction.
- **R.5** Declared, frozen compression format. $C^{-1}$ must be bit-exact against $C$; the format is pinned in `MODEL_CARD.md` alongside $\theta$.

Then $\hat{z} = z$, $\hat{b} = b$, and $\hat{S} = S$. Verification is the checksum: pass or fail, with no partial measure.

---

## 10. Undeclared quantities

| Quantity | Where it is settled |
|---|---|
| $\Psi(\nu)$, the spectral shape of the host law | `D-COLOUR`, at R1 |
| $p_Z$ and its marginals | R1 |
| Layer construction of $f_\theta$ | R3 |
| Concrete form of $W$ | R2 |
| Integer overflow discipline (R.4) | R3 |
| Concrete form of $C$ | R2 |

---

## Cross-references

`pipeline.mermaid` governs the shape of the flow. `ARCHITECTURE.md` describes the components. `ALGORITHMS.md` gives the numbered procedures for §7. `EVALUATION.md` defines the reference, neutral and stego comparisons that measure the two gaps. `lab/PLAN.md` holds gates R0–R7. `lab/DECISIONS.md` holds the committed choices.