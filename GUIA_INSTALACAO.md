# GUIA DE INSTALAÇÃO — MCP Godot Agent v3.0

> **Para a IA agêntica (DeepSeek, Claude, Copilot, etc.):**
> Siga cada passo na ordem. Não pule nada. Ao final, o MCP estará conectado
> ao VS Code e pronto para construir o Star Colony.

---

## PRÉ-REQUISITOS (verifique antes de começar)

| Item | Como verificar |
|---|---|
| Python 3.12+ | `python --version` |
| Git | `git --version` |
| Godot 4.7 | Verificar se Godot_v4.7-stable_win64.exe existe |
| VS Code com Copilot | Extensão GitHub Copilot instalada |
| Conta GitHub autenticada | `gh auth status` |

---

## PASSO 1 — Clonar o MCP fora do NUCLEO

O MCP é uma ferramenta independente — **NÃO** vai dentro da pasta `NUCLEO`.
O local ideal é ao lado dela, na mesma pasta `VS CODE`:

```powershell
cd "C:\Users\joabc\OneDrive\Documentos\VS CODE"
git clone https://github.com/joabcostamd/mcp-godot-desenvolvimento
```

Resultado esperado:
```
C:\Users\joabc\OneDrive\Documentos\VS CODE\
├── NUCLEO\                          ← o núcleo (projetos, sistema, etc.)
└── mcp-godot-desenvolvimento\       ← o MCP (NOVO, fora do núcleo)
    ├── server.py
    ├── tools/
    ├── config.json
    ├── requirements.txt
    └── ...
```

---

## PASSO 2 — Criar o ambiente virtual Python

```powershell
cd "C:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento"
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

Verifique:
```powershell
.venv\Scripts\python -c "import mcp; print('MCP OK')"
```

Deve imprimir: `MCP OK`

---

## PASSO 3 — Ajustar o config.json

```powershell
notepad config.json
```

Garanta que o conteúdo seja:

```json
{
  "godot_path": "C:\\Godot\\Godot_v4.7-stable_win64.exe",
  "godot_console_path": "C:\\Godot\\Godot_v4.7-stable_win64_console.exe",
  "python_path": "C:\\Users\\joabc\\AppData\\Local\\Programs\\Python\\Python314\\python.exe",
  "projects_root": "C:\\Users\\joabc\\OneDrive\\Documentos\\VS CODE\\NUCLEO\\projetos",
  "default_project": "C:\\Users\\joabc\\OneDrive\\Documentos\\VS CODE\\NUCLEO\\projetos\\star-colony",
  "addon_port": 9080,
  "game_port": 9081,
  "timeouts": { "fast": 15, "compile": 60, "export": 300 },
  "vibe_coding": { "enabled": true }
}
```

> Copie de `config.json.example` se precisar de um modelo limpo.

---

## PASSO 4 — Criar o mcp.json na raiz do NUCLEO

O VS Code lê o mcp.json da **raiz do workspace aberto**.
Como o workspace é a pasta `NUCLEO`, crie o arquivo lá:

```powershell
mkdir "C:\Users\joabc\OneDrive\Documentos\VS CODE\NUCLEO\.vscode" -Force
```

Conteúdo do arquivo mcp.json:

```json
{
  "servers": {
    "godot-mcp-agent": {
      "type": "stdio",
      "command": "C:\\Users\\joabc\\OneDrive\\Documentos\\VS CODE\\mcp-godot-desenvolvimento\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\joabc\\OneDrive\\Documentos\\VS CODE\\mcp-godot-desenvolvimento\\server.py"],
      "env": {
        "PYTHONPATH": "C:\\Users\\joabc\\OneDrive\\Documentos\\VS CODE\\mcp-godot-desenvolvimento"
      }
    }
  }
}
```

**Regras críticas deste arquivo:**
- Use `"servers"` (não `"mcpServers"`)
- Inclua `"type": "stdio"`
- Use caminhos **absolutos** (não relativos)
- Aponte para o `.venv` (não para o `python` do sistema)

---

## PASSO 5 — Ativar o autoStart no settings.json do VS Code

```powershell
notepad "$env:APPDATA\Code\User\settings.json"
```

Adicione (ou confirme que já existe):

```json
"chat.mcp.autoStart": true
```

Isso faz o VS Code iniciar o servidor MCP automaticamente ao abrir o workspace.

---

## PASSO 6 — Verificar os addons no Star Colony

O projeto Godot precisa dos addons do MCP:

```powershell
Test-Path "C:\Users\joabc\OneDrive\Documentos\VS CODE\NUCLEO\projetos\star-colony\addons\mcp_addon"
```

Deve retornar `True`. Se não existir, copie do repositório MCP:

```powershell
xcopy /E /I "C:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento\addons\mcp_addon" "C:\Users\joabc\OneDrive\Documentos\VS CODE\NUCLEO\projetos\star-colony\addons\mcp_addon"
```

Verifique também se o addon está ativado no `project.godot`:
```
[editor_plugins]
enabled=PackedStringArray("res://addons/mcp_addon/plugin.cfg")
```

---

## PASSO 7 — Recarregar o VS Code e testar

1. No VS Code: `Ctrl+Shift+P` → digite **"Reload Window"** → Enter
2. Aguarde 5 segundos para o servidor iniciar
3. Teste a conexão: peça no chat do Copilot:

> *"Liste as ferramentas disponíveis do MCP Godot"*

Ou chame uma ferramenta simples:

> *"Use a ferramenta `ping` do MCP do Godot"*

Se o servidor responder, a instalação está concluída.

---

## PASSO 8 — Teste com o Godot aberto

```powershell
& "C:\Godot\Godot_v4.7-stable_win64.exe" --path "C:\Users\joabc\OneDrive\Documentos\VS CODE\NUCLEO\projetos\star-colony" --editor
```

Com o Godot aberto e o servidor rodando, teste uma ferramenta que interage com o editor:

> *"Liste a árvore de cena atual do Star Colony"*

---

## SOLUÇÃO DE PROBLEMAS

| Sintoma | Causa | Solução |
|---|---|---|
| Ferramentas não aparecem no chat | mcp.json não foi lido | Recarregar janela (`Reload Window`) |
| `ModuleNotFoundError: No module named 'mcp'` | `.venv` não criado | Refazer Passo 2 |
| `Connection refused` | Servidor não iniciou | `chat.mcp.autoStart` deve estar `true` |
| Erro de caminho no config.json | Caminhos de outra máquina | Ajustar `godot_path`, `default_project` |
| Addons não carregam no Godot | `plugin.cfg` ausente | Refazer Passo 6 |

---

## RESUMO DOS CAMINHOS

| O quê | Onde |
|---|---|
| Repositório MCP | `C:\Users\joabc\OneDrive\Documentos\VS CODE\mcp-godot-desenvolvimento\` |
| Python do MCP | `...mcp-godot-desenvolvimento\.venv\Scripts\python.exe` |
| Servidor MCP | `...mcp-godot-desenvolvimento\server.py` |
| Projeto Star Colony | `C:\Users\joabc\OneDrive\Documentos\VS CODE\NUCLEO\projetos\star-colony\` |
| Godot 4.7 | `C:\Godot\Godot_v4.7-stable_win64.exe` |
| Config do MCP no VS Code | `NUCLEO\.vscode\mcp.json` |
| Settings do VS Code | `%APPDATA%\Code\User\settings.json` |
