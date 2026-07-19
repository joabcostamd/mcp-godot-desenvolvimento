---
name: seguir-roadmap
description: Inicia o ciclo autônomo — planeja, implementa e audita a próxima etapa pendente
agent: agent
tools: ['read', 'search', 'edit', 'terminal', 'agent']
---

# Ciclo Autônomo de Desenvolvimento

Você é um agente do projeto MCP Godot. Siga este processo EXATO, sem pular etapas.

## ETAPA 0 — Identificação
1. Leia `ROADMAP_UNIFICADO.md` completamente
2. Identifique se você é AGENTE 01 (foco: server.py/core) ou AGENTE 02 (foco: tools/.github)
3. Se não conseguir identificar, PERGUNTE ao humano
4. Localize a PRÓXIMA etapa com status ⬜ na SUA zona

## ETAPA 1 — Contexto
5. Leia `HANDOFF.md` (se existir) — entenda o estado da última sessão
6. Leia `SUTURE_ISSUES.md` — verifique conflitos pendentes
7. Confirme que a etapa escolhida NÃO pisa em arquivos do outro agente
   (use a MATRIZ DE CONFLITO no ROADMAP)

## ETAPA 2 — Planejamento
8. Use o modo Plan Agent para pesquisar:
   - Os arquivos que serão modificados (listados na etapa)
   - Se há dependências não resolvidas
   - Se o código atual já contém trabalho parcial da etapa
9. Se encontrar BLOQUEIO → registre em `SUTURE_ISSUES.md` e PARE
10. Gere o plano da etapa em `/memories/session/plan.md`

## ETAPA 3 — Implementação
11. Implemente EXATAMENTE o que a etapa descreve — nada mais, nada menos
12. Respeite os limites de arquivo (exclusividade do agente)
13. A cada arquivo modificado, verifique:
    - Não removeu `# INTERNAL`
    - Não importou bridge quebrada (9080/9081/9001)
    - Não modificou tool depreciada em `tools/deprecated.py`

## ETAPA 4 — Auditoria
14. Rode a validação OBRIGATÓRIA:
    - AGENTE 01: `validate_tool_registry_consistency()`
    - AGENTE 02: `auditar.py` com critérios C1-C6
15. Se FAIL → corrija e repita a validação (máx 3 tentativas)
16. Se FAIL após 3 tentativas → registre em `SUTURE_ISSUES.md` e PARE

## ETAPA 5 — Handoff
17. Atualize `ROADMAP_UNIFICADO.md`:
    - Marque a etapa concluída como ✅
    - Adicione data de conclusão
18. Escreva/atualize `HANDOFF.md`:
    - O que foi feito (arquivos modificados, linhas alteradas)
    - O que NÃO foi feito (e por quê)
    - Decisões tomadas (e o racional)
    - ⚠️ Pontos de atenção para o outro agente
19. Atualize `NEXT_STEP.md`:
    - Próxima etapa do AGENTE 01: _____
    - Próxima etapa do AGENTE 02: _____
20. Faça commit: `feat(agente-X-etapa-Y): descrição em português`

## ETAPA 6 — Comunicação
21. Informe ao humano:
    - ✅ Etapa concluída: [nome]
    - 📁 Arquivos modificados: [lista]
    - 🔍 Validação: PASS/FAIL
    - ⚠️ Alertas para o outro agente: [se houver]
    - 🎯 Próxima etapa automática: [nome da próxima]
22. Pergunte: "Posso continuar para a próxima etapa ou você quer revisar?"
