# MCP Godot — Completo e Funcional + Recuperação

> **Repositório dedicado do MCP Godot Agent v2.9.**
> Tudo que você precisa para conectar o Godot 4.7 a qualquer IA agêntica
> e criar jogos por linguagem natural. Autocontido — clone e use.

---

## O que tem aqui

| Pasta/Arquivo | O que é |
|---|---|
| `server.py` | Servidor MCP (4.552 linhas, 143+ ferramentas) |
| `tools/` | 22 módulos de operação (cenas, scripts, física, UI, etc.) |
| `templates/` | 5 templates GDScript (Jinja2) |
| `classdb_cache/` | Cache da API do Godot 4.7 |
| `addon/` | Plugins Godot (mcp_bridge + game_bridge) |
| `config.json` | Configuração (caminhos do Godot + projeto) |
| `requirements.txt` | Dependências Python |
| `GUIA_CONEXAO.md` | Como usar — passo a passo do zero |
| `ARQUITETURA_MCP.md` | Como funciona por dentro — 3 camadas, padrões, extensão |

---

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
