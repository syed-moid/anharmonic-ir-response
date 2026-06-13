import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, FancyBboxPatch
from matplotlib.lines import Line2D
import os

# ============================================================
# Graphical Abstract — mode-resolved, provenance-aware framing
# (matches the revised manuscript: established Green's-function
#  formalism -> documented phonon data -> compact mode-resolved response)
# ============================================================
from pathlib import Path

# --- Helper functions ---

def add_panel(ax, x, y, w, h, title, edgecolor, facecolor="#ffffff", title_color="black"):
    panel = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.008,rounding_size=0.012",
        linewidth=1.6, edgecolor=edgecolor, facecolor=facecolor, zorder=1
    )
    ax.add_patch(panel)
    ax.text(x + w / 2, y + h - 0.03, title, ha="center", va="top",
            fontsize=13, fontweight="bold", color=title_color)
    return panel


def add_text_box(ax, x, y, w, h, text, fontsize=9.5, facecolor="#f8f8f8",
                 edgecolor="#bbbbbb", linespacing=1.3):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.006,rounding_size=0.01",
        linewidth=1.0, edgecolor=edgecolor, facecolor=facecolor, zorder=2
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, linespacing=linespacing)
    return box


def draw_perovskite(ax, x, y, scale=1.0, main_color="#4c78a8", impurity=False):
    s = 0.06 * scale
    ax.add_patch(Rectangle((x, y), s, s, fill=False, linewidth=1.2,
                            edgecolor="#666666", zorder=3))
    corners = [(x, y), (x+s, y), (x, y+s), (x+s, y+s)]
    for i, (cx, cy) in enumerate(corners):
        color = "#e15759" if (impurity and i == 1) else main_color
        ax.add_patch(Circle((cx, cy), 0.0055 * scale, color=color, zorder=4))
    ax.add_patch(Circle((x + s/2, y + s/2), 0.0065 * scale, color="#59a14f", zorder=4))
    for ox, oy in [(x+s/2,y), (x+s/2,y+s), (x,y+s/2), (x+s,y+s/2)]:
        ax.add_patch(Circle((ox, oy), 0.0048 * scale, color="#f28e2b", zorder=4))
    arrow_scale = 0.012 * scale
    cx, cy = x + s/2, y + s/2
    for (x0,y0),(x1,y1) in [((cx,cy),(cx+arrow_scale,cy+arrow_scale)),
                              ((x+s/2,y),(x+s/2,y-arrow_scale)),
                              ((x+s/2,y+s),(x+s/2,y+s+arrow_scale))]:
        ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1), arrowstyle="->",
                                      mutation_scale=8, linewidth=1.0, color="#444444", zorder=5))


def draw_lattice_with_impurity(ax, x, y, w, h):
    nx, ny = 5, 4
    xs = np.linspace(x + 0.03, x + w - 0.03, nx)
    ys = np.linspace(y + 0.03, y + h - 0.03, ny)
    for yy in ys:
        for i in range(nx-1):
            ax.add_line(Line2D([xs[i],xs[i+1]], [yy,yy], lw=1.0, color="#b0b0b0", zorder=2))
    for xx in xs:
        for j in range(ny-1):
            ax.add_line(Line2D([xx,xx], [ys[j],ys[j+1]], lw=1.0, color="#b0b0b0", zorder=2))
    for j, yy in enumerate(ys):
        for i, xx in enumerate(xs):
            color, radius = "#4c78a8", 0.0065
            if i == 3 and j == 2:
                color, radius = "#e15759", 0.008
            ax.add_patch(Circle((xx, yy), radius, color=color, zorder=3))
            dx = 0.012 * np.sin(8*(xx-x))
            dy = 0.008 * np.cos(7*(yy-y))
            ax.add_patch(FancyArrowPatch((xx,yy),(xx+dx,yy+dy), arrowstyle="->",
                                          mutation_scale=7, linewidth=0.8, color="#555555", zorder=4))
    ax.text(x + 0.02, y + h + 0.005, "defect + soft-mode distortion",
            fontsize=8.5, color="#444444")


def lorentzian(x, x0, gamma, amp):
    return amp * gamma**2 / ((x - x0)**2 + gamma**2)


def draw_spectrum(ax, x, y, w, h, title=None, label_left=None, show_temp=True):
    """IR spectrum with CORRECTED (narrower) linewidths."""
    xx = np.linspace(20, 600, 2000)
    temps = [100, 300, 500]

    # UPDATED peak parameters: narrower gammas reflecting corrected linewidths
    # Format: (center_cm, gamma_cm_HWHM, amplitude)
    params = [
        # 100 K — narrow peaks
        [(90, 4.5, 2.2), (170, 4.0, 1.5), (185, 3.5, 1.3), (200, 3.5, 1.2), (520, 2.0, 2.8)],
        # 300 K — moderate broadening
        [(90, 8.0, 1.5), (170, 6.5, 1.1), (185, 6.0, 1.0), (200, 6.0, 0.9), (520, 3.5, 1.8)],
        # 500 K — wider but less extreme than before
        [(90, 14, 0.95), (170, 11, 0.80), (185, 10, 0.72), (200, 10, 0.68), (520, 5.5, 1.1)],
    ]
    colors = ["#3b5bdb", "#9c36b5", "#f08c00"]

    spectra = []
    for peaks in params:
        yy = np.zeros_like(xx)
        for x0, g, a in peaks:
            yy += lorentzian(xx, x0, g, a)
        spectra.append(yy)

    ymax = max(np.max(s) for s in spectra) * 1.05
    xmin, xmax = xx.min(), xx.max()

    ax.add_patch(Rectangle((x, y), w, h, fill=False, linewidth=1.0,
                            edgecolor="#999999", zorder=2))

    for yy, c, T in zip(spectra, colors, temps):
        X = x + (xx - xmin) / (xmax - xmin) * w
        Y = y + yy / ymax * h
        ax.plot(X, Y, color=c, lw=1.6, zorder=3)
        if show_temp:
            idx = temps.index(T)
            ax.text(x + w - 0.055, y + h - 0.018 - 0.016 * idx,
                    f"{T} K", fontsize=7.5, color=c)

    if title:
        ax.text(x + w/2, y + h + 0.012, title, ha="center", va="bottom", fontsize=8.5)
    if label_left:
        ax.text(x - 0.02, y + h/2, label_left, ha="center", va="center",
                fontsize=7.5, rotation=90, color="#444444")
    ax.text(x + w/2, y - 0.018, r"Wavenumber (cm$^{-1}$)",
            ha="center", va="top", fontsize=7.5)


def draw_linewidth_inset(ax, x, y, w, h):
    """Linewidth vs T inset with CORRECTED parameters."""
    T = np.linspace(50, 600, 200)

    # Linewidth coefficients from the revised manuscript (Table 5):
    # SrTiO3: A=0.040, B=1.0e-4, C=1.6e-6  (published anharmonic / damping data)
    # BaTiO3: A=0.091, B=2.3e-4, C=1.4e-6  (INS-calibrated reference data)
    g_sto = 0.040 + 1.0e-4 * T + 1.6e-6 * T**2
    g_bto = 0.091 + 2.3e-4 * T + 1.4e-6 * T**2

    ymin = 0
    ymax = max(g_sto.max(), g_bto.max()) * 1.08
    xmin, xmax = T.min(), T.max()

    ax.add_patch(Rectangle((x, y), w, h, fill=False, linewidth=1.0,
                            edgecolor="#999999", zorder=2))

    for arr, c, lab in [(g_sto, "#4c78a8", r"SrTiO$_3$"),
                         (g_bto, "#e15759", r"BaTiO$_3$")]:
        X = x + (T - xmin) / (xmax - xmin) * w
        Y = y + (arr - ymin) / (ymax - ymin) * h
        ax.plot(X, Y, color=c, lw=1.7, zorder=3)

    # Position labels inside plot area with clear spacing
    ax.text(x + w * 0.75, y + h * 0.92, r"BaTiO$_3$",
            fontsize=7.5, color="#e15759", ha="center", va="top")
    ax.text(x + w * 0.75, y + h * 0.72, r"SrTiO$_3$",
            fontsize=7.5, color="#4c78a8", ha="center", va="top")

    ax.text(x + w/2, y + h + 0.012, r"Linewidth $\Gamma_k(T) = A + BT + CT^2$",
            ha="center", va="bottom", fontsize=8.5)
    ax.text(x + w/2, y - 0.016, "Temperature (K)",
            ha="center", va="top", fontsize=7.2)


# ============================================================
# FIGURE CANVAS
# ============================================================

fig = plt.figure(figsize=(16, 9), dpi=600)
ax = plt.axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# Panel colors
theory_edge = "#2f5597"; dfpt_edge = "#2b8a3e"; pred_edge = "#c92a2a"
theory_fill = "#f7fbff"; dfpt_fill = "#f4fcf5"; pred_fill = "#fff5f5"

# --- Header ---
ax.text(0.5, 0.97,
    "Mode-Resolved Anharmonic Framework for Dielectric Susceptibility and\n"
    "Infrared Absorption in Disordered Polar Crystals",
    ha="center", va="top", fontsize=17, fontweight="bold", linespacing=1.2)

ax.text(0.5, 0.91,
    r"Established Green's-function formalism  $\rightarrow$  Documented phonon data  $\rightarrow$  Mode-resolved response",
    ha="center", va="top", fontsize=11.5, color="#444444")

# --- Panel backgrounds ---
left  = (0.035, 0.14, 0.285, 0.72)
mid   = (0.357, 0.14, 0.285, 0.72)
right = (0.679, 0.14, 0.286, 0.72)

add_panel(ax, *left,  title="Microscopic Green's-Function Formalism",
          edgecolor=theory_edge, facecolor=theory_fill)
add_panel(ax, *mid,   title="Documented Reference Inputs",
          edgecolor=dfpt_edge, facecolor=dfpt_fill)
add_panel(ax, *right, title="Compact Mode-Resolved Response",
          edgecolor=pred_edge, facecolor=pred_fill)


# ============================================================
# LEFT PANEL — Theory
# ============================================================
lx, ly, lw, lh = left

draw_lattice_with_impurity(ax, lx + 0.03, ly + 0.43, lw - 0.06, 0.18)

add_text_box(ax, lx + 0.035, ly + 0.32, lw - 0.07, 0.085,
    "Thermal double-time Green's functions\n"
    "Kubo linear response\n"
    r"$\chi(\omega)$, $\alpha(\omega)$, $\Gamma_k(T)$",
    fontsize=10.0, facecolor="#eef4ff", edgecolor="#9bb7e8")

add_text_box(ax, lx + 0.035, ly + 0.215, lw - 0.07, 0.075,
    "Disorder scattering\n"
    "Cubic anharmonicity\n"
    "Quartic anharmonicity",
    fontsize=9.6, facecolor="#f8f8f8", edgecolor="#c8c8c8")

# Self-energy decomposition -> renormalized frequency + linewidth
add_text_box(ax, lx + 0.02, ly + 0.115, lw - 0.04, 0.075,
    r"$\Sigma_k = \Delta_k - i\Gamma_k\ \rightarrow\ \Omega_k(T),\ \Gamma_k(T)$",
    fontsize=10.0, facecolor="#ffffff", edgecolor="#bdbdbd")

ax.text(lx + lw/2, ly + 0.05,
    "Microscopic origin of\ndielectric response and IR loss",
    ha="center", va="center", fontsize=9.5, style="italic", color="#333333",
    linespacing=1.2)


# ============================================================
# MIDDLE PANEL — Documented Reference Inputs
# ============================================================
mx, my, mw, mh = mid

# Perovskite icons — positioned below panel title (shifted down & left)
draw_perovskite(ax, mx + 0.03, my + 0.56, scale=1.6, impurity=False)
ax.text(mx + 0.065, my + 0.535, r"SrTiO$_3$", ha="center", fontsize=10)

draw_perovskite(ax, mx + 0.15, my + 0.56, scale=1.6, impurity=True)
ax.text(mx + 0.185, my + 0.535, r"BaTiO$_3$", ha="center", fontsize=10)

add_text_box(ax, mx + 0.025, my + 0.435, mw - 0.05, 0.085,
    "DFPT-level reference / literature inputs\n"
    "Reference frequencies & eigenvectors\n"
    "Born effective charges\n"
    r"High-frequency dielectric constant $\varepsilon_\infty$",
    fontsize=9.2, facecolor="#eefaf0", edgecolor="#9ad0a4", linespacing=1.25)

draw_spectrum(ax, mx + 0.05, my + 0.19, mw - 0.10, 0.18,
              title="Mode-resolved IR spectra", label_left="Abs.", show_temp=False)

# Linewidth reference data + compact fit (no validation/over-claim language)
add_text_box(ax, mx + 0.025, my + 0.06, mw - 0.05, 0.095,
    r"BaTiO$_3$: INS-calibrated reference $\Gamma^{\mathrm{ref}}_k(T)$"
    "\n"
    r"SrTiO$_3$: published anharmonic / damping data"
    "\n"
    r"$\Gamma_k(T) = A_k + B_k T + C_k T^2$  fit ($R^2 > 0.985$)",
    fontsize=8.8, facecolor="#ffffff", edgecolor="#7ec48a", linespacing=1.3)

ax.text(mx + mw/2, my + 0.01,
    "Provenance-aware input/output separation",
    ha="center", va="center", fontsize=9.5, style="italic",
    fontweight="bold", color="#2b8a3e")


# ============================================================
# RIGHT PANEL — Compact Mode-Resolved Response
# ============================================================
rx, ry, rw, rh = right

draw_spectrum(ax, rx + 0.035, ry + 0.46, rw - 0.07, 0.18,
              title="Temperature-dependent IR spectra",
              label_left="Abs.", show_temp=True)

draw_linewidth_inset(ax, rx + 0.055, ry + 0.27, rw - 0.11, 0.12)

# FIXED: equation box with slightly smaller font to prevent overflow
add_text_box(ax, rx + 0.02, ry + 0.125, rw - 0.04, 0.105,
    r"$\alpha(\omega,T,c_d)=K(\omega)\sum_k"
    r"\frac{S_k\,\omega_k^2\,\Gamma_k}"
    r"{[\omega^2-\Omega_k^2]^2+4\,\omega_k^2\,\Gamma_k^2}$",
    fontsize=10.0, facecolor="#fffdfd", edgecolor="#e0b4b4")

add_text_box(ax, rx + 0.04, ry + 0.05, rw - 0.08, 0.05,
    "Dielectric loss  •  Phononic resonators  •  THz / IR",
    fontsize=9.0, facecolor="#fff5f5", edgecolor="#e6b8b8")

ax.text(rx + rw/2, ry + 0.018,
    "Spectra from documented input parameters",
    ha="center", va="center", fontsize=9.5, style="italic", color="#333333")


# ============================================================
# CONNECTING ARROWS
# ============================================================
arrow1 = FancyArrowPatch(
    (left[0] + left[2] + 0.01, 0.52), (mid[0] - 0.012, 0.52),
    arrowstyle="simple", mutation_scale=18,
    linewidth=1.2, color="#7a7a7a", alpha=0.9)
ax.add_patch(arrow1)
ax.text(0.338, 0.545, "Microscopic\nformalism",
        ha="center", va="bottom", fontsize=9.5, color="#555555")

arrow2 = FancyArrowPatch(
    (mid[0] + mid[2] + 0.01, 0.52), (right[0] - 0.012, 0.52),
    arrowstyle="simple", mutation_scale=18,
    linewidth=1.2, color="#7a7a7a", alpha=0.9)
ax.add_patch(arrow2)
ax.text(0.662, 0.545, "Compact\nresponse model",
        ha="center", va="bottom", fontsize=9.5, color="#555555")


# ============================================================
# FOOTER
# ============================================================
ax.text(0.5, 0.075,
    "A provenance-aware framework linking anharmonic lattice dynamics, documented phonon\n"
    "data, and mode-resolved infrared response in disordered polar crystals.",
    ha="center", va="center", fontsize=11, color="#222222", linespacing=1.3)

ax.text(0.5, 0.03,
    r"Linewidth inputs: semi-empirical INS-calibrated reference data for BaTiO$_3$,"
    r" published anharmonic / damping data for SrTiO$_3$.",
    ha="center", va="center", fontsize=9.5, color="#555555")


# ============================================================
# SAVE
# ============================================================
figures_dir = Path(__file__).resolve().parent.parent / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)
output_file = figures_dir / "graphical_abstract.png"
plt.savefig(output_file, dpi=600, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Saved: {output_file}")
