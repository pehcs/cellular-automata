"""
Utilitários de visualização (paletas e estilos consistentes).
=============================================================

Centraliza cores e um estilo comum para que todas as figuras do artigo
tenham a mesma identidade visual.
"""

from __future__ import annotations

import matplotlib as mpl
from matplotlib.colors import ListedColormap

# Paleta acessível (segura para daltonismo) usada em todo o projeto.
INK = "#1b1b3a"
ACCENT = "#3b6ea5"      # azul
ACCENT2 = "#c1440e"     # laranja-queimado
GRID_BG = "#f4f1ea"

# Colormaps categóricos para os modelos.
# Fogo/epidemia: vazio (bege) / árvore (verde) / queimando (laranja).
FOREST_CMAP = ListedColormap(["#efe7d3", "#2e7d32", "#c1440e"])
# Percolação: vazio / ocupado / maior cluster destacado.
PERCOLATION_CMAP = ListedColormap(["#efe7d3", "#9fb3c8", "#c1440e"])
BINARY_CMAP = ListedColormap(["#faf7f0", INK])


def apply_style():
    """Aplica um estilo matplotlib limpo e uniforme."""
    mpl.rcParams.update({
        "figure.dpi": 130,
        "savefig.dpi": 200,
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.grid": False,
        "figure.facecolor": "white",
        "savefig.bbox": "tight",
    })
