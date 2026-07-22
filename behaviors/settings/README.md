# Settings

Tela de configurações com sliders de volume (Master/Music/SFX), toggle fullscreen e seletor de idioma. `apply()` persiste via `SaveLoad`. `setting_changed` emitido a cada mudança.

**Parâmetros:** `default_master_vol`, `default_music_vol`, `default_sfx_vol`, `show_fullscreen`, `show_language`.

**Uso:** Adicione à cena de opções. `apply()` salva. Sinal `setting_changed(setting, value)`.

**Fontes:** Godot 4.7 ClassDB (`DisplayServer`, `AudioServer`, `HSlider`, `CheckButton`).
