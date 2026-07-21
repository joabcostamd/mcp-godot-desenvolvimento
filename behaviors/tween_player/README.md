# Tween Player

Player de Tween genérico. Anima qualquer propriedade de qualquer nó com easing, transição e delay configuráveis. `play(node, prop, target, duration)`. Suporta cancelamento (`stop()`).

**Parâmetros:** `default_duration`, `default_easing`, `default_transition`, `default_delay`.

**Uso:** `play(sprite, "modulate:a", 0.0, 1.0)` — fade out. Sinais `tween_started` + `tween_finished`.

**Fontes:** Godot 4.7 ClassDB (`Tween`, `tween_property`, `set_ease`, `set_trans`).
