# PlayerTopDown — Controle Top-Down

Node filho de `CharacterBody2D` que lê input do `InputMap` (ui_up/down/left/right) e
aplica velocidade com aceleração e fricção configuráveis. O pai deve chamar
`move_and_slide()` no próprio `_physics_process`.

## Quick Start

```gdscript
# No _ready() do seu CharacterBody2D:
var movement := PlayerTopDown.new()
movement.speed = 250.0
add_child(movement)
```

No `_physics_process` do pai:
```gdscript
move_and_slide()
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `speed` | float | 10–2000 | 200 | Velocidade máxima (px/s) |
| `acceleration` | float | 10–10000 | 1000 | Taxa de aceleração (px/s²) |
| `friction` | float | 10–10000 | 1000 | Taxa de desaceleração sem input (px/s²) |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `velocity_changed` | `velocity: Vector2` | A cada frame com a velocidade atual |

## Edge Cases

- **Sem parent CharacterBody2D:** não crasha, apenas não aplica velocidade
- **Input diagonal:** normalizado — não anda mais rápido na diagonal
- **`enabled = false`:** não processa input nem move
- **`reset()`:** zera velocidade e `parent.velocity` imediatamente

## Fonte

Godot 4.7 ClassDB: `CharacterBody2D`, `Input.is_action_pressed()`, `Vector2.move_toward()`, `Vector2.limit_length()`.
