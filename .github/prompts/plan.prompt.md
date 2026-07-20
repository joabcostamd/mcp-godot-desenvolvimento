---
description: 'Planeja a proxima fatia do roadmap. Nao implementa nada.'
mode: 'agent'
---

# /plan — Planejar a proxima fatia

Voce vai **planejar e parar**. Nao escreva codigo. Nao edite arquivo.
Nao commite. O resultado deste comando e um plano na tela, mais nada.

---

## PASSO 1 — Descubra quem voce e

```
git branch --show-current
```

| Branch | Voce e | Territorio |
|---|---|---|
| `main` | Agente 1 — Nucleo | `server.py`, `tools/`, `resources/`, `.github/`, `docs/`, raiz |
| `agente2/*` | Agente 2 — Conteudo | `behaviors/`, `blueprints/`, `seeds/`, `addons/`, `tests/`, `templates/` |
| outra | **pare e pergunte ao humano** | — |

Se so existe um agente rodando, voce e o Agente 1 e tem todos os territorios.

Declare em uma linha: `Sou o Agente N. Territorio: ...`

---

## PASSO 2 — Leia o estado

Leia, nesta ordem:

1. [AGENTS.md](../../AGENTS.md) — regras de convivencia
2. [ROADMAP_DEFINITIVO.md](../../ROADMAP_DEFINITIVO.md) — ondas e fatias
3. `.roadmap_progress.json` (Agente 1) ou `.roadmap_progress_a2.json` (Agente 2)
4. A ficha da onda atual em `.github/roadmap/ONDA_*.md`
5. [aprendizados](../instructions/aprendizados.instructions.md) — o que ja quebrou antes

Se o arquivo de progresso nao existir, crie-o mentalmente como vazio
(nao escreva ainda — escrever e trabalho do `/act`).

---

## PASSO 3 — Escolha UMA fatia

Criterios, em ordem:

1. A onda anterior precisa estar fechada. Nao pule onda.
2. A fatia precisa estar no **seu** territorio.
3. As dependencias dela precisam estar concluidas.
4. Escolha a primeira que satisfaz 1, 2 e 3. Nao escolha a mais facil.
5. **Uma so.** Nunca planeje duas.

Se nao houver fatia elegivel no seu territorio: diga isso, liste o que esta
bloqueando, e pare.

---

## PASSO 4 — Cheque conflito com o outro agente

Se existir mais de um agente (verifique com `git worktree list`):

```
git merge-tree $(git merge-base main HEAD) main HEAD
```

- Saida vazia → sem conflito, siga.
- Saida com marcadores de conflito → **pare e escale.** Nao planeje esta fatia.

Alem disso: compare a lista de arquivos da sua fatia com a da fatia que o outro
agente esta executando. Se houver **qualquer** arquivo em comum, escale.
Isolamento de pasta nao elimina conflito, so adia para o merge.

---

## PASSO 5 — Apresente o plano

Use exatamente esta ficha de 10 campos, nesta ordem:

```markdown
## Fatia X.Y — <nome>

**1. O que e**
Uma frase.

**2. Por que agora**
Qual dependencia a torna possivel, ou qual dor a torna necessaria.

**3. Arquivos que toca**
Caminhos exatos, um por linha. Se um deles estiver fora do meu territorio, escalo.

**4. Fonte obrigatoria de consulta**
Qual documentacao/repositorio eu vou ler antes de escrever
(ver .github/instructions/fontes.instructions.md).

**5. Como fazer**
Passo a passo tecnico. A decisao de arquitetura ja vem tomada:
qual padrao, qual arquivo, qual funcao, qual assinatura.
Sem "vou avaliar a melhor forma" — decida agora ou escale agora.

**6. Armadilhas conhecidas**
O que quebra neste ponto especifico.

**7. Criterios de aceite**
Objetivos e verificaveis por codigo. Cada criterio vira passa/falha.
Se um criterio nao vira teste, ele nao e auto-avaliavel — marque [SENIOR].

**8. Como provar**
O comando exato que gera a evidencia.

**9. Regressao a retestar**
O que ja aprovado pode quebrar, e como confirmo que nao quebrou.

**10. Marcacao**
[AUTO] ou [SENIOR], com o motivo em uma linha.
```

**Regra da marcacao:**
- `[AUTO]` — todos os criterios do campo 7 sao verificaveis por comando.
- `[SENIOR]` — toca seguranca, arquitetura, contrato publico, migracao de dados,
  ou tem criterio que depende de julgamento. Na duvida, `[SENIOR]`.

---

## PASSO 6 — PARE

Termine com exatamente esta linha:

```
Plano pronto. Aguardando sua aprovacao para rodar /act.
```

Nao implemente. Nao pergunte se pode comecar. Nao ofereca alternativas.
Pare.

