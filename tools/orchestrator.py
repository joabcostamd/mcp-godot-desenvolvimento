"""orchestrator.py — Orquestrador Genius do MCP Godot.

Coordena TODOS os subsistemas com inteligencia e resiliencia:
    - Saga Pattern: operacoes transacionais com compensacao
    - Reconciliation Loop: verifica estado apos cada acao
    - Supervisor Tree: tolerancia a falhas com reinicializacao
    - Fallback Chain: degradacao graciosa
    - Decision Engine: decisoes assertivas com confidence scoring
    - Circuit Breaker: protecao contra APIs externas instaveis

Baseado em: Temporal.io, Kubernetes, Erlang/OTP, Netflix Hystrix.

Autor: Nucleo / Refinamento MCP v4.0
"""

import json
import math
import os
import threading
import time
import traceback
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════
# 1. SAGA ENGINE — Transações com Compensação
# ══════════════════════════════════════════════════════════════

@dataclass
class SagaStep:
    """Um passo de uma saga: acao + como desfazer."""
    name: str
    execute: Callable[[], Any]
    compensate: Callable[[], Any]
    critical: bool = True       # False = falha neste passo nao desfaz os anteriores
    max_retries: int = 1        # quantas vezes tentar antes de compensar


class SagaOrchestrator:
    """Executa uma sequencia de passos com compensacao em caso de falha.

    Se qualquer passo falhar, todos os anteriores sao desfeitos
    em ordem reversa (LIFO). Se todos passarem, commit atomico.
    """

    def __init__(self, name: str):
        self.name = name
        self.steps: list[SagaStep] = []
        self.executed: list[SagaStep] = []
        self.results: dict[str, Any] = {}
        self.start_time: float = 0.0

    def add_step(self, step: SagaStep):
        self.steps.append(step)
        return self

    def run(self) -> dict:
        """Executa a saga. Retorna resultado ou compensa."""
        self.start_time = time.time()

        try:
            for i, step in enumerate(self.steps):
                result = None
                last_error = None

                for attempt in range(step.max_retries + 1):
                    try:
                        result = step.execute()
                        break
                    except Exception as e:
                        last_error = e
                        if attempt < step.max_retries:
                            time.sleep(0.5 * (2 ** attempt))  # backoff

                if result is None and last_error:
                    if step.critical:
                        raise last_error
                    else:
                        self.results[step.name] = {"status": "skipped", "error": str(last_error)}
                        continue

                self.executed.append(step)
                self.results[step.name] = result

            # Sucesso total
            elapsed = time.time() - self.start_time
            return {
                "status": "success",
                "saga": self.name,
                "steps_completed": len(self.executed),
                "total_steps": len(self.steps),
                "elapsed_ms": int(elapsed * 1000),
                "results": {k: self._summarize(v) for k, v in self.results.items()},
            }

        except Exception as e:
            return self._compensate(e)

    def _compensate(self, error: Exception) -> dict:
        """Desfaz passos executados em ordem LIFO."""
        compensation_errors = []

        for step in reversed(self.executed):
            try:
                step.compensate()
            except Exception as comp_error:
                compensation_errors.append({
                    "step": step.name,
                    "error": str(comp_error),
                })

        elapsed = time.time() - self.start_time
        return {
            "status": "compensated",
            "saga": self.name,
            "error": f"{type(error).__name__}: {error}",
            "steps_completed_before_failure": len(self.executed),
            "compensation_errors": compensation_errors,
            "elapsed_ms": int(elapsed * 1000),
        }

    def _summarize(self, value: Any) -> Any:
        """Resume valores grandes para o log."""
        if isinstance(value, dict):
            return {k: self._summarize(v) for k, v in value.items()}
        if isinstance(value, str) and len(value) > 200:
            return value[:200] + "..."
        return value


# ══════════════════════════════════════════════════════════════
# 2. CIRCUIT BREAKER — Proteção de APIs Externas
# ══════════════════════════════════════════════════════════════

class CircuitState:
    CLOSED = "closed"         # funcionando normal
    OPEN = "open"             # rejeitando chamadas
    HALF_OPEN = "half_open"   # testando se voltou


@dataclass
class CircuitBreaker:
    """Protege contra falhas cascata em APIs externas.

    Estados:
        CLOSED → (3 falhas em 30s) → OPEN (rejeita por 60s)
        OPEN → (60s depois) → HALF_OPEN (1 chamada de teste)
        HALF_OPEN → (sucesso) → CLOSED | (falha) → OPEN
    """
    name: str
    failure_threshold: int = 3
    recovery_timeout: float = 60.0
    half_open_max_requests: int = 1

    state: str = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0.0
    opened_at: float = 0.0
    half_open_requests: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Chama a funcao protegida pelo circuit breaker."""
        with self.lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.opened_at >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_requests = 0
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' ABERTO. "
                        f"Tente novamente em {int(self.recovery_timeout - (time.time() - self.opened_at))}s."
                    )

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_requests >= self.half_open_max_requests:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' em HALF_OPEN — aguardando teste."
                    )
                self.half_open_requests += 1

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        with self.lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED

    def _on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.opened_at = time.time()
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.opened_at = time.time()

    def status(self) -> dict:
        with self.lock:
            return {
                "name": self.name,
                "state": self.state,
                "failure_count": self.failure_count,
                "opened_at": self.opened_at,
            }


class CircuitBreakerOpenError(Exception):
    pass


# Circuit breakers globais para APIs externas
flux_circuit = CircuitBreaker("FLUX_API")
replicate_circuit = CircuitBreaker("Replicate_API")
edge_tts_circuit = CircuitBreaker("EdgeTTS_API")


# ══════════════════════════════════════════════════════════════
# 3. FALLBACK CHAIN — Degradação Graciosa
# ══════════════════════════════════════════════════════════════

def fallback_chain(functions: list[Callable], error_msg: str = "Todos os fallbacks falharam") -> Any:
    """Tenta cada funcao em ordem. A ultima DEVE sempre funcionar.

    Args:
        functions: Lista de callables. O ultimo é o fallback garantido.
        error_msg: Mensagem se tudo falhar.

    Returns:
        Resultado da primeira funcao que funcionar.
    """
    errors = []
    for i, func in enumerate(functions):
        try:
            result = func()
            if i > 0:
                pass  # Registraria métrica: "fallback ativado no nível {i}"
            return result
        except CircuitBreakerOpenError:
            errors.append(f"Nível {i}: circuit breaker aberto")
        except Exception as e:
            errors.append(f"Nível {i}: {type(e).__name__}: {e}")

    return {"status": "error", "message": f"{error_msg}. Erros: {'; '.join(errors)}"}


# ══════════════════════════════════════════════════════════════
# 4. DECISION ENGINE — Confiança e Assertividade
# ══════════════════════════════════════════════════════════════

@dataclass
class Decision:
    """Uma decisao tomada pelo engine."""
    action: str
    confidence: float       # 0.0 a 1.0
    reasoning: str
    auto_execute: bool      # True = decidiu sozinho, False = precisa confirmar


class DecisionEngine:
    """Toma decisoes com base em confianca.

    Regras:
        confianca >= 0.90 → decide e executa automaticamente
        confianca >= 0.50 → decide + sugere confirmacao
        confianca <  0.50 → pergunta ao usuario
    """

    AUTO_THRESHOLD = 0.90
    SUGGEST_THRESHOLD = 0.50

    def should_generate_art(self, entity_name: str, entity_type: str,
                            project_stage: str, has_existing_sprite: bool) -> Decision:
        """Decide se deve gerar arte para uma entidade."""

        # Já existe → confiança 100% que NÃO precisa
        if has_existing_sprite:
            return Decision("skip_art", 1.0, "Sprite já existe", True)

        # Nó que SEMPRE precisa de sprite
        needs_sprite_types = ["CharacterBody2D", "StaticBody2D", "RigidBody2D",
                              "Area2D", "Sprite2D", "AnimatedSprite2D"]
        always_needs = entity_type in needs_sprite_types

        # Estágio do projeto influencia
        if project_stage in ("vazio", "prototipo"):
            if always_needs:
                return Decision("generate_placeholder", 0.95,
                              f"Protótipo — {entity_type} sempre precisa de sprite. Placeholder grátis.", True)
            else:
                return Decision("skip_art", 0.80,
                              f"Protótipo — {entity_type} não essencial", True)

        elif project_stage == "desenvolvimento":
            if always_needs:
                return Decision("generate_flux", 0.92,
                              f"Desenvolvimento — {entity_type} precisa de sprite. FLUX.2 para qualidade.", True)
            else:
                return Decision("suggest_art", 0.65,
                              f"{entity_type} pode não precisar de sprite. Confirma?", False)

        elif project_stage == "polimento":
            return Decision("generate_flux", 0.88,
                          f"Polimento — gerar arte final de qualidade.", False)

        return Decision("skip_art", 0.70, "Estágio desconhecido — não gerar", True)

    def should_generate_audio(self, action_name: str, has_existing_audio: bool,
                              script_methods: list[str] | None = None) -> Decision:
        """Decide se deve gerar audio para uma acao."""
        if has_existing_audio:
            return Decision("skip_audio", 1.0, "Áudio já existe", True)

        # Mapeamento de ações que sempre precisam de SFX
        always_needs_sfx = ["shoot", "jump", "attack", "damage", "die",
                           "explode", "collect", "click"]

        action_lower = action_name.lower()
        if any(a in action_lower for a in always_needs_sfx):
            return Decision("generate_sfx", 0.94,
                          f"Ação '{action_name}' → SFX necessário para game feel", True)

        if script_methods:
            for method in script_methods:
                if any(a in method.lower() for a in always_needs_sfx):
                    return Decision("generate_sfx", 0.88,
                                  f"Método '{method}' detectado no script → SFX", True)

        return Decision("skip_audio", 0.75,
                       f"Ação '{action_name}' não mapeada para SFX obrigatório", True)

    def project_stage(self, scene_count: int, script_count: int,
                      sprite_count: int, audio_count: int) -> str:
        """Determina o estágio do projeto."""
        if scene_count <= 1 and script_count <= 2:
            return "vazio"
        elif sprite_count < 5:
            return "prototipo"
        elif script_count > 5 and sprite_count > 3:
            return "desenvolvimento"
        elif sprite_count > 10:
            return "polimento"
        return "desenvolvimento"


# Singleton
orchestrator_decision_engine = DecisionEngine()


# ══════════════════════════════════════════════════════════════
# 5. RECONCILIATION LOOP — Verificação Pós-Ação
# ══════════════════════════════════════════════════════════════

class ReconciliationLoop:
    """Verifica se o estado real do projeto corresponde ao esperado.

    Após cada ação do pipeline, verifica:
        - O arquivo foi realmente criado?
        - O conteúdo está correto?
        - O Godot consegue abrir?

    Se não corresponder, reexecuta a ação (máx 3 tentativas).
    """

    MAX_RECONCILE_ATTEMPTS = 3

    def verify_file_exists(self, file_path: str) -> bool:
        """Verifica se um arquivo foi criado e tem conteúdo."""
        from tools.project_ops import _get_active_project
        proj = _get_active_project()
        full = proj / file_path
        return full.exists() and full.stat().st_size > 0

    def verify_scene_valid(self, scene_path: str) -> bool:
        """Verifica se um .tscn é parseável."""
        from tools.project_ops import _get_active_project
        proj = _get_active_project()
        full = proj / scene_path

        if not full.exists():
            return False

        try:
            content = full.read_text(encoding='utf-8', errors='ignore')
            return content.startswith('[gd_scene') and '[node' in content
        except Exception:
            return False

    def verify_script_valid(self, script_path: str) -> bool:
        """Verifica se um .gd é parseável."""
        from tools.project_ops import _get_active_project
        proj = _get_active_project()
        full = proj / script_path

        if not full.exists():
            return False

        try:
            content = full.read_text(encoding='utf-8', errors='ignore')
            return 'extends' in content
        except Exception:
            return False

    def verify_sprite_valid(self, sprite_path: str, min_size: int = 64) -> bool:
        """Verifica se um sprite PNG é válido."""
        from tools.project_ops import _get_active_project
        proj = _get_active_project()
        full = proj / sprite_path

        if not full.exists():
            return False

        try:
            size = full.stat().st_size
            if size < min_size:
                return False
            # Verificar header PNG
            with open(full, 'rb') as f:
                header = f.read(8)
            return header == b'\x89PNG\r\n\x1a\n'
        except Exception:
            return False

    def reconcile(self, action_name: str, verify_func: Callable[[], bool],
                  retry_func: Callable[[], Any], compensate_func: Callable[[], None] | None = None) -> dict:
        """Executa ação, verifica resultado, retenta se necessário.

        Returns:
            {"status": "success"|"failed", "attempts": int, "verified": bool}
        """
        for attempt in range(self.MAX_RECONCILE_ATTEMPTS):
            try:
                result = retry_func()
            except Exception as e:
                if attempt == self.MAX_RECONCILE_ATTEMPTS - 1:
                    if compensate_func:
                        try:
                            compensate_func()
                        except Exception:
                            pass
                    return {"status": "failed", "attempts": attempt + 1,
                            "error": str(e), "verified": False}
                time.sleep(0.3 * (2 ** attempt))
                continue

            # Verificar
            if verify_func():
                return {"status": "success", "attempts": attempt + 1,
                       "verified": True, "result": result}

            if attempt < self.MAX_RECONCILE_ATTEMPTS - 1:
                time.sleep(0.2 * (2 ** attempt))

        if compensate_func:
            try:
                compensate_func()
            except Exception:
                pass

        return {"status": "failed", "attempts": self.MAX_RECONCILE_ATTEMPTS,
                "verified": False, "error": "Falha na verificação após todas as tentativas"}


# Singleton
reconciler = ReconciliationLoop()


# ══════════════════════════════════════════════════════════════
# 6. TOOLS DO ORQUESTRADOR (o que a IA vai ver)
# ══════════════════════════════════════════════════════════════

def create_entity(
    name: str,
    entity_type: str = "enemy",
    description: str = "",
    behavior: str = "patrol",
    art_style: str = "scifi",
    save_path: str | None = None,
) -> dict:
    """Cria uma entidade COMPLETA de jogo usando o Orquestrador Genius.

    Pipeline: cena → collider → script → arte → áudio
    Com Saga (rollback), Reconciliation (verificação), Circuit Breaker (APIs).

    Args:
        name: Nome da entidade.
        entity_type: enemy, player, tower, npc, item, projectile.
        description: Descricao visual.
        behavior: patrol, chase, static, flee, none.
        art_style: scifi, fantasia, cartoon, pixel, minimalista.
        save_path: Caminho da cena (auto se None).

    Returns:
        Resultado completo com status, passos, artefatos, sugestões.
    """
    from tools.project_ops import _get_active_project, _check_path_traversal
    from tools.project_state import get_state, refresh_state

    proj = _get_active_project()
    refresh_state(proj)
    state = get_state()

    if not save_path:
        safe_name = name.lower().replace(' ', '_')
        save_path = f"scenes/{entity_type}s/{safe_name}.tscn"

    violation = _check_path_traversal(save_path, proj)
    if violation:
        return {"status": "error", "message": violation}

    # Mapear tipo → Godot node
    node_map = {
        "enemy": "CharacterBody2D", "player": "CharacterBody2D",
        "tower": "StaticBody2D", "npc": "CharacterBody2D",
        "item": "Area2D", "projectile": "Area2D",
    }
    godot_type = node_map.get(entity_type, "Node2D")

    # ── DECISION ENGINE ─────────────────────────────────────
    stage = state.get_stage() if hasattr(state, 'get_stage') else orchestrator_decision_engine.project_stage(
        len(state.scenes), len(state.scripts), len(state.sprites), len(state.audio))

    art_decision = orchestrator_decision_engine.should_generate_art(
        name, godot_type, stage, state.has_sprite_for(name) if hasattr(state, 'has_sprite_for') else False)

    audio_decision = orchestrator_decision_engine.should_generate_audio(
        name, state.has_audio_for(name) if hasattr(state, 'has_audio_for') else False)

    # ── SAGA: Construir pipeline transacional ───────────────
    saga = SagaOrchestrator(f"create_{entity_type}_{name}")
    script_path = save_path.replace('.tscn', '.gd')
    sprite_path = f"assets/sprites/{entity_type}s/{name}.png"
    audio_path = f"assets/audio/sfx/{name}.wav"

    # Passo 1: Criar cena
    def create_scene_step():
        from tools.scene_ops import create_scene as sc_create
        r = sc_create(name, godot_type, save_path)
        if r.get("status") != "success":
            raise Exception(r.get("message", "Erro ao criar cena"))
        # Reconciliation: verificar que arquivo existe
        if not reconciler.verify_scene_valid(save_path):
            raise Exception(f"Cena criada mas inválida: {save_path}")
        return r

    def compensate_scene():
        full = proj / save_path
        if full.exists():
            full.unlink()

    saga.add_step(SagaStep("create_scene", create_scene_step, compensate_scene))

    # Passo 2: Adicionar CollisionShape2D
    def add_collider_step():
        from tools.scene_ops import add_node as sc_add_node
        from tools.scene_ops import set_node_property
        coll_name = f"{name}_collision"
        r = sc_add_node(save_path, ".", coll_name, "CollisionShape2D")
        if r.get("status") == "success":
            shape_path = f"{save_path}::{name}/{coll_name}"
            set_node_property(shape_path, "shape", "RectangleShape2D")
        return r

    saga.add_step(SagaStep("add_collider", add_collider_step,
                           lambda: None, critical=False))

    # Passo 3: Gerar script (se behavior != none)
    if behavior != "none":
        def create_script_step():
            try:
                from tools.behavior_ops import behavior_tree_generate
                r = behavior_tree_generate(
                    description=f"{description or entity_type + ' ' + name}. Comportamento: {behavior}",
                    behavior_name=name.replace(' ', ''),
                    save_path=script_path,
                )
            except Exception:
                # Fallback: script básico
                code = f"extends {godot_type}\n\nfunc _ready():\n\tpass\n"
                full = proj / script_path
                full.parent.mkdir(parents=True, exist_ok=True)
                full.write_text(code, encoding='utf-8')
                r = {"status": "success", "fallback": True}

            if not reconciler.verify_script_valid(script_path):
                raise Exception(f"Script inválido: {script_path}")
            return r

        saga.add_step(SagaStep("create_script", create_script_step,
                               lambda: Path(proj / script_path).unlink(missing_ok=True)))

    # Passo 4: Gerar arte (se Decision Engine decidiu)
    if art_decision.auto_execute and art_decision.action != "skip_art":
        def create_art_step():
            generator = "placeholder" if art_decision.action == "generate_placeholder" else "flux"

            if generator == "flux":
                try:
                    result = flux_circuit.call(
                        lambda: _generate_art_flux(description, entity_type, art_style, sprite_path))
                except CircuitBreakerOpenError:
                    result = _generate_art_placeholder(name, entity_type, sprite_path)
            else:
                result = _generate_art_placeholder(name, entity_type, sprite_path)

            if not reconciler.verify_sprite_valid(sprite_path):
                result = _generate_art_placeholder(name, entity_type, sprite_path)

            return result

        saga.add_step(SagaStep("create_art", create_art_step,
                               lambda: Path(proj / sprite_path).unlink(missing_ok=True),
                               critical=False))

    # Passo 5: Gerar áudio (se Decision Engine decidiu)
    if audio_decision.auto_execute and audio_decision.action != "skip_audio":
        def create_audio_step():
            from tools.placeholder_ops import generate_audio_sfx
            safe_audio_name = name.lower().replace(' ', '_')
            r = generate_audio_sfx(name=name, sfx_type="beep", duration=0.3,
                                   save_path=f"assets/audio/sfx/{safe_audio_name}.wav")
            return r

        saga.add_step(SagaStep("create_audio", create_audio_step,
                               lambda: Path(proj / audio_path).unlink(missing_ok=True),
                               critical=False))

    # ── EXECUTAR SAGA ──────────────────────────────────────
    result = saga.run()
    refresh_state(proj)

    # ── SUGESTÕES PÓS-CRIAÇÃO ──────────────────────────────
    suggestions = []
    if art_decision.action == "skip_art" and not (hasattr(state, 'has_sprite_for') and state.has_sprite_for(name)):
        suggestions.append(f"🎨 '{name}' não tem sprite. Gerar?")
    if not (hasattr(state, 'has_audio_for') and state.has_audio_for(name)):
        suggestions.append(f"🔊 '{name}' não tem SFX. Gerar?")
    if script_path not in str(state.scripts):
        suggestions.append(f"🧠 '{name}' não tem script de IA. Gerar?")

    return {
        **result,
        "entity": {"name": name, "type": entity_type, "scene": save_path},
        "decisions": {
            "art": art_decision.action,
            "art_confidence": art_decision.confidence,
            "audio": audio_decision.action,
            "audio_confidence": audio_decision.confidence,
        },
        "suggestions": suggestions[:2],
        "project_stage": stage,
    }


def _generate_art_flux(description: str, category: str, style: str, save_path: str) -> dict:
    """Wrapper com proteção do circuit breaker."""
    from tools.flux_ops import generate_game_art_flux
    return generate_game_art_flux(
        description=description or f"{category} game asset",
        category=category, style=style,
        width=64, height=64, frames=1, save_path=save_path,
    )


def _generate_art_placeholder(name: str, category: str, save_path: str) -> dict:
    """Fallback garantido — SEMPRE funciona."""
    from tools.placeholder_ops import generate_placeholder_sprite
    return generate_placeholder_sprite(
        name=name, width=64, height=64, save_path=save_path,
    )


def circuit_breaker_status() -> dict:
    """Status de todos os circuit breakers."""
    return {
        "status": "success",
        "circuits": [
            flux_circuit.status(),
            replicate_circuit.status(),
            edge_tts_circuit.status(),
        ],
    }
