# Timer Behavior

Wrapper de `Timer` com `start`/`stop`/`restart`/`pause`/`resume`. Emite `timeout` ao terminar e `tick` a cada ciclo (não one-shot). `one_shot` e `auto_start` configuráveis.

**Parâmetros:** `wait_time`, `one_shot`, `auto_start`.

**Uso:** `start()`, `restart()`. Sinais `timeout` + `tick`. Base para cooldowns e spawners.

**Fontes:** Godot 4.7 ClassDB (`Timer`).
