# DoubleJump — Pulo Múltiplo

Node filho de CharacterBody2D. Permite `jump_count` pulos no ar.
Coyote time dá margem após sair do chão. Complementar ao PlayerController.

## Quick Start

```gdscript
var controller := PlayerController.new()
controller.jump_velocity = -450.0
add_child(controller)

var dj := DoubleJump.new()
dj.jump_count = 2        # pulo duplo
dj.jump_velocity = -450.0  # mesma força
dj.coyote_time = 0.08
add_child(dj)
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `jump_count` | int | 1–10 | 2 | Pulos totais (2 = duplo) |
| `jump_velocity` | float | -2000 – -50 | -400 | Força do pulo |
| `coyote_time` | float | 0–0.5 | 0.1 | Margem após sair do chão |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `jumped` | `jumps_used: int` | A cada pulo no ar |
| `jumps_exhausted` | — | Último pulo usado |

## Edge Cases

- **No chão:** PlayerController cuida do 1º pulo; DoubleJump não interfere
- **Coyote time:** `_air_time <= coyote_time` + `_jumps_used == 0` → ainda pode pular
- **`jump_count = 1`:** comporta como sem pulo extra (só coyote time)
- **`reset_jumps()`:** zera contador (ex: ao tomar dano)

## Fonte

Godot 4.7 ClassDB: `CharacterBody2D.is_on_floor()`, `Input.is_action_just_pressed()`.
