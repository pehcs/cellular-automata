"""
Percolação de sítios em rede quadrada 2D.
=========================================

A percolação é o modelo canônico de transição de fase geométrica e um
"autômato celular estático": cada sítio de uma rede LxL é ocupado de
forma independente com probabilidade ``p``. Sítios ocupados vizinhos
(vizinhança de von Neumann) formam **aglomerados** (clusters). Existe
uma probabilidade crítica ``p_c`` tal que:

  * p < p_c : apenas aglomerados finitos (nenhum atravessa a rede);
  * p > p_c : surge um aglomerado infinito que "percola" (atravessa a
              rede de um lado ao outro).

Para a rede quadrada em 2D, o valor conhecido é ``p_c ≈ 0,592746``.
Exatamente em ``p_c`` o aglomerado percolante é um objeto **fractal**,
com dimensão ``D = 91/48 ≈ 1,896``.

Este é o mesmo mecanismo que governa o limiar de um surto epidêmico
espacial (ver ``forest_fire.py``): abaixo do limiar a "infecção" morre;
acima dele, ela varre toda a rede.

Referências:
  * Stauffer, D. & Aharony, A. "Introduction to Percolation Theory".
  * Newman, M. E. J. & Ziff, R. M. "Efficient Monte Carlo algorithm and
    high-precision results for percolation", PRL 85, 4104 (2000).
  * Sedgewick & Wayne, Princeton CS126, aula sobre percolação (P4).
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage

# Conectividade de von Neumann (4 vizinhos) para a rotulagem de clusters.
_VON_NEUMANN_STRUCT = np.array([[0, 1, 0],
                                [1, 1, 1],
                                [0, 1, 0]], dtype=int)


def occupy(L: int, p: float, rng: np.random.Generator) -> np.ndarray:
    """Gera uma rede LxL com sítios ocupados (1) com probabilidade p."""
    return (rng.random((L, L)) < p).astype(np.int8)


def label_clusters(grid: np.ndarray) -> tuple[np.ndarray, int]:
    """Rotula os aglomerados conexos (von Neumann). Devolve (labels, n)."""
    labels, n = ndimage.label(grid, structure=_VON_NEUMANN_STRUCT)
    return labels, n


def spans(labels: np.ndarray) -> bool:
    """Verdadeiro se algum aglomerado toca as bordas superior e inferior."""
    top = set(np.unique(labels[0, :])) - {0}
    bottom = set(np.unique(labels[-1, :])) - {0}
    return len(top & bottom) > 0


def largest_cluster_mask(grid: np.ndarray) -> np.ndarray:
    """Máscara booleana do maior aglomerado da rede."""
    labels, n = label_clusters(grid)
    if n == 0:
        return np.zeros_like(grid, dtype=bool)
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0  # ignora o "fundo" (rótulo 0)
    biggest = sizes.argmax()
    return labels == biggest


def spanning_probability(L: int, p: float, trials: int,
                         rng: np.random.Generator) -> float:
    """Fração de redes (em ``trials`` amostras) que percolam na densidade p."""
    hits = 0
    for _ in range(trials):
        grid = occupy(L, p, rng)
        labels, _ = label_clusters(grid)
        if spans(labels):
            hits += 1
    return hits / trials


def sweep_threshold(L: int, ps: np.ndarray, trials: int,
                    rng: np.random.Generator) -> np.ndarray:
    """Varre uma faixa de densidades e devolve P(percolar) para cada p."""
    return np.array([spanning_probability(L, p, trials, rng) for p in ps])


def estimate_pc(ps: np.ndarray, probs: np.ndarray) -> float:
    """Estima p_c como o ponto onde P(percolar) cruza 1/2 (interpolação)."""
    # Procura o primeiro par de pontos que cruza 0.5 e interpola linearmente.
    for i in range(1, len(ps)):
        if probs[i - 1] < 0.5 <= probs[i]:
            x0, x1 = ps[i - 1], ps[i]
            y0, y1 = probs[i - 1], probs[i]
            return float(x0 + (0.5 - y0) * (x1 - x0) / (y1 - y0))
    # fallback: densidade de maior derivada
    return float(ps[np.argmax(np.gradient(probs))])


# Valores teóricos de referência (rede quadrada 2D).
PC_THEORETICAL = 0.592746        # limiar de percolação de sítios
DF_SPANNING_CLUSTER = 91 / 48    # ≈ 1.8958 : dimensão fractal em p_c


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    # Longe do limiar o comportamento deve ser claro.
    p_lo = spanning_probability(64, 0.45, 40, rng)
    p_hi = spanning_probability(64, 0.75, 40, rng)
    print(f"P(percolar | p=0.45) = {p_lo:.2f}  (esperado ~0)")
    print(f"P(percolar | p=0.75) = {p_hi:.2f}  (esperado ~1)")
    assert p_lo < 0.2 and p_hi > 0.8, "comportamento de limiar inesperado"
    print("Percolação de sítios: OK")
