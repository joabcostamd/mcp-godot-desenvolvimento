# GUIA DE CONEXAO — Godot 4.7 + MCP v3.5.0 (do zero)

> **Leia este arquivo primeiro.** Ele contém TUDO que você precisa para conectar o
> Godot 4.7 ao servidor MCP e começar a criar jogos por linguagem natural.
> Funciona em qualquer computador, mesmo sem contexto prévio do NUCLEO.

---

## ARQUITETURA (o que cada peça faz)

```
┌──────────────────────────────────────────────────────────────┐
│  SERVIDOR MCP (Python)                                       │
│  mcp-godot-desenvolvimento/server.py                         │
│  ├── tools/      ← 115 modulos, 240 ferramentas              │
│  ├── templates/  ← templates GDScript (Jinja2)              │
│  ├── resources/  ← game patterns (18 gêneros) + prompts     │
│  ├── classdb_cache/ ← API do Godot 4.7 (1074 classes)      │
│  └── config.json ← caminhos do Godot + projeto padrão       │
│                                                              │
│  Perfis: --profile core (31 tools) / dev (80) / full (240)  │
│  O servidor recebe comandos em linguagem natural,            │
│  traduz para operações no Godot, e aplica via TCP/WS.        │
└──────┬───────────┬──────────┬────────────┬──────────────────┘
       │ TCP :9080 │ WS :9082 │ TCP :9081  │ TCP :8790
       ▼           ▼          ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐
│  EDITOR  │ │  ADDON   │ │  GAME    │ │ RUNTIME BRIDGE   │
│  BRIDGE  │ │  DOCK    │ │  BRIDGE  │ │ (autoload)       │
│  TCP     │ │ WebSocket│ │  TCP     │ │ TCP :8790        │
│  :9080   │ │ :9082    │ │  :9081   │ │ só debug builds  │
│          │ │          │ │          │ │ screenshot, FPS, │
│  Comandos│ │ 3 tabs:  │ │ Estado   │ │ input injection  │
│  de      │ │ Status,  │ │ runtime  │ │ custom commands  │
│  edição  │ │ Log,     │ │ do jogo  │ │                  │
│          │ │ Tools    │ │          │ │                  │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘
     │            │            │                 │
     └────────────┴────────────┴─────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  PROJETO GODOT      │
              │  (shardbreaker-    │
              │   nodebuster-like  │
              │   ou qualquer outro)│
              └─────────────────────┘
```

## PRÉ-REQUISITOS (o que precisa existir na máquina)

| Item | Como verificar | Onde baixar |
|---|---|---|
| Python 3.12+ | `python --version` | python.org |
| Godot 4.7 | Abrir Godot → versão no canto | godotengine.org |
| VS Code + Copilot + DeepSeek | Extensões instaladas | marketplace |

---

## PASSO A PASSO — Primeira máquina

### 1. Clonar o repositório MCP

```powershell
cd "C:\Users\joabc\OneDrive\Documentos\VS CODE"
git clone https://github.com/joabcostamd/mcp-godot-desenvolvimento
```

O MCP é uma ferramenta **independente** — não vai dentro do NUCLEO. Fica ao lado:

```
C:\Users\joabc\OneDrive\Documentos\VS CODE\
├── NUCLEO\                          ← o núcleo (projetos, sistema, etc.)
└── mcp-godot-desenvolvimento\       ← o MCP (standalone)
    ├── server.py
    ├── tools/          (64 módulos)
    ├── resources/      (game patterns + prompts)
    ├── templates/      (5 templates GDScript)
    ├── classdb_cache/  (API Godot 4.7)
    ├── config.json
    ├── config.json.example
    └── requirements.txt
```

### 2. Criar o ambiente virtual (.venv + dependências)

```powershell
cd "C:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento"
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# Verificar
.venv\Scripts\python -c "import mcp; print('MCP OK:', mcp.__version__)"
```

**O que isso faz:** Cria um Python isolado com os pacotes `mcp`, `godot_parser`, `jinja2`, `pillow`.
Sem isso, o servidor não inicia.

### 3. Configurar o config.json

Abra `config.json` e ajuste **APENAS estes 3 campos**:

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

> **Override local (opcional):** Crie `config.local.json` (gitignorado) para sobrescrever
> campos sem alterar o `config.json` versionado. Também pode usar env vars `GODOT_MCP_*`.

### 4. Preparar o projeto Godot (instalar addons)

Dentro da pasta do SEU projeto Godot, você precisa das pastas de addons:

```
seu-projeto/
├── addons/
│   ├── mcp_addon/           ← WebSocket bridge + Dock UI (porta 9082)
│   └── mcp_runtime_bridge/  ← Runtime bridge (porta 8790, só debug)
├── project.godot
```

Os addons **já existem** no repositório MCP. Para copiá-los para o projeto:

```powershell
# Copiar addons do repositório MCP para o projeto Godot
xcopy /E /I "C:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento\addons\mcp_addon" "SEU-PROJETO\addons\mcp_addon"
xcopy /E /I "C:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento\addons\mcp_runtime_bridge" "SEU-PROJETO\addons\mcp_runtime_bridge"
```

**Ative os addons no Godot:** Abra o projeto → Project → Project Settings → Plugins → ative "MCP Addon".

### 5. Criar .vscode/mcp.json (VS Code)

Na raiz do workspace aberto no VS Code (ex: `NUCLEO/.vscode/mcp.json`):

```json
{
  "servers": {
    "godot-mcp-agent": {
      "type": "stdio",
      "command": "C:\\Users\\joabc\\OneDrive\\Documentos\\VS CODE\\mcp-godot-desenvolvimento\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\joabc\\OneDrive\\Documentos\\VS CODE\\mcp-godot-desenvolvimento\\server.py",
        "--profile", "dev"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\joabc\\OneDrive\\Documentos\\VS CODE\\mcp-godot-desenvolvimento"
      }
    }
  }
}
```

**Regras críticas:**
- Use `"servers"` (não `"mcpServers"`)
- Inclua `"type": "stdio"`
- Use caminhos **absolutos** (não relativos)
- Aponte para o `.venv` (não para o `python` do sistema)
- Use `"--profile", "dev"` para 31 tools (~5K tokens). Para todas as 189, use `"--profile", "full"` ou omita.

### 6. Ativar autoStart no VS Code

No `%APPDATA%\Code\User\settings.json`:

```json
"chat.mcp.autoStart": true
```

Isso faz o VS Code iniciar o servidor MCP automaticamente.

### 7. Iniciar e testar

1. No VS Code: `Ctrl+Shift+P` → **"Reload Window"** → Enter
2. Aguarde 5 segundos para o servidor iniciar
3. Teste no chat do Copilot:

> *"Use a ferramenta `ping` do MCP do Godot"*

Se responder com status `success`, a conexão funcionou.

### 8. Testar com Godot aberto

```powershell
& "C:\Godot\Godot_v4.7-stable_win64.exe" --path "SEU-PROJETO" --editor
```

Com o Godot aberto e o addon ativo, teste:

> *"Liste a árvore de cena atual do projeto"*

### 9. Testar runtime bridge (com jogo rodando)

```powershell
# No chat do Copilot, com o Godot aberto:
# > "Inicie o jogo e tire um screenshot"
```

O runtime bridge (porta 8790) só funciona com o jogo rodando em modo debug.
Use `godot_wait_for_bridge` antes de `godot_screenshot`.

---

## EM OUTRA MÁQUINA (computador novo)

1. Instale Python 3.12+, Godot 4.7, VS Code + Copilot + DeepSeek
2. Clone o repositório MCP do GitHub
3. Execute os passos 1 a 7 acima
4. Ajuste `config.json` com os caminhos **DAQUELA** máquina
5. Copie os addons para o projeto Godot (passo 4)

**O que NÃO precisa refazer:**
- O código do servidor (`server.py`, `tools/`) já vem no repositório
- Os addons (`mcp_addon/`, `mcp_runtime_bridge/`) já estão no repositório MCP
- Templates, classdb_cache, game patterns já estão no repositório

**O que SEMPRE precisa refazer:**
- Criar `.venv` e instalar dependências (passo 2)
- Ajustar `config.json` com os caminhos da máquina (passo 3)
- Criar `mcp.json` no workspace (passo 5)

---

## PORTAS (referência rápida)

| Porta | Protocolo | Propósito | Requer |
|-------|-----------|-----------|--------|
| **9080** | TCP | Editor Bridge — comandos de edição | Godot Editor aberto |
| **9081** | TCP | Game Bridge — estado do jogo | Jogo rodando |
| **9082** | WebSocket | Addon Dock — UI no Godot | Godot Editor + addon ativo |
| **8790** | TCP | Runtime Bridge — screenshot, FPS | Jogo rodando em debug |
| **6005** | TCP | LSP — referências, definição | Godot Editor aberto |

---

## PERFIS DE TOOLS

| Perfil | Tools | Tokens (~) | Quando usar |
|--------|-------|------------|-------------|
| `core` | 16 | ~2K | Bootstrap, health checks, operações básicas |
| `dev` | 31 | ~5K | Desenvolvimento diário (cenas, scripts, runtime) |
| `full` | 189 | ~18K | Acesso completo a todas as ferramentas |

Configure no `mcp.json`: `"args": ["...server.py", "--profile", "dev"]`
Ou via env var: `MCP_TOOL_PROFILE=dev`

---

## SOLUÇÃO DE PROBLEMAS

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError: No module named 'mcp'` | .venv não foi criado ou ativado | Refazer passo 2 |
| `Connection refused` | Servidor não está rodando | `chat.mcp.autoStart` deve estar `true` |
| Godot não abre | Caminho errado no config.json | Verificar passo 3 |
| `TabError: inconsistent tabs` | Arquivo .py com tabs | `python -m tabnanny server.py` |
| Addon não carrega | plugin.cfg faltando | Verificar passo 4 |
| Porta 9080/9082 já em uso | Outro servidor rodando | `netstat -ano \| findstr "908"` e matar processo |
| Addon WebSocket não conecta | Godot não está aberto | Abrir Godot + ativar addon nas Plugins |
| Runtime bridge não responde | Jogo não está rodando em debug | `godot_wait_for_bridge` antes de usar |
| TimeoutError no Windows | Porta fechada (≠ ConnectionRefused) | R16 do LEARNINGS.md — capturar OSError |
| Muitas tools consome tokens | Perfil full é o default | Usar `--profile dev` (31 tools) |

---

## RESUMO (colar no terminal, uma vez por máquina)

```powershell
# 1. Clone + .venv
cd "C:\Users\joabc\OneDrive\Documentos\VS CODE"
git clone https://github.com/joabcostamd/mcp-godot-desenvolvimento
cd mcp-godot-desenvolvimento
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. Copiar addons para o projeto Godot
xcopy /E /I "addons\mcp_addon" "..\NUCLEO\projetos\shardbreaker-nodebuster-like\addons\mcp_addon"
xcopy /E /I "addons\mcp_runtime_bridge" "..\NUCLEO\projetos\shardbreaker-nodebuster-like\addons\mcp_runtime_bridge"

# 3. Iniciar servidor (toda vez que for trabalhar)
.venv\Scripts\python server.py --profile dev

# 4. Godot (em outro terminal)
& "C:\Godot\Godot_v4.7-stable_win64.exe" --path "C:\Users\joabc\OneDrive\Documentos\VS CODE\NUCLEO\projetos\shardbreaker-nodebuster-like" --editor
```

---

**Última atualização:** 2026-07-12 | **MCP versão:** 3.2 | **Godot:** 4.7 | **Python:** 3.12+

