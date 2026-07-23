"""
Reproduz TODAS as figuras e resultados numéricos do artigo.

Uso:
    python experiments/run_all.py

Gera os PNGs em ``figures/`` e grava um resumo em ``figures/results.json``.
A semente global é fixa para garantir reprodutibilidade.
"""
from __future__ import annotations

import json
import time

import numpy as np

from _common import figpath
import fig_elementary_ca
import fig_rule90_fractal
import fig_percolation_threshold
import fig_percolation_fractal
import fig_forest_fire


def main():
    t0 = time.time()
    # Uma semente por experimento (reprodutibilidade e independência).
    results = {}
    print(">> Fig 1: AC elementares ...")
    results["fig1_elementary_ca"] = fig_elementary_ca.make(np.random.default_rng(42))
    print(">> Fig 2: Regra 90 / dimensão fractal ...")
    results["fig2_rule90_fractal"] = fig_rule90_fractal.make(np.random.default_rng(90))
    print(">> Fig 3: limiar de percolação ...")
    results["fig3_percolation_threshold"] = fig_percolation_threshold.make(np.random.default_rng(7))
    print(">> Fig 4: dimensão fractal do aglomerado percolante ...")
    results["fig4_percolation_fractal"] = fig_percolation_fractal.make(np.random.default_rng(11))
    print(">> Fig 5: propagação fogo/epidemia ...")
    results["fig5_forest_fire"] = fig_forest_fire.make(np.random.default_rng(3))

    results["_meta"] = {"elapsed_seconds": round(time.time() - t0, 1)}

    with open(figpath("results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n===== RESUMO DOS RESULTADOS =====")
    r2 = results["fig2_rule90_fractal"]
    r3 = results["fig3_percolation_threshold"]
    r4 = results["fig4_percolation_fractal"]
    print(f"Regra 90  : D = {r2['D_estimated']:.3f}  (teórico {r2['D_theoretical']:.3f}, "
          f"erro {r2['rel_error_pct']:.1f}%)")
    print(f"Percolação: p_c = {r3['pc_estimated_mean']:.4f}  (teórico {r3['pc_theoretical']:.4f}, "
          f"erro {r3['rel_error_pct']:.1f}%)")
    print(f"Aglomerado: D = {r4['D_estimated_mean']:.3f} ± {r4['D_estimated_std']:.3f}  "
          f"(teórico {r4['D_theoretical']:.3f}, erro {r4['rel_error_pct']:.1f}%)")
    print(f"Tempo total: {results['_meta']['elapsed_seconds']} s")
    return results


if __name__ == "__main__":
    main()
