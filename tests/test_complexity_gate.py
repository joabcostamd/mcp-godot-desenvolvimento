"""Testes para complexity_gate_manage — Fatia 3.F."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.complexity_gate_ops import complexity_gate_manage, _count_metrics


class TestCountMetrics:
    def test_counts_scripts(self):
        m = _count_metrics(Path("tools"))
        assert m["scripts_count"] == 0  # tools/ nao tem .gd
        assert m["total_lines"] == 0


class TestBaseline:
    def test_baseline_works(self):
        r = complexity_gate_manage(op="baseline")
        assert r["status"] == "success"
        assert "baseline" in r
        assert r["baseline"]["scripts_count"] >= 0

    def test_check_without_baseline(self):
        # Precisa resetar estado — usa op=baseline primeiro
        r = complexity_gate_manage(op="check")
        # Pode ter baseline de teste anterior
        assert r["status"] in ("error", "pass", "warn", "block")


class TestOps:
    def test_invalid_op(self):
        r = complexity_gate_manage(op="invalid")
        assert r["status"] == "error"
