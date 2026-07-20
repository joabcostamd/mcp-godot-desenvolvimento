---
description: 'Protocolo de encerramento de sessão do MCP Godot Agent. Audita, documenta, commita, sincroniza e prepara o projeto para a próxima sessão sem perda de contexto.'
mode: 'agent'
tools: ['read', 'search', 'edit', 'terminal', 'runSubagent']
agentMode: true
user-invocable: true
---

# /encerrar — Encerramento do MCP Godot Agent

Pipeline de 10 fases para finalizar a sessão. Cada fase só avança se a
anterior concluir. Erro crítico → registre e continue com fases independentes.

**Regras:** idempotente · fail-safe · rastreável · nada de ficção.

---

## 🔍 FASE 1 — AUDITORIA DA SESSÃO

```bash
git --no-pager log --oneline -10
git --no-pager diff --stat HEAD~1 HEAD 2>/dev/null
git status --porcelain
```

Monte a tabela do que mudou: arquivos criados/modificados/removidos, features,
bugs corrigidos, pendências, decisões arquiteturais.

**Validação:** tabela cobre todas as categorias. **Erro:** use `dir`/`ls`.

---

## ✅ FASE 2 — VALIDAÇÃO

```bash
python auditar.py --fatia 0.H --skip-c5 2>/dev/null || echo "auditar.py OK"
.\.venv\Scripts\python.exe -c "
import py_compile
for f in ['server.py','core/tool_definitions.py','scripts/docs_sync.py']:
    py_compile.compile(f, doraise=True)
print('sintaxe OK')
"
.\.venv\Scripts\python.exe -c "
import sys; sys.path.insert(0,'.')
import server
print(f'{len(server._raw_tool_defs())} tools, {len(server._build_handlers())} handlers')
"
python scripts/docs_sync.py
```

**Validação:** 274 tools, 295 handlers, docs_sync idempotente.

**Erro:** ferramenta ausente → pule. Erro crítico → registre, não corrija.

---

## 📝 FASE 3 — DOCUMENTAÇÃO

Para cada doc, verifique e atualize se necessário:

| Doc | Atualizar se... |
|---|---|
| `README.md` | DOCS_SYNC desatualizado |
| `HANDOFF.md` | nova fatia concluída |
| `NEXT_STEP.md` | progresso alterado |
| `.roadmap_progress.json` | fatias novas |
| `.session/SESSION_NEXT.md` | estado alterado |
| `docs/arquitetura.md` | novos módulos |

Use `python scripts/docs_sync.py` para números. Atualize manualmente o resto.

**Validação:** docs_sync roda sem mudanças. **Erro:** doc bloqueado → registre.

**IMPORTANTE:** se um doc NÃO mudou, informe explicitamente: "X.md — não precisou
de atualização". NUNCA pule esta verificação.

---

## 🧠 FASE 4 — MEMÓRIA

```bash
memory view /memories/
```

Atualize:
- `/memories/repo/status.md` — versão, módulos, tools, estado atual
- `/memories/repo/decisions.md` — novas decisões da sessão

**Validação:** pelo menos 1 arquivo verificado. **Erro:** indisponível → continue.

---

## 🔒 FASE 5 — SEGURANÇA

```bash
Select-String -Path "tools\*.py","server.py" -Pattern "sk-|api.key\s*=\s*[\x22\x27]|password\s*=\s*[\x22\x27]|secret\s*=\s*[\x22\x27]" -AllMatches 2>$null
```

Verifique `.gitignore` contém: `journal/`, `__pycache__/`, `*.pyc`, `.env`.

**Validação:** zero segredos, .gitignore OK.

**Erro:** segredo encontrado → BLOQUEIE commit, alerte.

---

## 📦 FASE 6 — GIT

```bash
git status --porcelain
```

Se houver mudanças:
1. Agrupe por tema (feat, fix, docs, chore)
2. Para cada grupo, proponha commit Conventional Commits
3. **NUNCA commite sozinho — aguarde aprovação**

Após TODOS aprovados: `git add <arquivos> ; git commit -m "<mensagem>"`

**Validação:** `git status --porcelain` limpo.

**Erro:** sem aprovação → registre pendência.

---

## ☁️ FASE 7 — GITHUB

```bash
git remote -v
git push origin main 2>&1
```

**Validação:** push executado ou remote ausente. **Erro:** rede → registre.

---

## 📸 FASE 8 — SNAPSHOT + NEXT SESSION

Crie `.session/SNAPSHOT_$(date +%Y-%m-%d).json`:
```json
{
  "date": "<ISO 8601>", "version": "<pyproject.toml>",
  "commit": "<hash>", "branch": "main",
  "tools": 274, "handlers": 295,
  "onda_0": ["0.A-0.G concluidas", "0.H escalada"],
  "files_changed": ["..."], "pending": ["..."],
  "next": "0.H — aprovar/escalar ou 0.I — /plan"
}
```

Atualize `.session/SESSION_NEXT.md` com resumo, pendências, fluxo sugerido.

**Validação:** ambos criados/atualizados.

---

## 📊 FASE 9 — RELATÓRIO FINAL

```markdown
# 📊 ENCERRAMENTO — <data> <hora>

## 🎯 Resumo
## 📁 Arquivos alterados
## 📝 Documentação atualizada
## 🧠 Memória
## 📦 Commits
## ☁️ GitHub
## ⚠️ Pendências
## 🔜 Próxima: /plan para <fatia>
```

**Validação:** todas as seções preenchidas.

---

## 🚫 NUNCA

- Commitar sem aprovação · Inventar métricas · Apagar histórico
- Deixar segredo exposto · Pular fase sem registrar · Ignorar erro crítico
- Encerrar sessão com documento desatualizado
