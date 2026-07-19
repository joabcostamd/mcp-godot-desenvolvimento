# 🤝 HANDOFF — Comunicação entre Agentes

> **Regra:** Ao finalizar cada etapa, o agente ATUALIZA este arquivo
> para que o outro agente saiba o estado do projeto na próxima sessão.

## Último Handoff (AGENTE 01)
- **Data:** 2026-07-19
- **De:** AGENTE 01 (Arquitetura & Core)
- **Etapas concluídas:** A1 (Namespaces) + A2 (ExecutionContext)

### O que foi feito (A2)
- **`core/context.py`** (novo): `ExecutionContext` dataclass com thread-local storage
  - Campos: `active_project`, `active_scene`, `phase`, `vibe_enabled`, `vibe_focus_node`
  - Cache TTL 5s para `scene_tree` (evita re-resolução a cada chamada)
  - API: `resolve_execution_context()`, `get_execution_context()`, `set_execution_context()`
- **`server.py`**: `_dispatch_with_context` wrapper no `call_tool` injeta contexto antes de cada handler
  - Contexto resolvido UMA vez por tool, disponível via `get_execution_context()`
- **`tools/scene_ops.py`**: `_resolve_scene_path_from_vibe()` estendido para consultar `ExecutionContext`
  - `paint_tilemap_cell` e `detect_offscreen_elements` ganharam fallback (eram as únicas sem)
  - `scene_path` agora é `str | None = None` com resolução automática
- **`tools/code_quality_ops.py`**: SyntaxError corrigido (f-string com escape inválido) — bloqueava `import server`
- **Gate**: `scene_manage(op="create")` funciona SEM parâmetro `scene_path`

### O que foi feito (A1)
- **TOOLSETS reestruturado** em 5 namespaces semânticos (239 tools mapeadas):
  - `project` (51 tools) — Cenas, scripts, arquivos, UI, gameplay estrutural
  - `assets` (37 tools) — Arte, áudio, shaders, VFX, geração procedural
  - `runtime` (77 tools) — Execução, debug, testes, bridge, jogo rodando
  - `analysis` (29 tools) — Auditoria, qualidade, referências, introspecção
  - `orchestration` (45 tools) — Meta-tools, workflow, governança, segurança
- **TOOL_NAMESPACES**: Dicionário reverso (239 tool_name → namespace) derivado do TOOLSETS
- **Injeção de namespace**: Cada `Tool()` recebe `_meta={"namespace": "..."}` via pós-processamento
- **`tools/dynamic_groups.py`**: `GROUPS` sincronizado (239 tools); `NAMESPACE_INFO` com descrições PT-BR; `tool_groups` suporta `action="hierarchy"`; `tool_catalog` suporta `namespace`
- **Auditoria**: 28 problemas encontrados e corrigidos (14 órfãs, 1 rollup não mapeado, 13 inconsistências) — agora 0 problemas
- Arquivos: `server.py`, `tools/dynamic_groups.py`, `ROADMAP_UNIFICADO.md`, `HANDOFF.md`, `NEXT_STEP.md`

### O que NÃO foi feito
- NÃO modifiquei `tools/deprecated.py`, rollups, ou handlers
- NÃO mudei o comportamento de `--profile` ou `--toolsets`
- A duplicação `TOOLSETS` ↔ `GROUPS` é conhecida (239 tools idênticas) — futura refatoração pode unificar

### ⚠️ Pontos de atenção para AGENTE 02
- `GROUPS` antigo (13 grupos) foi substituído por 5 namespaces — se houver referências aos grupos antigos, atualizar
- `tool_catalog` agora retorna `namespace` em cada resultado e `namespace_info` no envelope
- `tool_groups("hierarchy")` retorna visão hierárquica: namespace → descrição → tools
- Novas tools adicionadas ao `TOOLSETS` automaticamente recebem namespace; novas tools também devem ser adicionadas ao `GROUPS` em `dynamic_groups.py`

### Próxima etapa (AGENTE 01)
- **A2 — ExecutionContext**: Criar `core/context.py` com `ExecutionContext` dataclass

---

## Histórico

### AGENTE 02 — B3 (2026-07-19) 🔶 [aguardando revisão]
- Criado `tools/code_quality_ops.py` (~520 linhas, 4 funções + helpers)
- Criado `.gdlintrc` (limiares: 80 linhas/função, CC≤10, 500 linhas/classe)
- Integrado no `run_verification_pipeline` (etapa 6, parâmetro `include_code_quality`)
- `requirements.txt` atualizado com `gdtoolkit>=4.0,<5.0`
- **2 auditorias realizadas**: 12 problemas encontrados, 12 corrigidos
  - Bugs críticos: import ausente, parâmetro ausente (NameError), gate false-pass
  - Performance: regex O(n²)→O(n) com pre-filtro, stdin=DEVNULL
  - Robustez: Windows paths, FileNotFoundError, gdtoolkit_version consistente
- ⚠️ **Pendente**: teste canary com Godot real, validação do `.gdlintrc`

### AGENTE 02 — B2 (2026-07-19)
- Criado `.github/workflows/verification.yml` — CI com 7 jobs
