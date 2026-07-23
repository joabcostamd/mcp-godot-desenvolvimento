"""
Gate de pre-commit — ONDA R, Fatia R1.
Chamado por .githooks/pre-commit durante git commit.
Verifica G1, G2, G3. Fail-closed: erro = bloqueio.
Escape hatch: git commit --no-verify.

G1 — Entrada nova "concluida" precisa de checkpoint com hash real.
G2 — Se roadmap/HANDOFF está staged, .roadmap_progress.json também precisa.
G3 — Tools por fase não pode exceder baseline; igual passa, menor atualiza.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _resolve_root(repo_root: Path | None = None) -> Path:
    """Resolve a raiz do repositório. Usa o parâmetro se fornecido (testes),
    senão usa o CWD (hook roda no raiz do repo)."""
    if repo_root is not None:
        return Path(repo_root)
    return Path.cwd()


def _progress_file(repo_root: Path | None = None) -> Path:
    return _resolve_root(repo_root) / ".roadmap_progress.json"


def _baseline_file(repo_root: Path | None = None) -> Path:
    return _resolve_root(repo_root) / ".reorg_baseline.json"


PROGRESS_FILE = _progress_file()
BASELINE_FILE = _baseline_file()

# Arquivos cuja alteração exige que .roadmap_progress.json também seja staged
PAR_OBRIGATORIO = [
    "docs/REORG_ROADMAP.md",
    ".github/roadmap/ONDA_R_reconciliacao.md",
    "AGENTS.md",
    "HANDOFF.md",
    ".github/copilot-instructions.md",
]


def run_git(*args: str, repo_root: Path | None = None) -> str:
    """Roda git e devolve stdout.strip(), ou levanta subprocess.CalledProcessError."""
    root = _resolve_root(repo_root)
    result = subprocess.run(
        ["git"] + list(args),
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, "git " + " ".join(args),
                                            output=result.stdout, stderr=result.stderr)
    return result.stdout.strip()


def get_staged_files(repo_root: Path | None = None) -> set[str]:
    """Devolve conjunto de caminhos staged (relativos à raiz)."""
    out = run_git("diff", "--cached", "--name-only", repo_root=repo_root)
    if not out:
        return set()
    return set(out.splitlines())


def load_json(path: Path):
    """Carrega JSON, devolve {} se não existir."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    """Salva JSON com encoding UTF-8 sem BOM."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def is_real_hash(value) -> bool:
    """Hash git real tem 40 caracteres hexadecimais."""
    if not isinstance(value, str):
        return False
    if len(value) != 40:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def check_g1(baseline_progress: dict, repo_root: Path | None = None) -> list[str]:
    """
    G1 — Entrada nova com "status": "concluida" precisa de checkpoint com hash real.
    Compara o staged .roadmap_progress.json com o estado atual committed (HEAD).
    """
    errors = []
    root = _resolve_root(repo_root)
    progress_file = _progress_file(repo_root)

    # Pega o .roadmap_progress.json do HEAD (antes do stage)
    try:
        head_raw = run_git("show", f"HEAD:{progress_file.name}", repo_root=repo_root)
        head_progress = json.loads(head_raw) if head_raw.strip() else {}
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        # Arquivo novo ou primeiro commit — sem HEAD para comparar
        head_progress = {}

    staged = baseline_progress

    for key, entry in staged.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("status") != "concluida":
            continue

        checkpoint = entry.get("checkpoint")

        # Entrada nova (não existia no HEAD) marcada concluida sem hash real
        if key not in head_progress:
            if not is_real_hash(checkpoint):
                errors.append(
                    f"G1 BLOQUEADO: entrada nova '{key}' marcada 'concluida' "
                    f"sem checkpoint de hash real (valor: {checkpoint!r}). "
                    f"Use git commit --no-verify se for consciente."
                )
        else:
            # Entrada existente cujo status mudou para concluida
            old_status = head_progress[key].get("status") if isinstance(head_progress[key], dict) else None
            if old_status != "concluida":
                if not is_real_hash(checkpoint):
                    errors.append(
                        f"G1 BLOQUEADO: entrada '{key}' promovida a 'concluida' "
                        f"sem checkpoint de hash real (valor: {checkpoint!r}). "
                        f"Use git commit --no-verify se for consciente."
                    )

    return errors


def check_g2(staged_files: set[str], repo_root: Path | None = None) -> list[str]:
    """
    G2 — Se arquivo de roadmap ou HANDOFF está staged,
    .roadmap_progress.json também precisa estar staged.
    """
    errors = []
    root = _resolve_root(repo_root)
    progress_file = _progress_file(repo_root)

    progress_staged = str(progress_file.name) in staged_files or str(progress_file.relative_to(root)) in staged_files

    for fname in PAR_OBRIGATORIO:
        if fname in staged_files and not progress_staged:
            errors.append(
                f"G2 BLOQUEADO: '{fname}' está staged mas "
                f"'.roadmap_progress.json' não está. "
                f"Alteração de roadmap/HANDOFF exige atualização do progresso. "
                f"Use git commit --no-verify se for consciente."
            )
            break  # Um erro já basta para bloquear

    return errors


def check_g3(repo_root: Path | None = None) -> list[str]:
    """
    G3 — Contagem de tools por fase não pode ser maior que .reorg_baseline.json.
    Igual passa. Menor passa e atualiza o baseline.
    Falha de medição bloqueia (fail-closed).
    """
    errors = []
    root = _resolve_root(repo_root)
    baseline_file = _baseline_file(repo_root)

    # Medir tools por fase
    try:
        sys.path.insert(0, str(root))
        import server

        baseline = load_json(baseline_file)

        for phase in server.PHASE_TOOLSETS:
            tools = set(server.PHASE_TOOLSETS[phase]) | set(getattr(server, "PHASE_TOOLS_CORE", []))
            count = len(tools)

            phase_key = f"PHASE_TOOLSETS:{phase}"
            prev = baseline.get("tools_por_fase", {}).get(phase_key)

            if prev is not None and count > prev:
                errors.append(
                    f"G3 BLOQUEADO: fase {phase} subiu de {prev} para {count} tools. "
                    f"Redução de teto exige justificativa. "
                    f"Use git commit --no-verify se for consciente."
                )
        # Se passou sem erro, atualiza o baseline com os números atuais
        new_baseline = baseline.copy()
        new_baseline["tools_por_fase"] = {}
        for phase in server.PHASE_TOOLSETS:
            tools = set(server.PHASE_TOOLSETS[phase]) | set(getattr(server, "PHASE_TOOLS_CORE", []))
            new_baseline["tools_por_fase"][f"PHASE_TOOLSETS:{phase}"] = len(tools)
        new_baseline["_ultima_atualizacao"] = _safe_git_rev_parse(repo_root)
        new_baseline["_total_tools"] = len(server._tool_defs())
        save_json(baseline_file, new_baseline)

    except Exception as e:
        # Fail-closed: erro de medição bloqueia
        errors.append(
            f"G3 BLOQUEADO (fail-closed): erro ao medir tools — {e}. "
            f"Use git commit --no-verify se for consciente."
        )

    return errors


def _safe_git_rev_parse(repo_root: Path | None = None) -> str:
    """Tenta git rev-parse HEAD, devolve placeholder se falhar."""
    try:
        return run_git("rev-parse", "HEAD", repo_root=repo_root)
    except Exception:
        return "0000000000000000000000000000000000000000"


def main(repo_root: Path | None = None) -> int:
    """Ponto de entrada. Devolve 0 (passa) ou 1 (bloqueia)."""
    errors = []
    root = _resolve_root(repo_root)

    staged_files = get_staged_files(repo_root=repo_root)

    # G1
    errors.extend(check_g1(load_json(_progress_file(repo_root)), repo_root=repo_root))

    # G2
    errors.extend(check_g2(staged_files, repo_root=repo_root))

    # G3
    errors.extend(check_g3(repo_root=repo_root))

    if errors:
        print("=" * 60)
        print("  GATE DE PRE-COMMIT — BLOQUEADO")
        print("=" * 60)
        for err in errors:
            print(err)
        print("=" * 60)
        print("  Use: git commit --no-verify  (escape hatch consciente)")
        print("=" * 60)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
