# 🎮 MCP Godot Agent

> **Seu assistente de IA que cria jogos completos no Godot — da ideia ao lançamento.**
> Conecte o Godot Engine 4.7 ao VS Code Copilot e comece a criar em minutos.

<!-- BADGES_START -->
![Status](https://img.shields.io/badge/status-active-brightgreen)
![Godot](https://img.shields.io/badge/Godot-4.7-blue)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![MCP](https://img.shields.io/badge/MCP-2025--11--25-orange)
<!-- BADGES_END -->

> 📊 **Versão:** <!--DOCS_SYNC:version-->3.7.0<!--/DOCS_SYNC:version--> | **Tools:** <!--DOCS_SYNC:tools-->287<!--/DOCS_SYNC:tools--> | **Rollups:** <!--DOCS_SYNC:rollups-->32<!--/DOCS_SYNC:rollups-->
> ⚠️ Números gerados por `scripts/docs_sync.py` — não edite manualmente.

---

## O que é

O **MCP Godot Agent** é um servidor MCP em Python que atua como **dono do processo** de desenvolvimento de um jogo Godot inteiro. Não é só uma ponte entre IA e engine — ele tem travas reais que impedem pular etapas, verificação automatizada e um guia passo a passo.

**Para quem é:** Pessoas que querem criar um jogo mas não sabem programar. Você descreve o que quer em linguagem natural e a IA constrói.

**O que ele faz:**
- Cria projetos Godot completos a partir de uma frase
- Gerencia 6 fases de desenvolvimento (Ideia → Design → Protótipo → Conteúdo → Polimento → Pronto)
- Oferece 32 gêneros de jogos prontos para começar
- Verifica cada etapa automaticamente (compilação, testes, smoke test)
- Funciona offline para operações que não dependem de IA

---

## ⚡ Comece em 1 minuto

```powershell
# 1. Instale (só Python 3.11+ necessário, sem dependências)
python init.py

# 2. Abra o VS Code na pasta do projeto

# 3. No chat do Copilot, digite:
/plan
```

**Comandos disponíveis após instalação:**

| Comando | O que faz |
|---|---|
| `/plan` | Planeja a próxima etapa do seu jogo |
| `/act` | Executa o plano aprovado |
| `/handoff` | Salva o progresso da sessão |
| `/manual` | Manual completo de comandos |

**Alternativa sem instalador:**
```powershell
git clone https://github.com/joabcostamd/mcp-godot-desenvolvimento
cd mcp-godot-desenvolvimento
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python server.py --profile dev
```

---

## 🎮 Vitrine de Gêneros (32 gêneros)

Escolha um gênero e comece a criar. Use `quickstart_manage(op="showcase")` para ver a lista completa.

### ⭐ Fácil

| Gênero | Experimente: |
|---|---|
| 🐍 Snake | "jogo da cobrinha, controle a cobra no grid" |
| 🐦 Flappy Bird | "jogo do passarinho que voa entre canos" |
| 🏓 Pong | "jogo de ping-pong com dois paddles e uma bola" |
| 📈 Doodle Jump | "jogo de pular de plataforma em plataforma subindo" |
| 🧠 Memória | "jogo da memória, vire as cartas e encontre os pares" |
| 🧱 Breakout | "jogo de quebrar tijolos com bola e paddle" |
| 🖱️ Idle Clicker | "jogo de clique incremental, automatize" |
| 🌌 Asteroids | "jogo de nave no espaço, gire e atire" |
| 💣 Campo Minado | "jogo de campo minado, deduza onde estão as minas" |

### ⭐⭐ Médio

| Gênero | Experimente: |
|---|---|
| 👾 Space Invaders | "jogo de nave que atira em aliens" |
| 🏃 Endless Runner | "jogo de corrida infinita, desvie dos obstáculos" |
| 🫧 Bubble Shooter | "jogo de atirar bolhas coloridas, forme grupos" |
| 🐸 Frogger | "jogo do sapo, atravesse a rua e o rio" |
| 🎯 Top-Down Shooter | "jogo de nave que atira em asteroides" |
| 🔫 Twin-Stick | "jogo de arena, mova e atire contra waves" |
| 🧊 Tetris | "jogo de encaixar peças que caem" |
| 📦 Sokoban | "jogo de empurrar caixas no grid" |
| 🎮 Plataforma | "jogo de plataforma com pulo e coleta de moedas" |
| 🕹️ Pac-Man | "jogo de labirinto, colete pontos e fuja dos fantasmas" |
| 🧩 Match-3 | "jogo de combinar 3 peças coloridas no grid" |
| 🏎️ Corrida | "jogo de corrida visto de cima" |
| 🧲 Puzzle Física | "jogo de puzzle com física realista" |

### ⭐⭐⭐ Avançado

| Gênero | Experimente: |
|---|---|
| 🏰 Tower Defense | "jogo de defesa de torre, posicione torres" |
| 🧛 Vampire Survivors | "jogo de sobrevivência com ataque automático" |
| ⚔️ RPG Turno | "RPG de turno, explore o mapa e lute" |
| 🗡️ Dungeon Crawler | "dungeon procedural, explore salas aleatórias" |
| 🃏 Deck Builder | "jogo de cartas estratégico, monte seu deck" |
| 🗺️ Metroidvania | "exploração com plataforma e habilidades" |
| 📖 Visual Novel | "história interativa com diálogos" |
| 💥 Bullet Hell | "jogo de esquiva com dezenas de projéteis" |
| 👊 Beat 'em Up | "jogo de luta de rua, derrote ondas de inimigos" |
| 🥷 Stealth 2D | "jogo de furtividade, evite guardas nas sombras" |

---

## 📂 Estrutura

| Pasta/Arquivo | O que é |
|---|---|
| `server.py` | Servidor MCP principal (279 ferramentas, stdio JSON-RPC 2.0) |
| `init.py` | Instalador de 1 comando (só stdlib, zero dependências) |
| `tools/` | 115+ módulos Python (cenas, scripts, física, arte, som, pipeline) |
| `resources/` | 32 padrões de gêneros + 11 prompts MCP |
| `addons/` | Plugins Godot (bridge, dock, runtime) |
| `llms.txt` | Índice completo do projeto para IAs (padrão llmstxt.org) |
| `README.en.md` | English version of this document |

---

## 📖 Documentação

| Documento | Conteúdo |
|---|---|
| [ROADMAP_DEFINITIVO.md](ROADMAP_DEFINITIVO.md) | Ordem canônica de desenvolvimento (5 ondas, 80+ fatias) |
| [AGENTS.md](AGENTS.md) | Regras para agentes de IA no repositório |
| [docs/manual/](docs/manual/) | Manual do usuário (10 seções, gerado por código) |
| [docs/tutorial/](docs/tutorial/) | Tutoriais progressivos (01 a 04) |
| [CHANGELOG.md](CHANGELOG.md) | Histórico completo de versões |

---

## 🔧 Requisitos

- Python 3.11+
- Godot 4.7
- VS Code + Copilot (ou qualquer cliente MCP)

---

**English:** [README.en.md](README.en.md) | **llms.txt:** [llms.txt](llms.txt) | **GitHub:** [joabcostamd/mcp-godot-desenvolvimento](https://github.com/joabcostamd/mcp-godot-desenvolvimento)
