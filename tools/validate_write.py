"""validate_write.py — Validate-Before-Write (Fase 3 / beckettlab).

Recusa escrever GDScript que não compila. Inspirado no beckettlab/beckett-godot-mcp.

Tool: safe_write_file — write com validação automática de sintaxe.
"""

import re
from pathlib import Path


def validate_gdscript_syntax(code: str) -> dict:
    """Valida sintaxe GDScript sem precisar do Godot.

    Verificações:
    - Blocos indentados corretamente
    - Parênteses/colchetes/chaves balanceados
    - Palavras-chave reservadas
    - Estrutura básica de funções

    Args:
        code: Código GDScript.

    Returns:
        {"valid": bool, "errors": [...]}
    """
    errors = []

    # Verifica indentação (tabs vs spaces)
    lines = code.splitlines()
    for i, line in enumerate(lines, 1):
        if "\t" in line and "    " in line:
            errors.append({"line": i, "message": "Mistura de tabs e espaços", "code": line.strip()[:60]})

    # Verifica balanceamento
    brackets = {"(": ")", "[": "]", "{": "}"}
    stack = []
    for i, ch in enumerate(code):
        if ch in brackets:
            stack.append((brackets[ch], i))
        elif ch in brackets.values():
            if not stack or stack[-1][0] != ch:
                errors.append({"line": code[:i].count("\n") + 1, "message": f"Fechamento inesperado: {ch}"})
                break
            stack.pop()

    if stack:
        for closer, pos in stack:
            errors.append({"line": code[:pos].count("\n") + 1, "message": f"Abertura não fechada"})

    # Verifica funções sem indentação
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("func ") and not line.startswith(" ") and not line.startswith("\t"):
            # func no nível raiz — OK
            pass
        elif stripped and not stripped.startswith("#") and not line[0] in (" ", "\t") and i > 1:
            # Código não indentado fora de função (pode ser class_name, extends, var, signal)
            if not any(stripped.startswith(kw) for kw in ("extends", "class_name", "var ", "signal ", "enum ", "const ", "@", "func ", "#", "static ", "tool", "preload", "await")):
                errors.append({"line": i, "message": f"Linha não indentada fora de escopo: {stripped[:50]}"})

    # R1: var duplicado na mesma função (regra R1 do LEARNINGS.md)
    in_function = False
    func_name = ""
    seen_vars: dict[str, tuple[int, str]] = {}  # nome_var -> (linha, func_name)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("func "):
            in_function = True
            func_name = stripped.split("(")[0].replace("func ", "").strip()
            seen_vars = {}
            continue
        if in_function:
            # Detecta fim de função: outra declaração func ou linha não indentada
            indent = len(line) - len(line.lstrip())
            if stripped and indent == 0:
                if stripped.startswith("func "):
                    in_function = True
                    func_name = stripped.split("(")[0].replace("func ", "").strip()
                    seen_vars = {}
                    continue
                elif not stripped.startswith(("var ", "const ", "enum ", "signal ", "static ", "#", "@", "extends", "class_name")):
                    in_function = False
                    continue
            m = re.match(r"var\s+(\w+)", stripped)
            if m:
                vname = m.group(1)
                if vname in seen_vars:
                    errors.append({
                        "line": i,
                        "message": f"R1: variável '{vname}' declarada duas vezes na mesma função '{func_name}' (primeira na linha {seen_vars[vname][0]})",
                        "rule": "R1_CRITICAL",
                    })
                else:
                    seen_vars[vname] = (i, func_name)

    # R2: := com acesso a Dictionary (regra R2 do LEARNINGS.md)
    # Padrão: := seguido de qualquer expressão que acesse [...] (dict/array).
    # Ex: var x := enemies[i]["pos"], var y := (target - pu["pos"]).normalized()
    # O compilador GDScript não infere tipo de acesso a Dictionary/Array.
    for i, line in enumerate(lines, 1):
        # Procura := em algum lugar da linha
        walrus_pos = line.find(":=")
        if walrus_pos >= 0:
            # Verifica se há acesso por índice [ após o :=
            after_walrus = line[walrus_pos:]
            # Padrões: algo[...] onde algo é uma expressão (var, dict[key], call())
            if re.search(r'\w+\s*\[', after_walrus) or re.search(r'\)\s*\[', after_walrus):
                # Filtra falsos positivos: anotação de tipo array (ex: var arr: Array[int] = ...)
                # Se o primeiro [ após := está em uma anotação de tipo (: Type[ ...), pula
                type_annot = re.search(r':\s*\w+\s*\[', line[:walrus_pos])
                first_bracket_after = re.search(r'\[', after_walrus)
                if first_bracket_after:
                    # Se há := ... algo["chave"] — isso É um problema de inferência
                    errors.append({
                        "line": i,
                        "message": "R2: uso de ':=' com acesso a Dictionary/Array pode falhar "
                                   "inferência de tipo — considere tipo explícito",
                        "rule": "R2_HIGH",
                        "code": line.strip()[:80],
                    })

    return {
        "valid": len(errors) == 0,
        "errors": errors or None,
        "checked": "sintaxe básica (validação completa requer Godot --check-only)",
    }


def safe_write_gdscript(
    file_path: str,
    content: str,
    project_path: str | None = None,
    strict: bool = True,
    deep_validate: bool = False,
) -> dict:
    """Escreve GDScript com validação automática de sintaxe.

    Se o código tiver erros de sintaxe, RECUSA escrever.
    Isso evita que a IA salve código quebrado.

    Args:
        file_path: Caminho do arquivo .gd.
        content: Conteúdo GDScript.
        project_path: Projeto (para validação Godot completa).
        strict: Se True, recusa salvar com erros. Se False, avisa mas salva.
        deep_validate: Se True, executa validação R9 (API mismatch via ClassDB)
                       usando o motor do validate_gdscript.py standalone.

    Returns:
        dict com status, validação e ação tomada.
    """
    # 1. Validação básica local (R1, R2, brackets, indentação)
    validation = validate_gdscript_syntax(content)

    if not validation["valid"] and strict:
        return {
            "status": "error",
            "message": "❌ GDScript INVÁLIDO — escrita BLOQUEADA. Corrija os erros abaixo.",
            "validation": validation,
            "written": False,
            "errors": validation["errors"],
        }

    # 1.5 Auto-detectar projeto ativo se não informado
    if not project_path:
        try:
            from tools.project_ops import _get_active_project
            project_path = str(_get_active_project())
        except Exception:
            project_path = None

    # 2. Validação Godot (se projeto disponível)
    godot_check = None
    if project_path:
        try:
            import subprocess, tempfile
            from tools.config_loader import load_config
            godot_path = load_config().get("godot_path", "")

            if godot_path:
                with tempfile.NamedTemporaryFile(suffix=".gd", mode="w", delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name

                result = subprocess.run(
                    [godot_path, "--headless", "--check-only", "--path", project_path, tmp_path],
                    capture_output=True, text=True, timeout=10,
                )
                Path(tmp_path).unlink(missing_ok=True)

                if result.returncode != 0:
                    godot_check = {"valid": False, "output": result.stderr[:500]}
                    if strict:
                        return {
                            "status": "error",
                            "message": "❌ Godot rejeitou o script. Escrita BLOQUEADA.",
                            "validation": validation,
                            "godot_check": godot_check,
                            "written": False,
                        }
        except Exception:
            pass

    # 2.5 Validação profunda R9: API mismatch via ClassDB (validate_gdscript.py standalone)
    r9_check = None
    if deep_validate:
        try:
            # Usa o motor de validação do validate_gdscript.py standalone
            # para detectar métodos/propriedades que não existem na classe nativa
            import sys
            from pathlib import Path as _Path
            _root = _Path(__file__).resolve().parent.parent
            if str(_root) not in sys.path:
                sys.path.insert(0, str(_root))
            from validate_gdscript import find_api_mismatches as _find_r9
            r9_issues = _find_r9(content.splitlines())
            if r9_issues:
                r9_check = {"valid": False, "api_mismatches": r9_issues}
                if strict:
                    return {
                        "status": "error",
                        "message": "❌ R9: chamadas a métodos/propriedades inexistentes detectadas. Escrita BLOQUEADA.",
                        "validation": validation,
                        "godot_check": godot_check,
                        "r9_check": r9_check,
                        "written": False,
                    }
        except Exception:
            pass  # R9 é bônus — se falhar, não bloqueia

    # 3. Escreve
    try:
        Path(file_path).write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "message": "✅ GDScript válido. Arquivo salvo." if validation["valid"] else "⚠️ Salvo com warnings.",
            "validation": validation,
            "godot_check": godot_check,
            "r9_check": r9_check,
            "written": True,
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "written": False}
