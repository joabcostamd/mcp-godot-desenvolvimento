# MCP Example — Puzzle Grid

Puzzle estilo Sokoban construido com o **MCP Godot Agent**.
10 behaviors do arsenal de 249 componentes.

## Genero
Puzzle Grid-Based (Sokoban-like)

## Behaviors Usados (10)

| Behavior | Proposito |
|----------|-----------|
| `grid_movement` | Movimento discreto em grid |
| `pushable` | Blocos que podem ser empurrados |
| `target_zone` | Zona alvo onde blocos devem chegar |
| `victory_condition` | Todos os blocos nos alvos |
| `undo_move` | Desfazer ultimo movimento |
| `move_counter` | Contador de movimentos |
| `level_manager` | Carregar proximo nivel |
| `reset_button` | Reiniciar nivel atual |
| `screen_transition` | Fade entre niveis |
| `save_load` | Salvar progresso (nivel atual) |

## Controles

- **Setas** Mover
- **Z** Desfazer
- **R** Reiniciar nivel
- **ESC** Menu

## Niveis

1. Tutorial (4x4) — 1 bloco, 1 alvo
2. Basico (5x5) — 2 blocos, 2 alvos
3. Intermediario (6x6) — 3 blocos, 3 alvos

## Estrutura

```
example_project/puzzle/
  project.godot  seed.json  README.md
  scenes/        menu.tscn  level.tscn  victory.tscn
  scripts/       puzzle_main.gd
```

## Licenca

MIT
