# Ambience Zone

Zona de som ambiente 2D. `Area2D` + `AudioStreamPlayer2D` com atenuação espacial. Toca ao detectar body; para ao sair. `auto_play` para som contínuo.

**Parâmetros:** `audio_stream`, `volume_db`, `max_distance`, `attenuation`, `auto_play`.

**Uso:** Posicione na cena, configure `audio_stream`. Sinais `entered_zone` + `exited_zone`.

**Fontes:** Godot 4.7 ClassDB (`Area2D`, `AudioStreamPlayer2D`).
