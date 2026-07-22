# Trail

Rastro visual via `Line2D` que segue o nó pai. Acumula pontos históricos com spacing configurável e fading de alpha opcional. Ideal para projéteis, dash e movimento rápido.

**Parâmetros:** `max_points`, `point_spacing`, `fade`, `trail_width`.

**Uso:** Adicione como filho de um Node2D em movimento. `clear()` limpa o rastro.

**Fontes:** Godot 4.7 ClassDB (`Line2D`, `Node2D.global_position`, `to_local()`).
