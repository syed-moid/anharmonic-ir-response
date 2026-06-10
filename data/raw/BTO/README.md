# BaTiO₃ reference linewidth data

Files: `phonon_modes_100K.csv` … `phonon_modes_600K.csv` (one per temperature,
100–600 K in 100 K steps).

These are the **reference data fit by the manuscript** to obtain the BaTiO₃
rows of Table 5 and the points of Table 5a, and to draw the soft-mode figure.

## Columns

| column | meaning | units |
|---|---|---|
| `mode_name` | internal mode identifier | — |
| `label` | human-readable mode description (with Q) | — |
| `omega_Q_meV` | phonon frequency at wavevector Q | meV |
| `Gamma_Q_HWHM_meV` | half-width at half-maximum linewidth | meV |
| `Q_x, Q_y, Q_z` | reduced wavevector components | r.l.u. |
| `expected_peak_barns` | neutron scattering cross-section | barns |
| `mode_type` | classification (polar_soft, optical_high, acoustic, …) | — |
| `temperature_K` | temperature | K |

## Mode mapping (used by the scripts)

The three infrared-active TO modes used in the linewidth model map as:

| `mode_name` | manuscript label |
|---|---|
| `Mode_1_Ti-O_soft` | TO1 (soft) |
| `Mode_2_A-O_TO2_gamma` | TO2 |
| `Mode_3_A-O_TO2` | TO3 |

## Unit conversion

The analysis converts meV → THz with **1 meV = 0.24180 THz** (E = hν). Thus
Γ(THz) = `Gamma_Q_HWHM_meV` × 0.24180 and ω(THz) = `omega_Q_meV` × 0.24180.
For example, the soft mode at 300 K (`Gamma_Q_HWHM_meV` = 1.05) gives
Γ = 0.254 THz, matching Table 5a.

## Provenance

These are **results-level** tabular data (frequencies + HWHM linewidths at
finite Q), provided as inputs to this repository — no script here generates
them. They are in an inelastic-neutron-scattering-style format. See
[`../../../provenance/PROVENANCE.md`](../../../provenance/PROVENANCE.md) for the
full provenance discussion, including the relationship to the manuscript's
described perturbative self-energy methodology and to the exploratory
(incomplete) Quantum ESPRESSO calculations.
