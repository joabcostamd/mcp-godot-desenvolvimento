# LookAtTarget — Mirar Alvo

Rotaciona parent Node2D para mirar alvo com `lerp_angle`.

```gdscript
var turret := Node2D.new()
var aim := LookAtTarget.new(); turret.add_child(aim)
aim.set_target(player)
```

| Nome | Tipo | Range | Default | Desc |
|------|------|-------|---------|------|
| `rotation_speed` | float | 0–50 | 5.0 | rad/s |
| `angle_offset` | float | — | 0 | offset rad |
