# DamageOverTime — Dano Contínuo

**PT:** Node que aplica dano periódico (DOT) a um `Health` alvo. `start(health)` inicia, `stop()` interrompe. Sinais `dot_tick` e `dot_ended`.

**EN:** Node that applies periodic damage (DOT) to a target `Health`. `start(health)` begins, `stop()` interrupts. Signals `dot_tick` and `dot_ended`.

## Uso Rápido

```gdscript
var dot := DamageOverTime.new()
dot.damage_per_tick = 8
dot.tick_interval = 0.5
dot.duration = 4.0
dot.dot_ended.connect(_on_dot_finished)
add_child(dot)

# Aplicar a um inimigo:
dot.start(enemy.get_node("Health"))
```
