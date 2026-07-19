# Copilot Instructions — MCP Godot Agent

Este arquivo contém instruções permanentes para a IA agêntica (VS Code Copilot / DeepSeek V4 Pro)
que opera neste repositório e nos projetos Godot conectados via MCP.

Este documento é o equivalente ao `00-mestre.md` do Cline, adaptado para o Copilot nativo.
O fluxo de trabalho usa os comandos `/plan` (planejar fatia) e `/act` (implementar + auditar).

---

## ⚡ ATIVAÇÃO DE GRUPOS VIRTUAIS (INÍCIO DE SESSÃO)

> **Regra fixa:** No início de **toda sessão de trabalho**, antes de qualquer outra ação,
> verifique se existem tools com prefixo `activate_` visíveis no chat (ex: `activate_scene`,
> `activate_script`, `activate_art`, etc.). Essas tools são stubs de grupos virtuais criados
> pelo VS Code Copilot quando o número total de tools do servidor MCP `godot-agent` excede o
> threshold de 128 — as tools reais do grupo ficam **inacessíveis** até que o stub seja chamado.
>
> **Procedimento:**
> 1. Liste as tools disponíveis e identifique TODAS as que começam com `activate_`.
> 2. Chame **todas** elas, uma por uma, sem exceção.
> 3. Só então prossiga com o bootstrap normal da sessão (leitura de docs, auditoria, etc.).
>
> **Exemplo:**
> ```
> # Se existirem activate_scene, activate_script, activate_art:
> 1. Chamar activate_scene → grupo scene expandido
> 2. Chamar activate_script → grupo script expandido
> 3. Chamar activate_art → grupo art expandido
> # Agora as tools reais (scene_manage, safe_write_gdscript, generate_game_art, etc.)
> # estão acessíveis e a sessão pode prosseguir normalmente.
> ```
>
> **Se NÃO existirem tools `activate_*`:** O threshold de virtualização não foi atingido
> (total de tools ≤ 128 ou o mecanismo não está ativo nesta versão do Copilot).
> Prossiga com o bootstrap normal — **não invente tools que não existem.**

---

## 📋 FLUXO DE TRABALHO: /plan → /act

Toda implementação segue dois comandos:

| Comando | O que faz | Regra de ouro |
|---|---|---|
| `/plan` | Lê roadmap, verifica suposições, monta plano, **NÃO edita código** | Termina com: "Plano pronto. Digite `/act` para implementar." |
| `/act` | Implementa, audita (C1-C6), cross-model, grava progresso, fecha ou escala | "Pronto" é o que o portão (`auditar.py`) retornou |

**Regra:** Nunca implemente sem plano. Se o usuário pedir implementação direta, ofereça rodar `/plan` primeiro.

---

## 🏗 REGRAS DE TETO DE FERRAMENTAS (TOOL BUDGET)

O servidor MCP tem limite prático de tools visíveis. Estas regras mantêm o projeto dentro do orçamento:

| Regra | Descrição |
|---|---|
| **Rollup-first** | Toda nova capacidade entra como **op dentro de um rollup existente**, NÃO como tool de topo. Só crie tool de topo com justificativa explícita. |
| **Consolidar** | Se uma fase tem >40 tools visíveis, agrupe atômicas relacionadas em rollups. |
| **Gate de orçamento** | Teste `test_budget_gate.py` no CI: fase ≤ 40 tools, total ≤ 70. |
| **Perfil lean** | Modo padrão carrega ferramental base + tools da fase atual. Use `catalog_search` para encontrar tools fora do perfil ativo. |
| **Meta-tools** | `catalog_search`, `describe_tool`, `invoke_by_name` permitem acesso sob demanda sem poluir o namespace. |

---

## 🔒 REGRAS DE SEGURANÇA

| Regra | Descrição |
|---|---|
| **Loopback** | Todos os bridges e servidores bindam em `127.0.0.1` — nunca em `0.0.0.0`. |
| **Checkpoint ≠ commit** | Checkpoint (`git stash`/branch) é rede de segurança automática. Commit só com aprovação humana. |
| **Nunca commitar sozinho** | Propor commit com mensagem, aguardar confirmação. |
| **Segredos** | Nunca escreva API keys, tokens ou segredos em arquivos. Use variáveis de ambiente. |
| **Sem auto-aprovar** | A IA não aprova o próprio código. Quem aprova é o portão (`auditar.py`) + humano. |

---

## 📊 CRITÉRIOS DE AUTOAUDITORIA (C1–C6)

Estes 6 critérios são o portão de qualidade. Toda fatia implementada passa por eles:

| # | Nome | O que verifica | Como rodar |
|---|---|---|---|
| **C1** | Contrato | Schema não driftou — só a tool/op nova aparece no diff | `auditar.py --c1-before <antes> --c1-after <depois>` |
| **C2** | Canary | 2-3 chamadas conhecidas com entrada/saída esperada | `auditar.py --canary <arquivo.json>` |
| **C3** | Regressão | `smoke_test` — nada que passava antes quebrou | `auditar.py` (roda smoke_test internamente) |
| **C4** | Segurança | Loopback, checkpoint feito, sem segredo, passou por rollup, idempotente | `auditar.py --c4-checklist <json>` |
| **C5** | Orçamento | Teto de tools ≤ 40/fase, ≤ 70 total | `python tests/test_budget_gate.py` |
| **C6** | Distinguibilidade | Tool nova não se confunde com nenhuma existente | `auditar.py --tool-name <nome>` |

**Portão completo:** `python auditar.py --fatia <N>`

### Critérios Progressivos (antes do `auditar.py` existir)

Se a Fatia 0.0.5 (`auditar.py`) ainda não foi concluída, execute os critérios manualmente:

- **C1:** Comparar `tools/list` antes/depois manualmente
- **C2:** Executar canaries manualmente e comparar saída
- **C3:** Rodar `smoke_test` e verificar resultado
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

