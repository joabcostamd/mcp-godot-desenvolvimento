"""Teste do modo remix — clonar jogo-semente."""
import sys; sys.path.insert(0, ".")
import shutil
from pathlib import Path
from tools.quickstart_ops import quickstart_manage, _clone_seed

# Diretórios criados pelos testes — limpeza pós-teste
_TEST_DIRS = [
    Path("C:/Users/joabc/OneDrive/Documentos/VSCODE/NUCLEO/projetos/teste_remix"),
    Path("C:/Users/joabc/OneDrive/Documentos/VSCODE/NUCLEO/projetos/teste_run_pos_remix"),
]


def _cleanup():
    """Remove diretórios de teste residuais (bug de isolamento corrigido em E5)."""
    for d in _TEST_DIRS:
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)


def test_remix_success():
    """C1: remix do breakout funciona."""
    _cleanup()  # Garante ambiente limpo antes
    try:
        r = quickstart_manage(op="remix", seed="breakout", project_name="teste_remix")
        assert r.get("status") == "success", f"Remix falhou: {r}"
        assert r.get("seed") == "breakout"
        assert r.get("scenes_copied", 0) > 0
        print(f"  projeto: {r.get('project_name')}, cenas: {r.get('scenes_copied')}")
    finally:
        _cleanup()  # Limpa sempre, mesmo se falhar


def test_remix_invalid_seed():
    """C4: seed inexistente retorna erro."""
    r = quickstart_manage(op="remix", seed="xyz_inexistente")
    assert r.get("status") == "error", f"Esperava erro para seed invalida: {r}"
    assert "nao encontrada" in r.get("message", "")
    print(f"  erro: {r.get('message')}")


def test_run_still_works():
    """C5: op=run continua funcionando."""
    _cleanup()  # Garante ambiente limpo antes
    try:
        r = quickstart_manage(op="run", phrase="jogo de plataforma", project_name="teste_run_pos_remix")
        assert r.get("status") == "success", f"Run falhou apos remix: {r}"
        print(f"  run OK: {r.get('blueprint')}")
    finally:
        _cleanup()  # Limpa sempre, mesmo se falhar

if __name__ == "__main__":
    test_remix_success()
    test_remix_invalid_seed()
    test_run_still_works()
    print("[PASS] remix — todos os testes passaram")
