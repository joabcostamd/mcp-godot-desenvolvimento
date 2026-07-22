# Chromatic Aberration

Simulação de aberração cromática via flicker RGB no `modulate` do parent. `trigger(intensity, duration)` oscila entre canais vermelho/verde/azul e restaura o modulate original. Sem dependência de shader.

**Parâmetros:** `default_intensity`, `default_duration`, `flicker_speed`.

**Uso:** `trigger(0.8, 0.5)` — efeito intenso por 0.5s. Sinais `aberration_started` + `aberration_finished`.

**Fontes:** Godot 4.7 ClassDB (`CanvasItem.modulate`, `Tween`).
