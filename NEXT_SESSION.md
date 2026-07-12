# NEXT_SESSION.md — MCP Godot Agent

**Última sessão:** 2026-07-12 (Onda 0.1 — auditoria + correções + Features C1-C4, A1, Feature 10)
**Estado atual:** v3.3.0 — 191 tools, 191 handlers, 72 módulos, 6 fases, 10 features Fase 1, 4 features Grupo C
**📄 Doc completo:** `MCP_ESTADO_ATUAL.md` — auto-contido com TUDO para retomar

## 📋 CHECKLIST DE INICIALIZAÇÃO (próxima sessão)

1. [ ] Ler `MCP_ESTADO_ATUAL.md` (este é o doc mais completo)
2. [ ] Ler `LEARNINGS.md` R1-R18
3. [ ] Ler `config.json` (verificar paths)
4. [ ] Ativar venv: `.venv\Scripts\Activate.ps1`
5. [ ] `python server.py --profile dev`
6. [ ] Se necessário: abrir Godot (Star Colony)

## Resumo da sessão (12/07/2026 — completa)

### Features implementadas
- **Feature 4**: Vibe Coding Mode fallback
- **Feature 5**: Project Brief
- **Feature 6**: Batch Entity Creation
- **Feature 7**: Hook Stop
- **Task B**: tool_catalog PT→EN (scoring ponderado + 35 aliases)
- **Feature 8**: Toolsets por fase (PHASE_TOOLSETS dinâmico)
- **Feature 9**: Trava de exportação (mín 6/10)
- **Feature 10**: Stress Test (run_stress_test)
- **C1**: find_unused_resources (assets órfãos)
- **C2**: analyze_signal_flow (conexões de sinal órfãs)
- **C3**: set_auto_dismiss (fechamento automático de diálogos)
- **C4**: fuzzy_suggest (sugestão por proximidade + aplicado em handlers)
- **A1**: Shader editor (read_shader, edit_shader, get_shader_params)

### Bugs corrigidos (Onda 0.1)
- PHASE_TOOLSETS não filtrava — _get_phase_tools() auto-cria .mcp_phase_state.json
- PhaseState.load() não persistia estado inicial no disco
- Validação de gênero case-sensitive (Tower Defense → tower_defense)
- BUG-008: dead imports em find_unused_resources.py
- BUG-009: str/Path em milestone_ops.py
- _find_node_in_parsed: parent="." (Godot root children)
- Gate marker nunca limpo em _validate_after_edit
- Várias race conditions com locks

### Pipeline
- Star Colony: ✅ PASSOU (compile PASS, headless PASS, screenshot OK, GUT SKIPPED)
- 28 tools visíveis em IDEIA (PHASE_TOOLSETS funcional)

## Para retomar

```bash
cd "c:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento"
.venv\Scripts\Activate.ps1
python server.py --profile dev
```

## Pontos de atenção

- `godot --headless --script` E `--check-only` NÃO funcionam no Windows Godot 4.7 (R12)
- Use `--profile dev` para iniciar com 80 tools (economiza tokens vs full)
- `tool_catalog` aceita português (35 aliases) — queries: "criar cena", "adicionar nó"
- Fase do projeto afeta tools visíveis — avance com `advance_phase` para liberar mais tools
- `safety_manage` (checkpoint/backup/undo) disponível em TODAS as fases
- `.mcp_phase_state.json` é auto-criado na primeira chamada de get_current_phase()
- PHASE_TOOLSETS filtra apenas _tool_defs() — _build_handlers() não é afetado
- `find_unused_resources` usa matching exato de path (não substring)
- Autoloads do project.godot são detectados como referências implícitas
3. [ ] Ler `config.json` (verificar paths)
4. [ ] Ativar venv: `.venv\Scripts\Activate.ps1`
5. [ ] `python server.py --profile dev`
6. [ ] Se necessário: abrir Godot (Star Colony)

## Resumo da sessão (12/07/2026 — tarde)

### Features implementadas
- **Feature 4**: Vibe Coding Mode fallback (8 funções em scene_ops + vibe_ops rewrite + config_lock)
- **Feature 5**: Project Brief (project_brief_ops.py + orchestrator fallback)
- **Feature 6**: Batch Entity Creation (create_entities com MAX_BATCH_SIZE=20, Counter duplicate detection)
- **Feature 7**: Hook Stop (safety.py fix + hook_stop.py + script_ops auto-clear gate marker)
- **Task B**: tool_catalog — BM25 substituído por scoring ponderado (nome +3, ops +2, desc +1, rollup +1)
  - 35 aliases PT→EN + QUERY_ALIASES_ACCENT_ONLY ("nó"→"node" só com acento)
  - Filtro e scoring usam token matching exato (não substring)
  - rank-bm25 removido do código e do venv
- **Feature 8**: Toolsets por fase (PHASE_TOOLSETS dinâmico, cumulativo, 191 tools validadas)
  - 6 fases: IDEIA(28)→DESIGN(+28)→PROTOTIPO(+48)→CONTEUDO(+35)→POLIMENTO(+27)→PRONTO_PARA_LANCAR(+25)
  - Cache invalidado via callback registration (sem import circular)
  - Visibilidade apenas (não bloqueio de execução)
  - safety_manage disponível desde IDEIA

### Bugs corrigidos
- _find_node_in_parsed: parent="." (formato Godot para root children)
- _snapshot_scene: path relativo resolvido contra project root
- _connect_signal_file: kwargs from_node_path/to_node_path corrigidos
- Godot PID 22104 stuck em --headless --check-only (morto)
- 39 temp projects sem run/main_scene (criados + auto-config)
- _load_brief_state() race condition (substituído por get_project_brief() com lock)
- _validate_after_edit nunca limpava gate marker (adicionado _clear_gate_failed_marker)
- _get_file_path() string vs Path (adicionado Path() wrapper)

### Decisões arquiteturais
- BM25 substituído por scoring manual (melhor controle sobre ranking PT)
- Alias "no"→"node" rejeitado em favor de "nó" (acento) → "node" (QUERY_ALIASES_ACCENT_ONLY)
- PHASE_TOOLSETS lê .mcp_phase_state.json diretamente do disco (não usa singleton em memória)
- _build_handlers() NÃO é filtrado por fase (visibilidade ≠ bloqueio)

## Para retomar

```bash
cd "c:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento"
.venv\Scripts\Activate.ps1
python server.py --profile dev
```

## Pontos de atenção

- `godot --headless --script` E `--check-only` NÃO funcionam no Windows Godot 4.7 (R12)
- Godot check desligado por padrão — para religar: `"tentar_checagem_godot": true` no config.json
- Use `--profile dev` para iniciar com 80 tools (economiza tokens vs full)
- **config.json NÃO é mais versionado** — use `config.json.example` como template
- `tool_catalog` aceita português (35 aliases) — queries: "criar cena", "adicionar nó", etc.
- Fase do projeto afeta tools visíveis — avance com `advance_phase` para liberar mais tools
- `safety_manage` (checkpoint/backup/undo) disponível em TODAS as fases

## Pendências conhecidas

| Pendência | Prioridade |
|-----------|-----------|
| EARS-A: Trigger real de upgrade individual de torre (Star Colony) | Média |
| Sandbox: BYPASS-1 (concat via variáveis) e BYPASS-5 (aliasing) não bloqueados | Média |
| B1: regex `\d+` não captura IDs alfanuméricos (ex: `1_sh`) | Baixa |
| Testar gatilho U + VFX visualmente no editor Godot (headless não simula input) | Baixa |
