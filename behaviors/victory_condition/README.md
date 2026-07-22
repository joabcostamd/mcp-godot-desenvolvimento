# Victory Condition

Condição de vitória: `ALL_ENEMIES_DEAD` (polling de grupo), `SCORE_REACHED`, `TIME_SURVIVED` ou `CUSTOM`. `check(value)` manual ou `trigger()` direto. Emite `victory_achieved`.

**Parâmetros:** `condition_type`, `target_value`, `enemy_group`.

**Uso:** `check(score)` a cada kill. `trigger()` para vitória instantânea.

**Fontes:** Godot 4.7 ClassDB (`SceneTree.get_nodes_in_group`).
