#!/usr/bin/env python3
"""
FASE 1 — Quarentena REAL: Remove 19 tools do wire e move para quarentena_defs.py

O que faz:
1. Remove 19 Tool() definições de core/tool_definitions.py
2. Remove 19 nomes de core/legacy_data.py (TOOLSETS + PHASE_TOOLSETS)
3. Remove 19 handlers de server.py (_build_handlers + _handle_*)
4. Cria experimental/quarentena_defs.py com as definições movidas
5. Verifica consistência pós-migração
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent  # scripts/ → raiz do projeto

QUARENTENA_TOOLS = [
    "capsule_generate_store_image",
    "cloud_save_configure",
    "community_manage",
    "cutscene_add_camera_shot",
    "cutscene_add_dialogue_event",
    "cutscene_create_timeline",
    "mod_manifest_generate",
    "onboarding_check_first_experience",
    "onboarding_create_guided_tour",
    "onboarding_create_tutorial_step",
    "publish_manage",
    "remote_balance_config",
    "telemetry_get_funnel",
    "telemetry_heatmap",
    "telemetry_session_summary",
    "telemetry_track_event",
    "trailer_capture_clip",
    "trailer_render_sequence",
    "validate_mod_compatibility",
]

# ---------------------------------------------------------------------------
# PASSO 1: core/tool_definitions.py — extrair e remover 19 Tool() blocos
# ---------------------------------------------------------------------------
def patch_tool_definitions():
    """Remove as 19 definições Tool() de _raw_tool_defs()."""
    path = ROOT / "core" / "tool_definitions.py"
    original = path.read_text(encoding="utf-8")
    lines = original.split("\n")
    
    extracted = {}  # tool_name -> (start_line_0, end_line_0, block_text)
    
    # Encontrar cada bloco Tool(name="TOOL_NAME", ...)
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match:        Tool(
        m = re.match(r'^(\s*)Tool\($', line)
        if m:
            indent = m.group(1)
            # Next line should have name="tool_name"
            if i + 1 < len(lines):
                name_match = re.match(rf'^{indent}\s+name="(\w+)"', lines[i + 1])
                if name_match:
                    tool_name = name_match.group(1)
                    if tool_name in QUARENTENA_TOOLS:
                        # Find the closing ), for this Tool() block
                        # Count parentheses
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
                                # j is the closing line
                                break
                            j += 1
                        else:
                            print(f"  ⚠️  Não encontrou fechamento para {tool_name} na linha {i+1}")
                            i += 1
                            continue
                        
                        end = j
                        block = "\n".join(lines[start:end + 1])
                        extracted[tool_name] = (start, end, block)
                        i = end + 1
                        continue
        i += 1
    
    if len(extracted) != 19:
        print(f"  ⚠️  Encontradas {len(extracted)}/19 tools. Faltando: {set(QUARENTENA_TOOLS) - set(extracted.keys())}")
        # Continue anyway for tools found
    
    # Remover blocos (de trás pra frente para preservar índices)
    new_lines = lines.copy()
    for tool_name, (start, end, _) in sorted(extracted.items(), key=lambda x: -x[1][0]):
        del new_lines[start:end + 1]
    
    new_text = "\n".join(new_lines)
    path.write_text(new_text, encoding="utf-8")
    
    print(f"  ✅ core/tool_definitions.py: {len(extracted)}/19 Tool() removidas")
    return extracted


# ---------------------------------------------------------------------------
# PASSO 2: core/legacy_data.py — remover nomes de TOOLSETS e PHASE_TOOLSETS
# ---------------------------------------------------------------------------
def patch_legacy_data():
    """Remove os 19 nomes de ferramenta das listas em legacy_data.py."""
    path = ROOT / "core" / "legacy_data.py"
    original = path.read_text(encoding="utf-8")
    text = original
    
    removals = 0
    for tool in QUARENTENA_TOOLS:
        # Remove "tool_name", (com ou sem vírgula depois, com ou sem espaço antes)
        # Padrão: remove a string entre aspas e a vírgula que a segue ou precede
        patterns = [
            rf'"\s*{re.escape(tool)}\s*"\s*,\s*',  # "tool", 
            rf',\s*"\s*{re.escape(tool)}\s*"',       # , "tool"
        ]
        for pat in patterns:
            new_text = re.sub(pat, "", text)
            if new_text != text:
                removals += 1
                text = new_text
                break
    
    # Limpar vírgulas duplas (,,) que podem sobrar
    text = re.sub(r',\s*,', ',', text)
    # Limpar linhas com só espaços e vírgula
    text = re.sub(r'\n(\s+),\s*\n', r'\n', text)
    
    path.write_text(text, encoding="utf-8")
    
    # Contar ocorrências restantes
    remaining = 0
    for tool in QUARENTENA_TOOLS:
        if tool in text:
            remaining += 1
            # Mostrar contexto
            for i, line in enumerate(text.split("\n"), 1):
                if tool in line:
                    print(f"  ⚠️  {tool} ainda aparece na linha {i}: {line.strip()[:80]}")
    
    print(f"  ✅ core/legacy_data.py: {removals} ocorrências removidas, {remaining} restantes (devem ser 0)")
    return remaining == 0


# ---------------------------------------------------------------------------
# PASSO 3: server.py — remover handlers
# ---------------------------------------------------------------------------
def patch_server_handlers():
    """Remove registros e definições de handler das 19 tools."""
    path = ROOT / "server.py"
    original = path.read_text(encoding="utf-8")
    text = original
    
    removed_regs = 0
    removed_funcs = 0
    
    # 3a: Remover registros no dicionário _build_handlers()
    # Formato:        "tool_name": _handle_tool_name,
    for tool in QUARENTENA_TOOLS:
        # Registro no dict
        pat = rf'^\s*"{re.escape(tool)}":\s*_\w+,\s*$\n'
        new_text = re.sub(pat, "", text, flags=re.MULTILINE)
        if new_text != text:
            removed_regs += 1
            text = new_text
    
    # 3b: Remover funções _handle_* completas
    # Estas têm 2 padrões:
    #   Padrão A (thin wrapper): def _handle_tool(args):\n    return tool_func(args)\n
    #   Padrão B (manage): def _handle_tool(args):\n    """..."""\n    from ...\n    op = ...\n    params = ...\n    return func(op=op, params=params)\n
    
    # Mapeamento tool -> handler function name
    handler_map = {
        "capsule_generate_store_image": "_handle_capsule_generate_store_image",
        "cloud_save_configure": "_handle_cloud_save_configure",
        "community_manage": "_handle_community_manage",
        "cutscene_add_camera_shot": "_handle_cutscene_add_camera_shot",
        "cutscene_add_dialogue_event": "_handle_cutscene_add_dialogue_event",
        "cutscene_create_timeline": "_handle_cutscene_create_timeline",
        "mod_manifest_generate": "_handle_mod_manifest_generate",
        "onboarding_check_first_experience": "_handle_onboarding_check_first_experience",
        "onboarding_create_guided_tour": "_handle_onboarding_create_guided_tour",
        "onboarding_create_tutorial_step": "_handle_onboarding_create_tutorial_step",
        "publish_manage": "_handle_publish_manage",
        "remote_balance_config": "_handle_remote_balance_config",
        "telemetry_get_funnel": "_handle_telemetry_get_funnel",
        "telemetry_heatmap": "_handle_telemetry_heatmap",
        "telemetry_session_summary": "_handle_telemetry_session_summary",
        "telemetry_track_event": "_handle_telemetry_track_event",
        "trailer_capture_clip": "_handle_trailer_capture_clip",
        "trailer_render_sequence": "_handle_trailer_render_sequence",
        "validate_mod_compatibility": "_handle_validate_mod_compatibility",
    }
    
    for tool, handler_name in handler_map.items():
        # Remove a definição da função _handle_*
        # Padrão: def _handle_xxx(args):\n    (conteúdo)\n\n
        # O conteúdo pode ser 1 linha (thin wrapper) ou várias (manage)
        pattern = rf'def {re.escape(handler_name)}\(args: dict\) -> dict:.*?(?=\n    def |\n\n\S|\n# ──|\Z)'
        match = re.search(pattern, text, flags=re.DOTALL)
        if match:
            full_match = match.group(0)
            # Remover também as blank lines que seguem
            # Encontrar onde termina
            end_pos = match.end()
            # Comer blank lines depois
            while end_pos < len(text) and text[end_pos] == '\n':
                end_pos += 1
            text = text[:match.start()] + text[end_pos:]
            removed_funcs += 1
    
    # Se ainda há handlers não removidos, tentar padrão mais simples
    for tool in QUARENTENA_TOOLS:
        if f'"_handle_{tool}"' in text or f"def _handle_{tool}" in text:
            handler_name = f"_handle_{tool}"
            pattern = rf'def {handler_name}\(.*?\n(?:\s+.*?\n)*?(?=\n    def |\n#|\n\S)'
            match = re.search(pattern, text, flags=re.DOTALL)
            if match:
                end_pos = match.end()
                while end_pos < len(text) and text[end_pos] == '\n':
                    end_pos += 1
                text = text[:match.start()] + text[end_pos:]
                removed_funcs += 1
    
    path.write_text(text, encoding="utf-8")
    
    # Verificar handlers restantes
    remaining = 0
    for tool in QUARENTENA_TOOLS:
        handler_name = handler_map.get(tool, f"_handle_{tool}")
        if handler_name in text:
            remaining += 1
            # Find context
            for i, line in enumerate(text.split("\n"), 1):
                if handler_name in line:
                    print(f"  ⚠️  {handler_name} ainda na linha {i}: {line.strip()[:100]}")
    
    print(f"  ✅ server.py: {removed_regs} registros removidos, {removed_funcs} funções removidas, {remaining} restantes (devem ser 0)")
    
    # Also remove the imports for the ops modules if they're now unused
    # tools.achievement_ops, tools.mod_ops, tools.cutscene_ops, etc.
    # We'll skip this for now - unused imports are harmless
    
    return remaining == 0


# ---------------------------------------------------------------------------
# PASSO 4: Criar experimental/quarentena_defs.py
# ---------------------------------------------------------------------------
def create_quarentena_defs(extracted_tools):
    """Cria arquivo com as definições movidas para quarentena."""
    path = ROOT / "experimental" / "quarentena_defs.py"
    
    header = '''"""
Definições de tools em QUARENTENA — FASE 1 (2026-07-23).

Estas tools foram removidas do wire (tools/list) porque nunca foram
exercitadas por um jogo real. Continuam invocáveis via invoke_by_name,
que importa deste arquivo.

Critério de saída da quarentena:
    Um jogo real precisou da capacidade + teste passa + tool volta ao wire.
"""

from mcp.types import Tool

# Tools movidas de core/tool_definitions.py em 2026-07-23
QUARENTENA_TOOL_DEFS: list[Tool] = []

'''
    
    blocks = []
    for tool_name in sorted(extracted_tools.keys()):
        _, _, block_text = extracted_tools[tool_name]
        blocks.append(f"# ── {tool_name} ──\nQUARENTENA_TOOL_DEFS.append(\n{block_text}\n)\n")
    
    content = header + "\n".join(blocks)
    path.write_text(content, encoding="utf-8")
    print(f"  ✅ experimental/quarentena_defs.py criado com {len(extracted_tools)} definições")


# ---------------------------------------------------------------------------
# PASSO 5: Verificação
# ---------------------------------------------------------------------------
def verify():
    """Verifica que os 3 arquivos não contêm mais as 19 tools."""
    files_to_check = [
        ("core/tool_definitions.py", "Tool(name="),
        ("core/legacy_data.py", None),  # check by name
        ("server.py", None),
    ]
    
    all_clean = True
    for filepath, _ in files_to_check:
        path = ROOT / filepath
        text = path.read_text(encoding="utf-8")
        for tool in QUARENTENA_TOOLS:
            # For tool_definitions, check Tool(name="tool_name"
            if filepath == "core/tool_definitions.py":
                if f'name="{tool}"' in text:
                    print(f"  ❌ {tool} ainda em {filepath}")
                    all_clean = False
            # For others, just check string presence
            else:
                if tool in text:
                    # But allow in comments
                    lines_with_tool = [l for l in text.split("\n") if tool in l and not l.strip().startswith("#")]
                    if lines_with_tool:
                        print(f"  ❌ {tool} ainda em {filepath} (linhas: {len(lines_with_tool)})")
                        all_clean = False
    
    if all_clean:
        print("\n  ✅ VERIFICAÇÃO: Nenhuma das 19 tools nos arquivos principais")
    return all_clean


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("FASE 1 — Quarentena REAL: Removendo 19 tools do wire")
    print("=" * 60)
    
    # Backup (já feito manualmente via PowerShell)
    print(f"\n📦 Backup: verificar .mcp_backups/fase1_quarentena/")
    
    # Passo 1
    print("\n--- Passo 1: core/tool_definitions.py ---")
    extracted = patch_tool_definitions()
    
    # Passo 2
    print("\n--- Passo 2: core/legacy_data.py ---")
    legacy_ok = patch_legacy_data()
    
    # Passo 3
    print("\n--- Passo 3: server.py ---")
    server_ok = patch_server_handlers()
    
    # Passo 4
    print("\n--- Passo 4: experimental/quarentena_defs.py ---")
    create_quarentena_defs(extracted)
    
    # Passo 5
    print("\n--- Passo 5: Verificação ---")
    verify_ok = verify()
    
    print("\n" + "=" * 60)
    if verify_ok and legacy_ok and server_ok:
        print("✅ FASE 1 CONCLUÍDA — 19 tools em quarentena real")
    else:
        print("⚠️  FASE 1 PARCIAL — Verificar warnings acima")
    print("=" * 60)


if __name__ == "__main__":
    main()
