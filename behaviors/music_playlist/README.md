# Music Playlist

Playlist de música com suporte a shuffle, crossfade e navegação. `play()` inicia, `next()`/`prev()` navegam. Toca no bus `Music`. Crossfade suave entre faixas.

**Parâmetros:** `tracks`, `shuffle`, `crossfade_duration`, `volume_db`, `auto_play`.

**Uso:** Adicione tracks no array e chame `play()`. Sinais `track_changed` + `playlist_finished`.

**Fontes:** Godot 4.7 ClassDB (`AudioStreamPlayer`, `RandomNumberGenerator`).
