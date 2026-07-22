"""fix_recipes.py — Receitas de Conserto Automatizadas (FATIA 2.AK).

Detecta erros comuns de GDScript/Godot e sugere correcoes.
7 receitas cobrem a maioria dos erros em projetos Godot.

IMPORTANTE: Automatiza apenas a CONFIRMACAO, nunca a aplicacao.
O humano sempre decide se aplica ou nao a correcao.

Receitas:
  1. No nao encontrado       → Sugere caminho correto
  2. Sinal → metodo errado   → Sugere assinatura correta
  3. Tipo incompativel        → Sugere cast ou correcao
  4. Recurso ausente          → Sugere criar ou importar
  5. Autoload faltando        → Sugere adicionar ao project.godot
  6. Divisao por zero         → Sugere guard clause
  7. Null por ordem de init   → Sugere @onready ou _ready()

Tools:
    analyze_error — analisa um erro e sugere receita
    list_recipes — lista todas as receitas disponiveis
    apply_recipe — gera codigo da receita (confirmacao, nao aplica)
"""

import json
import re
from pathlib import Path

# ── Receitas ────────────────────────────────────────────────────────

RECIPES = {
    "node_not_found": {
        "id": "node_not_found",
        "title": "No nao encontrado",
        "patterns": [
            r"Node not found: ['\"](?P<path>[^'\"]+)['\"]",
            r"get_node.*?(?P<path>[^)]+)\).*?not found",
            r"Cannot get node ['\"](?P<path>[^'\"]+)['\"]",
        ],
        "severity": "error",
        "description": "O caminho do no nao existe na cena. Pode ser erro de digitação, caminho errado ou no removido.",
        "suggestion_template": (
            "Verifique se o no '{path}' existe na cena atual.\n"
            "Use $NomeNo para caminhos diretos ou get_node(\"Caminho/Completo\") para aninhados.\n"
            "Dica: nomes de nos sao case-sensitive. '$Player' ≠ '$player'."
        ),
        "auto_fix_possible": False,
    },
    "signal_method_mismatch": {
        "id": "signal_method_mismatch",
        "title": "Sinal conectado a metodo inexistente",
        "patterns": [
            r"Method.*?(?P<method>[^(]+).*?not found.*?signal",
            r"connect\(.*?,\s*['\"](?P<method>[^'\"]+)['\"]\)",
        ],
        "severity": "error",
        "description": "Um sinal esta conectado a um metodo que nao existe ou tem assinatura errada.",
        "suggestion_template": (
            "O metodo '{method}' nao foi encontrado.\n"
            "Verifique se o nome esta correto e se a assinatura bate com os parametros do sinal.\n"
            "Ex: signal meu_sinal(valor: int) → func _on_meu_sinal(valor: int):"
        ),
        "auto_fix_possible": False,
    },
    "type_mismatch": {
        "id": "type_mismatch",
        "title": "Tipo incompativel",
        "patterns": [
            r"Cannot assign.*?(?P<from_type>\w+).*?to.*?(?P<to_type>\w+)",
            r"Invalid type.*?expected.*?(?P<to_type>\w+).*?got.*?(?P<from_type>\w+)",
            r"type mismatch.*?(?P<from_type>\w+).*?(?P<to_type>\w+)",
        ],
        "severity": "error",
        "description": "Tentativa de atribuir um valor de tipo errado a uma variavel tipada.",
        "suggestion_template": (
            "Conversao de tipo necessaria: '{from_type}' → '{to_type}'.\n"
            "Use: var valor: {to_type} = meu_valor as {to_type}\n"
            "Ou converta explicitamente: int(), float(), str(), Vector2()."
        ),
        "auto_fix_possible": True,
    },
    "resource_missing": {
        "id": "resource_missing",
        "title": "Recurso ausente",
        "patterns": [
            r"Resource.*?['\"](?P<path>[^'\"]+)['\"].*?not found",
            r"Failed to load.*?['\"](?P<path>[^'\"]+)['\"]",
            r"Cannot open.*?['\"](?P<path>[^'\"]+)['\"]",
        ],
        "severity": "error",
        "description": "Arquivo de recurso (.tscn, .tres, .png, etc.) nao encontrado.",
        "suggestion_template": (
            "Recurso '{path}' nao encontrado.\n"
            "Verifique: 1) O arquivo existe? 2) O caminho esta correto?\n"
            "Use caminhos 'res://' relativos a raiz do projeto.\n"
            "Ex: res://scenes/player.tscn em vez de scenes/player.tscn"
        ),
        "auto_fix_possible": False,
    },
    "autoload_missing": {
        "id": "autoload_missing",
        "title": "Autoload faltando",
        "patterns": [
            r"Identifier ['\"](?P<name>[^'\"]+)['\"].*?not declared",
            r"Undeclared identifier.*?(?P<name>\w+)",
        ],
        "severity": "error",
        "description": "Referencia a um autoload que nao esta registrado no project.godot.",
        "suggestion_template": (
            "Autoload '{name}' nao declarado.\n"
            "Adicione ao project.godot:\n"
            "[autoload]\n"
            "{name}=\"res://caminho/para/{name}.gd\"\n"
            "Depois reinicie o Godot para aplicar."
        ),
        "auto_fix_possible": True,
    },
    "division_by_zero": {
        "id": "division_by_zero",
        "title": "Divisao por zero",
        "patterns": [
            r"Division by zero",
            r"divided by zero",
            r"cannot divide by zero",
        ],
        "severity": "error",
        "description": "Operacao de divisao ou modulo com divisor zero.",
        "suggestion_template": (
            "Divisao por zero detectada.\n"
            "Adicione uma guard clause antes da divisao:\n"
            "if divisor == 0:\n"
            "    return  # ou valor padrao\n"
            "resultado = valor / float(max(divisor, 1))"
        ),
        "auto_fix_possible": False,
    },
    "null_init_order": {
        "id": "null_init_order",
        "title": "Null por ordem de inicializacao",
        "patterns": [
            r"Invalid access.*?null.*?on base",
            r"Cannot call method.*?on a null",
            r"Attempt to call.*?on null",
        ],
        "severity": "error",
        "description": "Variavel acessada antes de ser inicializada. Problema comum com @onready.",
        "suggestion_template": (
            "Acesso a variavel nao inicializada.\n"
            "Use @onready var meu_no = $Caminho/No para garantir inicializacao.\n"
            "Ou verifique com: if meu_no: antes de usar.\n"
            "Ordem: _init() → @onready → _ready() → _process()"
        ),
        "auto_fix_possible": False,
    },
}


# ══════════════════════════════════════════════════════════════════════
# analyze_error
# ══════════════════════════════════════════════════════════════════════

def analyze_error(error_message: str) -> dict:
    """Analisa uma mensagem de erro e sugere a receita de conserto.

    Args:
        error_message: Texto completo da mensagem de erro (Godot output).

    Returns:
        dict com receita(s) sugerida(s) e confianca.
    """
    matches = []

    for recipe_id, recipe in RECIPES.items():
        for pattern in recipe["patterns"]:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                context = match.groupdict()
                # Preencher template com valores capturados
                suggestion = recipe["suggestion_template"]
                for key, value in context.items():
                    suggestion = suggestion.replace("{" + key + "}", str(value))

                matches.append({
                    "recipe_id": recipe_id,
                    "title": recipe["title"],
                    "severity": recipe["severity"],
                    "confidence": _calculate_confidence(recipe_id, error_message, match),
                    "captured": context,
                    "suggestion": suggestion,
                    "auto_fix_possible": recipe["auto_fix_possible"],
                })
                break  # Um padrao por receita basta

    if not matches:
        return {
            "status": "no_recipe",
            "message": "Nenhuma receita conhecida para este erro. Reporte para adicionarmos cobertura.",
            "error_preview": error_message[:200],
        }

    # Ordenar por confianca
    matches.sort(key=lambda m: m["confidence"], reverse=True)
    best = matches[0]

    return {
        "status": "recipe_found",
        "recipe": best,
        "alternatives": matches[1:3] if len(matches) > 1 else [],
        "total_matches": len(matches),
        "message": f"Receita sugerida: {best['title']} (confianca: {best['confidence']:.0%})",
        "warning": "⚠️ Receitas sao sugestoes. SEMPRE revise antes de aplicar.",
    }


# ══════════════════════════════════════════════════════════════════════
# list_recipes
# ══════════════════════════════════════════════════════════════════════

def list_recipes() -> dict:
    """Lista todas as receitas de conserto disponiveis."""
    recipes_list = []
    for recipe_id, recipe in RECIPES.items():
        recipes_list.append({
            "id": recipe_id,
            "title": recipe["title"],
            "severity": recipe["severity"],
            "description": recipe["description"],
            "auto_fix_possible": recipe["auto_fix_possible"],
            "patterns_count": len(recipe["patterns"]),
        })

    return {
        "status": "success",
        "total": len(recipes_list),
        "recipes": recipes_list,
        "message": f"{len(recipes_list)} receitas disponiveis. Use analyze_error() para diagnosticar.",
    }


# ══════════════════════════════════════════════════════════════════════
# apply_recipe
# ══════════════════════════════════════════════════════════════════════

def apply_recipe(
    recipe_id: str,
    error_message: str,
    confirm: bool = False,
) -> dict:
    """Gera o codigo da receita para revisao humana.

    NAO APLICA automaticamente. Retorna o codigo sugerido para revisao.

    Args:
        recipe_id: ID da receita (ex: 'node_not_found').
        error_message: Mensagem de erro original.
        confirm: Deve ser True para confirmar que o humano revisou.

    Returns:
        dict com codigo sugerido ou mensagem de confirmacao.
    """
    if recipe_id not in RECIPES:
        return {"status": "error", "message": f"Receita desconhecida: {recipe_id}. Use list_recipes()."}

    if not confirm:
        return {
            "status": "requires_confirmation",
            "recipe": RECIPES[recipe_id]["title"],
            "message": "Confirme que voce revisou a sugestao antes de gerar o codigo. Use confirm=True.",
            "warning": "⚠️ Nunca aplique correcoes sem revisao humana.",
        }

    recipe = RECIPES[recipe_id]

    # Analisar o erro para extrair contexto
    analysis = analyze_error(error_message)
    if analysis["status"] != "recipe_found":
        return {"status": "error", "message": "Nao foi possivel analisar o erro com esta receita."}

    suggestion = analysis["recipe"]["suggestion"]

    # Gerar codigo especifico por tipo de receita
    fix_code = _generate_fix_code(recipe_id, analysis["recipe"]["captured"])

    return {
        "status": "code_generated",
        "recipe": recipe["title"],
        "suggestion": suggestion,
        "fix_code": fix_code,
        "message": "Codigo gerado para revisao. Revise e aplique manualmente.",
        "warning": "⚠️ Este codigo e uma sugestao. Teste antes de commitar.",
    }


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _calculate_confidence(recipe_id: str, error_message: str, match: re.Match) -> float:
    """Calcula confianca da receita (0.0 a 1.0)."""
    base = 0.7  # Confianca base por pattern match

    # Bonus por multiplos patterns
    pattern_count = len(RECIPES[recipe_id]["patterns"])
    if pattern_count > 1:
        base += 0.1

    # Bonus por match especifico (mais grupos capturados = mais confianca)
    groups = match.groupdict()
    if len(groups) > 1:
        base += 0.1

    # Penalidade por mensagem muito curta
    if len(error_message) < 100:
        base -= 0.1

    return min(base, 1.0)


def _generate_fix_code(recipe_id: str, context: dict) -> str:
    """Gera codigo de correcao especifico por tipo de receita."""
    if recipe_id == "node_not_found":
        path = context.get("path", "Caminho/No")
        return (
            f"# Verifique se o no existe na cena:\n"
            f"@onready var meu_no = ${path.split('/')[-1]}\n"
            f"# Ou use caminho completo:\n"
            f"# @onready var meu_no = $\"{path}\""
        )

    elif recipe_id == "type_mismatch":
        from_type = context.get("from_type", "Variant")
        to_type = context.get("to_type", "int")
        return (
            f"# Conversao explicita de tipo:\n"
            f"var valor: {to_type} = meu_valor as {to_type}\n"
            f"# Ou use funcao de conversao:\n"
            f"# var valor = {to_type.lower()}(meu_valor)"
        )

    elif recipe_id == "autoload_missing":
        name = context.get("name", "MeuAutoload")
        return (
            f"# Adicione ao project.godot:\n"
            f"# [autoload]\n"
            f"# {name}=\"res://autoloads/{name.lower()}.gd\""
        )

    elif recipe_id == "division_by_zero":
        return (
            "# Adicione guard clause:\n"
            "if divisor == 0:\n"
            "    return valor_padrao\n"
            "resultado = valor / float(divisor)"
        )

    elif recipe_id == "null_init_order":
        return (
            "# Use @onready para garantir inicializacao:\n"
            "@onready var meu_no = $Caminho/No\n"
            "# E verifique antes de usar:\n"
            "# if meu_no: meu_no.metodo()"
        )

    elif recipe_id == "resource_missing":
        path = context.get("path", "res://caminho/arquivo.tres")
        return (
            f"# Verifique o caminho do recurso:\n"
            f"# var recurso = load(\"{path}\")\n"
            f"# Caminhos devem comecar com res://"
        )

    elif recipe_id == "signal_method_mismatch":
        method = context.get("method", "meu_callback")
        return (
            f"# Verifique a assinatura do metodo:\n"
            f"# func {method}(param1: Tipo) -> void:\n"
            f"#     pass"
        )

    return "# Consulte a sugestao na analise do erro."
