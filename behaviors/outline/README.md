# Outline — Contorno Visual

Aplica outline shader ao parent CanvasItem.

```gdscript
var sprite := Sprite2D.new(); sprite.texture = ...
var ol := Outline.new(); ol.outline_color = Color.YELLOW
sprite.add_child(ol)
```
