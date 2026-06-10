#!/usr/bin/env python3
"""
Generate Table 5 and Table 5a (Markdown + CSV) from the committed data.

Table 5a : BaTiO3 perturbative linewidths Gamma^pert(T), HWHM in THz, at
           100-600 K, for the three IR-active TO modes.
Table 5  : fitted three-term coefficients Gamma(T)=A+B*T+C*T^2 for BaTiO3
           (from the CSVs) and SrTiO3 (from the literature CSV).

Reuses the fit logic in validate_bto_linewidths / validate_sto_literature so
the tables and the validation reports can never drift apart.

Outputs (tables/):
    table5.md, table5.csv, table5a.md, table5a.csv

Usage:
    python scripts/make_tables.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_bto_linewidths as vbto  # noqa: E402
import validate_sto_literature as vsto  # noqa: E402
from common import TABLES_DIR, T_REF, ensure_dirs  # noqa: E402


def make_table5a(bto_modes) -> None:
    temps = bto_modes["TO1 (soft)"].T
    headers = ["Mode"] + [f"{int(t)} K" for t in temps]
    rows = [[label] + [f"{g:.3f}" for g in bto_modes[label].gamma_THz]
            for label in vbto.MODE_ORDER]

    with open(TABLES_DIR / "table5a.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(headers)
        w.writerows(rows)

    lines = [
        "# Table 5a. Independently computed phonon linewidths "
        "Gamma^pert(T) for BaTiO3",
        "",
        "All values in THz (HWHM). Generated from "
        "`data/raw/BTO/phonon_modes_*K.csv`.",
        "",
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    (TABLES_DIR / "table5a.md").write_text("\n".join(lines) + "\n")


def make_table5(bto_modes, bto_fits, sto_modes, sto_fits) -> None:
    headers = ["Material", "Mode", "omega (THz)", "A (THz)", "B (THz/K)",
               "C (THz/K^2)", "Gamma(300 K) (THz)", "R^2"]
    rows = []
    for material, modes, fits, order in (
        ("BaTiO3", bto_modes, bto_fits, vbto.MODE_ORDER),
        ("SrTiO3", sto_modes, sto_fits, vsto.MODE_ORDER),
    ):
        for label in order:
            f = fits[label]
            rows.append([
                material, label, f"{modes[label].omega_at(T_REF):.2f}",
                f"{f.A:.4f}", f"{f.B:.2e}", f"{f.C:.2e}",
                f"{modes[label].gamma_at(T_REF):.3f}", f"{f.r2:.4f}",
            ])

    with open(TABLES_DIR / "table5.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(headers)
        w.writerows(rows)

    lines = [
        "# Table 5. Temperature-dependent linewidth parameters "
        "Gamma(T) = A + B*T + C*T^2",
        "",
        "Least-squares fit of independently computed (BaTiO3) and published "
        "(SrTiO3) linewidths.",
        "",
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    (TABLES_DIR / "table5.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    ensure_dirs()
    bto_modes, bto_fits = vbto.build()
    sto_modes, sto_fits = vsto.build()
    make_table5a(bto_modes)
    make_table5(bto_modes, bto_fits, sto_modes, sto_fits)
    for name in ("table5.md", "table5.csv", "table5a.md", "table5a.csv"):
        print(f"wrote tables/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
