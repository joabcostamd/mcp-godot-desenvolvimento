# NEXT_SESSION.md — MCP Godot Agent

**Última sessão:** 2026-07-14 (Blocos 1-3 + Smoke Test)
**Estado atual:** v3.3.1 — 211 tools, 76 módulos, 5 auditorias, 10 regressões

## 📋 CHECKLIST DE INICIALIZAÇÃO (próxima sessão)

1. [ ] Ler `CHANGELOG.md` (v3.3.1)
2. [ ] Ler `LEARNINGS.md` R1-R20
3. [ ] Ler `FEATURES.md` (status do Shardbreaker)
4. [ ] Ler `AUDIT_PROTOCOL.md` (cadência das auditorias)
5. [ ] Ativar venv: `.venv\Scripts\Activate.ps1`
6. [ ] `python server.py --profile dev`

## Resumo da sessão (14/07/2026 — Blocos 1-3 completos)

### Ferramentas novas (5)
- `audit_input_map` — Input Map (ações declaradas vs usadas)
- `audit_autoloads` — Autoloads (registrados vs referenciados)
- `audit_scene_reachability` — Cenas (BFS, change_scene_to_file)
- `audit_uid_consistency` — UID (.uid files, duplicados, uid_cache.bin)
- `audit_save_compatibility` — Save (chaves, versionamento, migração)

### Automação
- `git_commit_checkpoint` → wiring + UID warnings (NÃO bloqueia)
- `run_verification_pipeline` → etapa 5: reachability
- `hook_stop.py` → reachability no encerramento
- `analyze_game_structure` → campo `wiring_status`
- `suggest_next_steps` → sugestão priority 0
- `regression_test` → 10 cenários

### Smoke Test — Hooks VS Code
- ❌ Agent hooks NÃO disparam com vizards.deepseek-v4-for-copilot
- Gates via handlers MCP (safety.py, hook_stop.py) — independentes de hooks

### Shardbreaker — Resultados
- 2 cenas, ambas alcançáveis
- 8 autoloads, 2 possibly unused (AudioManager, MCPRuntimeBridge)
- Sem Input Map configurado
- 12 UIDs, 0 problemas
- Save: campo version sem migração, 1 divergência

## Para retomar

```bash
cd "c:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento"
.venv\Scripts\Activate.ps1
python server.py --profile dev
```

## Pontos de atenção

- Hooks VS Code NÃO disparam → automação via handlers MCP
- `config_version=5` no Shardbreaker → sem .uid files (esperado)
- `uid_cache.bin` não parseável no Godot 4.7
- `AudioManager` possibly_unused → verificar manualmente
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
