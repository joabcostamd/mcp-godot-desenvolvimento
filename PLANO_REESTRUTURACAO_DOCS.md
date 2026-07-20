
# PLANO DE REESTRUTURAÇÃO DOCUMENTAL

> **Público:** IA agêntica.
> **Validade:** temporário. Apague este arquivo quando a Fatia 1.G estiver concluída.
> **Local correto:** raiz do repositório.

---

## 1. O PROBLEMA (leia antes de mover qualquer coisa)

Os 17 documentos atuais (5.563 linhas) foram escritos como diário de bordo pessoal.
Eles servem a públicos diferentes no mesmo arquivo, e por isso se contradizem.

Divergências reais já confirmadas por leitura do código:

| Documento | Diz que tem | Código real |
|---|---|---|
| README | 193 tools, v3.4.0 | 204 `Tool()` em `server.py` |
| MCP_ESTADO_ATUAL | 191 tools, v3.3.0 | idem |
| NEXT_SESSION | 212 tools | idem |
| CONTEXTO_PROJETO | 248 / 201 | idem |

**A causa não é desleixo: é número escrito à mão.** A correção estrutural é gerar
todo número a partir do código. Depois desta reestruturação, número escrito à mão
em documento é violação de regra.

---

## 2. PRINCÍPIO: 1 DOCUMENTO = 1 PÚBLICO

Todo documento declara o público na primeira linha. Se serve a dois, parte em dois.

| Público | Precisa de | Onde vive |
|---|---|---|
| Usuário final | O que faço e como faço | `README.md` + `docs/manual/` (gerado) |
| IA agêntica | Regras, fatias, como implementar | `.github/` |
| Contribuidor | Como funciona por dentro | `docs/arquitetura.md` |
| Você (humano) | Onde parei, o que aprendi | `journal/` (fora do git) |

Segunda divisão: **escrito à mão** vs **gerado por código**.
Gerado: catálogo de tools, estado atual, inventário de rollups, manual, changelog.

---

## 3. MAPA DE-PARA (a tabela que a IA executa)

### 3.1 Vira instrução da IA

| De | Para | Ação |
|---|---|---|
| `.clinerules/00-mestre.md` | `.github/copilot-instructions.md` | Já entregue pronto. Preservar o conteúdo original em `journal/` |
| `.clinerules/01-camada-0-*.md` | `.github/instructions/camada-0.instructions.md` | Mover + frontmatter `applyTo` |
| `.clinerules/02` a `08` | `.github/instructions/camada-1..7.instructions.md` | Mover + frontmatter |
| `.clinerules/09-glossario-referencias.md` | `.github/instructions/glossario.instructions.md` | Mover |
| `.clinerules/workflows/act.md` | `.github/prompts/act.prompt.md` | Substituído pelo arquivo do Lote 2 |
| `.clinerules/workflows/plan.md` | `.github/prompts/plan.prompt.md` | Substituído pelo arquivo do Lote 2 |
| `LEARNINGS.md` | `.github/instructions/aprendizados.instructions.md` | Mover. **Documento mais valioso para a IA** — não editar conteúdo |
| `AUDIT_PROTOCOL.md` | fundir em `copilot-instructions.md` | Verificar se algo não coberto; se sim, anexar |

**Frontmatter obrigatório** em cada `.instructions.md`:

```markdown
---
applyTo: '**'
---
```

Use glob mais específico quando a camada só valer para certos arquivos
(exemplo: camada do dock → `applyTo: 'addons/**'`).

### 3.2 Vira documentação pública

| De | Para | Ação |
|---|---|---|
| `ARQUITETURA_MCP.md` | `docs/arquitetura.md` | Mover. Reescrita é fatia separada |
| `GUIA_CONEXAO.md` | `journal/` | Aposentar quando o instalador (1.A) existir |
| `GUIA_INSTALACAO.md` | `journal/` | Idem. Substituto: `docs/instalacao.md` de 20 linhas |
| `FEATURES.md` | `journal/` | Absorvido pelo manual gerado (1.H) |
| `README.md` | `README.md` | Reescrita total é fatia separada (1.N) |

### 3.3 Passa a ser gerado

| Arquivo | Fonte de geração |
|---|---|
| `CATALOGO_COMPLETO_MCP_GODOT.md` | `_tool_defs()` |
| `INVENTARIO_OPS_ROLLUPS.md` | rollups + `_meta_tool.py` |
| `MCP_ESTADO_ATUAL.md` | código + `.roadmap_progress.json` |
| `CHANGELOG.md` | commits |
| `docs/manual/` | `behavior.json` + blueprints + prompts + fases |

Enquanto o gerador não existir (Fatia 0.F), **mova os quatro primeiros para `journal/`**
para não continuarem mentindo.

### 3.4 Sai do repositório público

Mover para `journal/` (que entra no `.gitignore`):
`NEXT_SESSION.md` · `SESSION_SUMMARY_*.md` · `AUDITORIA-PENDENCIAS-RESPOSTAS.md` ·
`pendencias.md` · `CONTEXTO_PROJETO_MCP_GODOT.md`

Motivo: são logs de trabalho pessoais, contêm caminhos do seu disco e rotina,
e confundem quem chega no repositório.

### 3.5 Morre

`RELOGIO_CLINE_COMPORTAMENTO.md` — apagar.
Além disso: **toda referência a Cline** nas camadas 01–08 deve ser trocada por
"IA agêntica (Copilot)". Buscar por: `Cline`, `.clinerules`, `cline_mcp_settings`.

### 3.6 Nasce

| Arquivo | Fatia | Observação |
|---|---|---|
| `LICENSE` | 0.E | MIT. Bloqueia AssetLib e Sponsors enquanto não existir |
| `CONTRIBUTING.md` | 0.E | Como contribuir, padrão de commit, como rodar testes |
| `CODE_OF_CONDUCT.md` | 0.E | Contributor Covenant padrão |
| `SECURITY.md` | 0.E | Como reportar vulnerabilidade |
| `AGENTS.md` | 0.D | Já entregue pronto |
| `llms.txt` | 1.N | Fatos estruturados para agentes de IA |
| `docs/manual/` | 1.H | Gerado |
| `docs/tutorial/` | 1.I | Escrito à mão, testado com pessoas |

---

## 4. ESTRUTURA FINAL

```
raiz/
  README.md              ← vitrine (usuário)
  LICENSE
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  SECURITY.md
  AGENTS.md              ← convivência das IAs
  ROADMAP_DEFINITIVO.md
  llms.txt
  server.py, tools/, addons/, ...

  .github/
    copilot-instructions.md
    instructions/        ← camadas + aprendizados + fontes + glossário
    prompts/             ← /plan /act /handoff /manual
    agents/              ← implementador, revisor
    roadmap/             ← fichas das ondas

  docs/
    instalacao.md
    arquitetura.md
    manual/              ← GERADO
    tutorial/            ← escrito à mão

  journal/               ← NO GITIGNORE, só seu
```

Raiz sai de 17 arquivos confusos para 8 arquivos com propósito claro.

---

## 5. AS 5 FATIAS DE EXECUÇÃO

Não faça tudo de uma vez. Cinco fatias, nesta ordem:

**R1 — Criar estrutura e mover sem editar** `[AUTO]`
Criar pastas, `git mv` de tudo conforme a seção 3, criar `journal/` e adicionar ao
`.gitignore`. **Zero edição de conteúdo.** Prova: `git status` mostrando apenas
renomeações, e `ls` da nova estrutura.

**R2 — Frontmatter e expurgo de Cline** `[AUTO]`
Adicionar `applyTo` em cada `.instructions.md`. Substituir toda menção a Cline.
Prova: `grep -ri "cline" .` retornando zero (fora de `journal/`).

**R3 — Arquivos que nascem** `[AUTO]`
LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY. Prova: arquivos existem e
`release_checklist` do próprio MCP reconhece o LICENSE.

**R4 — `docs_sync`** `[AUTO]`
Script que extrai números reais do código e injeta nos documentos gerados.
Prova: rodar o script e mostrar que as 4 contagens divergentes viraram uma só,
igual ao número real de `Tool()` em `server.py`.

**R5 — Reescrita do README e da arquitetura** `[SÊNIOR]`
Só depois que o instalador (1.A) existir, senão o README documenta algo que
não existe mais. Prova: revisão humana.

---

## 6. ARMADILHAS (a IA erra aqui)

1. **"Melhorar" o texto ao mover.** Proibido. Mover é `git mv` e nada mais.
   Regras que custaram meses de aprendizado somem quando a IA "resume".
2. **Apagar em vez de arquivar.** Nada é apagado, exceto `RELOGIO_CLINE_*`.
   Tudo o mais vai para `journal/`.
3. **Esquecer o `.gitignore`.** Se `journal/` for commitado, o expurgo não serviu de nada.
4. **`git mv` vs mover no explorador.** Use `git mv` — preserva histórico.
5. **Instruções em subpasta não funcionam.** O VS Code só lê
   `.github/copilot-instructions.md` do workspace aberto. Se você abrir uma subpasta
   como workspace, as regras somem. Por isso os dois agentes usam `git worktree`
   (pastas completas), nunca subpastas.

