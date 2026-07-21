"""Testes para teacher_manage, scope_manage, reviewer_manage — 3.H/3.I/3.J/3.K."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.teacher_ops import teacher_manage
from tools.scope_ops import scope_manage
from tools.reviewer_ops import reviewer_manage


class TestTeacherManage:
    def test_explain_without_context(self):
        r = teacher_manage(op="explain")
        assert r["status"] == "error"

    def test_explain_with_context(self):
        r = teacher_manage(op="explain", params={"context": "criar um inimigo com patrulha"})
        assert r["status"] == "success"
        assert "o_que" in r["explanation"]
        assert "por_que" in r["explanation"]
        assert "proximo" in r["explanation"]

    def test_invalid_op(self):
        r = teacher_manage(op="invalid")
        assert r["status"] == "error"


class TestScopeManage:
    def test_validate_idea_huge(self):
        r = scope_manage(op="validate_idea", params={"idea": "MMO open world com crafting"})
        assert r["status"] == "success"
        assert r["decision"] == "contraproposta"
        assert "counter_offer" in r

    def test_validate_idea_viable(self):
        r = scope_manage(op="validate_idea", params={"idea": "jogo de plataforma simples"})
        assert r["status"] == "success"
        assert r["decision"] == "viavel"

    def test_disclosure(self):
        r = scope_manage(op="disclosure")
        assert r["status"] == "success"
        assert "steam_section" in r["disclosure"]
        assert "itch_io_section" in r["disclosure"]


class TestReviewerManage:
    def test_status_default(self):
        r = reviewer_manage(op="status")
        assert r["status"] == "success"
        assert "enabled" in r

    def test_enable_disable(self):
        reviewer_manage(op="enable", params={"reason": "teste"})
        r = reviewer_manage(op="status")
        assert r["enabled"] is True
        reviewer_manage(op="disable")
        r = reviewer_manage(op="status")
        assert r["enabled"] is False

    def test_invalid_op(self):
        r = reviewer_manage(op="invalid")
        assert r["status"] == "error"
