# Interactable — Objeto Interagível

Area2D: player entra → foco, `ui_accept` → `interacted`.

```gdscript
var npc := Area2D.new()
var ia := Interactable.new(); ia.prompt_text = "Falar"
npc.add_child(ia)
ia.interacted.connect(func(b): print("Interagiu!"))
```
