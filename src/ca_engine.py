"""
Motor genérico de Autômatos Celulares (AC) em 2D.
==================================================

Um autômato celular é definido por:
  1. uma rede de células (aqui, uma grade 2D);
  2. um conjunto finito de estados por célula;
  3. uma vizinhança (aqui, von Neumann ou Moore);
  4. uma regra de transição local, aplicada simultaneamente a todas as
     células (atualização síncrona).

Este módulo fornece uma implementação vetorizada (NumPy) que conta os
vizinhos de cada célula com deslocamentos de matriz (np.roll), evitando
laços explícitos em Python. Como demonstração canônica do motor,
incluímos o "Jogo da Vida" de Conway.

Referência: Wolfram, S. "A New Kind of Science" (2002); Gardner, M.
"The fantastic combinations of John Conway's new solitaire game 'Life'",
Scientific American (1970).
"""

from __future__ import annotations

import numpy as np

# Deslocamentos (dx, dy) das vizinhanças mais usadas em AC 2D.
VON_NEUMANN = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 4 vizinhos ortogonais
MOORE = VON_NEUMANN + [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # 8 vizinhos


def count_neighbors(grid: np.ndarray, neighborhood=MOORE, wrap: bool = True) -> np.ndarray:
    """Conta, para cada célula, quantos vizinhos estão "vivos" (valor != 0).

    Parameters
    ----------
    grid : np.ndarray
        Grade 2D de inteiros (0/1 tipicamente).
    neighborhood : list[tuple[int, int]]
        Lista de deslocamentos (dx, dy) que define a vizinhança.
    wrap : bool
        Se True, a rede é toroidal (bordas periódicas). Se False, as
        bordas são tratadas como zero (mundo finito).

    Returns
    -------
    np.ndarray
        Matriz com a contagem de vizinhos vivos de cada célula.
    """
    alive = (grid != 0).astype(np.int32)
    total = np.zeros_like(alive)
    for dx, dy in neighborhood:
        if wrap:
            total += np.roll(np.roll(alive, dx, axis=0), dy, axis=1)
        else:
            shifted = np.zeros_like(alive)
            xs_src = slice(max(0, -dx), alive.shape[0] - max(0, dx))
            ys_src = slice(max(0, -dy), alive.shape[1] - max(0, dy))
            xs_dst = slice(max(0, dx), alive.shape[0] - max(0, -dx))
            ys_dst = slice(max(0, dy), alive.shape[1] - max(0, -dy))
            shifted[xs_dst, ys_dst] = alive[xs_src, ys_src]
            total += shifted
    return total


class CellularAutomaton2D:
    """Motor genérico de AC 2D com atualização síncrona.

    A regra de transição é uma função ``rule(grid, neighbors) -> new_grid``.
    Isso mantém o motor agnóstico ao modelo: basta trocar a regra para
    obter Jogo da Vida, majority voting, modelos de propagação, etc.
    """

    def __init__(self, grid: np.ndarray, rule, neighborhood=MOORE, wrap: bool = True):
        self.grid = np.array(grid, dtype=np.int32)
        self.rule = rule
        self.neighborhood = neighborhood
        self.wrap = wrap
        self.generation = 0

    def step(self) -> np.ndarray:
        """Avança o AC em uma geração e devolve o novo estado."""
        neighbors = count_neighbors(self.grid, self.neighborhood, self.wrap)
        self.grid = self.rule(self.grid, neighbors).astype(np.int32)
        self.generation += 1
        return self.grid

    def run(self, steps: int) -> list[np.ndarray]:
        """Executa ``steps`` gerações, devolvendo a história completa."""
        history = [self.grid.copy()]
        for _ in range(steps):
            history.append(self.step().copy())
        return history


# --------------------------------------------------------------------------
# Regra de demonstração: Jogo da Vida de Conway (B3/S23)
# --------------------------------------------------------------------------
def game_of_life_rule(grid: np.ndarray, neighbors: np.ndarray) -> np.ndarray:
    """Regra B3/S23: nasce com 3 vizinhos; sobrevive com 2 ou 3."""
    born = (grid == 0) & (neighbors == 3)
    survive = (grid == 1) & ((neighbors == 2) | (neighbors == 3))
    return (born | survive).astype(np.int32)


def random_grid(shape, density: float, rng: np.random.Generator) -> np.ndarray:
    """Gera uma grade aleatória com dada densidade de células vivas."""
    return (rng.random(shape) < density).astype(np.int32)


if __name__ == "__main__":
    # Autoteste rápido: um "glider" do Jogo da Vida deve se transladar.
    rng = np.random.default_rng(0)
    g = np.zeros((16, 16), dtype=np.int32)
    g[1, 2] = g[2, 3] = g[3, 1] = g[3, 2] = g[3, 3] = 1  # glider
    ca = CellularAutomaton2D(g, game_of_life_rule, MOORE, wrap=True)
    hist = ca.run(4)
    print("Células vivas por geração:", [int(h.sum()) for h in hist])
    assert hist[0].sum() == hist[4].sum() == 5, "glider deve conservar 5 células"
    print("Motor de AC 2D: OK")
