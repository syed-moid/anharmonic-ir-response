"""
Shared utilities for the Anharmonic IR Response reproducibility pipeline.

This module centralises:
  * physical constants and unit conversions,
  * the canonical mapping from raw mode labels to manuscript mode names,
  * loaders for the committed CSV data,
  * the A + B*T + C*T**2 least-squares linewidth fit,
  * the *published* Table 5 reference values (for validation / regression tests).

Nothing here invents data: every number returned by the loaders comes from a
committed CSV under ``data/raw/``. The published reference values are quoted
verbatim from the manuscript (Table 5) and are used only to
*check* that the fit reproduces the paper.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
TABLES_DIR = ROOT / "tables"
FIGURES_DIR = ROOT / "figures"

BTO_DIR = DATA_RAW / "BTO"
LIT_DIR = DATA_RAW / "literature"

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
# 1 meV = 0.2417989 THz (E = h*nu). The original analysis used 0.24180;
# we keep that value so the reproduced coefficients match the manuscript to
# the printed precision. The difference vs the exact value is < 1e-4 THz.
MEV_TO_THZ = 0.24180

# Temperatures (K) at which the BaTiO3 perturbative linewidths were tabulated.
BTO_TEMPERATURES = [100, 200, 300, 400, 500, 600]

# Curie temperature used for the soft-mode figure annotation.
T_C_BTO = 393.0  # K

# Reference temperature for the Gamma(300 K) column of Table 5.
T_REF = 300.0  # K

# Mapping from the raw `mode_name` field in the BaTiO3 CSVs to the
# infrared-active mode labels used in the manuscript (Table 5 / 5a).
# Only these three modes are IR-active TO modes used in the linewidth model.
BTO_MODE_MAP = {
    "Mode_1_Ti-O_soft": "TO1 (soft)",
    "Mode_2_A-O_TO2_gamma": "TO2",
    "Mode_3_A-O_TO2": "TO3",
}

# --------------------------------------------------------------------------- #
# Published reference (manuscript, Table 5) -- for validation only.
# The revised Table 5 lists A, B, C, Gamma(300 K), R^2 (the Gamma-point
# reference frequencies are tabulated separately in Table 2), so no omega
# column is carried here.
# --------------------------------------------------------------------------- #
# (A, B, C, Gamma300, R2)
PUBLISHED_TABLE5 = {
    "BaTiO3": {
        "TO1 (soft)": (0.091, 2.3e-4, 1.4e-6, 0.25, 0.985),
        "TO2":        (0.069, 4.8e-4, 2.2e-8, 0.22, 0.998),
        "TO3":        (0.094, 4.2e-4, 1.3e-7, 0.23, 0.992),
    },
    "SrTiO3": {
        "TO1 (soft)": (0.040, 1.0e-4, 1.6e-6, 0.22, 0.999),
        "TO2":        (0.028, 1.4e-4, 6.4e-7, 0.13, 0.999),
    },
}


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #
@dataclass
class ModeSeries:
    """Temperature series for a single phonon mode."""
    label: str                      # manuscript label, e.g. "TO1 (soft)"
    raw_name: str                   # raw mode_name in the CSV
    T: list[float] = field(default_factory=list)        # K
    omega_THz: list[float] = field(default_factory=list)
    gamma_THz: list[float] = field(default_factory=list)

    def omega_at(self, T_target: float) -> float:
        for t, w in zip(self.T, self.omega_THz):
            if t == T_target:
                return w
        raise KeyError(f"{self.label}: no omega at T={T_target} K")

    def gamma_at(self, T_target: float) -> float:
        """Raw measured/computed linewidth datapoint at T_target (THz).

        Note: the manuscript Table 5 "Gamma(300 K)" column reports this raw
        datapoint, not the A+B*T+C*T**2 polynomial evaluated at 300 K. For all
        modes except the BaTiO3 soft mode the two agree to the printed 2 d.p.;
        for the soft mode the polynomial overshoots (~0.29 vs 0.25) because its
        T-dependence departs from a smooth polynomial near the transition
        (this is the R^2 = 0.985 mode).
        """
        for t, g in zip(self.T, self.gamma_THz):
            if t == T_target:
                return g
        raise KeyError(f"{self.label}: no gamma at T={T_target} K")


@dataclass
class ABCFit:
    """Result of a Gamma(T) = A + B*T + C*T**2 least-squares fit."""
    A: float
    B: float
    C: float
    r2: float
    rms: float
    T: np.ndarray
    gamma_data: np.ndarray
    gamma_fit: np.ndarray

    def gamma(self, T):
        T = np.asarray(T, dtype=float)
        return self.A + self.B * T + self.C * T ** 2


# --------------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------------- #
def load_bto_modes() -> dict[str, ModeSeries]:
    """Load the BaTiO3 IR-active mode series from data/raw/BTO/phonon_modes_*K.csv.

    Returns a dict keyed by manuscript label ("TO1 (soft)", "TO2", "TO3").
    Linewidths and frequencies are converted meV -> THz.
    """
    series: dict[str, ModeSeries] = {}
    for T in BTO_TEMPERATURES:
        fp = BTO_DIR / f"phonon_modes_{T}K.csv"
        if not fp.exists():
            raise FileNotFoundError(f"Missing committed data file: {fp}")
        with open(fp, newline="") as fh:
            for row in csv.DictReader(fh):
                raw = row["mode_name"]
                if raw not in BTO_MODE_MAP:
                    continue
                label = BTO_MODE_MAP[raw]
                s = series.setdefault(label, ModeSeries(label=label, raw_name=raw))
                s.T.append(float(row["temperature_K"]))
                s.omega_THz.append(float(row["omega_Q_meV"]) * MEV_TO_THZ)
                s.gamma_THz.append(float(row["Gamma_Q_HWHM_meV"]) * MEV_TO_THZ)
    # sort each series by temperature for determinism
    for s in series.values():
        order = np.argsort(s.T)
        s.T = [s.T[i] for i in order]
        s.omega_THz = [s.omega_THz[i] for i in order]
        s.gamma_THz = [s.gamma_THz[i] for i in order]
    return series


def load_sto_literature() -> dict[str, ModeSeries]:
    """Load the SrTiO3 literature linewidths from data/raw/literature/."""
    fp = LIT_DIR / "SrTiO3_linewidths_literature.csv"
    if not fp.exists():
        raise FileNotFoundError(f"Missing committed data file: {fp}")
    series: dict[str, ModeSeries] = {}
    with open(fp, newline="") as fh:
        for row in csv.DictReader(fh):
            label = row["mode"]
            s = series.setdefault(label, ModeSeries(label=label, raw_name=label))
            s.T.append(float(row["temperature_K"]))
            s.gamma_THz.append(float(row["Gamma_THz"]))
            s.omega_THz.append(float(row["omega_THz"]))
    for s in series.values():
        order = np.argsort(s.T)
        s.T = [s.T[i] for i in order]
        s.omega_THz = [s.omega_THz[i] for i in order]
        s.gamma_THz = [s.gamma_THz[i] for i in order]
    return series


# --------------------------------------------------------------------------- #
# Fit
# --------------------------------------------------------------------------- #
def fit_abc(T, gamma) -> ABCFit:
    """Least-squares fit Gamma(T) = A + B*T + C*T**2 (HWHM, THz)."""
    T = np.asarray(T, dtype=float)
    gamma = np.asarray(gamma, dtype=float)
    X = np.column_stack([np.ones_like(T), T, T ** 2])
    coef, *_ = np.linalg.lstsq(X, gamma, rcond=None)
    fit = X @ coef
    ss_res = float(np.sum((gamma - fit) ** 2))
    ss_tot = float(np.sum((gamma - gamma.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    rms = float(np.sqrt(np.mean((gamma - fit) ** 2)))
    return ABCFit(A=float(coef[0]), B=float(coef[1]), C=float(coef[2]),
                  r2=r2, rms=rms, T=T, gamma_data=gamma, gamma_fit=fit)


def ensure_dirs() -> None:
    for d in (DATA_PROCESSED, TABLES_DIR, FIGURES_DIR):
        d.mkdir(parents=True, exist_ok=True)
