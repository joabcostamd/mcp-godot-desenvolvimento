# 🤝 HANDOFF — Comunicação entre Agentes

> **Regra:** Ao finalizar cada etapa, o agente ATUALIZA este arquivo
> para que o outro agente saiba o estado do projeto na próxima sessão.

## Último Handoff (AGENTE 02 — 2026-07-19 — Sessão de Polimento)

- **Data:** 2026-07-19
- **De:** AGENTE 02 (Extensões & Qualidade)
- **Ação:** Polimento completo — 7 fases implementadas

### O que foi feito (resumo)

| Fase | Nome | Resultado |
|---|---|---|
| F1 | Diagnóstico | 51% coverage, 18 tools sem teste |
| F2 | Cobertura Tier-1 | +18 handlers sintéticos → 87.8% (100% excl skip), 0 tools sem cobertura |
| F3 | Regressão Visual | `manage_visual_baselines()`, threshold calibrado, `--visual` no `auditar.py` |
| F4 | Perf Regression | Handler sintético, `perf_regression_track` já existia em `perf_ops.py` |
| F5 | Canary Queries | 14 → 48 queries, 45 tools cobertas |
| F6 | Audio Engine | `tools/audio_ops.py` (fachada unificada), play/set/stop no runtime bridge |
| F7 | Documentação | HANDOFF, NEXT_STEP, roadmap atualizados |

### Arquivos modificados/criados
- `tools/test_ops.py` — +18 handlers sintéticos, +40 `_SYNTHETIC_HANDLERS`
- `tests/canary_queries.json` — 14 → 48 queries
- `tools/runtime_ops.py` — `manage_visual_baselines()`, thresholds documentados
- `auditar.py` — `--visual`, `C7_visual`
- `tools/audio_ops.py` — NOVO, fachada unificada de áudio
- `runtime_bridge_client.py` — `play_audio()`, `set_volume()`, `stop_audio()`
- `addons/mcp_runtime_bridge/runtime_bridge.gd` — comandos de áudio em GDScript

### ⚠️ Pontos de atenção para AGENTE 01
- `_SYNTHETIC_HANDLERS` expandido de 21 → 40 tools — se adicionar tool nova, considere adicionar handler também
- `auditar.py` ganhou C7_visual — se modificar a assinatura de `run_audit()`, inclua os parâmetros `visual*`
- `audio_ops.py` reexporta de `devsolo_ops.py`, `music_ops.py`, `tts_ops.py`, etc. — se renomear funções nesses arquivos, atualize a fachada

### Próximo passo (AGENTE 02)
- **Camada 5 (Gameplay)**: TODAS [MARGINAL] — aguarda aprovação do Joab

---

## Último Handoff (AGENTE 01)
- **Data:** 2026-07-19
- **De:** AGENTE 01 (Arquitetura & Core)
- **Etapas concluídas:** A1 (Namespaces) + A2 (ExecutionContext) + A3 (DATA_CONTRACTS)

### O que foi feito (A3)
- **`DATA_CONTRACTS.md`** (novo): Contrato formal entre agentes — ZERO código
  - **6 seções**: Tool Definition, Handler, Pipeline, Comunicação, Nomenclatura, Validação
  - Documenta o ciclo completo: `Tool()` → filtros → `call_tool` → handler → resposta
  - Inclui contratos das Etapas A1 (5 namespaces, `TOOLSETS`, `TOOL_NAMESPACES`) e A2 (`ExecutionContext`, thread-local, cache TTL)
  - Define regras para AGENTE 02 adicionar tools (onde mexer, onde NÃO mexer)
  - Especifica Zona de Sutura (arquivos congelados)
  - Referência canônica para ambos os agentes

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

### AGENTE 02 — B3 (2026-07-19) ✅ Testado com gdtoolkit 4.5.0 real
- Criado `tools/code_quality_ops.py` (~570 linhas) com gdlint + gdformat + gdradon
- `.gdlintrc` reescrito em YAML (formato correto do gdlint 4.5.0)
- Gate integrado no `run_verification_pipeline` (etapa 6)
- 19/19 testes passaram (T1-T6) com projeto real (max-manos-like)
- Gate detectou: 569 violações gdlint, 89 arquivos mal formatados, avg CC=2.2
- 4 bugs de CLI corrigidos (--config, --show-complexity, PATH, SyntaxWarning)
- `tests/test_code_quality_ops.py` criado com 19 testes automatizados

### AGENTE 02 — B2 (2026-07-19)
- Criado `.github/workflows/verification.yml` — CI com 7 jobs
