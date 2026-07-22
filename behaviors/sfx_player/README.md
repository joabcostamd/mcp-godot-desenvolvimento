# SFX Player

Player de efeitos sonoros one-shot. `play()` toca o `audio_stream` padrão; `play_stream(stream)` sobrescreve. Auto-limpeza via `finished` signal.

**Parâmetros:** `audio_stream`, `volume_db`, `pitch_scale`, `bus`, `auto_play`.

**Uso:** `play_stream(explosion_sound)` — toca e auto-limpa. Sinais `played` + `finished`.

**Fontes:** Godot 4.7 ClassDB (`AudioStreamPlayer`).
