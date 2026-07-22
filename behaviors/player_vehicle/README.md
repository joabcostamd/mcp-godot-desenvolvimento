# PlayerVehicle — Controle de Veículo

Node filho de CharacterBody2D. Movimento baseado em rotação com drift.
`ui_left`/`ui_right` gira, `ui_up` acelera, `ui_down` ré.

## Quick Start

```gdscript
var ship := CharacterBody2D.new()
var vehicle := PlayerVehicle.new()
vehicle.acceleration = 600.0
vehicle.max_speed = 500.0
vehicle.turn_rate = 4.0
vehicle.drift = 0.8
ship.add_child(vehicle)
add_child(ship)
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `acceleration` | float | 10–5000 | 500 | Impulso (px/s²) |
| `max_speed` | float | 10–3000 | 400 | Velocidade máxima (px/s) |
| `turn_rate` | float | 0.5–20 | 3.0 | Rotação (rad/s) |
| `drift` | float | 0–1 | 0.9 | Aderência lateral |

## Edge Cases

- **`drift = 0`:** derrapagem total (gelo/espaço)
- **`drift = 1`:** sem derrapagem (trilho)
- **Sem parent:** não processa, não crasha

## Fonte

Godot 4.7 ClassDB: `CharacterBody2D`, `move_and_slide()`, `Vector2.rotated()`, `Input.get_axis()`.
