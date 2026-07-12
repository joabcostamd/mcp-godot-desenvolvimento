# CHANGELOG — mcp-godot-desenvolvimento

## v3.1.0 (2026-07-12)
- **PATCH 12:** Runtime Bridge — servidor TCP GDScript (8790) + cliente Python + 4 tools (screenshot, runtime_info, custom_command, list_custom_commands)
- **PATCH 12.1:** Process Lifecycle — godot_run_project, godot_stop_project, godot_wait_for_bridge com save-before-kill e proteção contra PID reaproveitado
- **PATCH 13:** ClassDB introspecção — godot_class_ref via extension_api.json (Python puro), 1074 classes com herança, fuzzy suggestions
- **PATCH 17:** Curadoria de toolset — `--toolsets` com 10 grupos nomeados
- **PATCH 18:** Marcador `.mcp_gate_failed` integrado com hooks

## v3.0.1 (2026-07-10)
- Orquestrador Genius: Saga + Circuit Breaker + Decision Engine + Reconciliation
- 172 ferramentas no total
- Estrutura `addons/` corrigida, bridges restaurados

## v3.0 (2026-07-10)
- Pipeline Executor: `create_entity`, `project_status`
- Decision Engine: decide automaticamente arte placeholder vs FLUX
- 171 ferramentas no total
- 46 bugs corrigidos (grupos CRITICAL, HIGH, MEDIUM, LOW)
- Servidor completo e autocontido

## v2.9 (2026-07-09)
- Repositório completo e autocontido
- 143+ ferramentas
- MCP bridge + Game bridge addons incluídos
