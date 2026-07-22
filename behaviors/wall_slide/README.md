# WallSlide — Deslize em Parede

Node filho de CharacterBody2D. Detecta paredes com RayCast2D e reduz
velocidade de queda. Wall jump impulsiona para longe da parede.

## Quick Start

```gdscript
var controller := PlayerController.new()
add_child(controller)
var wall := WallSlide.new()
wall.slide_speed = 80.0
wall.wall_jump_horizontal = 350.0
add_child(wall)
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `slide_speed` | float | 10–500 | 60 | Velocidade máx de descida (px/s) |
| `wall_jump_horizontal` | float | 50–1000 | 300 | Força horizontal do wall jump |
| `wall_jump_vertical` | float | -2000 – -50 | -350 | Força vertical do wall jump |
| `wall_detection_distance` | float | 4–64 | 16 | Distância de detecção (px) |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `wall_sliding` | `is_sliding: bool` | Estado de deslize muda |
| `wall_jumped` | `direction: Vector2` | Wall jump executado |

## Edge Cases

- **No chão:** não processa — `is_on_floor()` desliga o slide
- **Entre duas paredes:** não desliza (sem direção definida)
- **`enabled = false`:** não processa, RayCast2D não atualiza
- **Sem parent CharacterBody2D:** não crasha, retorna cedo

## Fonte

Godot 4.7 ClassDB: `RayCast2D`, `CharacterBody2D.is_on_floor()`, `force_raycast_update()`.
