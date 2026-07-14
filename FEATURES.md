# FEATURES.md — Registro de Wiring do Projeto Shardbreaker

> **Projeto:** Shardbreaker (nodebuster-like)
> **Data da última auditoria:** 2026-07-14
> **MCP:** godot-mcp-agent v3.3.0
> **Ferramentas utilizadas:** audit_input_map, audit_autoloads, audit_scene_reachability, audit_uid_consistency, audit_save_compatibility

---

## Cenas

| Feature | Arquivo | Ponto de entrada | Status | Ferramenta |
|---------|---------|-----------------|--------|-----------|
| Menu principal | `res://scenes/ui/main_menu.tscn` | `run/main_scene` no project.godot | ✅ Alcançável | audit_scene_reachability |
| Jogo (gameplay) | `res://scenes/game.tscn` | `change_scene_to_file("res://scenes/game.tscn")` em `scripts/ui/title_screen.gd:147` | ✅ Alcançável | audit_scene_reachability |

**Resumo:** 2 cenas no projeto, ambas alcançáveis a partir da cena raiz. Nenhuma cena órfã detectada.

---

## Autoloads

| Singleton | Script | Status | Nota |
|-----------|--------|--------|------|
| EventBus | `res://scripts/autoloads/event_bus.gd` | ✅ Referenciado | — |
| GameState | `res://scripts/autoloads/game_state.gd` | ✅ Referenciado | — |
| UpgradeManager | `res://scripts/autoloads/upgrade_manager.gd` | ✅ Referenciado | — |
| SaveManager | `res://scripts/autoloads/save_manager.gd` | ✅ Referenciado | Encontrado via autoload + padrão de nome |
| AudioManager | `res://scripts/autoloads/audio_manager.gd` | ⚠️ Possibly unused | Verificar manualmente — pode ser usado via get_node() ou grupo |
| AchievementManager | `res://scripts/autoloads/achievement_manager.gd` | ✅ Referenciado | — |
| MCPRuntimeBridge | `res://addons/mcp_runtime_bridge/runtime_bridge.gd` | ⚠️ Possibly unused | Falso positivo esperado — ponte interna do MCP |
| LocalizationManager | `res://scripts/autoloads/localization_manager.gd` | ✅ Referenciado | — |

**Resumo:** 8 autoloads registrados, 2 sem referência direta encontrada. **Atenção:** `possibly_unused` não significa remover — pode haver uso via `get_node("/root/Nome")` ou grupo. Verificar manualmente antes de qualquer ação.

---

## Input Map

| Status | Detalhe |
|--------|---------|
| ⚠️ Não configurado | Seção `[input]` não encontrada no `project.godot`. O projeto pode usar teclas diretas (`Input.is_key_pressed`) que esta auditoria não detecta. |

---

## Consistência de UID

| Métrica | Valor |
|---------|-------|
| UIDs declarados verificados | 12 |
| UIDs divergentes | 0 |
| UIDs duplicados | 0 |
| Arquivos `.uid` ausentes | 0 (projeto `config_version=5`, pré-4.4 — ausência esperada) |
| Não resolvidos | 1 (`uid_cache.bin` não parseável) |

**Resumo:** Projeto usa sistema de UID antigo (Godot 4.3). Nenhum problema de consistência detectado.

---

## Compatibilidade de Save

| Campo | Valor |
|-------|-------|
| Script de save | `res://scripts/autoloads/save_manager.gd` (SaveManager) |
| Campo de versão | ✅ Presente (`"version": 1`) |
| Lógica de migração | ❌ Ausente (sem `if version < N` ou `match version`) |
| Divergências escrita/leitura | 1 (`"version"` é escrito mas nunca lido condicionalmente) |
| Testado contra save real | Não (save em `user://`, não em `res://`) |

**Resumo:** O save tem campo de versão mas nunca é verificado. Se o schema mudar no futuro, saves antigos quebrarão silenciosamente. Recomendado adicionar `if data.get("version", 1) < 2: migrate()` no `_deserialize_state()`.

---

## Limitações Conhecidas

- **Input Map:** Só detecta ações nomeadas (`Input.is_action_*`). Teclas diretas (`Input.is_key_pressed`) não são cobertas.
- **Autoloads:** `possibly_unused` pode ser falso positivo (uso via `get_node()` ou string dinâmica).
- **Cenas:** `change_scene_to_file()` detectado, mas `change_scene_to_packed()` com variável dinâmica não é resolvido.
- **UID:** `uid_cache.bin` não foi parseável (formato Godot 4.7 pode ter mudado).
- **Save:** Análise estática — não garante que a lógica de save funcione em runtime.
