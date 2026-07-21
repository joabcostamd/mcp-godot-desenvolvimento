"""Testes para fun_report_manage — Fatia 3.D."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.fun_report_ops import (
    fun_report_manage,
    _analyze_approval,
    _analyze_attempts,
    _analyze_strategy,
    _analyze_escalation,
    _diagnose_failure_mode,
)


class TestSignals:
    def test_approval_no_data(self):
        r = _analyze_approval([], None)
        assert r["status"] == "no_data"

    def test_approval_balanced(self):
        personas = [
            {"result": {"completed": True, "total_time_s": 30}},
            {"result": {"completed": True, "total_time_s": 45}},
            {"result": {"completed": False, "total_time_s": 60}},
        ]
        r = _analyze_approval(personas, None)
        assert r["rate"] == pytest.approx(0.67, 0.01)
        assert r["status"] == "balanced"

    def test_approval_too_hard(self):
        personas = [
            {"result": {"completed": False}},
            {"result": {"completed": False}},
            {"result": {"completed": False}},
        ]
        r = _analyze_approval(personas, None)
        assert r["status"] == "too_hard"

    def test_attempts_consistent(self):
        personas = [
            {"result": {"total_time_s": 30}},
            {"result": {"total_time_s": 35}},
            {"result": {"total_time_s": 32}},
        ]
        r = _analyze_attempts(personas)
        assert r["status"] == "consistent"
        assert r["mean_s"] == pytest.approx(32.3, 0.1)

    def test_strategy_degenerate(self):
        personas = [
            {"inputs": [{"action": "ui_right"}, {"action": "ui_right"}]},
        ]
        r = _analyze_strategy(personas, None)
        assert r["status"] == "degenerate"
        assert r["distinct_actions"] == 1

    def test_strategy_varied(self):
        personas = [
            {"inputs": [
                {"action": "ui_right"}, {"action": "ui_up"},
                {"action": "space"}, {"action": "ui_left"},
                {"action": "ui_accept"},
            ]},
        ]
        r = _analyze_strategy(personas, None)
        assert r["status"] == "varied"


class TestDiagnosis:
    def test_no_failures_when_balanced(self):
        failures = _diagnose_failure_mode(
            {"status": "balanced", "rate": 0.5, "completed": 2, "total": 3},
            {"status": "consistent", "mean_s": 30, "std_s": 5},
            {"status": "varied", "distinct_actions": 5},
            {"status": "normal", "fps_drop": 3},
        )
        assert len(failures) == 0

    def test_detects_degenerate_strategy(self):
        failures = _diagnose_failure_mode(
            {"status": "balanced", "rate": 0.5},
            {"status": "consistent"},
            {"status": "degenerate", "distinct_actions": 1},
            {"status": "normal"},
        )
        assert any(f["mode"] == "estrategia_degenerada" for f in failures)

    def test_detects_too_hard(self):
        failures = _diagnose_failure_mode(
            {"status": "too_hard", "rate": 0.1},
            {"status": "consistent"},
            {"status": "varied"},
            {"status": "normal"},
        )
        assert any(f["mode"] == "recompensa_distante" for f in failures)


class TestOpGenerate:
    def test_generate_no_data(self):
        r = fun_report_manage(op="generate")
        assert r["status"] == "success"
        assert "Nenhum dado" in r["message"]

    def test_generate_with_data(self):
        r = fun_report_manage(op="generate", params={
            "persona_results": [
                {"result": {"completed": True, "total_time_s": 30},
                 "inputs": [{"action": "ui_right"}, {"action": "ui_up"}, {"action": "space"}]},
            ],
        })
        assert r["status"] == "success"
        assert r["signals"]["approval"]["total"] == 1

    def test_invalid_op(self):
        r = fun_report_manage(op="invalid")
        assert r["status"] == "error"
        assert "available_ops" in r
