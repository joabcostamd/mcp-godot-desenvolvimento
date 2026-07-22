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

**Worktree/Agente:** <resultado de git rev-parse --show-toplevel>
**Peso:** O que aconteceu nos ultimos minutos da sessao merece mais detalhe;
  o que aconteceu no inicio pode ser resumido em 1 linha ou omitido se ja
  esta no roadmap.

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

### Contexto que nao esta no codigo (nao mexer sem saber disso)
O que um agente novo mexeria por engano se nao soubesse: convencoes nao obvias,
 decisoes de arquitetura que parecem estranhas mas sao propositais, partes que
 parecem redundantes mas nao sao. Se nada se aplica, escreva 'nada alem do que
 ja esta documentado nas instructions'.

### Decisoes que so um humano pode tomar (separado de pendencia tecnica)
Pergunta em aberto que precisa da palavra do usuario, nao de mais trabalho de
 agente. Se nao houver nenhuma, escreva 'nenhuma'.

### Arquivos que eu toquei
Lista de caminhos.

### Proxima fatia sugerida
X.Y — <nome> — [AUTO|SENIOR]

### Como voltar atras
git reset --hard <hash>
```

---

## PASSO 2.5 — Varredura de seguranca rapida

Antes de confirmar o handoff, rode:
```
git diff --cached -- HANDOFF.md | Select-String -Pattern 'api[_-]?key|password|secret|token' -CaseSensitive:$false
```
Se encontrar QUALQUER ocorrencia, NAO grave o handoff — pare e avise o usuario
qual linha disparou o alerta.

---

## PASSO 3 — Confirme

Cole a secao adicionada ao `HANDOFF.md`.

`HANDOFF.md` e tracked pelo git — e o estado oficial do projeto.

---

## Regras

- Estado, nao intencao. "Falta X" vale; "vou fazer X" nao vale.
- Nao repita o que ja esta no roadmap. Handoff e o que mudou, nao o plano inteiro.
- Nao invente progresso. Se voce nao provou, escreva "nao provado".

