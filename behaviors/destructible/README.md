# Destructible — Objeto Destrutível

Node2D que escuta Health sibling. Emite `destroyed` ao zerar HP.

```gdscript
var crate := Node2D.new()
var h := Health.new(); h.max_hp = 3; crate.add_child(h)
var d := Destructible.new(); crate.add_child(d)
d.destroyed.connect(func(): print("Crate quebrou!"))
```
