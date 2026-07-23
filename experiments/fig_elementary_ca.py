"""
Figura 1 — Diagramas espaço-tempo de AC elementares (regras de Wolfram).

Mostra quatro regras representativas das classes de comportamento de
Wolfram, incluindo a Regra 90 (fractal de Sierpiński) e a Regra 30
(caótica). Cada painel é um diagrama espaço-tempo: o tempo cresce de
cima para baixo.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from _common import figpath
from src import elementary_ca as eca
from src.visualize import apply_style, BINARY_CMAP


def make(rng: np.random.Generator | None = None) -> dict:
    apply_style()
    rng = rng or np.random.default_rng(42)

    W, T = 401, 200
    rules = [90, 30, 110, 184]
    titles = {
        90: "Regra 90 — Sierpiński (fractal)",
        30: "Regra 30 — caótica",
        110: "Regra 110 — universal",
        184: "Regra 184 — fluxo de tráfego",
    }
    seeds = {90: "single", 30: "single", 110: "single", 184: "random"}

    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6))
    densities = {}
    for ax, r in zip(axes, rules):
        img = eca.evolve(r, width=W, steps=T, seed=seeds[r], rng=rng)
        densities[r] = float(img[-1].mean())
        ax.imshow(img, cmap=BINARY_CMAP, interpolation="nearest", aspect="auto")
        ax.set_title(titles[r], fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlabel("espaço"); ax.set_ylabel("tempo")

    fig.suptitle("Autômatos celulares elementares 1D: quatro classes de comportamento",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = figpath("fig1_elementary_ca.png")
    fig.savefig(out)
    plt.close(fig)
    return {"figure": out, "final_densities": densities}


if __name__ == "__main__":
    print(make())
