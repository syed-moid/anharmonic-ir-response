# Anharmonic IR Response: Reproducible Data and Scripts for Mode-Resolved Dielectric Susceptibility in Perovskites

Reproducible data and analysis scripts accompanying the manuscript
**"Mode-Resolved Anharmonic Framework for Dielectric Susceptibility and Infrared
Absorption in Disordered Polar Crystals"** (BaTiO₃ and SrTiO₃).

The manuscript develops a mode-resolved, **provenance-aware** response framework
that propagates independently specified phonon data (mode frequencies, oscillator
strengths, and linewidth reference data) into the one-phonon dielectric
susceptibility and infrared absorption — keeping a clear separation between
inputs, fitted intermediates, and outputs.

This repository regenerates the temperature-dependent phonon-linewidth tables
and the BaTiO₃ soft-mode figure of the manuscript **directly from committed
reference data**, with a single command, so the central quantitative claims can
be independently checked.

---

## Reproducibility target

> Running three commands regenerates **Table 5**, **Table 5a**, and the
> **BaTiO₃ soft-mode figure** from the committed CSV files.

```bash
python scripts/validate_bto_linewidths.py   # BaTiO3: CSV -> Table 5a + Table 5 (BTO rows)
python scripts/validate_sto_literature.py   # SrTiO3: literature -> Table 5 (STO rows)
python scripts/make_tables.py               # -> tables/table5.md, table5a.md (+ .csv)
python scripts/make_figures.py              # -> figures/fig_bto_soft_mode.png (+ linewidth fit)
```

or simply:

```bash
make reproduce      # runs validation + tables + figures
make test           # pytest regression check against the manuscript Table 5
```

The validation scripts **exit non-zero** if the fitted coefficients drift from
the manuscript Table 5 values, so they double as regression checks.

---

## What is reproduced, and from what

| Output | Source data (committed) | Method |
|---|---|---|
| **Table 5a** — BaTiO₃ Γ^ref(T), 100–600 K | `data/raw/BTO/phonon_modes_*K.csv` | meV → THz conversion |
| **Table 5 (BaTiO₃ rows)** — A, B, C, Γ(300 K), R² | `data/raw/BTO/phonon_modes_*K.csv` | least-squares fit Γ(T)=A+BT+CT² |
| **Table 5 (SrTiO₃ rows)** | `data/raw/literature/SrTiO3_linewidths_literature.csv` | least-squares fit of published linewidths |
| **BaTiO₃ soft-mode figure** — ω(T), Γ(T), Γ/ω(T) | `data/raw/BTO/phonon_modes_*K.csv` | direct plot + fit |

Verified reproduction (R² and coefficients match the manuscript to printed
precision): BaTiO₃ soft mode A = 0.091 THz, B = 2.3×10⁻⁴, C = 1.4×10⁻⁶,
R² = 0.985; SrTiO₃ soft mode A = 0.040, R² = 0.999. See `tests/`.

> **Note on the "Γ(300 K)" column.** The manuscript reports the *measured/computed
> 300 K data point* (soft mode 0.25 THz), not the polynomial evaluated at 300 K
> (≈0.29 THz). The soft mode's T-dependence departs slightly from a smooth
> polynomial near the transition (it is the lowest-R² mode), so the fit overshoots
> at 300 K. The scripts reproduce the data point, as the manuscript does; the
> distinction is documented in `scripts/common.py` (`ModeSeries.gamma_at`).

---

## Data provenance (read before reuse)

This repository is deliberately explicit about where each number comes from
(full detail in [`provenance/PROVENANCE.md`](provenance/PROVENANCE.md)):

- **BaTiO₃ `phonon_modes_*K.csv`** — **semi-empirical, INS-calibrated**
  mode-resolved linewidth and soft-mode reference data at six temperatures
  (100–600 K), in an inelastic-neutron-scattering-style tabular format (energies
  in meV, finite-Q labels, cross-sections in barns), adopted from the author's
  prior inelastic-neutron-scattering framework. As stated in the
  manuscript, these are **not** phonon self-energies computed in the present work;
  they are *inputs* to this repository (no generating script is included) and are
  fitted here to Γ(T)=A+BT+CT².
- **SrTiO₃ linewidths** — digitised from published anharmonic-phonon and
  experimental damping data (Tadano & Tsuneyuki 2015; Denisov et al. 1983;
  Servoin et al. 1980). SrTiO₃ is the *literature cross-validation* material.
- **Shirane neutron spectra** (`ShiraneFig4a/4b.csv`) — digitised literature
  neutron energy-loss spectra, included as an experimental anchor.
- **Quantum ESPRESSO** — exploratory, **incomplete**, and **not used** to
  generate any manuscript table or figure. See
  [`provenance/quantum_espresso_exploratory/STATUS.md`](provenance/quantum_espresso_exploratory/STATUS.md).

---

## Repository layout

```
anharmonic-ir-response/
├── README.md
├── LICENSE                     MIT (code)
├── LICENSE-DATA                CC-BY-4.0 (data, figures, tables)
├── CITATION.cff
├── environment.yml             conda environment
├── requirements.txt            pip dependencies
├── pyproject.toml              package metadata / tooling
├── Makefile                    `make reproduce`, `make test`
├── data/
│   ├── raw/
│   │   ├── BTO/                phonon_modes_100K.csv ... 600K.csv (+ README)
│   │   └── literature/         SrTiO3_linewidths_literature.csv, Shirane*.csv (+ README)
│   └── processed/              fit outputs (regenerated)
├── scripts/
│   ├── common.py               constants, loaders, the A+BT+CT² fit
│   ├── validate_bto_linewidths.py
│   ├── validate_sto_literature.py
│   ├── make_tables.py
│   └── make_figures.py
├── figures/                    regenerated figures
├── tables/                     regenerated tables (md + csv)
├── notebooks/
├── manuscript/                 (manuscript PDF/DOCX distributed via the Zenodo
│                               deposit — not tracked in git)
├── provenance/
│   ├── PROVENANCE.md
│   └── quantum_espresso_exploratory/
└── tests/
    └── test_reproduce_table5.py
```

---

## Installation

```bash
# conda
conda env create -f environment.yml
conda activate anharmonic-ir-response

# or pip
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies are minimal: `numpy`, `matplotlib`, `pytest`.

---

## License

- **Code** (`scripts/`, `tests/`): MIT — see [`LICENSE`](LICENSE).
- **Data, figures, tables** (`data/`, `figures/`, `tables/`): CC-BY-4.0 — see
  [`LICENSE-DATA`](LICENSE-DATA). Please cite the manuscript and this repository.

## Citation

See [`CITATION.cff`](CITATION.cff). Please cite both the manuscript and the
archived release:

- **Repository:** <https://github.com/syed-moid/anharmonic-ir-response>
- **Archived release (Zenodo):** [10.5281/zenodo.20682813](https://doi.org/10.5281/zenodo.20682813)
