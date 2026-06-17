#!/usr/bin/env python3
"""
Soft-mode consistency figures (manuscript Figures 8 and 9).

The axes and titles are expressed in terms of *response-model values* versus
*literature/experimental benchmarks* (SrTiO3) and *INS-calibrated reference data*
(BaTiO3), matching the provenance framing of the manuscript.

Figure 8 — SrTiO3: response-model values vs. literature/experimental benchmarks.
  Mode frequencies are compared with experimental values; Born effective charges
  with established literature values; the soft-mode 300 K FWHM with experiment.
  Data are reference/benchmark values quoted from the manuscript Tables 2, 3, 8
  (see PROVENANCE constants below).

Figure 9 — BaTiO3: soft-mode reference-data consistency. The compact-model
  linewidth fit Gamma_k(T)=A+BT+CT^2 is compared against the semi-empirical,
  INS-calibrated reference linewidths Gamma_k^ref(T). This panel is regenerated
  directly from the committed CSVs (data/raw/BTO/phonon_modes_*K.csv) via the
  shared loader/fit in common.py.

Usage:
    python scripts/make_validation_figures.py
Outputs (figures/):
    fig8_sto_consistency.png
    fig9_bto_consistency.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from common import FIGURES_DIR, ensure_dirs, fit_abc, load_bto_modes  # noqa: E402

plt.rcParams.update({
    "font.family": "serif", "font.size": 11, "axes.labelsize": 11,
    "axes.titlesize": 11, "legend.fontsize": 8, "figure.dpi": 150,
    "axes.linewidth": 0.8,
})

# --------------------------------------------------------------------------- #
# Figure 8 data — SrTiO3 response-model values vs literature/experimental
# benchmarks. Quoted from the manuscript:
#   frequencies (cm^-1): Table 2 (model omega_DFPT vs experimental omega_exp)
#   Born charges:        Table 3 (model) vs established literature values
#   soft-mode FWHM (cm^-1, 300 K): Table 8 (model vs experiment)
# Each entry: (label, model_value, benchmark_value, group)
# --------------------------------------------------------------------------- #
STO_POINTS = [
    ("ω TO1 (soft)", 91.2, 91, "Frequency (cm⁻¹) vs exp."),
    ("ω TO2",        167.6, 175, "Frequency (cm⁻¹) vs exp."),
    ("ω TO3",        183.9, 178, "Frequency (cm⁻¹) vs exp."),
    ("ω TO4",        200.7, 265, "Frequency (cm⁻¹) vs exp."),
    ("ω TO5",        518.5, 545, "Frequency (cm⁻¹) vs exp."),
    ("Z*(Sr)",        2.54, 2.54, "Born charge vs lit."),
    ("Z*(Ti)",        7.12, 7.12, "Born charge vs lit."),
    ("Z*(O∥)",       -5.66, -5.66, "Born charge vs lit."),
    ("Z*(O⊥)",       -2.00, -2.00, "Born charge vs lit."),
    ("FWHM TO1 (300 K)", 14.6, 15, "FWHM (cm⁻¹) vs exp."),
]
GROUP_COLORS = {
    "Frequency (cm⁻¹) vs exp.": "#1f77b4",
    "Born charge vs lit.": "#2ca02c",
    "FWHM (cm⁻¹) vs exp.": "#d62728",
}

BTO_MODE_COLORS = {"TO1 (soft)": "#d62728", "TO2": "#1f77b4", "TO3": "#2ca02c"}
BTO_TEMPS = [100, 300, 600]  # representative temperatures (manuscript Table 5b)


def _consistency_panel(ax, deviations):
    """Panel (c): count of quantities by deviation band (no PASS/FAIL verdict)."""
    bands = [("≤5%", sum(d <= 5 for d in deviations)),
             ("5–15%", sum(5 < d <= 15 for d in deviations)),
             (">15%", sum(d > 15 for d in deviations))]
    labels = [b[0] for b in bands]
    counts = [b[1] for b in bands]
    colors = ["#2ca02c", "#ff7f0e", "#d62728"]
    ax.bar(labels, counts, color=colors, edgecolor="k", lw=0.6)
    ax.set_ylabel("Number of quantities")
    ax.set_title("(c) Soft-mode consistency metrics", loc="left", fontweight="bold")
    rms = float(np.sqrt(np.mean(np.square(deviations)))) if deviations else 0.0
    ax.text(0.97, 0.95, f"RMS dev = {rms:.1f}%\nmax = {max(deviations):.1f}%",
            transform=ax.transAxes, ha="right", va="top", fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.85))
    ax.set_ylim(0, max(counts) + 1)


def figure8_sto() -> Path:
    model = np.array([p[1] for p in STO_POINTS], float)
    bench = np.array([p[2] for p in STO_POINTS], float)
    groups = [p[3] for p in STO_POINTS]
    labels = [p[0] for p in STO_POINTS]
    dev = np.abs(model - bench) / np.abs(bench) * 100.0

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))

    # (a) model vs benchmark scatter
    seen = set()
    for x, y, g in zip(bench, model, groups):
        ax[0].scatter(x, y, c=GROUP_COLORS[g], s=70, edgecolors="k", lw=0.6,
                      zorder=5, label=g if g not in seen else None)
        seen.add(g)
    lim = [min(bench.min(), model.min()) - 10, max(bench.max(), model.max()) + 20]
    ax[0].plot(lim, lim, "k--", lw=1, alpha=0.7, label="exact agreement")
    ax[0].set_xlim(lim); ax[0].set_ylim(lim)
    ax[0].set_xlabel("Literature/experimental benchmark")
    ax[0].set_ylabel("Value used in response model")
    ax[0].set_title("(a) Response-model values vs.\nliterature/experimental benchmarks",
                    loc="left", fontweight="bold", fontsize=9.5)
    ax[0].legend(loc="upper left", fontsize=7.5); ax[0].grid(True, alpha=0.2)

    # (b) relative deviation from benchmark
    yk = np.arange(len(labels))
    ax[1].barh(yk, dev, color=[GROUP_COLORS[g] for g in groups], edgecolor="k", lw=0.5)
    ax[1].axvline(5, color="green", ls="--", lw=1, label="5%")
    ax[1].axvline(15, color="orange", ls="--", lw=1, label="15%")
    ax[1].set_yticks(yk); ax[1].set_yticklabels(labels, fontsize=8)
    ax[1].invert_yaxis()
    ax[1].set_xlabel("Relative deviation from benchmark (%)")
    ax[1].set_title("(b) Relative deviation from benchmark (%)", loc="left", fontweight="bold", fontsize=9.5)
    ax[1].legend(fontsize=7.5); ax[1].grid(True, axis="x", alpha=0.2)

    # (c) consistency metrics
    _consistency_panel(ax[2], list(dev))

    fig.suptitle(r"SrTiO$_3$: soft-mode and TO-mode consistency with literature/experimental benchmarks",
                 fontsize=13, fontweight="bold", y=1.03)
    fig.tight_layout()
    out = FIGURES_DIR / "fig8_sto_consistency.png"
    fig.savefig(out, dpi=300, bbox_inches="tight"); plt.close(fig)
    return out


def figure9_bto() -> Path:
    modes = load_bto_modes()
    ref_vals, fit_vals, dev, colors, pts = [], [], [], [], []
    for label in ("TO1 (soft)", "TO2", "TO3"):
        s = modes[label]
        f = fit_abc(s.T, s.gamma_THz)
        for T in BTO_TEMPS:
            ref = s.gamma_at(T)
            mod = float(f.gamma(T))
            ref_vals.append(ref); fit_vals.append(mod)
            dev.append(abs(mod - ref) / ref * 100.0)
            colors.append(BTO_MODE_COLORS[label]); pts.append(f"{label} {T}K")
    ref_vals = np.array(ref_vals); fit_vals = np.array(fit_vals); dev = np.array(dev)

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))

    # (a) compact-model vs INS-calibrated reference
    for label in ("TO1 (soft)", "TO2", "TO3"):
        idx = [i for i, p in enumerate(pts) if p.startswith(label)]
        ax[0].scatter(ref_vals[idx], fit_vals[idx], c=BTO_MODE_COLORS[label],
                      s=70, edgecolors="k", lw=0.6, zorder=5, label=label)
    lim = [0, max(ref_vals.max(), fit_vals.max()) * 1.1]
    ax[0].plot(lim, lim, "k--", lw=1, alpha=0.7, label="exact agreement")
    ax[0].set_xlim(lim); ax[0].set_ylim(lim)
    ax[0].set_xlabel("INS-calibrated reference value  Γ$^{\\mathrm{ref}}$ (THz)")
    ax[0].set_ylabel("Compact-model value  Γ$^{\\mathrm{fit}}$ (THz)")
    ax[0].set_title("(a) Compact-model vs.\nINS-calibrated reference linewidths",
                    loc="left", fontweight="bold", fontsize=9.5)
    ax[0].legend(loc="upper left", fontsize=8); ax[0].grid(True, alpha=0.2)

    # (b) relative deviation from benchmark
    yk = np.arange(len(pts))
    ax[1].barh(yk, dev, color=colors, edgecolor="k", lw=0.5)
    ax[1].axvline(5, color="green", ls="--", lw=1, label="5%")
    ax[1].axvline(15, color="orange", ls="--", lw=1, label="15%")
    ax[1].set_yticks(yk); ax[1].set_yticklabels(pts, fontsize=8); ax[1].invert_yaxis()
    ax[1].set_xlabel("Relative deviation from benchmark (%)")
    ax[1].set_title("(b) Relative deviation from benchmark (%)", loc="left", fontweight="bold", fontsize=9.5)
    ax[1].legend(fontsize=7.5); ax[1].grid(True, axis="x", alpha=0.2)

    # (c) consistency metrics
    _consistency_panel(ax[2], list(dev))

    fig.suptitle(r"BaTiO$_3$ soft-mode reference-data consistency",
                 fontsize=13, fontweight="bold", y=1.03)
    fig.tight_layout()
    out = FIGURES_DIR / "fig9_bto_consistency.png"
    fig.savefig(out, dpi=300, bbox_inches="tight"); plt.close(fig)
    return out


def main() -> int:
    ensure_dirs()
    for out in (figure8_sto(), figure9_bto()):
        print(f"wrote figures/{out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
