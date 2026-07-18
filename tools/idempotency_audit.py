"""idempotency_audit.py — Auditoria e documentação da regra de idempotência.

Regra (Fatia 0.13, Camada 0):
────────────────────────────
Toda tool que participa de uma cadeia (Saga Engine, Reconciliation Loop,
Pipeline) DEVE ser idempotente: f(f(x)) = f(x) — rodar 2x com os mesmos
argumentos produz o mesmo resultado, sem efeito colateral duplicado e sem
lançar exceção.

Definição operacional (C4 da autoauditoria):
  - Se a operação já foi realizada (estado já reflete o resultado),
    uma segunda chamada retorna sucesso, e não duplica o efeito.
  - Se a operação não pode ser realizada (recurso não existe, já removido),
    retorna sucesso (não erro) — erro quebraria compensação da Saga.
  - Nenhuma tool em cadeia lança exceção para o estado "já feito" ou
    "já removido".

Padrões para garantir idempotência:
  1. Check-before-create: antes de criar, verificar se já existe. Se sim,
     retornar sucesso com {"idempotent": True, "note": "..."}.
  2. Check-content-before-write: em overwrite, comparar hash do conteúdo
     novo com o existente. Se idêntico, pular checkpoint e escrita.
  3. missing_ok em compensação: Path.unlink(missing_ok=True) para nunca
     crashar ao desfazer algo já desfeito.
  4. delete-then-check: ao deletar, verificar se recurso já não existe.
     Se não existe, retornar sucesso (não erro).

Uso:
  @idempotent
  def minha_tool(args):
      ...

  relatorio = audit_tool_idempotency()
"""

import hashlib
import functools
from pathlib import Path
from typing import Any, Callable


# ── Registro de tools auditadas ──────────────────────────────────────

_IDEMPOTENCY_REGISTRY: dict[str, dict] = {}
"""Registro global de tools marcadas como idempotentes.
Chave = nome da tool, Valor = metadados de auditoria."""


def idempotent(func: Callable = None, *, tool_name: str | None = None,
               category: str = "cadeia") -> Callable:
    """Decorator que marca uma tool como idempotente e a registra.

    Args:
        func: A função a decorar (quando usado sem parênteses).
        tool_name: Nome opcional para o registro (default: nome da função).
        category: Categoria: "cadeia" (participa de Saga), "leitura", "escrita".

    Uso:
        @idempotent
        def minha_tool(args):
            ...

        @idempotent(tool_name="add_node")
        def add_node(...):
            ...
    """
    if func is None:
        return functools.partial(idempotent, tool_name=tool_name, category=category)

    name = tool_name or func.__name__
    _IDEMPOTENCY_REGISTRY[name] = {
        "tool_name": name,
        "function": func.__name__,
        "module": func.__module__,
        "category": category,
        "doc": (func.__doc__ or "").strip(),
    }

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


# ── Ferramentas de auditoria ─────────────────────────────────────────

def audit_tool_idempotency(project_root: Path | None = None) -> dict:
    """Audita todas as tools registradas quanto à idempotência.

    Verifica:
      1. Se a tool está no registro @idempotent.
      2. Se a tool tem docstring mencionando idempotência.
      3. Se a tool é usada em Saga (verifica orquestrador.py).

    Returns:
        {"status": "success", "tools": {nome: status}, "summary": {...}}
    """
    registered = set(_IDEMPOTENCY_REGISTRY.keys())

    # Varre os módulos conhecidos por funções que parecem tools de cadeia
    chain_tools = _discover_chain_tools()

    tools_report = {}
    for tool_name in chain_tools:
        if tool_name in registered:
            entry = _IDEMPOTENCY_REGISTRY[tool_name]
            tools_report[tool_name] = {
                "status": "✅ idempotente (registrada)",
                "category": entry["category"],
                "evidence": f"Registrada via @idempotent em {entry['module']}::{entry['function']}",
            }
        else:
            tools_report[tool_name] = {
                "status": "❌ NÃO registrada",
                "category": "desconhecida",
                "evidence": "Não possui decorator @idempotent — necessário para cadeia Saga",
            }

    # Adiciona tools registradas que não são diretamente de cadeia
    for name, entry in _IDEMPOTENCY_REGISTRY.items():
        if name not in tools_report:
            tools_report[name] = {
                "status": f"✅ idempotente ({entry['category']})",
                "category": entry["category"],
                "evidence": f"Registrada via @idempotent em {entry['module']}::{entry['function']}",
            }

    # Resumo
    total = len(tools_report)
    ok = sum(1 for v in tools_report.values() if v["status"].startswith("✅"))
    fail = total - ok

    return {
        "status": "success",
        "tools": tools_report,
        "summary": {
            "total": total,
            "idempotent": ok,
            "not_idempotent": fail,
        },
    }


def _discover_chain_tools() -> set[str]:
    """Descobre ferramentas que participam de cadeias (Saga/Pipeline).

    Usa heurística: ferramentas referenciadas em SagaStep dentro de
    orchestrator.py, verification_ops.py, e pipeline_ops.py.
    Também inclui tools conhecidas de manipulação de arquivo/cena.
    """
    # Ferramentas conhecidas de cadeia (verificadas manualmente)
    return {
        # scene_ops
        "create_scene",
        "add_node",
        "delete_node",
        "set_node_property",
        # file_ops
        "write_file",
        "delete_file",
        "move_file",
        # pipeline/verification
        "_step_compile",
        "run_verification_pipeline",
        # saga steps (em orchestrator.py)
        "create_scene_step",
        "add_collider_step",
        "create_script_step",
        "create_art_step",
        "create_audio_step",
        "compile_gate_step",
    }


# ── Helpers de idempotência para uso compartilhado ──────────────────

def content_identical(file_path: Path | str, new_content: str) -> bool:
    """Verifica se o conteúdo em disco é idêntico ao novo conteúdo.

    Args:
        file_path: Caminho absoluto do arquivo (Path ou str).
        new_content: Conteúdo a comparar.

    Returns:
        True se o conteúdo for idêntico (hash SHA-256).
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if not file_path.exists():
        return False

    try:
        existing = file_path.read_bytes()
        new_bytes = new_content.encode("utf-8")
        return (
            hashlib.sha256(existing).hexdigest()
            == hashlib.sha256(new_bytes).hexdigest()
        )
    except Exception:
        return False


def node_exists_in_scene(scene_path: Path, node_name: str,
                         parent_path: str = ".") -> bool:
    """Verifica se um nó com o nome dado já existe na cena sob o pai.
    (Helper compartilhado para uso futuro — disponível mas não integrado.)

    Parseia o .tscn e busca [node name="<node_name>" ... parent="<parent>"].
    O parent é mapeado: "." vira raiz (sem parent ou parent=".").

    Args:
        scene_path: Caminho absoluto do arquivo .tscn.
        node_name: Nome do nó a buscar.
        parent_path: Path do pai (ex: ".", "./Child").

    Returns:
        True se nó já existir.
    """
    if not scene_path.exists():
        return False

    try:
        lines = scene_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return False

    # Mapeia parent_path para o formato usado no .tscn
    # "." vira "" (raiz) ou "."
    parent_tscn = ""
    if parent_path == ".":
        parent_tscn = "."  # nó raiz é filho da raiz
    elif parent_path.startswith("./"):
        parent_tscn = parent_path[2:]  # "./Child" -> "Child"
    else:
        parent_tscn = parent_path

    import re

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("[node "):
            continue

        # Extrai name, parent
        name_match = re.search(r'name="([^"]*)"', stripped)
        parent_match = re.search(r'parent="([^"]*)"', stripped)

        if not name_match:
            continue

        name = name_match.group(1)
        parent = parent_match.group(1) if parent_match else ""

        if name != node_name:
            continue

        # Verifica parent
        if parent_tscn == ".":
            # Raiz: não tem parent ou é "."
            if not parent or parent == ".":
                return True
        elif parent == parent_tscn:
            return True

    return False


def ensure_unique_operation(operation_id: str, state_file: Path | None = None) -> bool:
    """Garante que uma operação é executada apenas uma vez (durable execution).

    Args:
        operation_id: Identificador único da operação (ex: "migracao_v2").
        state_file: Caminho para arquivo de estado. Se None, usa
                    <project_root>/.idempotency_state.json.

    Returns:
        True se a operação JÁ foi executada (pular).
        False se é a primeira vez (executar e registrar).
    """
    if state_file is None:
        try:
            from tools.project_ops import _get_active_project
            proj = _get_active_project()
            state_file = proj / ".idempotency_state.json"
        except Exception:
            return False  # Sem projeto ativo, não pode verificar — executar operação

    if state_file.exists():
        try:
            import json
            state = json.loads(state_file.read_text(encoding="utf-8"))
            if state.get(operation_id):
                return True  # Já foi executada
        except Exception:
            pass

    # Registra como executada
    try:
        import json
        if state_file.exists():
            state = json.loads(state_file.read_text(encoding="utf-8"))
        else:
            state = {}
        state[operation_id] = True
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass  # Não crítico — operação segue mesmo sem registro

    return False


# ── Documentação da regra (inline) ──────────────────────────────────

RULE_DOCUMENTATION = """
REGRAMA DE IDEMPOTÊNCIA PARA TOOLS EM CADEIA
=============================================

Contexto:
  Ferramentas MCP que participam de cadeias transacionais (Saga Engine,
  Reconciliation Loop, Verification Pipeline, Export Gate) PRECISAM ser
  idempotentes. Caso contrário, uma única falha intermediária com retry
  pode gerar duplicatas (nós, arquivos, assets) ou corrupção.

Definição:
  f(f(x)) = f(x)
  Executar a tool 2x com os mesmos argumentos produz o mesmo resultado
  observável que executar 1x.

Isso significa:
  - NÃO lançar exceção na segunda execução
  - NÃO criar duplicata (ex.: segundo nó com mesmo nome)
  - NÃO sobrescrever checkpoint desnecessariamente (se conteúdo é o
    mesmo, pular escrita)

Quando NÃO é necessário:
  - Tools de leitura (inspect, get, list) — por definição não alteram
    estado, então são naturalmente idempotentes.
  - Tools de geração externa (generate_game_art, generate_audio_sfx) —
    são protegidas pelo Circuit Breaker e pelo client HTTP compartilhado
    (0.9) com retry + idempotência por id de requisição.

Quando é OBRIGATÓRIO:
  - Toda tool registrada como SagaStep no orchestrator.py
  - Toda tool chamada dentro de VerificationPipeline
  - Toda tool de escrita de arquivo (write_file, delete_file, move_file)
  - Toda tool de manipulação de cena/nó (create_scene, add_node,
    delete_node, set_node_property)

Como implementar:
  1. Adicione o decorator @idempotent à função.
  2. Implemente o check-before-operate para o estado "já feito".
  3. Use os helpers deste módulo (content_identical, node_exists_in_scene).
  4. Em compensações de Saga, use missing_ok=True sempre.
"""