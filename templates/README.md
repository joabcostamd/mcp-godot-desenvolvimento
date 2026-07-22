# Templates de Projeto — MCP Godot Agent

Scaffolds prontos para iniciar projetos de diferentes generos.
Cada template define: core loop, cenas, behaviors recomendados, viewport e dificuldade.

## Templates Disponiveis (5)

| # | Template | Genero | Behaviors | Dificuldade | Tempo Estimado |
|---|----------|--------|-----------|-------------|----------------|
| 1 | `topdown_shooter` | Tiro Top-Down | 12 | Media | 2-4h |
| 2 | `idle_clicker` | Idle/Clicker | 10 | Facil | 1-2h |
| 3 | `visual_novel` | Visual Novel | 12 | Facil | 3-6h |
| 4 | `roguelike` | Roguelike | 15 | Dificil | 6-12h |
| 5 | `tower_defense` | Tower Defense | 13 | Media | 4-8h |

## Formato

Cada `template.json` contem:
- `name`, `display_name_pt/en` — Nome e descricao bilingue
- `genre` — Genero do jogo
- `core_loop` — Loop principal de gameplay
- `scene_structure` — Cenas necessarias e seu conteudo
- `recommended_behaviors` — Behaviors do arsenal (249 disponiveis)
- `viewport` — Resolucao base recomendada
- `difficulty` — Dificuldade de implementacao (easy/medium/hard)
- `estimated_dev_time` — Tempo estimado com MCP

## Uso

No prompt do MCP:
> "Crie um jogo tower defense usando o template tower_defense"

Ou via tool:
> `create_project_from_template("tower_defense")`

## + 4 Jogos-Exemplo Completos

Alem dos templates, existem 4 jogos completos em `example_project/`:
- `platformer/` — Plataforma 2D (15 behaviors)
- `rpg/` — RPG Top-Down (20 behaviors)
- `puzzle/` — Puzzle Grid (10 behaviors)
- `shooter/` — Survivors-like (14 behaviors)
