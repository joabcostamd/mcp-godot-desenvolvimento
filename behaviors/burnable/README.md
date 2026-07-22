# Burnable — Inflamável

Auto-detecta Health sibling. Dano `fire` → ignição → queima com DPS.

```gdscript
var obj := Node2D.new()
var h := Health.new(); h.max_hp = 20; obj.add_child(h)
var b := Burnable.new(); obj.add_child(b)
```
