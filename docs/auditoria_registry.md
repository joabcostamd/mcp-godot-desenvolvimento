# Auditoria do Registry — ONDA 1.1

**Data:** 2026-07-23
**Versão:** 1.0

---

## Módulos do `registry/`

### `types.py` — ✅ COMPLETO
- `Phase` (enum): 6 fases (IDEIA, DESIGN, PROTOTIPO, CONTEUDO, POLIMENTO, PRONTO_PARA_LANCAR)
- `OpSpec` (dataclass): nome, handler, inputSchema, annotations
- `DomainManifest` (dataclass): domain_name, version, phase, ops, toolsets, description
- **Gap:** Nenhum. Tipos canônicos definidos.

### `discovery.py` — ✅ COMPLETO (infra)
- `discover()`: Varre `domains/*/manifest.py`, coleta `MANIFEST`. Retorna `dict[str, DomainManifest]`.
- `build_tool_defs(phase)`: Delega ao `legacy_adapter`. Retorna `list[Tool]`.
- `build_handlers()`: Delega ao `legacy_adapter`. Retorna `dict[str, Callable]`.
- `invalidate_caches()`: Limpa cache local + `server._TOOL_DEFS_CACHE` + `server._HANDLERS_CACHE`.
- **Gap:** `discover()` retorna vazio porque `domains/` não tem manifestos migrados ainda (ONDA 5).

### `legacy_adapter.py` — ✅ COMPLETO
- `build_tool_defs_legacy(phase)`: Ponte para `server._tool_defs()` com guarda de recursão.
- `build_handlers_legacy()`: Ponte para `server._build_handlers()`.
- `get_phase_tools_legacy()`: Ponte para `server._get_phase_tools()`.
- `get_toolsets_legacy()` / `get_phase_toolsets_legacy()`: Lê `TOOLSETS`/`PHASE_TOOLSETS`.
- **Gap:** Nenhum. Funciona como proxy transparente.

### `invariants.py` — ✅ COMPLETO (6 ativas)
- `check_all(phase)`: Executa INV-01, INV-02, INV-04, INV-10, INV-11, INV-12, INV-13.
- `_inv_01()`: Toda tool tem handler — ✅
- `_inv_02()`: Todo handler tem tool — ✅
- `_inv_04()`: Toda tool tem fase — ✅ (implementado na ONDA 8.1)
- `_inv_10()`: PHASE_TOOLSETS → tools/list — ✅
- `_inv_11()`: TOOLSETS → tools/list — ✅
- `_inv_12()`: Sem duplicação de namespace — ✅
- **Gap:** INV-05 a INV-09, INV-14, INV-15 são xfail (fases futuras).

### `annotations.py` — ✅ COMPLETO
- `validate_annotations(tool)`: Verifica `ToolAnnotations` e 4 hints obrigatórios.
- **Gap:** Nenhum.

### `legacy_annotations.py` — ✅ COMPLETO
- `_HINT_RULES`: Regras estáticas de prefixo/sufixo para hints MCP.
- **Gap:** Nenhum. Dados extraídos de `server.py` na Onda 2.3.

---

## Fluxo atual

```
MCP client
  → @server.list_tools()
    → server._tool_defs()
      → registry.build_tool_defs()          ← ONDA 1.2: server chama registry
        → legacy_adapter.build_tool_defs_legacy()
          → server._tool_defs() [guarda]    ← proxy circular com guarda
            → core.tool_definitions._raw_tool_defs()
      → pós-processamento (hints, títulos, rollups, filtros)
      → list[Tool] final (234 tools)
```

**Paridade:** `registry.build_tool_defs()` ≡ `server._tool_defs()` — 234 tools, 0 diff.

---

## Gaps identificados

| Gap | Impacto | Quando resolver |
|---|---|---|
| `domains/` sem manifestos | `discover()` retorna vazio | ONDA 5 (migração) |
| Fluxo circular server↔registry | Complexidade desnecessária | ONDA 5 (quando discover() tiver dados) |
| INV-05 a INV-09 xfail | Validações pendentes | ONDA 2 (conformidade) |

**Conclusão:** O registry está funcional como infraestrutura. A ONDA 1 atinge seu objetivo: preparar o terreno para a ONDA 5 (migração de domínios).
