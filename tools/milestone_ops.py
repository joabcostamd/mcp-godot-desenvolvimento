"""milestone_ops.py — Roteiro do Projeto / Milestone Plan (Feature 3 da Fase 1, Parte B).

Singleton que gerencia milestones do ciclo de vida do projeto.
Persiste estado em <project_root>/.mcp_milestones.json.
Arquivo SEPARADO do .mcp_phase_state.json porque milestones e fases são
conceitos diferentes: fase = etapa macro do projeto, milestone = tarefa
concreta dentro de uma fase. Separar evita acoplamento e corrupção cruzada.

Segue o padrão de singleton de tools/phase_ops.py e tools/project_state.py.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class MilestonePlan:
    """Singleton — plano de milestones do projeto ativo."""

    def __init__(self):
        self.milestones: list[dict] = []
        self._file_path: Path | None = None

    def _get_file_path(self) -> Path | None:
        try:
            from tools.project_ops import _get_active_project
            proj = Path(_get_active_project())
            return proj / ".mcp_milestones.json"
        except Exception:
            return None

    def load(self) -> dict:
        fp = self._get_file_path()
        if fp and fp.exists():
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                self.milestones = data.get("milestones", [])
                return {"status": "success", "loaded": True, "count": len(self.milestones)}
            except Exception as e:
                return {"status": "error", "message": f"Erro ao carregar milestones: {e}"}
        self.milestones = []
        return {"status": "success", "loaded": False, "count": 0, "note": "Nenhum plano existente."}

    def save(self) -> dict:
        fp = self._get_file_path()
        if not fp:
            return {"status": "error", "message": "Nenhum projeto ativo definido."}
        try:
            fp.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "milestones": self.milestones,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            fp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            return {"status": "success", "path": str(fp)}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao salvar milestones: {e}"}

    def add_milestone(self, titulo: str, descricao: str, fase_associada: str) -> dict:
        ordem = len(self.milestones) + 1
        milestone = {
            "id": f"m{ordem}",
            "titulo": titulo,
            "descricao": descricao,
            "fase_associada": fase_associada,
            "status": "pendente",
            "criado_em": datetime.now(timezone.utc).isoformat(),
            "concluido_em": None,
            "ordem": ordem,
        }
        self.milestones.append(milestone)
        self.save()
        return {"status": "success", "milestone": milestone}

    def mark_milestone(self, milestone_id: str, status: str) -> dict:
        valid_statuses = {"pendente", "em_andamento", "concluido"}
        if status not in valid_statuses:
            return {"status": "error", "message": f"Status invalido: '{status}'. Validos: {valid_statuses}"}

        for m in self.milestones:
            if m["id"] == milestone_id:
                m["status"] = status
                if status == "concluido":
                    m["concluido_em"] = datetime.now(timezone.utc).isoformat()
                self.save()
                return {"status": "success", "milestone": m}

        return {"status": "error", "message": f"Milestone '{milestone_id}' nao encontrada."}

    def get_next_milestone(self) -> dict | None:
        for m in self.milestones:
            if m["status"] in ("pendente", "em_andamento"):
                return m
        return None

    def progress_summary(self) -> dict:
        total = len(self.milestones)
        if total == 0:
            return {"total": 0, "concluidos": 0, "pendentes": 0, "em_andamento": 0, "percentual": 0.0}
        concluidos = sum(1 for m in self.milestones if m["status"] == "concluido")
        pendentes = sum(1 for m in self.milestones if m["status"] == "pendente")
        em_andamento = sum(1 for m in self.milestones if m["status"] == "em_andamento")
        return {
            "total": total,
            "concluidos": concluidos,
            "pendentes": pendentes,
            "em_andamento": em_andamento,
            "percentual": round(100.0 * concluidos / total, 1),
        }


# ══════════════════════════════════════════════════════════════════
# Singleton + funções de módulo (expostas como tools)
# ══════════════════════════════════════════════════════════════════

_milestone_plan = MilestonePlan()
_milestone_plan.load()


def project_progress() -> dict:
    """Termometro de progresso do milestone atual (Fatia 1.14).

    Retorna percentual, barra visual ASCII e mensagem motivacional.
    Usa os dados do MilestonePlan ja carregado.

    Tool MCP: project_progress
    """
    summary = _milestone_plan.progress_summary()
    total = summary["total"]
    concluidos = summary["concluidos"]
    percentual = summary["percentual"]

    # Barra visual ASCII (10 chars)
    cheio = min(10, round(percentual / 10))
    vazio = 10 - cheio
    barra = "\u2588" * cheio + "\u2591" * vazio

    # Mensagem motivacional
    if total == 0:
        mensagem = "Nenhum milestone ainda. Crie um plano com create_milestone_plan!"
        proximo = None
    elif percentual >= 100:
        mensagem = "Milestone concluido! Avance para o proximo com advance_milestone()."
        proximo = _milestone_plan.get_next_milestone()
    elif percentual >= 75:
        mensagem = f"Quase la! {concluidos}/{total} concluidos. Foco na reta final!"
        proximo = _milestone_plan.get_next_milestone()
    elif percentual >= 50:
        mensagem = f"Metade do caminho! {concluidos}/{total} concluidos."
        proximo = _milestone_plan.get_next_milestone()
    elif percentual > 0:
        mensagem = f"Comecando bem! {concluidos}/{total} concluidos."
        proximo = _milestone_plan.get_next_milestone()
    else:
        mensagem = f"Nenhum item concluido ainda. Comece pelo primeiro milestone!"
        proximo = _milestone_plan.get_next_milestone()

    return {
        "status": "success",
        "milestone_progresso": summary,
        "termometro": f"{barra} {percentual:.1f}%",
        "mensagem": mensagem,
        "proximo_milestone": proximo,
    }


def _generate_milestones_from_gdd(gdd: dict, num: int, scope: str = "medio") -> list[dict]:
    """Gera milestones a partir do GDD e scope, distribuídos por fase.

    O escopo afeta a QUANTIDADE de milestones via multiplicador:
      micro=0.6, pequeno=0.8, medio=1.0, grande=1.3, epico=1.6
    """
    gameplay = gdd.get("gameplay", {})
    mechanics = gameplay.get("mechanics", [])

    SCOPE_MULTIPLIER = {
        "micro": 0.6, "pequeno": 0.8, "medio": 1.0,
        "grande": 1.3, "epico": 1.6,
    }
    num_efetivo = max(3, round(num * SCOPE_MULTIPLIER.get(scope, 1.0)))

    milestones = []

    # PROTOTIPO: mecânicas core (extrai dos primeiros do GDD)
    proto_count = max(1, min(3, num_efetivo // 3))
    proto_mechanics = mechanics[:proto_count]
    for mech in proto_mechanics:
        milestones.append({
            "titulo": f"Prototipar: {mech[:50]}",
            "descricao": f"Implementar a mecanica core '{mech}' com placeholder visual. Foco em funcionamento, nao em aparencia.",
            "fase": "PROTOTIPO",
        })

    # CONTEUDO: conteúdo e assets
    content_tasks = [
        "Criar assets visuais principais (sprites, tiles)",
        "Implementar todos os tipos de inimigos/entidades",
        "Criar sistema de progressao (levels/ondas/fases)",
        "Adicionar SFX e musica de fundo",
        "Criar efeitos visuais e animacoes",
        "Implementar sistema de save/load",
    ]
    content_count = max(1, num_efetivo // 3)
    for task in content_tasks[:content_count]:
        milestones.append({
            "titulo": task[:60],
            "descricao": f"{task}. Fase de CONTEUDO — foco em volume e variedade.",
            "fase": "CONTEUDO",
        })

    # POLIMENTO: ajustes finais
    polish_tasks = [
        "Balanceamento de dificuldade e economia",
        "UI/UX: menus, HUD, feedback visual",
        "Testes de jogabilidade e correcoes de bugs",
        "Otimizacao de performance e exportacao",
        "Sistema de conquistas e trophies",
        "Modo NG+ e conteudo pos-jogo",
    ]
    polish_count = max(1, num_efetivo // 4)
    for task in polish_tasks[:polish_count]:
        milestones.append({
            "titulo": task[:60],
            "descricao": f"{task}. Fase de POLIMENTO — foco em qualidade e experiencia do jogador.",
            "fase": "POLIMENTO",
        })

    return milestones[:num_efetivo]


def create_milestone_plan(
    genero: str = "tower_defense",
    ideia: str = "",
    num_milestones: int = 8,
    force: bool = False,
) -> dict:
    """Cria um plano de milestones baseado no genero e ideia do jogo.

    Args:
        genero: Genero do jogo (17 generos via GAME_PATTERNS).
        ideia: Descricao da ideia do jogo.
        num_milestones: Quantidade de milestones a gerar (default: 8).
        force: Se True, sobrescreve plano existente.

    Returns:
        dict com status e milestones gerados.
    """
    # Verifica se já existe plano
    if _milestone_plan.milestones and not force:
        return {
            "status": "error",
            "message": "Ja existe um plano de milestones. Use force=true para sobrescrever.",
        }

    # Gera GDD (Parte A já corrigida — suporta 17 gêneros)
    from tools.balance_ops import gdd_generate
    gdd_result = gdd_generate(concept=ideia or f"Jogo de {genero}", game_type=genero)

    if gdd_result.get("status") == "error":
        # Propaga erro do gdd_generate (gênero inválido etc)
        return gdd_result

    gdd = gdd_result.get("gdd", {})

    # Estima escopo
    scope_estimation = "real"
    scope_category = "medio"
    try:
        from tools.analyze_ops import estimate_game_scope
        scope_result = estimate_game_scope()
        scope_category = scope_result.get("category", "medio")
    except Exception:
        scope_category = "medio"
        scope_estimation = "fallback"

    # Gera milestones a partir do GDD
    raw_milestones = _generate_milestones_from_gdd(gdd, num_milestones, scope=scope_category)

    # Limpa plano anterior se force=True
    if force:
        _milestone_plan.milestones = []

    # Adiciona cada milestone
    created = []
    for rm in raw_milestones:
        r = _milestone_plan.add_milestone(
            titulo=rm["titulo"],
            descricao=rm["descricao"],
            fase_associada=rm["fase"],
        )
        if r["status"] == "success":
            created.append(r["milestone"])

    return {
        "status": "success",
        "genero": genero,
        "gdd_title": gdd.get("title", ""),
        "scope": scope_category,
        "scope_estimation": scope_estimation,
        "milestones": created,
        "progress": _milestone_plan.progress_summary(),
    }


def advance_milestone(milestone_id: str | None = None) -> dict:
    """Avança um milestone. Sem id, avança o próximo pendente/em_andamento.

    Args:
        milestone_id: ID do milestone a concluir. Se None, usa get_next_milestone().

    Returns:
        dict com milestone concluido, próximo, e progress_summary.
    """
    if milestone_id:
        target = None
        for m in _milestone_plan.milestones:
            if m["id"] == milestone_id:
                target = m
                break
        if target is None:
            return {"status": "error", "message": f"Milestone '{milestone_id}' nao encontrada."}
    else:
        target = _milestone_plan.get_next_milestone()
        if target is None:
            return {
                "status": "error",
                "message": "Nenhum milestone pendente ou em andamento.",
                "progress": _milestone_plan.progress_summary(),
            }

    # Marca como concluido
    r = _milestone_plan.mark_milestone(target["id"], "concluido")
    if r["status"] != "success":
        return r

    next_ms = _milestone_plan.get_next_milestone()

    return {
        "status": "success",
        "concluido": target,
        "proximo": next_ms,
        "progress": _milestone_plan.progress_summary(),
    }


def get_milestone_plan() -> dict:
    """Retorna o plano completo de milestones + progresso."""
    return {
        "status": "success",
        "milestones": _milestone_plan.milestones,
        "progress": _milestone_plan.progress_summary(),
    }
