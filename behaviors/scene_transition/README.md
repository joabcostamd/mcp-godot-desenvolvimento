# Scene Transition

Transição entre cenas com fade via `CanvasLayer` + `ColorRect` fullscreen. `transition_to(scene_path, duration)` — fade-out → `change_scene_to_file` → fade-in. Sinais `transition_started`/`transition_finished`.

**Parâmetros:** `fade_color`, `default_duration`.

**Uso:** `transition_to("res://scenes/level2.tscn", 1.0)`. Destrava `main_menu` e `teleport`.

**Fontes:** Godot 4.7 ClassDB (`SceneTree.change_scene_to_file`, `CanvasLayer`, `ColorRect`).
