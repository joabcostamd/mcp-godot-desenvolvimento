# Round Timer

Timer de rodada com contagem regressiva/progressiva. `start()` inicia, emite `tick(remaining)` a cada segundo. `countdown` decrementa; `pause_on_end` pausa o jogo ao terminar.

**Parâmetros:** `duration`, `countdown`, `pause_on_end`.

**Uso:** `start()` — emite `round_started`, `tick`, `time_up`, `round_ended`.

**Fontes:** Godot 4.7 ClassDB (`Timer`).
