"""Teste do modo remix — clonar jogo-semente."""
import sys; sys.path.insert(0, ".")
from tools.quickstart_ops import quickstart_manage, _clone_seed

def test_remix_success():
    """C1: remix do breakout funciona."""
    r = quickstart_manage(op="remix", seed="breakout", project_name="teste_remix")
    assert r.get("status") == "success", f"Remix falhou: {r}"
    assert r.get("seed") == "breakout"
    assert r.get("scenes_copied", 0) > 0
    print(f"  projeto: {r.get('project_name')}, cenas: {r.get('scenes_copied')}")

def test_remix_invalid_seed():
    """C4: seed inexistente retorna erro."""
    r = quickstart_manage(op="remix", seed="xyz_inexistente")
    assert r.get("status") == "error", f"Esperava erro para seed invalida: {r}"
    assert "nao encontrada" in r.get("message", "")
    print(f"  erro: {r.get('message')}")

def test_run_still_works():
    """C5: op=run continua funcionando."""
    r = quickstart_manage(op="run", phrase="jogo de plataforma", project_name="teste_run_pos_remix")
    assert r.get("status") == "success", f"Run falhou apos remix: {r}"
    print(f"  run OK: {r.get('blueprint')}")

if __name__ == "__main__":
    test_remix_success()
    test_remix_invalid_seed()
    test_run_still_works()
    print("[PASS] remix — todos os testes passaram")
