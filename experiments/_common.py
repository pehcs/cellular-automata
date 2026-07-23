"""Infraestrutura comum aos experimentos (path, pastas, salvamento)."""
from __future__ import annotations

import os
import sys

# Permite importar o pacote ``src`` ao rodar os scripts diretamente.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

FIG_DIR = os.path.join(REPO_ROOT, "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def figpath(name: str) -> str:
    return os.path.join(FIG_DIR, name)
