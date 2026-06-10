#!/usr/bin/env python3
"""
Validate the BaTiO3 temperature-dependent phonon linewidths.

Reads the committed BaTiO3 reference data (``data/raw/BTO/phonon_modes_*K.csv``),
builds Gamma^pert(T) for the three IR-active TO modes, fits the three-term
decomposition Gamma(T) = A + B*T + C*T**2, and compares the recovered
coefficients against the published Table 5 values.

This is the primary reproducibility target of the repository: it regenerates
**Table 5a** (the per-temperature perturbative linewidths) and the **BaTiO3
rows of Table 5** (fitted A, B, C, Gamma(300 K), R^2) directly from the CSVs.

Outputs (written to data/processed/):
    table5a_bto.csv        Gamma^pert(T) per mode and temperature
    table5_bto.csv         fitted coefficients + published reference + delta

Usage:
    python scripts/validate_bto_linewidths.py
Exit code is non-zero if any fitted coefficient deviates from the published
value beyond tolerance (so it doubles as a regression check).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA_PROCESSED, PUBLISHED_TABLE5, T_REF,
    ensure_dirs, fit_abc, load_bto_modes,
)

# Absolute tolerances for the regression check (coefficients are small).
TOL = {"A": 3e-3, "B": 5e-5, "C": 3e-7, "r2": 0.01}
MODE_ORDER = ["TO1 (soft)", "TO2", "TO3"]


def build():
    modes = load_bto_modes()
    fits = {label: fit_abc(modes[label].T, modes[label].gamma_THz) for label in MODE_ORDER}
    return modes, fits


def write_table5a(modes):
    out = DATA_PROCESSED / "table5a_bto.csv"
    temps = modes[MODE_ORDER[0]].T
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mode"] + [f"{int(t)}K_THz" for t in temps])
        for label in MODE_ORDER:
            w.writerow([label] + [f"{g:.3f}" for g in modes[label].gamma_THz])
    return out


def write_table5(modes, fits):
    out = DATA_PROCESSED / "table5_bto.csv"
    ref = PUBLISHED_TABLE5["BaTiO3"]
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mode", "omega_THz", "A_THz", "B_THz_per_K", "C_THz_per_K2",
                    "Gamma300_THz", "R2",
                    "A_pub", "B_pub", "C_pub", "Gamma300_pub", "R2_pub"])
        for label in MODE_ORDER:
            f = fits[label]
            omega = modes[label].omega_at(T_REF)
            g300 = modes[label].gamma_at(T_REF)  # raw datapoint (matches Table 5)
            pub = ref[label]
            w.writerow([label, f"{omega:.2f}", f"{f.A:.4f}", f"{f.B:.3e}",
                        f"{f.C:.3e}", f"{g300:.3f}", f"{f.r2:.4f}",
                        pub[1], pub[2], pub[3], pub[4], pub[5]])
    return out


def report(modes, fits) -> bool:
    ref = PUBLISHED_TABLE5["BaTiO3"]
    ok = True
    print("=" * 78)
    print("BaTiO3 linewidth validation  (data/raw/BTO/phonon_modes_*K.csv -> A+BT+CT^2)")
    print("=" * 78)
    print(f"{'mode':<12} {'omega':>6} {'A':>8} {'B':>11} {'C':>11} {'G(300)':>7} {'R2':>7}")
    for label in MODE_ORDER:
        f = fits[label]
        omega = modes[label].omega_at(T_REF)
        print(f"{label:<12} {omega:6.2f} {f.A:8.4f} {f.B:11.3e} {f.C:11.3e} "
              f"{modes[label].gamma_at(T_REF):7.3f} {f.r2:7.4f}")
        pub = ref[label]
        for key, got, exp in (("A", f.A, pub[1]), ("B", f.B, pub[2]),
                              ("C", f.C, pub[3]), ("r2", f.r2, pub[5])):
            if abs(got - exp) > TOL[key]:
                ok = False
                print(f"    !! {label} {key}: got {got:.4g}, published {exp:.4g} "
                      f"(|delta| > {TOL[key]:.0e})")
    print("-" * 78)
    print("PASS: fitted coefficients reproduce published Table 5 (BaTiO3)" if ok
          else "FAIL: deviation from published Table 5 exceeds tolerance")
    return ok


def main() -> int:
    ensure_dirs()
    modes, fits = build()
    t5a = write_table5a(modes)
    t5 = write_table5(modes, fits)
    ok = report(modes, fits)
    print(f"\nwrote {t5a.relative_to(t5a.parents[2])}")
    print(f"wrote {t5.relative_to(t5.parents[2])}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
