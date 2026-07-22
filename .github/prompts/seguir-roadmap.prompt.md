---
name: seguir-roadmap
description: Inicia o ciclo autônomo — planeja, implementa e audita a próxima etapa pendente
agent: agent
tools: ['read', 'search', 'edit', 'terminal', 'agent']
---

# Ciclo Autônomo de Desenvolvimento

Você é um agente do projeto MCP Godot. Siga este processo EXATO, sem pular etapas.

## ETAPA 0 — Identificação
1. Leia `docs/ROADMAP_DEFINITIVO.md` completamente
2. Voce e o agente unico — opera em TODO o repositorio
3. Localize a PROXIMA etapa com status ⬜ no roadmap

## ETAPA 1 — Contexto
5. Leia `HANDOFF.md` (se existir) — entenda o estado da ultima sessao
6. Leia `docs/SUTURE_ISSUES.md` — verifique conflitos pendentes
7. Confirme que a etapa escolhida e viavel

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
14. Rode a validacao OBRIGATORIA:
    - `python auditar.py` com criterios C1-C6
    - `validate_tool_registry_consistency()` se disponivel
15. Se FAIL -> corrija e repita a validacao (max 3 tentativas)
16. Se FAIL apos 3 tentativas -> registre em `SUTURE_ISSUES.md` e PARE

## ETAPA 5 — Handoff
17. Atualize `docs/ROADMAP_DEFINITIVO.md`:
    - Marque a etapa concluida como ✅
    - Adicione data de conclusao
18. Escreva/atualize `HANDOFF.md`:
    - O que foi feito (arquivos modificados, linhas alteradas)
    - O que NAO foi feito (e por que)
    - Decisoes tomadas (e o racional)
    - Pontos de atencao para a proxima sessao
19. Atualize `.roadmap_progress.json`:
    - Proxima etapa: _____
20. Faca commit: `feat(etapa-Y): descricao em portugues`

## ETAPA 6 — Comunicacao
21. Informe ao humano:
    - ✅ Etapa concluida: [nome]
    - 📁 Arquivos modificados: [lista]
    - 🔍 Validacao: PASS/FAIL
    - 🎯 Proxima etapa automatica: [nome da proxima]
22. Pergunte: "Posso continuar para a proxima etapa ou voce quer revisar?"
