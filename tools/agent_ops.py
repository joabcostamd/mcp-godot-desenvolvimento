"""agent_ops.py — Orquestracao de Agentes (Fatia 4.6 / Etapa B6).

Suporte ao processo autonomo multi-agente:
- File lock entre agentes (evita edicao concorrente)
- Fila de tarefas com dependencia
- Revisao cruzada entre agentes
- Comparacao de outputs de modelos
- Context pack para handoff
- Onboarding brief para agente novo

Usa config_lock do projeto para protecao de escrita concorrente.
"""

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _get_agent_dir() -> Path:
    """Retorna diretorio de estado dos agentes."""
    d = ROOT / ".mcp_agents"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _get_lock_dir() -> Path:
    """Retorna diretorio de locks."""
    d = _get_agent_dir() / "locks"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _get_queue_dir() -> Path:
    """Retorna diretorio de filas de tarefa."""
    d = _get_agent_dir() / "queues"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════════════
# Op 1-2: File Lock entre Agentes
# ══════════════════════════════════════════════════════════════════════

def acquire_file_lock(file_path: str, agent_id: str = "agente-02", ttl_seconds: int = 300) -> dict:
    """Adquire lock exclusivo em um arquivo para evitar edicao concorrente.

    Cria um arquivo .lock com metadata do agente. Se o lock ja existe
    e nao expirou, retorna conflito.

    Args:
        file_path: Caminho do arquivo a travar (relativo ou absoluto).
        agent_id: Identificador do agente (default: agente-02).
        ttl_seconds: Tempo maximo do lock em segundos (default: 300 = 5min).

    Returns:
        dict com status do lock.
    """
    lock_dir = _get_lock_dir()
    # Nome do lock baseado no hash do path
    lock_name = hashlib.md5(file_path.encode()).hexdigest()[:16] + ".lock"
    lock_path = lock_dir / lock_name

    # Verifica se ja existe lock ativo
    if lock_path.exists():
        try:
            existing = json.loads(lock_path.read_text(encoding="utf-8"))
            acquired_at = existing.get("acquired_at", "")
            if acquired_at:
                age = time.time() - datetime.fromisoformat(acquired_at).timestamp()
                if age < ttl_seconds:
                    return {
                        "status": "conflict",
                        "locked_by": existing.get("agent_id", "desconhecido"),
                        "acquired_at": acquired_at,
                        "age_seconds": round(age, 1),
                        "detail": f"Arquivo travado por '{existing.get('agent_id')}' ha {round(age)}s. TTL={ttl_seconds}s.",
                    }
                # Lock expirado — remove
        except Exception:
            pass
        lock_path.unlink(missing_ok=True)

    # Adquire lock
    lock_data = {
        "file": file_path,
        "agent_id": agent_id,
        "acquired_at": _now_iso(),
        "ttl_seconds": ttl_seconds,
    }
    lock_path.write_text(json.dumps(lock_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "acquired",
        "lock_file": str(lock_path),
        "agent_id": agent_id,
        "acquired_at": lock_data["acquired_at"],
        "ttl_seconds": ttl_seconds,
    }


def release_file_lock(file_path: str, agent_id: str = "agente-02") -> dict:
    """Libera um lock de arquivo previamente adquirido.

    Args:
        file_path: Caminho do arquivo travado.
        agent_id: Identificador do agente que adquiriu o lock.

    Returns:
        dict com status da liberacao.
    """
    lock_dir = _get_lock_dir()
    lock_name = hashlib.md5(file_path.encode()).hexdigest()[:16] + ".lock"
    lock_path = lock_dir / lock_name

    if not lock_path.exists():
        return {"status": "not_found", "detail": "Nenhum lock ativo para este arquivo."}

    try:
        existing = json.loads(lock_path.read_text(encoding="utf-8"))
        if existing.get("agent_id") != agent_id:
            return {
                "status": "not_owner",
                "locked_by": existing.get("agent_id"),
                "detail": f"Lock pertence a '{existing.get('agent_id')}', nao a '{agent_id}'.",
            }
    except Exception:
        pass

    lock_path.unlink(missing_ok=True)
    return {"status": "released", "file": file_path, "agent_id": agent_id}


# ══════════════════════════════════════════════════════════════════════
# Op 3-4: Fila de Tarefas com Dependencia
# ══════════════════════════════════════════════════════════════════════

def create_task_queue(queue_name: str, tasks: list[dict] | None = None) -> dict:
    """Cria ou reinicializa uma fila de tarefas com dependencias.

    Args:
        queue_name: Nome da fila (ex: "etapas-b6").
        tasks: Lista de tarefas [{id, title, depends_on: [id, ...], status}].

    Returns:
        dict com status da fila criada.
    """
    queue_dir = _get_queue_dir()
    queue_path = queue_dir / f"{queue_name}.json"

    if tasks is None:
        tasks = []

    queue_data = {
        "queue_name": queue_name,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "tasks": tasks,
        "completed": 0,
        "total": len(tasks),
    }
    queue_path.write_text(json.dumps(queue_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "created",
        "queue_name": queue_name,
        "total_tasks": len(tasks),
    }


def get_next_task(queue_name: str, agent_id: str = "agente-02") -> dict:
    """Retorna a proxima tarefa disponivel na fila (respeitando dependencias).

    Uma tarefa esta disponivel se:
      - status = "pending"
      - Todas as dependencias (depends_on) estao "completed"

    Args:
        queue_name: Nome da fila.
        agent_id: Identificador do agente.

    Returns:
        dict com a proxima tarefa ou status "empty"/"blocked".
    """
    queue_dir = _get_queue_dir()
    queue_path = queue_dir / f"{queue_name}.json"

    if not queue_path.exists():
        return {"status": "not_found", "detail": f"Fila '{queue_name}' nao encontrada."}

    try:
        queue_data = json.loads(queue_path.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "error", "detail": "Erro ao ler fila."}

    tasks = queue_data.get("tasks", [])
    completed_ids = {t["id"] for t in tasks if t.get("status") == "completed"}

    for task in tasks:
        if task.get("status") != "pending":
            continue
        depends = task.get("depends_on", [])
        if not depends or all(d in completed_ids for d in depends):
            # Atribui tarefa
            task["status"] = "in_progress"
            task["assigned_to"] = agent_id
            task["assigned_at"] = _now_iso()
            queue_data["updated_at"] = _now_iso()
            queue_path.write_text(json.dumps(queue_data, ensure_ascii=False, indent=2), encoding="utf-8")

            return {
                "status": "available",
                "task": task,
                "queue_name": queue_name,
            }

    # Verifica se ha tarefas pendentes bloqueadas
    pending = [t for t in tasks if t.get("status") == "pending"]
    in_progress = [t for t in tasks if t.get("status") == "in_progress"]

    if pending:
        return {
            "status": "blocked",
            "pending_count": len(pending),
            "in_progress_count": len(in_progress),
            "detail": f"{len(pending)} tarefas pendentes bloqueadas por dependencias.",
        }
    elif in_progress:
        return {
            "status": "waiting",
            "in_progress_count": len(in_progress),
            "detail": f"{len(in_progress)} tarefas em andamento.",
        }

    return {"status": "empty", "detail": "Nenhuma tarefa pendente."}


# ══════════════════════════════════════════════════════════════════════
# Op 5: request_peer_review
# ══════════════════════════════════════════════════════════════════════

def request_peer_review(
    artifact: str,
    reviewer: str = "agente-01",
    context: str = "",
    criteria: list[str] | None = None,
) -> dict:
    """Solicita revisao cruzada de um artefato por outro agente.

    Args:
        artifact: Descricao do artefato a revisar (ex: "tools/code_quality_ops.py").
        reviewer: Agente revisor (default: agente-01).
        context: Contexto adicional sobre o que revisar.
        criteria: Lista de criterios de revisao (ex: ["syntax", "logic", "security"]).

    Returns:
        dict com a requisicao de revisao.
    """
    if criteria is None:
        criteria = ["syntax", "logic", "edge_cases", "performance"]

    review_dir = _get_agent_dir() / "reviews"
    review_dir.mkdir(parents=True, exist_ok=True)

    review_id = hashlib.md5(f"{artifact}{_now_iso()}".encode()).hexdigest()[:12]
    review_data = {
        "review_id": review_id,
        "artifact": artifact,
        "reviewer": reviewer,
        "requester": "agente-02",
        "context": context,
        "criteria": criteria,
        "status": "requested",
        "requested_at": _now_iso(),
        "completed_at": None,
        "result": None,
    }

    review_path = review_dir / f"{review_id}.json"
    review_path.write_text(json.dumps(review_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "requested",
        "review_id": review_id,
        "reviewer": reviewer,
        "artifact": artifact,
        "criteria": criteria,
        "detail": f"Revisao solicitada a '{reviewer}' para '{artifact}'.",
    }


# ══════════════════════════════════════════════════════════════════════
# Op 6: compare_agent_outputs
# ══════════════════════════════════════════════════════════════════════

def compare_agent_outputs(
    agent_a: str,
    output_a: dict,
    agent_b: str,
    output_b: dict,
    criteria: list[str] | None = None,
) -> dict:
    """Compara outputs de dois agentes/modelos com criterios objetivos.

    Criterios de comparacao:
      - completeness: qual output tem mais campos preenchidos?
      - consistency: os dados sao consistentes entre si?
      - correctness: ha erros evidentes em algum output?
      - detail: qual output tem mais detalhes relevantes?

    Args:
        agent_a: Nome do primeiro agente (ex: "deepseek-v4").
        output_a: Output do primeiro agente (dict).
        agent_b: Nome do segundo agente (ex: "claude-sonnet").
        output_b: Output do segundo agente (dict).
        criteria: Lista de criterios a avaliar.

    Returns:
        dict com comparacao detalhada e vencedor por criterio.
    """
    if criteria is None:
        criteria = ["completeness", "consistency", "correctness", "detail"]

    results = {}

    # Completeness: conta campos com valor nao-nulo/nao-vazio
    def count_filled(d: dict, prefix: str = "") -> int:
        count = 0
        for k, v in d.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                count += count_filled(v, key)
            elif v is not None and v != "" and v != [] and v != {}:
                count += 1
        return count

    filled_a = count_filled(output_a)
    filled_b = count_filled(output_b)

    results["completeness"] = {
        "agent_a": filled_a,
        "agent_b": filled_b,
        "winner": agent_a if filled_a > filled_b else (agent_b if filled_b > filled_a else "empate"),
        "detail": f"{agent_a}={filled_a} campos, {agent_b}={filled_b} campos",
    }

    # Consistency: keys em comum vs total
    keys_a = set(_flatten_keys(output_a))
    keys_b = set(_flatten_keys(output_b))
    common = keys_a & keys_b
    total = keys_a | keys_b
    consistency_score = round(len(common) / max(len(total), 1) * 100, 1)

    results["consistency"] = {
        "common_keys": len(common),
        "total_keys": len(total),
        "score_pct": consistency_score,
        "detail": f"{consistency_score}% de chaves em comum ({len(common)}/{len(total)})",
    }

    # Correctness: verifica campos com "error" ou "exception"
    def count_errors(d: dict) -> int:
        errors = 0
        for v in d.values():
            if isinstance(v, dict):
                errors += count_errors(v)
            elif isinstance(v, str) and ("error" in v.lower() or "exception" in v.lower()):
                errors += 1
        return errors

    errors_a = count_errors(output_a)
    errors_b = count_errors(output_b)

    results["correctness"] = {
        "agent_a_errors": errors_a,
        "agent_b_errors": errors_b,
        "winner": agent_a if errors_a < errors_b else (agent_b if errors_b < errors_a else "empate"),
        "detail": f"{agent_a}={errors_a} erros, {agent_b}={errors_b} erros",
    }

    # Detail: tamanho total do JSON
    detail_a = len(json.dumps(output_a, ensure_ascii=False))
    detail_b = len(json.dumps(output_b, ensure_ascii=False))

    results["detail"] = {
        "agent_a_bytes": detail_a,
        "agent_b_bytes": detail_b,
        "winner": agent_a if detail_a > detail_b else (agent_b if detail_b > detail_a else "empate"),
        "detail": f"{agent_a}={detail_a}B, {agent_b}={detail_b}B",
    }

    # Agregado
    wins_a = sum(1 for r in results.values() if r.get("winner") == agent_a)
    wins_b = sum(1 for r in results.values() if r.get("winner") == agent_b)

    return {
        "status": "completed",
        "agent_a": agent_a,
        "agent_b": agent_b,
        "wins_a": wins_a,
        "wins_b": wins_b,
        "overall_winner": agent_a if wins_a > wins_b else (agent_b if wins_b > wins_a else "empate"),
        "criteria": results,
    }


def _flatten_keys(d: dict, prefix: str = "") -> set:
    """Achata chaves de dict aninhado para comparacao."""
    keys = set()
    for k, v in d.items():
        full = f"{prefix}.{k}" if prefix else k
        keys.add(full)
        if isinstance(v, dict):
            keys |= _flatten_keys(v, full)
    return keys


# ══════════════════════════════════════════════════════════════════════
# Op 7: generate_agent_context_pack
# ══════════════════════════════════════════════════════════════════════

def generate_agent_context_pack(
    session_summary: str = "",
    include_roadmap: bool = True,
    include_handoff: bool = True,
    include_suture: bool = True,
) -> dict:
    """Gera um context pack para handoff entre agentes ou sessoes.

    Agrega ROADMAP, HANDOFF, SUTURE_ISSUES e resumo da sessao atual
    em um unico pacote estruturado para o proximo agente.

    Args:
        session_summary: Resumo da sessao atual (fornecido pelo agente).
        include_roadmap: Incluir ROADMAP_UNIFICADO.md.
        include_handoff: Incluir HANDOFF.md.
        include_suture: Incluir SUTURE_ISSUES.md.

    Returns:
        dict com context pack completo.
    """
    pack = {
        "generated_at": _now_iso(),
        "generated_by": "agente-02",
        "session_summary": session_summary,
        "files": {},
    }

    file_map = {
        "roadmap": (ROOT / "ROADMAP_UNIFICADO.md", include_roadmap),
        "handoff": (ROOT / "HANDOFF.md", include_handoff),
        "suture_issues": (ROOT / "SUTURE_ISSUES.md", include_suture),
    }

    for key, (path, include) in file_map.items():
        if include and path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                # Inclui apenas as secoes mais relevantes (primeiras 200 linhas)
                lines = content.splitlines()[:200]
                pack["files"][key] = {
                    "path": str(path.relative_to(ROOT)),
                    "lines": len(lines),
                    "preview": "\n".join(lines),
                }
            except Exception:
                pack["files"][key] = {"error": f"Nao foi possivel ler {path.name}"}

    # Adiciona progresso
    progress_path = ROOT / ".roadmap_progress.json"
    if progress_path.exists():
        try:
            progress = json.loads(progress_path.read_text(encoding="utf-8"))
            pack["progress"] = {
                "total_fatias": len(progress),
                "concluidas": sum(1 for v in progress.values() if isinstance(v, dict) and v.get("status") in ("concluida", "implementada_pendente_revisao")),
            }
        except Exception:
            pass

    # Salva o pack
    pack_dir = _get_agent_dir() / "context_packs"
    pack_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pack_path = pack_dir / f"context_pack_{timestamp}.json"
    pack_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")

    pack["pack_file"] = str(pack_path.relative_to(ROOT))
    return pack


# ══════════════════════════════════════════════════════════════════════
# Op 8: generate_agent_onboarding_brief
# ══════════════════════════════════════════════════════════════════════

def generate_agent_onboarding_brief(
    new_agent_name: str = "novo-agente",
    role: str = "extensoes-qualidade",
) -> dict:
    """Gera um briefing de onboarding para um novo agente.

    Extrai informacoes do ROADMAP, HANDOFF e documentos de spec
    para criar um resumo do que o novo agente precisa saber.

    Args:
        new_agent_name: Nome do novo agente.
        role: Papel do agente ("extensoes-qualidade" ou "arquitetura-core").

    Returns:
        dict com briefing estruturado.
    """
    brief = {
        "agent_name": new_agent_name,
        "role": role,
        "generated_at": _now_iso(),
        "project": "MCP Godot Agent",
        "goal": "Desenvolvimento autonomo multi-agente de um MCP para Godot Engine",
    }

    # Le ROADMAP para extrair etapas pendentes
    roadmap_path = ROOT / "ROADMAP_UNIFICADO.md"
    if roadmap_path.exists():
        try:
            content = roadmap_path.read_text(encoding="utf-8")
            # Extrai etapas com status ⬜
            pending = re.findall(r'⬜\s+(\w[\w\s()-]+)', content)
            brief["pending_etapas"] = pending[:10]
            brief["total_pending"] = len(pending)
        except Exception:
            brief["pending_etapas"] = ["(erro ao ler roadmap)"]

    # Le HANDOFF para ultimo contexto
    handoff_path = ROOT / "HANDOFF.md"
    if handoff_path.exists():
        try:
            content = handoff_path.read_text(encoding="utf-8")
            # Extrai data e agente do ultimo handoff
            m = re.search(r'Data:\*\*\s*(.+)|Data:\s*(.+)', content)
            if m:
                brief["last_handoff_date"] = (m.group(1) or m.group(2)).strip()
        except Exception:
            pass

    # Arquivos exclusivos por role
    if "arquitetura" in role:
        brief["exclusive_files"] = ["server.py", "core/*", "tools/deprecated.py", "tools/registry_validation.py", "tools/rollups.py"]
        brief["next_etapa"] = "A3 — DATA_CONTRACTS.md"
    else:
        brief["exclusive_files"] = ["tools/*_ops.py", ".github/*", "docs/*", "tests/*", ".clinerules/*"]
        brief["next_etapa"] = "B6 — agent_manage (concluida); proximo: B7 ou B9"

    brief["key_rules"] = [
        "NUNCA edite arquivos do outro agente (ver exclusive_files)",
        "Respeite # INTERNAL: funcoes marcadas sao usadas por rollups",
        "1 commit por etapa. NUNCA acumular +2 etapas sem commit",
        "Audite apos cada implementacao (auditar.py ou validate_tool_registry_consistency)",
        "Registre conflitos em SUTURE_ISSUES.md, nao resolva sozinho",
    ]

    brief["environment"] = {
        "godot": r"C:\Godot\Godot_v4.7-stable_win64.exe",
        "test_project": r"C:\Users\joabc\OneDrive\Documentos\VSCODE\NUCLEO\projetos\breakout_test",
        "venv": ".venv na raiz do projeto",
    }

    return brief
