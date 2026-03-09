from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.report.coord_writer import write_coord
from lcmodel_pyport.report.corraw_writer import write_corraw
from lcmodel_pyport.report.models import ConcentrationRow, MiscMetrics
from lcmodel_pyport.report.ps_writer import write_ps
from lcmodel_pyport.report.table_writer import write_table
from lcmodel_pyport.verify.parsers_coord import parse_coord
from lcmodel_pyport.verify.parsers_corraw import parse_corraw
from lcmodel_pyport.verify.parsers_ps import parse_ps
from lcmodel_pyport.verify.parsers_table import parse_table

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tests" / ".tmp" / "gate_g5_report_writers"
TMP.mkdir(parents=True, exist_ok=True)

# Traceability:
# - VT-C-002 maps to LCModel.f:10423-10427, 10804-10808
# - VT-C-003 maps to LCModel.f:10775-10787
# - VT-C-004 maps to LCModel.f:10810-10833
# - VT-C-001/VT-D-001 (weak .ps contract) maps to LCModel.f:10944-11064, 11476-11483


def test_vt_c_002_table_writer_contract() -> None:
    out = TMP / "out.table"
    conc = [
        ConcentrationRow(conc=1.2e-6, pct_sd=13, ratio_label="0.659", metabolite="Cr"),
        ConcentrationRow(conc=2.14e-6, pct_sd=8, ratio_label="1.171", metabolite="Glu"),
    ]
    misc = MiscMetrics(
        fwhm_ppm=0.084,
        sn=21,
        data_shift_ppm=0.008,
        phase0_deg=9,
        phase1_deg_per_ppm=2.2,
        alpha_b=1.7e-1,
        alpha_s=3.7e-1,
        spline_knots=28,
        ns=5,
        incsid=1,
        inflections=2,
        extrema=1,
    )
    write_table(out, conc, misc, ["nunfil=1024", "deltat=5e-04"])
    parsed = parse_table(out)
    assert parsed["sections_order"] == ["$$CONC", "$$MISC", "$$DIAG", "$$INPU"]
    assert parsed["concentration_rows"] == 2
    assert parsed["misc_metrics"]["alpha_b"] > 0


def test_vt_c_003_coord_writer_contract() -> None:
    out = TMP / "out.coord"
    ppm = [4.0, 3.5, 3.0, 2.5]
    phased = [0.2, 0.3, 0.4, 0.1]
    fit = [0.21, 0.31, 0.38, 0.09]
    background = [0.01, 0.02, 0.03, 0.04]
    write_coord(out, ppm, phased, fit, background)
    parsed = parse_coord(out)
    pos = parsed["positions"]
    assert pos["ppm_axis"] < pos["phased_data"] < pos["fit"] < pos["background"]


def test_vt_c_004_corraw_writer_contract() -> None:
    out = TMP / "out.corraw"
    data = [complex(0.1, -0.1), complex(0.2, -0.2), complex(0.3, -0.3)]
    write_corraw(
        out,
        hzpppm=127.786142,
        fmtdat="(2E15.6)",
        tramp=1.0,
        volume=1.0,
        data=data,
        seq="PRESS",
    )
    parsed = parse_corraw(out)
    assert parsed["has_seqpar"] is True
    assert parsed["has_nmid"] is True
    assert parsed["n_points"] == 3


def test_vt_c_001_ps_writer_contract() -> None:
    out = TMP / "out.ps"
    write_ps(
        out,
        ppm_axis=[4.0, 3.5, 3.0, 2.5],
        phased_data=[0.2, 0.3, 0.4, 0.1],
        fit=[0.21, 0.31, 0.38, 0.09],
        background=[0.01, 0.02, 0.03, 0.04],
        dofull=False,
        title="PS contract test",
    )
    text = out.read_text(encoding="utf-8")
    assert text.startswith("%!PS-Adobe-3.0")
    parsed = parse_ps(out)
    assert parsed["has_crude_model_marker"] is True
