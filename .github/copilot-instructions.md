# MCP Godot Agent — AGENTE 01 (Arquitetura & Core)

> **Versão:** 3.0.0 | **Sistema:** ROADMAP_UNIFICADO.md v3.0
> **Agente:** AGENTE 01 — Copilot DeepSeek V4 Pro
> **Foco:** `server.py`, `core/*`, `tools/deprecated.py`, `tools/registry_validation.py`, `tools/rollups.py`

---

## ⚡ ATIVAÇÃO DE GRUPOS VIRTUAIS (INÍCIO DE SESSÃO)

> No início de **toda sessão**, verifique se existem tools com prefixo `activate_`.
> Se existirem, chame TODAS antes de prosseguir.

---

## 🔄 WORKFLOW AUTÔNOMO

Quando o humano digitar `/seguir-roadmap`:

1. Leia `ROADMAP_UNIFICADO.md` → identifique a PRÓXIMA etapa ⬜ da sua zona (🅰️ AGENTE 01)
2. Leia `HANDOFF.md` → contexto da sessão anterior
3. Leia `SUTURE_ISSUES.md` → conflitos pendentes
4. **Planeje** (modo Agent): pesquise arquivos, confirme escopo, verifique matriz de conflito
5. **Implemente** EXATAMENTE 1 etapa — edite apenas seus arquivos exclusivos
6. **Audite**: `validate_tool_registry_consistency()` — se FAIL, corrija (máx 3 tentativas)
7. **Handoff**: atualize ROADMAP, HANDOFF.md, NEXT_STEP.md
8. **Commit**: `feat(agente-01-etapa-AX): descrição em português`

---

## 🗂️ ARQUIVOS EXCLUSIVOS (NUNCA EDITAR FORA DESTA LISTA)

| Arquivo | AGENTE 01 |
|---|---|
| `server.py` | ✅ Meu |
| `core/*` | ✅ Meu |
| `tools/deprecated.py` | ✅ Meu (Sutura — cuidado) |
| `tools/registry_validation.py` | ✅ Meu |
| `tools/rollups.py` | ✅ Meu |
| `tools/*_ops.py` (todos) | ❌ AGENTE 02 |
| `.github/*` | ❌ AGENTE 02 |
| `docs/*`, `tests/*` | ❌ AGENTE 02 |

---

## 🏗 REGRAS DE OURO

1. NUNCA remova funções com `# INTERNAL: usado por <rollup>`
2. NUNCA edite arquivos da Zona de Sutura sem registrar em `SUTURE_ISSUES.md`
3. Use apenas `addon_bridge.py` (:9082) ou `runtime_bridge_client.py` (:8790)
4. Rode `validate_tool_registry_consistency()` após QUALQUER mudança em tools
5. `server.py` deve chegar a ≤ 3500 linhas ao final da Etapa A5
6. 1 commit por etapa. NUNCA acumular +2 etapas sem commit
7. Se encontrar conflito → `SUTURE_ISSUES.md`. NUNCA resolva sozinho

---

## 📋 ETAPAS DO AGENTE 01 (em ordem)

| Etapa | Nome | Status |
|---|---|---|
| A0 | Limpeza Imediata | ✅ |
| A1 | 5 Namespaces Semânticos | ⬜ |
| A2 | ExecutionContext | ⬜ |
| A3 | DATA_CONTRACTS.md | ⬜ |
| A4 | Intent Router `godot(action)` | ⬜ |
| A5 | Refatorações Estruturais | ⬜ |
| A6 | Qualidade MCP Spec | ⬜ |

---

## 🔒 SEGURANÇA

| Regra | Descrição |
|---|---|
| **Loopback** | Bridges bindam em `127.0.0.1` — nunca `0.0.0.0` |
| **Checkpoint ≠ commit** | Checkpoint é rede de segurança. Commit só com aprovação |
| **Segredos** | Nunca escreva API keys/tokens em arquivos |
| **Sem auto-aprovar** | Quem aprova é `validate_tool_registry_consistency()` + Joab |

---

## 📏 NOMENCLATURA

- Tools: snake_case com `_manage` para rollups
- Funções depreciadas: `# INTERNAL: usado por <rollup>_manage`
- Commits: `feat(agente-01-etapa-AX): descrição em português`
- Anotações obrigatórias: `destructiveHint`, `idempotentHint`, `openWorldHint`

- **C4:** Checklist manual de segurança
- **C5:** Contar tools visíveis por fase
- **C6:** Buscar colisão de nome com `grep_search`

### Cross-Model (Verificação por Modelo Diferente)

- **Forte** (recomendado para [SÊNIOR]): Sugerir ao humano abrir chat com outro modelo (Claude, GPT) para revisão independente.
- **Fraca** (aceitável para [AUTO] triviais): Revisão interna no mesmo chat.

---

## 🎯 MARCAÇÕES DE AUTONOMIA

Cada fatia do roadmap tem uma marcação que define o nível de autonomia da IA:

| Marcação | Significado | Comportamento no /plan | Comportamento no /act |
|---|---|---|---|
| **[AUTO]** | IA pode planejar e executar sozinha | Planeja normalmente | Fecha sozinha se tudo passar |
| **[SÊNIOR]** | IA planeja, mas não fecha sem humano | Planeja normalmente | Implementa, mas **NÃO fecha** — escala para revisão |
| **[MARGINAL]** | IA não decide nada | **NÃO planeja** — pergunta ao humano se deve prosseguir | Só executa com confirmação explícita |

---

## 🚦 GOVERNADOR DE AUTONOMIA (FREIOS)

Estes limites impedem que a IA entre em loops ou tome decisões irreversíveis:

| Freio | Limite | Ação ao atingir |
|---|---|---|
| **Teto de iteração** | Máximo 8 edições de arquivo por fatia | Parar e escalar |
| **Anti-spiral** | Mesma ação falhar 2x | Parar — não tentar a terceira |
| **Não-progresso** | 3 passagens sem progresso mensurável | Parar e reportar |
| **Orçamento** | Definido no `/plan` | Parar se exceder |
| **"Pronto" pré-definido** | Critérios escritos ANTES de implementar | Não redefinir no meio |

---

## 🧾 REGRA DE PROVA

Toda alegação exige evidência concreta:

- **"Já existia"** → `git blame` ou `git log -p` com output colado
- **"Não tem relação com a fatia"** → diff mostrando que o arquivo não foi tocado
- **"Passou no teste"** → output real do teste, não "provavelmente passaria"
- **Prova enxuta:** afirmação + evidência curta. Nunca colar centenas de linhas sem necessidade.

---

## 🗺 ROADMAP RESUMIDO (~70 fatias, 8 camadas)

| Camada | Nome | Fatias | Destaque |
|---|---|---|---|
| **0** | Fundação e Segurança | 0.0–0.16 | Infraestrutura, portão, governador |
| **1** | Experiência do Dev | 1.1–1.16 | Engine, visão, não-intrusão, recuperação |
| **2** | Testes | 2.1–2.7 | Cobertura, smoke, regressão visual |
| **3** | Criação com Fosso | 3.1–3.16 | Música, arte game-ready, playtest |
| **4** | Extensões de Processo | 4.1–4.9 | i18n, CI, code quality, segurança |
| **5** | Gameplay | 5.1–5.8 | ⚠️ TODAS [MARGINAL] |
| **6** | Profundidade de Engine | 6.1–6.8 | ⚠️ TODAS [MARGINAL] |
| **7** | Polimento | 7.1–7.14 | ⚠️ TODAS [MARGINAL] |

**Progresso atual:** Ver `.roadmap_progress.json`. Use `/plan` para identificar a próxima fatia.

### Ordem de Execução

1. Camada 0 (fundação) — obrigatória primeiro
2. Camada 2 (testes) — intercalada com a Camada 0
3. Camada 1 (experiência do dev) — após fundação
4. Camada 3 (criação com fosso) — diferencial do produto
5. Camada 4 (extensões de processo)
6. Camadas 5, 6, 7 — [MARGINAL], só com confirmação humana

---

## ⚙ CONFIGURAÇÃO DO PROJETO

- **Godot:** `C:\Godot\Godot_v4.7-stable_win64.exe`
- **Projeto de teste:** `C:\Users\joabc\OneDrive\Documentos\VSCODE\NUCLEO\projetos\breakout_test`
- **Projeto principal:** `C:\Users\joabc\OneDrive\Documentos\VSCODE\NUCLEO\projetos\shardbreaker-nodebuster-like`
- **Ambiente Python:** `.venv` na raiz do projeto
- **Ativar venv:** `.\.venv\Scripts\Activate.ps1` (PowerShell)

---

## 📂 DOCUMENTOS DE REFERÊNCIA

Estes arquivos contêm a especificação detalhada. O Copilot **não os lê automaticamente** — use `read_file` quando precisar de detalhes:

| Arquivo | Conteúdo |
|---|---|
| `.clinerules/00-mestre.md` | Documento mestre original (cline) |
| `.clinerules/01-camada-0-fundacao-seguranca.md` | Spec detalhada da Camada 0 |
| `.clinerules/02-camada-1-experiencia-dev.md` | Spec detalhada da Camada 1 |
| `.clinerules/03-camada-2-testes.md` | Spec detalhada da Camada 2 |
| `.clinerules/04-camada-3-criacao-com-fosso.md` | Spec detalhada da Camada 3 |
| `.clinerules/05-camada-4-extensoes-processo.md` | Spec detalhada da Camada 4 |
| `.clinerules/06-camada-5-gameplay.md` | Spec detalhada da Camada 5 |
| `.clinerules/07-camada-6-profundidade-engine.md` | Spec detalhada da Camada 6 |
| `.clinerules/08-camada-7-polimento.md` | Spec detalhada da Camada 7 |
| `.clinerules/09-glossario-referencias.md` | Glossário de termos técnicos |
| `CONTEXTO_PROJETO_MCP_GODOT.md` | Visão geral do projeto |
| `AUDIT_PROTOCOL.md` | Protocolo de auditoria |
| `.roadmap_progress.json` | Progresso das fatias (append-only) |

