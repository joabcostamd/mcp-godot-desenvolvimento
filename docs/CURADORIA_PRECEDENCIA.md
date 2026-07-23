# Precedência de Filtros — MCP Godot Agent

**Versão:** 1.0 · **Data:** 2026-07-23 · **Onda:** 8.3

## Pipeline de Filtros (ordem de aplicação)

As tools passam por 2 filtros sequenciais (AND lógico).
Uma tool só aparece em `tools/list` se passar em TODOS os filtros ativos.

```
_raw_tool_defs()          272 tools brutas
    ↓
[Filtro 1: --toolsets]    Se ativo, mantém só tools do namespace selecionado
    ↓
[Filtro 2: fase]          CORE (23 tools) + tools da fase atual do projeto
    ↓
_tool_defs()              236 tools (após depreciação)
```

## Detalhamento

### Filtro 1: `--toolsets` (namespaces)

- **Origem:** CLI arg `--toolsets` ou env `MCP_TOOLSETS`
- **Dados:** `core/legacy_data.py:TOOLSETS` (5 namespaces: project, art, audio, code, data)
- **Default:** desligado (todas as tools)
- **Quando usar:** reduzir contexto para IA que só precisa de um domínio

### Filtro 2: Fase do projeto

- **Origem:** `.mcp_phase_state.json` no projeto ativo
- **Dados:** `core/legacy_data.py:PHASE_TOOLSETS` + `PHASE_TOOLS_CORE`
- **CORE (sempre visível):** 23 tools (ping, catalog_search, describe_tool, etc.)
- **Fases:** IDEIA(37) → DESIGN(45) → PROTOTIPO(11) → CONTEUDO(52) → POLIMENTO(37) → PRONTO_PARA_LANCAR(8)

### Depreciação

Após os 2 filtros, tools em `tools/deprecated.py:DEPRECATED_TOOLS` são removidas.
Aliases em `ALIAS_MAP` redirecionam nomes antigos para rollups equivalentes.

## O que foi removido (ONDA 8.2)

- **Profile filter** (`standard`/`lean`/`dev`/`full`): redundante com fase + toolsets.
  Dados mantidos em `core/legacy_data.py:TOOL_PROFILES` como referência histórica.

## Regras

1. **Ordem fixa:** toolsets → fase. Nunca inverter.
2. **AND lógico:** tool precisa passar em TODOS os filtros ativos.
3. **Filtro desligado = passa tudo:** `None` significa "sem filtro".
4. **Fail-open:** se `_get_phase_tools()` falhar, ignora o filtro de fase.
