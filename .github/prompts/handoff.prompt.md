---
description: 'Escreve o resumo de passagem de bastao para a proxima sessao.'
mode: 'agent'
---

# /handoff — Passar o bastao

> Use este comando para um checkpoint rapido no meio da sessao ou ao trocar de tarefa. Para o fechamento completo do dia, com testes e auditoria, use /encerrar.

A proxima sessao **nao tem o seu historico de conversa**. So existe o que estiver
em arquivo. Este comando transforma o que voce sabe em algo que a proxima sessao consegue ler.

Use quando: terminar uma fatia, ou a sessao estiver ficando longa.

---

## PASSO 1 — Junte os fatos

```
git branch --show-current
git --no-pager log --oneline -5
git status --porcelain
```

Leia tambem `.roadmap_progress.json`.

---

## PASSO 2 — Escreva o arquivo

Atualize `HANDOFF.md` com uma nova secao de handoff
(exemplo: adicione `## Handoff — <data>` ao final de `HANDOFF.md`).

Use exatamente este formato. Seja curto: quem le quer saber onde pegar, nao ler um livro.

```markdown
## Handoff — <data>

### Onde estou
Branch: <branch>
Ultimo commit: <hash curto> <mensagem>
Arvore limpa: sim/nao

### O que eu terminei
- Fatia X.Y — <nome> — concluida e aprovada
- Fatia X.Z — <nome> — escalada, esperando decisao do humano

### O que ficou pendente
Descreva o estado exato, nao a intencao.
Errado: "vou terminar o dock"
Certo: "dock_v1.gd criado com as 3 zonas; falta ligar o botao Reverter ao git_checkpoint"

### Decisoes tomadas nesta sessao
Uma linha cada, com o motivo.

### Armadilhas que eu encontrei
O que quebrou e como contornei.

### Arquivos que eu toquei
Lista de caminhos.

### Proxima fatia sugerida
X.Y — <nome> — [AUTO|SENIOR]

### Como voltar atras
git reset --hard <hash>
```

---

## PASSO 3 — Confirme

Cole a secao adicionada ao `HANDOFF.md`.

`HANDOFF.md` e tracked pelo git — e o estado oficial do projeto.

---

## Regras

- Estado, nao intencao. "Falta X" vale; "vou fazer X" nao vale.
- Nao repita o que ja esta no roadmap. Handoff e o que mudou, nao o plano inteiro.
- Nao invente progresso. Se voce nao provou, escreva "nao provado".

