# MCP Godot — Desenvolvimento

> **Servidor MCP Godot Agent v3.0 — 171 ferramentas para criação de jogos por linguagem natural.**
> Conecta Godot 4.7 ao VS Code Copilot (DeepSeek V4) via protocolo MCP.
> Autocontido — clone, instale dependências e use.

**Status:** ✅ 171 tools · 171 handlers · 46 bugs corrigidos · Pipeline Executor · DAP debugger · R$0

---

## O que tem aqui

| Pasta/Arquivo | O que é |
|---|---|
| `server.py` | Servidor MCP (~5950 linhas, 171 ferramentas) |
| `tools/` | 50+ módulos (cenas, scripts, física, arte IA, som IA, pipeline, etc.) |
| `resources/` | Game patterns (17 gêneros) + MCP Prompts (11 comandos) |
| `templates/` | Templates GDScript (Jinja2) |
| `classdb_cache/` | Cache da API do Godot 4.7 |
| `addons/` | Plugins Godot (mcp_bridge + game_bridge) |
| `config.json` | Configuração (caminhos do Godot + projeto) |
| `requirements.txt` | Dependências Python |
| `GUIA_CONEXAO.md` | Como usar — passo a passo do zero |
| `ARQUITETURA_MCP.md` | Como funciona por dentro — 3 camadas, padrões, extensão |

---

## Novidades da v3.0 (Onda 7)

| Feature | Descrição |
|---------|-----------|
| 🧩 **Pipeline Executor** | `create_entity` — cria entidade completa (cena+collider+script+sprite+áudio) em 1 chamada |
| 🤖 **Decision Engine** | Decide automaticamente se gera arte placeholder ou FLUX, com base no estágio do projeto |
| 📊 **Project State** | Snapshot em memória do projeto, atualizado por hooks automáticos |
| 🔒 **Sandbox** | 80+ padrões de segurança bloqueados em `execute_gdscript_runtime` |
| 🐛 **46 bugs corrigidos** | Auditoria completa em 4 grupos (CRITICAL/HIGH/MEDIUM/LOW) |

## Instalação (2 minutos)

```powershell
# 1. Clone este repositório
git clone <url-deste-repo>
cd mcp-godot-completo

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

**Versão:** 2.9 | **Tools:** 143+ | **Última atualização:** 2026-07-09
