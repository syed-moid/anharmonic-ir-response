# Literature reference data (SrTiO₃)

SrTiO₃ is the **literature cross-validation** material in the manuscript: its
phonon linewidths are taken from published anharmonic-phonon calculations and
experimental damping data, then fit to the same Γ(T) = A + B·T + C·T² form.

## `SrTiO3_linewidths_literature.csv`

Soft-mode (TO1) and TO2 HWHM linewidths at 100–500 K, digitised from the
sources below.

| column | meaning | units |
|---|---|---|
| `mode` | manuscript label (`TO1 (soft)`, `TO2`) | — |
| `temperature_K` | temperature | K |
| `Gamma_THz` | HWHM linewidth | THz |
| `omega_THz` | mode frequency | THz |
| `source` | originating reference(s) | — |

Fitting these points reproduces the SrTiO₃ rows of Table 5 (R² > 0.999).

## `ShiraneFig4a.csv`, `ShiraneFig4b.csv`

Digitised neutron energy-loss spectra (counts per 15 min vs energy in meV) from
a Shirane et al. figure, included as an experimental anchor for the soft-mode
behaviour. Columns: `NEUTRON ENERGY LOSS meV`, `Neutrons per 15 Minutes`.

## Sources (refs [25–27] in the manuscript)

- **[25]** T. Tadano and S. Tsuneyuki, *Self-consistent phonon calculations of
  lattice dynamical properties in cubic SrTiO₃*, Phys. Rev. B **92**, 054301
  (2015). https://doi.org/10.1103/PhysRevB.92.054301
- **[26]** V. N. Denisov, B. N. Mavrin, V. B. Podobedov, *Hyper-Raman scattering
  in SrTiO₃*, J. Raman Spectrosc. **14**, 276 (1983).
  https://doi.org/10.1002/jrs.1250140413
- **[27]** J. L. Servoin, Y. Luspin, F. Gervais, *Infrared dispersion in SrTiO₃
  at high temperature*, Phys. Rev. B **22**, 5501 (1980).
  https://doi.org/10.1103/PhysRevB.22.5501

These underlying data remain the property of their original authors/publishers;
reusers must cite the original sources (see `../../LICENSE-DATA`).
