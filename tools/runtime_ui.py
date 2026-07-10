"""runtime_ui.py — UI Runtime + Sistema (Fase 3).

Ferramentas de UI runtime, performance, janela, debug draw, input state.
Inspirado no tugcantopaloglu/godot-mcp.

Tools: game_performance, game_window, game_os_info, game_debug_draw,
       game_input_state, game_time_scale, game_world_settings
"""

import json


def _run(code: str) -> dict:
    try:
        from tools.runtime_ops import execute_gdscript_runtime
        result = execute_gdscript_runtime(code)
        if isinstance(result, dict) and result.get("status") == "error":
            return result
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def game_performance() -> dict:
    """Métricas de performance: FPS, frame time, memória, objetos, draw calls."""
    code = """
    var perf = Performance.get_monitor(Performance.TIME_FPS)
    var frame_time = Performance.get_monitor(Performance.TIME_PROCESS) * 1000
    var mem_static = Performance.get_monitor(Performance.MEMORY_STATIC)
    var objects = Performance.get_monitor(Performance.OBJECT_COUNT)
    var nodes = Performance.get_monitor(Performance.OBJECT_NODE_COUNT)
    var draw_calls = Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
    var video_mem = Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)
    return {
        "fps": perf,
        "frame_time_ms": snapped(frame_time, 0.01),
        "memory_static_mb": snapped(mem_static / 1048576.0, 0.1),
        "objects": objects,
        "nodes": nodes,
        "draw_calls": draw_calls,
        "video_mem_mb": snapped(video_mem / 1048576.0, 0.1)
    }
    """
    return _run(code)


def game_window(
    action: str = "get",
    width: int = 0, height: int = 0,
    fullscreen: bool | None = None,
    title: str = "",
) -> dict:
    """Controle de janela do jogo."""
    if action == "get":
        code = """
        var win = DisplayServer.window_get_size()
        return {
            "width": win.x, "height": win.y,
            "fullscreen": DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN,
            "title": DisplayServer.window_get_title()
        }
        """
    elif action == "set":
        code = f"""
        if {width} > 0 and {height} > 0:
            DisplayServer.window_set_size(Vector2i({width}, {height}))
        if "{title}":
            DisplayServer.window_set_title("{title}")
        var fs = {str(fullscreen).lower()}
        return {{"status":"success"}}
        """
    elif action == "fullscreen":
        code = """
        var current = DisplayServer.window_get_mode()
        var new_mode = DisplayServer.WINDOW_MODE_FULLSCREEN if current != DisplayServer.WINDOW_MODE_FULLSCREEN else DisplayServer.WINDOW_MODE_WINDOWED
        DisplayServer.window_set_mode(new_mode)
        return {"status":"success","fullscreen":new_mode == DisplayServer.WINDOW_MODE_FULLSCREEN}
        """
    else:
        return {"status": "error", "message": f"Ação desconhecida: {action}"}
    return _run(code)


def game_os_info() -> dict:
    """Info do sistema operacional."""
    code = """
    return {
        "platform": OS.get_name(),
        "locale": OS.get_locale(),
        "screen_size": str(DisplayServer.screen_get_size()),
        "screen_dpi": DisplayServer.screen_get_dpi(),
        "adapters": str(RenderingServer.get_video_adapter_name()),
        "memory_mb": snapped(OS.get_static_memory_usage() / 1048576.0, 0.1),
        "processor_count": OS.get_processor_count()
    }
    """
    return _run(code)


def game_debug_draw(
    shape: str = "line",
    from_x: float = 0, from_y: float = 0, from_z: float = 0,
    to_x: float = 100, to_y: float = 100, to_z: float = 0,
    color: str = "#ff0000",
    duration: float = 5.0,
    mode: str = "3d",
) -> dict:
    """Desenha geometria de debug no jogo."""
    color_hex = color.lstrip("#")
    r, g, b = int(color_hex[0:2], 16)/255, int(color_hex[2:4], 16)/255, int(color_hex[4:6], 16)/255

    if mode == "2d":
        code = f"""
        var c = Color({r},{g},{b})
        var canvas = get_tree().root.get_node_or_null("_debug_canvas")
        if not canvas:
            canvas = CanvasLayer.new()
            canvas.name = "_debug_canvas"
            get_tree().root.add_child(canvas)
        if "{shape}" == "line":
            canvas.draw_line(Vector2({from_x},{from_y}), Vector2({to_x},{to_y}), c, 2.0)
        elif "{shape}" == "rect":
            canvas.draw_rect(Rect2({from_x},{from_y},{to_x},{to_y}), c, false)
        return {{"status":"success","shape":"{shape}","mode":"2d"}}
        """
    else:
        code = f"""
        var c = Color({r},{g},{b})
        var debug = get_tree().root.get_node_or_null("_debug_draw")
        if not debug:
            debug = Node3D.new()
            debug.name = "_debug_draw"
            get_tree().root.add_child(debug)
        
        var mesh = ImmediateMesh.new()
        var mat = StandardMaterial3D.new()
        mat.albedo_color = c
        mat.flags_unshaded = true
        mat.vertex_color_use_as_albedo = true
        
        mesh.surface_begin(Mesh.PRIMITIVE_LINES)
        mesh.surface_set_color(c)
        mesh.surface_add_vertex(Vector3({from_x},{from_y},{from_z}))
        mesh.surface_add_vertex(Vector3({to_x},{to_y},{to_z}))
        mesh.surface_end()
        
        var mi = MeshInstance3D.new()
        mi.mesh = mesh
        mi.material_override = mat
        debug.add_child(mi)
        await get_tree().create_timer({duration}).timeout
        mi.queue_free()
        return {{"status":"success","shape":"line","mode":"3d","duration":{duration}}}
        """
    return _run(code)


def game_input_state() -> dict:
    """Estado atual de input: teclas, mouse, gamepad."""
    code = """
    var keys = []
    for i in range(KEY_SPECIAL):
        if Input.is_key_pressed(i):
            keys.append(OS.get_keycode_string(i))
    
    var mouse = {
        "position": str(DisplayServer.mouse_get_position()),
        "buttons": []
    }
    for b in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT, MOUSE_BUTTON_MIDDLE]:
        if Input.is_mouse_button_pressed(b):
            mouse.buttons.append(b)
    
    var pads = Input.get_connected_joypads()
    
    return {
        "keys": keys,
        "mouse": mouse,
        "gamepads": pads
    }
    """
    return _run(code)


def game_time_scale(scale: float | None = None) -> dict:
    """Get/set Engine.time_scale."""
    if scale is not None:
        code = f"""
        Engine.time_scale = {scale}
        return {{"status":"success","time_scale":Engine.time_scale}}
        """
    else:
        code = """
        return {"status":"success","time_scale":Engine.time_scale}
        """
    return _run(code)


def game_world_settings(
    gravity_x: float | None = None, gravity_y: float | None = None, gravity_z: float | None = None,
    physics_fps: int | None = None,
) -> dict:
    """Get/set configurações do mundo (gravidade, physics FPS)."""
    changes = []
    if gravity_y is not None:
        changes.append(f"ProjectSettings.set_setting('physics/2d/default_gravity', {gravity_y})")
    if physics_fps is not None:
        changes.append(f"Engine.physics_ticks_per_second = {physics_fps}")

    if changes:
        code = "\n".join(changes) + f"""
        return {{"status":"success","gravity_2d":ProjectSettings.get_setting('physics/2d/default_gravity'),"physics_fps":Engine.physics_ticks_per_second}}
        """
    else:
        code = """
        return {"status":"success","gravity_2d":ProjectSettings.get_setting('physics/2d/default_gravity'),"physics_fps":Engine.physics_ticks_per_second}
        """
    return _run(code)
