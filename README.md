# MCP Godot — Desenvolvimento

> **Servidor MCP Godot Agent v3.2.1 — 191 ferramentas para criação de jogos por linguagem natural.**
> Conecta Godot 4.7 ao VS Code Copilot (DeepSeek V4) via protocolo MCP.
> Autocontido — clone, instale dependências e use.

**Status:** ✅ 190 tools · 190 handlers · 64 módulos · 18 patches · 5 grupos auditoria · 10 toolsets · 3 perfis · Pipeline Executor · DAP debugger · R$0

---

## O que tem aqui

| Pasta/Arquivo | O que é |
|---|---|
| `server.py` | Servidor MCP (~7300 linhas, 190 ferramentas) |
| `tools/` | 64 módulos (cenas, scripts, física, arte IA, som IA, pipeline, etc.) |
| `resources/` | Game patterns (17 gêneros) + MCP Prompts (11 comandos) |
| `templates/` | Templates GDScript (Jinja2) |
| `classdb_cache/` | Cache da API do Godot 4.7 |
| `addons/` | Plugins Godot (mcp_addon + mcp_runtime_bridge) |
| `config.json` | Configuração (caminhos do Godot + projeto) |
| `requirements.txt` | Dependências Python |
| `GUIA_CONEXAO.md` | Como usar — passo a passo do zero |
| `ARQUITETURA_MCP.md` | Como funciona por dentro — 3 camadas, padrões, extensão |

---

## Novidades da v3.2.1 (Auditoria e Hardening — 2026-07-12)

| Feature | Descrição |
|---------|-----------|
| 🛡️ **Sandbox conectado** | `write_file` + `safe_write_gdscript` validam antes de escrever .gd (36/36 padrões bloqueados) |
| 🧹 **Normalizador GDScript** | Remove comentários, colapsa whitespace, resolve concatenação — fecha 3/4 bypasses |
| 🐛 **Bugs B1-B3** | B2 runtime tools corrigido, B3 status corrigido, B1 documentado |
| 🔧 **Godot check desligado** | `tentar_checagem_godot=false` (padrão) — `--check-only` não funciona no Windows Godot 4.7 |
| 🪝 **Hook Stop NUCLEO** | `check-gate-failed.ps1` bloqueia encerramento se `.mcp_gate_failed` existir |
| 🧹 **Limpeza** | MCPs duplicados removidos, `config.json` untracked, paths corrigidos |
| 📚 **Docs sincronizados** | Todos os 6 docs + MCP ESTADO ATUAL atualizados para 190 tools |

## Novidades da v3.2 (Sessão anterior — 2026-07-12)

| Feature | Descrição |
|---------|-----------|
| 🔬 **Testes roteirizados** | `smoke_test`, `regression_test`, `run_scripted_tests`, `dump_mcp_state`, `estimate_tool_tokens` |
| 🔍 **Validação de referências** | `validate_project_refs`, `find_usages` (estático, offline, sem precisar do Godot aberto) |
| 📦 **Asset Manifest** | `import_asset_manifest` (5 fontes), `create_asset_manifest` |
| ⚡ **Runtime Bridge** | Servidor TCP GDScript (8790) + 4 tools (`screenshot`, `runtime_info`, `custom_command`, `list_custom_commands`) |
| 🔄 **Process Lifecycle** | `godot_run_project`, `godot_stop_project`, `godot_wait_for_bridge` com save-before-kill |
| 📚 **ClassDB Introspecção** | `godot_class_ref` via `extension_api.json` (Python puro), 1074 classes com herança, fuzzy suggestions |
| 🎯 **Curadoria de Toolsets** | `--toolsets` com 10 grupos nomeados (core, 2d, 3d, physics, ui, audio, art, debug, pipeline, advanced) |
| ⚙️ **Perfis** | `--profile core/dev/full` — inicie com 29, ~80 ou 189 tools (economiza tokens) |
| ✅ **Validação GDScript** | `safe_write_gdscript` com validação dupla (sintaxe local + `validate_gdscript.py`) |
| 🛡️ **Git Checkpoint** | `git_commit_checkpoint` com gates de compilação + GUT |
| 💰 **Cost Guard** | `allow_paid_generation=False` + `estimated_cost` em tools de arte IA |
| 🔧 **Config local** | `config.local.json` + `GODOT_MCP_*` env vars para overrides por máquina |
| 🐛 **43 bugs corrigidos** | Auditoria completa em 5 grupos (10 rodadas) |

### Histórico (v3.0)

| Feature | Descrição |
|---------|-----------|
| 🧩 **Pipeline Executor** | `create_entity` — cria entidade completa (cena+collider+script+sprite+áudio) em 1 chamada |
| 🤖 **Decision Engine** | Decide automaticamente se gera arte placeholder ou FLUX, com base no estágio do projeto |
| 📊 **Project State** | Snapshot em memória do projeto, atualizado por hooks automáticos |
| 🔒 **Sandbox** | 80+ padrões de segurança bloqueados em `execute_gdscript_runtime` |

## Instalação (2 minutos)

```powershell
# 1. Clone este repositório
git clone <url-deste-repo>
cd mcp-godot-desenvolvimento

# 2. Crie o ambiente virtual
python -m venv .venv

# 3. Instale as dependências
.venv\Scripts\pip install -r requirements.txt

# 4. Ajuste config.json com seus caminhos
#    (godot_path, godot_console_path, python_path)

# 5. Inicie o servidor
.venv\Scripts\python server.py
```

**Documentação completa:** leia `GUIA_CONEXAO.md` para o passo a passo detalhado.

---

## Requisitos

- Python 3.12+
- Godot 4.7
- VS Code + Copilot + DeepSeek (ou qualquer IA com suporte MCP)

---

## Para recuperar em outra máquina

1. Instale Python 3.12+ e Godot 4.7
2. Clone este repositório
3. Execute os passos de instalação acima
4. Ajuste `config.json` para os caminhos da máquina
5. Leia `GUIA_CONEXAO.md` se tiver dúvidas

---

**Versão:** 3.2 | **Tools:** 189 | **Módulos:** 64 | **Última atualização:** 2026-07-12
