# GridMovement — Movimento em Grid

Node filho de Node2D. Movimento discreto em passos de `grid_size` pixels
com animação Tween. Bloqueia input durante movimento.

## Quick Start

```gdscript
var player := CharacterBody2D.new()
var grid := GridMovement.new()
grid.grid_size = Vector2(48, 48)
grid.move_duration = 0.1
player.add_child(grid)
add_child(player)
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `grid_size` | Vector2 | min 4,4 | (32,32) | Tamanho da célula (px) |
| `move_duration` | float | 0.01–1 | 0.15 | Duração da animação (s) |
| `snap_on_start` | bool | — | `true` | Ajusta posição inicial ao grid |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `moved` | `direction: Vector2` | Início do movimento |
| `arrived` | `grid_pos: Vector2` | Chegada na célula |

## Edge Cases

- **Durante movimento:** input bloqueado (`_moving = true`)
- **`snap_on_start`:** `_ready()` ajusta posição para grid mais próximo
- **`move_to_grid(x, y)`:** movimento forçado para coordenadas de grid

## Fonte

Godot 4.7 ClassDB: `Tween.tween_property()`, `Input.is_action_just_pressed()`.
