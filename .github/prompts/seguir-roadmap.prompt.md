---
description: 'Ciclo autônomo — planeja, implementa e valida etapas do roadmap. Aceita argumento: vazio (uma etapa), "onda" (bloco inteiro), "tudo" (roadmap inteiro até bloqueio real), "tudo max=N" (com limite de ondas), "tudo sem-limite" (ignora teto).'
mode: 'agent'
argument-hint: '<vazio | onda | tudo | tudo max=N | tudo sem-limite>'
---

# /seguir-roadmap — Ciclo Autônomo de Desenvolvimento

Você é o agente único do projeto MCP Godot. Siga este processo EXATO, sem pular etapas.

---

## ETAPA -1 — Determinar o modo

Determine o modo pelo argumento recebido:

- **Sem argumento ou 'uma':** Execute UMA etapa (comportamento padrão). Após concluir a etapa, faça handoff e pergunte ao humano se quer continuar. Não chame /audit automaticamente.
- **'onda':** Execute TODAS as etapas do bloco/onda atual do roadmap em sequência, sem parar para perguntar entre elas. Ao final do bloco, execute a auditoria adversarial: use a ferramenta `runSubagent` para delegar a auditoria. Passe como instrução do subagente o CONTEÚDO INTEIRO de `.github/prompts/audit.prompt.md` (leia o arquivo primeiro e inclua o texto completo no prompt do subagente, não apenas o nome). Isso garante execução isolada e rigorosa do roteiro de 7 passos. Pare e reporte o resultado.
- **'tudo':** Execute etapas em sequência até o fim do roadmap. Ao final de CADA bloco/onda, execute a auditoria adversarial (use `runSubagent` com o conteúdo completo de `audit.prompt.md`, igual ao modo 'onda') sobre aquele bloco antes de seguir para o próximo. **Limite padrão: 5 ondas por chamada.** Ao completar a 5ª onda (ou quando o argumento especificar outro número, ex.: `tudo max=10`), pare e reporte, mesmo sem bloqueio real — isso é um check-in de segurança, não uma falha. O humano só precisa rodar `/seguir-roadmap tudo` de novo para continuar de onde parou (o `HANDOFF.md` já tem o estado). Se o argumento for `tudo sem-limite`, ignore o teto. Mantenha um contador de ondas completadas nesta execução, comparando com o limite.

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
    a. Execute a auditoria adversarial via `runSubagent` com o conteúdo completo de `audit.prompt.md` sobre o conjunto de mudanças do bloco inteiro.
    b. Informe ao humano:
       - 📦 Bloco concluído: [nome da onda].
       - 📁 Total de arquivos modificados no bloco: [lista].
       - 🔍 Validação por etapa: [resumo PASS/FAIL].
       - 🔎 Auditoria adversarial (runSubagent com audit.prompt.md): [resultado].
       - ⚠️ Se houver Bloqueantes na auditoria: destaque em NEGRITO no topo do relatório, não apenas como mais um item.
       - 🎯 Próximo bloco: [nome da próxima onda].
    c. **Pare** e aguarde.

### Modo 'tudo'

20. Se esta foi a ÚLTIMA etapa de um bloco/onda → execute a auditoria adversarial via `runSubagent` com o conteúdo completo de `audit.prompt.md` sobre aquele bloco antes de seguir.
21. **Regra de bloqueante:** Se o subagente de auditoria retornar QUALQUER achado classificado como Bloqueante, NÃO continue para o próximo bloco/onda. Registre os bloqueantes em `docs/SUTURE_ISSUES.md`, informe o humano, e PARE — com o mesmo peso de uma falha de validação (ETAPA 4.15).
22. Se atingiu o limite de ondas (padrão 5, ou o valor de `max=N`) → informe o progresso, registre handoff, e PARE (check-in de segurança).
23. Se ainda há etapas no roadmap E não há bloqueantes E não atingiu o limite → volte para ETAPA 0 com a PRÓXIMA etapa (sem perguntar, sem pausa).
24. Se chegou ao FIM do roadmap (todas as etapas ✅) → informe o resumo completo e PARE.
25. Se encontrou BLOQUEIO real (ETAPA 2.9 ou 4.15) → registre, informe o ponto exato do bloqueio, e PARE. NÃO tente contornar — bloqueio é parede, não sugestão.

---

## 🚫 NUNCA (vale em todos os modos)

- Pular handoff individual de etapa.
- Ignorar bloqueio real — nem no modo 'tudo'.
- Continuar para o próximo bloco com Bloqueante de auditoria pendente — nem no modo 'tudo'.
- Continuar após 3 falhas de validação na mesma etapa.
- Remover `# INTERNAL` ou modificar `tools/deprecated.py`.
- Fazer commit sem a etapa passar na validação (ETAPA 4).
