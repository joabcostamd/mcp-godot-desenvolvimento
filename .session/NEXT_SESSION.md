# 🔄 PRÓXIMA SESSÃO — MCP Godot Agent

## Resumo
ONDA 0: 12/12 concluída. ONDA 1: 5/17 (1.A–1.E) concluídas.
Iniciado suporte multi-cliente, orçamento de tokens, dock visual v2 com 14 melhorias UX.
Pesquisa externa documentada (MCP Spec, Godot Docs, Apple HIG, Material Design 3).

## Estado
- Versão: 275 tools, 296 handlers
- Branch: main
- Último commit: 761d103 (dock v2 + pesquisa externa)
- Progresso ONDA 1: 5/17 (29%)

## Última tarefa
- 1.E — Dock v2 com 14 melhorias UX + P3 (sub-plugins) + P4 (@export)
- Pendente de commit: dock.gd, dock.tscn, mcp_addon.gd, PESQUISA_EXTERNA.md

## Pendências
- [ ] Commitar arquivos pendentes (ALTA)
- [ ] 1.F — Erro amigável universal [AUTO]
- [ ] 1.G — Reestruturação documental [SÊNIOR]
- [ ] 1.H a 1.Q — Restante da ONDA 1

## Arquivos-chave
- init.py — instalador de 1 comando
- tools/budget_ops.py — orçamento de tokens
- addons/mcp_dock/dock.gd — dock visual (717 linhas)
- docs/PESQUISA_EXTERNA.md — referência técnica

## Fluxo sugerido
1. Commite os pendentes: `git add -A && git commit -m "..." && git push`
2. Rode `/plan` para 1.F
3. Continue o desenvolvimento

## Decisões da sessão
- Preços DeepSeek V4 como estimativas (~R$0.003/1K input, ~R$0.010/1K output)
- Dock segue padrão Godot oficial (add_control_to_dock)
- Sub-plugins: mcp_addon auto-gerencia mcp_dock

## ⚠️ Atenção
- Agente 2 ativo em agente2/behaviors-onda2 — verificar merge-tree antes de cada fatia
- C1/C5 do auditar.py pré-existentes (7 breaking, 8 fases overflow)
- Dock não testado com Godot editor aberto (validado apenas por sintaxe)
