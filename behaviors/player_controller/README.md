# PlayerController — Controle de Plataforma

Node filho de `CharacterBody2D`. Movimento horizontal com aceleração/fricção,
pulo com gravidade e `is_on_floor()`. Chama `move_and_slide()` automaticamente.

## Quick Start

```gdscript
# No _ready() do seu CharacterBody2D:
var controller := PlayerController.new()
controller.speed = 350.0
controller.jump_velocity = -450.0
add_child(controller)
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `speed` | float | 10–2000 | 300 | Velocidade horizontal máx (px/s) |
| `jump_velocity` | float | -2000 – -50 | -400 | Força do pulo (negativa) |
| `gravity` | float | 100–5000 | 980 | Gravidade (px/s²) |
| `acceleration` | float | 10–10000 | 1000 | Aceleração horizontal |
| `friction` | float | 10–10000 | 1000 | Fricção sem input |
| `kill_plane_y` | float | — | 0 | Y abaixo do qual morre |

## Sinais

| Nome | Quando |
|------|--------|
| `jumped` | Pulo executado |
| `player_died` | Caiu abaixo de `kill_plane_y` |

## Edge Cases

- **Sem parent CharacterBody2D:** não processa, não crasha
- **kill_plane_y = 0:** kill plane desativado
- **Input:** `ui_left`/`ui_right` para horizontal, `ui_accept` para pulo

## Fonte

Godot 4.7 ClassDB: `CharacterBody2D`, `move_and_slide()`, `is_on_floor()`, `Input.get_axis()`.
