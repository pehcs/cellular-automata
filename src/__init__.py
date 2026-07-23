"""
Autômatos Celulares, Percolação e Dimensão Fractal
==================================================

Pacote com um motor genérico de autômatos celulares (AC) em 2D e um
conjunto de modelos clássicos usados para estudar auto-organização,
transições de fase (percolação) e auto-similaridade (dimensão fractal).

Módulos
-------
ca_engine     : motor genérico de AC 2D (Moore / von Neumann) + Jogo da Vida
elementary_ca : autômatos celulares elementares 1D (regras de Wolfram)
percolation   : percolação de sítios, rotulagem de clusters e limiar p_c
forest_fire   : propagação tipo fogo/epidemia (SIR espacial) em rede
fractal       : dimensão fractal por contagem de caixas (box-counting)
visualize     : utilitários de visualização

Autor: (preencher)  ---  Disciplina: Autômatos Celulares
"""

from . import ca_engine, elementary_ca, percolation, forest_fire, fractal, visualize

__all__ = [
    "ca_engine",
    "elementary_ca",
    "percolation",
    "forest_fire",
    "fractal",
    "visualize",
]

__version__ = "1.0.0"
