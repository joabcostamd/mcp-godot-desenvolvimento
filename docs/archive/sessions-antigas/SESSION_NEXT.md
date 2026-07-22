# 🔄 PRÓXIMA SESSÃO — MCP Godot Agent

## Resumo
Sessão de 20-jul-2026. Camada 6 implementada (38 tools, 8 fatias). ONDA 0: 7/12 fatias concluídas (0.A–0.G). 4 Lotes documentais instalados. 4 agentes Copilot criados. Comando /encerrar implementado.

## Estado
- Versão: 3.2.1 | Tools: 274 | Handlers: 295 | Rollups: 32
- Python 3.14, Godot 4.7, MCP stdio
- Camadas 0–6: ✅ (91/96 fatias). Camada 7: ⬜ [MARGINAL]
- ONDA 0: 0.A–0.G ✅ | 0.H implementado (aguarda teste com Godot) | 0.I–0.L ⬜

## Última tarefa
- Fatia 0.H — Protocolo anti-conflito MCP ↔ editor Godot (implementado, 2/4 cenários testados)

## Pendências
- [ ] 0.H: testar com Godot aberto (cena limpa + cena suja) — ALTA
- [ ] 0.I: Detectar pasta sincronizada — MÉDIA
- [ ] 0.J: Normalização de nome — MÉDIA
- [ ] 0.K: Guarda de propriedade intelectual — BAIXA
- [ ] 0.L: Bug set_node_property — MÉDIA

## Arquivos-chave
- server.py (entry point, call_tool integrado com editor_safety)
- core/tool_definitions.py (274 Tool() definitions)
- tools/editor_safety.py (novo — protocolo anti-conflito)
- scripts/docs_sync.py (gerador de números)
- .roadmap_progress.json (83 entradas)
- .github/roadmap/ONDA_0_destravar.md (próximas fatias)

## Fluxo sugerido
1. Leia .session/SESSION_NEXT.md
2. Rode `python scripts/docs_sync.py` (atualizar números)
3. Rode `/plan` para planejar 0.I
4. Se Godot aberto: teste 0.H antes de prosseguir

## Decisões da sessão
- MIT License escolhida para o projeto
- Fatia 0.7b rebaixada para MARGINAL (modo LEAN resolve na prática)
- ROADMAP_UNIFICADO.md movido para journal/
- 4 Lotes documentais instalados (.github/ reestruturado)

## ⚠️ Atenção
- `_tool_defs()` retorna None sem projeto ativo (bug pré-existente)
- PROTOTIPO tem 100 tools efetivas — monitorar
- 38 handlers da Camada 6 foram corrigidos (bug de nome de função)
- Editor safety integrado no call_tool — testar antes de deploy
- **GitHub API:** descricao NAO atualizada (HTTP 503)

## 🎮 Para o HUMANO
1. Execute `git stash list` — verifique o stash checkpoint-fatia-4.1
2. Decida se avanca para Camada 6 [MARGINAL] ou Camada 7 [MARGINAL]
3. Se avancar Camada 6, o AGENTE 02 precisa ativar as 28 tools no PHASE_TOOLSETS

## 🔧 Regras do projeto
- NUNCA edite arquivos do outro agente (matriz de conflito)
- Respeite `# INTERNAL:` — funcoes usadas por rollups
- 1 commit por etapa. Auditoria apos cada implementacao
- Conflitos em `SUTURE_ISSUES.md`, nao resolva sozinho
