# Counter — Contador

Node com valor mínimo/máximo. `increment()`/`decrement()`/`add()` com clamp.

## Quick Start

```gdscript
var score := Counter.new()
score.max_value = 999
score.increment()
score.add(10)
print(score.get_value())  # 10
```

## Propriedades

| Nome | Tipo | Default | Descrição |
|------|------|---------|-----------|
| `initial_value` | int | 0 | Valor inicial |
| `min_value` | int | 0 | Valor mínimo |
| `max_value` | int | 0 | Máximo (0=sem limite) |
| `step` | int | 1 | Incremento/decremento |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `value_changed` | `new: int, old: int` | Valor alterado |
| `min_reached` | — | Atingiu mínimo |
| `max_reached` | — | Atingiu máximo |

## Fonte

Godot 4.7 ClassDB: `clampi()`.
