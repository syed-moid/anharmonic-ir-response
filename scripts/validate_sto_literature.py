#!/usr/bin/env python3
"""
Cross-validate the SrTiO3 linewidths against published anharmonic data.

SrTiO3 is the *literature* reference material in the manuscript: its linewidths
are taken from published self-consistent-phonon / bubble-diagram calculations
and experimental damping data (refs [25-27] in the paper), digitised in
``data/raw/literature/SrTiO3_linewidths_literature.csv``.

This script fits Gamma(T) = A + B*T + C*T**2 to those published points and
checks that the recovered coefficients match the SrTiO3 rows of Table 5.

Output (data/processed/):
    table5_sto.csv

Usage:
    python scripts/validate_sto_literature.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA_PROCESSED, PUBLISHED_TABLE5, T_REF,
    ensure_dirs, fit_abc, load_sto_literature,
)

TOL = {"A": 3e-3, "B": 5e-5, "C": 3e-7, "r2": 0.01}
MODE_ORDER = ["TO1 (soft)", "TO2"]


def build():
    modes = load_sto_literature()
    fits = {label: fit_abc(modes[label].T, modes[label].gamma_THz) for label in MODE_ORDER}
    return modes, fits


def write_table5(modes, fits):
    out = DATA_PROCESSED / "table5_sto.csv"
    ref = PUBLISHED_TABLE5["SrTiO3"]
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mode", "omega_THz", "A_THz", "B_THz_per_K", "C_THz_per_K2",
                    "Gamma300_THz", "R2",
                    "A_pub", "B_pub", "C_pub", "Gamma300_pub", "R2_pub"])
        for label in MODE_ORDER:
            f = fits[label]
            omega = modes[label].omega_at(T_REF)
            pub = ref[label]
            w.writerow([label, f"{omega:.2f}", f"{f.A:.4f}", f"{f.B:.3e}",
                        f"{f.C:.3e}", f"{modes[label].gamma_at(T_REF):.3f}", f"{f.r2:.4f}",
                        pub[1], pub[2], pub[3], pub[4], pub[5]])
    return out


def report(modes, fits) -> bool:
    ref = PUBLISHED_TABLE5["SrTiO3"]
    ok = True
    print("=" * 78)
    print("SrTiO3 literature cross-validation  (refs [25-27] -> A+BT+CT^2)")
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
                print(f"    !! {label} {key}: got {got:.4g}, published {exp:.4g}")
    print("-" * 78)
    print("PASS: fitted coefficients reproduce published Table 5 (SrTiO3)" if ok
          else "FAIL: deviation from published Table 5 exceeds tolerance")
    return ok


def main() -> int:
    ensure_dirs()
    modes, fits = build()
    out = write_table5(modes, fits)
    ok = report(modes, fits)
    print(f"\nwrote {out.relative_to(out.parents[2])}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
