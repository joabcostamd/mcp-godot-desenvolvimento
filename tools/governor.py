"""governor.py — Governador de Autonomia (Fatia 0.14).

Transforma os 5 guardrails da seção 4 do mestre em mecanismo real.
Atua como middleware no call_tool() — verifica antes, registra depois.

Princípios:
  - Simples: uma classe, estado em memória + flush para disco
  - Reusa rate_limiter.py (sliding window) para orçamento de chamadas
  - Desligável via flag GOVERNOR_ENABLED
  - Não altera comportamento de tools existentes — só adiciona verificações
"""

import time
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("mcp-godot.governor")

# ── Defaults ──────────────────────────────────────────────────────────

DEFAULT_MAX_ITERATIONS = 8       # Teto de iteração por fatia (mestre 4.1)
DEFAULT_SPIRAL_THRESHOLD = 2     # Mesma chamada falhando N vezes = anti-spiral (4.2)
DEFAULT_NO_PROGRESS_THRESHOLD = 3  # N passagens sem progresso (4.3)
DEFAULT_BUDGET_CALLS = 300       # Orçamento de chamadas por fatia (4.4)

# Tools de infra/setup que nunca são bloqueadas (equivalente a SESSION_ALWAYS_ALLOWED)
ALWAYS_ALLOWED = {
    "ping", "health_check", "self_test", "bootstrap_godot_mcp",
    "read_file", "write_file", "safe_write_gdscript",
    "smoke_test", "dump_mcp_state", "capture_proof", "verify_proof",
}


@dataclass
class CallRecord:
    """Registro de uma chamada de tool."""
    name: str
    arguments: dict
    success: bool
    timestamp: float
    error_message: str = ""


@dataclass
class GovernorState:
    """Estado serializável do governador."""
    iteration_count: int = 0
    last_call: Optional[str] = None
    last_args_hash: Optional[int] = None
    spiral_failures: int = 0
    no_progress_count: int = 0
    last_progress_marker: Optional[str] = None
    budget_used: int = 0
    recent_calls: list[dict] = field(default_factory=list)
    stopped: bool = False
    stop_reason: str = ""


class AutonomyGovernor:
    """Governador de autonomia — os freios reais da IA agêntica.

    Uso:
        gov = AutonomyGovernor()
        # Antes de executar uma tool:
        ok, reason = gov.check_before("tool_name", args)
        if not ok:
            return error(reason)
        # Depois de executar:
        gov.record_after("tool_name", args, success, error_msg)
    """

    def __init__(
        self,
        enabled: bool = True,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        spiral_threshold: int = DEFAULT_SPIRAL_THRESHOLD,
        no_progress_threshold: int = DEFAULT_NO_PROGRESS_THRESHOLD,
        budget_calls: int = DEFAULT_BUDGET_CALLS,
        hard_stop: bool = True,
    ):
        self.enabled = enabled
        self.max_iterations = max_iterations
        self.spiral_threshold = spiral_threshold
        self.no_progress_threshold = no_progress_threshold
        self.budget_calls = budget_calls
        self.hard_stop = hard_stop  # False = modo "warn only"
        self.state = GovernorState()
        self._state_path: Optional[Path] = None

    # ── Hooks de integração ──────────────────────────────────────────

    def check_before(self, tool_name: str, arguments: dict) -> tuple[bool, str]:
        """Verifica se a tool pode ser executada. Retorna (permitido, motivo).

        Chamado ANTES de executar a tool.
        Se não permitido, a tool NÃO deve executar.
        """
        if not self.enabled:
            return True, ""

        # Tools de infra sempre passam
        if tool_name in ALWAYS_ALLOWED:
            return True, ""

        # 1. Verificar se já parou por limite anterior
        if self.state.stopped:
            return False, f"Governador parou anteriormente: {self.state.stop_reason}"

        # 2. Teto de iteração (4.1)
        if self.state.iteration_count >= self.max_iterations:
            msg = f"Limite de {self.max_iterations} iterações atingido. Escalar para revisão sênior."
            if self.hard_stop:
                self.state.stopped = True
                self.state.stop_reason = msg
            return False, msg

        # 3. Anti-spiral (4.2)
        args_hash = hash(f"{tool_name}:{json.dumps(arguments, sort_keys=True, default=str)}")
        if (self.state.last_call == tool_name
                and self.state.last_args_hash == args_hash
                and self.state.spiral_failures >= self.spiral_threshold):
            msg = (f"Anti-spiral: '{tool_name}' falhou {self.spiral_threshold}x com os mesmos "
                   f"argumentos. Parando para evitar loop.")
            if self.hard_stop:
                self.state.stopped = True
                self.state.stop_reason = msg
            return False, msg

        # 4. Orçamento (4.4)
        if self.state.budget_used >= self.budget_calls:
            msg = f"Orcamento de {self.budget_calls} chamadas excedido."
            if self.hard_stop:
                self.state.stopped = True
                self.state.stop_reason = msg
            return False, msg

        return True, ""

    def record_after(
        self,
        tool_name: str,
        arguments: dict,
        success: bool,
        error_message: str = "",
        progress_marker: Optional[str] = None,
    ):
        """Registra o resultado de uma chamada de tool.

        Chamado DEPOIS de executar a tool (com sucesso ou falha).
        """
        if not self.enabled:
            return

        args_hash = hash(f"{tool_name}:{json.dumps(arguments, sort_keys=True, default=str)}")

        # Incrementar contadores
        self.state.iteration_count += 1
        self.state.budget_used += 1

        # Detectar repetição (anti-spiral)
        if not success:
            if (tool_name == self.state.last_call
                    and args_hash == self.state.last_args_hash):
                self.state.spiral_failures += 1
            else:
                # Nova ferramenta/args diferentes: iniciar contagem em 1
                self.state.spiral_failures = 1
            # Se atingiu o threshold, parar AGORA
            if self.state.spiral_failures >= self.spiral_threshold:
                msg = (f"Anti-spiral: '{tool_name}' falhou {self.spiral_threshold}x com os mesmos "
                       f"argumentos. Parando para evitar loop.")
                if self.hard_stop:
                    self.state.stopped = True
                    self.state.stop_reason = msg
        else:
            self.state.spiral_failures = 0  # Sucesso reseta

        # Detectar progresso (4.3)
        if progress_marker and progress_marker != self.state.last_progress_marker:
            self.state.no_progress_count = 0  # Novo progresso → reset
            self.state.last_progress_marker = progress_marker
        elif not success:
            self.state.no_progress_count += 1

        # Atualizar último estado
        self.state.last_call = tool_name
        self.state.last_args_hash = args_hash

        # Manter histórico (últimas 50 chamadas)
        self.state.recent_calls.append({
            "name": tool_name,
            "success": success,
            "error": error_message[:200] if error_message else "",
            "timestamp": time.time(),
        })
        if len(self.state.recent_calls) > 50:
            self.state.recent_calls = self.state.recent_calls[-50:]

        # Verificar não-progresso após registrar
        if self.state.no_progress_count >= self.no_progress_threshold:
            msg = (f"Não-progresso detectado: {self.no_progress_threshold} passagens sem "
                   f"avanço mensurável.")
            if self.hard_stop:
                self.state.stopped = True
                self.state.stop_reason = msg

    # ── Escalação (4.7) ──────────────────────────────────────────────

    def build_escalation_package(self, task_description: str) -> dict:
        """Monta o pacote de escalação conforme mestre 4.7.

        Retorna:
            {
                "task": o que a fatia deveria fazer,
                "attempts": o que foi tentado (últimas 10 chamadas),
                "output": estado atual do governador,
                "hypothesis": hipótese da causa,
                "state_preserved": caminho do estado salvo
            }
        """
        return {
            "task": task_description,
            "attempts": self.state.recent_calls[-10:] if self.state.recent_calls else [],
            "output": {
                "iteration_count": self.state.iteration_count,
                "spiral_failures": self.state.spiral_failures,
                "no_progress_count": self.state.no_progress_count,
                "budget_used": self.state.budget_used,
                "stopped": self.state.stopped,
                "stop_reason": self.state.stop_reason,
            },
            "hypothesis": self._hypothesize_cause(),
            "state_preserved": str(self._state_path) if self._state_path else "in-memory",
        }

    def _hypothesize_cause(self) -> str:
        """Tenta diagnosticar a causa da parada."""
        if self.state.stopped:
            return self.state.stop_reason
        if self.state.spiral_failures >= self.spiral_threshold:
            return f"Possível loop: '{self.state.last_call}' repetido com mesmos argumentos"
        if self.state.no_progress_count >= self.no_progress_threshold:
            return "Possível stuck: múltiplas tentativas sem progresso mensurável"
        if self.state.budget_used >= self.budget_calls:
            return "Orçamento de chamadas excedido"
        return "Causa desconhecida"

    # ── Persistência ─────────────────────────────────────────────────

    def save(self, path: Optional[Path] = None) -> str:
        """Salva o estado do governador em disco (com schema_version via Fatia 0.10)."""
        if isinstance(path, str):
            path = Path(path)
        save_path = path or self._state_path or Path(".mcp_governor_state.json")
        self._state_path = save_path
        data = {
            "iteration_count": self.state.iteration_count,
            "stopped": self.state.stopped,
            "stop_reason": self.state.stop_reason,
            "no_progress_count": self.state.no_progress_count,
            "budget_used": self.state.budget_used,
        }
        try:
            from tools.schema_migration import save_state_with_version
            save_state_with_version(".mcp_governor_state.json", data, save_path.parent)
        except Exception:
            save_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        logger.info("Governador: estado salvo em %s", save_path)
        return str(save_path)

    def load(self, path: Optional[Path] = None):
        """Restaura o estado do governador do disco (com migração se necessário)."""
        # Aceitar str ou Path
        if isinstance(path, str):
            path = Path(path)
        load_path = path or self._state_path or Path(".mcp_governor_state.json")
        self._state_path = load_path
        if load_path.exists():
            try:
                from tools.schema_migration import load_state_with_migration
                data, _migrated = load_state_with_migration(
                    ".mcp_governor_state.json", load_path.parent
                )
                self.state.iteration_count = data.get("iteration_count", 0)
                self.state.stopped = data.get("stopped", False)
                self.state.stop_reason = data.get("stop_reason", "")
                self.state.no_progress_count = data.get("no_progress_count", 0)
                self.state.budget_used = data.get("budget_used", 0)
                logger.info("Governador: estado restaurado de %s", load_path)
            except Exception as e:
                logger.warning("Governador: erro ao restaurar estado: %s", e)

    def reset(self):
        """Reseta o governador para o estado inicial."""
        self.state = GovernorState()
        logger.info("Governador: estado resetado")


# ── Instância global ─────────────────────────────────────────────────

_governor: Optional[AutonomyGovernor] = None


def get_governor() -> AutonomyGovernor:
    """Retorna instância global do governador (lazy init)."""
    global _governor
    if _governor is None:
        _governor = AutonomyGovernor(
            enabled=True,
            max_iterations=DEFAULT_MAX_ITERATIONS,
            spiral_threshold=DEFAULT_SPIRAL_THRESHOLD,
            no_progress_threshold=DEFAULT_NO_PROGRESS_THRESHOLD,
            budget_calls=DEFAULT_BUDGET_CALLS,
            hard_stop=True,
        )
    return _governor


def set_governor(g: AutonomyGovernor):
    """Permite injetar instância para testes."""
    global _governor
    _governor = g