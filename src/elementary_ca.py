"""
Autômatos Celulares Elementares (1D) — Regras de Wolfram.
=========================================================

Um AC elementar é o AC mais simples possível: rede 1D, dois estados por
célula (0/1) e vizinhança de raio 1 (a própria célula mais os dois
vizinhos imediatos). Cada configuração de 3 células (2^3 = 8 padrões)
mapeia para um novo estado, e as 8 saídas formam um número de 8 bits:
por isso há exatamente 2^8 = 256 "regras", numeradas de 0 a 255
(numeração de Wolfram).

Empilhando as gerações sucessivas como linhas, obtemos um padrão 2D.
Algumas regras produzem estruturas auto-similares (fractais). O exemplo
mais célebre é a **Regra 90**, que a partir de uma única célula gera o
**Triângulo de Sierpiński**, cuja dimensão fractal teórica é
log(3)/log(2) ≈ 1,585. Isso liga diretamente os AC ao conceito de
"dimensão de similaridade" estudado no curso.

Referência: Wolfram, S. "Statistical mechanics of cellular automata",
Rev. Mod. Phys. 55, 601 (1983).
"""

from __future__ import annotations

import numpy as np


def rule_table(rule_number: int) -> np.ndarray:
    """Converte um número de regra (0-255) em tabela de transição.

    A saída ``table[k]`` (k = 0..7) é o novo estado da célula quando a
    tripla (esquerda, centro, direita) vale, em binário, ``7 - k`` no
    esquema de Wolfram. Usamos indexação por peso 4*L + 2*C + R.
    """
    if not (0 <= rule_number <= 255):
        raise ValueError("O número da regra deve estar entre 0 e 255.")
    # bit i (i = 0..7) da regra define a saída para o padrão i = 4L+2C+R.
    return np.array([(rule_number >> i) & 1 for i in range(8)], dtype=np.int8)


def evolve(rule_number: int, width: int, steps: int,
           seed: str = "single", rng: np.random.Generator | None = None) -> np.ndarray:
    """Evolui um AC elementar e devolve o diagrama espaço-tempo.

    Parameters
    ----------
    rule_number : int
        Regra de Wolfram (0-255).
    width : int
        Número de células (rede 1D com bordas periódicas).
    steps : int
        Número de gerações (linhas) a gerar.
    seed : {"single", "random"}
        "single": uma única célula viva no centro (gera fractais nítidos).
        "random": condição inicial aleatória.
    rng : np.random.Generator, opcional
        Fonte de aleatoriedade (para reprodutibilidade).

    Returns
    -------
    np.ndarray
        Matriz (steps x width) com o histórico de estados (0/1).
    """
    table = rule_table(rule_number)
    row = np.zeros(width, dtype=np.int8)
    if seed == "single":
        row[width // 2] = 1
    elif seed == "random":
        rng = rng or np.random.default_rng()
        row = (rng.random(width) < 0.5).astype(np.int8)
    else:
        raise ValueError("seed deve ser 'single' ou 'random'.")

    out = np.zeros((steps, width), dtype=np.int8)
    out[0] = row
    for t in range(1, steps):
        left = np.roll(row, 1)
        right = np.roll(row, -1)
        idx = (left << 2) | (row << 1) | right  # peso 4L + 2C + R
        row = table[idx]
        out[t] = row
    return out


# Regras notáveis, para referência no artigo e nos experimentos.
NOTABLE_RULES = {
    30: "Caótica (usada como gerador pseudoaleatório na Wolfram|Alpha)",
    90: "Triângulo de Sierpiński (auto-similar, fractal)",
    110: "Universal (capaz de computação universal — Cook, 2004)",
    184: "Modelo de tráfego / fluxo",
}


if __name__ == "__main__":
    # Autoteste: a Regra 90 deve satisfazer a recorrência XOR dos vizinhos.
    img = evolve(90, width=64, steps=32, seed="single")
    # Regra 90: novo estado = esquerda XOR direita.
    row0 = img[0].astype(int)
    left = np.roll(row0, 1)
    right = np.roll(row0, -1)
    assert np.array_equal(img[1], (left ^ right).astype(np.int8)), "Regra 90 falhou"
    print("AC elementar (Regra 90 = XOR dos vizinhos): OK")
    print("Densidade de células vivas na última linha:", img[-1].mean())
