# Defeat Condition

Condição de derrota: `PLAYER_DEAD` (polling de grupo), `TIME_UP` ou `CUSTOM`. `check(defeated)` manual ou `trigger()` direto. Emite `defeat_triggered`.

**Parâmetros:** `condition_type`, `player_group`.

**Uso:** `check(true)` quando player morre. `trigger()` para game over instantâneo.

**Fontes:** Godot 4.7 ClassDB.
