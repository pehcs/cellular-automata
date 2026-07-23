"""
Figura 4 — O aglomerado percolante é um fractal em p_c.

Gera redes grandes exatamente no limiar p_c, isola o maior aglomerado
(condicionado a percolar) e mede sua dimensão fractal por box-counting,
comparando com o valor teórico D = 91/48 ≈ 1,896.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from _common import figpath
from src import percolation as perc
from src import fractal
from src.visualize import apply_style, ACCENT, ACCENT2, PERCOLATION_CMAP


def _spanning_largest_cluster(L, rng, max_try=60):
    """Amostra redes em p_c até obter uma que percola; devolve o maior cluster."""
    for _ in range(max_try):
        grid = perc.occupy(L, perc.PC_THEORETICAL, rng)
        labels, _ = perc.label_clusters(grid)
        if perc.spans(labels):
            return perc.largest_cluster_mask(grid)
    return perc.largest_cluster_mask(perc.occupy(L, perc.PC_THEORETICAL, rng))


def make(rng: np.random.Generator | None = None) -> dict:
    apply_style()
    rng = rng or np.random.default_rng(11)

    L = 1024
    # Média da dimensão sobre algumas realizações que percolam.
    dims, sample_mask = [], None
    for k in range(6):
        mask = _spanning_largest_cluster(L, rng)
        res = fractal.fractal_dimension(mask)
        dims.append(res["dimension"])
        if k == 0:
            sample_mask, sample_res = mask, res

    D = float(np.mean(dims))
    D_std = float(np.std(dims))
    theo = perc.DF_SPANNING_CLUSTER

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))

    disp = np.zeros_like(sample_mask, dtype=int)
    disp[sample_mask] = 2
    ax1.imshow(disp, cmap=PERCOLATION_CMAP, interpolation="nearest")
    ax1.set_title(f"(a) Aglomerado percolante em $p_c$  (L={L})")
    ax1.set_xticks([]); ax1.set_yticks([])

    ax2.plot(sample_res["log_inv_size"], sample_res["log_count"], "o",
             mfc="white", color=ACCENT, label="todas as escalas")
    xf, yf = sample_res["log_inv_size_fit"], sample_res["log_count_fit"]
    ax2.plot(xf, yf, "o", color=ACCENT, label="faixa ajustada")
    xx = np.linspace(xf.min(), xf.max(), 100)
    ax2.plot(xx, sample_res["dimension"] * xx + sample_res["intercept"],
             "-", color=ACCENT2, label=f"ajuste: D = {sample_res['dimension']:.3f}")
    ax2.set_title("(b) Dimensão fractal do aglomerado")
    ax2.set_xlabel(r"$\log(1/s)$"); ax2.set_ylabel(r"$\log N(s)$")
    ax2.legend(loc="upper left", frameon=False)
    ax2.text(0.98, 0.05,
             f"média (6 amostras): D = {D:.3f} ± {D_std:.3f}\n"
             f"teórico 91/48 = {theo:.3f}",
             transform=ax2.transAxes, ha="right", va="bottom", fontsize=9)

    fig.tight_layout()
    out = figpath("fig4_percolation_fractal.png")
    fig.savefig(out)
    plt.close(fig)
    return {
        "figure": out,
        "D_estimated_mean": D,
        "D_estimated_std": D_std,
        "D_theoretical": float(theo),
        "rel_error_pct": float(100 * abs(D - theo) / theo),
        "n_samples": len(dims),
        "L": L,
    }


if __name__ == "__main__":
    print(make())
