# Quantum ESPRESSO exploratory calculations

These files document **exploratory** Quantum ESPRESSO calculations performed
during manuscript development.

## Status

- SCF (ground-state) calculations were **completed** for the listed defect
  supercell structures.
- DFPT / phonon calculations were **started but not converged** to a
  production-quality result.
- **No** third-order force constants, phonon self-energies, or converged phonon
  linewidths were generated from these runs.
- These QE files were **not used** to generate Tables 5, 5a, 5b, the BaTiO₃
  soft-mode curve, or the infrared-absorption spectra in the revised manuscript.

## What completed vs. what did not

| Run | System | SCF | DFPT phonon |
|---|---|---|---|
| `BaTiO3_defect_2x2x2` | BaTiO₃ + 1 O-vacancy (39 atoms) | completed (`JOB DONE`) | crashed at startup (could not read SCF save) — no dynamical matrix |
| `SrTiO3_defect_2x2x2` | SrTiO₃ + 1 O-vacancy (39 atoms) | completed (`JOB DONE`) | ran on a GPU VM, stalled on convergence at the first representation (q1, irrep 1 of 117); `*.dyn1` empty — no frequencies |

The SrTiO₃ phonon run terminated cleanly (`JOB DONE` printed) but **did not
converge**: the linear-response SCF for the first representation oscillated at
|ddv_scf|² ≈ 1.5×10⁻¹⁵ against `tr2_ph = 1×10⁻¹⁵`. No dynamical matrix was
written.

## Notes for anyone reusing these inputs

- QE version: PWSCF/PHonon **v7.4** (SrTiO₃ run); BaTiO₃ run with v6.x-era inputs.
  Phonon recover files are version-specific — restart with the matching version.
- Pseudopotentials: PBE PAW (`*.pbe-*-kjpaw_psl.1.0.0.UPF`). Note this differs
  from the norm-conserving (ONCV) pseudopotentials described in the manuscript's
  primitive-cell methodology table; these supercell runs are a separate,
  exploratory line of calculation.
- Cells: ~9 Å cubic 2×2×2 defect supercells, `K_POINTS 2×2×2`, `nat = 39`
  (one oxygen vacancy). This is **not** the primitive-cell DFPT setup of the
  manuscript methodology table.
- The calculations were run on a cloud VM that is no longer available; the large
  raw outputs are archived externally by the author.

## Excluded from this repository (by design)

The following are **not** included here because of size and because they are not
needed to reproduce any manuscript result:

- `*.save/` directories
- wavefunction files (`wfc*.dat`)
- charge-density binaries (`charge-density.dat`)
- DFPT scratch / recover files (`*.mix`, `_ph0/`, `*.recover`, `*.bar`, …)
- pseudopotential `.UPF` binaries
- any multi-hundred-MB raw folders or partial binary outputs

Checksums and sizes of the key external raw files are recorded in
`checksums_external_raw_data.txt` so they can be matched against the author's
external archive if needed.
