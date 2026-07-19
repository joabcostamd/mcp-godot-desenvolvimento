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


# ══════════════════════════════════════════════════════════════════════
# Fatia 1.3 — capture_ui_snapshot (dump de Control + Rect2)
# ══════════════════════════════════════════════════════════════════════

_control_types_cache: set[str] | None = None


def _get_control_types() -> set[str]:
    """Retorna o set de todos os tipos que herdam de Control."""
    global _control_types_cache
    if _control_types_cache is not None:
        return _control_types_cache
    base_controls = {
        "Control", "Button", "Label", "LineEdit", "TextEdit",
        "Panel", "PanelContainer", "VBoxContainer", "HBoxContainer",
        "GridContainer", "MarginContainer", "ScrollContainer",
        "TabContainer", "SplitContainer", "ColorRect", "TextureRect",
        "TextureButton", "CheckBox", "CheckButton", "OptionButton",
        "PopupMenu", "Popup", "PopupPanel", "Window",
        "AcceptDialog", "ConfirmationDialog", "FileDialog",
        "GraphEdit", "GraphNode", "ItemList", "Tree", "RichTextLabel",
        "ProgressBar", "Slider", "SpinBox", "TabBar", "MenuBar",
        "MenuButton", "LinkButton", "ColorPicker", "ColorPickerButton",
        "SubViewport", "SubViewportContainer",
        "Container", "Range", "BaseButton", "AspectRatioContainer",
        "CenterContainer", "FlowContainer", "NinePatchRect",
        "ReferenceRect", "Separator", "HSlider", "VSlider",
        "HSplitContainer", "VSplitContainer", "HScrollBar", "VScrollBar",
    }
    _control_types_cache = base_controls
    return _control_types_cache


def capture_ui_snapshot(
    scene_path: str | None = None,
    project_path: str | None = None,
) -> dict:
    """Captura dump estruturado de todos os nós Control com Rect2.

    Percorre a árvore da cena e coleta nome, caminho, tipo, Rect2 global
    (posicao + tamanho), visibilidade e z_index de cada no Control.

    Modo bridge (editor/jogo vivo): usa get_scene_tree() do editor/addon.
    Modo file-based (fallback): parseia o arquivo .tscn.

    Args:
        scene_path: Caminho da cena .tscn. Se None, tenta via bridge.
        project_path: Caminho do projeto (auto-detecta se None).

    Returns:
        {"status": "success", "controls": [{"name","path","type",
         "rect2":{"x","y","w","h"},"visible":bool,"z_index":int}],
         "total": int, "mode": "bridge"|"file"}
    """
    from pathlib import Path as _Path
    from tools.project_ops import _get_active_project as _gap

    # ── Modo 1: Bridge (editor/jogo vivo) ──────────────────────────
    try:
        from tools.addon_bridge import get_bridge
        bridge = get_bridge()
        if bridge.is_available():
            result = bridge.call("get_scene_tree", {})
            if result.get("status") == "success":
                tree = result.get("tree", result)
                controls = _extract_controls_from_tree(tree)
                return {
                    "status": "success",
                    "controls": controls,
                    "total": len(controls),
                    "mode": "bridge",
                }
    except Exception:
        pass

    # ── Modo 2: File-based (parse .tscn) ───────────────────────────
    if scene_path is None:
        return {
            "status": "error",
            "message": "Nenhum bridge disponivel e scene_path nao informado. "
                       "Informe o caminho da cena .tscn ou conecte ao editor.",
        }

    proj = _Path(project_path) if project_path else _Path(_gap())
    full_path = proj / scene_path
    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' nao encontrada."}

    try:
        import godot_parser as gp
        scene = gp.load(str(full_path))
    except Exception as e:
        return {"status": "error", "message": f"Erro ao parsear cena: {e}"}

    control_types = _get_control_types()
    controls = []
    nodes = scene.get_nodes() if hasattr(scene, 'get_nodes') else []

    for node in nodes:
        node_type = getattr(node, 'type', '') or ''
        if node_type not in control_types:
            try:
                from tools.classdb import get_class_hierarchy
                hierarchy = get_class_hierarchy(node_type)
                if "Control" not in hierarchy:
                    continue
            except Exception:
                continue

        props = {}
        if hasattr(node, 'properties'):
            props = dict(node.properties)
        elif hasattr(node, 'get'):
            for key in ["offset_left", "offset_top", "offset_right", "offset_bottom",
                        "visible", "z_index", "position", "size"]:
                try:
                    val = node.get(key)
                    if val is not None:
                        props[key] = val
                except Exception:
                    pass

        rect2 = _compute_control_rect(props)
        name = getattr(node, 'name', '') or props.get('name', '')
        parent = getattr(node, 'parent', '') or ''

        controls.append({
            "name": str(name),
            "path": f"{parent}/{name}" if parent else str(name),
            "type": str(node_type),
            "rect2": rect2,
            "visible": _parse_bool(props.get("visible", "true")),
            "z_index": int(props.get("z_index", 0)),
        })

    # Normaliza paths: "./Child" -> "RootName/Child"
    root_name = ""
    for c in controls:
        if not c["path"].startswith("./") and "/" not in c["path"]:
            root_name = c["path"]
            break
    if root_name:
        for c in controls:
            if c["path"].startswith("./"):
                c["path"] = root_name + "/" + c["path"][2:]

    return {
        "status": "success",
        "controls": controls,
        "total": len(controls),
        "mode": "file",
        "scene": scene_path,
    }


def _compute_control_rect(props: dict) -> dict:
    """Calcula Rect2 {x, y, w, h} a partir de propriedades de Control."""
    left = float(props.get("offset_left", 0))
    top = float(props.get("offset_top", 0))
    right = float(props.get("offset_right", left + 100))
    bottom = float(props.get("offset_bottom", top + 100))
    return {
        "x": round(left, 1),
        "y": round(top, 1),
        "w": round(right - left, 1),
        "h": round(bottom - top, 1),
    }


def _parse_bool(value) -> bool:
    """Converte valor de .tscn para bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    return bool(value)


def _extract_controls_from_tree(tree: dict, prefix: str = "") -> list[dict]:
    """Extrai nos Control de uma arvore retornada pelo bridge."""
    controls = []
    if not isinstance(tree, dict):
        return controls

    node_type = tree.get("type", "")
    name = tree.get("name", "")
    path = f"{prefix}/{name}" if prefix else name

    if node_type and (
            "Control" in node_type or "Button" in node_type or
            "Label" in node_type or "Panel" in node_type or
            "Container" in node_type or "Bar" in node_type or
            "Edit" in node_type or "Rect" in node_type or
            "Popup" in node_type or "Window" in node_type):
        props = tree.get("properties", {})
        rect2 = _compute_control_rect(props)
        controls.append({
            "name": name,
            "path": path,
            "type": node_type,
            "rect2": rect2,
            "visible": _parse_bool(props.get("visible", True) if isinstance(props, dict) else True),
            "z_index": int(props.get("z_index", 0) if isinstance(props, dict) else 0),
        })

    for child in tree.get("children", []):
        controls.extend(_extract_controls_from_tree(child, path))

    return controls


# ══════════════════════════════════════════════════════════════════════
# Fatia 1.4 — detect_ui_overlaps (sobreposicao geometrica de UI)
# ══════════════════════════════════════════════════════════════════════

def _rects_intersect(a: dict, b: dict) -> dict | None:
    """Verifica se dois retangulos se intersectam.

    Args:
        a, b: dicts com rect2: {x, y, w, h}

    Returns:
        dict com area de intersecao {x, y, w, h} ou None se nao intersectam.
    """
    ax1 = a["rect2"]["x"]
    ay1 = a["rect2"]["y"]
    ax2 = ax1 + a["rect2"]["w"]
    ay2 = ay1 + a["rect2"]["h"]

    bx1 = b["rect2"]["x"]
    by1 = b["rect2"]["y"]
    bx2 = bx1 + b["rect2"]["w"]
    by2 = by1 + b["rect2"]["h"]

    ix = max(ax1, bx1)
    iy = max(ay1, by1)
    iw = min(ax2, bx2) - ix
    ih = min(ay2, by2) - iy

    if iw <= 0 or ih <= 0:
        return None

    area = iw * ih
    area_a = a["rect2"]["w"] * a["rect2"]["h"]
    area_b = b["rect2"]["w"] * b["rect2"]["h"]

    return {
        "x": round(ix, 1),
        "y": round(iy, 1),
        "w": round(iw, 1),
        "h": round(ih, 1),
        "intersection_pct_a": round(area / area_a * 100, 1) if area_a > 0 else 0,
        "intersection_pct_b": round(area / area_b * 100, 1) if area_b > 0 else 0,
    }


def _is_parent_child(a: dict, b: dict) -> bool:
    """Verifica se a e b tem relacao pai-filho (aninhamento intencional).

    No Godot, um Control pai contem seus filhos — isso nao e sobreposicao
    indevida. Verificamos pelo path: se o path de um e prefixo do outro.
    """
    path_a = a.get("path", "")
    path_b = b.get("path", "")
    if not path_a or not path_b:
        return False
    return path_b.startswith(path_a + "/") or path_a.startswith(path_b + "/")


def detect_ui_overlaps(
    scene_path: str,
    project_path: str | None = None,
    min_overlap_pct: float = 5.0,
) -> dict:
    """Detecta sobreposicao indevida entre elementos de UI.

    Usa capture_ui_snapshot para obter todos os Control nodes com Rect2
    e compara geometricamente cada par. Filtra relacoes pai-filho
    (aninhamento intencional). Retorna apenas sobreposicoes entre irmaos
    ou elementos sem relacao hierarquica direta.

    Args:
        scene_path: Caminho da cena .tscn.
        project_path: Caminho do projeto (auto-detecta se None).
        min_overlap_pct: Percentual minimo de sobreposicao para reportar
                        (default 5%, evita falsos positivos por bordas).

    Returns:
        {"status": "success", "overlaps": [{"control_a","control_b",
         "intersection": {"x","y","w","h","intersection_pct_a","intersection_pct_b"},
         "severity": "high"|"medium"|"low"}], "total_controls": int,
         "total_overlaps": int}
    """
    snapshot = capture_ui_snapshot(scene_path, project_path)
    if snapshot.get("status") != "success":
        return snapshot

    controls = snapshot.get("controls", [])
    visible_controls = [c for c in controls if c.get("visible", True)]

    overlaps = []
    for i in range(len(visible_controls)):
        for j in range(i + 1, len(visible_controls)):
            a = visible_controls[i]
            b = visible_controls[j]

            # Pula relacoes pai-filho
            if _is_parent_child(a, b):
                continue

            intersection = _rects_intersect(a, b)
            if intersection is None:
                continue

            # Filtra sobreposicoes minusculas
            max_pct = max(intersection["intersection_pct_a"],
                         intersection["intersection_pct_b"])
            if max_pct < min_overlap_pct:
                continue

            # Classifica severidade
            if max_pct > 50:
                severity = "high"
            elif max_pct > 20:
                severity = "medium"
            else:
                severity = "low"

            overlaps.append({
                "control_a": {"name": a["name"], "path": a["path"], "type": a["type"]},
                "control_b": {"name": b["name"], "path": b["path"], "type": b["type"]},
                "intersection": intersection,
                "severity": severity,
            })

    return {
        "status": "success",
        "overlaps": overlaps,
        "total_controls": len(controls),
        "visible_controls": len(visible_controls),
        "total_overlaps": len(overlaps),
    }


# ══════════════════════════════════════════════════════════════════════
# Fatia 1.5 — generate_ui_overlay (Set-of-Marks)
# ══════════════════════════════════════════════════════════════════════

# Cores para o Set-of-Marks (paleta distinguivel)
_MARKER_COLORS = [
    (255, 50, 50), (50, 150, 255), (50, 200, 80), (255, 180, 30),
    (200, 60, 220), (30, 200, 200), (255, 120, 60), (120, 80, 255),
    (80, 200, 120), (255, 60, 180), (180, 180, 40), (60, 120, 255),
]


def generate_ui_overlay(
    scene_path: str,
    project_path: str | None = None,
    width: int = 1280,
    height: int = 720,
    bg_color: str = "#1a1a2e",
    line_width: int = 3,
    font_size: int = 18,
) -> dict:
    """Gera overlay Set-of-Marks: caixas numeradas sobre cada Control.

    Cria uma imagem com retangulos coloridos e numeros para cada elemento
    de UI visivel. A IA pode referenciar elementos como "elemento #3"
    para dar feedback preciso de layout.

    Args:
        scene_path: Caminho da cena .tscn.
        project_path: Caminho do projeto (auto-detecta se None).
        width: Largura da imagem (default 1280).
        height: Altura da imagem (default 720).
        bg_color: Cor de fundo em hex (default azul escuro).
        line_width: Espessura da borda em px (default 3).
        font_size: Tamanho da fonte dos numeros (default 18).

    Returns:
        {"status": "success", "image_base64": str,
         "markers": [{"id": int, "name", "type", "rect2": {...}}],
         "total_markers": int}
    """
    import base64
    from io import BytesIO

    snapshot = capture_ui_snapshot(scene_path, project_path)
    if snapshot.get("status") != "success":
        return snapshot

    controls = snapshot.get("controls", [])
    visible = [c for c in controls if c.get("visible", True)]

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return {
            "status": "error",
            "message": "Pillow nao instalado. Execute: pip install Pillow",
        }

    # Converte bg_color hex → RGB
    hex_color = bg_color.lstrip("#")
    bg_rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    img = Image.new("RGB", (width, height), bg_rgb)
    draw = ImageDraw.Draw(img)

    # Tenta carregar fonte, fallback para default
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    markers = []
    for idx, control in enumerate(visible):
        r = control["rect2"]
        x1 = max(0, int(r["x"]))
        y1 = max(0, int(r["y"]))
        x2 = min(width, int(r["x"] + r["w"]))
        y2 = min(height, int(r["y"] + r["h"]))

        # Pula controles fora da tela
        if x2 <= 0 or y2 <= 0 or x1 >= width or y1 >= height:
            continue

        color = _MARKER_COLORS[(idx + 1) % len(_MARKER_COLORS)]
        marker_id = idx + 1

        # Retangulo com padding
        draw.rectangle([x1, y1, x2, y2], outline=color, width=line_width)

        # Etiqueta com fundo
        label = str(marker_id)
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0] + 8
        th = bbox[3] - bbox[1] + 4
        label_x = x1 + 2
        label_y = max(0, y1 - th - 2)

        draw.rectangle([label_x, label_y, label_x + tw, label_y + th], fill=color)
        draw.text((label_x + 4, label_y + 2), label, fill=(255, 255, 255), font=font)

        markers.append({
            "id": marker_id,
            "name": control["name"],
            "type": control["type"],
            "path": control.get("path", ""),
            "rect2": r,
        })

    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return {
        "status": "success",
        "image_base64": b64,
        "markers": markers,
        "total_markers": len(markers),
        "image_size": f"{width}x{height}",
    }
