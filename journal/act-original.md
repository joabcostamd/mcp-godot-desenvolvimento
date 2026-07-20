---
description: Implementa a fatia planejada, roda a autoauditoria pelo portão executável, verifica cross-model, grava o progresso e encadeia na próxima fatia [AUTO]. Roda no modo ACT.
---

# /act — Implementar, auditar e fechar a fatia

**Modo obrigatório: ACT.** Use o plano que ficou no contexto do `/plan`. Se não houver plano no contexto, pare e peça para o humano rodar `/plan` primeiro.

Execute em ordem. Marque as caixas conforme avança.

---

## Passo 1 — Ancorar o plano (evita deriva na troca de modo)

- [ ] Reescrever, em 3–5 linhas, o plano acordado: qual fatia, o que vai ser feito, quais os critérios de "pronto".
- [ ] Se o que você reescreveu não bate com o que foi planejado: **pare e avise.** Houve perda de contexto na troca de modo.

## Passo 2 — Checkpoint de segurança (antes de tocar em qualquer coisa)

- [ ] Criar checkpoint: `git stash push -u -m "checkpoint-fatia-<numero>"` **ou** branch `safety/fatia-<numero>`.
- [ ] **Não pede aprovação** — checkpoint é rede de segurança, não decisão (mestre 3.3).
- [ ] Confirmar que o checkpoint existe antes de prosseguir. Sem checkpoint, não implemente.

## Passo 3 — Capturar o estado "antes"

- [ ] Salvar `tools/list` (ou o `_tool_defs()` serializado) num arquivo temporário — base do critério C1.
- [ ] Registrar a contagem de tools de topo e por fase — base do C5.
- [ ] Rodar o `smoke_test` e salvar o resultado — base do C3 (você precisa saber o que passava ANTES).

## Passo 4 — Implementar

- [ ] Executar os passos do plano, um a um.
- [ ] Toda capacidade nova entra como **op de rollup** (mestre seção 2).
- [ ] **Se uma suposição do plano cair no meio: PARE** (Governador 4.9). Registre no progresso qual suposição caiu, e reporte ao humano para replanejar. Não conserte o plano em silêncio enquanto executa — essa é a deriva mais invisível que existe.
- [ ] Respeitar os freios o tempo todo: máximo 8 iterações; se a mesma ação falhar 2x, **pare** (não tente a terceira); se 3 passagens não gerarem progresso mensurável, **pare**.

## Passo 5 — Autoauditoria pelo portão

- [ ] **Se `auditar.py` já existir:** rodá-lo. **Exit code 0 = passou. Qualquer outra coisa = falhou.** Não interprete, não argumente, não "considere que passou". O que o script retornou é o que vale.
- [ ] **Se ainda não existir** (antes da Fatia 0.0.5): rodar os 6 critérios no nível declarado no plano (mestre seção 6, "critérios progressivos") e **registrar qual nível foi usado em cada um**.
- [ ] Se o script não conseguir rodar (ex.: `server.py` quebrado, import falhou): isso é **FALHA**, não "sem resultado". Silêncio nunca é aprovação.
- [ ] Se C3 (regressão) falhou: **rollback para o checkpoint do Passo 2** e escale. Não tente consertar por cima.

## Passo 6 — Verificação cross-model (Flash)

- [ ] Escolher e **declarar** qual forma foi usada (mestre seção 6):
  - **Forte** — abrir tarefa nova com o Flash, colando só o resultado e os critérios (recomendada para [SÊNIOR] e para qualquer fatia que mexa em código aprovado).
  - **Fraca** — subtarefa dentro deste `/act` (aceitável em [AUTO] triviais).
- [ ] Se o Flash reprovar onde você aprovou: **escale.** Divergência é sinal, não ruído.

## Passo 7 — Gravar o progresso (nunca pule este passo)

Este passo é o que impede a inconsistência entre fatias.

- [ ] Escrever em `.roadmap_progress.json` (append-only, fora do git):
  - fatia, data, resultado (passou/falhou/escalada)
  - passos concluídos
  - qual nível de critério foi usado em cada um dos 6
  - qual verificação cross-model foi usada (forte/fraca)
  - tentativas feitas e o que falhou em cada uma
  - orçamento consumido
- [ ] Se falhou: registrar **a abordagem que falhou**, para a próxima tentativa não repeti-la.

## Passo 8 — Fechar ou escalar

### Se TUDO passou e a fatia é [AUTO]:
- [ ] Atualizar `.clinerules/00-mestre.md`: marcar a fatia como concluída.
- [ ] **Propor** o commit ao humano com a mensagem sugerida. **Nunca commitar sozinha** (mestre 3.3).
- [ ] Descartar o checkpoint de segurança (não é mais necessário).
- [ ] **Encadear:** preparar o plano da próxima fatia (rodar internamente o conteúdo do `/plan`: ler progresso, escolher a próxima, verificar suposições, definir "pronto") e apresentá-lo.
- [ ] Terminar **exatamente** assim:

> **"Fatia <N> concluída e auditada. Commit proposto acima, aguardando sua aprovação. Plano da próxima fatia (<N+1>) pronto abaixo. Digite `/act` para seguir."**

### Se a fatia é [SÊNIOR], OU qualquer critério falhou, OU o Flash divergiu:
- [ ] **NÃO feche. NÃO encadeie.**
- [ ] Montar o pacote de escalação completo (mestre 4.10), incluindo obrigatoriamente:
  1. número, nome e marcação da fatia
  2. **o trecho do documento da camada, colado** (quem revisar não terá seu contexto)
  3. os critérios de aceite definidos antes de começar
  4. o que passou e o que falhou, com output real e curto
  5. as tentativas já feitas (do arquivo de progresso)
  6. sua hipótese de causa
  7. a pergunta específica que precisa ser respondida
- [ ] Terminar assim:

> **"Fatia <N> precisa de revisão. Pacote de escalação acima. Não vou prosseguir até sua confirmação."**

---

## Regras que valem o tempo todo neste workflow

- **"Pronto" é o que o portão retornou, nunca o que você acha.** Um agente que fabrica conclusão é tipicamente confiante — por isso quem decide é código.
- **Nunca redefina os critérios no meio** para caber no que você fez.
- **Alegação exige prova:** "é bug pré-existente" / "sem relação com a fatia" só vale com `git blame` ou `git log -p`, output colado.
- **Prova enxuta:** teste que afirma + resultado curto. Nunca colar centenas de linhas por padrão.
- **Nunca faça duas fatias na mesma execução**, exceto o encadeamento explícito do Passo 8 (que só prepara o plano da próxima, não a implementa).
- Se a fatia se mostrar grande demais: proponha dividir em duas e escale. Não force.
