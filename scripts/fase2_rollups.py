#!/usr/bin/env python3
"""
FASE 2 — Rollups Adicionais: colapsa 10 atômicas → 5 _manage rollups

Pares:
  1. workflow_snapshot + workflow_handoff → workflow_manage
  2. configure_security + security_status → security_manage
  3. get_audit_log + get_audit_replay → audit_manage
  4. start_recording + stop_recording → recording_manage
  5. vibe_coding_mode + get_vibe_context → vibe_manage
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ── Definição dos 5 rollups ──────────────────────────────────────
ROLLUPS = [
    {
        "name": "workflow_manage",
        "description": "Gerencia workflow: snapshot do estado atual e handoff para proxima sessao.",
        "ops": {
            "snapshot": ("tools.workflow_ops", "workflow_snapshot"),
            "handoff": ("tools.workflow_ops", "workflow_handoff"),
        },
        "namespace": "orchestration",
        "phase": "POLIMENTO",
        "hints": {"destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
        "title": "Workflow",
        "tags": ["workflow", "handoff", "snapshot"],
        "atomics": ["workflow_snapshot", "workflow_handoff"],
    },
    {
        "name": "security_manage",
        "description": "Gerencia seguranca: configura token e verifica status de seguranca.",
        "ops": {
            "configure": ("tools.security_ops", "configure_security"),
            "status": ("tools.security_ops", "security_status"),
        },
        "namespace": "orchestration",
        "phase": "POLIMENTO",
        "hints": {"destructiveHint": True, "idempotentHint": False, "openWorldHint": False},
        "title": "Seguranca",
        "tags": ["seguranca", "token", "config"],
        "atomics": ["configure_security", "security_status"],
    },
    {
        "name": "audit_manage",
        "description": "Gerencia auditoria: historico (log) e replay de acoes da IA.",
        "ops": {
            "log": ("tools.safety_policy", "get_audit_log"),
            "replay": ("tools.safety_policy", "get_audit_replay"),
        },
        "namespace": "orchestration",
        "phase": "POLIMENTO",
        "hints": {"destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
        "title": "Auditoria",
        "tags": ["auditoria", "log", "replay"],
        "atomics": ["get_audit_log", "get_audit_replay"],
    },
    {
        "name": "recording_manage",
        "description": "Gerencia gravacao: inicia e para gravacao de sessoes de jogo.",
        "ops": {
            "start": ("tools.recording_ops", "start_recording"),
            "stop": ("tools.recording_ops", "stop_recording"),
        },
        "namespace": "runtime",
        "phase": "POLIMENTO",
        "hints": {"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        "title": "Gravacao",
        "tags": ["recording", "gravacao", "sessao"],
        "atomics": ["start_recording", "stop_recording"],
    },
    {
        "name": "vibe_manage",
        "description": "Gerencia Vibe Coding Mode: ativa/desativa e consulta contexto atual.",
        "ops": {
            "enable": ("tools.vibe_ops", "vibe_coding_mode"),
            "context": ("tools.vibe_ops", "get_vibe_context"),
        },
        "namespace": "orchestration",
        "phase": "POLIMENTO",
        "hints": {"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        "title": "Vibe Coding",
        "tags": ["vibe", "contexto", "modo"],
        "atomics": ["vibe_coding_mode", "get_vibe_context"],
    },
]

# Todas as 10 atômicas
ALL_ATOMICS = [a for r in ROLLUPS for a in r["atomics"]]

# ── PASSO 1: Adicionar builders em tools/rollups.py ──────────────
def patch_rollups():
    path = ROOT / "tools" / "rollups.py"
    original = path.read_text(encoding="utf-8")

    # 1a. Adicionar imports das funções
    import_block = """
# ── FASE 2 (Rollups adicionais) ─────────────────────────────────
from tools.workflow_ops import workflow_snapshot, workflow_handoff
from tools.security_ops import configure_security, security_status
from tools.safety_policy import get_audit_log, get_audit_replay
from tools.recording_ops import start_recording, stop_recording
from tools.vibe_ops import vibe_coding_mode, get_vibe_context
"""
    # Adiciona após o último import existente (antes de _ROLLUP_BUILDERS)
    text = original.replace(
        "\n\n# ── Builders registry",
        import_block + "\n# ── Builders registry"
    )

    # 1b. Adicionar builders
    builder_code = """
# ── FASE 2 (Rollups adicionais — colapso de atômicas) ────────────

def _build_workflow_manage():
    \"\"\"workflow_snapshot + workflow_handoff → workflow_manage\"\"\"
    return create_manage_tool(
        tool_name="workflow_manage",
        description="Gerencia workflow: snapshot do estado atual e handoff para proxima sessao.",
        ops={
            "snapshot": workflow_snapshot,
            "handoff": workflow_handoff,
        },
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
        title="Workflow",
        tags=["workflow", "handoff", "snapshot"],
    )


def _build_security_manage():
    \"\"\"configure_security + security_status → security_manage\"\"\"
    return create_manage_tool(
        tool_name="security_manage",
        description="Gerencia seguranca: configura token e verifica status de seguranca.",
        ops={
            "configure": configure_security,
            "status": security_status,
        },
        tool_hints={"destructiveHint": True, "idempotentHint": False, "openWorldHint": False},
        title="Seguranca",
        tags=["seguranca", "token", "config"],
    )


def _build_audit_manage():
    \"\"\"get_audit_log + get_audit_replay → audit_manage\"\"\"
    return create_manage_tool(
        tool_name="audit_manage",
        description="Gerencia auditoria: historico (log) e replay de acoes da IA.",
        ops={
            "log": get_audit_log,
            "replay": get_audit_replay,
        },
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
        title="Auditoria",
        tags=["auditoria", "log", "replay"],
    )


def _build_recording_manage():
    \"\"\"start_recording + stop_recording → recording_manage\"\"\"
    return create_manage_tool(
        tool_name="recording_manage",
        description="Gerencia gravacao: inicia e para gravacao de sessoes de jogo.",
        ops={
            "start": start_recording,
            "stop": stop_recording,
        },
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        title="Gravacao",
        tags=["recording", "gravacao", "sessao"],
    )


def _build_vibe_manage():
    \"\"\"vibe_coding_mode + get_vibe_context → vibe_manage\"\"\"
    return create_manage_tool(
        tool_name="vibe_manage",
        description="Gerencia Vibe Coding Mode: ativa/desativa e consulta contexto atual.",
        ops={
            "enable": vibe_coding_mode,
            "context": get_vibe_context,
        },
        tool_hints={"destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
        title="Vibe Coding",
        tags=["vibe", "contexto", "modo"],
    )
"""

    # Adiciona antes de _ROLLUP_BUILDERS
    text = text.replace(
        "\n\n_ROLLUP_BUILDERS = [",
        builder_code + "\n\n_ROLLUP_BUILDERS = ["
    )

    # 1c. Registrar builders no _ROLLUP_BUILDERS
    new_builders = """    # FASE 2: Rollups adicionais (10 atômicas → 5 rollups)
    _build_workflow_manage,
    _build_security_manage,
    _build_audit_manage,
    _build_recording_manage,
    _build_vibe_manage,
"""
    # Adiciona antes do último builder
    text = text.replace(
        "    # ONDA 3: budget_manage (migrado)\n    _build_budget_manage,",
        "    # ONDA 3: budget_manage (migrado)\n    _build_budget_manage,\n" + new_builders
    )

    path.write_text(text, encoding="utf-8")
    print("  ✅ tools/rollups.py: 5 builders adicionados + registrados")


# ── PASSO 2: Atualizar core/legacy_data.py ──────────────────────
def patch_legacy_data():
    path = ROOT / "core" / "legacy_data.py"
    original = path.read_text(encoding="utf-8")
    text = original

    # 2a. Adicionar novos rollups aos namespaces
    ns_additions = {
        "orchestration": ["workflow_manage", "security_manage", "audit_manage", "vibe_manage"],
        "runtime": ["recording_manage"],
    }

    for ns, tools in ns_additions.items():
        for tool in tools:
            # Encontra o namespace e adiciona antes do fechamento ]
            ns_pattern = rf'("{ns}":\s*\[)'
            # Adiciona após o último item do namespace
            # Abordagem mais simples: adicionar após "budget_manage" ou similar
            pass

    # Abordagem manual: adicionar os 5 novos nomes em posições específicas
    # workflow_manage, security_manage, audit_manage, vibe_manage → orchestration
    # recording_manage → runtime

    # orchestration: adicionar após o último item antes de ],
    text = text.replace(
        '"polish_manage",\n    ],',
        '"polish_manage",\n        # FASE 2: Rollups adicionais\n        "workflow_manage", "security_manage", "audit_manage", "vibe_manage",\n    ],'
    )

    # runtime: adicionar após o último item antes de ],
    text = text.replace(
        '"runtime_connect_signal",\n        "runtime_disconnect_signal",\n        "runtime_emit_signal",\n],',
        '"runtime_connect_signal",\n        "runtime_disconnect_signal",\n        "runtime_emit_signal",\n        # FASE 2: Rollup recording\n        "recording_manage",\n],'
    )

    # 2b. Remover as 10 atômicas de TOOLSETS e PHASE_TOOLSETS
    for tool in ALL_ATOMICS:
        patterns = [
            rf'"\s*{re.escape(tool)}\s*"\s*,\s*',
            rf',\s*"\s*{re.escape(tool)}\s*"',
        ]
        for pat in patterns:
            text = re.sub(pat, "", text)

    # Limpar vírgulas duplas
    text = re.sub(r',\s*,', ',', text)

    # 2c. Adicionar novos rollups às fases (POLIMENTO)
    text = text.replace(
        '"POLIMENTO": {\n',
        '"POLIMENTO": {\n        # FASE 2: Rollups adicionais\n        "workflow_manage", "security_manage", "audit_manage", "recording_manage", "vibe_manage",\n'
    )

    path.write_text(text, encoding="utf-8")
    print("  ✅ core/legacy_data.py: 10 atômicas removidas, 5 rollups adicionados")


# ── PASSO 3: Atualizar tools/deprecated.py ──────────────────────
def patch_deprecated():
    path = ROOT / "tools" / "deprecated.py"
    original = path.read_text(encoding="utf-8")
    text = original

    # 3a. Adicionar atômicas a DEPRECATED_TOOLS
    new_entries = ",\n    ".join(f'"{t}"' for t in ALL_ATOMICS)
    text = text.replace(
        'DEPRECATED_TOOLS: set[str] = {',
        f'DEPRECATED_TOOLS: set[str] = {{\n    # FASE 2: Atômicas colapsadas em rollups\n    {new_entries},'
    )

    # 3b. Adicionar aliases
    alias_entries = []
    for rollup in ROLLUPS:
        for atomic in rollup["atomics"]:
            # Encontra qual op corresponde a esta atômica
            op_name = None
            for op, (mod, func) in rollup["ops"].items():
                if func == atomic:
                    op_name = op
                    break
            alias_entries.append(f'    "{atomic}": ("{rollup["name"]}", "{op_name}"),')

    alias_block = "\n".join(alias_entries)
    text = text.replace(
        'ALIAS_MAP: dict[str, tuple[str, str]] = {',
        f'ALIAS_MAP: dict[str, tuple[str, str]] = {{\n    # FASE 2: Aliases para rollups\n{alias_block}'
    )

    path.write_text(text, encoding="utf-8")
    print("  ✅ tools/deprecated.py: 10 atômicas depreciadas + 10 aliases")


# ── PASSO 4: Remover atômicas de core/tool_definitions.py ──────
def patch_tool_definitions():
    path = ROOT / "core" / "tool_definitions.py"
    original = path.read_text(encoding="utf-8")
    lines = original.split("\n")

    removed = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^(\s*)Tool\($', line)
        if m:
            indent = m.group(1)
            if i + 1 < len(lines):
                name_match = re.match(rf'^{indent}\s+name="(\w+)"', lines[i + 1])
                if name_match:
                    tool_name = name_match.group(1)
                    if tool_name in ALL_ATOMICS:
                        # Encontrar fechamento
                        start = i
                        j = i
                        depth = 0
                        found_start = False
                        while j < len(lines):
                            l = lines[j]
                            for ch in l:
                                if ch == '(':
                                    depth += 1
                                    found_start = True
                                elif ch == ')':
                                    depth -= 1
                            if found_start and depth == 0:
                                break
                            j += 1
                        end = j
                        removed.add(tool_name)
                        i = end + 1
                        continue
        i += 1

    # Remover blocos (de trás pra frente)
    new_lines = lines.copy()
    # Precisamos reencontrar
    i = 0
    blocks_to_remove = []
    while i < len(new_lines):
        line = new_lines[i]
        m = re.match(r'^(\s*)Tool\($', line)
        if m:
            indent = m.group(1)
            if i + 1 < len(new_lines):
                name_match = re.match(rf'^{indent}\s+name="(\w+)"', new_lines[i + 1])
                if name_match and name_match.group(1) in ALL_ATOMICS:
                    tool_name = name_match.group(1)
                    start = i
                    j = i
                    depth = 0
                    found_start = False
                    while j < len(new_lines):
                        l = new_lines[j]
                        for ch in l:
                            if ch == '(':
                                depth += 1
                                found_start = True
                            elif ch == ')':
                                depth -= 1
                        if found_start and depth == 0:
                            break
                        j += 1
                    blocks_to_remove.append((start, j))
                    i = j + 1
                    continue
        i += 1

    for start, end in sorted(blocks_to_remove, key=lambda x: -x[0]):
        del new_lines[start:end + 1]

    new_text = "\n".join(new_lines)
    path.write_text(new_text, encoding="utf-8")
    print(f"  ✅ core/tool_definitions.py: {len(ALL_ATOMICS)}/10 atômicas removidas")


# ── PASSO 5: Remover handlers de server.py ──────────────────────
def patch_server():
    path = ROOT / "server.py"
    original = path.read_text(encoding="utf-8")
    text = original

    # 5a. Remover registros de handler no dicionário
    for tool in ALL_ATOMICS:
        pat = rf'^\s*"{re.escape(tool)}":\s*_\w+,\s*$\n'
        text = re.sub(pat, "", text, flags=re.MULTILINE)

    # 5b. Remover funções _handle_*
    handler_names = [f"_handle_{t}" for t in ALL_ATOMICS]
    for hname in handler_names:
        pattern = rf'def {hname}\(args: dict\) -> dict:.*?(?=\n    def |\n\n\S|\n# ──|\Z)'
        match = re.search(pattern, text, flags=re.DOTALL)
        if match:
            end_pos = match.end()
            while end_pos < len(text) and text[end_pos] == '\n':
                end_pos += 1
            text = text[:match.start()] + text[end_pos:]

    # 5c. Limpar imports
    import_cleanups = [
        (r'from tools\.workflow_ops import \(?\s*workflow_snapshot,\s*workflow_handoff,?\s*\)?', ''),
        (r'from tools\.security_ops import configure_security,\s*security_status\s*', ''),
        (r'from tools\.safety_policy import set_safety_policy,\s*get_audit_log,\s*get_audit_replay', 'from tools.safety_policy import set_safety_policy'),
        (r'from tools\.recording_ops import start_recording,\s*stop_recording,\s*game_serialize_state', 'from tools.recording_ops import game_serialize_state'),
        (r'from tools\.vibe_ops import vibe_coding_mode,\s*get_vibe_context\s*', ''),
    ]
    for pat, repl in import_cleanups:
        text = re.sub(pat, repl, text)

    path.write_text(text, encoding="utf-8")
    print("  ✅ server.py: 10 handlers removidos + imports limpos")


# ── VERIFICAÇÃO ──────────────────────────────────────────────────
def verify():
    print("\n--- Verificação ---")
    errors = []

    # Verificar server import
    import sys
    sys.path.insert(0, str(ROOT))
    try:
        import server
        tools = server._tool_defs()
        print(f"  Server import OK, tools: {len(tools)}")
    except Exception as e:
        errors.append(f"server import: {e}")
        print(f"  ❌ Server import falhou: {e}")

    # Verificar atômicas removidas
    for fname in ["core/tool_definitions.py", "core/legacy_data.py", "server.py"]:
        path = ROOT / fname
        content = path.read_text(encoding="utf-8")
        for tool in ALL_ATOMICS:
            if tool in content:
                # Verifica se não está em comentário
                lines_with = [l for l in content.split("\n") if tool in l and not l.strip().startswith("#")]
                if lines_with:
                    errors.append(f"{tool} ainda em {fname}")
                    print(f"  ❌ {tool} ainda em {fname}")

    if not errors:
        print("  ✅ Nenhuma atômica restante nos arquivos principais")

    return len(errors) == 0


# ── MAIN ─────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("FASE 2 — Rollups Adicionais: 10 atômicas → 5 rollups")
    print("=" * 60)

    patch_rollups()
    patch_legacy_data()
    patch_deprecated()
    patch_tool_definitions()
    patch_server()

    ok = verify()

    print("\n" + "=" * 60)
    if ok:
        print("✅ FASE 2 CONCLUÍDA — 10 atômicas → 5 rollups (-5 tools)")
    else:
        print("⚠️  FASE 2 PARCIAL — Verificar erros acima")
    print("=" * 60)


if __name__ == "__main__":
    main()
