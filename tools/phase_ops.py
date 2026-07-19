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


def resume_session() -> dict:
    """Fatia 1.8: resume_session — recuperacao de sessao.

    Le o estado persistente de todas as fontes (fase, milestone, roadmap)
    e devolve um resumo unificado: "voce parou aqui, o proximo passo e X".

    Fontes consultadas:
    1. .roadmap_progress.json (raiz do MCP) — progresso das fatias
    2. PhaseState (phase_ops) — fase atual do projeto de jogo
    3. MilestonePlan (milestone_ops) — milestone pendente/em andamento

    Tool MCP: resume_session
    """
    import json as _json
    from pathlib import Path as _Path

    result = {
        "status": "success",
        "projeto_jogo": {},
        "roadmap_mcp": {},
        "proximo_passo": "",
    }

    # ── 1. Roadmap MCP ──────────────────────────────────────
    roadmap_path = _Path(__file__).resolve().parent.parent / ".roadmap_progress.json"
    fatia_atual = None
    fatia_atual_status = None
    if roadmap_path.exists():
        try:
            roadmap = _json.loads(roadmap_path.read_text(encoding="utf-8"))
            # Encontrar a proxima fatia nao concluida
            fatias_pendentes = []
            fatia_atual = None
            fatia_atual_status = None

            # Ordenar fatias por numero: prioridade Camada 0, depois 1, etc.
            # Extrair todos os registros que comecam com "fatia_"
            fatias = {}
            for key, value in roadmap.items():
                if key.startswith("fatia_") and isinstance(value, dict):
                    fatias[key] = value

            # Verificar pendentes explicitos
            pendentes = roadmap.get("pendentes", {})

            result["roadmap_mcp"] = {
                "total_fatias_registradas": len(fatias),
                "fatias_concluidas": sum(1 for v in fatias.values() if v.get("status") == "concluida"),
                "fatias_bloqueadas": sum(1 for v in fatias.values() if v.get("status") == "bloqueada"),
                "pendentes_explicitos": pendentes,
            }

            # ── Parse numerico de chave "fatia_X.Y[sufixo]" ──
            import re as _re

            def _parse_fatia_key(key: str) -> tuple:
                """Converte 'fatia_1.8' → (1, 8, ''), 'fatia_0.7b' → (0, 7, 'b')."""
                m = _re.match(r'fatia_(\d+)\.(\d+)([a-z]*)$', key)
                if m:
                    return (int(m.group(1)), int(m.group(2)), m.group(3))
                return (999, 0, key)  # nao-parseaveis vao para o fim

            # Ordenacao numerica: camada, sub, sufixo alfabetico
            fatias_ordenadas = sorted(fatias.keys(), key=_parse_fatia_key)

            # 1) Priorizar pendentes explicitos do roadmap
            fatia_atual = None
            fatia_atual_status = None
            proxima_sugerida = None

            for pend_key in ["Camada_1_proximo", "Camada_0_proximo"]:
                if pend_key in pendentes and isinstance(pendentes[pend_key], str):
                    # Extrai numero da fatia do texto (ex: "1.8 resume_session")
                    m = _re.match(r'(\d+\.\d+[a-z]*)', pendentes[pend_key])
                    if m:
                        proxima_sugerida = f"fatia_{m.group(1)}"
                        break

            # 2) Se pendentes aponta para uma fatia conhecida e nao-concluida, usa ela
            if proxima_sugerida and proxima_sugerida in fatias:
                st = fatias[proxima_sugerida].get("status")
                if st != "concluida":
                    fatia_atual = proxima_sugerida
                    fatia_atual_status = st

            # 3) Fallback: percorrer em ordem numerica, pular concluidas E bloqueadas
            if not fatia_atual:
                for fkey in fatias_ordenadas:
                    st = fatias[fkey].get("status")
                    if st == "concluida":
                        continue
                    if st == "bloqueada":
                        # Registra bloqueadores mas nao para neles
                        if "bloqueadores" not in result["roadmap_mcp"]:
                            result["roadmap_mcp"]["bloqueadores"] = []
                        result["roadmap_mcp"]["bloqueadores"].append({
                            "fatia": fkey,
                            "motivo": fatias[fkey].get("resultado", "")[:120],
                        })
                        continue
                    fatia_atual = fkey
                    fatia_atual_status = st
                    break

            # 4) Se so tem bloqueadas, reportar a primeira delas
            if not fatia_atual:
                for fkey in fatias_ordenadas:
                    if fatias[fkey].get("status") == "bloqueada":
                        fatia_atual = fkey
                        fatia_atual_status = "bloqueada"
                        break

            if fatia_atual:
                result["roadmap_mcp"]["fatia_atual"] = fatia_atual
                result["roadmap_mcp"]["fatia_status"] = fatia_atual_status
                result["roadmap_mcp"]["detalhe"] = fatias[fatia_atual].get("resultado", "")
            elif pendentes:
                result["roadmap_mcp"]["proximo"] = str(pendentes)

            # Montar proximo_passo inteligente
            if fatia_atual and fatia_atual_status == "bloqueada":
                bloqueadores = result["roadmap_mcp"].get("bloqueadores", [])
                if bloqueadores:
                    nomes = [b["fatia"] for b in bloqueadores]
                    result["proximo_passo"] = (
                        f"Bloqueado: {', '.join(nomes)}. "
                        f"Resolver bloqueio antes de prosseguir."
                    )
                else:
                    result["proximo_passo"] = f"Fatia {fatia_atual} (bloqueada) — resolver bloqueio."
            elif fatia_atual:
                result["proximo_passo"] = f"Fatia {fatia_atual} ({fatia_atual_status})"
            elif pendentes:
                result["proximo_passo"] = f"Verificar pendentes: {pendentes}"
            else:
                result["proximo_passo"] = "Verificar roadmap"
        except Exception as e:
            result["roadmap_mcp"] = {"status": "error", "message": f"Erro ao ler roadmap: {e}"}
            result["proximo_passo"] = "Erro ao ler roadmap. Verificar .roadmap_progress.json."
    else:
        result["roadmap_mcp"] = {"status": "ausente", "message": ".roadmap_progress.json nao encontrado na raiz do MCP."}
        result["proximo_passo"] = "Roadmap ausente. Criar ou verificar configuracao do projeto."

    # ── 1.5. Passos intra-fatia (step_tracker) ─────────────
    try:
        from tools.step_tracker import get_step_tracker
        st = get_step_tracker()
        if fatia_atual and fatia_atual_status not in ("bloqueada", "concluida"):
            progress = st.get_progress(fatia_atual)
            next_step = st.get_next_pending_step(fatia_atual)
            result["passos_fatia"] = {
                "fatia": fatia_atual,
                "passos_concluidos": progress["passos_concluidos"],
                "total_concluidos": progress["total_concluidos"],
                "proximo_passo_fatia": next_step,
            }
            if next_step:
                result["proximo_passo"] = (
                    f"{result['proximo_passo']} | Passo {next_step} pendente"
                )
    except Exception:
        pass  # Step tracker e opcional — se falhar, segue sem ele

    # ── 2. Projeto de jogo: fase ───────────────────────────
    try:
        phase_info = get_current_phase()
        if phase_info.get("status") == "success":
            result["projeto_jogo"]["fase"] = phase_info.get("phase")
            result["projeto_jogo"]["fase_label"] = phase_info.get("phase_label")
            result["projeto_jogo"]["pode_avancar"] = phase_info.get("pode_avancar")
            result["projeto_jogo"]["criterio_para_avancar"] = phase_info.get("criterio_para_avancar")
        else:
            result["projeto_jogo"]["fase"] = None
            result["projeto_jogo"]["nota"] = "Sem projeto de jogo ativo ou erro ao consultar fase."
    except Exception as e:
        result["projeto_jogo"]["fase"] = None
        result["projeto_jogo"]["erro"] = str(e)

    # ── 3. Projeto de jogo: milestone ──────────────────────
    next_ms = None
    try:
        from tools.milestone_ops import _milestone_plan
        next_ms = _milestone_plan.get_next_milestone()
        progress = _milestone_plan.progress_summary()
        result["projeto_jogo"]["milestone_atual"] = next_ms
        result["projeto_jogo"]["milestone_progresso"] = progress
    except Exception as e:
        result["projeto_jogo"]["milestone_atual"] = None
        result["projeto_jogo"]["milestone_erro"] = str(e)

    # ── 4. Montar proximo passo unificado ──────────────────
    partes = []
    if result["projeto_jogo"].get("fase"):
        partes.append(f"Fase: {result['projeto_jogo'].get('fase_label', result['projeto_jogo']['fase'])}")
    if fatia_atual:
        partes.append(f"Roadmap: {fatia_atual} ({fatia_atual_status})")
    if next_ms:
        partes.append(f"Milestone: {next_ms.get('titulo', next_ms.get('id', '?'))} ({next_ms.get('status', '?')})")

    if partes:
        result["resumo"] = " | ".join(partes)
    else:
        result["resumo"] = "Nenhum estado encontrado. Use project_manage para selecionar um projeto."

    return result
