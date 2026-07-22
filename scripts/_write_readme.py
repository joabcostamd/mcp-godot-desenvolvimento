#!/usr/bin/env python3
"""Escreve o README.md completo com dados atuais."""

README = r"""# MCP Godot Agent v3.2.1

> **Da ideia ao lancamento. Sem pular etapas.**
> Servidor MCP dono do processo inteiro de fazer um jogo em Godot 4.7.
> 249 behaviors · Editor Visual de BT · 4 jogos-exemplo · 285+ tools.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Godot](https://img.shields.io/badge/Godot-4.7-blue)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![ONDA 2](https://img.shields.io/badge/ONDA%202-84%25-yellow)
![Qualidade](https://img.shields.io/badge/Qualidade-7%2F7-brightgreen)
![Atualizado](https://img.shields.io/badge/atualizado-2026--07--22-lightgrey)

**Repo:** https://github.com/joabcostamd/mcp-godot-agent
**Versao:** 3.2.1 | **Tools:** 285+ | **Behaviors:** 249 | **Jogos:** 4 | **Templates:** 5

---

## O que e

O **MCP Godot Agent** conecta o editor Godot 4.7 a uma IA via protocolo MCP.
Voce descreve o jogo em portugues, e o sistema cria tudo: projeto, cenas,
behaviors, assets, exportacao - com **travas reais** que impedem pular etapa.

**Nao-programadores** montam comportamentos arrastando caixinhas no
**Editor Visual de Behavior Trees**. Desenvolvedores usam as **285+ tools**
diretamente via MCP.

---

## Quick Start

```powershell
git clone https://github.com/joabcostamd/mcp-godot-agent
cd mcp-godot-agent
python install.py
```

No Godot: ative os plugins `MCP Addon` + `MCP Dock` + `MCP BT Editor`.
Aponte seu cliente MCP para `http://127.0.0.1:9082`.

```
Usuario: "Crie um jogo de plataforma com pulo duplo e inimigos."
MCP: IDEIA -> DESIGN -> PROTOTIPO -> CONTEUDO -> POLIMENTO -> PRONTO
```

---

## Numeros

| Metrica | Valor |
|---------|-------|
| **Tools MCP** | 285+ |
| **Behaviors** | 249 (Score 7/7) |
| **Jogos-Exemplo** | 4 (platformer, rpg, puzzle, shooter) |
| **Templates** | 5 (shooter, idle, visual novel, roguelike, tower defense) |
| **Seeds** | 4 (breakout, platformer, topdown_rpg, survivors_like) |
| **Blueprints** | 3 |
| **Addons Godot** | 5 |
| **Modulos Python** | 136 em tools/ |
| **Fases** | 6 (IDEIA -> PRONTO_PARA_LANCAR) |

---

## Editor Visual de Behavior Trees (NOVO)

Editor 100% GDScript integrado ao Godot. **16 features:**

- Paleta com 249 behaviors (busca + categorias)
- 4 tipos de portas coloridas (FLOW, CONDITION, DATA, EVENT)
- Validacao de conexoes + deteccao de ciclos (DAG)
- Reroute nodes · Expression nodes · Auto-Arrange
- Salvar/Carregar .tres · Exportar GDScript
- Undo/Redo · Debugger ao vivo (breakpoints, watch window)
- GraphFrame · Minimap

> Abra em: Project > MCP BT Editor

---

## Jogos-Exemplo

| Jogo | Genero | Behaviors | Cenas |
|------|--------|-----------|-------|
| Platformer | Plataforma 2D | 15 | 4 |
| RPG | Top-Down Action | 20 | 5 |
| Puzzle | Grid Sokoban | 10 | 3 |
| Shooter | Survivors-like | 14 | 4 |

> Abra example_project/<genero>/ no Godot e pressione F5.

---

## Estrutura

```
mcp-godot-agent/
  server.py              # Servidor MCP (285+ tools)
  tools/                 # 136 modulos Python
  behaviors/             # 249 behaviors (Score 7/7)
  addons/                # 5 plugins Godot
  example_project/       # 4 jogos completos
  templates/             # 5 templates de genero
  seeds/                 # 4 sementes
  blueprints/            # 3 blueprints
  docs/                  # Documentacao
  scripts/               # 9 scripts de manutencao
```

---

## Documentacao

| Documento | Conteudo |
|-----------|----------|
| [docs/getting-started.md](docs/getting-started.md) | Guia de inicio rapido |
| [docs/arquitetura.md](docs/arquitetura.md) | Arquitetura interna |
| [docs/tools.md](docs/tools.md) | Catalogo de 285+ tools |
| [docs/guia-migracao.md](docs/guia-migracao.md) | Migrando de outras ferramentas |
| [docs/modo-professor.md](docs/modo-professor.md) | Explicacoes didaticas |
| [ROADMAP_DEFINITIVO.md](ROADMAP_DEFINITIVO.md) | Roadmap completo (5 ondas) |
| [behaviors/CATALOGO_COMPLETO.md](behaviors/CATALOGO_COMPLETO.md) | 249 behaviors |

---

## Instalacao

```powershell
git clone https://github.com/joabcostamd/mcp-godot-agent
cd mcp-godot-agent
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
python install.py
```

**Requisitos:** Python 3.11+ · Godot 4.7 · VS Code + Copilot (ou cliente MCP)

---

## Progresso das Ondas

| Onda | Progresso |
|------|-----------|
| ONDA 0 — Destravar | 100% |
| ONDA 1 — Acessibilidade | 100% |
| ONDA 2 — O Fosso | 84% |
| ONDA 3 — Qualidade | 91% |
| ONDA 4 — Mundo | 86% (preparado, nao publicado) |

---

**Licenca:** MIT · **Autor:** Joab Costa · **Versao:** 3.2.1 · **Atualizado:** 2026-07-22
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(README)

print("README.md escrito com sucesso.")
