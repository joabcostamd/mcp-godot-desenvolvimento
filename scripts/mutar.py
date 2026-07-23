"""
scripts/mutar.py — sota_1.8: Mutation testing da suíte de behaviors (amostra).

Aplica 3 tipos de mutação no .gd de uma amostra de behaviors, roda os testes,
e registra se a mutação foi detectada (mutante morto) ou não (mutante vivo).

SEGURANÇA: Antes de modificar qualquer .gd, faz backup em arquivo temporário.
Em caso de crash, o backup pode ser restaurado manualmente.

Fonte: SOTA_01_FUNDACAO_CEREBRO.md, seção sota_1.8.

Uso:
    python scripts/mutar.py                    # amostra de 20 behaviors
    python scripts/mutar.py --behavior health  # behavior específico
    python scripts/mutar.py --all              # todos com teste próprio
"""

import os
import sys
import glob
import re
from random import sample
from typing import List, Dict

# Importa utilitários compartilhados de Godot (evita duplicação com rodar_testes_pares.py)
from _godot_utils import encontrar_godot, rodar_godot_headless, DEFAULT_GODOT

BACKUP_SUFFIX = ".mutar_backup"


# ═══════════════════════════════════════════════════════════════
# Estratégias de mutação
# ═══════════════════════════════════════════════════════════════

def mutacao_1_comparador(code: str) -> str:
    """Troca > por >= em condicionais."""
    # Troca > que NÃO são >= (evita dupla mutação)
    return re.sub(r'(?<!>)>(?!=)', '>=', code)


def mutacao_2_booleano(code: str) -> str:
    """Inverte o primeiro booleano default encontrado (true ↔ false)."""
    # Inverte @export var foo: bool = true/false
    def inverter(m):
        valor = m.group(1)
        novo = "false" if valor.lower() == "true" else "true"
        return m.group(0).replace(valor, novo)
    return re.sub(r'(@export\s+var\s+\w+\s*:\s*bool\s*=\s*)(true|false)', inverter, code, count=1, flags=re.IGNORECASE)


def mutacao_3_sinal(code: str) -> str:
    """Comenta a primeira linha de emissão de sinal (.emit)."""
    lines = code.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if ".emit(" in stripped and not stripped.startswith("#") and not stripped.startswith("signal "):
            # Preserva indentação
            indent = line[:len(line) - len(line.lstrip())]
            lines[i] = indent + "# [MUTADO] " + line.lstrip()
            break
    return "\n".join(lines)


MUTACOES = [
    ("troca_>_por_>=", mutacao_1_comparador),
    ("inverte_booleano_default", mutacao_2_booleano),
    ("comenta_emit", mutacao_3_sinal),
]


# ═══════════════════════════════════════════════════════════════
# Core
# ═══════════════════════════════════════════════════════════════

def behaviors_com_teste() -> List[str]:
    """Lista behaviors que têm test_*.gd próprio."""
    behaviors = []
    for d in sorted(glob.glob("behaviors/*/")):
        # d = "behaviors/health/" — extrai só o nome
        name = os.path.basename(d.rstrip("/\\"))
        if name.startswith("_"):
            continue
        test_file = os.path.join(d, f"test_{name}.gd")
        if os.path.exists(test_file):
            behaviors.append(name)
    return behaviors


def rodar_teste_behavior(
    godot_exe: str,
    behavior: str,
    timeout: int = 60,
):
    """Roda o teste de um behavior específico via GdUnit4 CLI."""
    test_path = f"res://behaviors/{behavior}/test_{behavior}.gd"
    return rodar_godot_headless(godot_exe, [test_path], timeout=timeout)


def testar_mutante(
    godot_exe: str,
    behavior: str,
    gd_path: str,
    mutacao_nome: str,
    mutacao_fn,
) -> Dict:
    """
    Aplica mutação, roda teste, restaura original.

    SEGURANÇA: Faz backup em <arquivo>.mutar_backup ANTES de modificar.
    Se o processo for interrompido entre escrita e restauração,
    o backup pode ser restaurado manualmente.

    Retorna dicionário com resultado.
    """
    backup_path = gd_path + BACKUP_SUFFIX

    # Detecta line endings originais para preservar
    with open(gd_path, "rb") as f:
        raw = f.read(4096)
    has_crlf = b"\r\n" in raw
    newline_mode = "\r\n" if has_crlf else "\n"

    # Lê original
    with open(gd_path, "r", encoding="utf-8") as f:
        original = f.read()

    # Aplica mutação
    mutado = mutacao_fn(original)
    if mutado == original:
        return {
            "behavior": behavior,
            "mutacao": mutacao_nome,
            "status": "nao_aplicavel",
            "motivo": "Mutação não alterou o código",
        }

    try:
        # BACKUP DE SEGURANÇA antes de modificar (crítico)
        with open(backup_path, "w", encoding="utf-8", newline="") as f:
            f.write(original)

        # Escreve mutante
        with open(gd_path, "w", encoding="utf-8", newline="") as f:
            f.write(mutado)

        # Roda teste
        exit_code, stdout, stderr = rodar_teste_behavior(godot_exe, behavior)

        # Detectado = teste falhou (mutante morto) ✓
        # Não detectado = teste passou (mutante vivo) ✗
        morto = exit_code != 0

        return {
            "behavior": behavior,
            "mutacao": mutacao_nome,
            "status": "morto" if morto else "vivo",
            "exit_code": exit_code,
        }
    finally:
        # RESTAURA ORIGINAL
        with open(gd_path, "w", encoding="utf-8", newline="") as f:
            f.write(original)
        # Remove backup (restauração bem-sucedida)
        try:
            os.remove(backup_path)
        except OSError:
            pass



def mutar_amostra(
    godot_exe: str,
    behaviors: List[str],
    sample_size: int = 20,
) -> None:
    """Roda mutation testing em uma amostra de behaviors."""
    if len(behaviors) > sample_size:
        amostra = sample(behaviors, sample_size)
    else:
        amostra = behaviors

    print(f"Godot: {godot_exe}")
    print(f"Amostra: {len(amostra)} behaviors")
    print(f"Mutações por behavior: {len(MUTACOES)}")
    print(f"Total de mutantes: {len(amostra) * len(MUTACOES)}")
    print()

    resultados: List[Dict] = []
    for i, behavior in enumerate(sorted(amostra)):
        gd_path = os.path.join("behaviors", behavior, f"{behavior}.gd")
        if not os.path.exists(gd_path):
            print(f"  [{i+1}/{len(amostra)}] {behavior}: SKIP (sem .gd)")
            continue

        print(f"  [{i+1}/{len(amostra)}] {behavior}:", end=" ", flush=True)
        statuses = []
        for mut_nome, mut_fn in MUTACOES:
            r = testar_mutante(godot_exe, behavior, gd_path, mut_nome, mut_fn)
            resultados.append(r)
            simbolo = {"morto": "✓", "vivo": "✗", "nao_aplicavel": "-"}.get(r["status"], "?")
            statuses.append(simbolo)
        print(" ".join(statuses))

    # Relatório
    mortos = sum(1 for r in resultados if r["status"] == "morto")
    vivos = sum(1 for r in resultados if r["status"] == "vivo")
    na = sum(1 for r in resultados if r["status"] == "nao_aplicavel")
    total = len(resultados)

    print()
    print("=== RELATÓRIO DE MUTAÇÃO ===")
    print(f"Total mutantes: {total}")
    print(f"Mortos (detectados): {mortos} ({round(mortos/max(total,1)*100,1)}%)")
    print(f"Vivos (NÃO detectados): {vivos} ({round(vivos/max(total,1)*100,1)}%)")
    print(f"Não aplicáveis: {na}")

    # Por behavior
    print()
    print("--- Score por behavior ---")
    scores: Dict[str, Dict] = {}
    for r in resultados:
        b = r["behavior"]
        if b not in scores:
            scores[b] = {"mortos": 0, "vivos": 0, "na": 0}
        if r["status"] == "morto":
            scores[b]["mortos"] += 1
        elif r["status"] == "vivo":
            scores[b]["vivos"] += 1
        else:
            scores[b]["na"] += 1

    for b, s in sorted(scores.items()):
        total_b = s["mortos"] + s["vivos"]
        pct = round(s["mortos"] / max(total_b, 1) * 100, 1) if total_b > 0 else 0
        bar = "█" * (s["mortos"]) + "░" * (s["vivos"])
        flag = "⚠️ " if pct < 50 else "  "
        print(f"  {flag}{b}: [{bar}] {pct}% ({s['mortos']}/{total_b})")

    # Lista de reforço
    print()
    print("--- Behaviors com <50% de mutantes mortos (reforço de teste) ---")
    for b, s in sorted(scores.items()):
        total_b = s["mortos"] + s["vivos"]
        pct = round(s["mortos"] / max(total_b, 1) * 100, 1) if total_b > 0 else 0
        if pct < 50 and total_b > 0:
            print(f"  - {b}: {pct}% ({s['mortos']}/{total_b})")

    # Salva JSON
    out = {
        "meta": {
            "amostra": len(amostra),
            "mutacoes_por_behavior": len(MUTACOES),
            "total_mutantes": total,
            "mortos": mortos,
            "vivos": vivos,
            "taxa_deteccao": round(mortos / max(total, 1) * 100, 1),
        },
        "resultados": resultados,
        "reforco_teste": [
            b for b, s in sorted(scores.items())
            if (s["mortos"] + s["vivos"]) > 0
            and round(s["mortos"] / max(s["mortos"] + s["vivos"], 1) * 100, 1) < 50
        ],
    }
    out_path = "behaviors/_index/mutation_report.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nRelatório salvo em: {out_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="sota_1.8: Mutation testing de behaviors")
    parser.add_argument("--godot", type=str, default=None, help="Caminho do Godot.exe")
    parser.add_argument("--behavior", type=str, default=None, help="Behavior específico")
    parser.add_argument("--all", action="store_true", help="Todos os behaviors com teste")
    parser.add_argument("--sample", type=int, default=20, help="Tamanho da amostra")
    args = parser.parse_args()

    godot_exe = args.godot or encontrar_godot()
    if not godot_exe:
        print("ERRO: Godot não encontrado.")
        sys.exit(1)
    if not os.path.exists(godot_exe):
        print(f"ERRO: Godot não existe: {godot_exe}")
        sys.exit(1)

    if args.behavior:
        gd_path = os.path.join("behaviors", args.behavior, f"{args.behavior}.gd")
        if not os.path.exists(gd_path):
            print(f"ERRO: {gd_path} não encontrado")
            sys.exit(1)
        print(f"Testando mutações em: {args.behavior}")
        for mut_nome, mut_fn in MUTACOES:
            r = testar_mutante(godot_exe, args.behavior, gd_path, mut_nome, mut_fn)
            print(f"  {mut_nome}: {r['status']}")
        # Restauração já feita por testar_mutante
    else:
        behaviors = behaviors_com_teste()
        if not behaviors:
            print("Nenhum behavior com teste próprio encontrado.")
            sys.exit(1)
        mutar_amostra(godot_exe, behaviors, sample_size=args.sample)
