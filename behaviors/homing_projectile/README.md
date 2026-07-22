# HomingProjectile — Projétil Teleguiado

**PT:** Area2D que persegue um alvo com steering. `set_target(node)` define o alvo. Causa dano ao colidir.

**EN:** Area2D that pursues a target with steering. `set_target(node)` sets the target. Deals damage on collision.

```gdscript
var missile := HomingProjectile.new()
missile.speed = 400.0; missile.turn_rate = 5.0; missile.damage = 50
missile.set_target(player)
add_child(missile)
```
