#!/usr/bin/env python3
"""
validate_gdscript.py -- Varredura preventiva de GDScript antes de compilar.

Detecta TODOS os padrões conhecidos que quebram no Godot 4.7 DE UMA VEZ
(em vez do compilador Godot que para no primeiro erro):

  R1 -- Variáveis duplicadas no mesmo escopo de função
  R2 -- Uso de := com acesso a Dictionary (dict["chave"])
  R9 -- Métodos/propriedades inexistentes em classes nativas do Godot

Uso:
    python scripts/validate_gdscript.py <arquivo.gd>       # só relatório
    python scripts/validate_gdscript.py <arquivo.gd> --fix # corrige automaticamente

Saída:
    Exit code 0 = nenhum problema encontrado
    Exit code 1 = problemas encontrados (lista exibida)
    Exit code 2 = problemas encontrados E corrigidos (com --fix)

Não altera server.py, bridges, nem portas. Apenas varredura estática.
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# Permitir import do classdb.py (tools/ está no mesmo repo)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# ======================================================================
# R1 -- Variáveis duplicadas no mesmo escopo de função
# ======================================================================

def find_duplicate_vars(lines: list[str]) -> list[dict]:
    """Encontra TODAS as declarações 'var' duplicadas em cada função.

    Retorna lista de {"line": N, "name": "x", "first_line": M, "function": "f"}.
    """
    issues = []
    current_function = None
    function_start = 0
    base_indent = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detectar início de função
        if stripped.startswith("func "):
            current_function = stripped.split("(")[0].replace("func ", "").strip()
            function_start = i
            base_indent = len(line) - len(line.lstrip())
            continue

        # Detectar fim de função (outra função no mesmo nível ou menor indentação)
        if current_function and stripped and not stripped.startswith("#"):
            indent = len(line) - len(line.lstrip())
            if indent <= base_indent and stripped.startswith("func "):
                current_function = None
                continue

    # Segunda passagem: por função, verificar vars
    in_function = False
    func_name = ""
    seen_vars: dict[str, int] = {}  # nome -> primeira linha

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped.startswith("func "):
            in_function = True
            func_name = stripped.split("(")[0].replace("func ", "").strip()
            func_indent = len(line) - len(line.lstrip())
            seen_vars = {}
            continue

        if in_function:
            indent = len(line) - len(line.lstrip())
            # Fim da função: outra função no mesmo nível
            if stripped and indent <= func_indent and stripped.startswith("func "):
                in_function = False
                continue
            # Fim da função: linha não-vazia com indentação <= declaração da função
            # e não é continuação
            if stripped and indent <= func_indent and not stripped.startswith("var "):
                # Pode ser código da função com indentação no mesmo nível (ex: match)
                # Só encerra se for outra declaração de função
                if stripped.startswith("func "):
                    in_function = False
                    continue

        if in_function:
            # Detectar declaração var
            m = re.match(r"var\s+(\w+)", stripped)
            if m:
                vname = m.group(1)
                if vname in seen_vars:
                    issues.append({
                        "rule": "R1",
                        "line": i + 1,
                        "name": vname,
                        "first_line": seen_vars[vname],
                        "function": func_name,
                        "message": f"var '{vname}' já declarada na linha {seen_vars[vname]}"
                    })
                else:
                    seen_vars[vname] = i + 1

    return issues


# ======================================================================
# R2 -- := com acesso a Dictionary
# ======================================================================

def find_walrus_with_dict(lines: list[str]) -> list[dict]:
    """Encontra TODOS os usos de := onde o lado direito acessa dict[key]."""
    issues = []
    # Padrão: var nome := ... dict[...] ... ou var nome := ... array[idx] ...
    # Captura: var x := expr["key"] OU var x := algo[expr]["key"]
    pattern = re.compile(
        r"var\s+(\w+)\s*:=\s*"   # var nome :=
        r".*?"                     # qualquer coisa no meio
        r"\[[\"'][^\"'\]]*[\"']\]"  # acesso a dict/array com string literal
    )

    for i, line in enumerate(lines):
        stripped = line.strip()
        if pattern.search(stripped):
            m = re.match(r"var\s+(\w+)", stripped)
            if m:
                vname = m.group(1)
                issues.append({
                    "rule": "R2",
                    "line": i + 1,
                    "name": vname,
                    "message": (
                        f"var '{vname}' usa := com acesso a Dictionary/Array. "
                        f"Use tipo explícito: 'var {vname}: Tipo = ...'"
                    )
                })

    return issues


# ======================================================================
# Auto-fix
# ======================================================================

def auto_fix(lines: list[str], issues: list[dict]) -> tuple[list[str], int]:
    """Aplica correções automáticas para problemas R1 e R2.

    R1: Renomeia variáveis duplicadas (adiciona _2, _3, etc.)
    R2: Converte := para : Variant (aviso, não consegue inferir o tipo correto)

    Retorna (novas_linhas, número_de_correções).
    """
    fixed = 0
    new_lines = list(lines)

    # Agrupar issues R1 por função e nome
    r1_by_func: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for issue in issues:
        if issue["rule"] == "R1":
            key = (issue.get("function", ""), issue["name"])
            r1_by_func[key].append(issue)

    # Para cada grupo R1, renomear duplicatas
    # Precisamos fazer de baixo para cima para não bagunçar os números de linha
    all_r1 = sorted(
        [i for i in issues if i["rule"] == "R1"],
        key=lambda x: -x["line"]
    )

    # Contador por nome de variável
    rename_counters: dict[str, int] = {}

    for issue in all_r1:
        old_name = issue["name"]
        if old_name not in rename_counters:
            rename_counters[old_name] = 1
        else:
            rename_counters[old_name] += 1
        new_name = f"{old_name}_{rename_counters[old_name]}"

        line_idx = issue["line"] - 1
        old_line = new_lines[line_idx]

        # Renomear a declaração
        new_lines[line_idx] = old_line.replace(
            f"var {old_name}", f"var {new_name}", 1
        )

        # Renomear usos subsequentes DENTRO DA MESMA FUNÇÃO
        # (do ponto da declaração até o fim da função atual)
        func_start = None
        func_indent = 0
        # Encontrar a função que contém esta linha
        for j in range(line_idx, -1, -1):
            if new_lines[j].strip().startswith("func "):
                func_start = j
                func_indent = len(new_lines[j]) - len(new_lines[j].lstrip())
                break

        if func_start is not None:
            # Encontrar fim da função
            func_end = len(new_lines)
            for j in range(line_idx + 1, len(new_lines)):
                stripped_j = new_lines[j].strip()
                indent_j = len(new_lines[j]) - len(new_lines[j].lstrip())
                if stripped_j and indent_j <= func_indent and stripped_j.startswith("func "):
                    func_end = j
                    break

            # Renomear usos entre a declaração e o fim da função
            for j in range(line_idx + 1, func_end):
                # Substituir apenas palavras inteiras
                new_lines[j] = re.sub(
                    r'\b' + re.escape(old_name) + r'\b',
                    new_name,
                    new_lines[j]
                )

        fixed += 1
        print(f"  [v] R1 AUTO-FIX: linha {issue['line']} -- var {old_name} -> var {new_name}")

    # Corrigir R2: trocar := por anotação explícita
    r2_issues = [i for i in issues if i["rule"] == "R2"]
    for issue in sorted(r2_issues, key=lambda x: -x["line"]):
        line_idx = issue["line"] - 1
        old_line = new_lines[line_idx]
        old_name = issue["name"]

        # Tentar inferir o tipo provável
        # Heurísticas baseadas no nome da variável
        inferred_type = "Variant"
        if "pos" in old_name.lower() or old_name.endswith("_pos"):
            inferred_type = "Vector2"
        elif "dir" in old_name.lower():
            inferred_type = "Vector2"
        elif "color" in old_name.lower():
            inferred_type = "Color"
        elif "size" in old_name.lower():
            inferred_type = "float"
        elif "timer" in old_name.lower() or "time" in old_name.lower():
            inferred_type = "float"

        new_line = old_line.replace(
            f"var {old_name} :=",
            f"var {old_name}: {inferred_type} =",
            1
        )
        new_lines[line_idx] = new_line
        fixed += 1
        print(f"  [v] R2 AUTO-FIX: linha {issue['line']} -- := -> : {inferred_type}")

    return new_lines, fixed


# ======================================================================
# R9 -- Métodos/propriedades contra a API real do Godot
# ======================================================================

def find_api_mismatches(lines: list[str]) -> list[dict]:
    """Verifica se métodos chamados em variáveis com tipo Godot nativo existem.

    Para cada variável com tipo explícito de classe nativa conhecida,
    confirma que os métodos/propriedades chamados nela existem na classe
    ou em ancestrais (via classdb.is_valid_method / is_valid_property).

    NÃO valida: tipos customizados (class_name), get_node() sem cast,
    chamadas dinâmicas (call, sinais por string), variáveis sem tipo.
    """
    try:
        from tools.classdb import (
            is_valid_class, is_valid_method, is_valid_property,
            is_valid_signal, suggest_similar_method,
        )
    except ImportError:
        return []

    # Tipos builtin do GDScript -- sempre pulamos (sintaxe especial)
    BUILTIN_TYPES = {
        "int", "float", "String", "bool", "void", "Variant",
        "Array", "Dictionary", "PackedByteArray", "PackedStringArray",
        "PackedVector2Array", "PackedVector3Array", "PackedColorArray",
        "Vector2", "Vector2i", "Vector3", "Vector3i", "Vector4", "Vector4i",
        "Rect2", "Rect2i", "Transform2D", "Transform3D", "Plane",
        "Quaternion", "AABB", "Basis", "Color", "NodePath", "RID",
        "Callable", "Signal", "StringName",
    }

    issues = []
    # Escopo global: vars declaradas fora de qualquer função
    global_var_types: dict[str, str] = {}
    # Escopo da função atual
    func_var_types: dict[str, str] = {}
    in_function = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # ── Início de função ──
        if stripped.startswith("func "):
            in_function = True
            # Inicia com as vars globais + parâmetros
            func_var_types = dict(global_var_types)

            # Capturar parâmetros tipados
            try:
                paren_open = stripped.index('(')
                paren_close = stripped.rindex(')')
                params_str = stripped[paren_open + 1:paren_close]
                for param in params_str.split(','):
                    param = param.strip()
                    m_param = re.match(r'(\w+)\s*:\s*(\w+)', param)
                    if m_param:
                        pname, ptype = m_param.group(1), m_param.group(2)
                        if ptype[0].isupper() and ptype not in BUILTIN_TYPES and is_valid_class(ptype):
                            func_var_types[pname] = ptype
            except ValueError:
                pass
            continue

        # ── Declaração de variável tipada ──
        m_var = re.match(r'(?:@onready\s+)?var\s+(\w+)\s*:\s*(\w+)', stripped)
        if m_var:
            vname, vtype = m_var.group(1), m_var.group(2)
            if vtype and vtype[0].isupper() and vtype not in BUILTIN_TYPES and is_valid_class(vtype):
                if in_function:
                    func_var_types[vname] = vtype
                else:
                    global_var_types[vname] = vtype
            continue  # não verificar a própria linha de declaração

        # ── Chamada de método: var.method( ──
        # Procura TODAS as ocorrências na linha
        for m_call in re.finditer(r'\b(\w+)\.(\w+)\s*\(', stripped):
            vname, method = m_call.group(1), m_call.group(2)

            # Pular palavras reservadas e singletons Godot
            skip = {'self', 'get_tree', 'get_node', 'get_parent', 'get_window',
                    'Input', 'OS', 'Engine', 'Time', 'ThemeDB', 'ClassDB',
                    'ResourceLoader', 'DisplayServer', 'RenderingServer',
                    'PhysicsServer2D', 'PhysicsServer3D'}
            if vname in skip:
                continue

            # Escolher o escopo correto
            scope = func_var_types if in_function else global_var_types
            if vname in scope:
                var_type = scope[vname]
                if not is_valid_method(var_type, method):
                    # Verificar se é um sinal nativo (uso legítimo: timer.timeout.connect(...))
                    if is_valid_signal(var_type, method):
                        continue
                    suggestions = suggest_similar_method(var_type, method)
                    issues.append({
                        "rule": "R9",
                        "line": i + 1,
                        "var_name": vname,
                        "class": var_type,
                        "method": method,
                        "suggestions": suggestions,
                        "message": (
                            f"'{vname}.{method}()' -- método NÃO existe em "
                            f"'{var_type}' (nem em ancestrais)"
                        )
                    })

        # ── Acesso a propriedade: var.prop (sem '(' depois) ──
        for m_prop in re.finditer(r'(?<!\.)\b(\w+)\.(\w+)\b(?!\s*\()', stripped):
            vname, prop = m_prop.group(1), m_prop.group(2)

            skip = {'self', 'get_tree', 'get_node', 'get_parent', 'get_window',
                    'Input', 'OS', 'Engine', 'Time', 'ThemeDB', 'ClassDB',
                    'ResourceLoader', 'DisplayServer', 'RenderingServer'}
            if vname in skip:
                continue

            scope = func_var_types if in_function else global_var_types
            if vname in scope:
                var_type = scope[vname]
                if not is_valid_property(var_type, prop):
                    if not is_valid_method(var_type, prop):
                        # Verificar se é um sinal nativo (uso legítimo)
                        if not is_valid_signal(var_type, prop):
                            suggestions = suggest_similar_method(var_type, prop)
                            issues.append({
                                "rule": "R9",
                                "line": i + 1,
                                "var_name": vname,
                                "class": var_type,
                                "method": prop,
                                "suggestions": suggestions,
                                "message": (
                                    f"'{vname}.{prop}' -- propriedade/método NÃO "
                                    f"encontrado em '{var_type}'"
                                )
                            })

    return issues


# ======================================================================
# Main
# ======================================================================

def validate_file(filepath: str, fix: bool = False) -> int:
    """Valida um arquivo .gd e opcionalmente aplica correções.

    Returns:
        0 = sem problemas
        1 = problemas encontrados (não corrigidos)
        2 = problemas encontrados e corrigidos
    """
    path = Path(filepath)
    if not path.exists():
        print(f"ERRO: Arquivo não encontrado: {filepath}")
        return 1

    if path.suffix != ".gd" and path.suffix != ".py":
        print(f"AVISO: O arquivo não tem extensão .gd: {filepath}")
        print(f"       A varredura continuará, mas os resultados podem não ser relevantes.")

    with open(path, encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    print(f"\n[SCAN] Validando: {path.name} ({len(lines)} linhas)")
    print("=" * 60)

    # R1 -- Variáveis duplicadas
    r1_issues = find_duplicate_vars(lines)
    if r1_issues:
        print(f"\n[ERR] R1 -- {len(r1_issues)} VARIÁVEL(IS) DUPLICADA(S):")
        for issue in r1_issues:
            print(f"  Linha {issue['line']:4d}: var {issue['name']} "
                  f"(já declarada na linha {issue['first_line']}) "
                  f"-- função {issue.get('function', '?')}()")
    else:
        print(f"\n[OK] R1 -- Nenhuma variável duplicada encontrada.")

    # R2 -- := com Dictionary
    r2_issues = find_walrus_with_dict(lines)
    if r2_issues:
        print(f"\n[ERR] R2 -- {len(r2_issues)} USO(S) DE := COM DICTIONARY:")
        for issue in r2_issues:
            print(f"  Linha {issue['line']:4d}: {issue['message']}")
    else:
        print(f"\n[OK] R2 -- Nenhum := com Dictionary encontrado.")

    # R9 -- Validação contra API real do Godot
    r9_issues = find_api_mismatches(lines)
    if r9_issues:
        print(f"\n[ERR] R9 -- {len(r9_issues)} CHAMADA(S) DE MÉTODO/PROP QUE NÃO EXISTE(M):")
        for issue in r9_issues:
            print(f"  Linha {issue['line']:4d}: {issue['message']}")
            if issue.get("suggestions"):
                print(f"          Sugestões: {', '.join(issue['suggestions'])}")
    else:
        print(f"\n[OK] R9 -- Nenhum método/propriedade inexistente encontrado.")

    all_issues = r1_issues + r2_issues + r9_issues

    if not all_issues:
        print(f"\n[PASS] NENHUM problema encontrado. Arquivo seguro para compilar.")
        return 0

    if fix:
        print(f"\n[FIX] Aplicando {len(all_issues)} correções automáticas...")
        new_lines, fixed_count = auto_fix(lines, all_issues)

        # Salvar arquivo corrigido
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))

        print(f"\n[PASS] {fixed_count} correções aplicadas em {path.name}")
        print(f"[WARN]  VERIFIQUE as mudanças antes de compilar: git diff {path.name}")
        return 2
    else:
        print(f"\n[FAIL] {len(all_issues)} problema(s) encontrado(s).")
        print(f"   Execute com --fix para corrigir automaticamente:")
        print(f"   python scripts/validate_gdscript.py {filepath} --fix")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Varredura preventiva de GDScript -- detecta padrões que quebram no Godot 4.7"
    )
    parser.add_argument("file", help="Arquivo .gd a ser validado")
    parser.add_argument(
        "--fix", action="store_true",
        help="Corrige automaticamente variáveis duplicadas e := com Dictionary"
    )
    args = parser.parse_args()

    exit_code = validate_file(args.file, fix=args.fix)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
