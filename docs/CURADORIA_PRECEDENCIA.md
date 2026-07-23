# Precedência de Filtros — MCP Godot Agent

**Versão:** 2.0 · **Data:** 2026-07-23 · **Onda:** 8.3 (pós-8.2)

## Pipeline de Filtros (ordem de aplicação)

As tools passam por 2 filtros sequenciais (AND lógico).
Uma tool só aparece em `tools/list` se passar em TODOS os filtros ativos.

```
_raw_tool_defs()          ~272 definições brutas
    ↓
[Filtro 1: --toolsets]    Se ativo, mantém só tools do namespace selecionado
    ↓
[Filtro 2: fase]          CORE (25 tools) + tools da fase atual do projeto
    ↓
_tool_defs()              234 tools (após depreciação e filtros)
```

## Detalhamento

### Filtro 1: `--toolsets` (namespaces semânticos)

- **Origem:** CLI arg `--toolsets` (resolvido em `parse_toolset_arg()`)
- **Dados:** `core/legacy_data.py:TOOLSETS` (5 namespaces)
- **Namespaces:** project (71), assets (32), runtime (40), analysis (38), orchestration (55)
- **Default:** `all` = desligado (todas as tools)
- **Quando usar:** reduzir contexto para IA que só precisa de um domínio

### Filtro 2: Fase do projeto

- **Origem:** `.mcp_phase_state.json` no projeto ativo (lido por `_get_phase_tools()`)
- **Dados:** `core/legacy_data.py:PHASE_TOOLSETS` + `PHASE_TOOLS_CORE`
- **CORE (sempre visível):** 25 tools (ping, health_check, fase, catalog_search, budget_manage, etc.)
- **Fases (não-cumulativas, Opção C):**
  - IDEIA: 38 tools · DESIGN: 57 · PROTOTIPO: 14
  - CONTEUDO: 63 · POLIMENTO: 42 · PRONTO_PARA_LANCAR: 16

### Depreciação

Após os 2 filtros, tools em `tools/deprecated.py:DEPRECATED_TOOLS` (191) são removidas.
Aliases em `ALIAS_MAP` (80) redirecionam nomes antigos para rollups equivalentes.

## O que foi removido (ONDA 8.2)

- **Eixo Profile:** `TOOL_PROFILES` (core/dev/lean/full) removido de `core/legacy_data.py`.
  `_resolve_tool_profile()` e `_PROFILE_TOOLS` removidos de `server.py`.
  Motivo: redundante com o filtro por fase — o perfil "lean" era essencialmente o CORE,
  "dev" era DESIGN, "full" era sem filtro. A fase já cobre essa granularidade.

## Regras

1. **Ordem fixa:** toolsets → fase. Nunca inverter.
2. **AND lógico:** tool precisa passar em TODOS os filtros ativos.
3. **Filtro desligado = passa tudo:** `None` significa "sem filtro".
4. **Fail-open:** se `_get_phase_tools()` falhar, retorna só CORE.
5. **Visibilidade ≠ bloqueio:** `_build_handlers()` não é filtrado. Tool escondida ainda pode ser chamada.
