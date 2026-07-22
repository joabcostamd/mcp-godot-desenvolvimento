# Floating Text

Texto flutuante que aparece na tela (dano, cura, crítico), sobe verticalmente e desaparece com fade-out. Ideal para feedback numérico em tempo real.

**Parâmetros:** `speed` (px/s), `lifetime` (s), `fade_duration` (s), `font_size`, `outline_size`.

**Uso:** `show_text("42", Color.RED)` — emite `text_shown` ao terminar.

**Fontes:** Nodot TextEmitter (arquitetura Label + Tween), Godot 4.7 docs (`Label`, `Tween`, `Node2D`).
