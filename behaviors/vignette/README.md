# Vignette

Efeito vinheta (bordas escuras) via `ColorRect` fullscreen com `GradientTexture2D` radial sobre `CanvasLayer`. `trigger(intensity, duration)` com Tween. Não bloqueia input.

**Parâmetros:** `vignette_color`, `default_intensity`, `default_duration`.

**Uso:** `trigger(0.7, 1.0)` — vinheta intensa por 1s. Sinais `vignette_started` + `vignette_finished`.

**Fontes:** Godot 4.7 ClassDB (`ColorRect`, `GradientTexture2D`, `CanvasLayer`).
