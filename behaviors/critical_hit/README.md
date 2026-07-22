# CriticalHit — Chance de Crítico

**PT:** Node que aplica chance de crítico. `try_critical(damage)` retorna o dano com ou sem multiplicador. Compatível com `health.take_damage(amount, multiplier)`.

**EN:** Node that applies critical hit chance. `try_critical(damage)` returns damage with or without multiplier. Compatible with `health.take_damage(amount, multiplier)`.

## Uso Rápido

```gdscript
var crit := CriticalHit.new()
crit.crit_chance = 0.15    # 15%
crit.crit_multiplier = 2.5

# Com health:
var final_damage := crit.try_critical(base_damage)
health.take_damage(final_damage)

# Ou usando o multiplier do health diretamente:
if crit.roll():
    health.take_damage(base_damage, crit.crit_multiplier)
```
