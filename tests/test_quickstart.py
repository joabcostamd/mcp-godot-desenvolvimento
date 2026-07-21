"""Teste do quickstart_manage."""
import sys; sys.path.insert(0, ".")

def test_match_blueprint():
    """Verifica que _match_blueprint funciona com frases conhecidas."""
    from tools.quickstart_ops import _match_blueprint

    # Deve matchar plataforma
    bp, name, score = _match_blueprint("jogo de plataforma com herói que pula")
    assert bp is not None, f"Match falhou para plataforma: name={name}, score={score}"
    print(f"  plataforma: {name} (score={score:.2f})")

    # Deve matchar tiro
    bp, name, score = _match_blueprint("jogo de tiro com nave espacial")
    assert bp is not None, f"Match falhou para tiro: name={name}, score={score}"
    print(f"  tiro: {name} (score={score:.2f})")

    # Frase sem sentido deve retornar None
    bp, name, score = _match_blueprint("xyz abc def ghi jkl mno")
    assert bp is None or score < 0.3, f"Match indevido para frase sem sentido: {name}"
    print(f"  sem sentido: {name or 'None'} (score={score:.2f})")

def test_quickstart_tool_exists():
    """Verifica que a tool quickstart_manage está registrada."""
    from server import _build_handlers
    h = _build_handlers()
    assert "quickstart_manage" in h, "Tool quickstart_manage nao encontrada"
    print("  tool registrada: OK")

def test_quickstart_validation():
    """Verifica validação de entrada."""
    from tools.quickstart_ops import quickstart_manage

    r = quickstart_manage(op="run", phrase="")
    assert r["status"] == "error", f"Esperava erro para frase vazia: {r}"
    print("  validacao frase vazia: OK")

    r = quickstart_manage(op="invalido", phrase="teste")
    assert r["status"] == "error", f"Esperava erro para op invalida: {r}"
    print("  validacao op invalida: OK")

if __name__ == "__main__":
    test_match_blueprint()
    test_quickstart_tool_exists()
    test_quickstart_validation()
    print("[PASS] quickstart — todos os testes passaram")
