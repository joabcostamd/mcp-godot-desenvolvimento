# Day-Night Cycle

Ciclo dia-noite contínuo. `_process` interpola 0→1 sobre `cycle_duration`. Emite `time_changed(0-1)` a cada frame e `phase_changed(dawn/day/dusk/night)` nas transições. `start()`/`stop()` controlam.

**Parâmetros:** `cycle_duration`, `auto_start`.

**Uso:** Conecte `time_changed` a shaders/luzes. `get_phase()` retorna fase atual.

**Fontes:** Godot 4.7 ClassDB.
