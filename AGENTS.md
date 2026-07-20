
# AGENTS.md — Como as IAs trabalham neste repositório

> **Público:** IA agêntica (GitHub Copilot no VS Code).
> **O VS Code lê este arquivo automaticamente.** Ele vale para todo agente,
> em qualquer pasta de trabalho deste repositório.
> **Local correto:** raiz do repositório.

---

## 1. DESCUBRA QUEM VOCÊ É — FAÇA ISTO PRIMEIRO

Antes de qualquer coisa, rode:

```bash
git branch --show-current
```

| Branch | Você é | Território |
|---|---|---|
| `main` | **Agente 1 — Núcleo** | `server.py`, `tools/`, `.github/`, `docs/`, raiz |
| `agente2/*` | **Agente 2 — Conteúdo** | `behaviors/`, `blueprints/`, `seeds/`, `addons/`, `tests/` |

Se a branch não bater com nenhum padrão: **pare e pergunte ao humano.**

Se você é o único agente rodando (modo solo), você é o **Agente 1** e tem
todos os territórios. O fluxo é idêntico — nada muda.

---

## 2. TERRITÓRIOS (a regra que evita colisão)

A divisão é **por arquivo, não por assunto**. Isso importa: dois agentes podem
trabalhar no mesmo assunto desde que não toquem no mesmo arquivo.

### Agente 1 — Núcleo
```
server.py
tools/**
resources/**
auditar.py, install.py, launch.py
.github/**
docs/**
README.md, ROADMAP_DEFINITIVO.md, AGENTS.md, LICENSE
.roadmap_progress.json          ← EXCLUSIVO. Agente 2 nunca escreve aqui
```

### Agente 2 — Conteúdo
```
behaviors/**
blueprints/**
seeds/**
addons/**
tests/**
templates/**
.roadmap_progress_a2.json       ← o Agente 2 escreve aqui
```

### Terra de ninguém (exige combinação explícita)
`requirements.txt`, `pyproject.toml`, `.gitignore`, `CHANGELOG.md`

Quem precisar mexer nestes: **avise no pacote de escalação antes**, não depois.

---

## 3. AS 6 REGRAS DE CONVIVÊNCIA

**1. Nunca edite fora do seu território.**
Se a fatia exige tocar arquivo do outro, ela não é sua. Escale.

**2. Cheque conflito ANTES de terminar, não depois.**
```bash
git merge-tree $(git merge-base main HEAD) main HEAD
```
Saída vazia = sem conflito. Saída com marcadores = **pare e escale**.
Isolamento de pasta não elimina conflito, ele adia o conflito para o merge.
Você pode criar conflito com o outro agente sem perceber.

**3. Só o Agente 1 escreve em `.roadmap_progress.json`.**
O Agente 2 escreve em `.roadmap_progress_a2.json`. O Agente 1 consolida os dois
quando faz merge. Arquivo de estado é a causa número um de colisão.

**4. Nunca commite sozinha.** Proponha o commit ao humano com a mensagem sugerida
e espere aprovação. Vale para os dois agentes, sempre.

**5. Merge um de cada vez.** Nunca dois merges em paralelo.
Ordem: Agente 2 → `main`, resolver conflito, testar, só então o próximo.

**6. Passe o bastão por escrito.** Ao terminar uma fatia, rode `/handoff`.
O outro agente não tem o seu histórico de conversa — só o que estiver em arquivo.

---

## 4. COMO CRIAR O SEGUNDO AGENTE (humano faz isto uma vez)

Na pasta principal do repositório:

```bash
git worktree add ../mcp-agente2 -b agente2/trabalho
```

Isso cria uma pasta irmã completa, com o mesmo `.git` e todo o `.github/` junto —
por isso o Agente 2 herda estas regras automaticamente.

Abra uma segunda janela do VS Code em `../mcp-agente2`.

**Não use subpasta com um documento apontando para o MCP.** O VS Code só aplica
`.github/copilot-instructions.md` do workspace aberto; uma subpasta perderia todas
as regras. Worktree é pasta completa, por isso funciona.

Para desligar o segundo agente:
```bash
git worktree remove ../mcp-agente2
```

Quando existir apenas um agente, ele é o Agente 1 e nada mais muda.

---

## 5. FLUXO DE TRABALHO (idêntico para os dois)

```
/plan   → leio o roadmap, escolho a próxima fatia do MEU território,
          checo conflito com o outro agente, apresento o plano e PARO
  ↓
humano aprova
  ↓
/act    → implemento UMA fatia, rodo auditar.py, colo as provas,
          proponho o commit e PARO
  ↓
humano aprova
  ↓
/handoff → escrevo o resumo para o outro agente (ou para a próxima sessão)
```

Nunca pule `/plan`. Nunca faça duas fatias no mesmo `/act`.

---

## 6. MODO REVISOR ADVERSARIAL (opcional, para fatias críticas)

Em fatias marcadas `[SÊNIOR]` de alto risco, o humano pode pedir que o Agente 2
**audite** o trabalho do Agente 1 em vez de implementar a sua própria fatia.

Nesse modo o Agente 2 usa o agente customizado `revisor` e:
- não escreve código;
- roda `auditar.py` de forma independente;
- tenta **quebrar** a implementação, não confirmá-la;
- verifica se as provas coladas correspondem ao que o código realmente faz.

Custa metade da velocidade e ataca o problema número um do projeto:
evidência fabricada com confiança.

---

## 7. O QUE NUNCA FAZER

- Commitar sem aprovação humana.
- Editar arquivo fora do seu território.
- Fechar fatia `[SÊNIOR]` sozinha.
- Dizer "passou" sem colar o output real.
- Dizer "é bug pré-existente" sem `git blame` ou `git log -p` colado.
- Fazer duas fatias na mesma execução.
- "Melhorar" texto durante uma fatia de migração de documento.
- Redefinir os critérios de aceite no meio para caber no que você fez.

**Parar e escalar é sucesso. Insistir num loop é fracasso.**

