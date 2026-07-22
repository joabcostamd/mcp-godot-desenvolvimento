# Dialogue

Sistema de diálogo com `CanvasLayer` + `RichTextLabel`. Array de `{text, speaker}`. `next()` avança, `auto_advance` com Timer, `advance_input` escuta ação. `skip()` encerra.

**Parâmetros:** `lines`, `auto_advance`, `auto_delay`, `advance_input`.

**Uso:** `start([{text:"Hi", speaker:"NPC"}])`. Sinais `dialogue_started`, `line_displayed`, `dialogue_finished`.

**Fontes:** Godot 4.7 ClassDB (`RichTextLabel`, `Input`, `Timer`).
