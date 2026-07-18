"""phase_ops.py — Máquina de Estados de Fase (Feature 1 da Fase 1).

Singleton que gerencia o ciclo de vida do projeto:
  IDEIA → DESIGN → PROTOTIPO → CONTEUDO → POLIMENTO → PRONTO_PARA_LANCAR

Persiste estado em <project_root>/.mcp_phase_state.json.
Segue o padrão de singleton de tools/project_state.py.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent

# ── Callback de invalidação de cache (Feature 8) ──
# Registrado por server.py para invalidar _TOOL_DEFS_CACHE quando a fase avança.
_cache_invalidator: Callable[[], None] | None = None


def set_cache_invalidator(fn: Callable[[], None]) -> None:
    """Registra callback chamado quando a fase avança com sucesso."""
    global _cache_invalidator
    _cache_invalidator = fn

# ══════════════════════════════════════════════════════════════════
# Enum de fases (ordem fixa)
# ══════════════════════════════════════════════════════════════════

PHASE_ORDER: list[str] = [
    "IDEIA",
    "DESIGN",
    "PROTOTIPO",
    "CONTEUDO",
    "POLIMENTO",
    "PRONTO_PARA_LANCAR",
]

_PHASE_LABELS: dict[str, str] = {
    "IDEIA": "Ideia",
    "DESIGN": "Design",
    "PROTOTIPO": "Protótipo",
    "CONTEUDO": "Conteúdo",
    "POLIMENTO": "Polimento",
    "PRONTO_PARA_LANCAR": "Pronto para Lançar",
}

# ══════════════════════════════════════════════════════════════════
# Classe PhaseState
# ══════════════════════════════════════════════════════════════════

class PhaseState:
    """Singleton — estado da máquina de fases do projeto ativo."""

    def __init__(self):
        self.current_phase: str = "IDEIA"
        self.history: list[dict] = []
        self._file_path: Path | None = None

    # ── Persistência ──────────────────────────────────────────

    def _get_file_path(self) -> Path | None:
        """Retorna o caminho do JSON de estado, ou None se não houver projeto ativo."""
        try:
            from tools.project_ops import _get_active_project
            proj = Path(_get_active_project())
            return proj / ".mcp_phase_state.json"
        except Exception:
            return None

    def load(self) -> dict:
        """Carrega estado do JSON. Se não existir, cria com IDEIA."""
        fp = self._get_file_path()
        if fp and fp.exists():
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                self.current_phase = data.get("current_phase", "IDEIA")
                self.history = data.get("history", [])
                return {"status": "success", "phase": self.current_phase, "loaded": True}
            except Exception as e:
                return {"status": "error", "message": f"Erro ao carregar estado: {e}"}

        # Estado novo — persiste no disco para que _get_phase_tools() funcione
        self.current_phase = "IDEIA"
        self.history = []
        save_result = self.save()
        return {
            "status": "success",
            "phase": "IDEIA",
            "loaded": False,
            "note": "Estado inicial criado e persistido.",
            "save_result": save_result,
        }

    def save(self) -> dict:
        """Grava estado no JSON (com schema_version via Fatia 0.10)."""
        fp = self._get_file_path()
        if not fp:
            return {"status": "error", "message": "Nenhum projeto ativo definido."}
        try:
            fp.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "current_phase": self.current_phase,
                "history": self.history,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            from tools.schema_migration import save_state_with_version
            save_state_with_version(".mcp_phase_state.json", data, fp.parent)
            return {"status": "success", "path": str(fp)}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao salvar estado: {e}"}

    # ── Critérios de transição ─────────────────────────────────

    def can_advance_to(self, next_phase: str) -> tuple[bool, str]:
        """Verifica se pode avançar para next_phase. Retorna (pode, motivo)."""
        # Valida se next_phase existe
        if next_phase not in PHASE_ORDER:
            return False, f"Fase '{next_phase}' não existe. Fases válidas: {PHASE_ORDER}"

        # Valida se é a PRÓXIMA fase (não pode pular)
        try:
            current_idx = PHASE_ORDER.index(self.current_phase)
            next_idx = PHASE_ORDER.index(next_phase)
        except ValueError:
            return False, "Fase atual ou destino inválida."

        if next_idx <= current_idx:
            return False, f"Não é possível retroceder de '{self.current_phase}' para '{next_phase}'."

        if next_idx > current_idx + 1:
            return False, (
                f"Não é possível pular fases. De '{self.current_phase}' "
                f"a próxima é '{PHASE_ORDER[current_idx + 1]}', não '{next_phase}'."
            )

        # Critérios específicos por transição
        transition_key = f"{self.current_phase}→{next_phase}"

        if transition_key == "IDEIA→DESIGN":
            return True, "Sempre permitido."

        elif transition_key == "DESIGN→PROTOTIPO":
            return self._check_design_to_prototipo()

        elif transition_key == "PROTOTIPO→CONTEUDO":
            return self._check_prototipo_to_conteudo()

        elif transition_key == "CONTEUDO→POLIMENTO":
            return self._check_conteudo_to_polimento()

        elif transition_key == "POLIMENTO→PRONTO_PARA_LANCAR":
            return self._check_polimento_to_pronto()

        return False, f"Transição desconhecida: {transition_key}"

    def _check_design_to_prototipo(self) -> tuple[bool, str]:
        """DESIGN→PROTOTIPO: exige pelo menos 1 .tscn no projeto."""
        try:
            from tools.project_ops import _get_active_project
            proj = _get_active_project()
            tscn_files = list(proj.rglob("*.tscn"))
            # Filtra .godot/
            tscn_files = [f for f in tscn_files if ".godot" not in str(f)]
            if len(tscn_files) == 0:
                return False, "É necessário pelo menos 1 arquivo .tscn no projeto para avançar para PROTOTIPO."
            return True, f"{len(tscn_files)} arquivo(s) .tscn encontrado(s)."
        except Exception as e:
            return False, f"Erro ao verificar .tscn: {e}"

    def _check_prototipo_to_conteudo(self) -> tuple[bool, str]:
        """PROTOTIPO→CONTEUDO: exige run_verification_pipeline com status PASSOU."""
        last_result = self._get_last_pipeline_result()
        if last_result is None:
            return False, "Rode run_verification_pipeline antes de avançar. O pipeline valida compilação, execução headless, screenshot e testes GUT."
        if last_result.get("status") not in ("success", "PASSOU"):
            reason = last_result.get("stopped_reason", "Pipeline falhou.")
            return False, f"Pipeline de verificação FALHOU: {reason}. Corrija os problemas e rode novamente."
        return True, f"Pipeline de verificação PASSOU ({last_result.get('total_duration_ms', '?')}ms)."

    def _check_conteudo_to_polimento(self) -> tuple[bool, str]:
        """CONTEUDO→POLIMENTO: exige >= 3 sprites E >= 1 áudio no projeto."""
        try:
            from tools.project_state import refresh_state, get_state
            refresh_state()
            state = get_state()
            sprite_count = len(state.sprites)
            audio_count = len(state.audio)
            missing = []
            if sprite_count < 3:
                missing.append(f"{3 - sprite_count} sprite(s) (tem {sprite_count}, precisa de 3)")
            if audio_count < 1:
                missing.append(f"{1 - audio_count} áudio(s) (tem {audio_count}, precisa de 1)")
            if missing:
                return False, "Requisitos não atendidos: " + "; ".join(missing) + "."
            return True, f"{sprite_count} sprites e {audio_count} áudio(s) encontrados."
        except Exception as e:
            return False, f"Erro ao verificar assets: {e}"

    def _check_polimento_to_pronto(self) -> tuple[bool, str]:
        """POLIMENTO→PRONTO_PARA_LANCAR: exige release_checklist >= 8/10."""
        try:
            from tools.deploy_ops import release_checklist
            result = release_checklist()
            score_str = result.get("score", "0/10")
            score_num = int(score_str.split("/")[0])
            if score_num < 8:
                return False, f"Release checklist insuficiente: {score_str}. Mínimo: 8/10."
            return True, f"Release checklist: {score_str} (>= 8/10)."
        except Exception as e:
            return False, f"Erro ao executar release_checklist: {e}"

    def _get_last_pipeline_result(self) -> dict | None:
        """Lê o último resultado do pipeline do JSON de estado."""
        fp = self._get_file_path()
        if not fp or not fp.exists():
            return None
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            return data.get("_last_pipeline_result")
        except Exception:
            return None

    def set_last_pipeline_result(self, result: dict) -> None:
        """Armazena o último resultado do pipeline no JSON (chamado por verification_ops)."""
        fp = self._get_file_path()
        if not fp:
            return
        try:
            if fp.exists():
                data = json.loads(fp.read_text(encoding="utf-8"))
            else:
                data = {}
            data["_last_pipeline_result"] = {
                "status": result.get("status"),
                "overall": result.get("overall"),
                "stopped_at_step": result.get("stopped_at_step"),
                "stopped_reason": result.get("stopped_reason"),
                "total_duration_ms": result.get("total_duration_ms"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            fp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass  # Falha ao salvar resultado do pipeline não deve quebrar o pipeline

    # ── Avanço ─────────────────────────────────────────────────

    def advance(self, next_phase: str, force: bool = False, reason: str = "") -> dict:
        """Avança para a próxima fase. Se force=True, ignora critério mas exige reason."""
        if force:
            if not reason or not reason.strip():
                return {
                    "status": "error",
                    "message": "Avanço forçado exige o parâmetro 'reason' com a justificativa.",
                    "current_phase": self.current_phase,
                }
            ok, _msg = True, f"Forçado: {reason}"
        else:
            ok, msg = self.can_advance_to(next_phase)
            if not ok:
                return {
                    "status": "error",
                    "message": msg,
                    "current_phase": self.current_phase,
                }

        old_phase = self.current_phase
        self.current_phase = next_phase
        entry = {
            "from": old_phase,
            "to": next_phase,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "criterio_cumprido": msg if not force else f"Forçado: {reason}",
            "forced": force,
        }
        if force:
            entry["reason"] = reason
        self.history.append(entry)
        self.save()

        # Feature 8: invalida cache de tools do server.py
        if _cache_invalidator:
            _cache_invalidator()

        return {
            "status": "success",
            "from": old_phase,
            "to": next_phase,
            "criterio_cumprido": entry["criterio_cumprido"],
        }


# ══════════════════════════════════════════════════════════════════
# Singleton + funções de módulo (expostas como tools)
# ══════════════════════════════════════════════════════════════════

_phase_state = PhaseState()

# Garante que o estado é carregado do disco na primeira chamada
_phase_state.load()


def get_current_phase() -> dict:
    """Retorna a fase atual e o que falta para avançar.

    Tool MCP: get_current_phase
    """
    phase = _phase_state.current_phase
    try:
        current_idx = PHASE_ORDER.index(phase)
    except ValueError:
        return {"status": "error", "message": f"Fase desconhecida: {phase}"}

    # Última fase
    if current_idx >= len(PHASE_ORDER) - 1:
        return {
            "status": "success",
            "phase": phase,
            "phase_label": _PHASE_LABELS.get(phase, phase),
            "next_phase": None,
            "criterio_para_avancar": "Projeto já está na fase final (PRONTO_PARA_LANCAR).",
            "history_count": len(_phase_state.history),
        }

    next_phase = PHASE_ORDER[current_idx + 1]
    ok, msg = _phase_state.can_advance_to(next_phase)

    return {
        "status": "success",
        "phase": phase,
        "phase_label": _PHASE_LABELS.get(phase, phase),
        "next_phase": next_phase,
        "next_phase_label": _PHASE_LABELS.get(next_phase, next_phase),
        "pode_avancar": ok,
        "criterio_para_avancar": msg,
        "history_count": len(_phase_state.history),
    }


def advance_phase(force: bool = False, reason: str = "") -> dict:
    """Avança automaticamente para a PRÓXIMA fase da sequência.

    Tool MCP: advance_phase
    """
    phase = _phase_state.current_phase
    try:
        current_idx = PHASE_ORDER.index(phase)
    except ValueError:
        return {"status": "error", "message": f"Fase desconhecida: {phase}"}

    if current_idx >= len(PHASE_ORDER) - 1:
        return {
            "status": "error",
            "message": "Projeto já está na fase final (PRONTO_PARA_LANCAR). Não há próxima fase.",
            "current_phase": phase,
        }

    next_phase = PHASE_ORDER[current_idx + 1]
    return _phase_state.advance(next_phase, force=force, reason=reason)


def get_phase_history() -> dict:
    """Retorna o histórico de avanços de fase.

    Tool MCP: get_phase_history
    """
    return {
        "status": "success",
        "current_phase": _phase_state.current_phase,
        "history": _phase_state.history,
        "total_advances": len(_phase_state.history),
    }


def get_next_step() -> dict:
    """Feature 10: retorna o proximo passo obrigatorio da sessao.

    Grava o PID atual no marcador .mcp_session_started do projeto ativo,
    liberando o gate em call_tool() para esta sessao.

    Tool MCP: get_next_step
    """
    import os
    from tools.project_ops import _get_active_project

    try:
        proj = _get_active_project()
        marker = proj / ".mcp_session_started"
    except Exception:
        # Sem projeto ativo: retorna orientacao basica, sem gravar marcador
        return {
            "status": "success",
            "phase": None,
            "phase_label": "Sem projeto ativo",
            "next_milestone": "Selecionar ou criar um projeto",
            "blockers": ["Nenhum projeto ativo selecionado"],
            "suggested_action": "Use project_manage para selecionar um projeto existente ou criar um novo. "
                                "Depois chame get_next_step() novamente.",
            "session_started": False,
        }

    # Grava PID no marcador
    marker_content = {"session_started": True, "server_pid": os.getpid()}
    import json
    marker.write_text(json.dumps(marker_content), encoding="utf-8")

    # Coleta dados da fase atual
    phase_info = get_current_phase()
    if phase_info.get("status") != "success":
        return {"status": "error", "message": "Erro ao consultar fase atual.", "detail": phase_info}

    phase = phase_info["phase"]
    pode_avancar = phase_info.get("pode_avancar", False)
    criterio = phase_info.get("criterio_para_avancar", "")
    next_phase = phase_info.get("next_phase")
    next_label = phase_info.get("next_phase_label", "")

    # Monta blockers e suggested_action com base na fase
    blockers = []
    suggested_action = ""

    if phase == "IDEIA":
        blockers = [] if pode_avancar else ["Nenhum criterio bloqueia IDEIA->DESIGN (sempre permitido)"]
        suggested_action = "Defina o conceito do jogo: use set_project_brief para registrar genero e estilo. "
        suggested_action += "Depois avance com advance_phase()."

    elif phase == "DESIGN":
        blockers = ["Nenhum arquivo .tscn encontrado"] if not pode_avancar else []
        suggested_action = "Crie a cena principal do jogo: use scene_manage op 'create' com root_type apropriado. "
        if next_phase:
            suggested_action += f"Quando tiver pelo menos 1 .tscn, avance para {next_label} com advance_phase()."

    elif phase == "PROTOTIPO":
        blockers = ["Pipeline de verificacao nao executado ou falhou"] if not pode_avancar else []
        suggested_action = "Execute run_verification_pipeline para validar compilacao, execucao e testes. "
        if next_phase:
            suggested_action += f"Se passar, avance para {next_label} com advance_phase()."

    elif phase == "CONTEUDO":
        blockers = []
        if not pode_avancar:
            crit_parts = criterio.split(".")
            for part in crit_parts:
                part = part.strip()
                if "sprite" in part.lower():
                    blockers.append(f"Sprites insuficientes: {part}")
                elif "audio" in part.lower():
                    blockers.append(f"Audio insuficiente: {part}")
            if not blockers:
                blockers = [criterio]
        suggested_action = "Adicione sprites e audio ao projeto. Use asset_manage para importar assets. "
        if next_phase:
            suggested_action += f"Quando tiver >= 3 sprites e >= 1 audio, avance para {next_label} com advance_phase()."

    elif phase == "POLIMENTO":
        blockers = ["Release checklist insuficiente (< 8/10)"] if not pode_avancar else []
        suggested_action = "Execute release_checklist() e corrija os itens pendentes. "
        if next_phase:
            suggested_action += f"Quando atingir >= 8/10, avance para {next_label} com advance_phase()."

    elif phase == "PRONTO_PARA_LANCAR":
        blockers = []
        suggested_action = "Projeto na fase final. Execute export_manage op 'build' para exportar o executavel. "
        suggested_action += "Use release_checklist() para verificar se todos os itens estao OK."

    return {
        "status": "success",
        "phase": phase,
        "phase_label": phase_info.get("phase_label", phase),
        "next_milestone": f"{next_label}" if next_phase else "Fase final",
        "pode_avancar": pode_avancar,
        "criterio_para_avancar": criterio,
        "blockers": blockers,
        "suggested_action": suggested_action,
        "session_started": True,
        "server_pid": os.getpid(),
    }
