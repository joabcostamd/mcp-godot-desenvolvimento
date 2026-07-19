---
description: "Use when: implementar a fatia planejada pelo /plan, rodar autoauditoria (C1-C6), verificar cross-model, gravar progresso no roadmap e fechar ou escalar. Este é o comando /act."
---
# /act — Implementar, auditar e fechar a fatia

**Modo: Execução.** Use o plano que ficou no contexto do `/plan`. Se não houver plano no contexto, pare e peça para o humano rodar `/plan` primeiro.

Execute em ordem.

---

## Passo 1 — Ancorar o plano (evita deriva entre comandos)

1. Reescrever, em 3–5 linhas, o plano acordado: qual fatia, o que vai ser feito, quais os critérios de "pronto".
2. Se o que você reescreveu não bate com o que foi planejado: **pare e avise.** Houve perda de contexto entre comandos.

## Passo 2 — Checkpoint de segurança (antes de tocar em qualquer coisa)

1. Criar checkpoint: `git stash push -u -m "checkpoint-fatia-<numero>"` **ou** branch `safety/fatia-<numero>`.
2. **Não peça aprovação** — checkpoint é rede de segurança, não decisão.
3. Confirmar que o checkpoint existe antes de prosseguir. Sem checkpoint, não implemente.

Comando PowerShell:
```powershell
git stash push -u -m "checkpoint-fatia-<numero>"
```

## Passo 3 — Capturar o estado "antes"

1. Salvar `tools/list` (ou o `_tool_defs()` serializado) num arquivo temporário — base do critério C1.
2. Registrar a contagem de tools de topo e por fase — base do C5.
3. Rodar o `smoke_test` e salvar o resultado — base do C3 (você precisa saber o que passava ANTES).

## Passo 4 — Implementar

1. Executar os passos do plano, um a um.
2. Toda capacidade nova entra como **op de rollup** — NÃO como tool de topo, a menos que justificado no plano.
3. **Se uma suposição do plano cair no meio: PARE.** Registre qual suposição caiu e reporte ao humano para replanejar. Não conserte o plano em silêncio enquanto executa.
4. Respeitar os freios: máximo 8 iterações de edição; se a mesma ação falhar 2x, **pare** (não tente a terceira); se 3 passagens não gerarem progresso mensurável, **pare**.

## Passo 5 — Autoauditoria pelo portão

### Se `auditar.py` existir no projeto:

Rodar o script. **Exit code 0 = passou. Qualquer outra coisa = falhou.** Não interprete, não argumente, não "considere que passou".

Comando PowerShell:
```powershell
python auditar.py --fatia <numero>
```

### Se `auditar.py` ainda NÃO existir:

Rodar os 6 critérios no nível declarado no plano e **registrar qual nível foi usado em cada um**:

| # | Nome | Verificação |
|---|---|---|
| C1 | Contrato | Comparar snapshots `tools/list` antes/depois. Só a tool/op nova deve aparecer no diff. |
| C2 | Canary | Executar as 2-3 chamadas canary definidas no plano. Saída deve bater com o esperado. |
| C3 | Regressão | Rodar `smoke_test`. Nada que passava antes pode quebrar. Se quebrou → rollback para checkpoint. |
| C4 | Segurança | Checklist: loopback bind (127.0.0.1), checkpoint git feito, sem vazamento de segredo, passou por rollup, operação idempotente. |
| C5 | Orçamento | Contar tools de topo (≤40/fase, ≤70 total). Se estourou → escalar. |
| C6 | Distinguibilidade | Buscar colisão de nome: a tool nova não pode se confundir com nenhuma existente. |

Se o script não conseguir rodar (ex.: `server.py` quebrado, import falhou): isso é **FALHA**, não "sem resultado". Silêncio nunca é aprovação.

Se C3 (regressão) falhou: **rollback para o checkpoint do Passo 2** e escale. Não tente consertar por cima.

## Passo 6 — Verificação cross-model

1. Escolher e **declarar** qual forma será usada:
   - **Forte** — sugerir ao humano abrir outro chat com um modelo diferente (ex: Claude) e colar o resultado + critérios para revisão independente.
   - **Fraca** — revisão interna no mesmo chat (aceitável para fatias [AUTO] triviais).
2. Se houver divergência: **escale.** Divergência entre modelos é sinal, não ruído.

Sugestão para o humano:
> "Recomendo abrir um chat com outro modelo e pedir: 'Revise esta implementação da fatia <N>: [resultado] [critérios C1-C6] [diffs].'"

## Passo 7 — Gravar o progresso (nunca pule este passo)

Escrever em `.roadmap_progress.json` (append-only, fora do git):

```json
{
  "fatia_<N>": {
    "status": "<concluida|falhou|escalada>",
    "data": "<YYYY-MM-DD>",
    "tentativa": <numero>,
    "resultado": "<descrição curta do que foi feito e resultado>",
    "c1": "<pass|fail|skipped> — <detalhe>",
    "c2": "<pass|fail|skipped> — <detalhe>",
    "c3": "<pass|fail|skipped> — <detalhe>",
    "c4": "<pass|fail|skipped> — <detalhe>",
    "c5": "<pass|fail|skipped> — <detalhe>",
    "c6": "<pass|fail|skipped> — <detalhe>",
    "cross_model": "<forte|fraca> — <resultado>"
  }
}
```

Se falhou: registrar **a abordagem que falhou**, para a próxima tentativa não repeti-la.

Use `read_file` para ler o JSON atual, modifique em memória, e `replace_string_in_file` ou `create_file` para gravar. **Nunca sobrescreva entradas existentes** — o arquivo é append-only.

## Passo 8 — Fechar ou escalar

### ✅ Se TUDO passou e a fatia é [AUTO]:

1. Marcar a fatia como concluída no progresso.
2. **Propor** o commit ao humano com a mensagem sugerida. **Nunca commitar sozinho.**
3. Descartar o checkpoint de segurança (`git stash drop` ou deletar branch).
4. **Encadear:** preparar o plano da próxima fatia (seguir os passos do `/plan`: ler progresso, escolher a próxima, verificar suposições, definir "pronto") e apresentá-lo.
5. Terminar **exatamente** assim:

> **"Fatia <N> concluída e auditada. Commit proposto acima, aguardando sua aprovação. Plano da próxima fatia (<N+1>) pronto abaixo. Digite `/act` para seguir."**

### ❌ Se a fatia é [SÊNIOR], OU qualquer critério falhou, OU houve divergência cross-model:

1. **NÃO feche. NÃO encadeie.**
2. Montar o **pacote de escalação** completo:
   - Número, nome e marcação da fatia
   - O trecho do documento da camada, colado (quem revisar não terá seu contexto)
   - Os critérios de aceite definidos antes de começar
   - O que passou e o que falhou, com output real e curto
   - As tentativas já feitas (do arquivo de progresso)
   - Sua hipótese de causa
   - A pergunta específica que precisa ser respondida
3. Terminar assim:

> **"Fatia <N> precisa de revisão. Pacote de escalação acima. Não vou prosseguir até sua confirmação."**

---

## Regras que valem o tempo todo neste comando

- **"Pronto" é o que o portão retornou, nunca o que você acha.** Quem decide é o código/script.
- **Nunca redefina os critérios no meio** para caber no que você fez.
- **Alegação exige prova:** "é bug pré-existente" / "sem relação com a fatia" só vale com `git blame` ou `git log -p`, output colado.
- **Prova enxuta:** teste que afirma + resultado curto. Nunca colar centenas de linhas por padrão.
- **Nunca faça duas fatias na mesma execução**, exceto o encadeamento explícito do Passo 8 (que só prepara o plano da próxima, não a implementa).
- Se a fatia se mostrar grande demais: proponha dividir em duas e escale. Não force.
