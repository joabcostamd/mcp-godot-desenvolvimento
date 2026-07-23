# 🚀 PROMPT DE CONTINUIDADE — REDUÇÃO DE TETO DE TOOLS

**Data:** 2026-07-23 · **Commit:** `bd53e0b` · **Branch:** `main`
**Foco da sessão:** Pesquisar e implementar redução do teto de tools por fase.

---

## CONTEXTO RÁPIDO

Projeto: MCP Godot Agent — servidor MCP em Python que controla o desenvolvimento de jogos Godot.
Stack: Python 3.14, MCP SDK, Godot 4.7, Pydantic v2.

**Estado atual:**
- 233 tools ativas, 191 depreciadas
- 6 fases (IDEIA→PRONTO_PARA_LANCAR), 5 namespaces
- **Problema:** 5/6 fases excedem teto de 40 tools visíveis:
  - IDEIA: 63 · DESIGN: 82 · PROTOTIPO: 39 ✅ · CONTEUDO: 88 · POLIMENTO: 67 · PRONTO: 41
- CORE tem 25 tools (sempre visíveis)
- 12 _manage tools definidas manualmente em core/tool_definitions.py (sem rollup builder)
- Registry existe como infra mas é proxy circular do legado
- 19 tools em quarentena (experimental/quarentena.json)
- Hints MCP corrigidos (ONDA 2.1)
- Gate pre-commit funcional, auditoria passa (exit 0)
- Testes: 157 passed, 2 pré-existentes, 7 xfailed

## SUA MISSÃO NESTA SESSÃO

### Fase 1: Pesquisa (obrigatório — NÃO pule)

1. **Estado da arte em curadoria de tools para LLMs** (Claude Code, Cursor, Copilot, Aider)
2. **MCP Specification** (list_tools, tool_list_changed, deferLoading)
3. **Padrões enterprise** (GraphQL introspection, OpenAPI tags, BFF, API Gateway)
4. **O que já existe no projeto** (registry/, catalog_search, create_manage_tool, domains/)
5. **5 estratégias avaliadas:** A) Domínios B) Lazy loading C) Compressão D) Cumulativa E) Híbrida

### Fase 2: Plano → Fase 3: Execução

## CHECKLIST INICIAL

```bash
git log -3 --oneline && git status --porcelain
.venv\Scripts\python -c "import server; print(len(server._tool_defs()))"
.venv\Scripts\python -m pytest tests/ -q --ignore=tests/test_gate_reorg.py --tb=line 2>&1 | tail -5
.venv\Scripts\python scripts/gate_reorg.py --pre-commit
```

## ARQUIVOS ESSENCIAIS

`HANDOFF.md` · `docs/ARQUITETURA_MCP.md` · `docs/REORG_ROADMAP.md` · `docs/CURADORIA_PRECEDENCIA.md` · `docs/LEARNINGS.md` · `.roadmap_progress.json` · `AGENTS.md`
