# Auditoria do registry/ — Fatia 1.1

**Data:** 2026-07-23
**Objetivo:** Documentar o estado real de `registry/` antes da migração (Fatia 1.2).

---

## 1. registry/__init__.py

### Exports públicos
| Símbolo | Tipo | Origem |
|---------|------|--------|
| `build_tool_defs` | função | `discovery.build_tool_defs` |
| `build_handlers` | função | `discovery.build_handlers` |
| `discover` | função | `discovery.discover` |
| `invalidate_caches` | função | `discovery.invalidate_caches` |
| `DomainManifest` | classe | `types.DomainManifest` |
| `OpSpec` | classe | `types.OpSpec` |
| `Phase` | enum | `types.Phase` |

### Status: FUNCIONAL. Interface pública definida, imports resolvidos.

---

## 2. registry/types.py

### Classes
| Classe | Campos | Status |
|--------|--------|--------|
| `Phase` | Enum: IDEIA, DESIGN, PROTOTIPO, CONTEUDO, POLIMENTO, PRONTO_PARA_LANCAR | OK |
| `OpSpec` | dataclass: name, fn, summary, schema, examples, annotations, deprecated_since, replaced_by, rollback | OK |
| `DomainManifest` | dataclass: domain, tool_name, title, namespace, version, aliases, description, phases, always_visible, internal, named_justification, annotations, ops, tags | OK |

### Status: COMPLETO. Define a estrutura de dados para manifestos de domínio.

---

## 3. registry/discovery.py

### Funções
| Função | Comportamento | Status |
|--------|--------------|--------|
| `discover()` | Varre `domains/*/manifest.py`, carrega `MANIFEST`, cacheia resultado | FUNCIONAL |
| `build_tool_defs(phase)` | **Delega 100% para `legacy_adapter.build_tool_defs_legacy(phase)`** | WRAPPER |
| `build_handlers()` | **Delega 100% para `legacy_adapter.build_handlers_legacy()`** | WRAPPER |
| `invalidate_caches()` | Reseta `_manifests` para None | FUNCIONAL |

### GAP: `build_tool_defs` e `build_handlers` são wrappers puros — não usam `discover()`.
O código real está em `legacy_adapter`, que chama `server._tool_defs()` e `server._build_handlers()`.

---

## 4. registry/legacy_adapter.py

### Funções
| Função | Implementação | Dependência de server.py |
|--------|--------------|--------------------------|
| `build_tool_defs_legacy(phase)` | `return server._tool_defs()` | `server._tool_defs` |
| `build_handlers_legacy()` | `return server._build_handlers()` | `server._build_handlers` |
| `get_phase_tools_legacy()` | `return server._get_phase_tools()` | `server._get_phase_tools` |
| `get_toolsets_legacy()` | `return dict(server.TOOLSETS)` | `server.TOOLSETS` |
| `get_phase_toolsets_legacy()` | `return {CORE, PHASE_TOOLSETS}` | `server.PHASE_TOOLS_CORE`, `server.PHASE_TOOLSETS` |

### GAP CRÍTICO: Dependência circular.
`registry` → `legacy_adapter` → `server` → (ainda não importa `registry`).
Para a Fatia 1.2 (`server.py` chamar `registry.build_tool_defs()`), teremos:
`server` → `registry` → `legacy_adapter` → `server` (circular!).
É necessário quebrar este ciclo antes de 1.2.

---

## 5. registry/invariants.py

### Invariantes implementadas
| ID | Descrição | Status |
|----|-----------|--------|
| INV-01 | Toda tool em tools/list tem handler | IMPLEMENTADO |
| INV-02 | Todo handler tem tool em tools/list | IMPLEMENTADO |
| INV-10 | PHASE_TOOLSETS ⊆ tools/list | IMPLEMENTADO |
| INV-11 | TOOLSETS ⊆ tools/list | IMPLEMENTADO |
| INV-12 | Sem duplicação de namespace | IMPLEMENTADO |
| INV-13 | Sem colisão de registro | PLACEHOLDER (ativado em F3) |

### Dependências de server.py
- `server._tool_defs()` — INV-01, INV-02
- `server._build_handlers()` — INV-01, INV-02
- `server.TOOLSETS` — INV-11, INV-12
- `server.PHASE_TOOLSETS`, `server.PHASE_TOOLS_CORE` — INV-10
- `tools.deprecated.DEPRECATED_TOOLS` — INV-10, INV-11

### GAP: Mesmo problema de dependência circular. `invariants.py` importa `server` diretamente.

---

## 6. registry/annotations.py

### Funções
| Função | Descrição | Status |
|--------|-----------|--------|
| `validate_annotations(tool)` | Valida hints MCP (4 campos) | FUNCIONAL |
| `create_annotations(...)` | Cria ToolAnnotations limpo | FUNCIONAL |
| `validate_all(tools)` | Validação em lote | FUNCIONAL |

### Status: INDEPENDENTE. Não depende de `server.py`, só do SDK MCP.
Pronto para uso imediato. Já resolve o bug da Fatia 2.1 (tags apagando hints).

---

## 7. Resumo de Gaps

| Gap | Severidade | Impacto |
|-----|-----------|---------|
| Dependência circular `registry → legacy_adapter → server` | **BLOQUEADOR** | Impede Fatia 1.2 (`server.py` chamar `registry.build_tool_defs()`) |
| `invariants.py` importa `server` diretamente | **ALTO** | Viola isolamento do registry |
| `build_tool_defs` não usa `discover()` | **MÉDIO** | Código morto: `discover()` existe mas nunca é chamado em produção |
| `discover()` varre `domains/*/manifest.py` | **BAIXO** | Funciona, mas domínios ainda não têm manifestos (estão no sistema legado) |
| INV-13 placeholder | **BAIXO** | Ativado em F3, OK por enquanto |

---

## 8. Recomendação para Fatia 1.2

Antes de fazer `server.py` chamar `registry.build_tool_defs()`:

1. **Quebrar o ciclo:** `legacy_adapter` não pode importar `server`. Em vez disso, `server` deve passar as funções legadas como parâmetros (injeção de dependência) ou `legacy_adapter` deve acessar `core/tool_definitions.py` diretamente (não via `server`).
2. **Mover** `_tool_defs()`, `_build_handlers()`, `TOOLSETS`, `PHASE_TOOLSETS`, `PHASE_TOOLS_CORE` para um módulo separado (ex: `core/legacy_registry.py`) que ambos `server` e `registry` possam importar sem ciclo.
