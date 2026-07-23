# PROMPT MESTRE DE CONTINUIDADE — MCP Godot Agent

> **Use este prompt para iniciar uma nova conversa com qualquer IA agêntica moderna.**
> **Data de geração:** 2026-07-23 | **Commit:** 061ba9b | **Branch:** agente2/trabalho
> **Worktree:** mcp-godot-agente02 (Agente 2 — Conteúdo)

---

## 1. VISÃO GERAL DO PROJETO

**Nome:** MCP Godot Agent
**Objetivo final:** Um não-programador, usando linguagem natural, começa, desenvolve e TERMINA um jogo indie no Godot 4.7.
**Tipo:** Servidor MCP em Python que é DONO do processo de desenvolvimento de um jogo Godot inteiro — da ideia ao lançamento.
**Estado atual:** SOTA-1 (Fundação do Cérebro) 7/8 concluída. Stack completa de busca semântica, composição de behaviors e DSL de jogo operacional.

**Stack:** Python 3.14 (venv principal) + Python 3.12 (venv_ml) | Godot 4.7 | GdUnit4 | BGE-M3 (FlagEmbedding) | gifski + FFmpeg + Cairo | Windows (PowerShell 5.1)

**Worktrees ativos:**
- `mcp-godot-desenvolvimento` (main) — Agente 1: Núcleo (server.py, tools/, core/, domains/)
- `mcp-godot-agente02` (agente2/trabalho) — Agente 2: Conteúdo (behaviors/, blueprints/, seeds/, tests/, templates/)

**Coordenação:** `.git/coordenacao.json` no diretório comum. Sem claims ativos.

---

## 2. ARQUITETURA ATUAL

```
server.py              — Entry point MCP, tool registry, phase machine
core/                  — Máquina de estados (6 fases), intent_router, Saga Engine
tools/                 — Ferramentas MCP (gamespec_ops.py, semantic_search.py, tradutor.py, safety.py, etc.)
domains/               — Domínios modulares (physics, ui, shader, camera, navigation, vfx, runtime, export)
behaviors/             — 249 behaviors com behavior.json + .gd + .tscn + test_*.gd
behaviors/_index/      — embeddings.npz (BGE-M3, 926 KB) + ids.json
scripts/               — Scripts de desenvolvimento (gerar_testes_pares.py, mutar.py, _godot_utils.py)
ml/                    — embed_service.py (roda no venv_ml Python 3.12)
gamespec/              — gamespec.schema.json + examples/breakout.json
prompts_internos/      — normalizar.txt (prompt estágio A do tradutor)
tests/                 — Testes pytest (test_gamespec_ops.py, test_semantic_search.py, test_tradutor.py)
tests_godot/pairs/     — 1.881 testes GdUnit4 (pares combina_bem)
addons/                — GdUnit4, mcp_dock, mcp_runtime_bridge
```

**Máquina de fases:** IDEIA → DESIGN → PROTOTIPO → CONTEUDO → POLIMENTO → PRONTO_PARA_LANCAR

---

## 3. O QUE FOI IMPLEMENTADO NESTA SESSÃO

### SOTA-1 — Fundação do Cérebro (7/8 fatias)

| Fatia | O quê | Arquivos-chave |
|---|---|---|
| sota_1.1 | 249 behaviors enriquecidos (combina_bem, custo, verbo_pt, verbo_en, nivel) | behaviors/*/behavior.json |
| sota_1.2 | Busca semântica BGE-M3 (926 KB, 9/9 pytest) | ml/embed_service.py, tools/semantic_search.py |
| sota_1.4 | Tradutor de intenção 4 estágios (fallback heurístico offline) | tools/tradutor.py, prompts_internos/normalizar.txt |
| sota_1.5 | GameSpec v0 (JSON Schema 2020-12 + validador cross-ref + compilador .tscn) | gamespec/*, tools/gamespec_ops.py |
| sota_1.6 | Matriz de conflito executável (cache thread-safe, 11/11 pytest) | tools/gamespec_ops.py |
| sota_1.7 | 1.881 testes GdUnit4 de pares combina_bem | scripts/gerar_testes_pares.py, tests_godot/pairs/ |
| sota_1.8 | Mutation testing (80% detecção, 0 vivos) | scripts/mutar.py |

### Infraestrutura criada
- Python 3.12 instalado (winget)
- `.venv_ml` com FlagEmbedding + torch + BGE-M3
- `scripts/_godot_utils.py` — shared module
- `.gitignore`: `.venv_ml/`, `reports/`, `*.mutar_backup`
- Todos `subprocess.run` com `stdin=DEVNULL`

---

## 4. PENDÊNCIAS

### 🚨 BLOQUEANTE
- **sota_1.3 — GIFs NÃO FINALIZADOS.** 249 GIFs + 249 MP4s gerados (pipeline gifski+FFmpeg+Cairo funcional). Aguardando revisão de qualidade visual pelo Joab. Scripts prontos: `scripts/gerar_preview_enterprise.py`, `scripts/gerar_preview_visual.py`. Arquivos em `art_cache/`.

### SOTA-2 (próxima onda)
- sota_2.1 — Slots + herança de cena
- sota_2.2 — Três sementes jogáveis [SÊNIOR]

### Dívida técnica
- `core/intent_router.py` — tradutor não registrado como op (cross-territory Agente 1)
- `@pytest.mark.slow` não registrado no pytest.ini
- 1.881 testes GdUnit4 precisam de ~1.5h para execução completa
- 75 behavior.json com issues pré-existentes de schema (genres enum, description_en)
- `test_inv_03` falha pré-existente (`execute_gdscript_runtime` sem namespace)

---

## 5. CONVENÇÕES E PADRÕES OBRIGATÓRIOS

1. **Uma fatia por vez.** Nunca N+1 antes de N fechada.
2. **Prova sempre, nunca alegação.** Diff com `@@`, código real, output de teste completo.
3. **Nunca commite sozinho.** Proponha e aguarde aprovação.
4. **Fonte antes de código.** Consulte `.github/instructions/fontes.instructions.md`.
5. **Rollup-first.** Feature nova = op de rollup via `create_manage_tool()`, nunca tool de topo.
6. **stdin=DEVNULL** em todo subprocess. **Rede em 127.0.0.1.**
7. **Estado por projeto** em `<project_root>/.mcp_<nome>_state.json`.
8. **PowerShell sem `&&`.** Use `;` ou `cmd /c`.
9. **NÃO invente API do Godot.** R9 dos aprendizados.
10. **Path absoluto via `__file__`** em todos os módulos Python.

---

## 6. COMANDOS RÁPIDOS

```powershell
# Testes rápidos (sem BGE-M3)
.venv\Scripts\python.exe -m pytest tests/test_tradutor.py tests/test_gamespec_ops.py -q -k "not slow"

# Testes completos (com BGE-M3, ~12min)
.venv\Scripts\python.exe -m pytest tests/test_tradutor.py tests/test_gamespec_ops.py tests/test_semantic_search.py -q

# Auditoria
.venv\Scripts\python.exe auditar.py --fatia sota_1.X --skip-c5

# Reindexar embeddings
.venv_ml\Scripts\python.exe ml/embed_service.py index

# Query semântica
.venv_ml\Scripts\python.exe ml/embed_service.py query "texto da busca"

# Gerar testes de pares
python scripts/gerar_testes_pares.py --force

# Testar 1 par no Godot
cmd /c "C:\Godot\Godot_v4.7-stable_win64.exe --headless --path . -s addons/gdUnit4/bin/GdUnitCmdTool.gd --ignoreHeadlessMode -c -a res://tests_godot/pairs/test_health__hitbox.gd"

# Mutation testing
python scripts/mutar.py --sample 20 --godot "C:\Godot\Godot_v4.7-stable_win64.exe"

# Git (PowerShell)
git status --porcelain
git log --oneline -5
```

---

## 7. CHECKLIST INICIAL DA PRÓXIMA SESSÃO

1. [ ] Ler `HANDOFF.md` (fonte única de verdade)
2. [ ] Rodar `git log -3 --oneline` + `git status --porcelain`
3. [ ] Comparar HEAD com o commit do HANDOFF — detectar deriva
4. [ ] Rodar `.venv\Scripts\python.exe auditar.py --fatia sota_1.5 --skip-c5`
5. [ ] Rodar `pytest tests/test_gamespec_ops.py tests/test_tradutor.py -q -k "not slow"`
6. [ ] Verificar `coordenacao.json` no git common dir
7. [ ] Executar `/plan` para a próxima fatia (sota_2.1 ou sota_1.3)
8. [ ] NUNCA modificar arquivos sem antes rodar os passos 1-7

---

## 8. ESTADO DO GIT

```
Branch: agente2/trabalho
HEAD:   061ba9b (origin/agente2/trabalho)
Status: LIMPO (apenas untracked: SOTA_*.md, example_project/.mcp_*)
Push:   SINCRONIZADO
```

**Últimos 5 commits:**
```
061ba9b docs(encerramento): SOTA-1 7/8 concluída — HANDOFF definitivo
0b0fc20 docs(handoff): sota_1.4 + sota_1.5 concluídos
34af40b feat(sota): bloco Cérebro+GameSpec — tradutor + DSL do jogo (sota_1.4 + sota_1.5)
da4134b fix(sota_1.2): auditoria — paths absolutos via __file__, remover Tuple morto, docstring
875e348 docs(sota_1.2): atualizar HANDOFF, CHANGELOG e progresso
```

---

## 9. ARQUIVOS IMPORTANTES (LEIA ANTES DE MODIFICAR)

- `AGENTS.md` — regras de convivência entre agentes
- `.github/copilot-instructions.md` — instruções do VS Code
- `docs/ROADMAP_DEFINITIVO.md` — roadmap completo (5 ondas)
- `SOTA_01_FUNDACAO_CEREBRO.md` — fichas detalhadas da SOTA-1
- `.github/instructions/aprendizados.instructions.md` — anti-padrões (R1-R20)
- `.github/instructions/fontes.instructions.md` — fontes obrigatórias de consulta
- `HANDOFF.md` — este arquivo, estado canônico do projeto
- `.roadmap_progress_a2.json` — progresso das fatias (Agente 2)

---

**Fim do Prompt Mestre. Boa sessão.**
