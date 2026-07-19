# MCP Godot — Desenvolvimento

> **Servidor MCP Godot Agent v3.4.0 — 193 ferramentas para criação de jogos por linguagem natural.**
> Conecta Godot 4.7 ao VS Code Copilot (DeepSeek V4 Pro) via protocolo MCP stdio.
> Autocontido — clone, instale dependências e use.

**Status:** ✅ 193 tools · 193 handlers · 74 módulos · 23 patches · Bloco 1-4 · proof ledger · subprocess seguro · R$0

**GitHub:** `https://github.com/joabcostamd/mcp-godot-desenvolvimento`

---

## O que tem aqui

| Pasta/Arquivo | O que é |
|---|---|
| `server.py` | Servidor MCP (~7600 linhas, 193 ferramentas, stdio JSON-RPC 2.0) |
| `tools/` | 74 módulos Python (cenas, scripts, física, arte IA, som IA, pipeline, verificação, etc.) |
| `resources/` | Game patterns (17 gêneros) + MCP Prompts (11 comandos) |
| `templates/` | Templates GDScript (Jinja2) |
| `classdb_cache/` | Cache da API do Godot 4.7 (1074 classes) |
| `addons/` | Plugins Godot (mcp_addon + mcp_runtime_bridge) |
| `config.json.example` | Template de configuração |
| `requirements.txt` | Dependências Python |
| `MCP_ESTADO_ATUAL.md` | 📄 Documento canônico — TUDO sobre o MCP (arquitetura, 193 tools, protocolos, limitações) |
| `GUIA_CONEXAO.md` | Como usar — passo a passo do zero |
| `ARQUITETURA_MCP.md` | Como funciona por dentro — 3 camadas, padrões, extensão |
| `LEARNINGS.md` | 18 regras anti-padrão (R1-R18) |
| `CHANGELOG.md` | Histórico completo de versões |
| `pendencias.md` | Bugs ativos e resolvidos (legado) |
| `pendenciasMCP.md` | 📋 **Documento mestre de backlog v2.1.0** — 22 itens, 14 gaps, 8 KPIs, 7 riscos, 7 anti-padrões |

---

## 🆕 Novidades da v3.2.1 (2026-07-12)

### Item 1: Pipeline de Verificação (`run_verification_pipeline`)
| Feature | Descrição |
|---------|-----------|
| 🔬 **Pipeline 4 etapas** | Compile check → headless run → screenshot → GUT tests em 1 chamada |
| 📊 **Relatório JSON** | Status consolidado com evidência bruta de cada etapa + early exit |
| 📸 **Screenshot automático** | `--write-movie` com SW_HIDE, salva PNG em `verification_screenshots/` |
| ⚠️ **Ambiguity handling** | Retorna `ambiguous` se cena de teste não definida — não adivinha |
| 🐛 **6 bugs corrigidos** | BUG-V01 a V06 encontrados e resolvidos na própria implementação |

### Item 2: Fluxo EARS + Pipeline (Padrão de Fechamento de Pendência)
| Feature | Descrição |
|---------|-----------|
| 📋 **Fluxo documentado** | `AGENTS.md` no Star Colony: receber → EARS → aprovar → implementar → pipeline → relatório |
| 🎨 **EARS-B implementado** | VFX de evolução visual L1→L2→L3 com escala + borda por nível |
| ⌨️ **Gatilho debug** | Tecla U (provisório) — `spawn_explosion` + `spawn_floating_text` + `add_shake` |
| ✅ **Pixel evidence** | Análise de screenshot confirma borda prateada L2 (RGB 126,126,147) e dourada L3 (RGB 205,174,64) |

### Segurança & Infra (continuação)
| Feature | Descrição |
|---------|-----------|
| 🛡️ **Sandbox conectado** | `write_file` + `safe_write_gdscript` validam .gd antes de escrever (36/36 padrões) |
| 🧹 **Normalizador** | Remove comentários, colapsa whitespace, resolve concatenação — fecha 4/6 bypasses |
| 🔧 **Godot check off** | `tentar_checagem_godot=false` — `--check-only` quebrado no Windows Godot 4.7 (R12) |
| 🪝 **Hook Stop** | `check-gate-failed.ps1` bloqueia encerramento com gate falho |

---

## Histórico (v3.2.0 — 2026-07-12)

| Feature | Descrição |
|---------|-----------|
| 🔬 **Testes roteirizados** | `smoke_test`, `regression_test`, `run_scripted_tests`, `dump_mcp_state`, `estimate_tool_tokens` |
| 🔍 **Validação de refs** | `validate_project_refs`, `find_usages` (estático, offline) |
| 📦 **Asset Manifest** | `import_asset_manifest` (5 fontes), `create_asset_manifest` |
| ⚡ **Runtime Bridge** | Servidor TCP GDScript (8790) + screenshot, runtime_info, custom_command |
| 🔄 **Process Lifecycle** | `godot_run/stop_project`, `godot_wait_for_bridge` com save-before-kill |
| 📚 **ClassDB** | `godot_class_ref` via `extension_api.json`, 1074 classes, fuzzy suggestions |
| 🎯 **Toolsets** | `--toolsets` com 10 grupos + `--profile core/dev/full` (31/80/191 tools) |
| ✅ **Validação GDScript** | `safe_write_gdscript` com validação dupla (sintaxe local + sandbox) |
| 🛡️ **Git Checkpoint** | `git_commit_checkpoint` com gates de compilação + GUT |
| 💰 **Cost Guard** | `allow_paid_generation=False` + `estimated_cost` em tools de arte IA |
| 🐛 **43 bugs** | Auditoria completa em 5 grupos (10 rodadas) |

---

## Instalação (2 minutos)

```powershell
# 1. Clone
git clone https://github.com/joabcostamd/mcp-godot-desenvolvimento
cd mcp-godot-desenvolvimento

# 2. Ambiente virtual
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 3. Configure (copie config.json.example → config.json e ajuste os paths)
#    godot_path: caminho do Godot 4.7
#    godot_console_path: mesmo executável (Windows)

# 4. Inicie
.venv\Scripts\python server.py --profile dev
```

**Docs:** `MCP_ESTADO_ATUAL.md` (referência canônica) · `GUIA_CONEXAO.md` (passo a passo) · `ARQUITETURA_MCP.md` (internals)

---

## Requisitos

- Python 3.12+
- Godot 4.7
- VS Code + Copilot + DeepSeek V4 Pro (ou qualquer IA com suporte MCP)

---

## Para recuperar em outra máquina

1. Instale Python 3.12+ e Godot 4.7
2. Clone este repositório
3. Execute os passos de instalação acima
4. Ajuste `config.json` para os caminhos da máquina
5. Leia `MCP_ESTADO_ATUAL.md` para referência completa

---

**Versão:** 3.2.1 | **Tools:** 191 | **Módulos:** 69 | **Patches:** 18 | **Última atualização:** 2026-07-12
