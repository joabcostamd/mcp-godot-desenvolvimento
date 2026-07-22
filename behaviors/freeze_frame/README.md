# Freeze Frame

Congela o jogo completamente (`Engine.time_scale = 0`) por uma duração fixa. Timer com `ignore_time_scale = true` garante contagem mesmo parado. Ideal para momentos dramáticos (morte de boss, Ultimate, vitória).

**Parâmetros:** `default_duration`, `restore_duration`.

**Uso:** `freeze(0.5)` — freeze de 0.5s. Sinais `frozen` + `resumed`.

**Fontes:** Godot 4.7 ClassDB (`Engine.time_scale`, `Timer.ignore_time_scale`), Juicee.
