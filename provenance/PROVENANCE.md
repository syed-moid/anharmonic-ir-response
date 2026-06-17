# Data provenance

This repository is intentionally explicit about the origin and status of every
quantity used to produce the manuscript's linewidth tables and soft-mode
figure. The goal is full transparency about **what was computed, what was taken
from the literature, and what is reference data fit by the model.**

## Summary

| Quantity | Material | Source | Used for | Reproducible here? |
|---|---|---|---|---|
| Γ^pert(T) linewidths | BaTiO₃ | `data/raw/BTO/phonon_modes_*K.csv` (results-level reference data) | Table 5a, Table 5 (BTO), soft-mode fig | **Yes** — CSV → fit |
| Soft-mode ω(T) | BaTiO₃ | `data/raw/BTO/phonon_modes_*K.csv` | soft-mode figure | **Yes** |
| Γ(T) linewidths | SrTiO₃ | published data, digitised (`data/raw/literature/`) | Table 5 (STO) | **Yes** — literature → fit |
| Neutron spectra | — | Shirane (digitised literature) | experimental anchor | included, not fit |
| SCF ground states | BaTiO₃, SrTiO₃ defect supercells | Quantum ESPRESSO (exploratory) | **none** | n/a — incomplete |

## BaTiO₃ linewidths and soft-mode frequencies

The files `data/raw/BTO/phonon_modes_*K.csv` are **results-level, mode-resolved
reference data**: phonon frequencies and HWHM linewidths at six temperatures
(100–600 K), tabulated in an inelastic-neutron-scattering-style format (energies
in meV, finite-Q mode labels, scattering cross-sections in barns).

- Fitting Γ(T) = A + B·T + C·T² to the soft mode, TO2, and TO3 reproduces the
  BaTiO₃ rows of **Table 5** (A = 0.091/0.069/0.094 THz; R² = 0.985/0.998/0.992)
  and the points of **Table 5a**, to the printed precision (`make test`).
- The soft-mode frequency column (ω) of these files reproduces the manuscript's
  soft-mode softening curve: 2.71 THz at 100 K → ~0.85 THz near 400 K, with
  partial recovery above T_c (Figure: `figures/fig_bto_soft_mode.png`).

**Provenance note.** These CSVs are *inputs* to this repository: no script
here generates them from first principles. They are results-level finite-Q
reference data in a neutron-scattering tabular format, adopted as documented
linewidth inputs rather than as native Quantum ESPRESSO zone-center
bubble-diagram self-energy outputs.

## SrTiO₃ linewidths

Digitised from published anharmonic-phonon calculations and experimental damping
data (Tadano & Tsuneyuki 2015; Denisov et al. 1983; Servoin et al. 1980) — see
`data/raw/literature/README.md`. SrTiO₃ functions as a literature
cross-validation, not a from-scratch calculation here.

## Quantum ESPRESSO (exploratory, not used)

The `quantum_espresso_exploratory/` folder documents exploratory DFT/DFPT
calculations performed during manuscript development. **They did not produce any
table or figure in the manuscript.** Ground-state SCF calculations completed for
the defect supercells, but the phonon (DFPT) calculations did not converge to a
production-quality result, and no third-order force constants, phonon
self-energies, or converged linewidths were generated. See
[`quantum_espresso_exploratory/STATUS.md`](quantum_espresso_exploratory/STATUS.md).
Only small text inputs/outputs are included; large binary outputs
(wavefunctions, charge densities, `.save/`, scratch) are archived externally by
the author and referenced by checksum in
[`quantum_espresso_exploratory/checksums_external_raw_data.txt`](quantum_espresso_exploratory/checksums_external_raw_data.txt).
