# GUIA DE CONEXÃO — Godot 4.7 + MCP (do zero)

> **Leia este arquivo primeiro.** Ele contém TUDO que você precisa para conectar o
> Godot 4.7 ao servidor MCP e começar a criar jogos por linguagem natural.
> Funciona em qualquer computador, mesmo sem contexto prévio do nucleo.

---

## ARQUITETURA (o que cada peça faz)

```
┌──────────────────────────────────────────────────────────┐
│  SERVIDOR MCP (Python)                                   │
│  sistema/mcp-godot/servidor/server.py                    │
│  ├── tools/      ← 22 ferramentas (criar cena, nó, etc) │
│  ├── templates/  ← templates GDScript                    │
│  └── config.json ← caminhos do Godot + projeto padrão    │
│                                                          │
│  O servidor recebe comandos em linguagem natural,        │
│  traduz para operações no Godot, e aplica via TCP.       │
└──────────────┬──────────────────────┬────────────────────┘
               │ TCP :9080 (editor)   │ TCP :9081 (runtime)
               ▼                      ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  ADDON: mcp_bridge       │  │  ADDON: game_bridge      │
│  (dentro do projeto       │  │  (dentro do projeto      │
│   Godot)                  │  │   Godot)                 │
│  ───────────────────────  │  │  ─────────────────────── │
│  Recebe comandos de       │  │  Lê estado do jogo em    │
│  edição (criar cena,      │  │  tempo real (posição,    │
│  adicionar nó, script)    │  │  HP, colisões) e envia   │
│  e aplica no editor.      │  │  de volta pro servidor.  │
└──────────────────────────┘  └──────────────────────────┘
               │                      │
               └──────────┬───────────┘
                          ▼
               ┌─────────────────────┐
               │  PROJETO GODOT      │
               │  projetos/star-colony│
               │  (ou qualquer outro) │
               └─────────────────────┘
```

---

## PRÉ-REQUISITOS (o que precisa existir na máquina)

| Item | Como verificar | Onde baixar |
|---|---|---|
| Python 3.12+ | `python --version` | python.org |
| Godot 4.7 | Abrir Godot → versão no canto | godotengine.org |
| VS Code + Copilot + DeepSeek | Extensões instaladas | marketplace |

---

## PASSO A PASSO — Primeira máquina

### 1. Preparar o servidor (.venv + dependências)

```powershell
cd sistema\mcp-godot\servidor

# Criar ambiente virtual (só uma vez)
python -m venv .venv

# Instalar dependências
.venv\Scripts\pip install -r requirements.txt

# Verificar
.venv\Scripts\python -c "import mcp; print('MCP OK:', mcp.__version__)"
```

**O que isso faz:** Cria um Python isolado com o pacote `mcp` (1.28.1) e ~40 dependências
(httpx, uvicorn, pydantic, godot_parser, etc.). Sem isso, o servidor não inicia.

### 2. Configurar o config.json

Abra `sistema/mcp-godot/servidor/config.json` e ajuste **APENAS estes 3 campos**:

```json
{
  "godot_path": "C:\\Godot\\Godot_v4.7-stable_win64.exe",
  "godot_console_path": "C:\\Godot\\Godot_v4.7-stable_win64_console.exe",
  "default_project": "CAMINHO\\ATE\\SEU\\PROJETO"
}
```

- `godot_path`: onde o executável do Godot está instalado
- `godot_console_path`: versão console (para builds headless)
- `default_project`: a pasta do projeto Godot que você vai editar

### 3. Preparar o projeto Godot (instalar addons)

Dentro da pasta do SEU projeto Godot, você precisa de 3 pastas:

```
seu-projeto/
├── addon/
│   ├── game_bridge/     ← lê estado do jogo em tempo real
│   └── mcp_bridge/      ← recebe comandos de edição
├── .vscode/
│   └── mcp.json         ← diz ao VS Code onde está o server.py
└── project.godot
```

**O addon já existe** no Star Colony (`projetos/star-colony/addon/`).
Para um projeto NOVO, copie de lá:

```powershell
# Copiar addons para o novo projeto
xcopy /E /I projetos\star-colony\addon\game_bridge projetos\NOVO-PROJETO\addon\game_bridge
xcopy /E /I projetos\star-colony\addon\mcp_bridge projetos\NOVO-PROJETO\addon\mcp_bridge
```

### 4. Criar .vscode/mcp.json no projeto

Crie o arquivo `seu-projeto/.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "godot-mcp-agent": {
      "command": "python",
      "args": ["../../sistema/mcp-godot/servidor/server.py"],
      "env": {
        "PYTHONPATH": "../../sistema/mcp-godot/servidor"
      }
    }
  }
}
```

> O caminho `../../sistema/...` é relativo à pasta do projeto. Ajuste se a estrutura for
> diferente. O importante é que aponte para `server.py`.

### 5. Iniciar o servidor

```powershell
cd sistema\mcp-godot\servidor
.venv\Scripts\python server.py
```

Deixe esse terminal aberto. O servidor fica ouvindo nas portas 9080 (editor) e 9081
(runtime).

### 6. Abrir o Godot no projeto

```powershell
# Pelo terminal:
"C:\Godot\Godot_v4.7-stable_win64.exe" --path projetos\star-colony --editor

# Ou pelo atalho:
/godot
```

### 7. Testar

Com o servidor rodando e o Godot aberto, peça algo simples no chat do Copilot:

> "Liste as cenas do projeto"

Se o MCP responder com a lista de cenas (`main.tscn`, `main_menu.tscn`), a conexão
funcionou. Agora é só conversar.

---

## EM OUTRA MÁQUINA (computador novo)

1. Instale Python 3.12+, Godot 4.7, VS Code + Copilot + DeepSeek
2. Clone o repositório nucleo do GitHub
3. Execute os passos 1 a 7 acima
4. Ajuste `config.json` com os caminhos DAQUELA máquina

**O que NÃO precisa refazer:**
- O código do servidor (`server.py`, `tools/`) já vem no repositório
- Os addons (`game_bridge/`, `mcp_bridge/`) já estão no Star Colony
- Os templates e classdb_cache já estão no repositório

**O que SEMPRE precisa refazer:**
- Criar `.venv` e instalar dependências (passo 1)
- Ajustar `config.json` com os caminhos da máquina (passo 2)

---

## SOLUÇÃO DE PROBLEMAS

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError: No module named 'mcp'` | .venv não foi criado ou ativado | Refazer passo 1 |
| `Connection refused` | Servidor não está rodando | Rodar passo 5 |
| Godot não abre | Caminho errado no config.json | Verificar passo 2 |
| `TabError: inconsistent tabs` | Arquivo .py com tabs | `python -m tabnanny server.py` |
| Addon não carrega | plugin.cfg faltando | Verificar passo 3 |
| Porta 9080 já em uso | Outro servidor rodando | `netstat -ano \| findstr 9080` e matar processo |

---

## RESUMO (colar no terminal, uma vez por máquina)

```powershell
# 1. .venv
cd sistema\mcp-godot\servidor
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. Iniciar (toda vez que for trabalhar)
.venv\Scripts\python server.py

# 3. Godot (em outro terminal, ou use /godot)
C:\Godot\Godot_v4.7-stable_win64.exe --path projetos\star-colony --editor
```

---

**Última atualização:** 2026-07-09 | **MCP versão:** 2.9 | **Godot:** 4.7 | **Python:** 3.12+
