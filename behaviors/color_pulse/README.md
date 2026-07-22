# Color Pulse

Pulsação rítmica de `modulate` no nó pai via `_process + sin()`. Oscila entre cor original e `pulse_color`. `start()`/`stop()` controlam; `auto_start` inicia automaticamente. Restaura modulate original ao parar.

**Parâmetros:** `pulse_color`, `frequency` (Hz), `amplitude`, `auto_start`.

**Uso:** `start()` — começa a pulsar. `stop()` — para e restaura. Sinal `pulsing`.

**Fontes:** Godot 4.7 ClassDB (`Node.modulate`, `_process`, `sin()`).
