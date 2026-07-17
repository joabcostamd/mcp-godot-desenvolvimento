# CONTEXTO_PROJETO_MCP_GODOT — Status em 2026-07-17

## Opção C: aprovada ✅

**CORE sempre visível + tools da fase atual (não-cumulativo).**

- **Código:** `server.py` — `PHASE_TOOLS_CORE` (27 tools) + `_get_phase_tools()` reescrita
- **Perfil padrão:** `full` (restaurado — antes estava `dev`, revertido)
- **Filtro:** `CORE ∪ PHASE_TOOLSETS[phase]` — não cumulativo entre fases
- **Sem projeto:** retorna apenas CORE (27 tools)
- **Nenhuma fase > 128 tools**

### Contagem por fase validada

| Fase | CORE | + Específicas | = Total |
|------|------|--------------|---------|
| IDEIA | 27 | 18 | **45** |
| DESIGN | 27 | 21 | **48** |
| PROTOTIPO | 27 | 65 | **92** |
| CONTEUDO | 27 | 35 | **62** |
| POLIMENTO | 27 | 30 | **57** |
| PRONTO_PARA_LANCAR | 27 | 18 | **45** |
| Sem projeto | 27 | 0 | **27** |

### CORE tools (27)

`ping`, `health_check`, `self_test`, `bootstrap_godot_mcp`,
`get_current_phase`, `advance_phase`, `get_phase_history`,
`read_file`, `write_file`, `file_manage`,
`safe_write_gdscript`, `script_manage`,
`project_manage`, `project_status`,
`safety_manage`, `capture_proof`, `verify_proof`,
`dump_mcp_state`,
`tool_catalog`, `tool_groups`, `godot_class_ref`,
`scene_manage`, `node_manage`,
`validate_project_refs`, `find_usages`,
`create_entity`, `create_entities`

### Testes de regressão aprovados

| Tool | Resultado | Status |
|------|-----------|--------|
| `safety_manage` | Executou com sucesso (blockeado por erros de compilação do projeto de teste — comportamento correto) | ✅ |
| `scene_manage` | Executou com sucesso — cena criada em `scenes/test_temp.tscn` (`{"status":"success","path":"scenes/test_temp.tscn"}`) | ✅ |
| `create_entity` | Bug pré-existente (dispatch posicional, `'dict' object has no attribute 'lower'`) — **pendência separada** | ❌ |

---

## Ciclo B — confirmado ✅

- `import logging` + `logger = getLogger("mcp-godot")` em `server.py`
- `except Exception as e: logger.warning(...)` em `call_tool()`
- `NotificationOptions(tools_changed=True)` + `send_tool_list_changed()` no `advance_phase`

---

## Pendências registradas (não bloqueiam Opção C)

1. **Bug `create_entity`** — dispatch posicional `handler(arguments)` faz `entity_type` receber o dict inteiro. Pré-existente (commit `d495a213`, 2026-07-10). Afeta qualquer handler com assinatura de keyword params.
2. **`dump_mcp_state` trava** — sintoma de "Canceled" na UI. Bug isolado, não investigado ainda.
3. **`godot_class_ref`** — mesmo problema de dispatch posicional (recebe dict como `class_name`).

---

## Arquivos alterados nesta entrega

| Arquivo | Mudanças |
|---------|----------|
| `server.py` | `PHASE_TOOLS_CORE`, `_get_phase_tools()` não-cumulativo, perfil padrão `full`, `logging`, `logger.warning`, remoção `if _phase_tools is not None` |
| `tools/test_ops.py` | `sys.modules.get("server")` em `estimate_tool_tokens` e `_capture_state` (evita deadlock de import em thread) |
