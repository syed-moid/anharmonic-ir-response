# Quantum ESPRESSO exploratory inputs/outputs

This folder contains **small text inputs and selected text outputs** from
exploratory DFT/DFPT calculations. It exists for transparency only. **None of
these files were used to generate any manuscript table or figure.** Read
[`STATUS.md`](STATUS.md) first.

## Contents

```
quantum_espresso_exploratory/
├── STATUS.md                          status, caveats, what is excluded
├── checksums_external_raw_data.txt    SHA-256 of the large external raw files
├── BaTiO3_defect_2x2x2/
│   ├── scf.in    scf.out              SCF completed (JOB DONE)
│   └── ph.in     ph.out               DFPT crashed at startup (no dyn matrix)
└── SrTiO3_defect_2x2x2/
    ├── scf.in    scf.out              SCF completed (JOB DONE)
    └── ph.in     ph.out               DFPT stalled, not converged (no dyn matrix)
```

Included file types: `scf.in`, `scf.out`, `ph.in`, `ph.out` only.
Deliberately **excluded**: wavefunctions, charge densities, `.save/`, `.mix`,
`_ph0/`, pseudopotential binaries, and any large/partial binary outputs (see
`STATUS.md`).

## Calculation summary

- Code: Quantum ESPRESSO (PWSCF/PHonon **v7.4** for the SrTiO₃ run).
- Method: DFPT (`ph.x`), PBE PAW pseudopotentials (`*-kjpaw_psl.1.0.0.UPF`).
- System: 2×2×2 perovskite supercell (`nat = 39`) with a single oxygen vacancy.
- Plane-wave / charge cutoffs: `ecutwfc = 80 Ry`, `ecutrho = 320 Ry`.
- k-points: `2×2×2`; phonon q-mesh `2×2×2` (SrTiO₃) / as in `ph.in` (BaTiO₃).
- Run location: cloud VM (no longer available); large raw data archived
  externally by the author.

## Provenance caveat

These exploratory supercell runs use **PAW** pseudopotentials and a **defect
supercell**, which differ from the norm-conserving (ONCV) **primitive-cell**
DFPT described in the manuscript methodology table. They are a separate,
incomplete line of work and are documented here only for completeness of the
record of what exists and what does not.
