# LerpSmooth — Interpolação Suave

Tween wrapper: `move_to()`, `rotate_to()`, `scale_to()`, `modulate_to()`.

```gdscript
var sprite := Sprite2D.new()
var lerp := LerpSmooth.new(); lerp.duration = 0.3; sprite.add_child(lerp)
lerp.move_to(Vector2(200, 100))
```
