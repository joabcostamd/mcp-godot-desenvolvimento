# NEXT_SESSION.md — MCP Godot Agent

**Última sessão:** 2026-07-12 (Features 4-8 + Task B concluídos)
**Estado atual:** v3.3.0 — 191 tools, 191 handlers, 69 módulos, 6 fases, tool_catalog PT→EN
**📄 Doc completo:** `MCP_ESTADO_ATUAL.md` — auto-contido com TUDO para retomar

## 📋 CHECKLIST DE INICIALIZAÇÃO (próxima sessão)

1. [ ] Ler `MCP_ESTADO_ATUAL.md` (este é o doc mais completo)
2. [ ] Ler `LEARNINGS.md` R1-R17
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
