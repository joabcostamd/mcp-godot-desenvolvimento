
# AGENTS.md — Como o agente trabalha neste repositório

> **Público:** IA agêntica (GitHub Copilot no VS Code).
> **Modelo:** agente nativo + comandos `/`. Não há mais agentes personalizados.
> **O VS Code lê este arquivo automaticamente.**
> **Local correto:** raiz do repositório.
> **Infraestrutura:** Este projeto roda em dois worktrees do mesmo repositório:
> `mcp-godot-desenvolvimento` (agente principal) e `mcp-godot-agente02`
> (segundo agente, trabalho paralelo). Os dois compartilham histórico Git.
> Coordenação automática via `coordenacao.json` na pasta `.git` comum —
> nenhum agente escolhe etapa já reivindicada pelo outro. Sincronização
> ao final de cada onda (ver `/seguir-roadmap`).

---

## 1. VOCÊ É O AGENTE ÚNICO

Não há mais Agente 1 / Agente 2. Você opera em **todo o repositório**,
sem divisão de território. Use os comandos `/` para mode-switching:

| Comando | Função |
|---|---|
| `/plan` | Planeja a próxima fatia e para |
| `/act` | Implementa UMA fatia, prova, propõe commit e para |
| `/handoff` | Escreve resumo de estado em `HANDOFF.md` |
| `/audit` | Audita o trabalho feito (adversarial, não corrige) |
| `/encerrar` | Encerramento completo: audita, documenta, commita |
| `/manual` | Gera manual do usuário a partir do código |
| `/seguir-roadmap` | Ciclo autônomo: 3 modos — `uma` (padrão, 1 etapa), `onda` (bloco inteiro + runSubagent /audit), `tudo` (até o fim/bloqueio/limite; padrão max=5 ondas, use `tudo max=N` ou `tudo sem-limite`) |

---

## 2. TODO O REPOSITÓRIO É SEU TERRITÓRIO

```
server.py, core/, tools/, resources/, domains/, registry/
behaviors/, blueprints/, seeds/, addons/, tests/, templates/
.github/, docs/, journal/, scripts/
auditar.py, install.py, launch.py
README.md, HANDOFF.md, AGENTS.md, LICENSE
.roadmap_progress.json
```
blueprints/**
seeds/**
addons/**
tests/**
templates/**
.roadmap_progress_a2.json       ← o Agente 2 escreve aqui
```

### Terra de ninguém (exige combinação explícita)
`requirements.txt`, `pyproject.toml`, `.gitignore`, `CHANGELOG.md`

---

## 3. AS 6 REGRAS DE CONVIVÊNCIA (agora simplificadas)

Como não há mais divisão de território entre agentes:

**1. Nunca pule auditoria.** Rode `auditar.py` antes de propor commit.

**2. Checkpoint antes de qualquer operação destrutiva.** `git rev-parse HEAD`.

**3. Nunca commite sozinho.** Proponha o commit e espere aprovação.

**4. Passe o bastão por escrito.** Ao terminar fatia, rode `/handoff` para
atualizar `HANDOFF.md`. A próxima sessão não tem seu histórico de conversa.

**5. Um commit de cada vez.** Nunca dois commits em paralelo em branches diferentes.

**6. Estado único.** Só existe `.roadmap_progress.json`. Não há mais
`.roadmap_progress_a2.json`.

---

## 4. FLUXO DE TRABALHO

```
/plan   → leio o roadmap, escolho a próxima fatia, apresento o plano e PARO
  ↓
humano aprova
  ↓
/act    → implemento UMA fatia, rodo auditar.py, colo as provas,
          proponho o commit e PARO
  ↓
humano aprova
  ↓
/handoff → escrevo o resumo em HANDOFF.md para a próxima sessão
```

**Nunca pule `/plan`. Nunca faça duas fatias no mesmo `/act`.**

---

## 5. MODO REVISOR ADVERSARIAL

Para auditar o trabalho feito sem corrigir nada:

```
/audit
```

O comando `/audit` (`.github/prompts/audit.prompt.md`) executa o revisor adversarial:
- não escreve código;
- roda `auditar.py` de forma independente;
- tenta **quebrar** a implementação, não confirmá-la;
- verifica se as provas coladas correspondem ao que o código realmente faz.

---

## 6. O QUE NUNCA FAZER

- Commitar sem aprovação humana.
- Fechar fatia `[SÊNIOR]` sozinha.
- Dizer "passou" sem colar o output real.
- Dizer "é bug pré-existente" sem `git blame` ou `git log -p` colado.
- Fazer duas fatias na mesma execução.
- "Melhorar" texto durante uma fatia de migração de documento.
- Redefinir os critérios de aceite no meio para caber no que você fez.

**Parar e escalar é sucesso. Insistir num loop é fracasso.**

