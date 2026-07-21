# Pesquisa Externa — MCP Godot Agent

> Data: 2026-07-21 | Fontes: MCP Spec 2025-03-26, Godot 4.7 Docs, itch.io Creator Docs, GitHub Sponsors, opensource.guide, Steamworks, gd-plug, Discord Safety
> Objetivo: enriquecer a solução com conhecimento externo validado, sem regressões.
> **Protocolo canônico:** `.github/instructions/pesquisa.instructions.md`
> **Comando rápido:** `/pesquise` no chat do VS Code

---

## 0. Índice de pesquisas realizadas

| Data | Tema | Fatia | Resumo |
|---|---|---|---|
| 2026-07-20 | MCP Spec, Godot Plugins, GDScript Style | 1.E (Dock v1) | Protocolo, plugins, style guide |
| 2026-07-20 | Vitrine de gêneros, MCP Prompts/Resources, Competidores MCP+Godot | 1.L (Vitrine de gêneros) | Game patterns, UX de showcase, landscape competitivo |
| 2026-07-20 | VS Code Prompts, Agent Skills, Onboarding guiado | 1.M (Skills exportáveis) | .prompt.md vs SKILL.md, MCP prompts spec, UX de onboarding |
| 2026-07-21 | Telemetria opt-in, MCP Logging, VS Code Telemetry, Glean SDK | 1.P (Telemetria opt-in) | MCP spec (sem telemetria nativa), VS Code padrão ouro, Glean privacy-first, JSONL stdlib |
| 2026-07-21 | **ONDA 4 — MUNDO: distribuição, monetização, comunidade, identidade, métricas** | 4.A–4.G | AssetLib, itch.io, GitHub Sponsors, Steam Direct, open source metrics, gd-plug, Discord/GitHub Discussions, naming |

---

## 1. MCP Protocol (Model Context Protocol)

### 1.1 Arquitetura

```
MCP Host (VS Code) → MCP Client → MCP Server (nosso server.py)
                         ↓              ↓
                    stdin/stdout    JSON-RPC 2.0
```

- **Host:** VS Code com Copilot
- **Client:** Gerenciado pelo VS Code (cria um client por server)
- **Server:** Nosso `server.py` (stdio transport, processo local)
- **Protocolo:** JSON-RPC 2.0

### 1.2 Primitivas que usamos

| Primitiva | Uso no projeto |
|-----------|---------------|
| `tools/list` | VS Code descobre as tools do nosso server |
| `tools/call` | VS Code chama nossas tools |
| `notifications/tools/list_changed` | Avançar de fase → notificar novas tools |

### 1.3 O que NÃO usamos (oportunidades)

| Funcionalidade | Descrição | Aplicabilidade |
|---------------|-----------|---------------|
| **Resources** | Dados contextuais expostos pelo server | Expor `project.godot`, estado do jogo, logs |
| **Prompts** | Templates de interação | `/plan`, `/act`, `/handoff` como prompts MCP |
| **Sampling** (CLIENT) | Server pede para o host chamar LLM | ❌ Descontinuado na spec 2026-07-28 |
| **Elicitation** (CLIENT) | Server pede input do usuário | ✅ Podemos usar para confirmações (ex: "aprovar etapa?") |
| **Logging** (CLIENT) | Server envia logs para o host | ✅ Substituiria nossos prints por notificações estruturadas |
| **Tasks** (experimental) | Operações longas com status | Export, build, playtest |
| **Progress** | Barra de progresso em operações | Download de templates, export, build |

### 1.4 Segurança (MCP Spec)

> **User Consent and Control:** Users must explicitly consent to and understand all data access and operations.

**Aplicação no nosso projeto:**
- ✅ IP Guard (0.K) — avisa sobre PI de terceiros
- ✅ Budget (1.D) — mostra custo antes de estourar
- ⚠️ Podemos adicionar: confirmação antes de operações destrutivas via `elicitation`
- ✅ Ferramentas destrutivas já têm checkpoint (0.5)

---

## 2. Godot 4.x Editor Plugins

### 2.1 Estrutura canônica (Godot Docs)

```
addons/meu_plugin/
├── plugin.cfg          # [plugin] name, description, author, version, script
└── plugin.gd           # @tool extends EditorPlugin
```

### 2.2 Dock (Godot Docs)

```gdscript
# plugin.gd
@tool
extends EditorPlugin

func _enter_tree():
    var dock = preload("dock.tscn").instantiate()
    add_control_to_dock(DOCK_SLOT_RIGHT_BL, dock)

func _exit_tree():
    remove_control_from_docks(dock)
```

**Nossa implementação:** ✅ plugin.gd já segue este padrão.

### 2.3 Sub-plugins (Godot Docs)

Para organizar plugins com múltiplas funcionalidades:

```gdscript
# Plugin principal em addons/meu_plugin/
func _enable_plugin():
    EditorInterface.set_plugin_enabled("meu_plugin/dock", true)
    EditorInterface.set_plugin_enabled("meu_plugin/node", true)
```

**Aplicação:** Podemos separar `mcp_addon` (WebSocket bridge) e `mcp_dock` (UI) como sub-plugins de um plugin principal.

### 2.4 Autoloads via Plugin

```gdscript
func _enable_plugin():
    add_autoload_singleton("MCPRuntime", "res://addons/mcp_runtime_bridge/runtime.gd")
```

**Aplicação:** O `mcp_runtime_bridge` poderia ser registrado como autoload automaticamente.

---

## 3. GDScript Best Practices (Godot Style Guide)

### 3.1 Ordem de código (atualizado para nosso dock)

| Ordem | Categoria | dock.gd atual |
|-------|----------|---------------|
| 1 | `@tool`, `@icon` | ✅ Linha 21 |
| 2 | `class_name` | ❌ Não usado (não necessário) |
| 3 | `extends` | ✅ `extends Control` |
| 4 | Doc comment | ✅ Linhas 1-19 |
| 5 | Signals | ❌ Não temos signals |
| 6 | Enums | ❌ Não usado |
| 7 | Constants | ✅ Linhas 23-28 |
| 8 | Static variables | ❌ Não usado |
| 9 | `@export` vars | ❌ Não usado |
| 10 | Regular vars | ✅ Linhas 32-61 |
| 11 | `@onready` vars | ✅ Linhas 63-77 |
| 12 | `_init()` | ❌ Não usado |
| 13 | `_ready()` | ✅ Linha 82 |
| 14 | `_process()` | ✅ Linha 87 |
| 15 | Virtual methods | ✅ `_exit_tree()` linha 109 |
| 16 | Public methods | ✅ |
| 17 | Private methods | ✅ |

**Conformidade:** ~90%. Ajustes menores recomendados.

### 3.2 Static Typing

| Regra | dock.gd |
|-------|---------|
| Usar `: Type` para tipos ambíguos | ✅ |
| Usar `:=` quando tipo é óbvio | ✅ |
| Evitar `:=` com `get_node()` | ✅ Usamos `%` unique names |
| Tipos em parâmetros | ⚠️ Faltam em alguns métodos |

### 3.3 Naming

| Regra | dock.gd |
|-------|---------|
| snake_case para funções/vars | ✅ `_btn_run`, `_refresh_ui` |
| `_` prefixo para private | ✅ |
| CONSTANT_CASE para consts | ✅ `WS_PORT`, `MAX_HISTORY` |
| PascalCase para nós | ✅ `BtnRun`, `ProjectLabel` |

### 3.4 Formatação

| Regra | dock.gd |
|-------|---------|

---

## 4. Vitrine de Gêneros & UX de Quickstart (Pesquisa 2026-07-20 — Fatia 1.L)

> **Fontes:** MCP Spec 2025-06-18 (Prompts/Resources), Godot 4.7 Docs (Project Organization, Demo Projects), IvanMurzak/Godot-MCP (v0.19.0), godotengine/godot-demo-projects (9.2k★), Godot Asset Library

### 4.1 Como outras engines/ferramentas apresentam templates de gênero

| Fonte | Padrão | Aplicabilidade ao 1.L |
|---|---|---|
| godot-demo-projects | Categorização por dimensão (2d/, 3d/) + feature (physics_tests, audio/rhythm_game). Cada demo: README com descrição, linguagem, renderer, screenshots, link AssetLib | Cada gênero nosso vira um "cartão" com: nome PT-BR, frase pronta, dificuldade, referência |
| Godot Asset Library | Categorias: 2D Tools, 3D Tools, Scripts, Misc. Busca por texto livre. 5.227 assets | Nossa vitrine é navegável por categoria (ação, puzzle, estratégia) + busca por frase |
| Unity Hub / Templates | Templates de projeto com cena inicial, assets mínimos, configurações. Download → abre editor já funcional | Nosso `quickstart_manage` já faz isso; a vitrine só expõe as opções |
| Itch.io | Tags + gêneros como filtro de descoberta. Cada jogo: cover, descrição curta, tags | README pode ter "mini-cartões" com emoji + frase + dificuldade |

### 4.2 Ecossistema competitivo MCP + Godot

| Projeto | Estrelas | Versão | Linguagem | Tools | Diferencial |
|---|---|---|---|---|---|
| **IvanMurzak/Godot-MCP** | 178 | 0.19.0 | C# | 39 (11 famílias) | Cloud (ai-game.dev), runtime mode, prompts/resources, CLI |
| **Open Godot MCP** | — | 0.1.1 | ? | ? | MIT, simples |
| **Godot MCP Pro** | — | 1.15.1 | ? | ? | Proprietário |
| **Beckett (AI MCP)** | — | 1.10.1 | ? | ? | MIT |
| **Breakpoint MCP** | — | 1.7.0 | ? | ? | Foco em debugging |
| **Godot Agent** | — | 1.0.1 | ? | ? | MIT |
| **Godot AI Workbench** | — | 0.1.0 | ? | ? | Apache-2.0 |

**Nosso diferencial competitivo (confirmado pela pesquisa):**
- ✅ **Python** (não C#) — barreira de entrada menor, sem necessidade de mono build
- ✅ **Dono do processo** (fases, gates, verificação) — os outros são só pontes
- ✅ **PT-BR nativo** — nenhum concorrente tem
- ✅ **Não-programador como público-alvo** — os outros assumem desenvolvedor experiente
- ✅ **Vitrine de gêneros** — nenhum concorrente oferece catálogo de "o que posso criar"

**Oportunidade:** O IvanMurzak/Godot-MCP implementa MCP Prompts e Resources nativos (especificação 2025-06-18). Podemos adotar Prompts como canal adicional para a vitrine (Onda 2+), mas **não agora** — a vitrine via `quickstart_manage(op="showcase")` é mais simples e resolve o problema imediato.

### 4.3 MCP Prompts e Resources como canal de descoberta

A spec MCP 2025-06-18 define:

- **Prompts:** Templates de interação expostos como slash commands. Cada prompt tem `name`, `title`, `description`, `arguments`. Servers declaram capability `prompts`. Cliente faz `prompts/list` → `prompts/get`.
- **Resources:** Dados contextuais endereçáveis por URI. Suportam `annotations` (audience, priority, lastModified). Cliente faz `resources/list` → `resources/read`.

**Decisão para 1.L:** NÃO implementar MCP Prompts/Resources agora. Motivo:
1. Nosso server já usa `prompts/list` para os 11 prompts (`criar-jogo`, `revisar-cena`, etc.)
2. A vitrine como tool (`op="showcase"`) é mais direta: o agente chama, recebe JSON, mostra ao usuário
3. Prompts MCP exigiriam que o VS Code os expusesse como slash commands — depende do host, não controlamos
4. Custo de implementação de Resources como canal de vitrine é alto para ganho marginal na Onda 1

**Para Onda 2+:** Avaliar expor a vitrine como MCP Resource (`godot://showcase/genres`) com annotations de prioridade.

### 4.4 Padrões de organização de projetos Godot

Do Godot Docs "Project Organization":
- **snake_case** para arquivos e pastas
- Assets agrupados perto das cenas que os usam
- `addons/` para código de terceiros
- `.gdignore` para pastas que o Godot não deve importar

**Aplicação ao 1.L:** As frases-âncora no `game_patterns.py` já seguem snake_case para as chaves. Os arquivos da vitrine (se gerarmos Markdown) devem seguir a mesma convenção.

### 4.5 Recomendações para implementação

| # | Recomendação | Custo | Impacto | Prioridade |
|---|---|---|---|---|

---

## 5. VS Code Prompts, Agent Skills & Onboarding Guiado (Pesquisa 2026-07-20 — Fatia 1.M)

> **Fontes:** VS Code Docs (Prompt Files, Agent Skills, Agent Customizations), MCP Spec 2025-11-25 (Prompts), agentskills.io

### 5.1 VS Code Prompt Files (`.prompt.md`)

Formato oficial do VS Code para comandos de barra (`/`):

```yaml
---
description: Descrição curta do que o prompt faz
name: nome-do-comando     # opcional, usa nome do arquivo se omitido
argument-hint: [arg1]     # hint no campo de input
agent: ask|agent|plan     # qual agente usar
model:                    # modelo opcional
tools:                    # lista de tools/tool sets
---
# Corpo do prompt em Markdown
```

**Localização:**
- Workspace: `.github/prompts/` (descoberto automaticamente pelo VS Code)
- User profile: gerenciado pelo Settings Sync (NÃO copiar manualmente)

**Correção crítica ao plano original:** O destino NÃO é `%APPDATA%/Code/User/prompts/`. O VS Code descobre prompts do workspace automaticamente da pasta `.github/prompts/`. O `init.py` deve copiar para `<projeto_godot>/.github/prompts/`, não para o perfil do usuário.

### 5.2 Agent Skills (`SKILL.md`) — Padrão Aberto

Formato mais recente e portável (agentskills.io):

```yaml
---
name: skill-name          # lowercase, hífens, max 64 chars
description: O que faz e quando usar (max 1024 chars)
argument-hint: [opcional]
user-invocable: true      # aparece no menu /
disable-model-invocation: false  # agente pode carregar automaticamente
context: inline|fork      # fork = executa em subagente isolado
---
# Instruções, scripts, exemplos
```

**Localização:**
- `.github/skills/`, `.claude/skills/`, `.agents/skills/` (workspace)
- `~/.copilot/skills/` (user profile)

**Carregamento progressivo (3 níveis):**
1. Discovery: lê `name` + `description` do frontmatter
2. Instructions: carrega corpo do `SKILL.md` no contexto
3. Resources: acessa arquivos adicionais só quando referenciados

### 5.3 Prompt Files vs Agent Skills — Decisão para 1.M

| Dimensão | `.prompt.md` | `SKILL.md` |
|---|---|---|
| Invocação | `/comando` manual | `/comando` ou automático |
| Complexidade | Arquivo único | Pasta com scripts, exemplos |
| Portabilidade | VS Code apenas | VS Code + CLI + Cloud |
| Padrão | VS Code específico | agentskills.io (aberto) |
| Uso atual no projeto | 6 arquivos em `.github/prompts/` | Nenhum |

**Decisão:** Manter `.prompt.md` para 1.M. Motivos:
- Já temos 6 prompts nesse formato, funcionando
- Agent Skills é mais poderoso mas requer migração — escopo de fatia separada
- O `init.py` só precisa copiar o que já existe
- Migrar para SKILL.md é material para Onda 2+ (quando tivermos scripts/exemplos para empacotar)

### 5.4 MCP Prompts (nível de protocolo)

O MCP expõe prompts via `prompts/list` e `prompts/get`. Nosso `resources/prompts.py` tem 11 prompts MCP (criar-jogo, revisar-cena, balancear, polir, deploy, debug, etc.). Estes são diferentes dos `.prompt.md` — são prompts que o agente de IA pode solicitar ao servidor MCP, não comandos de barra do usuário.

**Relação com 1.M:** Nenhuma mudança necessária. Os MCP prompts já funcionam. A fatia é sobre os `.prompt.md` (comandos de barra do VS Code).

### 5.5 Estratégia de onboarding guiado

O `print_guided_mode()` deve mostrar:
1. Lista de comandos disponíveis com descrição de 1 linha
2. Exemplo concreto de primeiro uso ("digite /plan")
3. Dica de quickstart ("crie um jogo de plataforma")

**Anti-padrões identificados na pesquisa:**
- Não mostrar TODOS os comandos de uma vez (sobrecarga cognitiva) — mostrar os 3 principais + "veja /manual para todos"
- Não usar jargão técnico ("rollup", "tool", "MCP") — usar linguagem de jogo
- Não assumir que o usuário sabe o que é um "prompt" ou "slash command"

### 5.6 Correção ao plano original

| Item do plano | Correção |
|---|---|
| Destino: `%APPDATA%/Code/User/prompts/` | ❌ Errado. Destino correto: `<projeto>/.github/prompts/` |
| `copy_prompts_to_vscode()` | Renomear para `copy_prompts_to_project()` |
| Merge com prompts existentes | ✅ Mantido — se projeto já tem `.github/prompts/`, mesclar |

### 5.7 Recomendações

| # | Recomendação | Custo | Impacto |
|---|---|---|---|
| R1 | Copiar `.github/prompts/` para `<projeto>/.github/prompts/` | Baixo | Alto |
| R2 | `print_guided_mode()` com os 3 comandos principais | Baixo | Alto |
| R3 | Adicionar `argument-hint` ao YAML dos prompts existentes | Baixo | Médio |
| R4 | Migrar para Agent Skills (SKILL.md) | Médio | Onda 2+ |
|---|---|---|---|---|
| R1 | Adicionar `quickstart_phrase_pt` a cada gênero em `game_patterns.py` | Baixo | Alto | ✅ Imediata |
| R2 | Implementar `quickstart_manage(op="showcase")` retornando JSON com frases | Baixo | Alto | ✅ Imediata |
| R3 | Adicionar tabela de vitrine no README.md | Baixo | Alto | ✅ Imediata |
| R4 | Agrupar gêneros por dificuldade (fácil/médio/difícil) na vitrine | Baixo | Médio | ✅ Imediata |
| R5 | Adicionar `tags_pt` para busca semântica na vitrine | Médio | Médio | Onda 2 |
| R6 | Expor vitrine como MCP Resource (`godot://showcase/genres`) | Médio | Baixo | Onda 2+ |
| R7 | Gerar Markdown da vitrine automaticamente via `docs_sync.py` | Baixo | Médio | Onda 2 |

### 4.6 Riscos e anti-padrões identificados

| Risco | Mitigação |
|---|---|
| Frase pronta não corresponde ao que o blueprint realmente gera | Cada frase deve ser testada: `quickstart_manage(op="run", phrase="...")` e verificar se o match é ≥ 0.3 |
| Vitrine muito grande intimida o usuário | Agrupar por dificuldade (3 grupos de ~6) e mostrar "fáceis" primeiro |
| Frases em PT-BR não dão match com blueprints em EN | O `_SYNONYMS` já cobre PT→EN; as frases usam palavras que estão nos sinônimos |
| Duplicação: frases no README e no código divergem | Gerar README da vitrine via script que lê `game_patterns.py` (docs_sync) |
| Tabs (não espaços) | ✅ |
| Linhas < 100 chars | ✅ |
| Espaço após `#` | ✅ |
| Double quotes | ✅ |
| `and`/`or`/`not` (não `&&`/`||`/`!`) | ✅ |

---

## 4. Descobertas e Recomendações

### 4.1 Oportunidades de melhoria (priorizadas por impacto)

| # | Melhoria | Fonte | Impacto | Esforço |
|---|----------|-------|---------|---------|
| P1 | Usar MCP `elicitation` para confirmações | MCP Spec | 🔴 Alto | Médio |
| P2 | Usar MCP `logging` para enviar logs ao VS Code | MCP Spec | 🟠 Médio | Baixo |
| P3 | Separar mcp_addon e mcp_dock como sub-plugins | Godot Docs | 🟡 Baixo | Médio |
| P4 | Adicionar `@export` para configurar porta no dock | Style Guide | 🟡 Baixo | Baixo |
| P5 | MCP `resources` para expor estado do projeto | MCP Spec | 🟡 Baixo | Alto |
| P6 | MCP `tasks` para build/export assíncrono | MCP Spec | 🟡 Baixo | Alto |
| P7 | MCP `progress` para barra de progresso | MCP Spec | 🟡 Baixo | Médio |

### 4.2 Verificações de conformidade

| Verificação | dock.gd | server.py | init.py |
|-------------|---------|-----------|---------|
| GDScript Style Guide | 90% ✅ | N/A | N/A |
| Static Typing | 85% ✅ | N/A | N/A |
| MCP Spec (tools) | N/A | ✅ | N/A |
| MCP Spec (notifications) | N/A | ⚠️ Parcial | N/A |
| Python PEP 8 | N/A | ✅ | ✅ |

### 4.3 Anti-padrões identificados (prevenção)

| Anti-padrão | Onde | Prevenção |
|-------------|------|-----------|
| `:=` com `JSON.new()` em @tool | dock.gd:365 | ✅ Já validado, não dispara warning |
| `Dictionary.get()` com `:=` em @tool | dock.gd:367 | ✅ Já validado |
| Variáveis duplicadas no mesmo escopo | Corrigido | ✅ validate_gdscript.py |
| MCP sem notificação de mudança de tools | server.py | ⚠️ `tools/list_changed` poderia ser enviado |

---

## 5. Conclusão

O projeto está **bem alinhado** com as melhores práticas das fontes consultadas:

- ✅ MCP: Usamos tools corretamente. Oportunidade: `elicitation` para confirmações.
- ✅ Godot Plugins: dock segue o padrão oficial.
- ✅ GDScript: 90% conforme style guide.
- ✅ UX: 14 melhorias implementadas (Apple HIG + Material Design).
- ⚠️ Oportunidade: MCP `logging` para structured logs em vez de `print()`.
- ⚠️ Oportunidade: MCP `progress` para operações longas.

**Nenhuma regressão, incompatibilidade ou mudança arquitetural necessária.**

---

## 6. Telemetria Opt-in de Ferramenta de Desenvolvimento (Pesquisa 2026-07-21 — Fatia 1.P)

### 6.1 Fontes consultadas

| Fonte | URL | O que foi consultado |
|---|---|---|
| MCP Specification 2025-06-18 | modelcontextprotocol.io | Logging capability, primitivas de cliente, segurança e consentimento |
| MCP Python SDK (v1.x/v2) | github.com/modelcontextprotocol/python-sdk | API, hooks, padrões de servidor |
| VS Code Telemetry Guide | code.visualstudio.com/api | `isTelemetryEnabled`, `telemetry.json`, custom telemetry |
| Mozilla Glean SDK | mozilla.github.io/glean | Privacy-first telemetry, Python SDK, métricas declarativas |
| Python `logging` module | docs.python.org/3/library/logging | API padrão, handlers, thread safety |
| `structlog` (Hynek Schlawack) | pypi.org/project/structlog | Structured logging para Python |
| MCP Reference Servers | github.com/modelcontextprotocol/servers | Zero servidores de referência com telemetria |
| Python `json` module | docs.python.org/3/library/json | JSON Lines pattern (`--json-lines`) |

### 6.2 Estado da arte

#### 6.2.1 MCP Protocol — NÃO tem telemetria nativa

O protocolo MCP (2025-06-18) **não define primitiva de telemetria**. O que existe:

- **Logging capability:** Servidores podem enviar mensagens de log ao cliente via `logging/setLevel` e `notifications/message`. Isso é log operacional (debug, info, warning), não telemetria de uso.
- **Security principles:** Consentimento explícito, data privacy, tool safety — princípios que se aplicam perfeitamente à telemetria.
- **V2 SDK (2026-07-28):** Em beta. Nosso projeto usa v1.x (`mcp>=1.27,<2`). Nenhuma novidade de telemetria na v2.

**Conclusão:** Não há padrão MCP para telemetria. Somos pioneiros nisso. Isso é uma oportunidade (definimos o padrão) e um risco (sem referência para seguir).

#### 6.2.2 VS Code Telemetry — padrão ouro de DX tooling

O guia oficial de telemetria do VS Code define 2 abordagens aprovadas:

**Abordagem A — Módulo oficial:**
- `@vscode/extension-telemetry` (npm, Azure Monitor/Application Insights)
- Não aplicável a nós (servidor Python, não extensão TypeScript)

**Abordagem B — Solução customizada:**
- Respeitar `isTelemetryEnabled` e `onDidChangeTelemetryEnabled`
- Tag `telemetry` e `usesOnlineServices` em settings customizadas
- Arquivo `telemetry.json` na raiz (transparência: lista tudo que é coletado)

**Regras universais (aplicáveis a nós):**

| ✅ Do | ❌ Don't |
|---|---|
| Consentimento explícito do usuário | Telemetria ligada por padrão |
| Coletar o mínimo possível | Coletar PII (Personally Identifiable Information) |
| Transparência total (`telemetry.json`) | Coletar mais do que o necessário |
| Respeitar toggle global | Ignorar `isTelemetryEnabled` |

#### 6.2.3 Mozilla Glean — privacy-first, mas pesado

Glean é o SDK de telemetria do Firefox. Princípios de design:

- **Métricas declarativas em YAML** (`metrics.yaml`) — define o que é coletado ANTES de codificar
- **Built-in privacy guarantees** — dados nunca saem sem revisão
- **Python SDK** disponível (`glean_sdk` no PyPI), mas requer Rust/Cargo para compilar em plataformas não-glibc
- **Pings:** Upload em processo separado, atexit handler

**Por que NÃO usar:**
1. Dependência pesada (Rust + Cargo) — viola princípio de zero dependências externas
2. Overkill para telemetria local sem envio a servidor
3. Glean é desenhado para telemetria que sai da máquina (upload a servidor). Nosso caso é o oposto: dados ficam 100% locais.

**O que APRENDER do Glean:**
- Separar definição do que é coletado (schema) do código que coleta
- Toda métrica tem documentação obrigatória
- Privacy by design: cada métrica passa por review de privacidade

#### 6.2.4 Python `logging` + `json` — simplicidade máxima

A abordagem mais simples e robusta para telemetria local:

- **`logging` module:** stdlib, thread-safe, hierárquico, handlers plugáveis
- **JSON Lines (JSONL):** `python -m json --json-lines`, append-only, O(1) por evento, cada linha é um JSON válido
- **`json` module:** stdlib, `json.dumps()` com `ensure_ascii=False`, `separators=(',', ':')` para compacto

**Vantagens:**
- Zero dependências externas
- Thread-safe nativamente
- JSONL é parseável linha a linha (não precisa carregar arquivo inteiro)
- Append-only = sem corrupção de dados
- Fácil de exportar/analisar com qualquer ferramenta (jq, pandas, etc.)

#### 6.2.5 `structlog` — structured logging profissional

Biblioteca madura (2013-presente, 4.8k estrelas) para logging estruturado em Python:

- Renderização flexível: JSON, logfmt, console colorido
- Integração com `logging` stdlib
- Processors pipeline (filtros, transformações)
- Bound loggers (contexto imutável por logger)

**Por que NÃO usar:**
- Dependência externa adicional (mesmo que leve)
- Complexidade desnecessária para nosso caso (JSONL com `json.dumps` já resolve)
- Não queremos logging — queremos eventos discretos de telemetria

### 6.3 Decisão de arquitetura

**Abordagem escolhida: Zero dependências — `json` stdlib + arquivo JSONL + hook em `call_tool()`**

| Dimensão | Decisão | Justificativa |
|---|---|---|
| Formato | JSON Lines (`.jsonl`) | Append-only, parseável linha a linha, stdlib |
| Armazenamento | Arquivo local no projeto (`.mcp_telemetry_events.jsonl`) | Zero envio externo, transparência total |
| Consentimento | Arquivo `.mcp_telemetry_consent.json` (por projeto) | Explícito, desligado por padrão |
| Interface | Rollup `mcp_telemetry_manage(op=...)` | Padrão do projeto (`budget_manage`) |
| Integração | Hook fail-open em `call_tool()` | Padrão do projeto (`track_tool_cost`) |
| Dependências | **Zero** — só stdlib (`json`, `pathlib`, `time`, `threading`) | Consistente com `budget_ops.py` |
| Schema | Constantes no código (`_TELEMETRY_EVENT_TYPES`) | Sem YAML externo, sem parser adicional |

### 6.4 O que coletamos (schema)

| Campo | Tipo | Descrição | PII? |
|---|---|---|---|
| `event_type` | string | `tool_call`, `session_start`, `phase_transition`, `error` | Não |
| `timestamp` | ISO 8601 | UTC | Não |
| `session_id` | UUID | Gerado no início da sessão MCP | Não |
| `tool_name` | string | Nome da tool (ex: `scene_manage`) | Não |
| `phase` | string | Fase atual do projeto (ex: `PROTOTIPO`) | Não |
| `duration_ms` | int | Tempo de execução da tool | Não |
| `is_error` | bool | Se a tool retornou erro | Não |
| `error_code` | int | Código de erro (se aplicável) | Não |
| `mcp_version` | string | Versão do MCP (do `server.py`) | Não |

**NUNCA coletamos:** argumentos das tools, nomes de projetos, paths, conteúdo de arquivos.

### 6.5 Privacidade e conformidade

- **GDPR:** Dados 100% locais, zero PII, consentimento explícito → **isento** de obrigações GDPR (não há processamento de dados pessoais, não há transferência).
- **LGPD (Brasil):** Mesma lógica. Dados anônimos e locais = fora do escopo.
- **COPPA:** Não aplicável (ferramenta de desenvolvimento, não produto infantil).

### 6.6 Anti-padrões e armadilhas

| Anti-padrão | Risco | Prevenção |
|---|---|---|
| Telemetria ligada por padrão | Perda de confiança, violação de privacidade | Consent file com `consent: false` por default |
| Coletar argumentos de tools | Vazamento de código do usuário | Só coletamos metadados (nome, fase, duração, erro) |
| Envio automático a servidor | Violação de privacidade, problema legal | Zero código de rede no módulo |
| Hook síncrono pesado | Degradação de performance do MCP | JSONL append é O(1); hook é fail-open |
| Arquivo único sem lock | Corrupção em chamadas concorrentes | `threading.Lock` (igual `budget_ops.py`) |
| Confundir com `telemetry_ops.py` (5.4) | Duplicação de funcionalidade | 5.4 = telemetria DE JOGO. 1.P = telemetria DO MCP. |

### 6.7 Oportunidades futuras (pós-1.P)

| Oportunidade | Custo | Benefício |
|---|---|---|
| Dashboard local (HTML gerado a partir do JSONL) | Médio | Visualizar uso sem ferramenta externa |
| `telemetry.json` (transparência) | Baixo | Documentar schema publicamente |
| Integração com `isTelemetryEnabled` do VS Code | Baixo | Respeitar toggle global do editor |
| Análise de funil (`op=funnel`) | Baixo | "Quantos usuários chegam à fase PROTOTIPO?" |
| Heatmap de erros | Baixo | "Qual tool mais falha?" |

### 6.8 Conclusão da pesquisa

A abordagem de **zero dependências com JSONL stdlib** é a correta para este projeto porque:

1. **Alinhada com a arquitetura existente:** `budget_ops.py` já usa o mesmo padrão (hook em call_tool, estado em arquivo local, threading.Lock, fail-open).
2. **Privacidade por design:** Dados nunca saem da máquina. Consentimento explícito. Zero PII.
3. **Simplicidade máxima:** ~200 linhas de código, zero novas dependências no `requirements.txt`.
4. **Extensível:** JSONL é o formato mais portável que existe. Qualquer ferramenta consegue ler.
5. **Segue padrões da indústria:** Alinhado com as diretrizes do VS Code (consentimento, minimalidade, transparência) e com os princípios de privacidade do Glean (schema declarado, revisão de privacidade).


---

## 7. ONDA 4 — MUNDO: Distribuição, Monetização, Comunidade, Identidade, Métricas

> **Data:** 2026-07-21 | **Pesquisa nível extremo — saturação**
> **Fontes:** Godot Asset Library (godotengine.org/asset-library, 5.227 assets), itch.io Creator Docs (payments, getting started, 29.680 tools), GitHub Sponsors ($40M+ distribuídos, 4.2K+ orgs, 103 regiões), opensource.guide (Getting Paid, Metrics, Best Practices), Steamworks (Steam Direct $100/fee), imjp94/gd-plug (296★, plugin manager), Discord Safety Center, CHAOSS Community Metrics
> **Abrangência:** 7 fatias da ONDA 4 (4.A a 4.G) + temas adjacentes

### 7.1 Distribuição de Addons Godot — Canais e Ecossistema

#### 7.1.1 AssetLib Oficial (godotengine.org/asset-library)

**Estado atual:** 5.227 assets publicados. Mantida em modo "maintenance mode" — será substituída pela loja da Godot Foundation no futuro, mas ainda é o canal primário.

**Concorrentes MCP+Godot já na AssetLib (página 1 de busca):**

| Projeto | Versão | Godot | Licença | Diferencial |
|---|---|---|---|---|
| Godot-MCP (IvanMurzak) | 0.19.0 | 4.3 | Apache-2.0 | C#, cloud, runtime mode, 39 tools |
| Open Godot MCP | 0.1.1 | 4.3 | MIT | Simples |
| Godot MCP Pro | 1.15.1 | 4.4 | Proprietário | Pago |
| Beckett (AI MCP) | 1.10.1 | 4.4 | MIT | — |
| Breakpoint MCP | 1.7.0 | 4.2 | MIT | Foco em debugging |
| Godot Agent | 1.0.1 | 4.0 | MIT | — |
| Godot Runtime Bridge | 2.1.0 | 4.5 | MIT | Só bridge |

**Nosso diferencial competitivo (confirmado):**
- ✅ Somos o único **dono do processo inteiro** (fases, gates, verificação)
- ✅ **Python** (barreira de entrada menor que C#)
- ✅ **PT-BR nativo** — nenhum concorrente tem
- ✅ **Não-programador como público-alvo** — todos os outros assumem dev experiente
- ✅ **285 tools** — nenhum concorrente chega perto (IvanMurzak: 39)
- ✅ **Playtest automatizado** (smoke + personas + LLM) — único no mercado

**Regras de submissão:**
- `.zip` com `addons/<nome>/plugin.cfg` na raiz
- `plugin.cfg` com `[plugin] name, description, author, version, script`
- Licença compatível: MIT ✅
- Categorias: 2D Tools, 3D Tools, Scripts, Tools, Misc, Demos, Materials, Projects, Tutorials
- Submissão via formulário web (login com conta Godot)
- **Não há API programática** — o upload é manual
- Aprovação: ~1-3 dias, revisão humana

**Boas práticas de discoverability na AssetLib:**
- Descrição curta na primeira linha (aparece no card de busca)
- Tags relevantes (max ~10): mcp, copilot, ai, editor, bridge, websocket, godot, automation
- Screenshot/GIF do dock funcionando (315x250 ou maior, mesma proporção)
- Categoria correta: "Tools" (não "Scripts" nem "Misc")
- Godot version: usar a versão exata testada (4.7)
- Incluir link para GitHub, documentação, comunidade

#### 7.1.2 itch.io como Canal de Distribuição

**Escala:** 29.680 tools listadas. Plataforma aberta para qualquer tipo de conteúdo.

**Vantagens para o nosso caso:**
- **Open Revenue Sharing:** você escolhe quanto repassar ao itch.io (0% a 100%, default 10%)
- **"Pay what you want":** ideal para ferramentas open source — download grátis, doação opcional
- **Sem curadoria:** publica instantaneamente, sem revisão humana
- **Múltiplos formatos:** .zip, .exe, HTML5, PDF — aceita qualquer coisa
- **Analytics:** views, downloads, purchases, referrers
- **Press system:** distribuição gratuita para imprensa/YouTubers
- **Tags e busca:** SEO interno por tags + engines externas (Google indexa)
- **Devlogs:** blog integrado para updates do projeto

**Pagamentos no itch.io:**
- Modos: Direct to you (PayPal/Stripe, você é merchant of record) OU Collected by itch.io (payout system, itch.io é merchant)
- Taxa de pagamento: $0.30 + 2.9% por transação (padrão PayPal/Stripe)
- Payout mínimo: $5.00 USD
- Suporta VAT automático (EU)
- Retenção fiscal: 30% para não-EUA sem tratado (Brasil tem tratado — taxa reduzida com CPF/CNPJ)

**O que publicar no itch.io:**
- **Pacote MCP Godot Agent completo** (servidor Python + addons Godot)
- **Templates de gênero** (versão standalone de cada blueprint)
- **Jogos-semente** (Breakout, Shardbreaker) como exemplos jogáveis
- **Asset packs** (estilo visual consistente para cada gênero)

**Estratégia de preço recomendada:**
- Core (servidor MCP + addons): **grátis / "pay what you want"**
- Blueprints premium: **$2–5** (mínimo $2 para evitar taxa >30%)
- Asset packs: **"pay what you want" com mínimo $0**
- Jogos-semente: **grátis** (funcionam como marketing)

#### 7.1.3 gd-plug — Gerenciador de Plugins Alternativo

**imjp94/gd-plug** (296★, MIT): Gerenciador minimalista de plugins estilo vim-plug.

**Funcionalidades relevantes:**
- Instalação via Git (branch, tag ou commit específico)
- Version freeze (trava versão exata de cada plugin)
- `plug.gd` como arquivo de configuração (GDScript)
- Paralelo (download/instalação simultânea)
- Post-update hooks (callbacks após instalar/atualizar)
- Modo dev/production (plugins só de desenvolvimento)

**Aplicabilidade ao nosso projeto:**
- Podemos gerar `plug.gd` automaticamente para projetos criados com nosso MCP
- O `init.py` poderia opcionalmente configurar gd-plug como gerenciador de dependências
- Nosso addon aparece na lista de plugins gerenciáveis → canal adicional de descoberta
- **Risco:** gd-plug exige Git instalado — nossa persona não-programador pode não ter

#### 7.1.4 Canais de distribuição alternativos (mapeados)

| Canal | Tipo | Público | Esforço | Retorno |
|---|---|---|---|---|
| **AssetLib** | Oficial, dentro do editor | Devs Godot | Baixo (já feito — 4.A) | ⭐⭐⭐⭐⭐ |
| **itch.io** | Marketplace aberto | Indie devs, game jammers | Baixo (upload manual) | ⭐⭐⭐⭐ |
| **gd-plug** | Gerenciador de plugins | Devs Godot avançados | Baixo (compatibilidade) | ⭐⭐⭐ |
| **GitHub Releases** | Download direto | Devs em geral | Zero (já existe) | ⭐⭐⭐ |
| **Godot Forums** | Comunidade oficial | Devs Godot | Médio (post + manutenção) | ⭐⭐⭐ |
| **Reddit (r/godot)** | Comunidade | 200K+ membros | Baixo (post) | ⭐⭐⭐ |
| **YouTube/tutorial** | Conteúdo | Público geral | Alto (produção) | ⭐⭐⭐⭐ |
| **Game jams (Godot Wild Jam)** | Evento | Game devs | Médio (participação) | ⭐⭐⭐⭐ |
| **GodotCon/eventos** | Presencial | Comunidade Godot | Alto | ⭐⭐⭐ |

---

### 7.2 Monetização Open Source — Estratégias e Evidência

#### 7.2.1 GitHub Sponsors

**Escala:** $40M+ distribuídos, 4.2K+ organizações patrocinando, 103 regiões.

**Melhores práticas para tiers (do opensource.guide e casos reais):**

| Tier | Valor sugerido | Benefício | Evidência |
|---|---|---|---|
| **☕ Coffee** | $1–2/mês | Nome no README, badge de apoiador, acesso a devlogs | Baixa barreira, alto volume (Homebrew, curl) |
| **🚀 Supporter** | $5–10/mês | Vote em próximas features, acesso antecipado a releases beta | Mais popular entre dev tools |
| **⚡ Pro** | $25–50/mês | Suporte prioritário (resposta em 48h), sessão de onboarding 1:1 | "Resposta a issue em 48h" converte MUITO mais que "apoie meu trabalho" |
| **🏭 Enterprise** | $100–500/mês | Suporte dedicado, features sob demanda, consultoria, logo no site | Ex: Sidekiq, webpack (via OpenCollective) |

**Princípios de tiers eficazes:**
- ❌ **NUNCA** genérico ("apoie meu trabalho", "me ajude")
- ✅ **SEMPRE** benefício nomeado, concreto, de valor percebido
- ✅ Primeiro tier abaixo de $5 para capturar volume
- ✅ Tier "Pro" com benefício que custa pouco para entregar mas vale muito para o usuário
- ✅ Meta pública ("$500/mês = 1 dia/semana dedicado ao projeto")

**Exemplos reais:**
- **Homebrew:** $1–25/mês via GitHub Sponsors + OpenCollective
- **curl:** $5–50/mês, meta de $15K/mês (87% atingido)
- **webpack:** OpenCollective com tiers por empresa (Bronze $250, Silver $1K, Gold $5K)
- **Shopify:** usa GitHub Sponsors para gerenciar patrocínios a dependências open source

#### 7.2.2 Modelos de Negócio Open Source (além de Sponsors)

| Modelo | Como funciona | Exemplos | Aplicabilidade |
|---|---|---|---|
| **Open Core** | Núcleo MIT grátis, funcionalidades premium pagas | Sidekiq, GitLab | ⚠️ Difícil executar bem solo |
| **Dual Licensing** | MIT para uso aberto, licença comercial para closed-source | Qt, MySQL | ⚠️ Complexo juridicamente |
| **Hosted/SaaS** | Serviço hospedado pago, código aberto | Ghost, Travis CI | ❌ Fora de escopo (consome tempo) |
| **Consultoria** | Serviços pagos de implementação | Empresas de Godot | ❌ Fora de escopo permanente |
| **Assets/Templates** | Venda de blueprints, assets, seeds | itch.io asset stores | ✅ Mais viável para nosso caso |
| **Educação** | Cursos, tutoriais, workshops | GDQuest | ✅ Onda futura (modo professor já existe) |
| **Sponsorships** | Doações com benefícios nomeados | Homebrew, curl, webpack | ✅ GitHub Sponsors (4.C) |

**Decisão recomendada:** GitHub Sponsors + itch.io (pay what you want) + AssetLib (grátis). Sem open core, sem dual licensing, sem SaaS. Simplicidade máxima.

#### 7.2.3 Métricas financeiras realistas

**Referências do mercado de ferramentas Godot:**
- Godot-MCP (IvanMurzak/178★): tem tier pago com cloud (ai-game.dev), sem dados públicos de receita
- GDQuest: cursos pagos (modelo de educação), YouTube 100K+ inscritos
- Addons populares na AssetLib: maioria grátis (MIT), monetizam via consultoria ou patrocínio

**Projeção realista para MCP Godot Agent (12 meses):**
- GitHub Sponsors (1–5 apoiadores): $5–50/mês
- itch.io (blueprints premium): $10–100/mês
- AssetLib: $0 (canal gratuito de descoberta)
- **Total projetado:** $15–150/mês no primeiro ano

---

### 7.3 Steam Publishing — Shardbreaker como Prova (4.E)

> **Fonte:** Steamworks Partner Portal, Steam Direct documentation
> **Acesso:** Conteúdo confidencial Valve — requer NDA

#### 7.3.1 Steam Direct — Processo

**Custo:** $100 USD por produto (reembolsável quando receita bruta ≥ $1,000 USD)
**Prazo:** 30 dias de espera após pagamento + 2 semanas de página "Coming Soon"

**Passos:**
1. Assinar papelada digital (dados bancários, tributários, verificação de identidade)
2. Pagar $100 USD (qualquer forma de pagamento Steam, exceto Carteira Steam)
3. Preencher dados bancários + formulário fiscal (W-8BEN para Brasil)
4. Criar página da loja + upload de builds + configurar preço
5. Review pela Valve (1–5 dias): rodam o jogo, verificam página, conferem funcionamento
6. Período de espera: 30 dias (desde o pagamento) + página "Coming Soon" ≥ 2 semanas
7. Lançamento: botão "Release" — controle total do desenvolvedor

**Requisitos de página da loja:**
- **Cápsulas (capsules):** Header (460x215), Small (231x87), Main (616x353), Vertical (374x448)
- **Screenshots:** mínimo 5, recomendado 10–20, 1280x720 ou 1920x1080
- **Trailer:** obrigatório, YouTube (ou similar), recomendado < 2 min
- **Descrição curta** (aparece no topo da loja, ~300 chars)
- **Descrição longa** (formato Rich Text, seções: About, Features, System Requirements)
- **Tags/Gêneros:** até 20 tags (ex: Indie, Action, 2D, Pixel Graphics, Singleplayer)

**Conteúdo proibido (relevante para Shardbreaker):**
- ✅ Jogos feitos com IA: permitidos, mas exigem **disclosure** (3.J já implementado!)
- ❌ Conteúdo que você não possui direitos
- ❌ Jogos com blockchain/NFT/crypto
- ❌ Ad-supported business models

#### 7.3.2 Estratégia de Lançamento para Shardbreaker

**Pré-lançamento (3 meses antes):**
1. Página "Coming Soon" no Steam — coletar wishlists
2. Trailer de 60–90 segundos (gameplay real, sem cinematics)
3. Demo grátis (versão limitada) — gera wishlists, testa funil
4. Press kit: screenshots, logo, descrição, fact sheet (formato ZIP)

**Lançamento:**
5. Preço: $4.99–9.99 (indie pequeno, primeira publicação)
6. Desconto de lançamento: 10–15% na primeira semana
7. Post no r/godot, r/indiegames, r/playmygame (Reddit)
8. Gameplay no YouTube (envio para canais de indie games)

**Pós-lançamento:**
9. Atualizações quinzenais (correções + conteúdo novo)
10. Responder reviews (Steam mostra "Developer Response")
11. Descontos sazonais (Summer Sale, Winter Sale, etc.)

#### 7.3.3 O valor do Shardbreaker como "prova"

**Este é o argumento mais forte de marketing que existe:**
- Um jogo **publicado e funcional** feito inteiramente com o MCP Godot Agent
- Página no Steam com: "Este jogo foi desenvolvido do zero usando apenas linguagem natural, com MCP Godot Agent gerenciando o ciclo completo"
- Link na AssetLib, itch.io, README, e landing page: "Veja o que é possível criar"
- Game jams são uma alternativa de custo zero (Godot Wild Jam, itch.io jams)

**Alternativa de custo zero:** Publicar o Shardbreaker só no itch.io primeiro (sem custo, sem review). Se tiver tração (>100 downloads, feedback positivo), investir os $100 do Steam Direct.

---

### 7.4 Comunidade — Canais e Estratégia (4.F)

#### 7.4.1 GitHub Discussions vs Discord — Comparação Técnica

| Dimensão | GitHub Discussions | Discord |
|---|---|---|
| **Público** | Desenvolvedores (já no GitHub) | Comunidade gamer/dev |
| **Descoberta** | Indexado pelo Google, buscável no GitHub | Fechado, requer convite |
| **Assincronia** | Fórum tradicional (threads, respostas longas) | Chat em tempo real, fácil de perder |
| **Moderação** | GitHub Community Guidelines, automática (spam) | Manual, requer moderadores dedicados |
| **Integração** | Nativo: issues, PRs, commits, mentions | Webhooks + bots (integração manual) |
| **Manutenção** | Baixa — GitHub cuida da infra | Média/alta — moderar chat ao vivo |
| **Custo** | Grátis (repositório público) | Grátis (comunidade padrão) |
| **Suporte** | Ideal: bug reports, feature requests, troubleshooting | Ideal: comunidade, networking, quick help |
| **Permanência** | Conversas arquivadas, buscáveis para sempre | Mensagens efêmeras (limite de histórico no free tier) |

**Decisão recomendada:**
- **GitHub Discussions** PRIMEIRO — ativar no repositório (já existe `CONTRIBUTING.md` da 0.E)
- Categorias: 📢 Announcements, 💬 General, 🙏 Q&A, 💡 Ideas, 🐛 Bug Reports, 🎮 Showcase
- **Discord** DEPOIS (quando houver ≥ 50 usuários ativos) — custo de moderação é real

#### 7.4.2 Canais Complementares

| Canal | Quando ativar | Estratégia |
|---|---|---|
| **r/godot (Reddit)** | Imediato | Post mostrar o projeto + Shardbreaker como prova. Não spam. Participar da comunidade antes de divulgar |
| **Godot Forums** | Imediato | Thread oficial: "MCP Godot Agent — crie jogos em português com IA" |
| **YouTube** | Quando tiver Shardbreaker jogável | Tutorial: "Como criei um jogo sem programar — do zero ao Steam" |
| **Godot Wild Jam** | Próximo evento | Inscrever com jogo feito 100% via MCP. Marketing real |
| **BlueSky / X (Twitter)** | Imediato | Post regular: progresso, screenshots, GIFs do dock funcionando |

#### 7.4.3 Moderação e Governança

**Anti-padrões em comunidades open source (do opensource.guide):**
- ❌ Mantenedor fantasma (issues sem resposta por meses)
- ❌ Comunidade tóxica sem moderação → fuga de contribuidores
- ❌ Burocracia excessiva para contribuir (CLA extenso, processo de PR complexo)

**Regras para nossa comunidade:**
- ✅ `CONTRIBUTING.md` já existe (0.E) — guia de como contribuir
- ✅ `CODE_OF_CONDUCT.md` já existe (0.E) — base para moderação
- ✅ Response time público como meta: "respondemos issues em até 7 dias"
- ✅ Labels claras: `good first issue`, `help wanted`, `bug`, `enhancement`, `documentation`
- ✅ README com link para Discussions e comunidade

---

### 7.5 Nome e Identidade do Produto (4.D)

#### 7.5.1 Análise do Nome Atual

**Nome atual:** `mcp-godot-desenvolvimento`

| Dimensão | Avaliação | Problema |
|---|---|---|
| Descritivo | ✅ Diz o que é | Mas é técnico demais |
| Pesquisável | ❌ | "mcp" = protocolo técnico; "godot-desenvolvimento" = genérico |
| Memorável | ❌ | 25 caracteres, 3 hífens, ninguém lembra |
| Marketing | ❌ | Não evoca emoção, não sugere benefício |
| Pronúncia | ❌ | "eme-ce-pe-gô-dô-desenvolvimento" = trava na boca |
| Identidade visual | ❌ | Sem logo, sem paleta de cores, sem identidade |

#### 7.5.2 Princípios de Naming para Dev Tools

**Do que funciona no mercado (analisado de 50+ ferramentas):**

| Padrão | Exemplos | Quando usar |
|---|---|---|
| **Nome próprio + função** | Godot, Blender, Unity | Produto estabelecido, marca forte |
| **Verbo/função direta** | "Godot MCP", "Level Editor", "Tile Map" | Ferramentas utilitárias, AssetLib |
| **Nome abstrato/metáfora** | "Saga Engine", "Titon", "Prometheus", "Beckett" | Memorável, único, pesquisável |
| **Sigla pronunciável** | "GIMP", "VLC", "npm" | Curto, fácil de lembrar |
| **Composto criativo** | "Shardbreaker", "RPG in a Box", "GB Studio" | Evoca o propósito, único |

#### 7.5.3 Opções de Nome para Avaliação

| Nome | Tipo | Significado | Prós | Contras |
|---|---|---|---|---|
| **Saga Engine** | Metáfora | "Saga" = jornada completa — da ideia ao lançamento | Memorável, pesquisável, emocional | "Engine" soa como concorrente do Godot |
| **GameForge** | Composto | "Forge" = forjar, criar do zero | Direto, profissional | "Forge" é comum (Minecraft Forge, etc.) |
| **Projeto Saga** | Metáfora | Saga + projeto = ciclo completo | PT-BR natural | Inglês não entende |
| **CoreLoop** | Conceito | Core loop do game design | Técnico, preciso | Muito nichado |
| **Godot Guide** | Composto | Guia o processo, não só gera | Simples, claro | Perde o "MCP" do nome |

**Recomendação:** Manter `mcp-godot-desenvolvimento` como nome de repositório (SEO técnico). Criar nome de produto/marca separado para marketing. Ex: "**Saga** — crie seu jogo inteiro em português, da ideia ao lançamento." O repositório continua `mcp-godot-desenvolvimento`, o produto se chama **Saga**.

#### 7.5.4 Elementos de Identidade Necessários

- [ ] **Nome do produto** (não do repositório)
- [ ] **Logo** (SVG + PNG, variações: colorido, branco, ícone)
- [ ] **Paleta de cores** (2–3 cores primárias)
- [ ] **Tagline** (1 frase que vende): "Crie seu jogo inteiro em português, da ideia ao lançamento"
- [ ] **Tom de voz:** simples, direto, português brasileiro natural (sem "tu", "vós", "doravante")

---

### 7.6 Métricas de Produto e Sucesso (4.G)

#### 7.6.1 Framework CHAOSS + opensource.guide

**Métricas de Descoberta (Discovery):**
- GitHub stars (baseline de popularidade)
- Page views (GitHub Insights → Traffic)
- Unique visitors
- Referring sites (de onde vem o tráfego?)
- Search impressions (Google Search Console)
- AssetLib: número de downloads, page views

**Métricas de Uso (Usage):**
- Clones (GitHub clone graph)
- Downloads (GitHub Releases, itch.io, AssetLib)
- `init.py` execuções bem-sucedidas (telemetria opt-in — 1.P)
- `pip install` / `requirements.txt` instalações (PyPI stats, se publicarmos)

**Métricas de Retenção (Retention):**
- Contribuidores: total, novos, recorrentes, casuais
- Issues abertas/fechadas (velocidade de triagem)
- PRs abertos/mergeados
- Tempo médio até primeira resposta (mantainer responsiveness)
- Tempo médio até merge de PR

**Métrica de Produto (a que mais importa — 4.G):**
> **Quantas pessoas terminam um jogo usando esta ferramenta?**

Indicadores proxy (mais fáceis de medir):
1. Projetos criados que chegam à fase `PRONTO_PARA_LANCAR` (já temos o dado no `.roadmap_progress.json`)
2. Jogos publicados na AssetLib/itch.io/Steam que declaram uso do MCP
3. `fun_report` com 4 sinais positivos (balanceado, estratégia variada, etc.)
4. Depoimentos/testemunhais de usuários reais

#### 7.6.2 Dashboard de Métricas (proposta de tool)

Tool `metrics_manage(op=dashboard)` no MCP que gera:

```
📊 MCP Godot Agent — Métricas (2026-07-21)

Descoberta:
  ⭐ GitHub Stars:  X
  👁️ Page Views (7d): X (X únicos)

Uso:
  📥 Downloads (total): X
  🆕 Projetos criados: X
  🏁 Chegaram a PRONTO: X (X%)

Qualidade:
  🎮 fun_report médio: X/4 sinais positivos
  🐛 Issues abertas: X
  ⏱️ Tempo médio de resposta: X dias
  ✅ PRs mergeados (30d): X

Financeiro (se aplicável):
  💰 Sponsors mensal: $X
  🛒 itch.io receita (30d): $X
```

#### 7.6.3 Ciclo de Feedback

**Como saber se está funcionando:**
1. **Mês 1–3:** 10+ projetos criados, 1+ chega a PROTOTIPO
2. **Mês 3–6:** Primeira pessoa que NÃO É VOCÊ termina um jogo e publica
3. **Mês 6–12:** 3+ jogos publicados por pessoas diferentes (critério de saída da ONDA 4)
4. **Mês 12+:** 1+ jogo publicado no Steam feito com MCP Godot Agent

---

### 7.7 Oportunidades e Recomendações (além do roadmap atual)

#### 7.7.1 Funcionalidades de Distribuição que Ficaram de Fora

| # | Oportunidade | Custo | Impacto | Fatia sugerida |
|---|---|---|---|---|
| O1 | `publish_manage op=itchio_upload` — upload programático via itch.io API (butler) | Médio | Alto | 4.B+ |
| O2 | `publish_manage op=steam_build` — gerar build compatível com Steamworks SDK | Alto | Alto | 4.E+ |
| O3 | `publish_manage op=godot_export` — exportar jogo para Windows/Linux/HTML5 via MCP | Médio | Alto | Nova fatia |
| O4 | `publish_manage op=itchio_page` — gerar página HTML para itch.io a partir do README | Baixo | Médio | 4.B+ |
| O5 | Integração com gd-plug: `plug.gd` gerado automaticamente | Baixo | Médio | 4.A+ |

#### 7.7.2 Funcionalidades de Comunidade que Ficaram de Fora

| # | Oportunidade | Custo | Impacto | Fatia sugerida |
|---|---|---|---|---|
| O6 | `community_manage op=changelog` — gerar changelog formatado para GitHub Releases | Baixo | Alto | Nova fatia |
| O7 | `community_manage op=release_notes` — gerar release notes a partir dos commits | Baixo | Alto | Nova fatia |
| O8 | `community_manage op=roadmap_public` — gerar roadmap público em Markdown | Baixo | Médio | 4.F+ |
| O9 | Template de Issue/PR no `.github/` (bug report, feature request) | Baixo | Alto | 4.F+ |
| O10 | GitHub Actions: CI/CD que roda `auditar.py` em cada PR | Médio | Alto | Nova fatia |

#### 7.7.3 Funcionalidades de Marketing/Identidade

| # | Oportunidade | Custo | Impacto | Fatia sugerida |
|---|---|---|---|---|
| O11 | Landing page estática gerada a partir do README (GitHub Pages) | Baixo | Alto | 4.D+ |
| O12 | GIF/demo automático do dock funcionando para redes sociais | Baixo | Alto | Gap ONDA 3 (polish_manage) |
| O13 | `brand_manage op=generate` — gerar assets de marca (logo, cores, banner) | Baixo | Médio | 4.D+ |
| O14 | Badge "Made with MCP Godot Agent" para README de projetos | Baixo | Alto | 4.A+ |
| O15 | Game jam kit: template otimizado para Godot Wild Jam | Médio | Alto | 4.E+ |

#### 7.7.4 Funcionalidades de Qualidade/Confiança

| # | Oportunidade | Custo | Impacto | Fatia sugerida |
|---|---|---|---|---|
| O16 | Teste A/B de experiências de onboarding (qual fluxo gera mais projetos?) | Alto | Médio | Pós-ONDA 4 |
| O17 | Heatmap de erros: qual tool mais falha? (já temos telemetria — 1.P) | Baixo | Alto | Gap ONDA 4 |
| O18 | `quality_manage op=audit_public` — auditoria pública visível para transparência | Baixo | Alto | 4.F+ |
| O19 | Certificado de conclusão: "Você terminou seu jogo!" (PDF gerado) | Baixo | Médio | 4.G+ |

---

### 7.8 Riscos, Anti-Padrões e Armadilhas da ONDA 4

| Risco | Severidade | Mitigação |
|---|---|---|
| **Concorrência pesada na AssetLib** (6 MCPs já publicados) | 🔴 ALTO | Diferenciar com descrição PT-BR, foco em não-programador, "dono do processo", link para Shardbreaker |
| **AssetLib em maintenance mode** — substituição futura incerta | 🟠 MÉDIO | Diversificar canais: itch.io, GitHub Releases, gd-plug. Não depender só da AssetLib |
| **Baixa adoção inicial** (< 10 projetos criados) | 🟠 MÉDIO | Shardbreaker como prova. Game jam como marketing. Tutorial YouTube |
| **Discord exige moderação constante** | 🟠 MÉDIO | Começar com GitHub Discussions (assíncrono, baixa manutenção). Só migrar para Discord com ≥ 50 usuários |
| **Nome `mcp-godot-desenvolvimento` impublicável** | 🟡 BAIXO | Criar nome de produto separado do nome de repositório. "Saga" como sugestão |
| **Steam Direct $100 + 30 dias de espera** | 🟡 BAIXO | Publicar no itch.io primeiro (grátis). Steam só se tração ≥ 100 downloads |
| **Ninguém termina jogo (métrica 4.G = 0)** | 🔴 ALTO | Focar em jogo MUITO simples primeiro (Breakout, Flappy Bird). Depois escalar complexidade |
| **Documentação só em PT-BR limita alcance** | 🟡 BAIXO | README e AssetLib já têm versão EN. Priorizar tradução de tutoriais e manual |

---

### 7.9 Conclusão da Pesquisa

**O que a ONDA 4 deve priorizar (ordem revisada):**

1. ✅ **4.A — AssetLib** (concluído) — canal primário, dentro do editor
2. **4.D — Nome e identidade** — ANTES de publicar em qualquer outro lugar. Nome `mcp-godot-desenvolvimento` é repositório, não produto
3. **4.E — Shardbreaker** — a prova. Publicar no itch.io (grátis). Sem jogo publicado, não tem marketing
4. **4.B — itch.io** — publicar addon + Shardbreaker. Pay what you want
5. **4.F — Comunidade** — GitHub Discussions (já existe `CONTRIBUTING.md`). Template de issue/PR. Badge "Made with MCP"
6. **4.C — GitHub Sponsors** — tiers com benefícios nomeados. Só depois de existir comunidade
7. **4.G — Métricas** — dashboard `metrics_manage`. Métrica principal: quantas pessoas terminam um jogo

**Ordem original do roadmap vs ordem revisada:**
| Original | Revisada | Justificativa |
|---|---|---|
| 4.A AssetLib | 4.A ✅ | Já feito |
| 4.B itch.io | 4.D Nome | Sem nome, não publica em lugar nenhum |
| 4.C Sponsors | 4.E Shardbreaker | Sem prova, não tem marketing |
| 4.D Nome | 4.B itch.io | Com nome e prova, publica em todo lugar |
| 4.E Shardbreaker | 4.F Comunidade | Com produto publicado, cresce comunidade |
| 4.F Comunidade | 4.C Sponsors | Com comunidade, monetiza |
| 4.G Métricas | 4.G Métricas | Sempre relevante, pode correr em paralelo |

**A maior descoberta desta pesquisa:** O Shardbreaker (4.E) é a única fatia que multiplica o valor de TODAS as outras. Um jogo publicado é prova, marketing, conteúdo para redes sociais, material para tutorial, e resposta definitiva para "isso funciona?". Ele deveria vir ANTES de monetização e comunidade.
