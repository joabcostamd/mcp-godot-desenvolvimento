---
description: 'Escreve o resumo de passagem de bastao para o outro agente ou para a proxima sessao.'
mode: 'agent'
---

# /handoff — Passar o bastao

O outro agente **nao tem o seu historico de conversa**. So existe o que estiver
em arquivo. Este comando transforma o que voce sabe em algo que ele consegue ler.

Use quando: terminar uma fatia, trocar de agente, ou a sessao estiver ficando longa.

---

## PASSO 1 — Junte os fatos

```
git branch --show-current
git --no-pager log --oneline -5
git status --porcelain
```

Leia tambem `.roadmap_progress.json` e `.roadmap_progress_a2.json`
(os dois, para saber o que o outro agente andou fazendo).

---

## PASSO 2 — Escreva o arquivo

Crie ou sobrescreva `journal/HANDOFF_<agente>.md`
(exemplo: `journal/HANDOFF_agente1.md`).

Use exatamente este formato. Seja curto: quem le quer saber onde pegar, nao ler um livro.

```markdown
# HANDOFF — Agente <N> — <data>

## Onde estou
Branch: <branch>
Ultimo commit: <hash curto> <mensagem>
Arvore limpa: sim/nao

## O que eu terminei
- Fatia X.Y — <nome> — concluida e aprovada
- Fatia X.Z — <nome> — escalada, esperando decisao do humano

## O que ficou pendente
Descreva o estado exato, nao a intencao.
Errado: "vou terminar o dock"
Certo: "dock_v1.gd criado com as 3 zonas; falta ligar o botao Reverter ao git_checkpoint"

## Decisoes tomadas nesta sessao
Uma linha cada, com o motivo. Isto evita que o proximo agente desfaca sem saber.

## Armadilhas que eu encontrei
O que quebrou e como contornei. Se for regra nova, ela tambem vai para
aprendizados.instructions.md — aqui e so o aviso rapido.

## Arquivos que eu toquei
Lista de caminhos. O outro agente usa isto para checar conflito.

## Proxima fatia sugerida
X.Y — <nome> — [AUTO|SENIOR]

## Como voltar atras
git reset --hard <hash>
```

---

## PASSO 3 — Avise sobre conflito

Se voce tocou em algum arquivo do territorio do outro agente, ou em algum arquivo
de terra de ninguem (`requirements.txt`, `pyproject.toml`, `.gitignore`,
`CHANGELOG.md`), **escreva isso em negrito no topo do handoff**.

---

## PASSO 4 — Confirme

Cole o caminho do arquivo criado e as 10 primeiras linhas dele.

`journal/` esta no `.gitignore`, entao este arquivo nao vai para o repositorio
publico — e proposital. Ele e nota de trabalho, nao documentacao.

---

## Regras

- Estado, nao intencao. "Falta X" vale; "vou fazer X" nao vale.
- Nao repita o que ja esta no roadmap. Handoff e o que mudou, nao o plano inteiro.
- Nao invente progresso. Se voce nao provou, escreva "nao provado".

