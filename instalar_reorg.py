"""instalar_reorg.py - Posiciona o plano de reorganizacao no repositorio.

O QUE ESTE SCRIPT FAZ:
    1. Confirma que esta rodando na raiz certa.
    2. Faz backup datado do .roadmap_progress.json.
    3. Move REORG_ROADMAP.md para docs/ e ONDA_R_reconciliacao.md para .github/roadmap/.
    4. Registra as fatias R1..R8 no .roadmap_progress.json com status "nao verificado".
    5. Roda uma verificacao SOMENTE LEITURA e imprime o estado real.

O QUE ESTE SCRIPT NAO FAZ (de proposito):
    - Nao instala o git hook. Isso e a Fatia R1, que precisa de prova e revisao.
    - Nao mexe no settings.json. Isso e a Fatia R4.
    - Nao move os prompts locais. Isso e a Fatia R4.
    - Nao consolida os arquivos de estado. Isso e a Fatia R2.
    - Nao altera server.py, auditar.py ou qualquer codigo.
    - Nao commita nada.

Cada uma dessas coisas e uma fatia com criterio de aceite e prova. Se o instalador
as fizesse, elas nasceriam "concluidas" sem evidencia - que e exatamente o padrao
de falha que este plano existe para fechar.

E idempotente: rodar duas vezes nao duplica nada.

Uso:
    python instalar_reorg.py
    python instalar_reorg.py --dry-run     (so mostra o que faria)
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
PROGRESS = ROOT / ".roadmap_progress.json"
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

ACOES = []
AVISOS = []
ERROS = []


def log(icone, texto):
    print(f"  {icone} {texto}")


# ---------------------------------------------------------------- 1. LOCAL

def verificar_raiz() -> bool:
    print("\n[1/5] Confirmando a raiz do repositorio")
    obrigatorios = ["server.py", "auditar.py", "AGENTS.md", ".git"]
    faltando = [f for f in obrigatorios if not (ROOT / f).exists()]
    if faltando:
        ERROS.append(f"Nao parece ser a raiz do mcp-godot-desenvolvimento. Faltando: {faltando}")
        log("[X]", f"Faltando: {faltando}")
        return False
    log("[OK]", f"Raiz confirmada: {ROOT}")

    try:
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=15,
                           stdin=subprocess.DEVNULL)
        branch = r.stdout.strip()
        log("[OK]", f"Branch: {branch}")
        if branch not in ("main", "master"):
            AVISOS.append(f"Branch atual e '{branch}', nao main. A ONDA R e [EIXO-CENTRAL].")
    except Exception as e:
        AVISOS.append(f"Nao consegui ler a branch: {e}")
    return True


# ---------------------------------------------------------------- 2. BACKUP

def backup(dry: bool):
    print("\n[2/5] Backup do estado")
    if not PROGRESS.exists():
        AVISOS.append(".roadmap_progress.json nao existe - sera criado do zero.")
        log("[!]", ".roadmap_progress.json ausente")
        return
    destino = ROOT / f".roadmap_progress.json.backup-{STAMP}"
    if dry:
        log("[~]", f"criaria {destino.name}")
        return
    shutil.copy2(PROGRESS, destino)
    ACOES.append(f"backup criado: {destino.name}")
    log("[OK]", f"{destino.name} ({destino.stat().st_size} bytes)")


# ---------------------------------------------------------------- 3. ARQUIVOS

MOVIMENTOS = [
    ("REORG_ROADMAP.md", "docs/REORG_ROADMAP.md"),
    ("ONDA_R_reconciliacao.md", ".github/roadmap/ONDA_R_reconciliacao.md"),
]


def posicionar(dry: bool):
    print("\n[3/5] Posicionando os documentos")
    for origem_nome, destino_rel in MOVIMENTOS:
        origem = ROOT / origem_nome
        destino = ROOT / destino_rel

        if destino.exists() and not origem.exists():
            log("[=]", f"{destino_rel} ja esta no lugar")
            continue
        if not origem.exists():
            ERROS.append(f"Nao encontrei {origem_nome} na raiz. Voce colou o arquivo?")
            log("[X]", f"{origem_nome} nao esta na raiz")
            continue
        if dry:
            log("[~]", f"moveria {origem_nome} -> {destino_rel}")
            continue

        destino.parent.mkdir(parents=True, exist_ok=True)
        if destino.exists():
            antigo = destino.with_suffix(destino.suffix + f".anterior-{STAMP}")
            shutil.move(str(destino), str(antigo))
            AVISOS.append(f"{destino_rel} existia; versao anterior salva como {antigo.name}")
        shutil.move(str(origem), str(destino))
        ACOES.append(f"{origem_nome} -> {destino_rel}")
        log("[OK]", f"{origem_nome} -> {destino_rel}")


# ---------------------------------------------------------------- 4. REGISTRO

FATIAS = {
    "reorg_R1_gate_git":        "R1 - Gate git real em .githooks (a unica trava que dispara neste ambiente)",
    "reorg_R2_estado_unico":    "R2 - Estado unico: os outros 2 JSON viram arquivo morto",
    "reorg_R3_auditor":         "R3 - auditar.py: C1 tolerancia 0 (DR-6) e --skip-c5 -> baseline (DR-5)",
    "reorg_R4_caminhos":        "R4 - Caminho do roadmap, prompts locais e contradicao /seguir-roadmap x /act",
    "reorg_R5_reauditoria":     "R5 - Reauditar as fatias F1..F5 marcadas concluida contra o criterio real",
    "reorg_R6_branch_agente2":  "R6 - Branch agente2/behaviors-onda2: tag de arquivo morto, sem merge (DR-2)",
    "reorg_R7_medicao":         "R7 - Medicao real por fase via _get_phase_tools()",
    "reorg_R8_fichas":          "R8 - Gerar as fichas das ondas seguintes com os numeros da R7",
}


def registrar(dry: bool):
    print("\n[4/5] Registrando as fatias da ONDA R")
    if PROGRESS.exists():
        try:
            dados = json.loads(PROGRESS.read_text(encoding="utf-8"))
        except Exception as e:
            ERROS.append(f"Nao consegui ler .roadmap_progress.json: {e}")
            log("[X]", f"leitura falhou: {e}")
            return
    else:
        dados = {}

    novas = 0
    for chave, descricao in FATIAS.items():
        if chave in dados:
            log("[=]", f"{chave} ja registrada (status: {dados[chave].get('status','?')})")
            continue
        dados[chave] = {
            "status": "nao verificado",
            "data": datetime.now().strftime("%Y-%m-%d"),
            "agente": "AGENTE 01",
            "checkpoint": None,
            "resultado": descricao,
            "ficha": ".github/roadmap/ONDA_R_reconciliacao.md",
            "marcacao": "[EIXO-CENTRAL]",
        }
        novas += 1
        log("[+]", f"{chave} -> nao verificado")

    if novas == 0:
        log("[=]", "nada novo a registrar")
        return
    if dry:
        log("[~]", f"gravaria {novas} entradas novas")
        return

    PROGRESS.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    ACOES.append(f"{novas} fatias registradas como 'nao verificado'")
    log("[OK]", f"{novas} entradas gravadas")


# ---------------------------------------------------------------- 5. ESTADO REAL

def verificar_estado():
    """Somente leitura. Da a IA o chao de fatos antes da primeira fatia."""
    print("\n[5/5] Estado real do repositorio (somente leitura)")

    print("\n  -- Arquivos de progresso (a R2 resolve) --")
    for p in sorted(ROOT.glob("*progress*.json")):
        log("[i]", f"{p.name}  ({p.stat().st_size} bytes)")

    print("\n  -- Prompts locais (a R4 resolve) --")
    pasta = ROOT / ".github" / "prompts"
    achados = sorted(pasta.glob("*.prompt.md")) if pasta.exists() else []
    if achados:
        for p in achados:
            log("[!]", f"{p.name} - proibicao 9.3.1 da constituicao")
    else:
        log("[OK]", "nenhum prompt local")

    print("\n  -- Gate git (a R1 resolve) --")
    try:
        r = subprocess.run(["git", "config", "core.hooksPath"],
                           capture_output=True, text=True, timeout=15,
                           stdin=subprocess.DEVNULL)
        valor = r.stdout.strip()
        log("[OK]" if valor else "[!]", f"core.hooksPath = {valor or 'NAO CONFIGURADO'}")
    except Exception as e:
        log("[X]", f"git config falhou: {e}")
    log("[i]", f".githooks/ existe: {(ROOT / '.githooks').exists()}")

    print("\n  -- Simbolos que a ONDA 1 e a ONDA 2 removem --")
    alvo = ROOT / "server.py"
    if alvo.exists():
        texto = alvo.read_text(encoding="utf-8", errors="replace")
        for simbolo in ("TOOLSETS", "PHASE_TOOLSETS", "TOOL_PROFILES",
                        "PHASE_TOOLS_CORE", "_apply_hints", "_HINT_RULES",
                        "_READONLY", "_TITLES", "_TAGS"):
            n = texto.count(simbolo)
            log("[i]" if n else "[OK]", f"{simbolo}: {n} ocorrencias em server.py")

    print("\n  -- Vazamentos do auditor (a R3 resolve) --")
    aud = ROOT / "auditar.py"
    if aud.exists():
        t = aud.read_text(encoding="utf-8", errors="replace")
        log("[!]" if "skip_c5" in t else "[OK]", f"--skip-c5 presente: {'skip_c5' in t}")
        log("[!]" if "<= 5" in t else "[OK]", f"tolerancia C1 de 5 presente: {'<= 5' in t}")

    print("\n  -- Branch do Agente 2 (a R6 resolve) --")
    try:
        r = subprocess.run(
            ["git", "diff", "--shortstat", "main..agente2/behaviors-onda2"],
            capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        log("[i]", f"main..agente2/behaviors-onda2: {r.stdout.strip() or r.stderr.strip()}")
    except Exception as e:
        log("[!]", f"nao consegui comparar: {e}")


# ---------------------------------------------------------------- MAIN

def main():
    dry = "--dry-run" in sys.argv

    print("=" * 70)
    print("  INSTALADOR DO PLANO DE REORGANIZACAO - MCP Godot")
    print("  Modo:", "SIMULACAO (--dry-run)" if dry else "APLICAR")
    print("=" * 70)

    if not verificar_raiz():
        print("\n[FALHA] Rode este script na raiz do mcp-godot-desenvolvimento.")
        sys.exit(1)

    backup(dry)
    posicionar(dry)
    registrar(dry)
    verificar_estado()

    print("\n" + "=" * 70)
    print("  RELATORIO")
    print("=" * 70)
    print(f"\n  Acoes aplicadas: {len(ACOES)}")
    for a in ACOES:
        print(f"    [OK] {a}")
    print(f"\n  Avisos: {len(AVISOS)}")
    for a in AVISOS:
        print(f"    [!] {a}")
    print(f"\n  Erros: {len(ERROS)}")
    for e in ERROS:
        print(f"    [X] {e}")

    if ERROS:
        print("\n[FALHA] Corrija os erros acima. Nada foi commitado.")
        sys.exit(1)

    print("\n  NAO FOI FEITO (de proposito - cada item e uma fatia com prova):")
    print("    - gate git .............. Fatia R1")
    print("    - estado unico .......... Fatia R2")
    print("    - conserto do auditor ... Fatia R3")
    print("    - settings.json ......... Fatia R4")
    print("    - prompts locais ........ Fatia R4")
    print("\n  PROXIMO PASSO: rode /plan. A primeira fatia elegivel e a R1.")
    print("  Nenhum commit foi feito por este script.\n")


if __name__ == "__main__":
    main()
