"""adversarial_review.py — Revisor Adversarial (FATIA 3.K).

Ferramenta standalone para auditar o trabalho do implementador.
Tenta QUEBRAR a implementacao, nao confirma-la.
Nao escreve codigo — so reporta problemas.

Inspirado no agente 'revisor' do AGENTS.md.

Uso:
    python scripts/adversarial_review.py [--target <arquivo>] [--focus <area>]
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ── Lista de Verificacao Adversarial ────────────────────────────────

CHECKS = {
    "syntax": {
        "label": "Sintaxe GDScript",
        "questions": [
            "Existe @tool sem _get_configuration_warnings()?",
            "Existe variavel declarada duas vezes no mesmo escopo?",
            "Existe := com acesso a Dictionary?",
            "Existe caminho hardcoded (C:/Users/...)?",
            "Existe import nao usado?",
        ],
    },
    "security": {
        "label": "Seguranca",
        "questions": [
            "Existe OS.execute() ou OS.shell_open()?",
            "Existe FileAccess fora de res:// ou user://?",
            "Existe eval() ou Expression.execute() com input do usuario?",
            "Existe load() de .exe, .dll, .so, .dylib?",
            "Existe segredo hardcoded (token, senha, API key)?",
        ],
    },
    "architecture": {
        "label": "Arquitetura",
        "questions": [
            "Behavior extende classe correta? (Node para logica, Area2D para fisica)",
            "Dependencia circular entre behaviors?",
            "Metodo _process() ativo sem necessidade? (deveria ser event-driven)",
            "Referencia direta a no pai ($Parent) sem verificacao null?",
            "Nome de classe conflita com outro behavior?",
        ],
    },
    "integration": {
        "label": "Integracao",
        "questions": [
            "behavior.json referencia behavior que nao existe?",
            ".tres referencia script que nao existe?",
            ".tscn referencia cena que nao existe?",
            "Autoload referenciado mas nao registrado no project.godot?",
            "Sinal emitido mas nunca conectado?",
        ],
    },
    "quality": {
        "label": "Qualidade",
        "questions": [
            "Parametro @export sem range definido?",
            "Sinal sem documentacao de params?",
            "Descricao PT e EN divergentes (>20% diferente)?",
            "Behavior sem teste (test_<nome>.gd)?",
            "CHANGELOG.md nao atualizado para a versao atual?",
        ],
    },
}


def review_file(filepath: str) -> dict:
    """Revisa um arquivo individual contra todas as verificacoes."""
    path = Path(filepath)
    if not path.exists():
        return {"status": "error", "message": f"Arquivo nao encontrado: {filepath}"}

    content = path.read_text(encoding="utf-8", errors="ignore")
    ext = path.suffix.lower()

    findings = []

    if ext == ".gd":
        findings.extend(_check_gdscript(content, path))
    elif ext == ".json":
        findings.extend(_check_json(content, path))
    elif ext in (".tscn", ".tres"):
        findings.extend(_check_godot_resource(content, path))

    return {
        "status": "reviewed",
        "file": str(path),
        "findings": findings,
        "risk_level": _assess_risk(findings),
        "message": f"{len(findings)} problema(s) encontrado(s).",
    }


def _check_gdscript(content: str, path: Path) -> list[dict]:
    """Verificacoes especificas para GDScript."""
    findings = []

    # R1: Variavel duplicada no mesmo escopo
    # (ja coberto por validate_gdscript.py, mas reforcar)

    # R9: Metodo/propriedade inexistente
    # (ja coberto por validate_gdscript.py)

    # Seguranca: OS.execute, eval, FileAccess externo
    if re.search(r'OS\.execute\s*\(', content):
        findings.append({"severity": "critical", "check": "security", "message": "OS.execute() detectado"})
    if re.search(r'\beval\s*\(', content):
        findings.append({"severity": "critical", "check": "security", "message": "eval() detectado"})
    if re.search(r'FileAccess\.open\s*\(\s*"(?!/res://|user://)', content):
        findings.append({"severity": "high", "check": "security", "message": "FileAccess fora de res:// ou user://"})

    # Arquitetura: _process() desnecessario
    if "_process" in content and "extends Node" in content:
        # Verificar se _process faz algo alem de polling WebSocket
        if not re.search(r'_ws\.poll|_process_ws|_stream\.get_status', content):
            findings.append({"severity": "low", "check": "architecture", "message": "_process() ativo sem WebSocket/I/O. Prefira event-driven."})

    # Qualidade: @tool sem _get_configuration_warnings
    if "@tool" in content and "_get_configuration_warnings" not in content:
        findings.append({"severity": "medium", "check": "quality", "message": "@tool sem _get_configuration_warnings()"})

    return findings


def _check_json(content: str, path: Path) -> list[dict]:
    """Verificacoes para JSON (behavior.json, etc.)."""
    findings = []
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return [{"severity": "critical", "check": "syntax", "message": "JSON invalido"}]

    # Verificar campos obrigatorios no behavior.json
    if path.name == "behavior.json":
        for field in ["name", "version", "description_pt", "description_en"]:
            if field not in data:
                findings.append({"severity": "high", "check": "integration", "message": f"Campo obrigatorio ausente: {field}"})

    return findings


def _check_godot_resource(content: str, path: Path) -> list[dict]:
    """Verificacoes para .tscn e .tres."""
    findings = []

    # Referencias externas
    ext_resources = re.findall(r'path="([^"]+)"', content)
    for ref in ext_resources:
        ref_path = path.parent / ref
        if not ref_path.exists() and not ref.startswith("res://"):
            # Verificar caminho absoluto no projeto
            proj_ref = ROOT / ref.lstrip("res://")
            if not proj_ref.exists():
                findings.append({"severity": "high", "check": "integration", "message": f"Recurso referenciado nao encontrado: {ref}"})

    return findings


def _assess_risk(findings: list[dict]) -> str:
    """Avalia nivel de risco baseado nos findings."""
    if not findings:
        return "none"
    severities = [f["severity"] for f in findings]
    if "critical" in severities:
        return "critical"
    if "high" in severities:
        return "high"
    if "medium" in severities:
        return "medium"
    return "low"


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "behaviors"
    path = ROOT / target

    if path.is_file():
        result = review_file(str(path))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif path.is_dir():
        results = []
        for f in sorted(path.rglob("*.gd")):
            r = review_file(str(f))
            if r.get("findings"):
                results.append(r)
        print(f"Revisados: {len(list(path.rglob('*.gd')))}")
        print(f"Com problemas: {len(results)}")
        for r in results:
            print(f"  {r['file']}: {len(r['findings'])} problemas ({r['risk_level']})")
    else:
        print(f"Alvo nao encontrado: {target}")
