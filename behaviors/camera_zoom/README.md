# Camera Zoom

Zoom suave da câmera via `Camera2D.zoom` com Tween. `zoom_to(target, duration)` aproxima/afasta. Sem câmera = no-op seguro. Detecta Camera2D como parent ou via viewport.

**Parâmetros:** `default_zoom`, `default_duration`.

**Uso:** `zoom_to(Vector2(2, 2), 0.5)` — zoom 2x. Sinais `zoom_started` + `zoom_finished`.

**Fontes:** Godot 4.7 ClassDB (`Camera2D.zoom`, `Tween`).
