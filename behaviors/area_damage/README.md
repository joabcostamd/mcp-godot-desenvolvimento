# AreaDamage — Dano em Área

**PT:** Area2D que causa dano explosivo. `explode()` atinge todos os Health no raio, com falloff por distância e knockback opcional.

**EN:** Area2D that deals explosive damage. `explode()` hits all Health in radius, with distance falloff and optional knockback.

## Uso Rápido
```gdscript
var explosion := AreaDamage.new()
explosion.damage = 100
explosion.radius = 150.0
explosion.falloff = 0.3
explosion.explosion_force = 400.0
add_child(explosion)
explosion.global_position = bomb_position
explosion.explode()
```
