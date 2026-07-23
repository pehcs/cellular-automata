"""
Dimensão fractal por contagem de caixas (box-counting).
=======================================================

A "dimensão de similaridade" de um conjunto auto-similar generaliza a
noção de dimensão inteira. Para um padrão que se repete em várias
escalas, cobrimos o conjunto com caixas de lado ``s`` e contamos quantas
caixas ``N(s)`` contêm ao menos um ponto ocupado. Se o conjunto é
fractal, então

        N(s) ~ s^(-D)      =>      D = - d[log N] / d[log s],

ou seja, D é a inclinação (com sinal trocado) da reta ajustada em um
gráfico log-log de N(s) contra s. D é a **dimensão fractal** (ou de
Minkowski–Bouligand), que coincide com a dimensão de similaridade nos
fractais determinísticos clássicos.

Valores de referência:
  * Triângulo de Sierpiński (Regra 90):  D = log 3 / log 2 ≈ 1,585
  * Cluster percolante incipiente (2D):  D = 91/48        ≈ 1,896
"""

from __future__ import annotations

import numpy as np


def default_box_sizes(shape, frac_max: float = 0.25) -> list[int]:
    """Potências de 2 de 1 até ``frac_max`` do menor lado da imagem.

    Limitar o maior tamanho de caixa a ~1/4 da imagem evita o regime de
    saturação de tamanho finito (poucas caixas cobrindo tudo), que
    achata a reta log-log e subestima a dimensão.
    """
    m = min(shape)
    max_pow = int(np.floor(np.log2(max(2.0, m * frac_max))))
    return [2 ** k for k in range(0, max_pow + 1)]


def box_count(mask: np.ndarray, box_sizes=None) -> tuple[np.ndarray, np.ndarray]:
    """Conta caixas ocupadas para vários tamanhos de caixa.

    Parameters
    ----------
    mask : np.ndarray (2D, booleano/0-1)
        Conjunto de pontos ocupados (True/1 = ocupado).
    box_sizes : sequência de int, opcional
        Lados das caixas. Por padrão usa potências de 2 até ~1/4 do
        menor lado da imagem (regime de escala robusto).

    Returns
    -------
    (sizes, counts) : tuple[np.ndarray, np.ndarray]
        Tamanhos de caixa e número de caixas ocupadas correspondentes.
    """
    mask = np.asarray(mask) != 0
    if box_sizes is None:
        box_sizes = default_box_sizes(mask.shape)
    sizes, counts = [], []
    for s in box_sizes:
        if s < 1 or s > min(mask.shape):
            continue
        # Recorta para um múltiplo de s e agrupa em blocos s x s.
        nx = (mask.shape[0] // s) * s
        ny = (mask.shape[1] // s) * s
        sub = mask[:nx, :ny]
        blocks = sub.reshape(nx // s, s, ny // s, s)
        occupied = blocks.any(axis=(1, 3))  # caixa "ocupada" se tem >=1 ponto
        n = int(occupied.sum())
        if n > 0:
            sizes.append(s)
            counts.append(n)
    return np.array(sizes), np.array(counts)


def fractal_dimension(mask: np.ndarray, box_sizes=None,
                      drop_smallest: bool = True, min_count: int = 16) -> dict:
    """Estima a dimensão fractal por regressão linear em escala log-log.

    O ajuste é feito apenas na **faixa de escala confiável**, excluindo:
      * a escala de 1 pixel (``drop_smallest``), sensível à discretização
        e a desalinhamentos com a grade de caixas;
      * caixas grandes com pouquíssimas ocupações (``N < min_count``), no
        regime de saturação de tamanho finito.
    Todos os pontos são devolvidos para plotagem; apenas os do regime de
    escala entram na regressão (campos ``*_fit``).

    Returns
    -------
    dict com chaves:
        'dimension' : float   -- inclinação (dimensão fractal estimada)
        'intercept' : float
        'r_squared' : float   -- qualidade do ajuste (só na faixa usada)
        'sizes', 'counts'                 : todos os pontos
        'log_inv_size', 'log_count'       : todos os pontos (log)
        'sizes_fit', 'counts_fit'         : pontos usados na regressão
        'log_inv_size_fit', 'log_count_fit'
    """
    sizes, counts = box_count(mask, box_sizes)
    if len(sizes) < 2:
        raise ValueError("Poucos pontos de escala para estimar a dimensão.")

    # Seleção do regime de escala confiável.
    keep = counts >= min_count
    if drop_smallest:
        keep = keep & (sizes > 1)
    if keep.sum() < 2:                      # segurança: usa tudo se filtrar demais
        keep = np.ones_like(sizes, dtype=bool)

    xs, ys = sizes[keep], counts[keep]
    x = np.log(1.0 / xs)   # log(1/s)
    y = np.log(ys)         # log N(s)
    D, b = np.polyfit(x, y, 1)
    y_hat = D * x + b
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {
        "dimension": float(D),
        "intercept": float(b),
        "r_squared": float(r2),
        "sizes": sizes,
        "counts": counts,
        "log_inv_size": np.log(1.0 / sizes),
        "log_count": np.log(counts),
        "sizes_fit": xs,
        "counts_fit": ys,
        "log_inv_size_fit": x,
        "log_count_fit": y,
    }


if __name__ == "__main__":
    # Autoteste: um quadrado cheio deve ter dimensão ~2.
    full = np.ones((256, 256), dtype=int)
    d = fractal_dimension(full)
    print(f"Quadrado cheio -> D = {d['dimension']:.3f} (esperado ~2.0)")
    # Uma linha deve ter dimensão ~1.
    line = np.zeros((256, 256), dtype=int)
    line[128, :] = 1
    d = fractal_dimension(line)
    print(f"Linha reta     -> D = {d['dimension']:.3f} (esperado ~1.0)")
