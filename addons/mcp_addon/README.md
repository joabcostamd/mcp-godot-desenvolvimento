# MCP Godot Agent — Faça jogos em Godot com linguagem natural

> **🇧🇷 Portugues abaixo | 🇺🇸 English below**

---

## 🇧🇷 Portugues

### O que e

O **MCP Godot Agent** e um addon que transforma o Godot 4.7 em uma engine de
desenvolvimento assistido por IA. Ele conecta o editor Godot a um servidor MCP
(Model Context Protocol) em Python, permitindo que voce crie jogos inteiros
usando linguagem natural — sem escrever uma linha de codigo.

**249 componentes plugaveis** (behaviors) cobrem movimento, combate, IA, UI,
audio, saves, multiplayer, acessibilidade e muito mais. O sistema tem **travas
reais** que impedem pular etapas do desenvolvimento, garantindo que seu jogo
avance com qualidade do inicio ao fim.

### Funcionalidades principais

- 🧩 **249 behaviors** — componentes prontos para usar (vida, dash, patrulha, crafting, dialogos, conquistas...)
- 🎨 **Editor Visual de Behavior Trees** — monte comportamentos arrastando caixinhas e conectando portas coloridas
- 🐛 **Debugger ao vivo** — breakpoints visuais, watch window, destaque de nos ativos
- 🔗 **WebSocket bridge** — comunicacao em tempo real entre o editor Godot e o servidor Python
- 📋 **Exportacao automatica** — gere GDScript executavel a partir do editor visual
- ✅ **Validacao integrada** — cada behavior tem testes GdUnit4, `.tres` com parametros e documentacao
- 🌍 **Suporte PT/EN** — todas as descricoes e buscas funcionam nos dois idiomas

### Instalacao

1. **Instale o servidor Python:**
   ```bash
   git clone https://github.com/joabcostamd/mcp-godot-agent
   cd mcp-godot-agent
   python install.py
   ```

2. **No Godot:**
   - Copie a pasta `addons/` para o diretorio `addons/` do seu projeto
   - Ative os plugins: `Project > Project Settings > Plugins`
     - ✅ MCP Addon (obrigatorio)
     - ✅ MCP Dock (painel visual)
     - ✅ MCP BT Editor (editor visual de behaviors)
   - O dock MCP aparece no canto inferior direito

3. **Configure seu cliente de IA:**
   - Aponte para o servidor MCP em `http://127.0.0.1:9082`
   - Comece com: "Crie um jogo de plataforma com pulo duplo e inimigos que patrulham"

### Requisitos

- **Godot 4.7+** (Windows, Linux ou Mac)
- **Python 3.10+** com `pip`
- **Cliente MCP** — GitHub Copilot no VS Code (recomendado) ou qualquer cliente compativel com MCP

### Exemplo rapido

```
Usuario: "Quero um jogo de navinha. Tiro, power-up, chefao a cada 5 ondas."

MCP Godot Agent:
1. Cria projeto com template top-down shooter
2. Adiciona behaviors: player_ship, enemy_spawner, bullet, powerup, boss, wave_manager
3. Configura parametros: 3 vidas, 5 power-ups, chefao na onda 5
4. Gera cenas: game.tscn, menu.tscn, game_over.tscn
5. Exporta e testa — jogavel em 10 minutos
```

### Screenshots

> ⚠️ *Para gerar screenshots: abra o projeto example_project/ no Godot, pressione F5,
> e capture as telas. Coloque os arquivos .png em `addons/mcp_addon/screenshots/`.*

| Screenshot | Descricao |
|---|---|
| `screenshot_01.png` | Dock MCP no editor — progresso, diagnosticos e botoes |
| `screenshot_02.png` | Editor Visual de Behavior Trees — paleta + grafo + inspetor |
| `screenshot_03.png` | Debugger ao vivo — breakpoints e watch window |
| `screenshot_04.png` | Jogo exemplo rodando (Breakout) |
| `screenshot_05.png` | Behaviors no Scene Tree — composicao de componentes |

### Documentacao completa

- 📖 [README.md](../README.md) — visao geral do projeto
- 🗺️ [ROADMAP_DEFINITIVO.md](../ROADMAP_DEFINITIVO.md) — planejamento completo
- 📋 [behaviors/CATALOGO_COMPLETO.md](../behaviors/CATALOGO_COMPLETO.md) — catalogo dos 249 behaviors

### Licenca

**MIT** — veja [LICENSE](LICENSE).

---

## 🇺🇸 English

### What is it

The **MCP Godot Agent** is an addon that turns Godot 4.7 into an AI-assisted
game development engine. It connects the Godot editor to a Python MCP
(Model Context Protocol) server, enabling you to create entire games using
natural language — without writing a single line of code.

**249 pluggable components** (behaviors) cover movement, combat, AI, UI,
audio, saves, multiplayer, accessibility, and more. The system has **real
gates** that prevent skipping development stages, ensuring your game
progresses with quality from start to finish.

### Key Features

- 🧩 **249 behaviors** — ready-to-use components (health, dash, patrol, crafting, dialogue, achievements...)
- 🎨 **Visual Behavior Tree Editor** — build behaviors by dragging boxes and connecting colored ports
- 🐛 **Live Debugger** — visual breakpoints, watch window, active node highlighting
- 🔗 **WebSocket bridge** — real-time communication between Godot editor and Python server
- 📋 **Automatic export** — generate executable GDScript from the visual editor
- ✅ **Built-in validation** — each behavior has GdUnit4 tests, `.tres` parameters, and documentation
- 🌍 **PT/EN support** — all descriptions and searches work in both languages

### Installation

1. **Install the Python server:**
   ```bash
   git clone https://github.com/joabcostamd/mcp-godot-agent
   cd mcp-godot-agent
   python install.py
   ```

2. **In Godot:**
   - Copy the `addons/` folder to your project's `addons/` directory
   - Enable plugins: `Project > Project Settings > Plugins`
     - ✅ MCP Addon (required)
     - ✅ MCP Dock (visual panel)
     - ✅ MCP BT Editor (visual behavior editor)
   - The MCP dock appears in the bottom-right corner

3. **Configure your AI client:**
   - Point to the MCP server at `http://127.0.0.1:9082`
   - Start with: "Create a platformer game with double jump and patrolling enemies"

### Requirements

- **Godot 4.7+** (Windows, Linux, or Mac)
- **Python 3.10+** with `pip`
- **MCP Client** — GitHub Copilot in VS Code (recommended) or any MCP-compatible client

### Quick Example

```
User: "I want a shoot-em-up. Bullets, power-ups, boss every 5 waves."

MCP Godot Agent:
1. Creates project from top-down shooter template
2. Adds behaviors: player_ship, enemy_spawner, bullet, powerup, boss, wave_manager
3. Configures parameters: 3 lives, 5 power-ups, boss at wave 5
4. Generates scenes: game.tscn, menu.tscn, game_over.tscn
5. Exports and tests — playable in 10 minutes
```

### Screenshots

> ⚠️ *To generate screenshots: open example_project/ in Godot, press F5,
> and capture the screens. Place the .png files in `addons/mcp_addon/screenshots/`.*

| Screenshot | Description |
|---|---|
| `screenshot_01.png` | MCP Dock in the editor — progress, diagnostics and buttons |
| `screenshot_02.png` | Visual Behavior Tree Editor — palette + graph + inspector |
| `screenshot_03.png` | Live Debugger — breakpoints and watch window |
| `screenshot_04.png` | Example game running (Breakout) |
| `screenshot_05.png` | Behaviors in Scene Tree — component composition |

### Full Documentation

- 📖 [README.md](../README.md) — project overview
- 🗺️ [ROADMAP_DEFINITIVO.md](../ROADMAP_DEFINITIVO.md) — full roadmap
- 📋 [behaviors/CATALOGO_COMPLETO.md](../behaviors/CATALOGO_COMPLETO.md) — 249 behaviors catalog

### License

**MIT** — see [LICENSE](LICENSE).
