# 🚀 PROMPT MESTRE DE CONTINUIDADE — MCP Godot Agent

> **Cole este prompt inteiro na próxima conversa com qualquer IA agêntica.**
> **Data de geração:** 2026-07-23 · **Commit:** `a585814` · **Branch:** `main`

---

## 1. VISÃO GERAL DO PROJETO

Servidor MCP em Python que é o **dono do processo** de desenvolvimento de um jogo Godot inteiro — da ideia ao lançamento. Não é só uma ponte entre IA e engine: tem travas reais (fase, verificação, export, sessão) que impedem pular etapa.

**Stack:** Python 3.14, MCP SDK (stdio JSON-RPC 2.0), Godot 4.7, Pydantic v2
**Objetivo final:** um não-programador, usando linguagem natural, começa, desenvolve e **termina** um jogo indie.

## 2. ARQUITETURA ATUAL

```
MCP Client (IA)
  → server.py (list_tools / call_tool)
    → core/tool_definitions.py (_raw_tool_defs → ~272 brutas)
    → pós-processamento (hints, rollups, filtros, depreciação)
    → 233 tools visíveis
  → tools/ (80+ módulos handlers)
  → registry/ (infra de descoberta — ainda proxy do legado)
  → core/legacy_data.py (TOOLSETS, PHASE_TOOLSETS, PHASE_TOOLS_CORE)
  → Godot Engine (via bridge/addon, porta 8790)
```

**2 eixos de filtro:** `--toolsets` (5 namespaces) + fase (6 fases não-cumulativas + CORE)

## 3. MÉTRICAS ATUAIS (comandos executados, não estimativas)

```
Tools visíveis: 233 (233 handlers)
Definições brutas: 272
DEPRECATED_TOOLS: 191
ALIAS_MAP: 80
CORE: 25 tools
Fases (CORE+fase): IDEIA=63, DESIGN=82, PROTOTIPO=39, CONTEUDO=88, POLIMENTO=67, PRONTO=41
Hints MCP: readOnly=16, destructive=53, idempotent=25, openWorld=229
Quarentena: 19 tools em experimental/quarentena.json
Testes: 157 passed, 2 failed (test_remix — pré-existente), 7 xfailed
Gate pre-commit: exit 0
Auditoria: PASS (0 erros)
```

## 4. O QUE FOI FEITO NESTA SESSÃO (9 ondas concluídas)

| Onda | O que fez |
|---|---|
| 8 — CURADORIA | 45 tools ganharam fase, 3→2 eixos (profile removido), INV-04 implementado |
| R — RECONCILIAR | Gate git real, baseline atualizada, auditar.py C5 corrigido, tag agente2 |
| 1 — REGISTRY | Paridade registry≡server comprovada, gen_catalog.py corrigido, auditoria documentada |
| 2 — CONFORMIDADE | Hints MCP corrigidos (estavam None — bug Pydantic), _apply_hints refatorado |
| 3 — ROLLUPS | Colisão playtest_manage resolvida, 10 _manage classificados quarentena |
| 4 — DESCOBERTA | catalog_search retorna ops, describe_tool aceita op, guia AGENTS.md §1.5 |
| 9 — QUARENTENA | 19 tools em experimental/quarentena.json, critério de saída documentado |
| 10+P — CONGELAR | ARQUITETURA_MCP.md, LEARNINGS.md (5 causas-raiz), README corrigido |

## 5. CONVENÇÕES OBRIGATÓRIAS

- **Nunca commite sozinho.** Proponha e espere aprovação.
- **Prova sempre, nunca alegação.** `git diff` literal, output de teste completo.
- **Uma fatia por vez** (ou onda por vez, modo rápido). Nunca pule planejamento.
- **Rollup-first:** feature nova como `op` de `_manage`, nunca tool de topo.
- **Fonte antes de código:** leia `.github/instructions/fontes.instructions.md` antes de implementar.
- **Estado por projeto:** `<project_root>/.mcp_*_state.json`, nunca global.
- **Rede:** `127.0.0.1` apenas.
- **PowerShell:** `;` no lugar de `&&`.
- **`auditar.py`:** nunca altere para passar.

## 6. ARQUIVOS ESSENCIAIS (leia antes de qualquer ação)

1. `AGENTS.md` — fluxo de trabalho
2. `HANDOFF.md` — estado atual (este documento é gerado dele)
3. `docs/REORG_ROADMAP.md` — roadmap completo
4. `.github/instructions/aprendizados.instructions.md` — anti-padrões
5. `.github/instructions/fontes.instructions.md` — fontes de consulta
6. `.roadmap_progress.json` — progresso REAL (fonte única)
7. `docs/CURADORIA_PRECEDENCIA.md` — como os filtros funcionam
8. `docs/ARQUITETURA_MCP.md` — arquitetura documentada
9. `docs/LEARNINGS.md` — 5 causas-raiz de bugs

## 7. PRÓXIMA SESSÃO — PRIORIDADE #1

**Baixar o teto de tools por fase.** 5/6 fases excedem 40 tools.

Estratégia: **ONDA 5 — Migração de domínios.** Mover tools do `core/tool_definitions.py` para `domains/<x>/manifest.py`. Cada domínio declara suas tools e em qual fase elas aparecem. O registry descobre manifestos e filtra por fase, reduzindo o número de tools visíveis em cada fase.

## 8. CHECKLIST INICIAL (primeira ação da próxima IA)

```bash
git log -3 --oneline
git status --porcelain
.venv\Scripts\python -c "import server; print('OK, tools:', len(server._tool_defs()))"
.venv\Scripts\python -m pytest tests/ -q --ignore=tests/test_gate_reorg.py --tb=line 2>&1 | tail -5
.venv\Scripts\python scripts/gate_reorg.py --pre-commit
```

Se todos passarem, leia `HANDOFF.md` e prossiga com `/plan` para a ONDA 5.

## 9. PENDÊNCIAS CONHECIDAS

- 5/6 fases excedem teto de 40 tools (prioridade #1)
- 2 test_remix falhando (diretórios sujos — pré-existente, commit `996d588`)
- 7 xfails (INV-05 a INV-09, INV-14, INV-15) — implementar nas fases 2 e 4
- 26 menções "cline" em instalar*.py — limpeza cosmética
- .mcp_proof nunca exercitado — implementar prova real
- 10 _manage manuais sem rollup builder — ONDA 9 quarentena
- Branch agente2/behaviors-onda2 com 160 commits não mergeados

## 10. GIT

- **Branch:** `main`
- **Último commit:** `a585814` — chore: adiciona example_project/.mcp_* ao .gitignore
- **Remote:** origin — https://github.com/joabcostamd/mcp-godot-desenvolvimento
- **Sincronizado:** sim (main ↔ origin/main)
- **Worktree secundário:** `mcp-godot-agente02` (branch `agente2/trabalho`)
- **Tag:** `agente2/behaviors-onda2-archive`
