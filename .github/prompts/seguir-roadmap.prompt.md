---
description: 'Ciclo autônomo — planeja, implementa e valida etapas do roadmap. Aceita argumento: vazio (uma etapa), "onda" (bloco inteiro), "tudo" (roadmap inteiro até bloqueio real).'
mode: 'agent'
argument-hint: '<vazio | onda | tudo>'
---

# /seguir-roadmap — Ciclo Autônomo de Desenvolvimento

Você é o agente único do projeto MCP Godot. Siga este processo EXATO, sem pular etapas.

---

## ETAPA -1 — Determinar o modo

Determine o modo pelo argumento recebido:

- **Sem argumento ou 'uma':** Execute UMA etapa (comportamento padrão). Após concluir a etapa, faça handoff e pergunte ao humano se quer continuar. Não chame /audit automaticamente.
- **'onda':** Execute TODAS as etapas do bloco/onda atual do roadmap em sequência, sem parar para perguntar entre elas. Ao final do bloco, rode `/audit` (o comando de auditoria adversarial) sobre o conjunto de mudanças do bloco inteiro. Pare e reporte.
- **'tudo':** Execute etapas em sequência até o fim do roadmap. Ao final de CADA bloco/onda, rode `/audit` sobre aquele bloco antes de seguir para o próximo. Pare SÓ em bloqueio real ou fim do roadmap. Não pergunte ao humano durante o percurso.

Regras que valem em TODOS os modos:
- Bloqueio encontrado → PARE imediatamente (ETAPA 2.9).
- Falha após 3 tentativas de validação → PARE imediatamente (ETAPA 4.16).
- Cada etapa concluída SEMPRE registra handoff individual (ETAPA 5).
- Em 'onda' e 'tudo', o handoff individual é escrito, mas a pergunta ao humano é suprimida até o final do bloco.

---

## ETAPA 0 — Identificação

1. Leia `docs/ROADMAP_DEFINITIVO.md` completamente.
2. Você é o agente único — opera em TODO o repositório.
3. Localize a PRÓXIMA etapa com status ⬜ no roadmap.
4. No modo 'onda' ou 'tudo': identifique o bloco/onda INTEIRO (todas as etapas da onda atual), não só a primeira. Monte a lista de etapas do bloco ANTES de começar a implementar.

---

## ETAPA 1 — Contexto

5. Leia `HANDOFF.md` (se existir) — entenda o estado da última sessão.
6. Leia `docs/SUTURE_ISSUES.md` — verifique conflitos pendentes.
7. Confirme que a etapa escolhida é viável.

---

## ETAPA 2 — Planejamento

8. Use o modo Plan Agent para pesquisar:
   - Os arquivos que serão modificados (listados na etapa).
   - Se há dependências não resolvidas.
   - Se o código atual já contém trabalho parcial da etapa.
9. Se encontrar BLOQUEIO → registre em `docs/SUTURE_ISSUES.md` e PARE. (Vale em todos os modos, inclusive 'tudo'.)
10. Gere o plano da etapa em `/memories/session/plan.md`.

---

## ETAPA 3 — Implementação

11. Implemente EXATAMENTE o que a etapa descreve — nada mais, nada menos.
12. A cada arquivo modificado, verifique:
    - Não removeu `# INTERNAL`.
    - Não importou bridge quebrada (9080/9081/9001).
    - Não modificou tool depreciada em `tools/deprecated.py`.

---

## ETAPA 4 — Validação

13. Rode a validação OBRIGATÓRIA:
    - `python auditar.py` com critérios C1-C6.
    - `validate_tool_registry_consistency()` se disponível.
14. Se FAIL → corrija e repita a validação (máx 3 tentativas).
15. Se FAIL após 3 tentativas → registre em `docs/SUTURE_ISSUES.md` e PARE. (Vale em todos os modos, inclusive 'tudo'.)

---

## ETAPA 5 — Handoff (individual, roda SEMPRE após cada etapa)

16. Atualize `docs/ROADMAP_DEFINITIVO.md`:
    - Marque a etapa concluída como ✅.
    - Adicione data de conclusão.
17. Atualize `HANDOFF.md`:
    - O que foi feito (arquivos modificados, linhas alteradas).
    - O que NÃO foi feito (e por quê).
    - Decisões tomadas (e o racional).
    - Pontos de atenção para a próxima sessão.
18. Atualize `.roadmap_progress.json`:
    - Próxima etapa: _____.
19. Faça commit: `feat(etapa-Y): descrição em português`.

---

## ETAPA 6 — Comunicação (o que muda por modo)

### Modo 'uma' (padrão, sem argumento)

20. Informe ao humano:
    - ✅ Etapa concluída: [nome].
    - 📁 Arquivos modificados: [lista].
    - 🔍 Validação: PASS/FAIL.
    - 🎯 Próxima etapa automática: [nome da próxima].
21. Pergunte: "Posso continuar para a próxima etapa ou você quer revisar?"
22. **Pare** e aguarde resposta. NÃO continue sem confirmação.

### Modo 'onda'

20. Se ainda há etapas neste bloco → volte para ETAPA 0 com a PRÓXIMA etapa do mesmo bloco (sem perguntar ao humano, sem pausa).
21. Se esta foi a ÚLTIMA etapa do bloco:
    a. Rode `/audit` sobre o conjunto de mudanças do bloco inteiro.
    b. Informe ao humano:
       - 📦 Bloco concluído: [nome da onda].
       - 📁 Total de arquivos modificados no bloco: [lista].
       - 🔍 Validação por etapa: [resumo PASS/FAIL].
       - 🔎 Auditoria adversarial (/audit): [resultado].
       - 🎯 Próximo bloco: [nome da próxima onda].
    c. **Pare** e aguarde.

### Modo 'tudo'

20. Se esta foi a ÚLTIMA etapa de um bloco/onda → rode `/audit` sobre aquele bloco antes de seguir.
21. Se ainda há etapas no roadmap → volte para ETAPA 0 com a PRÓXIMA etapa (sem perguntar, sem pausa).
22. Se chegou ao FIM do roadmap (todas as etapas ✅) → informe o resumo completo e PARE.
23. Se encontrou BLOQUEIO real (ETAPA 2.9 ou 4.15) → registre, informe o ponto exato do bloqueio, e PARE. NÃO tente contornar — bloqueio é parede, não sugestão.

---

## 🚫 NUNCA (vale em todos os modos)

- Pular handoff individual de etapa.
- Ignorar bloqueio real — nem no modo 'tudo'.
- Continuar após 3 falhas de validação na mesma etapa.
- Remover `# INTERNAL` ou modificar `tools/deprecated.py`.
- Fazer commit sem a etapa passar na validação (ETAPA 4).
