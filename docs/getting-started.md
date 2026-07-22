# Guia de Início Rápido — MCP Godot Agent

## O que é

O MCP Godot Agent conecta o editor Godot 4.7 a uma IA via protocolo MCP.
Você descreve o jogo em português, e o sistema cria tudo: projeto, cenas,
behaviors, assets, exportação — com travas reais que impedem pular etapas.

## Instalação (5 minutos)

### 1. Instalar o servidor Python
```bash
git clone https://github.com/joabcostamd/mcp-godot-agent
cd mcp-godot-agent
python install.py
```

### 2. Configurar no Godot
- Abra seu projeto Godot 4.7
- Copie `addons/` para `addons/` do seu projeto
- Ative os plugins: `Project > Project Settings > Plugins`
  - ✅ MCP Addon
  - ✅ MCP Dock
  - ✅ MCP BT Editor

### 3. Conectar a IA
- Aponte seu cliente MCP para `http://127.0.0.1:9082`
- Comece com: "Crie um jogo de plataforma com pulo duplo e inimigos"

## Primeiro Jogo

```
Usuário: "Quero um jogo de navinha. Tiro, power-up, chefão."

MCP:
1. IDEIA    → Define gênero, escopo, nome
2. DESIGN   → Cria project.godot, cenas vazias
3. PROTÓTIPO → Adiciona behaviors (player_ship, bullet, enemy_spawner)
4. CONTEÚDO → Cria fases, balanceia dificuldade
5. POLIMENTO → Ajusta game feel, sons, partículas
6. PRONTO   → Exporta para Windows/Linux/Web
```

## Estrutura do Projeto

```
mcp-godot-agent/
├── server.py              # Servidor MCP principal (275+ tools)
├── tools/                 # 135+ módulos Python
├── behaviors/             # 249 componentes plugáveis
├── addons/                # Plugins Godot (dock, BT editor, bridge)
├── example_project/       # 4 jogos-exemplo completos
├── templates/             # 5 templates de gênero
├── seeds/                 # 3 sementes de jogo
├── blueprints/            # 3 blueprints de gênero
└── docs/                  # Documentação
```

## Behaviors (249 componentes)

Cada behavior é um nó Godot plugável. Exemplos:
- `health` — Vida, dano, cura, morte
- `player_controller` — Movimento, pulo, gravidade
- `enemy_patrol` — Patrulha entre waypoints
- `inventory` — Mochila com itens
- `dialogue` — Sistema de diálogo com NPCs

## Jogos-Exemplo (4)

| Jogo | Gênero | Behaviors |
|------|--------|-----------|
| Platformer | Plataforma 2D | 15 |
| RPG | Top-Down Action | 20 |
| Puzzle | Grid Sokoban | 10 |
| Shooter | Survivors-like | 14 |

## Templates (5)

| Template | Dificuldade | Tempo |
|----------|------------|-------|
| Top-Down Shooter | Média | 2-4h |
| Idle Clicker | Fácil | 1-2h |
| Visual Novel | Fácil | 3-6h |
| Roguelike | Difícil | 6-12h |
| Tower Defense | Média | 4-8h |

## Próximos Passos

- Leia `docs/arquitetura.md` para entender o sistema
- Explore `behaviors/CATALOGO_COMPLETO.md` para ver todos os behaviors
- Veja `ROADMAP_DEFINITIVO.md` para o planejamento completo
