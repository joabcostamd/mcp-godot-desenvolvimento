# Time Scale

Controle global de escala de tempo via `Engine.time_scale`. Bullet-time, slow-motion e fast-forward com transições suaves via Tween. Restaura 1.0 ao sair da árvore. Apenas um por cena.

**Parâmetros:** `default_scale`, `transition_duration`, `min_scale`, `max_scale`.

**Uso:** `set_scale(0.3, 0.5)` — bullet-time em 0.5s. `reset()` — volta ao normal. Sinal `scale_changed`.

**Fontes:** Godot 4.7 ClassDB (`Engine.time_scale`, `Tween`), Nodot TimeScale.
