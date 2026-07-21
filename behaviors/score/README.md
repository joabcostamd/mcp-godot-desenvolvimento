# Score

Sistema de pontuação com combo multiplier e high_score persistente. `add_score(amount)` incrementa, combo cresce dentro de `combo_window`. `reset_score()` zera tudo. High score salvo via SaveLoad.

**Parâmetros:** `combo_multiplier`, `combo_window`.

**Uso:** `add_score(100)` a cada kill. Sinais `score_changed`, `new_high_score`, `combo_reached`.

**Fontes:** Godot 4.7 ClassDB.
