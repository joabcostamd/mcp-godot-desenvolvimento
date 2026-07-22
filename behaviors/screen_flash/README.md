# Screen Flash

Flash de tela via ColorRect fullscreen em CanvasLayer. Disparado por `flash(color, duration)`. Fade-in/out configuráveis. Não bloqueia input do mouse. Reinicia se chamado durante animação ativa.

**Parâmetros:** `default_color`, `default_duration`, `fade_in`, `fade_out`.

**Uso:** `flash(Color.RED, 0.5)` — emite `flashed` ao terminar.

**Fontes:** Godot 4.7 ClassDB (`CanvasLayer`, `ColorRect`, `Tween`, `Control`), padrão universal screen flash.
