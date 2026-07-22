# Hit Stop

Congelamento momentâneo do jogo (hit-stop / impact-freeze). Reduz `Engine.time_scale` por uma duração curta e restaura suavemente. Ignora triggers durante freeze ativo. Restaura `1.0` ao sair da árvore.

**Parâmetros:** `freeze_scale`, `default_duration`, `restore_duration`.

**Uso:** `trigger(0.15)` — freeze de 0.15s. Sinais `hit_stopped` + `resumed`.

**Fontes:** Godot 4.7 ClassDB (`Engine.time_scale`, `Timer`), Juicee (hit-stop pattern).
