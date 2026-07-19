# 🔧 Ferramentas

## Gates de Qualidade

- `run_code_quality_gate` — gdlint + gdformat + gdradon
- `scan_addon_vulnerabilities` — 12 padroes de vulnerabilidade
- `check_addon_license` — 19 tipos de licenca

## Analises Especificas
- `find_unused_functions` — Funcoes nao utilizadas
- `detect_gdscript_antipatterns` — Antipadroes GDScript
- `find_orphan_signals_nodes` — Sinais orfaos
- `check_naming_convention` — Convencoes de nome
- `find_duplicate_code_blocks` — Codigo duplicado
- `detect_scene_reference_cycles` — Ciclos de cena
- `check_import_settings_consistency` — Consistencia .import
- `semantic_code_search` — Busca semantica
- `suggest_refactor` — Sugestoes de refatoracao

## Orquestracao
- `acquire_file_lock` / `release_file_lock` — Lock entre agentes
- `create_task_queue` / `get_next_task` — Fila de tarefas
- `request_peer_review` — Revisao cruzada
- `compare_agent_outputs` — Comparacao de modelos