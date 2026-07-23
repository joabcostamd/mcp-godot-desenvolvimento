"""
scripts/rodar_testes_pares.py — sota_1.7: Runner dos testes de pares.

Invoca o Godot com GdUnit4 CLI, coleta saída JUnit XML, agrega resultados
em behaviors/_index/pares_testados.json (aresta verde/vermelha por par).

Fonte: GdUnit4 doc oficial — CLI via GdUnitCmdTool.gd.
       SOTA_01_FUNDACAO_CEREBRO.md, seção sota_1.7.

Uso:
    python scripts/rodar_testes_pares.py
    python scripts/rodar_testes_pares.py --godot <caminho>
    python scripts/rodar_testes_pares.py --par "health__health_bar"
"""

import json
import os
import sys
import time
import glob
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple

# Importa utilitários compartilhados de Godot (evita duplicação com mutar.py)
from _godot_utils import encontrar_godot, rodar_godot_headless, DEFAULT_GODOT

GODOT_PROJECT = "."
TEST_DIR = "tests_godot/pairs"
OUTPUT_JSON = "behaviors/_index/pares_testados.json"
REPORTS_DIR = "reports"


def parse_junit_reports() -> Dict[str, Dict]:
    """
    Faz parse dos reports JUnit XML em reports/.
    Retorna {test_name: {status, duration, message}}.
    """
    resultados: Dict[str, Dict] = {}
    report_pattern = os.path.join(REPORTS_DIR, "*.xml")
    xml_files = sorted(glob.glob(report_pattern), key=os.path.getmtime, reverse=True)

    for xml_file in xml_files[:10]:  # Últimos 10 reports
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for testcase in root.iter("testcase"):
                name = testcase.get("name", "")
                classname = testcase.get("classname", "")
                full_name = f"{classname}.{name}" if classname else name

                duration = float(testcase.get("time", 0))

                failure = testcase.find("failure")
                error = testcase.find("error")
                skipped = testcase.find("skipped")

                if failure is not None:
                    resultados[full_name] = {
                        "status": "vermelho",
                        "duration": duration,
                        "message": (failure.get("message", "") or "")[:500],
                    }
                elif error is not None:
                    resultados[full_name] = {
                        "status": "vermelho",
                        "duration": duration,
                        "message": (error.get("message", "") or "")[:500],
                    }
                elif skipped is not None:
                    resultados[full_name] = {
                        "status": "pulado",
                        "duration": duration,
                        "message": skipped.get("message", "skipped") or "skipped",
                    }
                else:
                    resultados[full_name] = {
                        "status": "verde",
                        "duration": duration,
                        "message": "",
                    }
        except ET.ParseError:
            continue
        except Exception:
            continue

    return resultados


def gerar_indice_resultados(
    resultados_junit: Dict[str, Dict],
    pares: List[Tuple[str, str]],
) -> Dict:
    """
    Agrega resultados JUnit no formato pares_testados.json.
    """
    arestas: Dict[str, Dict] = {}

    for a, b in pares:
        par_key = f"{a}__{b}"
        test_name = f"test_{a}__{b}"

        # Procura resultado nos JUnit reports (match exato: test_a__b ou test_a__b.test_coexistencia)
        resultado = None
        for full_name, res in resultados_junit.items():
            # full_name = "res://tests_godot/pairs/test_a__b.gd.test_coexistencia" ou similar
            if full_name == test_name or full_name.endswith(f".{test_name}") or test_name in full_name.split("."):
                resultado = res
                break

        if resultado:
            arestas[par_key] = {
                "par": [a, b],
                "status": resultado["status"],
                "duration": resultado["duration"],
                "message": resultado["message"][:200],
            }
        else:
            arestas[par_key] = {
                "par": [a, b],
                "status": "nao_executado",
                "duration": 0,
                "message": "Sem resultado JUnit",
            }

    # Estatísticas
    verde = sum(1 for a in arestas.values() if a["status"] == "verde")
    vermelho = sum(1 for a in arestas.values() if a["status"] == "vermelho")
    pulado = sum(1 for a in arestas.values() if a["status"] == "pulado")
    nao_exec = sum(1 for a in arestas.values() if a["status"] == "nao_executado")

    return {
        "meta": {
            "data": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_pares": len(pares),
            "verde": verde,
            "vermelho": vermelho,
            "pulado": pulado,
            "nao_executado": nao_exec,
            "cobertura": round((verde + vermelho) / max(len(pares), 1) * 100, 1),
        },
        "arestas": arestas,
        "vermelhos_detalhe": [
            {"par": k, **v}
            for k, v in arestas.items()
            if v["status"] == "vermelho"
        ],
    }


def rodar_todos(
    godot_exe: str,
    batch_size: int = 50,
    dry_run: bool = False,
) -> None:
    """Roda todos os testes de pares em lotes."""
    # Carrega lista de pares dos arquivos gerados
    test_files = sorted(glob.glob(os.path.join(TEST_DIR, "test_*.gd")))
    if not test_files:
        print(f"Nenhum teste encontrado em {TEST_DIR}/")
        print("Rode primeiro: python scripts/gerar_testes_pares.py")
        return

    pares: List[Tuple[str, str]] = []
    test_paths: List[str] = []
    for tf in test_files:
        basename = os.path.splitext(os.path.basename(tf))[0]
        # test_a__b → a, b
        inner = basename.replace("test_", "", 1)
        parts = inner.split("__", 1)
        if len(parts) == 2:
            pares.append((parts[0], parts[1]))
            test_paths.append(f"res://{TEST_DIR}/{os.path.basename(tf)}")

    print(f"Godot: {godot_exe}")
    print(f"Testes: {len(test_paths)}")
    print(f"Lote: {batch_size} por execução")
    print()

    if dry_run:
        print("--- DRY RUN ---")
        for p in test_paths[:10]:
            print(f"  {p}")
        print(f"  ... +{len(test_paths) - 10} mais")
        return

    # Roda em lotes
    todos_resultados: Dict[str, Dict] = {}
    total_lotes = (len(test_paths) + batch_size - 1) // batch_size

    for lote_idx in range(total_lotes):
        inicio = lote_idx * batch_size
        fim = min(inicio + batch_size, len(test_paths))
        lote = test_paths[inicio:fim]

        print(f"Lote {lote_idx + 1}/{total_lotes}: {len(lote)} testes...")
        exit_code, stdout, stderr = rodar_godot_headless(godot_exe, lote, timeout=300)

        print(f"  Exit: {exit_code}")

        # Parse JUnit
        resultados = parse_junit_reports()
        todos_resultados.update(resultados)

        verde_lote = sum(1 for r in resultados.values() if r["status"] == "verde")
        vermelho_lote = sum(1 for r in resultados.values() if r["status"] == "vermelho")
        print(f"  Verde: {verde_lote}, Vermelho: {vermelho_lote}")

    # Agrega e salva
    indice = gerar_indice_resultados(todos_resultados, pares)
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(indice, f, indent=2, ensure_ascii=False)

    print()
    print(f"=== RESUMO FINAL ===")
    print(f"Total pares: {indice['meta']['total_pares']}")
    print(f"Verde: {indice['meta']['verde']}")
    print(f"Vermelho: {indice['meta']['vermelho']}")
    print(f"Pulado: {indice['meta']['pulado']}")
    print(f"Não executado: {indice['meta']['nao_executado']}")
    print(f"Cobertura: {indice['meta']['cobertura']}%")
    print(f"Resultado salvo em: {OUTPUT_JSON}")


def rodar_um(godot_exe: str, par: str) -> None:
    """Roda um único par para debug."""
    test_path = f"res://{TEST_DIR}/test_{par}.gd"
    if not os.path.exists(os.path.join(TEST_DIR, f"test_{par}.gd")):
        print(f"Teste não encontrado: {test_path}")
        return

    print(f"Godot: {godot_exe}")
    print(f"Teste: {test_path}")
    exit_code, stdout, stderr = rodar_godot_headless(godot_exe, [test_path], timeout=60)
    print(f"Exit: {exit_code}")
    print()
    print("--- STDOUT ---")
    print(stdout[-3000:] if len(stdout) > 3000 else stdout)
    if stderr:
        print("--- STDERR ---")
        print(stderr[-2000:] if len(stderr) > 2000 else stderr)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="sota_1.7: Rodar testes de pares no GdUnit4")
    parser.add_argument("--godot", type=str, default=None, help="Caminho do Godot.exe")
    parser.add_argument("--batch-size", type=int, default=50, help="Tamanho do lote")
    parser.add_argument("--dry-run", action="store_true", help="Apenas lista, sem rodar")
    parser.add_argument("--par", type=str, default=None, help="Rodar um par específico")
    args = parser.parse_args()

    godot_exe = args.godot or encontrar_godot()
    if not godot_exe:
        print("ERRO: Godot não encontrado.")
        print(f"  Tentado: {DEFAULT_GODOT}")
        print("  Defina GODOT_BIN ou passe --godot <caminho>")
        sys.exit(1)

    if not os.path.exists(godot_exe):
        print(f"ERRO: Godot não existe: {godot_exe}")
        sys.exit(1)

    if args.par:
        rodar_um(godot_exe, args.par)
    else:
        rodar_todos(godot_exe, batch_size=args.batch_size, dry_run=args.dry_run)
