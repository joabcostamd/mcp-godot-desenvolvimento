# CHANGELOG — mcp-godot-desenvolvimento

## v3.2.1 (2026-07-12) — Sessão de auditoria, hardening + Item 1+2 do plano de evolução

### Item 1: Pipeline de Verificação (run_verification_pipeline)
- **Nova tool:** `run_verification_pipeline` — pipeline completo em 4 etapas (compile → headless run → screenshot → GUT)
- **Módulo novo:** `tools/verification_ops.py` (330 linhas)
- **Relatório JSON consolidado** com status de cada etapa, early exit na primeira falha
- **Screenshot via `--write-movie`** com SW_HIDE (não usa `--headless` — evita crash SIGSEGV do renderer DUMMY)
- **Tratamento de ambiguidade:** retorna `ambiguous` se `test_scene` não definido
- **6 bugs encontrados e corrigidos** (BUG-V01 a V06): variáveis mortas, self-assignment, mutação de dict, partial output em timeout

### Item 2: Fluxo EARS + Pipeline (Padrão de Fechamento de Pendência)
- **AGENTS.md** criado no Star Colony com regra de comportamento obrigatória
- Fluxo documentado: receber → EARS → aprovar → implementar → pipeline → relatório → fechar condicional
- **EARS-B implementado:** VFX de evolução visual L1→L2→L3 com gatilho provisório (tecla U)
- **_draw() modificado:** escala por nível (L1=1.0, L2=1.15, L3=1.30) + borda (L2=prata, L3=douro)
- **VFX:** `spawn_explosion`, `spawn_floating_text`, `add_shake(0.15, 3.0)` via `vfx_system.gd`
- **Teste visual:** pixel analysis confirma bordas prateada/dourada exclusivas por nível

### Documentação
- **MCP_ESTADO_ATUAL.md** sincronizado com 191 tools, 69 módulos, v3.2.1
- **pendencias.md** criado (bugs ativos + resolvidos)
- **decisoes.md** (Star Colony) atualizado com EARS-B

### Métricas atualizadas
- **191 tools** (+2: run_verification_pipeline + 1 rollup), **69 módulos** (+5)
- **49 bugs corrigidos** (+6 BUG-V01~V06) em 12 rodadas de auditoria

### Correções de segurança
- **Sandbox conectado à escrita:** `write_file` e `safe_write_gdscript` agora chamam `validate_gdscript_code()` antes de escrever .gd em disco (36/36 padrões bloqueados com confirmação de disco)
- **Normalização de código:** `_normalize_gdscript()` remove comentários, colapsa whitespace, resolve concatenação literal — fecha 3/4 bypasses (comentário, quebra de linha, concatenação)
- **Escopo documentado:** aviso no topo de `gdscript_sandbox.py` — é filtro de texto, não sandbox de execução isolada
- **`safe_write_gdscript` corrigido:** path relativo ao projeto, `godot_console_path` para `--headless`, timeout handler com `skipped: True` explícito
- **Godot check desligado por padrão:** flag `tentar_checagem_godot` (default false) — R12 confirmado em 3 tipos de projeto (minimal, Star Colony, completo)

### Correções de bugs
- **B1 documentado:** `_parse_tscn_node_refs` regex `\d+` não detecta IDs alfanuméricos (ex: `1_sh`)
- **B2 corrigido:** `run_scripted_tests` agora suporta runtime tools (`godot_screenshot`, `godot_runtime_info`)
- **B3 corrigido:** `dump_mcp_state` retorna `"status": "success"` no nível raiz
- **Handler órfão:** adicionado schema `estimate_tool_tokens` em `_tool_defs()` (estava só no handler)
- **PATCH 12 auditado:** `_cmd_custom` com validação de callable, `_reply` com verificação de erro

### Infraestrutura
- **Hook Stop NUCLEO:** `check-gate-failed.ps1` — bloqueia encerramento se `.mcp_gate_failed` existir
- **pre-commit versionado:** movido para `.github/hooks/scripts/pre-commit.ps1`
- **Limpeza:** removidos MCPs duplicados (`sistema/mcp-godot/`, `refinamento-mcp/`)
- **config.json untracked:** removido do Git para evitar reversões acidentais

### Documentação
- **Todos os docs atualizados para v3.2:** README, ARQUITETURA_MCP, GUIA_CONEXAO, GUIA_INSTALACAO, LEARNINGS
- **LEARNINGS.md R12 ampliado:** cobre `--headless --script` E `--check-only`
- **MCP ESTADO ATUAL:** documento externo sincronizado com 190 tools, 64 módulos, 18 patches

**Total:** 190 ferramentas, 190 handlers, 64 módulos, 18 patches, 5 grupos de auditoria

## v3.2.0 (2026-07-12) — Sessão anterior
- **PATCH 14:** Testes roteirizados — smoke_test, regression_test, run_scripted_tests, dump_mcp_state, estimate_tool_tokens
- **PATCH 15:** Validação de referências — validate_project_refs, find_usages (estático, offline)
- **PATCH 16:** Asset manifest — import_asset_manifest (5 fontes), create_asset_manifest
- **GRUPO 1:** Validação GDScript no write_file + safe_write R9 deep validation
- **GRUPO 2:** git_commit_checkpoint com gates de compilação + GUT skipped
- **GRUPO 3:** --profile (core/dev/full) + MCP_TOOL_PROFILE + estimate_tool_tokens
- **GRUPO 4:** config.local.json + GODOT_MCP_* env vars (confirmado)
- **GRUPO 5:** allow_paid_generation=False + estimated_cost
- **Total:** 189 ferramentas, 64 módulos, 43 bugs corrigidos em 10 rodadas de auditoria

## v3.1.0 (2026-07-12)
- **PATCH 12:** Runtime Bridge — servidor TCP GDScript (8790) + cliente Python + 4 tools (screenshot, runtime_info, custom_command, list_custom_commands)
- **PATCH 12.1:** Process Lifecycle — godot_run_project, godot_stop_project, godot_wait_for_bridge com save-before-kill e proteção contra PID reaproveitado
- **PATCH 13:** ClassDB introspecção — godot_class_ref via extension_api.json (Python puro), 1074 classes com herança, fuzzy suggestions
- **PATCH 17:** Curadoria de toolset — `--toolsets` com 10 grupos nomeados
- **PATCH 18:** Marcador `.mcp_gate_failed` integrado com hooks

## v3.0.1 (2026-07-10)
- Orquestrador Genius: Saga + Circuit Breaker + Decision Engine + Reconciliation
- 172 ferramentas no total
- Estrutura `addons/` corrigida, bridges restaurados

## v3.0 (2026-07-10)
- Pipeline Executor: `create_entity`, `project_status`
- Decision Engine: decide automaticamente arte placeholder vs FLUX
- 171 ferramentas no total
- 46 bugs corrigidos (grupos CRITICAL, HIGH, MEDIUM, LOW)
- Servidor completo e autocontido

## v2.9 (2026-07-09)
- Repositório completo e autocontido
- 143+ ferramentas
- MCP bridge + Game bridge addons incluídos
