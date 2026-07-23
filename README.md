# Autômatos Celulares, Percolação e Dimensão Fractal

Simulação em **Python** de autômatos celulares (AC) e do fenômeno de
**percolação**, com medição da **dimensão fractal** (dimensão de
similaridade) dos padrões gerados. Projeto da disciplina de
**Autômatos Celulares** (BSI/UFRPE — Prof. Jones Albuquerque).

> **Ideia central.** Autômatos celulares — regras locais simples aplicadas
> a uma grade — geram, sozinhos, estruturas complexas e *auto-similares*.
> Este repositório mostra três faces do mesmo fenômeno: (1) fractais
> determinísticos (Regra 90 → triângulo de Sierpiński), (2) a transição de
> fase da percolação e o aglomerado percolante fractal, e (3) um AC de
> propagação (fogo/epidemia) cujo limiar de surto é governado pela mesma
> criticalidade da percolação. A "dimensão de similaridade" é o fio que
> costura tudo.

**Artigo:** [`docs/artigo.pdf`](docs/artigo.pdf)

---

## Resultados principais (reprodutíveis)

| Grandeza medida | Valor obtido | Valor teórico | Erro |
|---|---|---|---|
| Dimensão fractal da Regra 90 (Sierpiński) | **1,585** | log 3 / log 2 ≈ 1,585 | 0,0 % |
| Limiar de percolação de sítios `p_c` | **0,5917** | 0,592746 | 0,2 % |
| Dimensão fractal do aglomerado percolante em `p_c` | **1,856 ± 0,024** | 91/48 ≈ 1,896 | 2,1 % |

> A pequena diferença na dimensão do aglomerado é o esperado **efeito de
> tamanho finito**: o valor 91/48 é atingido apenas no limite `L → ∞`.

---

## Estrutura do projeto

```
cellular-automata-percolation/
├── src/                       # biblioteca (o "motor")
│   ├── ca_engine.py           # motor genérico de AC 2D + Jogo da Vida
│   ├── elementary_ca.py       # AC elementares 1D (regras de Wolfram)
│   ├── percolation.py         # percolação de sítios, clusters, limiar p_c
│   ├── forest_fire.py         # AC de propagação fogo/epidemia (SIR espacial)
│   ├── fractal.py             # dimensão fractal por box-counting
│   └── visualize.py           # paletas e estilo das figuras
├── experiments/               # scripts que geram as figuras do artigo
│   ├── run_all.py             # reproduz TUDO (figuras + results.json)
│   ├── fig_elementary_ca.py
│   ├── fig_rule90_fractal.py
│   ├── fig_percolation_threshold.py
│   ├── fig_percolation_fractal.py
│   └── fig_forest_fire.py
├── figures/                   # PNGs gerados + results.json
├── docs/                      # artigo (PDF/DOCX)
├── requirements.txt
├── LICENSE
└── README.md
```

## Instalação

```bash
pip install -r requirements.txt
```

Requer apenas Python 3.9+, NumPy, SciPy e Matplotlib.

## Uso

Reproduzir todas as figuras e resultados numéricos do artigo:

```bash
python experiments/run_all.py
```

As figuras são gravadas em `figures/` e um resumo numérico em
`figures/results.json`. Cada script de figura também roda isoladamente
(ex.: `python experiments/fig_rule90_fractal.py`).

Usar a biblioteca diretamente:

```python
import numpy as np
from src import elementary_ca as eca, percolation as perc, fractal

# Triângulo de Sierpiński (Regra 90) e sua dimensão fractal
img = eca.evolve(90, width=513, steps=256, seed="single")
print(fractal.fractal_dimension(img)["dimension"])   # ~1.585

# Percolação: a rede percola nesta densidade?
rng = np.random.default_rng(0)
grid = perc.occupy(256, p=0.60, rng=rng)
labels, _ = perc.label_clusters(grid)
print("percola?", perc.spans(labels))
```

## Modelos implementados

- **AC elementares 1D (Wolfram).** As 256 regras; destaque para a Regra 90
  (fractal), 30 (caótica), 110 (universal) e 184 (tráfego).
- **Percolação de sítios 2D.** Ocupação aleatória, rotulagem de aglomerados
  por vizinhança de von Neumann (SciPy), detecção de aglomerado percolante e
  estimativa de `p_c` por Monte Carlo com efeito de tamanho.
- **AC de propagação (fogo/epidemia).** Modelo SIR espacial de 3 estados
  (suscetível/infectado/removido) com limiar de surto ligado a `p_c`.
- **Jogo da Vida** (em `ca_engine.py`) como demonstração do motor genérico.
- **Dimensão fractal.** Box-counting com seleção automática da faixa de
  escala confiável.

## Reprodutibilidade

Todas as simulações usam sementes fixas (`numpy.random.default_rng`), então
`run_all.py` reproduz exatamente os mesmos números e figuras.

## Referências

1. Wolfram, S. *A New Kind of Science*. Wolfram Media, 2002.
2. Stauffer, D.; Aharony, A. *Introduction to Percolation Theory*. 2ª ed.,
   Taylor & Francis, 1994.
3. Newman, M. E. J.; Ziff, R. M. "Efficient Monte Carlo algorithm and
   high-precision results for percolation". *Phys. Rev. Lett.* **85**, 4104 (2000).
4. Gardner, M. "Mathematical Games: The fantastic combinations of John
   Conway's new solitaire game 'Life'". *Scientific American* (1970).
5. Sedgewick, R.; Wayne, K. *Percolation* — Princeton CS126 (P4).

## Licença

MIT — ver [LICENSE](LICENSE).
