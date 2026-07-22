# FollowPath — Seguir Caminho

Move parent Node2D ao longo de Path2D filho.

```gdscript
var enemy := Node2D.new()
var fp := FollowPath.new(); fp.speed = 80
var path := Path2D.new()
var c := Curve2D.new(); c.add_point(Vector2(0,0)); c.add_point(Vector2(200,0))
path.curve = c; fp.add_child(path); enemy.add_child(fp)
```
