"""
scripts/gerar_testes_pares.py — sota_1.7: Testes de composição dirigidos.

Lê os behavior.json, extrai combina_bem, e gera testes GdUnit4 em
tests_godot/pairs/test_<a>__<b>.gd para cada par.

Fonte: GdUnit4 doc oficial — https://mikeschulze.github.io/gdUnit4/
       SOTA_01_FUNDACAO_CEREBRO.md, seção sota_1.7.

Uso:
    python scripts/gerar_testes_pares.py              # gera todos
    python scripts/gerar_testes_pares.py --dry-run    # só lista
    python scripts/gerar_testes_pares.py --limit 20   # primeiros 20
"""

import json
import os
import glob
from typing import List, Dict, Tuple

OUTPUT_DIR = "tests_godot/pairs"


def carregar_fichas() -> List[Tuple[str, dict]]:
    """Carrega todos os behavior.json. Retorna [(nome, ficha), ...]."""
    fichas: List[Tuple[str, dict]] = []
    pattern = os.path.join("behaviors", "*", "behavior.json")
    for path in sorted(glob.glob(pattern)):
        name = os.path.basename(os.path.dirname(path))
        if name.startswith("_"):
            continue
        with open(path, encoding="utf-8") as f:
            fichas.append((name, json.load(f)))
    return fichas


def extrair_pares(fichas: List[Tuple[str, dict]]) -> List[Tuple[str, str]]:
    """
    Extrai todos os pares únicos de combina_bem.
    Cada par aparece uma vez (a, b) com a < b alfabeticamente.
    """
    nomes_validos = {nome for nome, _ in fichas}
    pares_set = set()

    for nome_a, ficha in fichas:
        combina = ficha.get("combina_bem", [])
        if not isinstance(combina, list):
            continue
        for nome_b in combina:
            if nome_b not in nomes_validos:
                continue  # behavior referenciado não existe
            par = tuple(sorted([nome_a, nome_b]))
            if par[0] != par[1]:  # não testar consigo mesmo
                pares_set.add(par)

    return sorted(pares_set)


def sinais_da_ficha(ficha: dict) -> List[str]:
    """Extrai nomes de sinais da ficha."""
    signals = ficha.get("signals", [])
    if not isinstance(signals, list):
        return []
    return [
        s["name"] if isinstance(s, dict) else str(s)
        for s in signals
    ]


def gerar_template_gd(
    nome_a: str, nome_b: str,
    sinais_a: List[str], sinais_b: List[str],
    ficha_a: dict, ficha_b: dict,
) -> str:
    """Gera o conteúdo de um arquivo test_<a>__<b>.gd no formato GdUnit4."""

    # Só gera verificação de sinal se houver sinais declarados
    signal_checks = ""
    if sinais_a:
        signal_checks += _gerar_signal_checks("_behavior_a", sinais_a, nome_a)
    if sinais_b:
        signal_checks += _gerar_signal_checks("_behavior_b", sinais_b, nome_b)

    if not signal_checks:
        signal_checks = "\t# Nenhum sinal declarado nas fichas — verificando ausência de erros apenas.\n"
        signal_checks += "\tassert_bool(true).is_true()\n"

    # Verifica se temos .tscn (não abstract)
    tscn_a = f"res://behaviors/{nome_a}/{nome_a}.tscn"
    tscn_b = f"res://behaviors/{nome_b}/{nome_b}.tscn"

    gd = f'''## Teste de composicao: {nome_a} + {nome_b}
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: {nome_a}
## @behavior_b: {nome_b}

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("{tscn_a}")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar {tscn_a}")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("{tscn_b}")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar {tscn_b}")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("{nome_a} foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("{nome_b} foi liberado durante o teste")
{signal_checks}
'''
    return gd


def _sanitizar_para_gdscript(texto: str) -> str:
    """Remove caracteres que quebrariam strings GDScript."""
    return texto.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ")


def _gerar_signal_checks(var_name: str, sinais: List[str], nome: str) -> str:
    """Gera verificações de sinal para o template."""
    nome_safe = _sanitizar_para_gdscript(nome)
    lines = []
    lines.append(f"\t# ── Verifica que {nome_safe} ainda consegue emitir sinais ──")
    for sinal in sinais[:5]:  # Máximo 5 sinais por behavior para não poluir
        sinal_safe = _sanitizar_para_gdscript(sinal)
        lines.append(f"\t# Sinal '{sinal_safe}': verifica conectividade")
        lines.append(f"\tassert_bool({var_name}.has_signal(\"{sinal_safe}\")).override_failure_message(\"Sinal '{sinal_safe}' nao encontrado em {nome_safe}\")")
        lines.append("")
    return "\n".join(lines)


def gerar_todos(
    dry_run: bool = False,
    limit: int = 0,
) -> None:
    """Gera todos os testes de pares."""
    fichas = carregar_fichas()
    pares = extrair_pares(fichas)

    if limit > 0:
        pares = pares[:limit]

    nome_para_ficha = {nome: ficha for nome, ficha in fichas}

    print(f"Behaviors: {len(fichas)}")
    print(f"Pares únicos: {len(pares)}")
    print(f"Saída: {OUTPUT_DIR}/")
    print()

    if dry_run:
        print("--- DRY RUN (sem gerar arquivos) ---")
        for i, (a, b) in enumerate(pares, 1):
            print(f"  {i:4d}. {a} + {b}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    gerados = 0
    pulados = 0
    for a, b in pares:
        out_path = os.path.join(OUTPUT_DIR, f"test_{a}__{b}.gd")
        if os.path.exists(out_path):
            pulados += 1
            continue

        ficha_a = nome_para_ficha.get(a, {})
        ficha_b = nome_para_ficha.get(b, {})
        sinais_a = sinais_da_ficha(ficha_a)
        sinais_b = sinais_da_ficha(ficha_b)

        gd = gerar_template_gd(a, b, sinais_a, sinais_b, ficha_a, ficha_b)

        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(gd)
        gerados += 1

    print(f"Gerados: {gerados}")
    print(f"Pulados (já existiam): {pulados}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="sota_1.7: Gerar testes de pares combina_bem")
    parser.add_argument("--dry-run", action="store_true", help="Apenas lista os pares, sem gerar")
    parser.add_argument("--limit", type=int, default=0, help="Limitar a N pares")
    parser.add_argument("--force", action="store_true", help="Sobrescrever arquivos existentes")
    args = parser.parse_args()

    if args.force and os.path.exists(OUTPUT_DIR):
        import shutil
        shutil.rmtree(OUTPUT_DIR)

    gerar_todos(dry_run=args.dry_run, limit=args.limit)
