# CameraFollow — Camera segue alvo com suavidade

Node filho de Camera2D. damping, offset, look_ahead.

## Quick Start

```gdscript
var camera := Camera2D.new()
camera.enabled = true
var follow := CameraFollow.new()
follow.set_target(player)
camera.add_child(follow)
add_child(camera)
```

## Propriedades

| Nome | Range | Default | Descricao |
|------|-------|---------|-----------|
| `target` | NodePath | — | Alvo (vazio=parent) |
| `offset` | Vector2 | (0,0) | Deslocamento |
| `damping` | 0–1 | 0.1 | Suavidade |
| `look_ahead` | 0–200 | 0 | Antecipacao (px) |
