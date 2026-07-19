# 📜 DATA CONTRACTS — Contratos Formais entre Agentes

> **Versão:** 1.0.0 | **Criado em:** 2026-07-19 | **Etapa:** A3
>
> **Objetivo:** Definir os contratos formais entre AGENTE 01 (Arquitetura & Core)
> e AGENTE 02 (Extensões & Qualidade). Ambos os agentes DEVEM consultar este
> documento antes de adicionar, modificar ou remover qualquer ferramenta.
>
> **ZERO código neste documento** — apenas especificações de interface.

---

## 🎯 Visão Geral

O MCP Godot Agent expõe **ferramentas** (tools) para IAs consumidoras (DeepSeek V4, Copilot).
Cada ferramenta passa por um **pipeline de registro** que transforma uma definição `Tool()`
em uma função invocável, aplicando filtros de fase, perfil, hints, namespaces e contexto.

Dois agentes mantêm partes diferentes deste sistema:

| Agente | Responsabilidade | Arquivos exclusivos |
|---|---|---|
| 🅰️ AGENTE 01 | Arquitetura & Core | `server.py`, `core/*`, `tools/deprecated.py`, `tools/registry_validation.py`, `tools/rollups.py` |
| 🅱️ AGENTE 02 | Extensões & Qualidade | `tools/*_ops.py`, `.github/*`, `docs/*`, `tests/*` |

---

## 1. CONTRATO DE DEFINIÇÃO DE TOOL

### 1.1 Estrutura Obrigatória

Toda ferramenta deve ser registrada em **3 lugares**:

| # | Local | O que definir |
|---|---|---|
| 1 | `server.py` → `_tool_defs()` | Objeto `Tool(name, description, inputSchema)` |
| 2 | `server.py` → `_build_handlers()` | Entrada `"nome_tool": _handle_nome_tool` |
| 3 | `server.py` → handler | Função `_handle_nome_tool(args: dict) -> dict` |

### 1.2 Campos da `Tool()`

```python
Tool(
    name: str,                          # OBRIGATÓRIO — identificador único, snake_case, 1-64 chars, [a-z0-9_]
    description: str,                   # OBRIGATÓRIO — explica o que a tool faz para a IA
    inputSchema: dict,                  # OBRIGATÓRIO — JSON Schema com type, properties, required
    # ── Campos opcionais (aplicados via pós-processamento) ──
    outputSchema: dict | None = None,   # Opcional — schema da resposta (aplicado de _OUTPUT_SCHEMAS)
    annotations: dict | None = None,    # Opcional — hints + operationCategory + tags
    _meta: dict | None = None,          # Opcional — metadados customizados (namespace, etc.)
    title: str | None = None,           # Opcional — título amigável (aplicado de _TITLES)
)
```

### 1.3 Template de Descrição

Toda descrição DEVE seguir o template para consistência:

```
[O que a tool faz — 1-2 frases].
Use para [caso de uso principal].
Quando NÃO usar: [contra-indicação].
Pré-condições: [o que precisa existir antes].
Exemplo de input: [JSON exemplo].
Erro mais comum: [erro frequente + como resolver].
```

**Exemplo canônico** (`ping`):
```
"Verifica se o servidor godot-mcp-agent está funcional e conectado.
Use esta tool no início de cada sessão para confirmar que o MCP está vivo.
Quando NÃO usar: durante fluxo normal de criação de jogos (desnecessário).
Pré-condições: nenhuma — o servidor só precisa estar em execução.
Exemplo de input: {} (chamada sem argumentos).
Erro mais comum: timeout ou conexão recusada — significa que o servidor
não está rodando; verifique se server.py está em execução no terminal."
```

### 1.4 Template de `inputSchema`

```json
{
    "type": "object",
    "properties": {
        "param_obrigatorio": {
            "type": "string",
            "description": "Descrição clara em português."
        },
        "param_opcional": {
            "type": "integer",
            "description": "Descrição. Default: 42."
        },
        "param_enum": {
            "type": "string",
            "enum": ["opcao_a", "opcao_b", "opcao_c"],
            "description": "Valores válidos: opcao_a, opcao_b, opcao_c."
        }
    },
    "required": ["param_obrigatorio"]
}
```

**Regras:**
- `type` sempre `"object"`
- `properties` contém os parâmetros com `type` e `description`
- `required` lista apenas os campos obrigatórios
- Tipos suportados: `string`, `integer`, `number`, `boolean`, `array`, `object`
- Use `enum` para restringir valores de string
- Descrições em **português claro**

### 1.5 Campos Pós-Processados

Estes campos NÃO são definidos manualmente — são injetados pelo pipeline:

| Campo | Fonte | Quando |
|---|---|---|
| `annotations.readOnlyHint` | `_HINT_RULES` + nome da tool | `_apply_hints()` |
| `annotations.destructiveHint` | `_HINT_RULES` + nome da tool | `_apply_hints()` |
| `annotations.idempotentHint` | `_HINT_RULES` + nome da tool | `_apply_hints()` |
| `annotations.openWorldHint` | `_HINT_RULES` + nome da tool | `_apply_hints()` |
| `annotations.intrusiveHint` | Default `False` | `_apply_hints()` |
| `annotations.operationCategory` | `_classify_operation()` | Pós-rollups |
| `annotations.deferLoading` | Regra: não-core | `_tool_defs()` |
| `_meta.namespace` | `TOOLSETS` → `TOOL_NAMESPACES` | `_tool_defs()` (Etapa A1) |
| `outputSchema` | `_OUTPUT_SCHEMAS` dict | `_tool_defs()` |
| `title` | `_TITLES` dict (PT-BR) | `_tool_defs()` |

### 1.6 Rollups — Contrato Especial

Rollups (`<domain>_manage`) são construídos via `_meta_tool.create_manage_tool()`:

```python
from _meta_tool import create_manage_tool

tool_def, handler = create_manage_tool(
    tool_name="scene_manage",            # Nome da tool
    description="Gerencia cenas...",     # Descrição base (ops são listadas automaticamente)
    ops={                                # Dicionário {nome_op: função_handler}
        "create": create_scene,
        "load_tree": load_scene_tree,
        "instance": instance_scene_as_child,
    },
    tool_hints={                         # Opcional — hints específicos
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
    title="Gerenciar Cenas",            # Opcional — título PT-BR
    tags=["cena", "godot", "tscn"],     # Opcional — tags para catalog_search
)
```

**Regras para rollups:**
- Nome: `<dominio>_manage` (ex: `scene_manage`, `asset_manage`)
- Parâmetro `op` (enum) + `params` (dict)
- Cada `op` mapeia para uma função em `tools/*_ops.py`
- Definidos em `tools/rollups.py` → builders → `_ROLLUP_BUILDERS`
- Registro automático em `_tool_defs()` e `_build_handlers()`

---

## 2. CONTRATO DE HANDLER

### 2.1 Estrutura do Dicionário

```python
_HANDLERS_CACHE: dict[str, Callable[..., dict]] = {
    "ping": _handle_ping,
    "read_file": _handle_read_file,
    "scene_manage": <rollup_handler>,   # injetado por get_rollup_handlers()
    # ...
}
```

**Regras:**
- Chave = `tool.name` (string exata)
- Valor = função handler que retorna `dict`
- Handlers de rollup são injetados via `get_rollup_handlers()` ao final
- Ferramentas depreciadas são removidas do cache (mas handlers mantidos para fallback)

### 2.2 Assinaturas de Handler (3 Modos)

O dispatch `_smart_call()` detecta automaticamente a assinatura:

| Modo | Assinatura | Quando usar | Exemplo |
|---|---|---|---|
| **0** | `handler() -> dict` | Tool sem parâmetros | `ping`, `health_check`, `godot_keep_alive` |
| **1** | `handler(args: dict) -> dict` | Tool com parâmetros agrupados | `read_file`, `write_file`, `tool_catalog` |
| **2** | `handler(**kwargs) -> dict` | Tool com parâmetros nomeados | `godot_screenshot`, `godot_stop_project` |

**Detecção automática:**
```python
# _smart_call() inspeciona a assinatura na primeira chamada e cacheia o modo
sig = inspect.signature(handler)
params = list(sig.parameters.keys())
if not params:           → modo 0
elif params[0] == "args": → modo 1
else:                     → modo 2
```

### 2.3 Contrato de Resposta do Handler

Todo handler DEVE retornar um `dict` com:

```json
{
    "status": "success",        // ou "error"
    "message": "descrição",     // obrigatório em caso de erro
    // ... campos específicos da tool
}
```

**Regras:**
- `status` é sempre injetado se ausente (`"success"` por default)
- Em caso de erro: `status="error"` + `message` descritivo
- `error_code` é injetado automaticamente para erros conhecidos
- `friendly` (mensagem amigável PT-BR) é injetado automaticamente

---

## 3. CONTRATO DO PIPELINE

### 3.1 Fluxo Completo: Definição → Invocação

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE REGISTRO (_tool_defs)                 │
│                                                                      │
│  1. Lista hardcoded de Tool()              [~linha 1366]             │
│  2. outputSchema aplicado                  [~linha 4759]             │
│  3. Filtro: deprecated                     [~linha 4767]             │
│  4. Filtro: --toolsets                     [~linha 4772]             │
│  5. Filtro: --profile                      [~linha 4777]             │
│  6. Filtro: fase do projeto                [~linha 4784]             │
│  7. _apply_hints()                         [~linha 4790]             │
│  8. _compact_all_tool_descriptions()       [~linha 4793]             │
│  9. Filtro: kill switch                    [~linha 4797]             │
│ 10. _meta.namespace injetado (A1)          [~linha 4600]             │
│ 11. Rollups append (get_rollup_tool_defs)  [~linha 4610]             │
│ 12. operationCategory (B6)                 [~linha 4615]             │
│ 13. deferLoading (M3)                      [~linha 4620]             │
│                                                                      │
│  Resultado: _TOOL_DEFS_CACHE (list[Tool])                            │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE INVOCAÇÃO (call_tool)                 │
│                                                                      │
│  1. Governor check             [autonomia, anti-spiral]              │
│  2. Auto-checkpoint            [se tool destrutiva, fail-open]       │
│  3. Rate limiter               [sliding window]                      │
│  4. Session gate               [exige get_next_step()]               │
│  5. ExecutionContext (A2)      [resolve + set thread-local]          │
│  6. Handler dispatch           [_smart_call via thread pool]         │
│  7. Post-process               [status, error_code, friendly]        │
│  8. Governor record            [registra resultado]                  │
│  9. Cleanup (A2)               [set_execution_context(None)]         │
│                                                                      │
│  Resultado: list[TextContent]                                        │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Ordem dos Filtros (IMUTÁVEL)

> ⚠️ **A ordem dos filtros em `_tool_defs()` NÃO pode ser alterada sem**
> **atualizar este documento e notificar o outro agente via `SUTURE_ISSUES.md`.**

A ordem garante que:
1. **outputSchema** primeiro — aplica schemas de saída antes de qualquer filtro
2. **Depreciação** antes de toolsets/profile — tools deprecated nunca aparecem
3. **Profile** antes de fase — profile é mais restritivo que fase
4. **Fase** depois de profile — fase é cumulativa com CORE
5. **Hints** depois dos filtros — só tools visíveis recebem hints
6. **Namespace** antes dos rollups — rollups também herdam namespace
7. **Rollups** no final — adicionam tools após todos os filtros

### 3.3 Sistema de Namespaces (Etapa A1)

**5 namespaces semânticos** definidos em `TOOLSETS` (`server.py`):

| Namespace | Tools | Descrição |
|---|---|---|
| `project` | 51 | Cenas, scripts, arquivos, UI, gameplay estrutural |
| `assets` | 37 | Arte, áudio, shaders, VFX, geração procedural |
| `runtime` | 77 | Execução, debug, testes, bridge, jogo rodando |
| `analysis` | 29 | Auditoria, qualidade, referências, introspecção |
| `orchestration` | 45 | Meta-tools, workflow, governança, segurança |

**Contratos:**
- `TOOLSETS` → `TOOL_NAMESPACES` (dict reverso tool_name → namespace)
- `TOOLSETS` ≡ `GROUPS` em `tools/dynamic_groups.py` (devem estar sincronizados)
- Toda Tool recebe `_meta.namespace` automaticamente
- `tool_catalog` suporta filtro `namespace`
- `tool_groups("hierarchy")` retorna visão hierárquica

### 3.4 ExecutionContext (Etapa A2)

**Disponível para qualquer handler** via:

```python
from core.context import get_execution_context

ctx = get_execution_context()
# ctx.active_project   → Path | None
# ctx.active_scene     → str | None
# ctx.phase            → str (IDEIA, DESIGN, ...)
# ctx.vibe_enabled     → bool
# ctx.vibe_focus_node  → str | None
# ctx.get_scene_tree() → dict | None (cache TTL 5s)
```

**Contratos:**
- Contexto é resolvido UMA vez por tool, ANTES do handler
- Thread-local: isolado por thread do pool
- LIMPO automaticamente após o handler (`try/finally`)
- Handlers de cena devem usar `_resolve_scene_path_from_vibe()` que consulta o contexto
- `scene_path` pode ser omitido — resolvido do contexto

### 3.5 Sistema de Fases

**6 fases** em ordem: `IDEIA → DESIGN → PROTOTIPO → CONTEUDO → POLIMENTO → PRONTO_PARA_LANCAR`

**Regras:**
- `PHASE_TOOLS_CORE` (27 tools) visível em TODAS as fases
- `PHASE_TOOLSETS[phase]` adiciona tools específicas da fase (NÃO cumulativo entre fases)
- Tools não listadas na fase atual NÃO aparecem em `_tool_defs()`
- `advance_phase` notifica `tools/list_changed`

### 3.6 Perfis de Tool

| Perfil | Qtd. aprox. | Uso |
|---|---|---|
| `lean` | ~15 | Mínimo — apenas meta-tools + CORE |
| `core` | ~15 | Essenciais para bootstrap |
| `dev` | ~40 | Desenvolvimento completo |
| `full` | ~239 | Todas as tools (sem filtro) |

---

## 4. CONTRATO DE COMUNICAÇÃO ENTRE AGENTES

### 4.1 Quando o AGENTE 02 Adiciona uma Nova Tool

1. Criar função handler em `tools/*_ops.py` (ex: `tools/novo_ops.py`)
2. **NÃO** modificar `server.py` diretamente — AGENTE 01 faz o registro
3. Para tools atômicas: documentar a função e notificar AGENTE 01 via `HANDOFF.md`
4. Para rollups: adicionar builder em `tools/rollups.py` → `_ROLLUP_BUILDERS`

### 4.2 Quando o AGENTE 01 Registra uma Nova Tool

1. Adicionar `Tool(name=..., description=..., inputSchema=...)` em `_tool_defs()`
2. Adicionar `"nome_tool": _handle_nome_tool` em `_build_handlers()`
3. Adicionar `_handle_nome_tool(args: dict) -> dict` como handler
4. Categorizar a tool no `TOOLSETS` (5 namespaces) e no `PHASE_TOOLSETS` (fase)
5. Sincronizar `GROUPS` em `tools/dynamic_groups.py`
6. Atualizar `TOOL_PROFILES` se necessário

### 4.3 Zona de Sutura (Arquivos Congelados)

**NENHUM agente edita estes arquivos sem acordo prévio:**

| Arquivo | Razão |
|---|---|
| `tools/deprecated.py` | Set unificado de tools depreciadas |
| `ROADMAP_UNIFICADO.md` | Fonte única da verdade |
| `SUTURE_ISSUES.md` | Canal de conflitos |
| `DATA_CONTRACTS.md` | Este documento |

---

## 5. CONVENÇÕES DE NOMENCLATURA

| Regra | Exemplo |
|---|---|
| Ferramenta: `snake_case`, verbo primeiro | `scene_manage`, `node_manage`, `asset_manage` |
| Rollup: `<dominio>_manage` | `script_manage`, `audio_manage` |
| Handler: `_handle_<nome_tool>` | `_handle_ping`, `_handle_read_file` |
| Módulo: `<dominio>_ops.py` | `tools/scene_ops.py`, `tools/asset_ops.py` |
| Função interna: `_resolve_<alvo>` | `_resolve_scene_path_from_vibe` |
| Depreciada: `# INTERNAL: usado por <rollup>` | Comentário na função depreciada |
| Namespace: lowercase em inglês | `project`, `assets`, `runtime`, `analysis`, `orchestration` |
| Fase: UPPERCASE em PT-BR | `IDEIA`, `DESIGN`, `PROTOTIPO`, `CONTEUDO`, `POLIMENTO`, `PRONTO_PARA_LANCAR` |

---

## 6. VALIDAÇÃO DE CONTRATO

### 6.1 Ferramentas de Diagnóstico

| Ferramenta | O que valida |
|---|---|
| `validate_mcp_registry` | Tools sem handler, handlers sem Tool, tools não categorizadas |
| `validate_tool_registry_consistency` | Consistência entre as 3 fontes (Tool defs, handlers, TOOLSETS) |
| `auditar.py` (C1-C6) | 6 critérios de qualidade (AGENTE 02) |
| `CONTRACT_SNAPSHOT.json` | Snapshot das tools para detecção de drift |
| `verify_loopback.py` | Violações de contrato |

### 6.2 Como Validar um Contrato

```bash
# 1. Validar registro de tools
python -c "from server import _tool_defs; print(len(_tool_defs()))"

# 2. Validar consistência
python -c "from tools.registry_validation import validate_tool_registry_consistency; print(validate_tool_registry_consistency())"

# 3. Validar namespaces
python -c "from tools.dynamic_groups import tool_groups; print(tool_groups('hierarchy'))"

# 4. Validar ExecutionContext
python -c "from core.context import resolve_execution_context; print(resolve_execution_context())"
```

---

**Este documento é vinculante para AMBOS os agentes.**
**Alterações devem ser propostas via `SUTURE_ISSUES.md` e aprovadas pelo humano (Joab).**
**Última atualização:** 2026-07-19 — Etapa A3 concluída.
