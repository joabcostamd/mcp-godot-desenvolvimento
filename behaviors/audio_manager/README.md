# Audio Manager

Gerenciador central de áudio. Controla volume dos buses `Master`, `Music`, `SFX` via `AudioServer`. `play_sfx(stream)` e `play_music(stream)` criam players temporários com auto-limpeza.

**Parâmetros:** `master_volume_db`, `music_volume_db`, `sfx_volume_db`.

**Uso:** `play_sfx(explosion_sound)`, `set_bus_volume("SFX", -6.0)`. Destrava `sfx_player`, `music_playlist`, `ambience_zone`.

**Fontes:** Godot 4.7 ClassDB (`AudioServer`, `AudioStreamPlayer`).
