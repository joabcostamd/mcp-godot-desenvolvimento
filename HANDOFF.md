# 🤝 HANDOFF — Comunicação entre Agentes

> **Regra:** Ao finalizar cada etapa, o agente ATUALIZA este arquivo
> para que o outro agente saiba o estado do projeto na próxima sessão.

## Último Handoff
- **Data:** 2026-07-19
- **De:** AGENTE 01 (Arquitetura & Core)
- **Etapa concluída:** A1 — 5 Namespaces Semânticos

### O que foi feito
- **TOOLSETS reestruturado** em 5 namespaces semânticos no `server.py`:
  - `project` (42 tools) — Cenas, scripts, arquivos, UI, gameplay estrutural
  - `assets` (31 tools) — Arte, áudio, shaders, VFX, geração procedural
  - `runtime` (76 tools) — Execução, debug, testes, bridge, jogo rodando
  - `analysis` (29 tools) — Auditoria, qualidade, referências, introspecção
  - `orchestration` (46 tools) — Meta-tools, workflow, governança, segurança
- **TOOL_NAMESPACES**: Dicionário reverso (224 tool_name → namespace) derivado do TOOLSETS
- **Injeção de namespace**: Cada `Tool()` recebe `_meta={"namespace": "..."}` via pós-processamento em `_tool_defs()`
- **`tools/dynamic_groups.py`**: `GROUPS` atualizado para 5 namespaces; `NAMESPACE_INFO` com descrições PT-BR; `tool_groups` suporta action `"hierarchy"`; `tool_catalog` suporta parâmetro `namespace`
- **Validação**: Sem erros de sintaxe; 100% das tools expostas têm namespace; profile dev sem regressão

### O que NÃO foi feito
- NÃO modifiquei `tools/deprecated.py`, rollups, ou handlers (conforme restrição da etapa)
- NÃO alterei o comportamento de `--profile` ou `--toolsets` — apenas estendi
- O mapeamento TOOL_NAMESPACES cobre 224 tools (named + rollups); ferramentas futuras precisam ser adicionadas ao TOOLSETS e automaticamente herdam namespace

### ⚠️ Pontos de atenção para AGENTE 02
- O `GROUPS` antigo (13 grupos) foi substituído por 5 namespaces. Se haviam referências aos grupos antigos (`"core"`, `"scene"`, `"lsp"`, etc.), elas precisam ser atualizadas.
- O `tool_catalog` agora retorna `namespace` em cada resultado e `namespace_info` no envelope.
- A fase atual (IDEIA) limita quais tools são visíveis — namespaces `assets` e `runtime` podem aparecer vazios até a fase PROTOTIPO.

### Próxima etapa (AGENTE 01)
- **A2 — ExecutionContext**: Criar `core/context.py` com `ExecutionContext` dataclass e injeção automática de contexto.
- `verification.yml` como pipeline completo com todos os gates
- Auditoria roda com `--skip-c5` (problema pre-existente documentado no commit f056aed8)
- `generate_ci_snippet` testado com 3 cenários (C3 regressão)

### 🔍 Correções pós-auditoria (v3 final)
- ✅ `permissions`: `contents: read, actions: read` no topo — menor privilégio
- ✅ `permissions`: `actions: write` isolado no job `audit` — upload-artifact
- ✅ `concurrency`: `${{ github.workflow }}-${{ github.ref }}` — isolamento cross-workflow
- ✅ `timeout-minutes`: 5-10 min por job — prevenção de CI runaway
- ✅ `cache: pip`: em todos `setup-python` — redução de ~60% no tempo de setup
- ✅ `PYTHONUNBUFFERED: "1"`: logs em tempo real sem buffering
- ✅ `set -o pipefail` no audit: pipe `| tee` não mascara mais exit code
- ✅ Summary portável: `for pair in` POSIX substitui `declare -A` (bash-only)

### ⚠️ Pontos de atenção para o AGENTE 01
- Nenhum. B2 não toca em arquivos do AGENTE 01 (server.py, core/*, tools/deprecated.py)
- Próximo: B3 (gdtoolkit Gate) — precisará criar `tools/code_quality_ops.py` (arquivo do AGENTE 02)

---

## Histórico
*(handoffs anteriores serão appendados aqui)*
