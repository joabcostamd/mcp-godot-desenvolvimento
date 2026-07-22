# StatusEffect — Buff/Debuff

Node que aplica efeito temporário. DoT/HoT por tick, stacks, refresh.

## Quick Start

```gdscript
# Aplicar veneno que causa 5 de dano/s por 10s
var poison := StatusEffect.new()
poison.effect_type = "poison"
poison.duration = 10.0
poison.tick_interval = 1.0
poison.tick_damage = 5
entity.add_child(poison)
poison.apply()
```

## Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `effect_type` | String | — | `"custom"` | Tipo do efeito |
| `duration` | float | 0–300 | 5.0 | Duração (0=permanente) |
| `tick_interval` | float | 0–10 | 1.0 | Intervalo entre ticks |
| `tick_damage` | int | — | 0 | Dano/cura por tick |
| `max_stacks` | int | 1–99 | 1 | Stacks máximos |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `applied` | — | Efeito aplicado |
| `tick` | `stacks: int` | A cada tick |
| `expired` | — | Duração expirou |
| `refreshed` | — | Duração renovada |
| `removed` | — | Removido manualmente |

## Fonte

Godot 4.7 ClassDB: `Timer`, `Health.take_damage()`/`heal()`.
