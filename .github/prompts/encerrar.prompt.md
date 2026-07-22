---
description: 'Encerramento profissional de sessão. Audita, documenta, commita e prepara qualquer projeto para a próxima sessão sem perda de contexto. Universal — adapta-se automaticamente à estrutura do projeto.'
mode: 'agent'
agentMode: true
user-invocable: true
---

# /encerrar — Protocolo Universal de Encerramento

Pipeline de 15 fases. Cada fase: pré-condições → execução → validação → tratamento de erro. Uma fase só avança se a anterior concluir. Erro crítico registra e segue nas fases independentes.

**Universal:** funciona em qualquer projeto — Python, JS, Godot, Rust, Go, web, CLI. Sem caminho fixo, sem nome fixo, sem suposição.

---

## ⚡ REGRAS UNIVERSAIS

1. **Descubra, não suponha.** Toda informação vem de varredura real do workspace.
2. **Idempotente.** Rodar 2x não duplica nada. Verifique antes de criar.
3. **Fail-safe.** Erro em fase X não corrompe o projeto nem bloqueia fases independentes.
4. **Nada de ficção.** Zero dado inventado. Se não sabe, escreva "não disponível".
5. **100% automático.** Commit, push, documentação, memória — tudo executado sem parar. Zero confirmação.

---

## 🔍 FASE 1 — DESCOBERTA

**Pré-condição:** workspace aberto.

**Execução:**
```
1. Liste a raiz: dir/ls
2. Detecte arquivos-chave: package.json, Cargo.toml, go.mod, requirements.txt, pyproject.toml, project.godot, CMakeLists.txt, Makefile, Dockerfile
3. Detecte pastas: src/, lib/, app/, pkg/, cmd/, internal/, tools/, scripts/, .github/, docs/, tests/
4. Detecte docs: README*, CHANGELOG*, TODO*, ROADMAP*, BACKLOG*, CONTRIBUTING*, LICENSE*
5. Detecte memória: /memories/, .session/, journal/, .vscode/, .cursor/
6. Detecte CI/CD: .github/workflows/, .gitlab-ci.yml, Jenkinsfile, azure-pipelines.yml
7. Detecte MCPs/Prompts: .github/prompts/, .github/agents/, .cursor/rules/, .windsurf/
```

**Saída obrigatória:** tabela com Linguagem, Framework, Build System, Test Runner, Linter, Docs, CI/CD.

**Validação:** pelo menos Linguagem e Framework preenchidos.

**Erro:** workspace vazio → registre, execute apenas fases sem dependência de código.

---

## 🔎 FASE 2 — AUDITORIA

**Pré-condição:** Fase 1 OK.

**Execução:**
```
git --no-pager log --oneline -10 2>/dev/null || echo "git indisponivel"
git --no-pager diff --stat HEAD~1 HEAD 2>/dev/null || echo "sem diff"
git status --porcelain 2>/dev/null || dir / ls -la
```

**Saída obrigatória:** tabela com:
- Arquivos criados / modificados / removidos
- Funcionalidades novas, bugs corrigidos, bugs conhecidos
- TODOs, dívida técnica, limitações
- Decisões arquiteturais tomadas na sessão
- Dependências novas/removidas, breaking changes
- Pendências e próximos passos

**Validação:** tabela cobre todas as categorias.

**Erro:** sem git → use comparação manual de timestamps.

---

## ✅ FASE 3 — VALIDAÇÃO

**Pré-condição:** Fase 1 OK.

**Execução:**
Detecte e execute APENAS o que existir:

| Detectado | Execute |
|---|---|
| `package.json` + `"test"` script | `npm test` |
| `Cargo.toml` | `cargo test`, `cargo clippy` |
| `go.mod` | `go test ./...`, `go vet ./...` |
| `requirements.txt` / `pyproject.toml` | `pytest` ou `python -m pytest` |
| `project.godot` | `godot --headless --quit` |
| `.eslintrc*` / `eslint.config.*` | `eslint .` |
| `ruff.toml` / `pyproject.toml[tool.ruff]` | `ruff check .` |
| `py_compile` (sempre disponível em Python) | Compile os .py modificados |
| `tsconfig.json` | `tsc --noEmit` |
| `Makefile` com target `test` | `make test` |

**Regra:** passar = ✅. Falha segura = corrija. Falha crítica = registre, NÃO corrija.

**Validação:** cada ferramenta detectada foi executada e seu resultado registrado.

**Erro:** ferramenta não instalada → registre "não disponível", continue.

---

## 📝 FASE 4 — DOCUMENTAÇÃO

**Pré-condição:** Fases 1 e 2 OK.

**Execução:**
Para CADA documento encontrado na Fase 1:

| Documento | Atualize se... |
|---|---|
| README | versão, badges, números, comandos mudaram |
| CHANGELOG | novas features, fixes, breaking changes |
| ROADMAP | itens concluídos, progresso alterado |
| TODO / BACKLOG | itens feitos ou novos pendentes |
| docs/arquitetura | novos módulos, mudanças estruturais |
| docs/api | endpoints, parâmetros alterados |
| docs/instalacao | dependências novas, passos alterados |
| journal/ | resumo da sessão, decisões, handoff |
| .github/ | instruções, agentes, prompts alterados |

**Use o gerador de docs se existir** (`docs_sync.py`, `generate-docs`, etc).

**Validação:** cada doc que mudou foi atualizado OU registrado como "não precisou".

**Erro:** arquivo bloqueado → registre, continue.

---

## 🧠 FASE 5 — MEMÓRIA

**Pré-condição:** Fases 1 e 2 OK.

**Execução:**
1. Verifique `/memories/`:
   ```
   memory view /memories/
   ```
2. Atualize/crie:
   - `/memories/repo/status.md` — versão, módulos, estado atual
   - `/memories/repo/decisions.md` — novas decisões da sessão
   - `/memories/session/` — resumo da sessão
3. Se `.session/` ou `journal/` existir, atualize com o estado real

**Validação:** pelo menos 1 arquivo de memória verificado/atualizado.

**Erro:** sistema indisponível → registre, continue.

---

## 🧹 FASE 6 — QUALIDADE

**Pré-condição:** Fase 1 OK.

**Execução:**
Varredura:
- Arquivos temporários: `*.tmp`, `*.bak`, `*.pyc`, `__pycache__`, `.DS_Store`, `Thumbs.db`
- Imports inválidos (compile os modificados)
- Links quebrados em Markdown
- Referências de arquivo inexistentes
- Dependências não usadas (npm: `depcheck`, Python: `pip check`, Rust: `cargo udeps`)

**Corrija automaticamente:** remover temporários, imports inválidos óbvios.

**NÃO corrija:** dependências — apenas registre.

**Validação:** varredura concluída, correções seguras aplicadas.

**Erro:** correção arriscada → apenas registre.

---

## 🔒 FASE 7 — SEGURANÇA

**Pré-condição:** Fase 1 OK.

**Execução:**
```
git grep -nE "sk-or-v1-|sk-[a-zA-Z0-9]{20,}|api[_-]?key\s*=\s*['\"][a-zA-Z0-9_\-]{8,}|password\s*=\s*['\"][^'\"]+['\"]|secret\s*=\s*['\"][^'\"]+['\"]" -- ':!journal/' ':!.git/' ':!node_modules/' ':!.venv/' 2>/dev/null
```

Se encontrar → **NÃO commite.** Liste no relatório com arquivo e linha.

Verifique `.gitignore`: cobre `__pycache__/`, `.env`, `node_modules/`, `journal/`?

**Validação:** scan executado, .gitignore verificado.

**Erro:** segredo encontrado → bloqueie commit, alerte.

---

## 📦 FASE 8 — GIT (automático)

**Pré-condição:** Fases 2 e 7 OK. Zero segredos.

**Execução:**
1. `git status --porcelain`
2. Se houver mudanças:
   - Agrupe por tema (docs, feat, fix, chore, refactor, test)
   - Execute commits com mensagem Conventional Commits
   - **NÃO pare. NÃO peça aprovação.** Commite tudo automaticamente.
3. Se NÃO houver mudanças: registre "working tree limpo".

**Validação:** `git status --porcelain` limpo.

**Erro:** conflito de merge → registre, pule.

---

## ☁️ FASE 9 — REMOTO (automático)

**Pré-condição:** Fase 8 OK.

**Execução:**
1. `git remote -v`
2. Se houver remote: `git push origin <branch>` — **automático, sem perguntar**
3. Se houver tags novas: `git push --tags`

**Validação:** push executado OU remote ausente registrado.

**Validação:** push executado OU remote ausente registrado.

**Erro:** push falhou (rede, permissão) → registre, não bloqueie.

---

## 📸 FASE 10 — SNAPSHOT

**Pré-condição:** Fases 2 e 8 OK.

**Execução:**
Crie `.session/SNAPSHOT_<YYYY-MM-DD>.json`:
```json
{
  "date": "<ISO 8601>",
  "project": "<nome>",
  "version": "<versão>",
  "commit": "<hash>",
  "branch": "<branch>",
  "files_changed": ["..."],
  "features": ["..."],
  "bugs_fixed": ["..."],
  "pending": ["..."],
  "risks": ["..."],
  "next_priorities": ["..."]
}
```

**Validação:** JSON válido, arquivo criado.

**Erro:** pasta inacessível → use `journal/` como fallback.

---

## 🔜 FASE 11 — HANDOFF (ESTADO)

**Pré-condição:** Fases 2 e 8 OK.

**Execução:**
Atualize `HANDOFF.md` (fonte única de estado do projeto) com a seção de encerramento:
```markdown
## Encerramento — <data>

### Resumo
(2-3 linhas do que foi feito)

### Estado
- Versão: X | Commit: <hash> | Branch: <branch>

### Pendências
- [ ] Item 1 (prioridade: alta/média/baixa)
- [ ] Item 2

### Arquivos-chave
- path/importante.py

### Fluxo sugerido
1. Leia HANDOFF.md
2. Rode validação (testes, lint)
3. Continue de <ponto específico>

### Decisões da sessão
- Decisão → motivo (1 linha)

### ⚠️ Atenção
- Bugs conhecidos, armadilhas, restrições
```

**Validação:** todas as seções preenchidas (mesmo que com "nada a declarar").

**Erro:** arquivo inacessível → registre.

---

## 📋 FASE 12 — PROMPT INICIAL

**Pré-condição:** Fases 10 e 11 OK.

**Execução:**
Gere um bloco pronto para colar no chat da próxima sessão:
```
Continue o desenvolvimento. Último commit: <hash> — <msg>.
Estado: <1 linha>. Próximo: <tarefa>. Rode /plan.
```

**Validação:** contém commit, estado e próxima ação.

**Erro:** dados faltando → use "não disponível".

---

## 📊 FASE 13 — MÉTRICAS

**Pré-condição:** Fases 1 e 2 OK.

**Execução:**
Atualize com números REAIS (medidos, não digitados):
- Itens concluídos / total
- Bugs corrigidos / bugs conhecidos
- Cobertura de testes (se disponível)
- Dívida técnica (TODOs, FIXMEs, HACKs)
- Performance (se benchmark existir)

**Validação:** todo número veio de medição.

**Erro:** métrica não mensurável → "não disponível".

---

## 🔗 FASE 14 — CONSISTÊNCIA

**Pré-condição:** Fases 4 a 13 OK.

**Execução:**
Revise a conversa. Para cada decisão tomada:
1. O que foi decidido?
2. Está documentado em arquivo?
3. Se NÃO → documente AGORA em `journal/decisions.md` ou equivalente

**Validação:** zero decisões órfãs.

**Erro:** não sabe onde documentar → registre no journal genérico.

---

## 📄 FASE 15 — RELATÓRIO FINAL

**Pré-condição:** Fases 1 a 14 executadas.

**Execução:**
```markdown
# 📊 RELATÓRIO DE ENCERRAMENTO — <data> <hora>

## 🎯 Resumo
(3-5 linhas)

## 📁 Arquivos alterados
| Arquivo | Ação |
|---|---|

## ✅ Validação
| Ferramenta | Resultado |
|---|---|

## 📝 Documentação
| Arquivo | Atualizado? |
|---|---|

## 📦 Commits
| Hash | Mensagem |
|---|---|

## ☁️ Remote
(push OK / sem remote / falhou)

## ⚠️ Problemas
| Problema | Status |
|---|---|

## 🔜 Recomendações
1. ...
2. ...
```

**Validação:** todas as seções preenchidas.

---

## 🚫 NUNCA

- Deixar segredo em commit
- Deixar projeto em estado inconsistente
- Pular fase sem registrar motivo
- Inventar métricas, dados ou documentação
- Apagar histórico (.git, changelog, journal)
