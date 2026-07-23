"""
Figura 3 — Transição de percolação de sítios.

Painel superior: três instantâneos de uma rede LxL abaixo, próximo e
acima do limiar p_c, com o maior aglomerado destacado.
Painel inferior: probabilidade de percolação P(atravessar) em função de
p para vários tamanhos L. As curvas ficam mais íngremes conforme L
cresce e se cruzam perto de p_c ≈ 0,5927 (transição de fase).
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from _common import figpath
from src import percolation as perc
from src.visualize import apply_style, PERCOLATION_CMAP


def _snapshot_axes(ax, L, p, rng):
    grid = perc.occupy(L, p, rng)
    biggest = perc.largest_cluster_mask(grid)
    disp = grid.astype(int)             # 0 vazio, 1 ocupado
    disp[biggest] = 2                   # 2 = maior aglomerado
    ax.imshow(disp, cmap=PERCOLATION_CMAP, interpolation="nearest")
    labels, _ = perc.label_clusters(grid)
    tag = "percola" if perc.spans(labels) else "não percola"
    ax.set_title(f"p = {p:.3f}  ({tag})", fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])


def make(rng: np.random.Generator | None = None) -> dict:
    apply_style()
    rng = rng or np.random.default_rng(7)

    fig = plt.figure(figsize=(11, 8.4))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.1], hspace=0.32, wspace=0.15)

    # ---- instantâneos ----
    Lsnap = 200
    for j, p in enumerate([0.50, perc.PC_THEORETICAL, 0.70]):
        ax = fig.add_subplot(gs[0, j])
        _snapshot_axes(ax, Lsnap, p, rng)

    # ---- curva de percolação para vários L ----
    ax = fig.add_subplot(gs[1, :])
    ps = np.linspace(0.45, 0.75, 31)
    pcs = {}
    for L, trials in [(32, 120), (64, 120), (128, 80)]:
        probs = perc.sweep_threshold(L, ps, trials, rng)
        ax.plot(ps, probs, "o-", ms=3, lw=1.4, label=f"L = {L}")
        pcs[L] = perc.estimate_pc(ps, probs)

    ax.axvline(perc.PC_THEORETICAL, color="0.4", ls="--", lw=1.2,
               label=f"$p_c$ teórico = {perc.PC_THEORETICAL:.4f}")
    ax.axhline(0.5, color="0.7", ls=":", lw=1)
    ax.set_xlabel("densidade de ocupação  p")
    ax.set_ylabel("probabilidade de percolação")
    ax.set_title("Transição de fase da percolação de sítios (efeito do tamanho L)")
    ax.legend(frameon=False, ncol=2, fontsize=9)

    fig.suptitle("Percolação como autômato celular estático: um limiar crítico",
                 fontsize=12, fontweight="bold")
    out = figpath("fig3_percolation_threshold.png")
    fig.savefig(out)
    plt.close(fig)

    pc_est = float(np.mean(list(pcs.values())))
    return {
        "figure": out,
        "pc_estimates_by_L": {int(k): float(v) for k, v in pcs.items()},
        "pc_estimated_mean": pc_est,
        "pc_theoretical": float(perc.PC_THEORETICAL),
        "rel_error_pct": float(100 * abs(pc_est - perc.PC_THEORETICAL) / perc.PC_THEORETICAL),
    }


if __name__ == "__main__":
    print(make())
