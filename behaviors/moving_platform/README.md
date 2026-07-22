# MovingPlatform — Plataforma Móvel

`AnimatableBody2D` que segue um `Path2D` filho. Sincroniza movimento com física
para que o jogador em cima não escorregue.

## Quick Start

```gdscript
# Crie um Path2D filho com pelo menos 2 pontos
var platform := MovingPlatform.new()
platform.speed = 150.0
platform.loop = true

var path := Path2D.new()
var curve := Curve2D.new()
curve.add_point(Vector2(0, 0))
curve.add_point(Vector2(300, 0))
path.curve = curve
platform.add_child(path)

add_child(platform)
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `speed` | float | 10–2000 | 100 | Velocidade (px/s) |
| `loop` | bool | — | `true` | Reinicia ao chegar ao fim |
| `pause_at_ends` | float | 0–10 | 0 | Pausa nas pontas (s) |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `waypoint_reached` | `index: int` | Chegou em ponta (0=início, 1=fim) |
| `loop_completed` | — | Completou volta (só com loop) |

## Edge Cases

- **Sem Path2D filho:** não move, não crasha
- **Curva com 1 ponto:** não move
- **`loop = false`:** vai e volta (ping-pong)
- **`pause_at_ends > 0`:** pausa antes de inverter/dar volta

## Fonte

Godot 4.7 ClassDB: `AnimatableBody2D`, `Path2D`, `Curve2D.sample_baked()`.
