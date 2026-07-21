# Glitch

Efeito glitch com deslocamento horizontal aleatório no parent `Node2D`. `trigger(intensity, duration)` aplica saltos de posição via Tween rápido e restaura o original.

**Parâmetros:** `default_intensity`, `default_duration`, `max_offset`, `flicker_speed`.

**Uso:** `trigger(0.8, 0.5)` — glitch intenso. Sinais `glitch_started` + `glitch_finished`.

**Fontes:** Godot 4.7 ClassDB (`Node2D.position`, `Tween`).
