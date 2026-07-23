"""
Figura 2 — Regra 90 e a dimensão fractal do triângulo de Sierpiński.

Painel (a): diagrama espaço-tempo da Regra 90 a partir de uma única
célula, que reproduz o triângulo de Sierpiński.
Painel (b): contagem de caixas (box-counting) em escala log-log; a
inclinação estima a dimensão fractal, comparada ao valor teórico
log(3)/log(2) ≈ 1,585.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from _common import figpath
from src import elementary_ca as eca
from src import fractal
from src.visualize import apply_style, BINARY_CMAP, ACCENT, ACCENT2


def make(rng: np.random.Generator | None = None) -> dict:
    apply_style()

    # Diagrama de Sierpiński: usar potência de 2 dá auto-similaridade exata.
    T = 256
    img = eca.evolve(90, width=2 * T + 1, steps=T, seed="single")

    # Dimensão fractal por box-counting.
    res = fractal.fractal_dimension(img)
    D = res["dimension"]
    theo = np.log(3) / np.log(2)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

    ax1.imshow(img, cmap=BINARY_CMAP, interpolation="nearest", aspect="auto")
    ax1.set_title("(a) Regra 90 → triângulo de Sierpiński")
    ax1.set_xticks([]); ax1.set_yticks([])
    ax1.set_xlabel("espaço"); ax1.set_ylabel("tempo")

    ax2.plot(res["log_inv_size"], res["log_count"], "o", mfc="white",
             color=ACCENT, label="todas as escalas")
    xf, yf = res["log_inv_size_fit"], res["log_count_fit"]
    ax2.plot(xf, yf, "o", color=ACCENT, label="faixa ajustada")
    xx = np.linspace(xf.min(), xf.max(), 100)
    ax2.plot(xx, D * xx + res["intercept"], "-", color=ACCENT2,
             label=f"ajuste: D = {D:.3f}")
    ax2.set_title("(b) Dimensão fractal (box-counting)")
    ax2.set_xlabel(r"$\log(1/s)$")
    ax2.set_ylabel(r"$\log N(s)$")
    ax2.legend(loc="upper left", frameon=False)
    ax2.text(0.98, 0.05,
             f"teórico log3/log2 = {theo:.3f}\nR² = {res['r_squared']:.4f}",
             transform=ax2.transAxes, ha="right", va="bottom", fontsize=9)

    fig.tight_layout()
    out = figpath("fig2_rule90_fractal.png")
    fig.savefig(out)
    plt.close(fig)
    return {
        "figure": out,
        "D_estimated": float(D),
        "D_theoretical": float(theo),
        "r_squared": float(res["r_squared"]),
        "rel_error_pct": float(100 * abs(D - theo) / theo),
    }


if __name__ == "__main__":
    print(make())
