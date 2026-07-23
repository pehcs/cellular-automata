"""
Propagação espacial tipo "fogo/epidemia" como Autômato Celular.
===============================================================

Este é um autômato celular *dinâmico* de três estados que ilustra, de
forma visual, a mesma transição de fase da percolação. Cada célula está
em um de três estados (modelo tipo SIR espacial):

    0 = VAZIO/RECUPERADO   (não pode mais pegar fogo / imune)
    1 = ÁRVORE/SUSCETÍVEL  (combustível disponível)
    2 = QUEIMANDO/INFECTADO (fonte ativa de propagação)

Regras locais (atualização síncrona, vizinhança de von Neumann):
    * uma célula QUEIMANDO passa a VAZIA na geração seguinte;
    * uma ÁRVORE passa a QUEIMAR se tiver ao menos um vizinho QUEIMANDO,
      com probabilidade de transmissão ``beta``;
    * células VAZIAS permanecem vazias.

Partindo de uma floresta com densidade ``p`` de árvores e uma única
faísca no centro, mede-se a fração final de território queimado. Há um
**limiar**: abaixo da densidade crítica, o fogo se extingue localmente;
acima dela, ele varre a floresta inteira — exatamente o análogo do
limiar epidêmico (R0 = 1) e do limiar de percolação ``p_c``.

Quando ``beta = 1`` a fronteira final do incêndio coincide com o
aglomerado de percolação de sítios que contém a faísca, unificando os
três modelos deste repositório.
"""

from __future__ import annotations

import numpy as np

EMPTY, TREE, BURNING = 0, 1, 2

_NEIGH = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # von Neumann


def initial_forest(L: int, density: float, rng: np.random.Generator) -> np.ndarray:
    """Floresta LxL com dada densidade de árvores e uma faísca no centro."""
    grid = (rng.random((L, L)) < density).astype(np.int8)  # 1 = árvore
    c = L // 2
    if grid[c, c] == EMPTY:
        grid[c, c] = TREE  # garante combustível no ponto de ignição
    grid[c, c] = BURNING
    return grid


def _burning_neighbors(grid: np.ndarray) -> np.ndarray:
    """Conta vizinhos em chamas (von Neumann), sem bordas periódicas."""
    burning = (grid == BURNING).astype(np.int16)
    total = np.zeros_like(burning)
    for dx, dy in _NEIGH:
        shifted = np.zeros_like(burning)
        xs = slice(max(0, -dx), burning.shape[0] - max(0, dx))
        ys = slice(max(0, -dy), burning.shape[1] - max(0, dy))
        xd = slice(max(0, dx), burning.shape[0] - max(0, -dx))
        yd = slice(max(0, dy), burning.shape[1] - max(0, -dy))
        shifted[xd, yd] = burning[xs, ys]
        total += shifted
    return total


def step(grid: np.ndarray, beta: float, rng: np.random.Generator) -> np.ndarray:
    """Uma geração do AC de propagação."""
    new = grid.copy()
    # 1) o que estava queimando vira vazio (recuperado).
    new[grid == BURNING] = EMPTY
    # 2) árvores com vizinho em chamas pegam fogo com probabilidade beta.
    exposed = (grid == TREE) & (_burning_neighbors(grid) > 0)
    if beta >= 1.0:
        ignite = exposed
    else:
        ignite = exposed & (rng.random(grid.shape) < beta)
    new[ignite] = BURNING
    return new


def simulate(L: int, density: float, beta: float, rng: np.random.Generator,
             max_steps: int = 10_000, record: bool = False):
    """Roda um incêndio até se extinguir. Devolve estatísticas do surto.

    Returns
    -------
    dict com:
        'burned_fraction' : fração do território que chegou a queimar
        'reached_border'  : se o fogo alcançou alguma borda da rede
        'duration'        : número de gerações até se extinguir
        'frames'          : lista de estados (apenas se record=True)
    """
    grid = initial_forest(L, density, rng)
    total_cells = L * L
    ever_burned = (grid == BURNING)
    frames = [grid.copy()] if record else None

    steps = 0
    while np.any(grid == BURNING) and steps < max_steps:
        grid = step(grid, beta, rng)
        ever_burned |= (grid == BURNING)
        if record:
            frames.append(grid.copy())
        steps += 1

    reached_border = bool(
        ever_burned[0, :].any() or ever_burned[-1, :].any()
        or ever_burned[:, 0].any() or ever_burned[:, -1].any()
    )
    return {
        "burned_fraction": float(ever_burned.sum() / total_cells),
        "reached_border": reached_border,
        "duration": steps,
        "ever_burned": ever_burned,
        "frames": frames,
    }


def outbreak_curve(L: int, densities: np.ndarray, beta: float, trials: int,
                   rng: np.random.Generator) -> np.ndarray:
    """Fração média queimada em função da densidade de árvores."""
    out = []
    for d in densities:
        vals = [simulate(L, d, beta, rng)["burned_fraction"] for _ in range(trials)]
        out.append(np.mean(vals))
    return np.array(out)


if __name__ == "__main__":
    rng = np.random.default_rng(2)
    lo = simulate(101, 0.40, 1.0, rng)["burned_fraction"]
    hi = simulate(101, 0.75, 1.0, rng)["burned_fraction"]
    print(f"Queimado | densidade 0.40 = {lo:.3f} (esperado pequeno)")
    print(f"Queimado | densidade 0.75 = {hi:.3f} (esperado grande)")
    print("AC de propagação (fogo/epidemia): OK")
