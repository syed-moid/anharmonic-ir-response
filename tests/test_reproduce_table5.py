"""
Regression test: the committed CSV data must reproduce the published Table 5.

Run with:  pytest -q
or:        python -m pytest tests/

These tests fit Gamma(T) = A + B*T + C*T**2 to the committed BaTiO3 and SrTiO3
data and assert that the recovered coefficients, R^2, and Gamma(300 K) match the
values printed in the manuscript (Table 5) within tolerance.
If a data file or fit ever changes such that the paper is no longer reproduced,
these tests fail.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import (  # noqa: E402
    PUBLISHED_TABLE5, T_REF, fit_abc, load_bto_modes, load_sto_literature,
)

ATOL = {"A": 3e-3, "B": 5e-5, "C": 3e-7, "g300": 0.02, "r2": 0.01}

CASES = []
for material, loader, modes_order in (
    ("BaTiO3", load_bto_modes, ["TO1 (soft)", "TO2", "TO3"]),
    ("SrTiO3", load_sto_literature, ["TO1 (soft)", "TO2"]),
):
    for label in modes_order:
        CASES.append((material, loader, label))


@pytest.mark.parametrize("material,loader,label", CASES,
                         ids=[f"{m}-{lab}" for m, _, lab in CASES])
def test_fit_matches_published(material, loader, label):
    modes = loader()
    s = modes[label]
    fit = fit_abc(s.T, s.gamma_THz)
    A, B, C, g300, r2 = PUBLISHED_TABLE5[material][label]

    assert fit.A == pytest.approx(A, abs=ATOL["A"]), f"{material} {label} A"
    assert fit.B == pytest.approx(B, abs=ATOL["B"]), f"{material} {label} B"
    assert fit.C == pytest.approx(C, abs=ATOL["C"]), f"{material} {label} C"
    assert fit.r2 == pytest.approx(r2, abs=ATOL["r2"]), f"{material} {label} R2"
    # Table 5's "Gamma(300 K)" column is the raw measured/computed datapoint at
    # 300 K, not the polynomial evaluation (see ModeSeries.gamma_at docstring).
    assert s.gamma_at(T_REF) == pytest.approx(g300, abs=ATOL["g300"]), \
        f"{material} {label} Gamma(300) datapoint"


def test_soft_mode_polynomial_overshoots_at_300K():
    """Documented subtlety: the BaTiO3 soft-mode A+BT+CT^2 fit overshoots the
    300 K datapoint (~0.29 vs 0.25). This is why Table 5 reports the datapoint."""
    modes = load_bto_modes()
    s = modes["TO1 (soft)"]
    fit = fit_abc(s.T, s.gamma_THz)
    assert s.gamma_at(T_REF) == pytest.approx(0.254, abs=0.01)
    assert float(fit.gamma(T_REF)) == pytest.approx(0.29, abs=0.01)
