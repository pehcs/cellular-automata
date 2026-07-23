"""
Figura 5 — Propagação espacial (fogo/epidemia) e o limiar de surto.

Painel superior: quatro instantâneos de um incêndio se espalhando a
partir de uma faísca central, numa floresta acima do limiar.
Painel inferior: fração final queimada em função da densidade de
árvores. A curva mostra um limiar abrupto próximo de p_c — o análogo
espacial do limiar epidêmico R0 = 1.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from _common import figpath
from src import forest_fire as ff
from src import percolation as perc
from src.visualize import apply_style, FOREST_CMAP


def make(rng: np.random.Generator | None = None) -> dict:
    apply_style()
    rng = rng or np.random.default_rng(3)

    # ---- instantâneos de um incêndio acima do limiar ----
    L = 201
    sim = ff.simulate(L, density=0.70, beta=1.0, rng=rng, record=True)
    frames = sim["frames"]
    picks = [0,
             len(frames) // 3,
             2 * len(frames) // 3,
             len(frames) - 1]

    fig = plt.figure(figsize=(11, 8.6))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.1], hspace=0.30, wspace=0.12)
    for j, idx in enumerate(picks):
        ax = fig.add_subplot(gs[0, j])
        ax.imshow(frames[idx], cmap=FOREST_CMAP, vmin=0, vmax=2,
                  interpolation="nearest")
        ax.set_title(f"t = {idx}", fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])

    # ---- curva de surto ----
    ax = fig.add_subplot(gs[1, :])
    densities = np.linspace(0.40, 0.85, 19)
    curve = ff.outbreak_curve(120, densities, beta=1.0, trials=12, rng=rng)
    ax.plot(densities, curve, "o-", color="#c1440e", lw=1.6, ms=4)
    ax.axvline(perc.PC_THEORETICAL, color="0.4", ls="--", lw=1.2,
               label=f"$p_c$ (percolação) = {perc.PC_THEORETICAL:.4f}")
    ax.set_xlabel("densidade de árvores (suscetíveis)  p")
    ax.set_ylabel("fração final queimada / infectada")
    ax.set_title("Limiar de surto: abaixo de $p_c$ o fogo se extingue; acima, varre a rede")
    ax.legend(frameon=False)

    fig.suptitle("Autômato celular de propagação (SIR espacial): fogo ≡ epidemia ≡ percolação",
                 fontsize=12, fontweight="bold")
    out = figpath("fig5_forest_fire.png")
    fig.savefig(out)
    plt.close(fig)

    # localizar o "joelho" da curva (maior derivada) como limiar empírico
    knee = float(densities[np.argmax(np.gradient(curve))])
    return {
        "figure": out,
        "burned_fraction_at_0.70": float(sim["burned_fraction"]),
        "empirical_threshold_knee": knee,
        "pc_theoretical": float(perc.PC_THEORETICAL),
    }


if __name__ == "__main__":
    print(make())
