#!/usr/bin/env python3
"""
Generate the publication figures from the committed data.

Figures (figures/):
    fig_bto_soft_mode.png   BaTiO3 soft-mode physics (3 panels):
                              (a) omega_soft(T), (b) Gamma_soft(T) with A+BT+CT^2
                              fit, (c) damping ratio Gamma/omega(T).
    fig_bto_linewidth_fit.png  BaTiO3 TO1/TO2/TO3 linewidths + A+BT+CT^2 fits.

Both are regenerated directly from data/raw/BTO/phonon_modes_*K.csv.

Usage:
    python scripts/make_figures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from common import (  # noqa: E402
    FIGURES_DIR, T_C_BTO, ensure_dirs, fit_abc, load_bto_modes,
)

MODE_ORDER = ["TO1 (soft)", "TO2", "TO3"]
MODE_COLORS = {"TO1 (soft)": "#d62728", "TO2": "#1f77b4", "TO3": "#2ca02c"}

plt.rcParams.update({
    "font.family": "serif", "font.size": 11, "axes.labelsize": 12,
    "axes.titlesize": 12, "legend.fontsize": 9, "figure.dpi": 150,
    "axes.linewidth": 0.8,
})


def fig_soft_mode(modes) -> Path:
    s = modes["TO1 (soft)"]
    T = np.asarray(s.T)
    omega = np.asarray(s.omega_THz)
    gamma = np.asarray(s.gamma_THz)
    fit = fit_abc(T, gamma)
    Tf = np.linspace(50, 650, 400)

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))

    # (a) frequency
    ax[0].plot(T, omega, "o-", color="#d62728", ms=8, lw=2, zorder=3)
    ax[0].axvline(T_C_BTO, color="gray", ls=":", lw=1.2, label=r"$T_c \approx 393$ K")
    ax[0].set_xlabel("Temperature (K)")
    ax[0].set_ylabel(r"$\omega_{\mathrm{soft}}$ (THz)")
    ax[0].set_title("(a) Soft-mode frequency", loc="left", fontweight="bold")
    ax[0].legend(); ax[0].grid(True, alpha=0.2)

    # (b) linewidth + fit
    ax[1].scatter(T, gamma, color="#d62728", s=60, zorder=5, edgecolors="k", lw=0.8,
                  label=r"Computed $\Gamma^{\mathrm{pert}}$")
    ax[1].plot(Tf, fit.gamma(Tf), "-", color="#d62728", lw=2,
               label=fr"$A+BT+CT^2$ ($R^2={fit.r2:.4f}$)")
    ax[1].axvline(T_C_BTO, color="gray", ls=":", lw=1.2)
    ax[1].set_xlabel("Temperature (K)")
    ax[1].set_ylabel(r"$\Gamma$ (THz)")
    ax[1].set_title("(b) Soft-mode linewidth", loc="left", fontweight="bold")
    ax[1].legend(); ax[1].grid(True, alpha=0.2)

    # (c) damping ratio
    ax[2].plot(T, gamma / omega, "D-", color="#d62728", ms=8, lw=2, zorder=3)
    ax[2].axhline(0.5, color="k", ls=":", lw=1.2, label=r"$\Gamma/\omega = 0.5$")
    ax[2].axvline(T_C_BTO, color="gray", ls=":", lw=1.2, label=r"$T_c$")
    ax[2].set_xlabel("Temperature (K)")
    ax[2].set_ylabel(r"$\Gamma/\omega$")
    ax[2].set_title("(c) Damping ratio", loc="left", fontweight="bold")
    ax[2].legend(loc="upper left"); ax[2].grid(True, alpha=0.2)

    fig.suptitle(r"BaTiO$_3$ soft mode: softening, broadening, and damping near $T_c$",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    out = FIGURES_DIR / "fig_bto_soft_mode.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_linewidth_fit(modes) -> Path:
    Tf = np.linspace(50, 650, 400)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, label in zip(axes, MODE_ORDER):
        s = modes[label]
        T = np.asarray(s.T)
        gamma = np.asarray(s.gamma_THz)
        fit = fit_abc(T, gamma)
        c = MODE_COLORS[label]
        ax.scatter(T, gamma, color=c, s=65, zorder=5, edgecolors="k", lw=0.8,
                   label=r"$\Gamma^{\mathrm{pert}}$")
        ax.plot(Tf, fit.gamma(Tf), "-", color=c, lw=2.2,
                label=fr"$A+BT+CT^2$ ($R^2={fit.r2:.4f}$)")
        ax.fill_between(Tf, fit.gamma(Tf) * 0.9, fit.gamma(Tf) * 1.1,
                        alpha=0.10, color=c, label=r"$\pm 10\%$")
        ax.set_xlabel("Temperature (K)")
        ax.set_ylabel(r"$\Gamma$ (THz)")
        ax.set_title(label, loc="left", fontweight="bold")
        ax.set_xlim(50, 650); ax.set_ylim(bottom=0)
        ax.legend(loc="upper left", fontsize=8); ax.grid(True, alpha=0.2)
    fig.suptitle(r"BaTiO$_3$: perturbative linewidths and $A+BT+CT^2$ fit",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    out = FIGURES_DIR / "fig_bto_linewidth_fit.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> int:
    ensure_dirs()
    modes = load_bto_modes()
    for out in (fig_soft_mode(modes), fig_linewidth_fit(modes)):
        print(f"wrote figures/{out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
