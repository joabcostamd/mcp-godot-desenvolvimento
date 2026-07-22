# Catálogo de Tools — MCP Godot Agent

> 285+ tools MCP registradas. Gerado do código em 2026-07-22.

## Namespaces

| Namespace | Tools | Descrição |
|-----------|-------|-----------|
| **project** | ~120 | Criação e edição de projetos, cenas, nós, scripts |
| **assets** | ~40 | Assets, arte, áudio, shaders, VFX, download |
| **runtime** | ~20 | Execução, debug, screenshots, runtime state |
| **analysis** | ~30 | Validação, auditoria, qualidade de código |
| **process** | ~25 | Fases, milestones, workflow, gates |
| **meta** | ~15 | Catálogo, debug do MCP, configuração |
| **testing** | ~10 | Testes, GdUnit4, smoke tests |

## Novas Tools (FATIAS 2.AL–2.AS)

### Style Kit (2.AL)
- `create_style_kit` — Cria style_kit.json com preset
- `validate_style_kit` — Valida contra schema
- `apply_style_kit` — Aplica ao project brief
- `list_style_presets` — Lista presets disponíveis

### Asset Security (2.AM)
- `validate_asset_security` — Verifica segurança de asset
- `scan_asset_directory` — Escaneia diretório
- `asset_security_report` — Relatório completo

### RAG Local (2.AE)
- `index_project` — Indexa .md + .gd com TF-IDF
- `search_project` — Busca semântica top-k

### Entity Index (2.AF)
- `index_scene` — Mapeia nomes → nós
- `query_entities` — Busca "inimigo" → nós

### Fix Recipes (2.AK)
- `analyze_error` — Diagnostica erro GDScript
- `list_recipes` — 7 receitas disponíveis
- `apply_recipe` — Gera código (confirmação humana)

### Reproducibility (2.AS)
- `generate_seed` — Seed determinística
- `replay_seed` — Recupera seed anterior
- `verify_seed` — Detecta regressão
- `list_seeds` — Histórico

### Context Compaction (2.AQ)
- `log_event` — Registra evento
- `get_context_summary` — Resumo do contexto
- `estimate_tokens` — Estima tokens

### Model Routing (2.AR)
- `classify_task` — Classifica complexidade
- `estimate_cost` — Estima custo

### Undo Unify (2.AT)
- `checkpoint` — Cria checkpoint
- `undo` — Desfaz operações
- `redo` — Refaz operações
- `get_history` — Histórico

## Tools Principais (seleção)

### Projeto
- `project_manage` — CRUD de projetos
- `scene_manage` — CRUD de cenas
- `node_manage` — CRUD de nós
- `script_manage` — CRUD de scripts
- `safe_write_gdscript` — Escrita segura de GDScript
- `behavior_tree_generate` — Gera BT
- `create_entity` / `create_entities` — Cria entidades compostas

### Assets
- `asset_manage` — CRUD de assets
- `generate_game_art` — Arte por IA
- `generate_audio_sfx` — SFX procedural
- `download_asset` — Download CC0 (Kenney, Poly Haven)
- `import_asset_manifest` — Importa via manifesto
- `juice_apply` — Aplica juice/polimento

### Runtime
- `runtime_manage` — Gestão do jogo rodando
- `execute_gdscript_runtime` — Executa GDScript no jogo
- `take_screenshot` — Captura tela
- `smart_restart` — Reinicia com verificação

### Análise
- `validate_gdscript_syntax` — Valida sintaxe
- `validate_project_refs` — Valida referências
- `find_usages` — Encontra usos de símbolo
- `auditar` — Auditoria completa (12 fases)

### Fases
- `get_current_phase` — Fase atual
- `advance_phase` — Avança fase
- `create_milestone_plan` — Plano de milestone
- `project_progress` — Progresso do projeto
