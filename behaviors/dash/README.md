# Dash — Impulso Rápido

Node filho de CharacterBody2D. Ao pressionar `ui_accept`, aplica velocidade
na direção do input por `dash_duration` segundos. Cooldown evita spam.

## Quick Start

```gdscript
# Junto com PlayerController:
var controller := PlayerController.new()
add_child(controller)
var dash := Dash.new()
dash.dash_speed = 1000.0
dash.cooldown = 0.3
add_child(dash)
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `dash_speed` | float | 100–5000 | 800 | Velocidade do dash (px/s) |
| `dash_duration` | float | 0.05–1 | 0.15 | Duração (s) |
| `cooldown` | float | 0–10 | 0.5 | Recarga (s) |

## Sinais

| Nome | Quando |
|------|--------|
| `dashed` | Dash iniciado |
| `dash_ready` | Cooldown terminou, dash disponível |

## Edge Cases

- **Direção:** input atual; se nenhum, última direção; fallback = RIGHT
- **Durante o dash:** `_physics_process` mantém velocidade fixa
- **Cooldown = 0:** dash pode ser reusado imediatamente após `dash_duration`
- **`cancel_dash()`:** interrompe o dash (ex: ao tomar dano)

## Fonte

Godot 4.7 ClassDB: `Timer`, `Input.get_vector()`, `CharacterBody2D.velocity`.
