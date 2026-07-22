# Health Bar

Barra de vida visual via `ColorRect`. Espelha `current_hp/max_hp` do `Health`. Auto-detecta sibling Health ou usa `target_health`. Suporte a texto e interpolação suave.

**Parâmetros:** `target_health`, `bar_color`, `background_color`, `show_text`, `smooth`, `bar_width`, `bar_height`.

**Uso:** Adicione como filho do mesmo nó que tem `Health`. Atualiza automaticamente.

**Fontes:** Godot 4.7 ClassDB (`ColorRect`, `NodePath`).
