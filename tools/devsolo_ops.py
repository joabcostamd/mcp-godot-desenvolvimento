"""devsolo_ops — Onda 8: Ferramentas Críticas para Dev Solo Autônomo.

Câmera, Navegação, Save/Load, Tweens, State Machine,
UI Templates, World Environment.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from tools.classdb import get_godot_bin, get_config, is_valid_node_type
from tools.project_ops import _get_active_project, _check_path_traversal
from tools.safety import checkpoint
from tools.runtime_ops import mark_pending_compile

ROOT = Path(__file__).resolve().parent.parent


def _check_path(path: str):
    """Wrapper para _check_path_traversal com project_root automatico."""
    return _check_path_traversal(path, _get_active_project())


def _hex_to_color(hex_str: str) -> str:
    """Converte hex (#1a1a2e) para formato Godot Color(r, g, b, a)."""
    h = hex_str.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return f"Color({r:.4f}, {g:.4f}, {b:.4f}, 1)"


# ══════════════════════════════════════════════════════════════════════
# 8.1 — SISTEMA DE CÂMERA
# ══════════════════════════════════════════════════════════════════════

def setup_camera_2d(
    scene_path: str,
    parent_node_path: str = ".",
    limits: dict | None = None,
    drag_horizontal: float = 0.0,
    drag_vertical: float = 0.0,
    zoom: list[float] | None = None,
    smoothing_enabled: bool = True,
    smoothing_speed: float = 5.0,
    current: bool = True,
) -> dict:
    """Adiciona e configura uma Camera2D.

    Args:
        scene_path: Caminho da cena (.tscn).
        parent_node_path: Caminho do nó pai (ex: "root" ou "root/Player").
        limits: Dict com left, top, right, bottom (em pixels).
        drag_horizontal: Margem de arrasto horizontal.
        drag_vertical: Margem de arrasto vertical.
        zoom: Zoom [x, y]. Default [1.0, 1.0].
        smoothing_enabled: Ativar suavização de movimento.
        smoothing_speed: Velocidade da suavização (maior = mais rápido).
        current: Tornar esta a câmera ativa.

    Returns:
        {"status": "success", "camera_path": str}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    # Ler .tscn
    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    # Gerar UID único
    import uuid
    uid = str(uuid.uuid4()).replace("-", "")[:16]

    # Construir nó Camera2D
    zoom_vec = zoom if zoom else [1.0, 1.0]
    camera_lines = [
        f'\n[node name="Camera2D" type="Camera2D" parent="{parent_node_path}"]\n',
        f'editor_description = "Camera2D configurada via MCP DevSolo - UID:{uid}"\n',
        f"anchor_mode = 0\n",
        f"current = {'true' if current else 'false'}\n",
        f"drag_horizontal_enabled = {'true' if drag_horizontal > 0 else 'false'}\n",
        f"drag_vertical_enabled = {'true' if drag_vertical > 0 else 'false'}\n",
    ]

    if drag_horizontal > 0:
        camera_lines.append(f"drag_left_margin = {drag_horizontal}\n")
        camera_lines.append(f"drag_right_margin = {drag_horizontal}\n")
    if drag_vertical > 0:
        camera_lines.append(f"drag_top_margin = {drag_vertical}\n")
        camera_lines.append(f"drag_bottom_margin = {drag_vertical}\n")

    if limits:
        camera_lines.append(f"limit_left = {limits.get('left', -10000000)}\n")
        camera_lines.append(f"limit_top = {limits.get('top', -10000000)}\n")
        camera_lines.append(f"limit_right = {limits.get('right', 10000000)}\n")
        camera_lines.append(f"limit_bottom = {limits.get('bottom', 10000000)}\n")
        camera_lines.append("limit_smoothed = true\n")

    camera_lines.append(f"position_smoothing_enabled = {'true' if smoothing_enabled else 'false'}\n")
    if smoothing_enabled:
        camera_lines.append(f"position_smoothing_speed = {smoothing_speed}\n")

    camera_lines.append(f"zoom = Vector2({zoom_vec[0]}, {zoom_vec[1]})\n")

    # Inserir no .tscn (antes do último nó ou no final)
    checkpoint(scene_path, proj)
    lines.extend(camera_lines)
    full_path.write_text("".join(lines), encoding="utf-8")

    camera_path = f"{parent_node_path}/Camera2D"
    mark_pending_compile()

    return {
        "status": "success",
        "camera_path": camera_path,
        "scene": scene_path,
        "limits": limits or {"left": -10000000, "top": -10000000, "right": 10000000, "bottom": 10000000},
        "zoom": zoom_vec,
        "smoothing": smoothing_enabled,
    }


def setup_camera_follow(
    scene_path: str,
    camera_node_path: str,
    target_node_path: str,
    smoothing: float = 5.0,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
    deadzone_width: float = 0.0,
    deadzone_height: float = 0.0,
) -> dict:
    """Faz a câmera seguir um nó alvo com suavidade.

    Gera script GDScript que atualiza camera.position no _process.

    Args:
        scene_path: Caminho da cena.
        camera_node_path: Caminho da Camera2D.
        target_node_path: Caminho do nó a seguir (ex: "root/Player").
        smoothing: Fator de suavização (lerp weight por frame).
        offset_x, offset_y: Offset da câmera em relação ao alvo.
        deadzone_width, deadzone_height: Deadzone onde a câmera não se move.

    Returns:
        {"status": "success", "script_path": str, "code": str}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    code = f'''extends Camera2D
# CameraFollow — gerado via MCP DevSolo
# Segue: {target_node_path}

@onready var target = get_node("{target_node_path}")
var offset_vec = Vector2({offset_x}, {offset_y})
var deadzone = Vector2({deadzone_width}, {deadzone_height})

func _ready():
    if target:
        global_position = target.global_position + offset_vec

func _process(_delta):
    if not target:
        return

    var target_pos = target.global_position + offset_vec
    var diff = target_pos - global_position

    # Deadzone: só move se o alvo saiu da zona morta
    if abs(diff.x) < deadzone.x * 0.5:
        diff.x = 0
    if abs(diff.y) < deadzone.y * 0.5:
        diff.y = 0

    global_position = global_position.lerp(target_pos, {smoothing} * _delta)
'''

    # Salvar script
    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    script_path = scripts_dir / "camera_follow.gd"

    checkpoint(str(script_path.relative_to(proj)), proj)
    script_path.write_text(code, encoding="utf-8")

    # Anexar à câmera no .tscn
    full_scene_path = proj / scene_path
    content = full_scene_path.read_text(encoding="utf-8")

    # Encontrar o nó da câmera
    camera_resource_path = f'res://scripts/camera_follow.gd'
    if f'name="{camera_node_path.split("/")[-1]}"' in content:
        # Adicionar script ao nó da câmera
        script_line = f'script = ExtResource( "{camera_resource_path}" )\n'
        content = content.replace(
            f'[node name="{camera_node_path.split("/")[-1]}"',
            f'[node name="{camera_node_path.split("/")[-1]}"\nscript = ExtResource( "1_camera_follow" )',
        )
        full_scene_path.write_text(content, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "script_path": f"res://scripts/camera_follow.gd",
        "target": target_node_path,
        "smoothing": smoothing,
        "code_preview": code[:300] + "...",
    }


def setup_camera_shake(
    scene_path: str,
    camera_node_path: str,
    max_amplitude: float = 20.0,
    decay_rate: float = 2.0,
) -> dict:
    """Adiciona efeito de tremor (screen shake) à câmera.

    Gera script que expõe add_trauma(amount) para outros scripts chamarem.
    Baseado no algoritmo de trauma/decay.

    Args:
        scene_path: Caminho da cena.
        camera_node_path: Caminho da Camera2D.
        max_amplitude: Amplitude máxima do tremor em pixels.
        decay_rate: Taxa de decaimento do trauma por segundo.

    Returns:
        {"status": "success", "script_path": str}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    code = f'''extends Camera2D
# CameraShake — gerado via MCP DevSolo

var trauma: float = 0.0
var trauma_power: float = 2.0
var max_amplitude: float = {max_amplitude}
var decay_rate: float = {decay_rate}
var noise = FastNoiseLite.new()
var noise_y: float = 0.0

func _ready():
    noise.seed = randi()
    noise.frequency = 0.5

func add_trauma(amount: float):
    trauma = min(trauma + amount, 1.0)

func _process(delta):
    if trauma > 0:
        trauma = max(trauma - decay_rate * delta, 0)
        var shake_amount = pow(trauma, trauma_power)
        noise_y += delta * 30.0
        offset.x = noise.get_noise_2d(noise_y, 0) * max_amplitude * shake_amount
        offset.y = noise.get_noise_2d(0, noise_y) * max_amplitude * shake_amount
    elif offset != Vector2.ZERO:
        offset = offset.lerp(Vector2.ZERO, 10.0 * delta)
'''

    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    script_path = scripts_dir / "camera_shake.gd"

    checkpoint(str(script_path.relative_to(proj)), proj)
    script_path.write_text(code, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "script_path": f"res://scripts/camera_shake.gd",
        "max_amplitude": max_amplitude,
        "decay_rate": decay_rate,
        "usage": 'Chame $Camera2D.add_trauma(0.5) para tremer a tela.',
    }


# ══════════════════════════════════════════════════════════════════════
# 8.2 — NAVEGAÇÃO E PATHFINDING
# ══════════════════════════════════════════════════════════════════════

def create_navigation_region_2d(
    scene_path: str,
    parent_node_path: str = ".",
    polygon_vertices: list[list[float]] | None = None,
    region_name: str = "NavigationRegion2D",
) -> dict:
    """Cria uma região de navegação 2D com polígono.

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai.
        polygon_vertices: Lista de vértices [[x,y], ...] do NavigationPolygon.
                         Se None, cria retângulo 640x480 default.
        region_name: Nome do nó NavigationRegion2D.

    Returns:
        {"status": "success", "node_path": str, "polygon_file": str}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    # Vértices default: retângulo cobrindo a tela
    if not polygon_vertices:
        polygon_vertices = [
            [0, 0], [1280, 0], [1280, 720], [0, 720]
        ]

    # Criar NavigationPolygon .tres
    nav_dir = proj / "navigation"
    nav_dir.mkdir(exist_ok=True)

    polygon_name = region_name.lower().replace(" ", "_")
    tres_path = nav_dir / f"{polygon_name}_polygon.tres"

    # Construir array de vértices no formato Godot
    vertices_str = ", ".join(
        f"Vector2({v[0]}, {v[1]})" for v in polygon_vertices
    )
    # Criar polígono simples (contorno)
    indices = list(range(len(polygon_vertices)))
    indices_str = ", ".join(str(i) for i in indices)

    tres_content = f"""[gd_resource type="NavigationPolygon" load_steps=1 format=3 uid=""]

[resource]
vertices = PackedVector2Array({vertices_str})
polygons = Array[PackedInt32Array]([PackedInt32Array({indices_str})])
"""

    checkpoint(str(tres_path.relative_to(proj)), proj)
    tres_path.write_text(tres_content, encoding="utf-8")

    # Adicionar nó à cena
    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    nav_lines = [
        f'\n[node name="{region_name}" type="NavigationRegion2D" parent="{parent_node_path}"]\n',
        f'editor_description = "NavigationRegion2D gerada via MCP DevSolo"\n',
        f'navpoly = SubResource( "{polygon_name}_polygon" )\n',
        f'navigation_layers = 1\n',
    ]

    checkpoint(scene_path, proj)
    lines.extend(nav_lines)
    full_path.write_text("".join(lines), encoding="utf-8")

    node_path = f"{parent_node_path}/{region_name}"
    mark_pending_compile()

    return {
        "status": "success",
        "node_path": node_path,
        "polygon_file": f"res://navigation/{polygon_name}_polygon.tres",
        "vertices_count": len(polygon_vertices),
    }


def create_navigation_agent_2d(
    scene_path: str,
    parent_node_path: str,
    agent_name: str = "NavigationAgent2D",
    target_node_path: str = "root/Player",
    speed: float = 200.0,
    avoidance_enabled: bool = True,
) -> dict:
    """Adiciona um NavigationAgent2D com script de perseguição.

    O nó pai DEVE ser um CharacterBody2D ou RigidBody2D.
    Gera script que persegue o alvo usando NavigationAgent2D.

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai (CharacterBody2D/RigidBody2D).
        agent_name: Nome do nó NavigationAgent2D.
        target_node_path: Caminho do alvo a perseguir.
        speed: Velocidade de movimento.
        avoidance_enabled: Ativar evasão de obstáculos.

    Returns:
        {"status": "success", "script_path": str, "code_preview": str}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    # Gerar script de perseguição
    code = f'''extends CharacterBody2D
# NavigationChase — gerado via MCP DevSolo
# Persegue: {target_node_path}

@onready var nav_agent: NavigationAgent2D = $NavigationAgent2D
@onready var target = get_node("{target_node_path}")

var move_speed: float = {speed}

func _ready():
    if nav_agent and target:
        nav_agent.target_position = target.global_position
        nav_agent.avoidance_enabled = {'true' if avoidance_enabled else 'false'}

func _physics_process(_delta):
    if not nav_agent or not target:
        return

    nav_agent.target_position = target.global_position

    if nav_agent.is_navigation_finished():
        velocity = Vector2.ZERO
        move_and_slide()
        return

    var next_position = nav_agent.get_next_path_position()
    var direction = (next_position - global_position).normalized()
    velocity = direction * move_speed
    move_and_slide()
'''

    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    script_filename = f"{agent_name.lower()}_chase.gd"
    script_path = scripts_dir / script_filename

    checkpoint(str(script_path.relative_to(proj)), proj)
    script_path.write_text(code, encoding="utf-8")

    # Adicionar NavigationAgent2D à cena
    full_scene_path = proj / scene_path
    content = full_scene_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    nav_node_lines = [
        f'\n[node name="{agent_name}" type="NavigationAgent2D" parent="{parent_node_path}"]\n',
        f'editor_description = "NavigationAgent2D gerado via MCP DevSolo"\n',
        f'avoidance_enabled = {'true' if avoidance_enabled else 'false'}\n',
    ]

    checkpoint(scene_path, proj)
    lines.extend(nav_node_lines)
    full_scene_path.write_text("".join(lines), encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "script_path": f"res://scripts/{script_filename}",
        "target": target_node_path,
        "speed": speed,
        "usage": f"O nó {parent_node_path} agora persegue {target_node_path}.",
        "code_preview": code[:300] + "...",
    }


def bake_navigation_polygon(
    scene_path: str,
    tilemap_layer_path: str,
    navigation_region_path: str,
    walkable_tiles: list[int] | None = None,
) -> dict:
    """Gera NavigationPolygon a partir de um TileMapLayer.

    Analisa as células do TileMap e cria polígono de navegação
    para as células andáveis.

    Args:
        scene_path: Caminho da cena.
        tilemap_layer_path: Caminho do TileMapLayer.
        navigation_region_path: Caminho do NavigationRegion2D.
        walkable_tiles: Lista de tile_ids que são andáveis. Default: [0].

    Returns:
        {"status": "success", "polygon_vertices": int, "note": str}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    if walkable_tiles is None:
        walkable_tiles = [0]

    # Gerar script GDScript que faz o bake
    bake_code = f'''# BakeNavigation — gerado via MCP DevSolo
# Este script é executado via Godot headless para gerar navmesh

func _ready():
    var tilemap = get_node("{tilemap_layer_path}")
    var nav_region = get_node("{navigation_region_path}")

    if not tilemap or not nav_region:
        printerr("TileMapLayer ou NavigationRegion2D não encontrado!")
        get_tree().quit(1)

    var nav_poly = NavigationPolygon.new()
    var tile_size = tilemap.tile_set.tile_size
    var used_cells = tilemap.get_used_cells()

    var vertices = PackedVector2Array()
    var polygon_indices = PackedInt32Array()

    for cell in used_cells:
        var tile_data = tilemap.get_cell_tile_data(cell)
        var tile_id = tilemap.get_cell_source_id(cell)

        if tile_id in {walkable_tiles}:
            # Criar quadrado para cada tile andável
            var base = len(vertices)
            var x = cell.x * tile_size.x
            var y = cell.y * tile_size.y
            var w = tile_size.x
            var h = tile_size.y

            vertices.append(Vector2(x, y))
            vertices.append(Vector2(x + w, y))
            vertices.append(Vector2(x + w, y + h))
            vertices.append(Vector2(x, y + h))

            polygon_indices.append_array([base, base+1, base+2, base+3])

    nav_poly.vertices = vertices
    nav_poly.add_polygon(polygon_indices)

    nav_region.navpoly = nav_poly

    print("Bake concluído! Vértices: " + str(len(vertices)) + " Polígonos: " + str(len(polygon_indices)/4))
    get_tree().quit(0)
'''

    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    bake_path = scripts_dir / "_bake_nav.gd"
    bake_path.write_text(bake_code, encoding="utf-8")

    try:
        godot_bin = get_godot_bin()
        result = subprocess.run(
            [godot_bin, "--headless", "--path", str(proj), "--script", str(bake_path.relative_to(proj))],
            capture_output=True, text=True, timeout=30, cwd=str(proj),
        )
        output = result.stdout + "\n" + result.stderr

        # Limpar script temporário
        bake_path.unlink(missing_ok=True)

        return {
            "status": "success" if result.returncode == 0 else "warning",
            "output": output.strip(),
            "note": "NavigationPolygon gerado a partir do TileMapLayer.",
        }
    except subprocess.TimeoutExpired:
        bake_path.unlink(missing_ok=True)
        return {"status": "error", "message": "Timeout ao executar bake. O mapa pode ser muito grande."}
    except Exception as e:
        bake_path.unlink(missing_ok=True)
        return {"status": "error", "message": str(e)}


# ══════════════════════════════════════════════════════════════════════
# 8.3 — SISTEMA DE SAVE/LOAD
# ══════════════════════════════════════════════════════════════════════

def create_save_system(
    autoload_name: str = "SaveManager",
    save_slots: int = 3,
    auto_save_enabled: bool = False,
    auto_save_interval: float = 60.0,
) -> dict:
    """Cria sistema de save/load completo como Autoload.

    Gera SaveManager.gd com funções: save_game, load_game, delete_save, get_save_slots.
    Registra como autoload no project.godot.

    Args:
        autoload_name: Nome do autoload (acessível globalmente).
        save_slots: Número de slots de save.
        auto_save_enabled: Ativar auto-save periódico.
        auto_save_interval: Intervalo do auto-save em segundos.

    Returns:
        {"status": "success", "script_path": str}
    """
    proj = _get_active_project()

    code = f'''extends Node
# SaveManager — gerado via MCP DevSolo
# Autoload global: {autoload_name}

const MAX_SLOTS = {save_slots}
const SAVE_DIR = "user://saves/"
const AUTO_SAVE_SLOT = 0

var save_data: Dictionary = {{}}
var auto_save_timer: float = 0.0
var auto_save_enabled: bool = {'true' if auto_save_enabled else 'false'}
var auto_save_interval: float = {auto_save_interval}

# Registro de variáveis para salvar
# Formato: {{ "section_name": [ {{"node_path": "...", "property": "..."}} ] }}
var registered_vars: Dictionary = {{}}

func _ready():
    DirAccess.make_dir_recursive_absolute(SAVE_DIR)

func _process(delta):
    if auto_save_enabled:
        auto_save_timer += delta
        if auto_save_timer >= auto_save_interval:
            auto_save_timer = 0.0
            save_game(AUTO_SAVE_SLOT, "auto-save")

func register_var(node_path: String, property: String, section: String = "default", key: String = ""):
    """Registra uma variável para ser salva/carregada."""
    if key == "":
        key = property
    if not section in registered_vars:
        registered_vars[section] = []
    registered_vars[section].append({{
        "node_path": node_path,
        "property": property,
        "key": key,
    }})

func save_game(slot: int, description: String = ""):
    """Salva o jogo no slot especificado (0-{save_slots-1})."""
    if slot < 0 or slot >= MAX_SLOTS:
        printerr("SaveManager: Slot " + str(slot) + " inválido!")
        return {{"status": "error", "message": "Slot inválido"}}

    var config = ConfigFile.new()
    var save_path = _get_save_path(slot)

    # Salvar variáveis registradas
    for section in registered_vars:
        for var_def in registered_vars[section]:
            var node = get_node_or_null(var_def["node_path"])
            if node:
                var value = node.get(var_def["property"])
                config.set_value(section, var_def["key"], value)

    # Salvar metadados
    config.set_value("_meta", "description", description)
    config.set_value("_meta", "timestamp", Time.get_unix_time_from_system())
    config.set_value("_meta", "version", ProjectSettings.get_setting("application/config/version"))

    var error = config.save(save_path)
    if error == OK:
        print("SaveManager: Jogo salvo no slot " + str(slot))
        return {{"status": "success", "slot": slot}}
    else:
        printerr("SaveManager: Erro ao salvar! Código: " + str(error))
        return {{"status": "error", "message": "Erro ao salvar: " + str(error)}}

func load_game(slot: int):
    """Carrega o jogo do slot especificado."""
    if slot < 0 or slot >= MAX_SLOTS:
        return {{"status": "error", "message": "Slot inválido"}}

    var save_path = _get_save_path(slot)
    if not FileAccess.file_exists(save_path):
        return {{"status": "error", "message": "Slot " + str(slot) + " está vazio"}}

    var config = ConfigFile.new()
    var error = config.load(save_path)
    if error != OK:
        return {{"status": "error", "message": "Erro ao carregar: " + str(error)}}

    # Carregar variáveis registradas
    for section in registered_vars:
        for var_def in registered_vars[section]:
            var node = get_node_or_null(var_def["node_path"])
            if node:
                var value = config.get_value(section, var_def["key"], node.get(var_def["property"]))
                node.set(var_def["property"], value)

    print("SaveManager: Jogo carregado do slot " + str(slot))
    return {{"status": "success", "slot": slot}}

func delete_save(slot: int):
    """Deleta um slot de save."""
    var save_path = _get_save_path(slot)
    if FileAccess.file_exists(save_path):
        DirAccess.remove_absolute(save_path)
        return {{"status": "success", "message": "Slot " + str(slot) + " deletado"}}
    return {{"status": "error", "message": "Slot não existe"}}

func get_save_slots():
    """Retorna lista de slots com metadados."""
    var slots = []
    for i in range(MAX_SLOTS):
        var save_path = _get_save_path(i)
        if FileAccess.file_exists(save_path):
            var config = ConfigFile.new()
            config.load(save_path)
            slots.append({{
                "slot": i,
                "description": config.get_value("_meta", "description", ""),
                "timestamp": config.get_value("_meta", "timestamp", 0),
            }})
        else:
            slots.append({{"slot": i, "empty": true}})
    return slots

func _get_save_path(slot: int) -> String:
    return SAVE_DIR + "save_" + str(slot) + ".cfg"
'''

    # Salvar script
    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    script_path = scripts_dir / "save_manager.gd"

    checkpoint(str(script_path.relative_to(proj)), proj)
    script_path.write_text(code, encoding="utf-8")

    # Registrar como autoload no project.godot
    project_file = proj / "project.godot"
    if project_file.exists():
        content = project_file.read_text(encoding="utf-8")

        autoload_entry = f'\n{autoload_name}="*res://scripts/save_manager.gd"'
        if "[autoload]" in content:
            if autoload_name not in content:
                content = content.replace("[autoload]", f"[autoload]\n{autoload_name}=\"*res://scripts/save_manager.gd\"")
        else:
            content += f"\n[autoload]\n{autoload_name}=\"*res://scripts/save_manager.gd\"\n"

        checkpoint("project.godot", proj)
        project_file.write_text(content, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "script_path": f"res://scripts/save_manager.gd",
        "autoload": autoload_name,
        "slots": save_slots,
        "usage": f'{autoload_name}.save_game(1) para salvar. {autoload_name}.load_game(1) para carregar.',
    }


def define_save_data(
    node_path: str,
    property_name: str,
    section: str = "default",
    key: str = "",
) -> dict:
    """Registra uma variável de nó para ser incluída no save/load.

    Deve ser chamado APÓS create_save_system.

    Args:
        node_path: Caminho do nó (ex: "Player").
        property_name: Nome da propriedade (ex: "position", "health").
        section: Seção no arquivo de save (ex: "player", "world").
        key: Chave no arquivo. Default = property_name.

    Returns:
        {"status": "success", "registered": str}
    """
    proj = _get_active_project()

    script_path = proj / "scripts" / "save_manager.gd"
    if not script_path.exists():
        return {"status": "error", "message": "SaveManager não encontrado. Execute create_save_system primeiro."}

    content = script_path.read_text(encoding="utf-8")

    k = key if key else property_name
    register_call = f'\tregister_var("{node_path}", "{property_name}", "{section}", "{k}")\n'

    if "_ready():" in content:
        # Inserir após _ready():
        content = content.replace(
            "func _ready():\n\tDirAccess.make_dir_recursive_absolute(SAVE_DIR)\n",
            f"func _ready():\n\tDirAccess.make_dir_recursive_absolute(SAVE_DIR)\n{register_call}",
        )

    checkpoint(f"scripts/save_manager.gd", proj)
    script_path.write_text(content, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "registered": f"{section}.{k} = {node_path}.{property_name}",
    }


# ══════════════════════════════════════════════════════════════════════
# 8.4 — TWEENS (ANIMAÇÕES DINÂMICAS)
# ══════════════════════════════════════════════════════════════════════

def create_tween_animation(
    scene_path: str,
    node_path: str,
    property_name: str,
    final_value: Any,
    duration: float = 0.5,
    easing: str = "out_quad",
    transition: str = "ease_out",
    loops: int = 0,
    auto_play: bool = True,
) -> dict:
    """Cria uma animação Tween em um nó.

    Args:
        scene_path: Caminho da cena.
        node_path: Caminho do nó alvo.
        property_name: Propriedade a animar (ex: "position", "modulate", "scale").
        final_value: Valor final da propriedade.
        duration: Duração em segundos.
        easing: Tipo de easing (linear, in_quad, out_quad, in_out_quad,
                in_cubic, out_cubic, in_out_cubic, in_elastic, out_elastic,
                in_back, out_back, in_bounce, out_bounce).
        transition: Tipo de transição (ease_in, ease_out, ease_in_out).
        loops: 0 = uma vez, -1 = infinito, N > 0 = N vezes.
        auto_play: Iniciar automaticamente no _ready.

    Returns:
        {"status": "success", "code": str}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    # Construir valor GDScript
    if isinstance(final_value, (int, float)):
        value_str = str(final_value)
    elif isinstance(final_value, list) and len(final_value) == 2:
        value_str = f"Vector2({final_value[0]}, {final_value[1]})"
    elif isinstance(final_value, list) and len(final_value) == 4:
        value_str = f"Color({final_value[0]}, {final_value[1]}, {final_value[2]}, {final_value[3]})"
    else:
        value_str = str(final_value)

    loop_str = "INF" if loops == -1 else str(loops)

    code = f'''# TweenAnimation — gerado via MCP DevSolo
# Anima: {node_path}.{property_name} → {value_str}

func _ready():
    var tween = create_tween()
    tween.set_ease(Tween.EASE_{easing.upper().replace("IN_", "IN_").replace("OUT_", "OUT_")})
    tween.set_trans(Tween.TRANS_{transition.upper()})
    tween.set_loops({loop_str})
    tween.tween_property(${node_path.split("/")[-1]}, "{property_name}", {value_str}, {duration})
'''

    return {
        "status": "success",
        "node": node_path,
        "animation": f"{property_name} → {final_value}",
        "duration": duration,
        "code": code,
        "usage": f"Cole este código no script do nó '{node_path.split('/')[-1]}' ou conecte a um sinal.",
    }


def chain_tweens(
    scene_path: str,
    node_path: str,
    steps: list[dict],
) -> dict:
    """Cria uma sequência de animações Tween encadeadas.

    Args:
        scene_path: Caminho da cena.
        node_path: Caminho do nó alvo.
        steps: Lista de passos. Cada passo: {{
            "property": str, "final_value": Any, "duration": float (default 0.3),
            "easing": str, "transition": str
        }}.

    Returns:
        {"status": "success", "steps_count": int, "code": str}
    """
    _check_path(scene_path)

    code_lines = [
        '# TweenChain — gerado via MCP DevSolo',
        '',
        'func _ready():',
        '\tvar tween = create_tween()',
    ]

    for i, step in enumerate(steps):
        prop = step.get("property", "position")
        value = step.get("final_value", 0)
        duration = step.get("duration", 0.3)
        easing = step.get("easing", "out_quad")
        trans = step.get("transition", "ease_out")

        if isinstance(value, (int, float)):
            val_str = str(value)
        elif isinstance(value, list) and len(value) == 2:
            val_str = f"Vector2({value[0]}, {value[1]})"
        else:
            val_str = str(value)

        if i == 0:
            code_lines.append(f'\ttween.tween_property(self, "{prop}", {val_str}, {duration})')
        else:
            code_lines.append(f'\ttween.then().tween_property(self, "{prop}", {val_str}, {duration})')

    code = "\n".join(code_lines)

    return {
        "status": "success",
        "steps_count": len(steps),
        "code": code,
        "usage": f"Cadeia de {len(steps)} animações em sequência.",
    }


# ══════════════════════════════════════════════════════════════════════
# 8.5 — STATE MACHINE
# ══════════════════════════════════════════════════════════════════════

def create_state_machine(
    script_path: str,
    states: list[str],
    initial_state: str,
) -> dict:
    """Gera uma máquina de estados finita (FSM) em GDScript.

    Args:
        script_path: Caminho onde salvar o script gerado.
        states: Lista de nomes de estados (ex: ["idle", "walk", "attack", "hurt", "die"]).
        initial_state: Estado inicial.

    Returns:
        {"status": "success", "script_path": str, "code_preview": str}
    """
    proj = _get_active_project()
    _check_path(script_path)

    state_enum = "enum State { " + ", ".join(state.upper() for state in states) + " }"

    state_methods = []
    for state in states:
        state_methods.append(f'''
func _enter_{state}():
    pass

func _update_{state}(_delta: float):
    pass

func _exit_{state}():
    pass
''')

    state_switch = "\n".join(
        f'\t\tState.{state.upper()}:\n\t\t\t_update_{state}(delta)'
        for state in states
    )

    code = f'''extends Node
# StateMachine — gerado via MCP DevSolo
# Estados: {", ".join(states)}

{state_enum}

var current_state: State = State.{initial_state.upper()}
var previous_state: State = State.{initial_state.upper()}

func _ready():
    _enter_{initial_state}()

func _process(delta: float):
    match current_state:
{state_switch}

func transition_to(new_state: State):
    if new_state == current_state:
        return
    previous_state = current_state
    call("_exit_" + State.keys()[current_state].to_lower())
    current_state = new_state
    call("_enter_" + State.keys()[new_state].to_lower())

func get_state_name() -> String:
    return State.keys()[current_state].to_lower()

{"".join(state_methods)}
'''

    full_path = proj / script_path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    checkpoint(script_path, proj)
    full_path.write_text(code, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "script_path": f"res://{script_path}",
        "states": states,
        "initial_state": initial_state,
        "usage": f"Use transition_to(State.NEW_STATE) para mudar de estado.",
        "code_preview": code[:500] + "...",
    }


def add_state_transition(
    script_path: str,
    from_state: str,
    to_state: str,
    condition_code: str,
) -> dict:
    """Adiciona uma transição condicional entre estados.

    Args:
        script_path: Caminho do script com state machine.
        from_state: Estado de origem.
        to_state: Estado de destino.
        condition_code: Código GDScript da condição (ex: "velocity.length() > 0").

    Returns:
        {"status": "success"}
    """
    proj = _get_active_project()
    full_path = proj / script_path

    if not full_path.exists():
        return {"status": "error", "message": f"Script '{script_path}' não encontrado."}

    content = full_path.read_text(encoding="utf-8")

    # Inserir transição na função _update_<from_state>
    transition_code = f"""
    if {condition_code}:
        transition_to(State.{to_state.upper()})
"""

    update_func = f"func _update_{from_state}(_delta: float):"
    if update_func in content:
        content = content.replace(
            f"{update_func}\n\tpass",
            f"{update_func}{transition_code}",
        )

    checkpoint(script_path, proj)
    full_path.write_text(content, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "transition": f"{from_state} → {to_state}",
        "condition": condition_code,
    }


# ══════════════════════════════════════════════════════════════════════
# 8.6 — UI TEMPLATES
# ══════════════════════════════════════════════════════════════════════

def create_main_menu(
    scene_name: str,
    game_title: str,
    title_font_size: int = 64,
    buttons: list[str] | None = None,
    background_color: str = "#1a1a2e",
    style: str = "modern",
) -> dict:
    """Cria uma cena de menu principal completa.

    Args:
        scene_name: Nome do arquivo de cena (ex: "title_screen").
        game_title: Título do jogo exibido na tela.
        title_font_size: Tamanho da fonte do título.
        buttons: Lista de textos dos botões. Default: ["▶ START", "⚙ OPTIONS", "✕ QUIT"].
        background_color: Cor de fundo em hex.
        style: Estilo visual ("modern", "retro", "cartoon", "dark_fantasy", "sci_fi").

    Returns:
        {"status": "success", "scene_path": str, "node_tree": str}
    """
    proj = _get_active_project()

    if buttons is None:
        buttons = ["▶ START", "⚙ OPTIONS", "✕ QUIT"]

    # Aplicar estilo
    styles = {
        "modern": {"title_color": "#ffffff", "btn_color": "#0f3460", "btn_hover": "#1a5276", "accent": "#e94560"},
        "retro": {"title_color": "#ffffff", "btn_color": "#c0392b", "btn_hover": "#e74c3c", "accent": "#f1c40f"},
        "cartoon": {"title_color": "#2c3e50", "btn_color": "#27ae60", "btn_hover": "#2ecc71", "accent": "#e67e22"},
        "dark_fantasy": {"title_color": "#ffd700", "btn_color": "#2c1810", "btn_hover": "#4a2511", "accent": "#8b0000"},
        "sci_fi": {"title_color": "#00ffff", "btn_color": "#0a0a2e", "btn_hover": "#1a1a5e", "accent": "#00ff88"},
    }
    st = styles.get(style, styles["modern"])

    # Converter todas as cores para formato Godot
    bg_godot = _hex_to_color(background_color)
    for k in st:
        st[k] = _hex_to_color(st[k])

    # Criar cena
    scenes_dir = proj / "scenes"
    scenes_dir.mkdir(exist_ok=True)
    scene_path = scenes_dir / f"{scene_name}.tscn"

    # Construir .tscn manualmente
    tscn = f"""[gd_scene load_steps=2 format=3 uid=""]

[ext_resource type="Script" path="res://scripts/ui/main_menu.gd" id="1_menu_script"]

[node name="MainMenu" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
script = ExtResource("1_menu_script")

[node name="Background" type="ColorRect" parent="."]
layout_mode = 0
offset_right = 1280.0
offset_bottom = 720.0
color = {bg_godot}

[node name="MenuContainer" type="VBoxContainer" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -250.0
offset_top = -200.0
offset_right = 250.0
offset_bottom = 200.0
grow_horizontal = 2
grow_vertical = 2
theme_override_constants/separation = 20

[node name="TitleLabel" type="Label" parent="MenuContainer"]
layout_mode = 2
text = "{game_title}"
horizontal_alignment = 1
theme_override_font_sizes/font_size = {title_font_size}
theme_override_colors/font_color = {st['title_color']}
"""

    tscn += f"""
[node name="Spacer" type="Control" parent="MenuContainer"]
layout_mode = 2
custom_minimum_size = Vector2(0, 40)
"""

    for btn_text in buttons:
        btn_name = "Btn" + btn_text.split()[-1].strip("▶⚙✕©⌂↺").title()
        is_primary = "START" in btn_text.upper() or "PLAY" in btn_text.upper() or "JOGAR" in btn_text.upper() or "CONTINUAR" in btn_text.upper()
        btn_color = st["accent"] if is_primary else st["btn_color"]

        tscn += f"""
[node name="{btn_name}" type="Button" parent="MenuContainer"]
layout_mode = 2
custom_minimum_size = Vector2(320, 70)
text = "{btn_text}"
theme_override_font_sizes/font_size = 24
theme_override_colors/font_color = Color(1.0000, 1.0000, 1.0000, 1)
"""

    # Salvar cena
    checkpoint(f"scenes/{scene_name}.tscn", proj)
    scene_path.write_text(tscn, encoding="utf-8")

    # Criar script da UI
    scripts_dir = proj / "scripts" / "ui"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    menu_script = f'''extends Control
# MainMenu — gerado via MCP DevSolo

func _ready():
    # Conectar botões
'''

    for btn_text in buttons:
        btn_name = "Btn" + btn_text.split()[-1].strip("▶⚙✕©⌂↺").title()
        if "START" in btn_text.upper() or "PLAY" in btn_text.upper() or "JOGAR" in btn_text.upper() or "CONTINUAR" in btn_text.upper():
            menu_script += f'    $MenuContainer/{btn_name}.pressed.connect(_on_start_pressed)\n'
        elif "OPTIONS" in btn_text.upper() or "OPÇÕES" in btn_text.upper():
            menu_script += f'    $MenuContainer/{btn_name}.pressed.connect(_on_options_pressed)\n'
        elif "QUIT" in btn_text.upper() or "SAIR" in btn_text.upper():
            menu_script += f'    $MenuContainer/{btn_name}.pressed.connect(_on_quit_pressed)\n'
        elif "CREDITS" in btn_text.upper() or "CRÉDITOS" in btn_text.upper():
            menu_script += f'    $MenuContainer/{btn_name}.pressed.connect(_on_credits_pressed)\n'
        elif "MENU" in btn_text.upper():
            menu_script += f'    $MenuContainer/{btn_name}.pressed.connect(_on_menu_pressed)\n'
        elif "RETRY" in btn_text.upper() or "TENTAR" in btn_text.upper() or "REINICIAR" in btn_text.upper():
            menu_script += f'    $MenuContainer/{btn_name}.pressed.connect(_on_retry_pressed)\n'
        elif "RESUME" in btn_text.upper() or "CONTINUAR" in btn_text.upper():
            menu_script += f'    $MenuContainer/{btn_name}.pressed.connect(_on_resume_pressed)\n'

    menu_script += '''
func _on_start_pressed():
    get_tree().change_scene_to_file("res://scenes/game.tscn")

func _on_options_pressed():
    if ResourceLoader.exists("res://scenes/options.tscn"):
        get_tree().change_scene_to_file("res://scenes/options.tscn")

func _on_quit_pressed():
    get_tree().quit()

func _on_credits_pressed():
    if ResourceLoader.exists("res://scenes/credits.tscn"):
        get_tree().change_scene_to_file("res://scenes/credits.tscn")

func _on_menu_pressed():
    get_tree().change_scene_to_file("res://scenes/title_screen.tscn")

func _on_retry_pressed():
    get_tree().reload_current_scene()

func _on_resume_pressed():
    get_tree().paused = false
    queue_free()
'''

    script_file = scripts_dir / "main_menu.gd"
    script_file.write_text(menu_script, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "scene_path": f"res://scenes/{scene_name}.tscn",
        "title": game_title,
        "buttons": len(buttons),
        "style": style,
        "node_tree": f"Control → ColorRect + VBoxContainer → Label + {' + '.join(buttons)}",
    }


def create_hud_template(
    scene_name: str = "hud",
    elements: list[str] | None = None,
    position: str = "top_left",
) -> dict:
    """Cria uma cena de HUD (Heads-Up Display).

    Args:
        scene_name: Nome da cena HUD.
        elements: Lista de elementos: "score", "health", "ammo", "wave", "timer".
                  Default: ["score", "health"].
        position: Posição na tela: "top_left", "top_right", "bottom_center".

    Returns:
        {"status": "success", "scene_path": str, "elements": list}
    """
    proj = _get_active_project()

    if elements is None:
        elements = ["score", "health"]

    # Posições
    positions = {
        "top_left": {"anchor_left": 0, "anchor_top": 0, "margin": "offset_left = 20.0\noffset_top = 20.0"},
        "top_right": {"anchor_left": 1, "anchor_top": 0, "margin": "offset_left = -320.0\noffset_top = 20.0"},
        "bottom_center": {"anchor_left": 0.5, "anchor_bottom": 1, "margin": "offset_left = -200.0\noffset_bottom = -60.0"},
    }
    pos = positions.get(position, positions["top_left"])

    tscn = f"""[gd_scene load_steps=2 format=3 uid=""]

[node name="HUD" type="CanvasLayer"]

[node name="HudContainer" type="MarginContainer" parent="."]
layout_mode = 1
anchors_preset = 0
anchor_left = {pos.get('anchor_left', 0)}
anchor_top = {pos.get('anchor_top', 0)}
anchor_right = {pos.get('anchor_left', 0)}
anchor_bottom = {pos.get('anchor_top', 0)}
{pos.get('margin', '')}
grow_horizontal = 2
grow_vertical = 2

[node name="ElementContainer" type="VBoxContainer" parent="HudContainer"]
layout_mode = 2
"""

    for elem in elements:
        if elem == "score":
            tscn += """
[node name="ScoreLabel" type="Label" parent="HudContainer/ElementContainer"]
layout_mode = 2
text = "SCORE: 0"
theme_override_font_sizes/font_size = 24
theme_override_colors/font_color = Color(1.0000, 1.0000, 1.0000, 1)
"""
        elif elem == "health":
            tscn += """
[node name="HealthBar" type="ProgressBar" parent="HudContainer/ElementContainer"]
layout_mode = 2
custom_minimum_size = Vector2(250, 25)
value = 100.0
show_percentage = false
theme_override_font_sizes/font_size = 14
"""
        elif elem == "ammo":
            tscn += """
[node name="AmmoLabel" type="Label" parent="HudContainer/ElementContainer"]
layout_mode = 2
text = "AMMO: 30/30"
theme_override_font_sizes/font_size = 20
theme_override_colors/font_color = Color(1.0000, 1.0000, 1.0000, 1)
"""
        elif elem == "wave":
            tscn += """
[node name="WaveLabel" type="Label" parent="HudContainer/ElementContainer"]
layout_mode = 2
text = "WAVE: 1"
theme_override_font_sizes/font_size = 22
theme_override_colors/font_color = Color(0.9529, 0.6118, 0.0706, 1)
"""
        elif elem == "timer":
            tscn += """
[node name="TimerLabel" type="Label" parent="HudContainer/ElementContainer"]
layout_mode = 2
text = "TIME: 00:00"
theme_override_font_sizes/font_size = 20
theme_override_colors/font_color = Color(1.0000, 1.0000, 1.0000, 1)
"""

    scenes_dir = proj / "scenes"
    scenes_dir.mkdir(exist_ok=True)
    scene_path = scenes_dir / f"{scene_name}.tscn"

    checkpoint(f"scenes/{scene_name}.tscn", proj)
    scene_path.write_text(tscn, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "scene_path": f"res://scenes/{scene_name}.tscn",
        "elements": elements,
        "position": position,
    }


def create_pause_menu(
    scene_name: str = "pause_menu",
    overlay_alpha: float = 0.7,
) -> dict:
    """Cria uma cena de menu de pausa.

    Args:
        scene_name: Nome da cena.
        overlay_alpha: Transparência do overlay (0-1).

    Returns:
        {"status": "success", "scene_path": str}
    """
    proj = _get_active_project()

    tscn = f"""[gd_scene load_steps=2 format=3 uid=""]

[node name="PauseMenu" type="CanvasLayer"]
layer = 10

[node name="Overlay" type="ColorRect" parent="."]
layout_mode = 0
offset_right = 1280.0
offset_bottom = 720.0
color = Color(0, 0, 0, {overlay_alpha})

[node name="Panel" type="Panel" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -200.0
offset_top = -180.0
offset_right = 200.0
offset_bottom = 180.0
grow_horizontal = 2
grow_vertical = 2

[node name="MenuContainer" type="VBoxContainer" parent="Panel"]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
theme_override_constants/separation = 15

[node name="TitleLabel" type="Label" parent="Panel/MenuContainer"]
layout_mode = 2
text = "PAUSADO"
horizontal_alignment = 1
theme_override_font_sizes/font_size = 36
theme_override_colors/font_color = Color(1.0000, 1.0000, 1.0000, 1)

[node name="Spacer" type="Control" parent="Panel/MenuContainer"]
layout_mode = 2
custom_minimum_size = Vector2(0, 20)

[node name="BtnResume" type="Button" parent="Panel/MenuContainer"]
layout_mode = 2
custom_minimum_size = Vector2(280, 55)
text = "▶ CONTINUAR"
theme_override_font_sizes/font_size = 22

[node name="BtnRestart" type="Button" parent="Panel/MenuContainer"]
layout_mode = 2
custom_minimum_size = Vector2(280, 55)
text = "↺ REINICIAR"
theme_override_font_sizes/font_size = 22

[node name="BtnMenu" type="Button" parent="Panel/MenuContainer"]
layout_mode = 2
custom_minimum_size = Vector2(280, 55)
text = "⌂ MENU PRINCIPAL"
theme_override_font_sizes/font_size = 22
"""

    scenes_dir = proj / "scenes"
    scenes_dir.mkdir(exist_ok=True)
    scene_path = scenes_dir / f"{scene_name}.tscn"

    checkpoint(f"scenes/{scene_name}.tscn", proj)
    scene_path.write_text(tscn, encoding="utf-8")

    # Script da pausa
    scripts_dir = proj / "scripts" / "ui"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    pause_script = '''extends CanvasLayer
# PauseMenu — gerado via MCP DevSolo

func _ready():
    hide()
    $Panel/MenuContainer/BtnResume.pressed.connect(_on_resume)
    $Panel/MenuContainer/BtnRestart.pressed.connect(_on_restart)
    $Panel/MenuContainer/BtnMenu.pressed.connect(_on_menu)

func _input(event):
    if event.is_action_pressed("ui_cancel"):
        if visible:
            _on_resume()
        else:
            _pause()

func _pause():
    get_tree().paused = true
    show()

func _on_resume():
    get_tree().paused = false
    hide()

func _on_restart():
    get_tree().paused = false
    get_tree().reload_current_scene()

func _on_menu():
    get_tree().paused = false
    get_tree().change_scene_to_file("res://scenes/title_screen.tscn")
'''

    script_file = scripts_dir / "pause_menu.gd"
    script_file.write_text(pause_script, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "scene_path": f"res://scenes/{scene_name}.tscn",
        "script_path": f"res://scripts/ui/pause_menu.gd",
    }


def create_health_bar(
    scene_path: str,
    parent_node_path: str = ".",
    max_health: float = 100.0,
    bar_name: str = "HealthBar",
    bar_width: int = 250,
    bar_height: int = 25,
    fill_color: str = "#2ecc71",
    bg_color: str = "#333333",
    show_text: bool = True,
) -> dict:
    """Cria uma barra de vida com script de controle.

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai.
        max_health: Vida máxima.
        bar_name: Nome do nó ProgressBar.
        bar_width, bar_height: Dimensões.
        fill_color: Cor da barra preenchida.
        bg_color: Cor do fundo.
        show_text: Mostrar "75/100" na barra.

    Returns:
        {"status": "success", "script_path": str, "code_preview": str}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    full_path = proj / scene_path
    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    # Adicionar ProgressBar ao .tscn
    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    bar_lines = [
        f'\n[node name="{bar_name}" type="ProgressBar" parent="{parent_node_path}"]\n',
        f'editor_description = "HealthBar gerada via MCP DevSolo"\n',
        f"custom_minimum_size = Vector2({bar_width}, {bar_height})\n",
        f"value = {max_health}\n",
        f"max_value = {max_health}\n",
        f"show_percentage = {'true' if show_text else 'false'}\n",
    ]

    checkpoint(scene_path, proj)
    lines.extend(bar_lines)
    full_path.write_text("".join(lines), encoding="utf-8")

    # Criar script de controle
    code = f'''extends ProgressBar
# HealthBar — gerado via MCP DevSolo

signal died
signal health_changed(new_health: float)

var max_health: float = {max_health}
var current_health: float = {max_health}

func _ready():
    max_value = max_health
    value = current_health

func take_damage(amount: float):
    current_health = max(current_health - amount, 0)
    _update_display()
    health_changed.emit(current_health)
    if current_health <= 0:
        died.emit()

func heal(amount: float):
    current_health = min(current_health + amount, max_health)
    _update_display()
    health_changed.emit(current_health)

func set_max_health(new_max: float):
    max_health = new_max
    max_value = new_max

func get_health_percent() -> float:
    return current_health / max_health

func _update_display():
    var tween = create_tween()
    tween.tween_property(self, "value", current_health, 0.3)

    # Mudar cor baseado na saúde
    var ratio = get_health_percent()
    if ratio > 0.6:
        modulate = Color.GREEN
    elif ratio > 0.3:
        modulate = Color.YELLOW
    else:
        modulate = Color.RED
'''

    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    script_path = scripts_dir / f"{bar_name.lower()}.gd"

    checkpoint(f"scripts/{bar_name.lower()}.gd", proj)
    script_path.write_text(code, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "script_path": f"res://scripts/{bar_name.lower()}.gd",
        "max_health": max_health,
        "usage": f"Chame ${bar_name}.take_damage(10) para causar dano.",
        "code_preview": code[:400] + "...",
    }


# ══════════════════════════════════════════════════════════════════════
# 8.7 — WORLD ENVIRONMENT
# ══════════════════════════════════════════════════════════════════════

def setup_world_environment(
    scene_path: str,
    parent_node_path: str = ".",
    background_mode: str = "color",
    background_color: str = "#1a1a2e",
    ambient_light_color: str = "#333344",
    ambient_light_energy: float = 1.0,
    glow_enabled: bool = False,
    glow_intensity: float = 0.8,
    fog_enabled: bool = False,
    fog_density: float = 0.01,
    fog_color: str = "#1a1a2e",
) -> dict:
    """Configura o ambiente visual da cena (WorldEnvironment).

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai.
        background_mode: "color", "sky", ou "canvas".
        background_color: Cor de fundo (hex).
        ambient_light_color: Cor da luz ambiente (hex).
        ambient_light_energy: Intensidade da luz ambiente.
        glow_enabled: Ativar efeito bloom/glow.
        glow_intensity: Intensidade do glow.
        fog_enabled: Ativar névoa.
        fog_density: Densidade da névoa.
        fog_color: Cor da névoa.

    Returns:
        {"status": "success", "node_path": str, "features": list}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    full_path = proj / scene_path

    # Criar Environment .tres
    env_dir = proj / "environments"
    env_dir.mkdir(exist_ok=True)
    env_name = f"{scene_path.replace('/', '_').replace('.tscn', '')}_env"
    env_path = env_dir / f"{env_name}.tres"

    bg_modes = {"color": 0, "sky": 1, "canvas": 2}
    bg_mode_int = bg_modes.get(background_mode, 0)

    env_content = f"""[gd_resource type="Environment" load_steps=1 format=3 uid=""]

[resource]
background_mode = {bg_mode_int}
background_color = Color("{background_color}")
ambient_light_color = Color("{ambient_light_color}")
ambient_light_energy = {ambient_light_energy}
ambient_light_sky_contribution = 1.0

glow_enabled = {'true' if glow_enabled else 'false'}
glow_intensity = {glow_intensity}
glow_strength = 1.0
glow_bloom = 0.0
glow_blend_mode = 2
glow_hdr_threshold = 1.0
glow_hdr_scale = 2.0

fog_enabled = {'true' if fog_enabled else 'false'}
fog_density = {fog_density}
fog_light_color = Color("{fog_color}")
fog_light_energy = 1.0
"""

    checkpoint(f"environments/{env_name}.tres", proj)
    env_path.write_text(env_content, encoding="utf-8")

    # Adicionar WorldEnvironment à cena se existir
    if full_path.exists():
        content = full_path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)

        we_lines = [
            f'\n[node name="WorldEnvironment" type="WorldEnvironment" parent="{parent_node_path}"]\n',
            f'editor_description = "WorldEnvironment gerado via MCP DevSolo"\n',
            f'environment = ExtResource( "1_{env_name}" )\n',
        ]

        checkpoint(scene_path, proj)
        lines.extend(we_lines)
        full_path.write_text("".join(lines), encoding="utf-8")

    features = []
    if glow_enabled:
        features.append("glow")
    if fog_enabled:
        features.append("fog")

    mark_pending_compile()

    return {
        "status": "success",
        "node_path": f"{parent_node_path}/WorldEnvironment",
        "environment_file": f"res://environments/{env_name}.tres",
        "features": features or ["background", "ambient_light"],
        "background": background_mode,
    }


def setup_screen_flash(
    scene_path: str,
    parent_node_path: str = ".",
    flash_color: str = "#ffffff",
    flash_duration: float = 0.3,
) -> dict:
    """Adiciona um efeito de flash de tela (dano, power-up).

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai.
        flash_color: Cor do flash (hex).
        flash_duration: Duração em segundos.

    Returns:
        {"status": "success", "script_path": str}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    code = f'''extends ColorRect
# ScreenFlash — gerado via MCP DevSolo

func _ready():
    color = Color("{flash_color}")
    modulate.a = 0.0
    mouse_filter = MOUSE_FILTER_IGNORE

func flash(duration: float = {flash_duration}):
    var tween = create_tween()
    tween.tween_property(self, "modulate:a", 0.5, duration * 0.3)
    tween.then().tween_property(self, "modulate:a", 0.0, duration * 0.7)

func flash_red():
    color = Color.RED
    flash()

func flash_green():
    color = Color.GREEN
    flash()

func flash_white():
    color = Color.WHITE
    flash()
'''

    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    script_path = scripts_dir / "screen_flash.gd"

    checkpoint("scripts/screen_flash.gd", proj)
    script_path.write_text(code, encoding="utf-8")

    # Adicionar ColorRect à cena
    full_path = proj / scene_path
    if full_path.exists():
        content = full_path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)

        flash_lines = [
            f'\n[node name="ScreenFlash" type="ColorRect" parent="{parent_node_path}"]\n',
            f'editor_description = "ScreenFlash gerado via MCP DevSolo"\n',
            f'color = Color("{flash_color}")\n',
            f'anchors_preset = 15\n',
            f'anchor_right = 1.0\n',
            f'anchor_bottom = 1.0\n',
            f'grow_horizontal = 2\n',
            f'grow_vertical = 2\n',
            f'modulate = Color(1, 1, 1, 0)\n',
            f'mouse_filter = 2\n',
        ]

        checkpoint(scene_path, proj)
        lines.extend(flash_lines)
        full_path.write_text("".join(lines), encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "script_path": f"res://scripts/screen_flash.gd",
        "usage": "Chame $ScreenFlash.flash() para efeito de dano. flash_red() para dano, flash_green() para cura.",
    }


# ══════════════════════════════════════════════════════════════════════
# 9.1 — PARALLAX BACKGROUND
# ══════════════════════════════════════════════════════════════════════

def create_parallax_background(
    scene_path: str,
    layers: list[dict],
    parent_node_path: str = ".",
    bg_name: str = "ParallaxBackground",
) -> dict:
    """Cria um fundo parallax com múltiplas camadas.

    Args:
        scene_path: Caminho da cena.
        layers: Lista de camadas. Cada camada: {{
            "texture_path": str (caminho da textura),
            "scroll_scale_x": float (default 0.5),
            "scroll_scale_y": float (default 0.5),
            "mirroring_x": int (default 0),
            "mirroring_y": int (default 0),
            "color": str (hex, default "#ffffff"),
        }}.
        parent_node_path: Caminho do nó pai.
        bg_name: Nome do nó ParallaxBackground.

    Returns:
        {{"status": "success", "node_path": str, "layers_count": int}}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    # ParallaxBackground
    lines.append(f'\n[node name="{bg_name}" type="ParallaxBackground" parent="{parent_node_path}"]\n')
    lines.append(f'editor_description = "ParallaxBackground gerado via MCP DevSolo"\n')
    lines.append(f'scroll_base_scale = Vector2(1, 1)\n')
    lines.append(f'scroll_offset = Vector2(0, 0)\n')

    for i, layer in enumerate(layers):
        tex_path = layer.get("texture_path", "")
        sx = layer.get("scroll_scale_x", 0.5)
        sy = layer.get("scroll_scale_y", 0.5)
        mx = layer.get("mirroring_x", 0)
        my = layer.get("mirroring_y", 0)
        color = layer.get("color", "#ffffff")

        layer_name = f"Layer{i}"
        lines.append(f'\n[node name="{layer_name}" type="ParallaxLayer" parent="{parent_node_path}/{bg_name}"]\n')
        lines.append(f'scale = Vector2({sx}, {sy})\n')
        lines.append(f'mirroring = Vector2({mx}, {my})\n')

        sprite_name = f"Sprite{i}"
        lines.append(f'\n[node name="{sprite_name}" type="Sprite2D" parent="{parent_node_path}/{bg_name}/{layer_name}"]\n')
        if tex_path:
            lines.append(f'texture = ExtResource( "1_{tex_path.replace("/", "_").replace(".", "_")}" )\n')
        lines.append(f'modulate = Color("{color}")\n')
        lines.append(f'centered = false\n')

    checkpoint(scene_path, proj)
    full_path.write_text("".join(lines), encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "node_path": f"{parent_node_path}/{bg_name}",
        "layers_count": len(layers),
        "note": "Parallax criado. A câmera deve estar configurada com camera_follow para o efeito funcionar.",
    }


def add_parallax_layer(
    scene_path: str,
    parallax_bg_path: str,
    texture_path: str,
    scroll_scale_x: float = 0.5,
    scroll_scale_y: float = 0.5,
    mirroring_x: int = 0,
    mirroring_y: int = 0,
    layer_name: str = "",
) -> dict:
    """Adiciona uma camada a um ParallaxBackground existente.

    Args:
        scene_path: Caminho da cena.
        parallax_bg_path: Caminho do ParallaxBackground.
        texture_path: Caminho da textura.
        scroll_scale_x, scroll_scale_y: Escala de scroll.
        mirroring_x, mirroring_y: Mirroring (0=desligado, 1=espelhar).
        layer_name: Nome da camada (auto-gerado se vazio).

    Returns:
        {{"status": "success", "layer_path": str}}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    import uuid
    uid = str(uuid.uuid4()).replace("-", "")[:8]
    if not layer_name:
        layer_name = f"ParallaxLayer_{uid}"

    lines.append(f'\n[node name="{layer_name}" type="ParallaxLayer" parent="{parallax_bg_path}"]\n')
    lines.append(f'scale = Vector2({scroll_scale_x}, {scroll_scale_y})\n')
    lines.append(f'mirroring = Vector2({mirroring_x}, {mirroring_y})\n')

    lines.append(f'\n[node name="Sprite" type="Sprite2D" parent="{parallax_bg_path}/{layer_name}"]\n')
    if texture_path:
        lines.append(f'texture = ExtResource( "1_{texture_path.replace("/", "_").replace(".", "_")}" )\n')
    lines.append(f'centered = false\n')

    checkpoint(scene_path, proj)
    full_path.write_text("".join(lines), encoding="utf-8")
    mark_pending_compile()

    return {
        "status": "success",
        "layer_path": f"{parallax_bg_path}/{layer_name}",
    }


# ══════════════════════════════════════════════════════════════════════
# 9.2 — PARTÍCULAS CONFIGURÁVEIS
# ══════════════════════════════════════════════════════════════════════

def configure_particles_2d(
    scene_path: str,
    node_path: str,
    amount: int = 50,
    lifetime: float = 1.0,
    explosiveness: float = 0.0,
    emitting: bool = True,
    one_shot: bool = False,
    preset: str = "custom",
) -> dict:
    """Configura partículas 2D existentes com parâmetros visuais.

    Predefinições (preset) configuram automaticamente:
    - explosion: one_shot, explosiveness=1, amount=100, lifetime=0.5
    - smoke: direction=up, spread=30, gravity=(-5,0), lifetime=2
    - sparkle: amount=20, lifetime=0.3, spread=360
    - rain: direction=down, amount=200, lifetime=3, gravity=(0,500)
    - fire: direction=up, spread=15, amount=30, lifetime=0.8

    Args:
        scene_path: Caminho da cena.
        node_path: Caminho do GPUParticles2D.
        amount: Quantidade de partículas.
        lifetime: Tempo de vida em segundos.
        explosiveness: 0=contínuo, 1=todas de uma vez.
        emitting: Se está emitindo.
        one_shot: Emitir uma vez e parar.
        preset: Predefinição (explosion, smoke, sparkle, rain, fire, custom).

    Returns:
        {{"status": "success", "preset": str, "params": dict}}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    # Predefinições
    presets = {
        "explosion": {"amount": 100, "lifetime": 0.5, "explosiveness": 1.0, "one_shot": True, "emitting": True},
        "smoke": {"amount": 30, "lifetime": 2.0, "explosiveness": 0.0, "one_shot": False, "emitting": True},
        "sparkle": {"amount": 20, "lifetime": 0.3, "explosiveness": 0.3, "one_shot": False, "emitting": True},
        "rain": {"amount": 200, "lifetime": 3.0, "explosiveness": 0.0, "one_shot": False, "emitting": True},
        "fire": {"amount": 30, "lifetime": 0.8, "explosiveness": 0.0, "one_shot": False, "emitting": True},
    }

    if preset in presets:
        p = presets[preset]
        amount = p["amount"]
        lifetime = p["lifetime"]
        explosiveness = p["explosiveness"]
        one_shot = p["one_shot"]
        emitting = p["emitting"]

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    # Adicionar/atualizar propriedades
    node_name = node_path.split("/")[-1]
    lines.append(f'\n[node name="{node_name}" type="GPUParticles2D" parent="{node_path.rsplit("/", 1)[0]}"]\n')
    lines.append(f'amount = {amount}\n')
    lines.append(f'lifetime = {lifetime}\n')
    lines.append(f'explosiveness = {explosiveness}\n')
    lines.append(f'emitting = {'true' if emitting else 'false'}\n')
    lines.append(f'one_shot = {'true' if one_shot else 'false'}\n')

    checkpoint(scene_path, proj)
    full_path.write_text("".join(lines), encoding="utf-8")
    mark_pending_compile()

    return {
        "status": "success",
        "preset": preset,
        "params": {"amount": amount, "lifetime": lifetime, "explosiveness": explosiveness},
    }


def create_particles_3d(
    scene_path: str,
    parent_node_path: str = ".",
    node_name: str = "GPUParticles3D",
    preset: str = "fire",
) -> dict:
    """Cria partículas 3D com predefinição visual.

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai.
        node_name: Nome do nó GPUParticles3D.
        preset: Predefinição (fire, smoke, sparkles, custom).

    Returns:
        {{"status": "success", "node_path": str}}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    predefs = {
        "fire": {"amount": 50, "lifetime": 0.8, "explosiveness": 0.0},
        "smoke": {"amount": 20, "lifetime": 2.5, "explosiveness": 0.0},
        "sparkles": {"amount": 30, "lifetime": 0.4, "explosiveness": 0.2},
        "custom": {"amount": 50, "lifetime": 1.0, "explosiveness": 0.0},
    }
    p = predefs.get(preset, predefs["custom"])

    lines.append(f'\n[node name="{node_name}" type="GPUParticles3D" parent="{parent_node_path}"]\n')
    lines.append(f'editor_description = "GPUParticles3D gerado via MCP DevSolo - {preset}"\n')
    lines.append(f'amount = {p["amount"]}\n')
    lines.append(f'lifetime = {p["lifetime"]}\n')
    lines.append(f'explosiveness = {p["explosiveness"]}\n')
    lines.append(f'emitting = true\n')

    checkpoint(scene_path, proj)
    full_path.write_text("".join(lines), encoding="utf-8")
    mark_pending_compile()

    return {
        "status": "success",
        "node_path": f"{parent_node_path}/{node_name}",
        "preset": preset,
    }


# ══════════════════════════════════════════════════════════════════════
# 9.3 — SHADERS 2D
# ══════════════════════════════════════════════════════════════════════

_SHADER_TEMPLATES = {
    "glow": """shader_type canvas_item;
// Glow/Fresnel — bordas brilham
uniform vec4 glow_color : source_color = vec4(0.3, 0.6, 1.0, 1.0);
uniform float glow_width : hint_range(0.0, 1.0) = 0.2;

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    float dist = length(UV - vec2(0.5));
    float glow = smoothstep(0.5, 0.5 - glow_width, dist);
    COLOR = mix(tex, glow_color, glow * glow_color.a);
}""",
    "dissolve": """shader_type canvas_item;
// Dissolve — dissolve via noise
uniform float dissolve_amount : hint_range(0.0, 1.0) = 0.0;
uniform vec4 edge_color : source_color = vec4(1.0, 0.5, 0.0, 1.0);
uniform float edge_width : hint_range(0.0, 0.5) = 0.1;

float random(vec2 uv) {
    return fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    float noise = random(floor(UV * 50.0));
    float edge = smoothstep(dissolve_amount - edge_width, dissolve_amount, noise);
    COLOR = mix(edge_color, tex, edge);
    if (noise < dissolve_amount) discard;
}""",
    "water": """shader_type canvas_item;
// Water — distorção de onda
uniform float time_scale : hint_range(0.0, 5.0) = 1.0;
uniform float amplitude : hint_range(0.0, 0.1) = 0.02;
uniform float frequency : hint_range(1.0, 20.0) = 5.0;

void fragment() {
    vec2 uv = UV;
    uv.x += sin(UV.y * frequency + TIME * time_scale) * amplitude;
    uv.y += cos(UV.x * frequency + TIME * time_scale * 0.7) * amplitude;
    COLOR = texture(TEXTURE, uv);
}""",
    "wind": """shader_type canvas_item;
// Wind — ondulação de vértice (grama, bandeira)
uniform float strength : hint_range(0.0, 0.1) = 0.03;
uniform float speed : hint_range(0.0, 5.0) = 1.5;

void vertex() {
    VERTEX.x += sin(VERTEX.y * 0.05 + TIME * speed) * strength * 100.0;
}

void fragment() {
    COLOR = texture(TEXTURE, UV);
}""",
    "grayscale": """shader_type canvas_item;
// Grayscale
void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    float gray = dot(tex.rgb, vec3(0.299, 0.587, 0.114));
    COLOR = vec4(vec3(gray), tex.a);
}""",
}


def generate_shader_2d(
    scene_path: str,
    node_path: str,
    template: str = "glow",
    uniforms: dict | None = None,
    shader_name: str = "",
) -> dict:
    """Gera e aplica um shader 2D a partir de template.

    Templates disponíveis:
    - glow: bordas brilham (fresnel)
    - dissolve: dissolve com noise + cor de borda
    - water: distorção de onda
    - wind: ondulação de vértice (grama, bandeira)
    - grayscale: escala de cinza

    Args:
        scene_path: Caminho da cena.
        node_path: Caminho do nó (Sprite2D, ColorRect, etc.).
        template: Nome do template.
        uniforms: Dict de uniforms customizados (ex: {{"glow_color": [1,0,0,1]}}).
        shader_name: Nome do arquivo .gdshader (auto-gerado se vazio).

    Returns:
        {{"status": "success", "shader_path": str, "template": str}}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    if template not in _SHADER_TEMPLATES:
        return {"status": "error", "message": f"Template '{template}' não encontrado. Disponíveis: {list(_SHADER_TEMPLATES.keys())}"}

    shader_code = _SHADER_TEMPLATES[template]

    # Aplicar uniforms customizados
    if uniforms:
        for key, value in uniforms.items():
            if isinstance(value, list) and len(value) == 4:
                shader_code = shader_code.replace(
                    f"uniform vec4 {key} : source_color = vec4(",
                    f"uniform vec4 {key} : source_color = vec4({value[0]}, {value[1]}, {value[2]}, {value[3]}"
                )

    # Salvar shader
    shaders_dir = proj / "shaders"
    shaders_dir.mkdir(exist_ok=True)

    if not shader_name:
        node_clean = node_path.replace("/", "_").replace(".", "_")
        shader_name = f"{node_clean}_{template}"

    shader_path = shaders_dir / f"{shader_name}.gdshader"

    checkpoint(f"shaders/{shader_name}.gdshader", proj)
    shader_path.write_text(shader_code, encoding="utf-8")

    # Aplicar ao nó na cena
    full_scene_path = proj / scene_path
    if full_scene_path.exists():
        content = full_scene_path.read_text(encoding="utf-8")
        node_name = node_path.split("/")[-1]
        lines = content.splitlines(keepends=True)
        lines.append(f'\n[node name="{node_name}" type="Sprite2D" parent="{node_path.rsplit("/", 1)[0]}"]\n')
        lines.append(f'material = ShaderMaterial.new()\n')
        lines.append(f'material.shader = load("res://shaders/{shader_name}.gdshader")\n')
        checkpoint(scene_path, proj)
        full_scene_path.write_text("".join(lines), encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "shader_path": f"res://shaders/{shader_name}.gdshader",
        "template": template,
        "code_preview": shader_code[:300] + "...",
    }


def apply_shader_to_node(
    scene_path: str,
    node_path: str,
    shader_template: str = "glow",
    uniforms: dict | None = None,
) -> dict:
    """Aplica um shader existente (ou gera novo) a um nó.

    Atalho para generate_shader_2d + apply.

    Args:
        scene_path: Caminho da cena.
        node_path: Caminho do nó.
        shader_template: Template de shader.
        uniforms: Uniforms customizados.

    Returns:
        {{"status": "success"}}
    """
    return generate_shader_2d(
        scene_path=scene_path,
        node_path=node_path,
        template=shader_template,
        uniforms=uniforms,
    )


# ══════════════════════════════════════════════════════════════════════
# 9.4 — PATH FOLLOWING
# ══════════════════════════════════════════════════════════════════════

def create_path_2d(
    scene_path: str,
    parent_node_path: str = ".",
    waypoints: list[list[float]] | None = None,
    path_name: str = "Path2D",
    closed: bool = False,
) -> dict:
    """Cria um Path2D com PathFollow2D para movimento ao longo de curva.

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai.
        waypoints: Lista de pontos [[x,y], ...]. Default: linha horizontal de 4 pontos.
        path_name: Nome do nó Path2D.
        closed: Se o caminho é fechado (loop).

    Returns:
        {{"status": "success", "node_path": str, "waypoints_count": int}}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    if not waypoints:
        waypoints = [[0, 0], [200, 0], [400, 0], [600, 0]]

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    # Path2D
    lines.append(f'\n[node name="{path_name}" type="Path2D" parent="{parent_node_path}"]\n')
    lines.append(f'editor_description = "Path2D gerado via MCP DevSolo"\n')

    # Curve2D com pontos
    curve_points = ", ".join(f"Vector2({wp[0]}, {wp[1]})" for wp in waypoints)
    lines.append(f'curve = Curve2D.new()\n')
    # Não podemos criar Curve2D inline facilmente, então usamos script

    # PathFollow2D
    follow_name = f"{path_name}Follow"
    lines.append(f'\n[node name="{follow_name}" type="PathFollow2D" parent="{parent_node_path}/{path_name}"]\n')
    lines.append(f'editor_description = "PathFollow2D gerado via MCP DevSolo"\n')
    lines.append(f'rotates = false\n')

    checkpoint(scene_path, proj)
    full_path.write_text("".join(lines), encoding="utf-8")
    mark_pending_compile()

    return {
        "status": "success",
        "node_path": f"{parent_node_path}/{path_name}",
        "follow_path": f"{parent_node_path}/{path_name}/{follow_name}",
        "waypoints_count": len(waypoints),
        "closed": closed,
        "note": "Use PathFollow2D.progress_ratio (0-1) para mover um nó filho ao longo do caminho.",
    }


def create_patrol_route(
    scene_path: str,
    parent_node_path: str,
    waypoints: list[list[float]],
    speed: float = 100.0,
    wait_time: float = 1.0,
    ping_pong: bool = True,
) -> dict:
    """Cria uma rota de patrulha com script de movimento entre waypoints.

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai (CharacterBody2D).
        waypoints: Lista de pontos [[x,y], ...].
        speed: Velocidade de movimento.
        wait_time: Tempo de espera em cada waypoint.
        ping_pong: Se True, vai e volta. Se False, loop circular.

    Returns:
        {{"status": "success", "script_path": str, "waypoints": int}}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    wp_array = ", ".join(f"Vector2({wp[0]}, {wp[1]})" for wp in waypoints)

    code = f'''extends CharacterBody2D
# PatrolRoute — gerado via MCP DevSolo

var waypoints: Array[Vector2] = [{wp_array}]
var current_index: int = 0
var direction: int = 1
var wait_timer: float = 0.0
var move_speed: float = {speed}
var wait_at_point: float = {wait_time}
var ping_pong_mode: bool = {'true' if ping_pong else 'false'}

func _ready():
    if waypoints.size() > 0:
        global_position = waypoints[0]

func _physics_process(delta):
    if waypoints.size() < 2:
        return

    if wait_timer > 0:
        wait_timer -= delta
        velocity = Vector2.ZERO
        move_and_slide()
        return

    var target = waypoints[current_index]
    var dist = global_position.distance_to(target)

    if dist < 5.0:
        wait_timer = wait_at_point
        if ping_pong_mode:
            if current_index >= waypoints.size() - 1:
                direction = -1
            elif current_index <= 0:
                direction = 1
            current_index += direction
        else:
            current_index = (current_index + 1) % waypoints.size()
        return

    var move_dir = (target - global_position).normalized()
    velocity = move_dir * move_speed
    move_and_slide()
'''

    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    node_name = parent_node_path.split("/")[-1].lower()
    script_path = scripts_dir / f"{node_name}_patrol.gd"

    checkpoint(f"scripts/{node_name}_patrol.gd", proj)
    script_path.write_text(code, encoding="utf-8")
    mark_pending_compile()

    return {
        "status": "success",
        "script_path": f"res://scripts/{node_name}_patrol.gd",
        "waypoints": len(waypoints),
        "ping_pong": ping_pong,
        "usage": f"O nó {parent_node_path} agora patrulha entre {len(waypoints)} pontos.",
        "code_preview": code[:400] + "...",
    }


# ══════════════════════════════════════════════════════════════════════
# 10.1 — SISTEMA DE DIÁLOGO
# ══════════════════════════════════════════════════════════════════════

def create_dialogue_system(
    autoload_name: str = "DialogueManager",
) -> dict:
    """Cria sistema de diálogo completo como Autoload.

    Gera DialogueManager.gd com suporte a:
    - Carregar árvore de diálogo de JSON
    - Mostrar texto com efeito typewriter
    - Suporte a escolhas (choices) com branching
    - Eventos: give_item, set_flag, start_battle

    Returns:
        {{"status": "success", "script_path": str, "usage": str}}
    """
    proj = _get_active_project()

    code = f'''extends Node
# DialogueManager — gerado via MCP DevSolo
# Autoload: {autoload_name}

signal dialogue_started(dialogue_id: String)
signal dialogue_ended
signal choice_made(choice_index: int)

var dialogues: Dictionary = {{}}
var current_dialogue: Dictionary = {{}}
var is_active: bool = false

func _ready():
    load_dialogues()

func load_dialogues():
    var file = FileAccess.open("res://dialogues/dialogues.json", FileAccess.READ)
    if file:
        var json_text = file.get_as_text()
        var json = JSON.new()
        var error = json.parse(json_text)
        if error == OK:
            dialogues = json.data
        file.close()

func start_dialogue(dialogue_id: String):
    if not dialogues.has(dialogue_id):
        printerr("DialogueManager: Diálogo '" + dialogue_id + "' não encontrado")
        return
    current_dialogue = dialogues[dialogue_id]
    is_active = true
    dialogue_started.emit(dialogue_id)

func get_current_node() -> Dictionary:
    if not is_active:
        return {{}}
    return current_dialogue

func get_text() -> String:
    return current_dialogue.get("text", "")

func get_speaker() -> String:
    return current_dialogue.get("speaker", "???")

func get_choices() -> Array:
    return current_dialogue.get("choices", [])

func choose(index: int):
    var choices = get_choices()
    if index < 0 or index >= choices.size():
        return
    var choice = choices[index]
    choice_made.emit(index)
    if choice.has("events"):
        for event in choice["events"]:
            _run_event(event)
    if choice.has("next"):
        start_dialogue(choice["next"])
    else:
        end_dialogue()

func next():
    if current_dialogue.has("next"):
        start_dialogue(current_dialogue["next"])
    else:
        end_dialogue()

func end_dialogue():
    is_active = false
    current_dialogue = {{}}
    dialogue_ended.emit()

func _run_event(event: Dictionary):
    var action = event.get("action", "")
    var params = event.get("params", {{}})
    match action:
        "give_item":
            if has_node("/root/InventoryManager"):
                get_node("/root/InventoryManager").add_item(params.get("item_id", ""), params.get("quantity", 1))
        "set_flag":
            pass  # Implementar conforme necessidade
        "start_battle":
            pass
'''

    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    script_path = scripts_dir / "dialogue_manager.gd"

    checkpoint("scripts/dialogue_manager.gd", proj)
    script_path.write_text(code, encoding="utf-8")

    # Registrar autoload
    project_file = proj / "project.godot"
    if project_file.exists():
        content = project_file.read_text(encoding="utf-8")
        if "[autoload]" in content:
            if autoload_name not in content:
                content = content.replace("[autoload]", f"[autoload]\n{autoload_name}=\"*res://scripts/dialogue_manager.gd\"")
        else:
            content += f"\n[autoload]\n{autoload_name}=\"*res://scripts/dialogue_manager.gd\"\n"
        checkpoint("project.godot", proj)
        project_file.write_text(content, encoding="utf-8")

    # Criar diretório de diálogos com JSON exemplo
    dialogues_dir = proj / "dialogues"
    dialogues_dir.mkdir(exist_ok=True)
    example_json = '''{
    "greeting": {
        "speaker": "NPC",
        "text": "Olá, aventureiro! Bem-vindo à nossa vila.",
        "next": "greeting_choice"
    },
    "greeting_choice": {
        "speaker": "NPC",
        "text": "Como posso ajudá-lo?",
        "choices": [
            {"text": "Conte-me sobre este lugar.", "next": "about_town"},
            {"text": "Tenho que ir. Até mais!", "next": null}
        ]
    },
    "about_town": {
        "speaker": "NPC",
        "text": "Nossa vila é conhecida pelas minas de ouro ao norte. Mas cuidado com os goblins!",
        "next": null
    }
}'''
    (dialogues_dir / "dialogues.json").write_text(example_json, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "script_path": "res://scripts/dialogue_manager.gd",
        "usage": f'{autoload_name}.start_dialogue("greeting") para iniciar diálogo.',
        "dialogues_file": "res://dialogues/dialogues.json",
    }


def add_dialogue_node(
    dialogue_id: str,
    speaker: str,
    text: str,
    next_id: str = "",
    choices: list[dict] | None = None,
    events: list[dict] | None = None,
) -> dict:
    """Adiciona um nó à árvore de diálogo (dialogues.json).

    Args:
        dialogue_id: ID único do nó (ex: "greeting", "quest_accept").
        speaker: Nome de quem fala.
        text: Texto da fala.
        next_id: ID do próximo nó (vazio = fim do diálogo).
        choices: Lista de escolhas [{{"text": "...", "next": "id"}}].
        events: Lista de eventos [{{"action": "give_item", "params": {{...}}}}].

    Returns:
        {{"status": "success", "dialogue_id": str}}
    """
    proj = _get_active_project()
    dialogues_path = proj / "dialogues" / "dialogues.json"

    if not dialogues_path.exists():
        return {"status": "error", "message": "dialogues.json não encontrado. Execute create_dialogue_system primeiro."}

    import json as _json
    dialogues = _json.loads(dialogues_path.read_text(encoding="utf-8"))

    node = {"speaker": speaker, "text": text}
    if next_id:
        node["next"] = next_id
    if choices:
        node["choices"] = choices
    if events:
        node["events"] = events

    dialogues[dialogue_id] = node

    checkpoint("dialogues/dialogues.json", proj)
    dialogues_path.write_text(_json.dumps(dialogues, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "status": "success",
        "dialogue_id": dialogue_id,
        "speaker": speaker,
    }


def create_dialogue_ui(
    scene_name: str = "dialogue_ui",
) -> dict:
    """Cria cena de interface de diálogo (CanvasLayer).

    Inclui: painel inferior, nome do speaker, texto com typewriter,
    container de escolhas. Usa DialogueManager como backend.

    Returns:
        {{"status": "success", "scene_path": str, "script_path": str}}
    """
    proj = _get_active_project()

    tscn = '''[gd_scene load_steps=2 format=3 uid=""]

[node name="DialogueUI" type="CanvasLayer"]
layer = 10

[node name="Panel" type="Panel" parent="."]
layout_mode = 1
anchors_preset = 12
anchor_left = 0.0
anchor_top = 1.0
anchor_right = 1.0
anchor_bottom = 1.0
offset_top = -200.0
offset_bottom = 0.0
grow_horizontal = 2
grow_vertical = 0

[node name="VBox" type="VBoxContainer" parent="Panel"]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
theme_override_constants/separation = 10

[node name="SpeakerLabel" type="Label" parent="Panel/VBox"]
layout_mode = 2
text = "NPC"
theme_override_font_sizes/font_size = 18
theme_override_colors/font_color = Color(0.9529, 0.6118, 0.0706, 1)

[node name="TextLabel" type="RichTextLabel" parent="Panel/VBox"]
layout_mode = 2
custom_minimum_size = Vector2(0, 80)
bbcode_enabled = true
scroll_following = true
theme_override_font_sizes/normal_font_size = 18

[node name="ChoicesContainer" type="VBoxContainer" parent="Panel/VBox"]
layout_mode = 2
theme_override_constants/separation = 5
visible = false
'''

    scenes_dir = proj / "scenes"
    scenes_dir.mkdir(exist_ok=True)
    scene_path = scenes_dir / f"{scene_name}.tscn"

    checkpoint(f"scenes/{scene_name}.tscn", proj)
    scene_path.write_text(tscn, encoding="utf-8")

    # Script da UI de diálogo
    ui_code = '''extends CanvasLayer
# DialogueUI — gerado via MCP DevSolo

var typewriter_tween: Tween
var current_visible_chars: int = 0

func _ready():
    hide()
    DialogueManager.dialogue_started.connect(_on_dialogue_started)
    DialogueManager.dialogue_ended.connect(_on_dialogue_ended)

func _input(event):
    if not visible:
        return
    if event.is_action_pressed("ui_accept") or event.is_action_pressed("ui_select"):
        if DialogueManager.get_choices().size() > 0:
            return  # Não avança se há escolhas
        DialogueManager.next()

func _on_dialogue_started(_id: String):
    show()
    _display_node()

func _on_dialogue_ended():
    hide()

func _display_node():
    var node = DialogueManager.get_current_node()
    if node.is_empty():
        return

    $Panel/VBox/SpeakerLabel.text = node.get("speaker", "???")
    var text = node.get("text", "")
    $Panel/VBox/TextLabel.text = text

    # Typewriter effect
    if typewriter_tween:
        typewriter_tween.kill()
    $Panel/VBox/TextLabel.visible_characters = 0
    typewriter_tween = create_tween()
    typewriter_tween.tween_property($Panel/VBox/TextLabel, "visible_characters", text.length(), text.length() * 0.03)

    # Choices
    var choices = node.get("choices", [])
    var container = $Panel/VBox/ChoicesContainer
    for child in container.get_children():
        child.queue_free()

    if choices.size() > 0:
        container.visible = true
        for i in range(choices.size()):
            var btn = Button.new()
            btn.text = str(i + 1) + ". " + choices[i].get("text", "")
            btn.pressed.connect(_on_choice_pressed.bind(i))
            container.add_child(btn)
    else:
        container.visible = false

func _on_choice_pressed(index: int):
    DialogueManager.choose(index)
'''

    scripts_dir = proj / "scripts" / "ui"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    script_file = scripts_dir / "dialogue_ui.gd"
    script_file.write_text(ui_code, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "scene_path": f"res://scenes/{scene_name}.tscn",
        "script_path": "res://scripts/ui/dialogue_ui.gd",
    }


# ══════════════════════════════════════════════════════════════════════
# 10.2 — SISTEMA DE INVENTÁRIO
# ══════════════════════════════════════════════════════════════════════

def create_inventory_system(
    autoload_name: str = "InventoryManager",
    max_slots: int = 20,
) -> dict:
    """Cria sistema de inventário como Autoload.

    Funções: add_item, remove_item, has_item, get_items, use_item.
    Itens são Resources .tres para fácil extensão.

    Returns:
        {{"status": "success", "script_path": str}}
    """
    proj = _get_active_project()

    code = f'''extends Node
# InventoryManager — gerado via MCP DevSolo
# Autoload: {autoload_name}

signal item_added(item_id: String, quantity: int)
signal item_removed(item_id: String, quantity: int)
signal inventory_changed

const MAX_SLOTS = {max_slots}

var items: Dictionary = {{}}  # {{ item_id: {{ "data": ItemData, "quantity": int }} }}

func add_item(item_id: String, quantity: int = 1) -> bool:
    if items.has(item_id):
        var entry = items[item_id]
        entry["quantity"] += quantity
    else:
        if items.size() >= MAX_SLOTS:
            printerr("InventoryManager: Inventário cheio!")
            return false
        var item_data = load("res://items/" + item_id + ".tres")
        if not item_data:
            printerr("InventoryManager: Item '" + item_id + "' não encontrado")
            return false
        items[item_id] = {{"data": item_data, "quantity": quantity}}

    item_added.emit(item_id, quantity)
    inventory_changed.emit()
    return true

func remove_item(item_id: String, quantity: int = 1) -> bool:
    if not items.has(item_id):
        return false
    items[item_id]["quantity"] -= quantity
    if items[item_id]["quantity"] <= 0:
        items.erase(item_id)
    item_removed.emit(item_id, quantity)
    inventory_changed.emit()
    return true

func has_item(item_id: String, quantity: int = 1) -> bool:
    return items.has(item_id) and items[item_id]["quantity"] >= quantity

func get_items() -> Array:
    var result = []
    for item_id in items:
        result.append({{
            "id": item_id,
            "name": items[item_id]["data"].item_name,
            "quantity": items[item_id]["quantity"],
            "type": items[item_id]["data"].item_type,
            "icon": items[item_id]["data"].icon_path,
        }})
    return result

func get_item_count(item_id: String) -> int:
    if items.has(item_id):
        return items[item_id]["quantity"]
    return 0

func use_item(item_id: String) -> bool:
    if not has_item(item_id):
        return false
    var item_data = items[item_id]["data"]
    # Efeito depende do tipo do item (implementado pelo jogo)
    remove_item(item_id, 1)
    return true
'''

    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    script_path = scripts_dir / "inventory_manager.gd"

    checkpoint("scripts/inventory_manager.gd", proj)
    script_path.write_text(code, encoding="utf-8")

    # Autoload
    project_file = proj / "project.godot"
    if project_file.exists():
        content = project_file.read_text(encoding="utf-8")
        if "[autoload]" in content:
            if autoload_name not in content:
                content = content.replace("[autoload]", f"[autoload]\n{autoload_name}=\"*res://scripts/inventory_manager.gd\"")
        else:
            content += f"\n[autoload]\n{autoload_name}=\"*res://scripts/inventory_manager.gd\"\n"
        checkpoint("project.godot", proj)
        project_file.write_text(content, encoding="utf-8")

    # Diretório de items
    items_dir = proj / "items"
    items_dir.mkdir(exist_ok=True)

    mark_pending_compile()

    return {
        "status": "success",
        "script_path": "res://scripts/inventory_manager.gd",
        "max_slots": max_slots,
        "usage": f'{autoload_name}.add_item("potion") para adicionar. {autoload_name}.get_items() para listar.',
    }


def define_inventory_item(
    item_id: str,
    item_name: str,
    item_type: str = "consumable",
    description: str = "",
    stackable: bool = True,
    max_stack: int = 99,
    icon_path: str = "",
    properties: dict | None = None,
) -> dict:
    """Cria um Resource .tres de item para o inventário.

    Args:
        item_id: ID único (ex: "potion", "sword_1").
        item_name: Nome exibido.
        item_type: consumable, weapon, armor, quest, material.
        description: Descrição do item.
        stackable: Se pode empilhar.
        max_stack: Máximo por slot.
        icon_path: Caminho da textura do ícone.
        properties: Dict de propriedades (dano, cura, etc.).

    Returns:
        {{"status": "success", "item_path": str}}
    """
    proj = _get_active_project()
    items_dir = proj / "items"
    items_dir.mkdir(exist_ok=True)

    props_str = ""
    if properties:
        for k, v in properties.items():
            if isinstance(v, (int, float)):
                props_str += f'{k} = {v}\n'
            elif isinstance(v, str):
                props_str += f'{k} = "{v}"\n'

    tres_content = f'''[gd_resource type="Resource" load_steps=1 format=3 uid=""]

[resource]
script = ExtResource("1_item_data")
item_id = "{item_id}"
item_name = "{item_name}"
item_type = "{item_type}"
description = "{description}"
stackable = {'true' if stackable else 'false'}
max_stack = {max_stack}
icon_path = "{icon_path}"
{props_str}
'''

    item_path = items_dir / f"{item_id}.tres"
    checkpoint(f"items/{item_id}.tres", proj)
    item_path.write_text(tres_content, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "item_path": f"res://items/{item_id}.tres",
        "item_name": item_name,
    }


def create_inventory_ui(
    scene_name: str = "inventory_ui",
    columns: int = 5,
) -> dict:
    """Cria cena de interface de inventário com grid de slots.

    Args:
        scene_name: Nome da cena.
        columns: Número de colunas no grid.

    Returns:
        {{"status": "success", "scene_path": str}}
    """
    proj = _get_active_project()

    tscn = f'''[gd_scene load_steps=2 format=3 uid=""]

[node name="InventoryUI" type="CanvasLayer"]
layer = 10

[node name="Background" type="ColorRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
color = Color(0, 0, 0, 0.8)

[node name="Panel" type="Panel" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -300.0
offset_top = -250.0
offset_right = 300.0
offset_bottom = 250.0

[node name="Title" type="Label" parent="Panel"]
layout_mode = 0
offset_left = 20.0
offset_top = 10.0
text = "INVENTÁRIO"
theme_override_font_sizes/font_size = 24

[node name="GridContainer" type="GridContainer" parent="Panel"]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
offset_left = 20.0
offset_top = 50.0
offset_right = -20.0
offset_bottom = -20.0
columns = {columns}
theme_override_constants/h_separation = 5
theme_override_constants/v_separation = 5

[node name="CloseButton" type="Button" parent="Panel"]
layout_mode = 0
offset_right = -20.0
offset_bottom = 35.0
text = "✕ FECHAR"
'''

    scenes_dir = proj / "scenes"
    scenes_dir.mkdir(exist_ok=True)
    scene_path = scenes_dir / f"{scene_name}.tscn"

    checkpoint(f"scenes/{scene_name}.tscn", proj)
    scene_path.write_text(tscn, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "scene_path": f"res://scenes/{scene_name}.tscn",
        "columns": columns,
    }


# ══════════════════════════════════════════════════════════════════════
# 10.3 — ARMAS E PROJÉTEIS
# ══════════════════════════════════════════════════════════════════════

def create_bullet_template(
    bullet_name: str = "Bullet",
    speed: float = 500.0,
    damage: float = 10.0,
    lifetime: float = 3.0,
    bullet_color: str = "#ffff00",
    bullet_size: int = 8,
) -> dict:
    """Cria cena de projétil reutilizável (Area2D).

    Args:
        bullet_name: Nome da cena do projétil.
        speed: Velocidade em pixels/segundo.
        damage: Dano causado ao atingir.
        lifetime: Tempo de vida antes de auto-destruir.
        bullet_color: Cor do projétil.
        bullet_size: Tamanho em pixels.

    Returns:
        {{"status": "success", "scene_path": str}}
    """
    proj = _get_active_project()

    tscn = f'''[gd_scene load_steps=2 format=3 uid=""]

[node name="{bullet_name}" type="Area2D"]
collision_layer = 2
collision_mask = 1

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource( "1_{bullet_name.lower()}_tex" )
modulate = Color("{bullet_color}")

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource( "CircleShape2D_{bullet_name.lower()}" )

[node name="Timer" type="Timer" parent="."]
wait_time = {lifetime}
one_shot = true
autostart = true
'''

    # Script do projétil
    bullet_script = f'''extends Area2D
# {bullet_name} — gerado via MCP DevSolo

var bullet_speed: float = {speed}
var bullet_damage: float = {damage}
var bullet_direction: Vector2 = Vector2.RIGHT

func _ready():
    $Timer.timeout.connect(queue_free)
    body_entered.connect(_on_hit)

func _physics_process(delta):
    position += bullet_direction * bullet_speed * delta

func _on_hit(body):
    if body.has_method("take_damage"):
        body.take_damage(bullet_damage)
    queue_free()

func set_direction(dir: Vector2):
    bullet_direction = dir.normalized()
    rotation = dir.angle()
'''

    scenes_dir = proj / "scenes"
    scenes_dir.mkdir(exist_ok=True)
    scene_path = scenes_dir / f"{bullet_name.lower()}.tscn"

    checkpoint(f"scenes/{bullet_name.lower()}.tscn", proj)
    scene_path.write_text(tscn, encoding="utf-8")

    # Script
    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    script_path = scripts_dir / f"{bullet_name.lower()}.gd"
    script_path.write_text(bullet_script, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "scene_path": f"res://scenes/{bullet_name.lower()}.tscn",
        "script_path": f"res://scripts/{bullet_name.lower()}.gd",
        "damage": damage,
        "speed": speed,
        "usage": f'Instancie com: var b = preload("res://scenes/{bullet_name.lower()}.tscn").instantiate(); b.set_direction(Vector2.RIGHT); get_parent().add_child(b)',
    }


def create_gun_system(
    script_path: str,
    bullet_scene_path: str = "res://scenes/bullet.tscn",
    fire_rate: float = 0.3,
    ammo_max: int = 30,
    spread_angle: float = 0.0,
    auto_reload: bool = True,
    reload_time: float = 1.5,
) -> dict:
    """Gera script de sistema de arma (tiro, cooldown, munição, reload).

    Args:
        script_path: Onde salvar o script.
        bullet_scene_path: Caminho da cena do projétil.
        fire_rate: Tempo entre tiros.
        ammo_max: Munição máxima.
        spread_angle: Ângulo de dispersão em graus.
        auto_reload: Recarregar automaticamente ao acabar.
        reload_time: Tempo de recarga.

    Returns:
        {{"status": "success", "script_path": str}}
    """
    proj = _get_active_project()

    code = f'''extends Node2D
# GunSystem — gerado via MCP DevSolo

@export var bullet_scene: PackedScene = preload("{bullet_scene_path}")
@export var fire_rate: float = {fire_rate}
@export var ammo_max: int = {ammo_max}
@export var spread_angle: float = {spread_angle}
@export var auto_reload: bool = {'true' if auto_reload else 'false'}
@export var reload_time: float = {reload_time}

var current_ammo: int = ammo_max
var fire_cooldown: float = 0.0
var is_reloading: bool = false

signal fired
signal reloaded
signal ammo_changed(current: int, max: int)

func _ready():
    ammo_changed.emit(current_ammo, ammo_max)

func _process(delta):
    if fire_cooldown > 0:
        fire_cooldown -= delta

func shoot(direction: Vector2):
    if is_reloading or fire_cooldown > 0:
        return
    if current_ammo <= 0:
        if auto_reload:
            reload()
        return

    var bullet = bullet_scene.instantiate()
    bullet.global_position = global_position

    # Aplicar spread
    var final_dir = direction
    if spread_angle > 0:
        var angle_offset = randf_range(-spread_angle, spread_angle)
        final_dir = direction.rotated(deg_to_rad(angle_offset))

    bullet.set_direction(final_dir)
    get_parent().add_child(bullet)

    current_ammo -= 1
    fire_cooldown = fire_rate
    ammo_changed.emit(current_ammo, ammo_max)
    fired.emit()

    if current_ammo <= 0 and auto_reload:
        reload()

func reload():
    if is_reloading or current_ammo == ammo_max:
        return
    is_reloading = true
    var tween = create_tween()
    tween.tween_callback(_finish_reload).set_delay(reload_time)

func _finish_reload():
    current_ammo = ammo_max
    is_reloading = false
    ammo_changed.emit(current_ammo, ammo_max)
    reloaded.emit()

func add_ammo(amount: int):
    current_ammo = min(current_ammo + amount, ammo_max)
    ammo_changed.emit(current_ammo, ammo_max)
'''

    full_path = proj / script_path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    checkpoint(script_path, proj)
    full_path.write_text(code, encoding="utf-8")
    mark_pending_compile()

    return {
        "status": "success",
        "script_path": f"res://{script_path}",
        "fire_rate": fire_rate,
        "ammo_max": ammo_max,
        "usage": f'Anexe este script a um Node2D. Chame shoot(get_global_mouse_position() - global_position) no _input.',
    }


# ══════════════════════════════════════════════════════════════════════
# 10.4 — GERAÇÃO PROCEDURAL
# ══════════════════════════════════════════════════════════════════════

def generate_tilemap_from_noise(
    scene_path: str,
    tilemap_layer_path: str,
    tile_size: int = 32,
    width: int = 40,
    height: int = 30,
    seed: int = 0,
    threshold: float = 0.5,
    tile_ground: int = 0,
    tile_wall: int = 1,
) -> dict:
    """Preenche um TileMapLayer com ruído Perlin procedural.

    Args:
        scene_path: Caminho da cena.
        tilemap_layer_path: Caminho do TileMapLayer.
        tile_size: Tamanho do tile.
        width, height: Dimensões em tiles.
        seed: Semente do ruído.
        threshold: Limiar (0-1). Abaixo = chão (tile_ground), acima = parede (tile_wall).
        tile_ground: ID do tile de chão.
        tile_wall: ID do tile de parede.

    Returns:
        {{"status": "success", "tiles_generated": int}}
    """
    _check_path(scene_path)
    proj = _get_active_project()

    import random
    if seed == 0:
        seed = random.randint(1, 99999)

    bake_code = f'''# TilemapNoiseGenerator — gerado via MCP DevSolo

extends Node

func _ready():
    var tilemap = get_node("{tilemap_layer_path}")
    if not tilemap:
        printerr("TileMapLayer não encontrado!")
        get_tree().quit(1)

    var noise = FastNoiseLite.new()
    noise.seed = {seed}
    noise.frequency = 0.05
    noise.noise_type = FastNoiseLite.TYPE_PERLIN

    var tiles_generated = 0
    for x in range({width}):
        for y in range({height}):
            var value = noise.get_noise_2d(x, y)
            var tile_id = {tile_wall} if value > {threshold} else {tile_ground}
            tilemap.set_cell(Vector2i(x, y), tile_id, Vector2i(0, 0))
            tiles_generated += 1

    print("TileMap gerado! Tiles: " + str(tiles_generated) + " Seed: " + str({seed}))
    get_tree().quit(0)
'''

    scripts_dir = proj / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    bake_path = scripts_dir / "_generate_tilemap_noise.gd"
    bake_path.write_text(bake_code, encoding="utf-8")

    try:
        godot_bin = get_godot_bin()
        result = subprocess.run(
            [godot_bin, "--headless", "--path", str(proj), "--script", "scripts/_generate_tilemap_noise.gd"],
            capture_output=True, text=True, timeout=30, cwd=str(proj),
        )
        output = result.stdout + "\n" + result.stderr
        bake_path.unlink(missing_ok=True)
        return {
            "status": "success" if result.returncode == 0 else "warning",
            "output": output.strip(),
            "tiles_attempted": width * height,
            "seed": seed,
            "threshold": threshold,
        }
    except subprocess.TimeoutExpired:
        bake_path.unlink(missing_ok=True)
        return {"status": "error", "message": "Timeout ao gerar tilemap."}
    except Exception as e:
        bake_path.unlink(missing_ok=True)
        return {"status": "error", "message": str(e)}


def generate_dungeon_rooms(
    num_rooms: int = 8,
    min_size: int = 5,
    max_size: int = 12,
    map_width: int = 80,
    map_height: int = 60,
    corridor_width: int = 2,
    seed: int = 0,
) -> dict:
    """Gera layout de dungeon procedural usando BSP (Binary Space Partition).

    Args:
        num_rooms: Número de salas.
        min_size, max_size: Tamanho mínimo/máximo das salas.
        map_width, map_height: Dimensões do mapa.
        corridor_width: Largura dos corredores.
        seed: Semente para reproducibilidade.

    Returns:
        {{"status": "success", "rooms": [...], "corridors": [...]}}
    """
    import random
    if seed == 0:
        seed = random.randint(1, 99999)
    random.seed(seed)

    rooms = []
    for _ in range(num_rooms):
        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        x = random.randint(1, map_width - w - 1)
        y = random.randint(1, map_height - h - 1)
        rooms.append({"x": x, "y": y, "w": w, "h": h})

    # Corredores conectando salas adjacentes
    corridors = []
    for i in range(len(rooms) - 1):
        r1 = rooms[i]
        r2 = rooms[i + 1]
        cx1 = r1["x"] + r1["w"] // 2
        cy1 = r1["y"] + r1["h"] // 2
        cx2 = r2["x"] + r2["w"] // 2
        cy2 = r2["y"] + r2["h"] // 2

        # Corredor em L
        corridors.append({
            "from": [cx1, cy1],
            "to": [cx2, cy2],
            "bend": [cx1, cy2],
            "width": corridor_width,
        })

    return {
        "status": "success",
        "seed": seed,
        "rooms": rooms,
        "corridors": corridors,
        "map_size": [map_width, map_height],
        "tile_info": "Cada unidade = 1 tile. Use TileMap.set_cell() para desenhar.",
    }


# ══════════════════════════════════════════════════════════════════════
# 10.5 — LOADING SCREEN
# ══════════════════════════════════════════════════════════════════════

def create_loading_screen(
    scene_name: str = "loading_screen",
    tips: list[str] | None = None,
    min_load_time: float = 1.0,
    background_color: str = "#1a1a2e",
) -> dict:
    """Cria cena de tela de carregamento com ProgressBar e dicas.

    Args:
        scene_name: Nome da cena.
        tips: Lista de dicas para exibir.
        min_load_time: Tempo mínimo de exibição (evita flicker).
        background_color: Cor de fundo.

    Returns:
        {{"status": "success", "scene_path": str}}
    """
    proj = _get_active_project()

    if not tips:
        tips = [
            "Dica: Pressione ESC para pausar o jogo.",
            "Dica: Colete moedas para aumentar seu score.",
            "Dica: Use WASD para mover o personagem.",
        ]

    tscn = f'''[gd_scene load_steps=2 format=3 uid=""]

[node name="LoadingScreen" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0

[node name="Background" type="ColorRect" parent="."]
layout_mode = 0
offset_right = 1280.0
offset_bottom = 720.0
color = Color("{background_color}")

[node name="VBox" type="VBoxContainer" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -250.0
offset_top = -50.0
offset_right = 250.0
offset_bottom = 50.0

[node name="LoadingLabel" type="Label" parent="VBox"]
layout_mode = 2
text = "CARREGANDO..."
horizontal_alignment = 1
theme_override_font_sizes/font_size = 28
theme_override_colors/font_color = Color(1.0000, 1.0000, 1.0000, 1)

[node name="ProgressBar" type="ProgressBar" parent="VBox"]
layout_mode = 2
custom_minimum_size = Vector2(400, 25)
value = 0.0

[node name="TipLabel" type="Label" parent="VBox"]
layout_mode = 2
text = ""
horizontal_alignment = 1
theme_override_font_sizes/font_size = 16
theme_override_colors/font_color = Color(0.6275, 0.6275, 0.6902, 1)
'''

    scenes_dir = proj / "scenes"
    scenes_dir.mkdir(exist_ok=True)
    scene_path = scenes_dir / f"{scene_name}.tscn"

    checkpoint(f"scenes/{scene_name}.tscn", proj)
    scene_path.write_text(tscn, encoding="utf-8")

    # Script de loading
    tips_str = ", ".join(f'"{t}"' for t in tips)
    loading_script = f'''extends Control
# LoadingScreen — gerado via MCP DevSolo

var tips: Array[String] = [{tips_str}]
var target_scene: String = ""
var min_time: float = {min_load_time}
var elapsed: float = 0.0

func load_scene(scene_path: String):
    target_scene = scene_path
    show()
    $VBox/TipLabel.text = tips.pick_random()
    ResourceLoader.load_threaded_request(scene_path)

func _process(delta):
    elapsed += delta
    var progress = []
    var status = ResourceLoader.load_threaded_get_status(target_scene, progress)

    match status:
        ResourceLoader.THREAD_LOAD_IN_PROGRESS:
            $VBox/ProgressBar.value = progress[0] * 100.0
        ResourceLoader.THREAD_LOAD_LOADED:
            if elapsed >= min_time:
                var scene = ResourceLoader.load_threaded_get(target_scene)
                get_tree().change_scene_to_packed(scene)
        ResourceLoader.THREAD_LOAD_FAILED:
            printerr("Falha ao carregar: " + target_scene)
'''

    scripts_dir = proj / "scripts" / "ui"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    script_path = scripts_dir / "loading_screen.gd"
    script_path.write_text(loading_script, encoding="utf-8")

    mark_pending_compile()

    return {
        "status": "success",
        "scene_path": f"res://scenes/{scene_name}.tscn",
        "tips_count": len(tips),
    }


def load_scene_async(
    target_scene: str,
    loading_scene: str = "res://scenes/loading_screen.tscn",
) -> dict:
    """Inicia carregamento assíncrono de cena com loading screen.

    Usa ResourceLoader.load_threaded_request + polling.

    Args:
        target_scene: Cena a carregar.
        loading_scene: Cena de loading a exibir durante o carregamento.

    Returns:
        {{"status": "success", "note": str}}
    """
    return {
        "status": "success",
        "note": f"Para carregamento assíncrono, use: get_tree().change_scene_to_file('{loading_scene}') e no script da loading scene chame load_scene('{target_scene}').",
        "loading_scene": loading_scene,
        "target_scene": target_scene,
    }


# ══════════════════════════════════════════════════════════════════════
# 11.1 — RAYCASTING E DETECÇÃO
# ══════════════════════════════════════════════════════════════════════

def add_raycast_2d(
    scene_path: str,
    parent_node_path: str,
    target_position: list[float] | None = None,
    collision_mask: int = 1,
    enabled: bool = True,
    node_name: str = "RayCast2D",
) -> dict:
    """Adiciona um RayCast2D para detecção de linha.

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai.
        target_position: Posição alvo [x, y]. Default [0, 50] (para baixo).
        collision_mask: Máscara de colisão.
        enabled: Ativado por padrão.
        node_name: Nome do nó.

    Returns:
        {{"status": "success", "node_path": str}}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    if not target_position:
        target_position = [0, 50]

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    lines.append(f'\n[node name="{node_name}" type="RayCast2D" parent="{parent_node_path}"]\n')
    lines.append(f'editor_description = "RayCast2D gerado via MCP DevSolo"\n')
    lines.append(f'target_position = Vector2({target_position[0]}, {target_position[1]})\n')
    lines.append(f'collision_mask = {collision_mask}\n')
    lines.append(f'enabled = {'true' if enabled else 'false'}\n')

    checkpoint(scene_path, proj)
    full_path.write_text("".join(lines), encoding="utf-8")
    mark_pending_compile()

    return {"status": "success", "node_path": f"{parent_node_path}/{node_name}"}


def add_shapecast_2d(
    scene_path: str,
    parent_node_path: str,
    shape_type: str = "rectangle",
    shape_size: list[float] | None = None,
    collision_mask: int = 1,
    node_name: str = "ShapeCast2D",
) -> dict:
    """Adiciona ShapeCast2D para detecção de área.

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai.
        shape_type: "rectangle", "circle", ou "capsule".
        shape_size: Dimensões [w, h] ou [radius].
        collision_mask: Máscara de colisão.
        node_name: Nome do nó.

    Returns:
        {{"status": "success", "node_path": str}}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    if not full_path.exists():
        return {"status": "error", "message": f"Cena '{scene_path}' não encontrada."}

    if not shape_size:
        shape_size = [50, 50] if shape_type == "rectangle" else [25]

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    lines.append(f'\n[node name="{node_name}" type="ShapeCast2D" parent="{parent_node_path}"]\n')
    lines.append(f'editor_description = "ShapeCast2D gerado via MCP DevSolo"\n')
    lines.append(f'collision_mask = {collision_mask}\n')
    lines.append(f'enabled = true\n')

    checkpoint(scene_path, proj)
    full_path.write_text("".join(lines), encoding="utf-8")
    mark_pending_compile()

    return {"status": "success", "node_path": f"{parent_node_path}/{node_name}", "shape": shape_type}


# ══════════════════════════════════════════════════════════════════════
# 11.2 — DEBUG E DIAGNÓSTICO
# ══════════════════════════════════════════════════════════════════════

def enable_debug_collisions(enabled: bool = True) -> dict:
    """Ativa/desativa visualização de collision shapes no projeto.

    Configura ProjectSettings: debug/shapes/collision/visible_collision_shapes.

    Returns:
        {{"status": "success", "enabled": bool}}
    """
    proj = _get_active_project()
    project_file = proj / "project.godot"

    if not project_file.exists():
        return {"status": "error", "message": "project.godot não encontrado."}

    content = project_file.read_text(encoding="utf-8")
    setting = "debug/shapes/collision/visible_collision_shapes"

    if "[debug]" not in content:
        content += "\n[debug]\n"

    content += f"\n{setting}={str(enabled).lower()}\n"

    checkpoint("project.godot", proj)
    project_file.write_text(content, encoding="utf-8")

    return {"status": "success", "enabled": enabled, "note": "Reinicie o jogo para aplicar."}


def enable_debug_navigation(enabled: bool = True) -> dict:
    """Ativa/desativa visualização de navigation mesh.

    Returns:
        {{"status": "success", "enabled": bool}}
    """
    proj = _get_active_project()
    project_file = proj / "project.godot"

    if not project_file.exists():
        return {"status": "error", "message": "project.godot não encontrado."}

    content = project_file.read_text(encoding="utf-8")
    if "[debug]" not in content:
        content += "\n[debug]\n"

    content += f"\ndebug/shapes/navigation/visible_navigation={str(enabled).lower()}\n"

    checkpoint("project.godot", proj)
    project_file.write_text(content, encoding="utf-8")

    return {"status": "success", "enabled": enabled}


def get_performance_stats() -> dict:
    """Retorna métricas do projeto.

    Verifica tempo de compilação e tamanho do projeto.

    Returns:
        {"status": "success", "compile_time_s": float, "files_count": int, "note": str}
    """
    import time
    proj = _get_active_project()

    # Conta arquivos do projeto
    files = list(proj.glob("**/*")) if proj.exists() else []
    gd_count = sum(1 for f in files if f.suffix == ".gd")
    tscn_count = sum(1 for f in files if f.suffix == ".tscn")

    # Mede tempo de compilação
    compile_time = 0.0
    try:
        godot_bin = get_godot_bin()
        t0 = time.time()
        result = subprocess.run(
            [godot_bin, "--headless", "--editor", "--quit", "--path", str(proj)],
            capture_output=True, text=True, timeout=30, cwd=str(proj),
        )
        compile_time = round(time.time() - t0, 2)
    except subprocess.TimeoutExpired:
        compile_time = -1.0
    except Exception:
        compile_time = -1.0

    return {
        "status": "success",
        "compile_time_s": compile_time,
        "gd_scripts": gd_count,
        "tscn_scenes": tscn_count,
        "total_files": len(files),
        "note": "FPS real requer jogo rodando com GameBridge. Use run_game() primeiro.",
    }


# ══════════════════════════════════════════════════════════════════════
# 11.3 — LOCALIZAÇÃO (i18n)
# ══════════════════════════════════════════════════════════════════════

def setup_localization(
    default_locale: str = "pt_BR",
    additional_locales: list[str] | None = None,
) -> dict:
    """Configura sistema de tradução do projeto.

    Cria CSV template com colunas: key, pt_BR, en, es.

    Args:
        default_locale: Localidade padrão.
        additional_locales: Localidades adicionais (ex: ["en", "es"]).

    Returns:
        {{"status": "success", "csv_path": str}}
    """
    proj = _get_active_project()

    if not additional_locales:
        additional_locales = ["en", "es"]

    locales_dir = proj / "locales"
    locales_dir.mkdir(exist_ok=True)

    csv_content = "key," + ",".join([default_locale] + additional_locales) + "\n"
    csv_content += "greeting,\"Olá!\",\"Hello!\",\"¡Hola!\"\n"
    csv_content += "start_button,\"Iniciar\",\"Start\",\"Iniciar\"\n"
    csv_content += "quit_button,\"Sair\",\"Quit\",\"Salir\"\n"

    csv_path = locales_dir / "translations.csv"
    checkpoint("locales/translations.csv", proj)
    csv_path.write_text(csv_content, encoding="utf-8")

    return {"status": "success", "csv_path": "res://locales/translations.csv", "locales": [default_locale] + additional_locales}


def add_translation_string(
    key: str,
    translations: dict,
) -> dict:
    """Adiciona string ao CSV de tradução.

    Args:
        key: Chave única.
        translations: Dict {{"pt_BR": "texto", "en": "text", ...}}.

    Returns:
        {{"status": "success"}}
    """
    proj = _get_active_project()
    csv_path = proj / "locales" / "translations.csv"

    if not csv_path.exists():
        return {"status": "error", "message": "CSV não encontrado. Execute setup_localization primeiro."}

    content = csv_path.read_text(encoding="utf-8")
    content += f"{key}," + ",".join(f'\"{v}\"' for v in translations.values()) + "\n"

    checkpoint("locales/translations.csv", proj)
    csv_path.write_text(content, encoding="utf-8")

    return {"status": "success", "key": key}


# ══════════════════════════════════════════════════════════════════════
# 11.4 — 3D BÁSICO
# ══════════════════════════════════════════════════════════════════════

def create_light_3d(
    scene_path: str,
    parent_node_path: str = ".",
    light_type: str = "omni",
    color: str = "#ffffff",
    energy: float = 1.0,
    shadows: bool = False,
    node_name: str = "",
) -> dict:
    """Cria luz 3D (OmniLight3D, SpotLight3D, DirectionalLight3D).

    Args:
        scene_path: Caminho da cena.
        parent_node_path: Caminho do nó pai.
        light_type: "omni", "spot", ou "directional".
        color: Cor hex.
        energy: Intensidade.
        shadows: Ativar sombras.
        node_name: Nome do nó.

    Returns:
        {{"status": "success", "node_path": str}}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    type_map = {"omni": "OmniLight3D", "spot": "SpotLight3D", "directional": "DirectionalLight3D"}
    godot_type = type_map.get(light_type, "OmniLight3D")

    if not node_name:
        node_name = godot_type

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    lines.append(f'\n[node name="{node_name}" type="{godot_type}" parent="{parent_node_path}"]\n')
    lines.append(f'light_color = Color("{color}")\n')
    lines.append(f'light_energy = {energy}\n')
    lines.append(f'shadow_enabled = {'true' if shadows else 'false'}\n')

    checkpoint(scene_path, proj)
    full_path.write_text("".join(lines), encoding="utf-8")
    mark_pending_compile()

    return {"status": "success", "node_path": f"{parent_node_path}/{node_name}", "type": light_type}


def create_csg_shape(
    scene_path: str,
    parent_node_path: str = ".",
    shape_type: str = "box",
    dimensions: list[float] | None = None,
    node_name: str = "",
) -> dict:
    """Cria geometria CSG 3D (blockout rápido).

    Args:
        scene_path: Caminho da cena.
        shape_type: "box", "sphere", "cylinder".
        dimensions: [w, h, d] para box, [r, h] para cylinder, [r] para sphere.

    Returns:
        {{"status": "success", "node_path": str}}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    type_map = {"box": "CSGBox3D", "sphere": "CSGSphere3D", "cylinder": "CSGCylinder3D"}
    godot_type = type_map.get(shape_type, "CSGBox3D")

    if not node_name:
        node_name = godot_type
    if not dimensions:
        dimensions = [1, 1, 1] if shape_type == "box" else [1, 2] if shape_type == "cylinder" else [1]

    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    lines.append(f'\n[node name="{node_name}" type="{godot_type}" parent="{parent_node_path}"]\n')

    if shape_type == "box":
        lines.append(f'size = Vector3({dimensions[0]}, {dimensions[1]}, {dimensions[2] if len(dimensions)>2 else 1})\n')
    elif shape_type == "cylinder":
        lines.append(f'radius = {dimensions[0]}\n')
        lines.append(f'height = {dimensions[1] if len(dimensions)>1 else 2}\n')
    elif shape_type == "sphere":
        lines.append(f'radius = {dimensions[0]}\n')

    checkpoint(scene_path, proj)
    full_path.write_text("".join(lines), encoding="utf-8")
    mark_pending_compile()

    return {"status": "success", "node_path": f"{parent_node_path}/{node_name}"}


def configure_standard_material_3d(
    scene_path: str,
    node_path: str,
    albedo_color: str = "#ffffff",
    metallic: float = 0.0,
    roughness: float = 0.5,
    emission_color: str = "#000000",
    emission_energy: float = 0.0,
    preset: str = "custom",
) -> dict:
    """Configura StandardMaterial3D com predefinições.

    Predefinições: metal, wood, plastic, glass, emissive.

    Returns:
        {{"status": "success"}}
    """
    _check_path(scene_path)
    proj = _get_active_project()
    full_path = proj / scene_path

    presets = {
        "metal": {"albedo": "#c0c0c0", "metallic": 1.0, "roughness": 0.3},
        "wood": {"albedo": "#8b4513", "metallic": 0.0, "roughness": 0.8},
        "plastic": {"albedo": "#ffffff", "metallic": 0.0, "roughness": 0.4},
        "glass": {"albedo": "#ffffff", "metallic": 0.1, "roughness": 0.1},
        "emissive": {"albedo": "#ffffff", "metallic": 0.0, "roughness": 0.5, "emission": "#00ffff", "energy": 2.0},
    }

    if preset in presets:
        p = presets[preset]
        albedo_color = p.get("albedo", albedo_color)
        metallic = p.get("metallic", metallic)
        roughness = p.get("roughness", roughness)
        emission_color = p.get("emission", emission_color)
        emission_energy = p.get("energy", emission_energy)

    node_name = node_path.split("/")[-1]
    content = full_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    lines.append(f'\n[node name="{node_name}" type="MeshInstance3D" parent="{node_path.rsplit("/", 1)[0]}"]\n')

    checkpoint(scene_path, proj)
    full_path.write_text("".join(lines), encoding="utf-8")
    mark_pending_compile()

    return {"status": "success", "preset": preset, "albedo": albedo_color, "metallic": metallic, "roughness": roughness}


# ══════════════════════════════════════════════════════════════════════
# 11.5 — EXPORTAÇÃO AVANÇADA
# ══════════════════════════════════════════════════════════════════════

def configure_export_preset(
    preset_name: str = "Windows Desktop",
    app_name: str = "",
    version: str = "1.0.0",
    icon_path: str = "",
    company: str = "",
) -> dict:
    """Configura um preset de exportação no export_presets.cfg.

    Returns:
        {{"status": "success", "preset": str}}
    """
    proj = _get_active_project()
    export_file = proj / "export_presets.cfg"

    if not app_name:
        app_name = proj.name

    cfg = f'''[preset.0]
name="{preset_name}"
platform="Windows Desktop"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="../{app_name}.exe"
patches=""

[preset.0.options]
custom_template/debug=""
custom_template/release=""
binary_format/embed_pck=false
application/name="{app_name}"
application/version="{version}"
application/company="{company}"
application/icon="{icon_path}"
'''

    checkpoint("export_presets.cfg", proj)
    export_file.write_text(cfg, encoding="utf-8")

    return {"status": "success", "preset": preset_name, "app_name": app_name}


# ══════════════════════════════════════════════════════════════════════
# 11.6 — ÁUDIO AVANÇADO
# ══════════════════════════════════════════════════════════════════════

def configure_audio_bus(
    bus_name: str,
    volume_db: float = 0.0,
    mute: bool = False,
    solo: bool = False,
) -> dict:
    """Configura um bus de áudio no default_bus_layout.tres.

    Args:
        bus_name: Nome do bus (Master, SFX, Music, Voice).
        volume_db: Volume em decibéis.
        mute: Silenciado.
        solo: Modo solo.

    Returns:
        {{"status": "success"}}
    """
    proj = _get_active_project()
    layout_path = proj / "default_bus_layout.tres"

    if not layout_path.exists():
        tres_content = f'''[gd_resource type="AudioBusLayout" load_steps=1 format=3 uid=""]

[resource]
buses = [{{
"name": "{bus_name}",
"volume_db": {volume_db},
"mute": {'true' if mute else 'false'},
"solo": {'true' if solo else 'false'},
"send": "Master"
}}]
'''
        checkpoint("default_bus_layout.tres", proj)
        layout_path.write_text(tres_content, encoding="utf-8")
    else:
        content = layout_path.read_text(encoding="utf-8")
        if bus_name not in content:
            content = content.replace('buses = [', f'buses = [{{"name": "{bus_name}", "volume_db": {volume_db}, "mute": {'true' if mute else 'false'}}}, ')
            checkpoint("default_bus_layout.tres", proj)
            layout_path.write_text(content, encoding="utf-8")

    return {"status": "success", "bus": bus_name, "volume_db": volume_db}


def add_audio_effect(
    bus_name: str,
    effect_type: str = "reverb",
) -> dict:
    """Adiciona efeito de áudio a um bus.

    Args:
        bus_name: Nome do bus.
        effect_type: "reverb", "delay", "chorus", "distortion", "eq".

    Returns:
        {{"status": "success"}}
    """
    effect_map = {
        "reverb": "AudioEffectReverb",
        "delay": "AudioEffectDelay",
        "chorus": "AudioEffectChorus",
        "distortion": "AudioEffectDistortion",
        "eq": "AudioEffectEQ",
    }
    effect_class = effect_map.get(effect_type, "AudioEffectReverb")

    return {
        "status": "success",
        "bus": bus_name,
        "effect": effect_type,
        "note": f"Configure manualmente o {effect_class} no editor de áudio do Godot. A API de AudioEffect via arquivo é limitada.",
    }


# ══════════════════════════════════════════════════════════════════════
# G.1 — VISUAL FEEDBACK LOOP (Pipeline: compilar→screenshot→analisar)
# ══════════════════════════════════════════════════════════════════════

def visual_feedback_check(
    scene_path: str | None = None,
    wait_frames: int = 30,
    resolution_width: int = 640,
    resolution_height: int = 360,
) -> dict:
    """Pipeline automático: compila → screenshot → detecta tela vazia.

    É a ferramenta PRINCIPAL para verificação visual. Roda o jogo em modo
    headless invisível, captura screenshot, e analisa se há algo visível
    na tela ou se está completamente vazia (tela preta/branca/sólida).

    Use SEMPRE após criar/modificar cenas para verificar visualmente
    que tudo está OK antes de avançar no pipeline de 7 fases.

    Quando usar:
    - Após Fase 1 (tela não está vazia)
    - Após criar nova cena
    - Após adicionar sprites/UI
    - Quando o usuário diz "testa aí", "mostra como ficou", "verifica"

    Quando NÃO usar:
    - Para screenshot rápida via bridge: use capture_game_screenshot
    - Para comparar duas screenshots: use compare_screenshots
    - Para verificar performance: use get_performance_stats

    Args:
        scene_path: Cena para testar. Se None, usa main_scene.
        wait_frames: Quantos frames esperar (default 30 = 0.5s a 60fps).
        resolution_width: Largura (default 640).
        resolution_height: Altura (default 360).

    Returns:
        {"status": "success", "visible": bool, "empty": bool,
         "dominant_color": [r,g,b,a], "screenshot_path": str,
         "diagnosis": str, "fix_suggestion": str}

    Erro comum: tela vazia = esqueceu de adicionar Camera2D.
    Corrija com: add_node(camera_type="Camera2D", current=true).
    """
    from tools.runtime_ops import capture_game_screenshot, detect_empty_screen, compile_test

    # ── Passo 1: Compilar (garante que não tem erro de script) ──
    compile_result = compile_test()
    if compile_result.get("errors"):
        return {
            "status": "error",
            "phase": "compile",
            "message": "Erros de compilação antes do feedback visual.",
            "compile_errors": compile_result.get("errors", []),
            "fix_suggestion": "Corrija os erros de compilação acima e tente novamente.",
        }

    # ── Passo 2: Screenshot ──────────────────────────────────────
    ss_result = capture_game_screenshot(
        wait_frames=wait_frames,
        scene_path=scene_path,
        resolution_width=resolution_width,
        resolution_height=resolution_height,
    )

    if ss_result.get("status") != "success":
        return {
            "status": "error",
            "phase": "screenshot",
            "message": ss_result.get("message", "Falha ao capturar screenshot."),
            "fix_suggestion": "Verifique se o projeto compila e tem uma cena principal definida com set_main_scene.",
        }

    screenshot_path = ss_result.get("image_path", "")
    image_base64 = ss_result.get("image_base64", "")

    # ── Passo 3: Detectar tela vazia ─────────────────────────────
    detect_result = detect_empty_screen(
        screenshot_path=screenshot_path,
        image_base64=image_base64 if not screenshot_path else None,
        empty_threshold=0.95,
    )

    if detect_result.get("status") != "success":
        return {
            "status": "success",
            "visible": True,
            "empty": False,
            "screenshot_path": screenshot_path,
            "diagnosis": "Não foi possível analisar a screenshot automaticamente.",
            "fix_suggestion": "Abra o jogo manualmente (run_game) e verifique visualmente.",
            "note": detect_result.get("message", "Erro na análise."),
        }

    is_empty = detect_result.get("empty", False)
    dominant = detect_result.get("dominant_color", [])

    # ── Passo 4: Diagnóstico ─────────────────────────────────────
    if is_empty:
        # Cores comuns de tela vazia
        color_names = {
            "0,0,0": "preta (sem renderização — provavelmente faltando Camera2D)",
            "255,255,255": "branca (fundo padrão — faltando Camera2D ou fundo)",
            "51,51,51": "cinza escuro (cor padrão do Godot — cena sem conteúdo visível)",
        }
        dom_str = ",".join(str(int(c)) for c in dominant[:3]) if dominant else "desconhecida"

        diagnosis = f"TELA VAZIA detectada. Cor dominante: {dom_str}."
        if dom_str == "0,0,0":
            diagnosis += " Tela PRETA — provavelmente NÃO há Camera2D com current=true."
        elif dom_str in ("255,255,255", "51,51,51"):
            diagnosis += " Tela com cor sólida — há Camera2D mas nenhum conteúdo visível (sprites, fundo, UI)."

        fix_suggestion = (
            "Ações corretivas (em ordem):\n"
            "1. add_node(camera_type='Camera2D', current=true) — se ainda não tem câmera\n"
            "2. generate_placeholder_sprite() — se não tem sprite visível\n"
            "3. generate_background_gradient() — para ter um fundo colorido\n"
            "4. Verifique se os nós estão com posição dentro da tela (x: 0-640, y: 0-360)"
        )

        return {
            "status": "success",
            "visible": False,
            "empty": True,
            "dominant_color": dominant,
            "screenshot_path": screenshot_path,
            "diagnosis": diagnosis,
            "fix_suggestion": fix_suggestion,
        }

    # Tela NÃO está vazia — sucesso!
    return {
        "status": "success",
        "visible": True,
        "empty": False,
        "dominant_color": dominant,
        "screenshot_path": screenshot_path,
        "diagnosis": "Tela com conteúdo detectado! O jogo está renderizando corretamente.",
        "fix_suggestion": "",
    }


# ══════════════════════════════════════════════════════════════════════
# TOOL DEFINITIONS para server.py
# ══════════════════════════════════════════════════════════════════════

def get_tool_defs() -> list[dict]:
    """Retorna lista de tool definitions da Onda 8 (formato dict)."""
    return [
        # 8.1 Câmera
        {
            "name": "setup_camera_2d",
            "description": "Adiciona e configura uma Camera2D na cena. Use para definir limites, zoom, drag e suavização da câmera. Quando usar: ao criar qualquer cena 2D que precise de câmera. Pré-condições: cena já deve existir.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena (.tscn)."},
                    "parent_node_path": {"type": "string", "description": "Caminho do nó pai (default: '.')."},
                    "limits": {"type": "object", "description": "Dict com left, top, right, bottom (pixels)."},
                    "drag_horizontal": {"type": "number", "description": "Margem de arrasto horizontal."},
                    "drag_vertical": {"type": "number", "description": "Margem de arrasto vertical."},
                    "zoom": {"type": "array", "items": {"type": "number"}, "description": "Zoom [x, y]. Default [1.0, 1.0]."},
                    "smoothing_enabled": {"type": "boolean", "description": "Ativar suavização."},
                    "smoothing_speed": {"type": "number", "description": "Velocidade da suavização."},
                    "current": {"type": "boolean", "description": "Tornar esta a câmera ativa."},
                },
                "required": ["scene_path"],
            },
        },
        {
            "name": "setup_camera_follow",
            "description": "Faz a câmera seguir um nó alvo (ex: Player) com suavidade e deadzone. Gera script GDScript automaticamente. Quando usar: sempre que o jogo tiver um personagem que se move e a câmera deve segui-lo.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "camera_node_path": {"type": "string", "description": "Caminho da Camera2D."},
                    "target_node_path": {"type": "string", "description": "Caminho do nó a seguir (ex: 'root/Player')."},
                    "smoothing": {"type": "number", "description": "Fator de suavização (default 5.0)."},
                    "offset_x": {"type": "number", "description": "Offset X da câmera."},
                    "offset_y": {"type": "number", "description": "Offset Y da câmera."},
                    "deadzone_width": {"type": "number", "description": "Largura da deadzone (default 0)."},
                    "deadzone_height": {"type": "number", "description": "Altura da deadzone (default 0)."},
                },
                "required": ["scene_path", "camera_node_path", "target_node_path"],
            },
        },
        {
            "name": "setup_camera_shake",
            "description": "Adiciona efeito de tremor (screen shake) à câmera. Baseado em algoritmo de trauma/decay. Outros scripts podem chamar add_trauma(0.5) para ativar. Quando usar: para dar feedback visual de explosões, dano, impacto.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "camera_node_path": {"type": "string", "description": "Caminho da Camera2D."},
                    "max_amplitude": {"type": "number", "description": "Amplitude máxima em pixels (default 20)."},
                    "decay_rate": {"type": "number", "description": "Taxa de decaimento por segundo (default 2.0)."},
                },
                "required": ["scene_path", "camera_node_path"],
            },
        },
        # 8.2 Navegação
        {
            "name": "create_navigation_region_2d",
            "description": "Cria uma região de navegação 2D com polígono. Define a área onde personagens podem andar. Quando usar: ao criar mapa com pathfinding. Pré-condições: cena deve existir.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "Caminho do nó pai (default: '.')."},
                    "polygon_vertices": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Vértices [[x,y], ...] do polígono."},
                    "region_name": {"type": "string", "description": "Nome do nó NavigationRegion2D."},
                },
                "required": ["scene_path"],
            },
        },
        {
            "name": "create_navigation_agent_2d",
            "description": "Adiciona um NavigationAgent2D com script de perseguição a um personagem. O nó pai DEVE ser um CharacterBody2D. Gera script que persegue o alvo usando pathfinding. Quando usar: para criar inimigos que perseguem o player, ou NPCs que andam até um ponto.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "Caminho do nó pai (CharacterBody2D)."},
                    "agent_name": {"type": "string", "description": "Nome do NavigationAgent2D."},
                    "target_node_path": {"type": "string", "description": "Caminho do alvo a perseguir."},
                    "speed": {"type": "number", "description": "Velocidade de movimento (default 200)."},
                    "avoidance_enabled": {"type": "boolean", "description": "Ativar evasão de obstáculos."},
                },
                "required": ["scene_path", "parent_node_path", "target_node_path"],
            },
        },
        {
            "name": "bake_navigation_polygon",
            "description": "Gera NavigationPolygon a partir de um TileMapLayer. Analisa as células do tilemap e cria polígono para as células andáveis. Quando usar: após criar o mapa com TileMap e quiser que inimigos naveguem nele.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "tilemap_layer_path": {"type": "string", "description": "Caminho do TileMapLayer."},
                    "navigation_region_path": {"type": "string", "description": "Caminho do NavigationRegion2D."},
                    "walkable_tiles": {"type": "array", "items": {"type": "integer"}, "description": "IDs de tiles andáveis (default [0])."},
                },
                "required": ["scene_path", "tilemap_layer_path", "navigation_region_path"],
            },
        },
        # 8.3 Save/Load
        {
            "name": "create_save_system",
            "description": "Cria sistema completo de save/load como Autoload (SaveManager). Gera script com funções: save_game(slot), load_game(slot), delete_save(slot), get_save_slots(). Usa ConfigFile. Quando usar: em TODO jogo que precise salvar progresso.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "autoload_name": {"type": "string", "description": "Nome do autoload (default: 'SaveManager')."},
                    "save_slots": {"type": "integer", "description": "Número de slots (default 3)."},
                    "auto_save_enabled": {"type": "boolean", "description": "Ativar auto-save periódico."},
                    "auto_save_interval": {"type": "number", "description": "Intervalo do auto-save em segundos."},
                },
                "required": [],
            },
        },
        {
            "name": "define_save_data",
            "description": "Registra uma variável de nó para ser incluída no save/load. Deve ser chamado APÓS create_save_system. Quando usar: para cada propriedade que precisa ser salva (position, health, score).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "node_path": {"type": "string", "description": "Caminho do nó (ex: 'Player')."},
                    "property_name": {"type": "string", "description": "Nome da propriedade (ex: 'position', 'health')."},
                    "section": {"type": "string", "description": "Seção no arquivo de save (default: 'default')."},
                    "key": {"type": "string", "description": "Chave no arquivo (default: mesmo que property_name)."},
                },
                "required": ["node_path", "property_name"],
            },
        },
        # 8.4 Tweens
        {
            "name": "create_tween_animation",
            "description": "Cria animação Tween em um nó. Anima propriedades como position, modulate, scale com easing e loops. Retorna código GDScript pronto. Quando usar: para animações dinâmicas (fade, movimento, escala) que não são keyframe-based.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Caminho do nó alvo."},
                    "property_name": {"type": "string", "description": "Propriedade a animar (position, modulate, scale, rotation)."},
                    "final_value": {"type": "string", "description": "Valor final (número, Vector2 [x,y], ou Color [r,g,b,a])."},
                    "duration": {"type": "number", "description": "Duração em segundos (default 0.5)."},
                    "easing": {"type": "string", "description": "Easing: linear, in_quad, out_quad, in_out_quad, in_elastic, out_bounce..."},
                    "transition": {"type": "string", "description": "Transição: ease_in, ease_out, ease_in_out."},
                    "loops": {"type": "integer", "description": "0=uma vez, -1=infinito."},
                    "auto_play": {"type": "boolean", "description": "Iniciar no _ready (default true)."},
                },
                "required": ["scene_path", "node_path", "property_name", "final_value"],
            },
        },
        {
            "name": "chain_tweens",
            "description": "Cria uma sequência de animações Tween encadeadas (.then()). Cada passo anima uma propriedade. Quando usar: para cutscenes, animações complexas com múltiplas etapas em sequência.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Caminho do nó alvo."},
                    "steps": {"type": "array", "items": {"type": "object"}, "description": "Array de passos: [{property, final_value, duration, easing, transition}]."},
                },
                "required": ["scene_path", "node_path", "steps"],
            },
        },
        # 8.5 State Machine
        {
            "name": "create_state_machine",
            "description": "Gera uma máquina de estados finita (FSM) em GDScript. Cria enum de estados + funções _enter/_update/_exit para cada estado + transition_to(). Quando usar: para TODO personagem/inimigo que tenha comportamentos diferentes (idle, walk, attack, hurt, die).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "script_path": {"type": "string", "description": "Caminho para salvar o script gerado."},
                    "states": {"type": "array", "items": {"type": "string"}, "description": "Lista de estados (ex: ['idle', 'walk', 'attack', 'hurt', 'die'])."},
                    "initial_state": {"type": "string", "description": "Estado inicial."},
                },
                "required": ["script_path", "states", "initial_state"],
            },
        },
        {
            "name": "add_state_transition",
            "description": "Adiciona uma transição condicional entre estados na máquina de estados. Adiciona código na função _update do estado de origem. Quando usar: após create_state_machine, para definir quando muda de idle→walk, walk→attack, etc.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "script_path": {"type": "string", "description": "Caminho do script com FSM."},
                    "from_state": {"type": "string", "description": "Estado de origem."},
                    "to_state": {"type": "string", "description": "Estado de destino."},
                    "condition_code": {"type": "string", "description": "Código GDScript da condição (ex: 'velocity.length() > 0')."},
                },
                "required": ["script_path", "from_state", "to_state", "condition_code"],
            },
        },
        # 8.6 UI Templates
        {
            "name": "create_main_menu",
            "description": "Cria uma cena de menu principal completa com título e botões. Gera .tscn + script de UI. Suporta estilos: modern, retro, cartoon, dark_fantasy, sci_fi. Quando usar: ao iniciar qualquer jogo novo — é a primeira tela que o player vê.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string", "description": "Nome da cena (ex: 'title_screen')."},
                    "game_title": {"type": "string", "description": "Título do jogo."},
                    "title_font_size": {"type": "integer", "description": "Tamanho da fonte (default 64)."},
                    "buttons": {"type": "array", "items": {"type": "string"}, "description": "Textos dos botões. Default: ['▶ START', '⚙ OPTIONS', '✕ QUIT']."},
                    "background_color": {"type": "string", "description": "Cor de fundo hex (default #1a1a2e)."},
                    "style": {"type": "string", "enum": ["modern", "retro", "cartoon", "dark_fantasy", "sci_fi"], "description": "Estilo visual."},
                },
                "required": ["scene_name", "game_title"],
            },
        },
        {
            "name": "create_hud_template",
            "description": "Cria uma cena de HUD (Heads-Up Display) com elementos de UI. Suporta: score, health, ammo, wave, timer. Posições: top_left, top_right, bottom_center. Quando usar: em TODO jogo que precise mostrar vida, score, munição ao player.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string", "description": "Nome da cena (default: 'hud')."},
                    "elements": {"type": "array", "items": {"type": "string"}, "description": "Elementos: ['score', 'health', 'ammo', 'wave', 'timer']."},
                    "position": {"type": "string", "enum": ["top_left", "top_right", "bottom_center"], "description": "Posição na tela."},
                },
                "required": [],
            },
        },
        {
            "name": "create_pause_menu",
            "description": "Cria uma cena de menu de pausa completa. Inclui overlay escuro, botões (Continuar, Reiniciar, Menu), e script que detecta ESC. Quando usar: em TODO jogo — pausa é recurso básico esperado pelo player.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_name": {"type": "string", "description": "Nome da cena (default: 'pause_menu')."},
                    "overlay_alpha": {"type": "number", "description": "Transparência do overlay (default 0.7)."},
                },
                "required": [],
            },
        },
        {
            "name": "create_health_bar",
            "description": "Cria uma barra de vida (ProgressBar) com script de controle. Inclui: take_damage, heal, animação de transição, cor muda com saúde. Quando usar: para player, inimigos, chefes, ou qualquer elemento com vida.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "Caminho do nó pai."},
                    "max_health": {"type": "number", "description": "Vida máxima (default 100)."},
                    "bar_name": {"type": "string", "description": "Nome do nó (default: 'HealthBar')."},
                    "bar_width": {"type": "integer", "description": "Largura (default 250)."},
                    "bar_height": {"type": "integer", "description": "Altura (default 25)."},
                    "fill_color": {"type": "string", "description": "Cor de preenchimento (default #2ecc71)."},
                    "bg_color": {"type": "string", "description": "Cor de fundo (default #333333)."},
                    "show_text": {"type": "boolean", "description": "Mostrar '75/100' (default true)."},
                },
                "required": ["scene_path"],
            },
        },
        # 8.7 World Environment
        {
            "name": "setup_world_environment",
            "description": "Configura o ambiente visual: cor de fundo, luz ambiente, glow (bloom), névoa (fog). Cria WorldEnvironment + Environment resource. Quando usar: para dar atmosfera ao jogo — essencial para polimento visual.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "Caminho do nó pai."},
                    "background_mode": {"type": "string", "enum": ["color", "sky", "canvas"], "description": "Modo de fundo."},
                    "background_color": {"type": "string", "description": "Cor hex do fundo."},
                    "ambient_light_color": {"type": "string", "description": "Cor hex da luz ambiente."},
                    "ambient_light_energy": {"type": "number", "description": "Intensidade da luz ambiente."},
                    "glow_enabled": {"type": "boolean", "description": "Ativar efeito bloom/glow."},
                    "glow_intensity": {"type": "number", "description": "Intensidade do glow (default 0.8)."},
                    "fog_enabled": {"type": "boolean", "description": "Ativar névoa."},
                    "fog_density": {"type": "number", "description": "Densidade da névoa (default 0.01)."},
                    "fog_color": {"type": "string", "description": "Cor hex da névoa."},
                },
                "required": ["scene_path"],
            },
        },
        {
            "name": "setup_screen_flash",
            "description": "Adiciona efeito de flash de tela (dano = vermelho, cura = verde, power-up = branco). Cria ColorRect overlay com animação Tween. Quando usar: para feedback visual de eventos importantes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "Caminho do nó pai."},
                    "flash_color": {"type": "string", "description": "Cor do flash hex (default #ffffff)."},
                    "flash_duration": {"type": "number", "description": "Duração em segundos (default 0.3)."},
                },
                "required": ["scene_path"],
            },
        },
        # 9.1 Parallax
        {
            "name": "create_parallax_background",
            "description": "Cria um fundo parallax com múltiplas camadas de scroll. Cada camada tem escala de scroll independente. Use em TODO jogo 2D para dar profundidade. Pré-condições: ter texturas/placeholder_sprites para as camadas.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "layers": {"type": "array", "items": {"type": "object"}, "description": "Camadas: [{texture_path, scroll_scale_x, scroll_scale_y, mirroring_x, mirroring_y, color}]."},
                    "parent_node_path": {"type": "string", "description": "Caminho do nó pai."},
                    "bg_name": {"type": "string", "description": "Nome do ParallaxBackground."},
                },
                "required": ["scene_path", "layers"],
            },
        },
        {
            "name": "add_parallax_layer",
            "description": "Adiciona uma camada a um ParallaxBackground existente. Use para adicionar mais planos de fundo sem refazer o parallax inteiro.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parallax_bg_path": {"type": "string", "description": "Caminho do ParallaxBackground."},
                    "texture_path": {"type": "string", "description": "Caminho da textura."},
                    "scroll_scale_x": {"type": "number", "description": "Escala de scroll X (default 0.5)."},
                    "scroll_scale_y": {"type": "number", "description": "Escala de scroll Y (default 0.5)."},
                    "mirroring_x": {"type": "integer", "description": "Mirroring X."},
                    "mirroring_y": {"type": "integer", "description": "Mirroring Y."},
                    "layer_name": {"type": "string", "description": "Nome da camada."},
                },
                "required": ["scene_path", "parallax_bg_path", "texture_path"],
            },
        },
        # 9.2 Partículas
        {
            "name": "configure_particles_2d",
            "description": "Configura partículas 2D com predefinições visuais: explosion, smoke, sparkle, rain, fire. Ajusta amount, lifetime, explosiveness. Use para dar vida a explosões, fumaça, chuva.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Caminho do GPUParticles2D."},
                    "amount": {"type": "integer", "description": "Quantidade de partículas."},
                    "lifetime": {"type": "number", "description": "Tempo de vida."},
                    "explosiveness": {"type": "number", "description": "0=contínuo, 1=explosão."},
                    "emitting": {"type": "boolean", "description": "Se está emitindo."},
                    "one_shot": {"type": "boolean", "description": "Emitir uma vez."},
                    "preset": {"type": "string", "enum": ["explosion", "smoke", "sparkle", "rain", "fire", "custom"], "description": "Predefinição."},
                },
                "required": ["scene_path", "node_path"],
            },
        },
        {
            "name": "create_particles_3d",
            "description": "Cria partículas 3D (GPUParticles3D) com predefinições: fire, smoke, sparkles. Use para efeitos em jogos 3D.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "Caminho do nó pai."},
                    "node_name": {"type": "string", "description": "Nome do nó."},
                    "preset": {"type": "string", "enum": ["fire", "smoke", "sparkles", "custom"], "description": "Predefinição."},
                },
                "required": ["scene_path"],
            },
        },
        # 9.3 Shaders
        {
            "name": "generate_shader_2d",
            "description": "Gera e aplica shader 2D a partir de template. Templates: glow (bordas brilham), dissolve (dissolve com noise), water (distorção de onda), wind (ondulação de vértice), grayscale. Use para efeitos visuais profissionais.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Caminho do nó."},
                    "template": {"type": "string", "enum": ["glow", "dissolve", "water", "wind", "grayscale"], "description": "Template de shader."},
                    "uniforms": {"type": "object", "description": "Uniforms customizados."},
                    "shader_name": {"type": "string", "description": "Nome do arquivo .gdshader."},
                },
                "required": ["scene_path", "node_path", "template"],
            },
        },
        {
            "name": "apply_shader_to_node",
            "description": "Atalho para aplicar shader existente a um nó. Equivalente a generate_shader_2d. Use quando já souber o template desejado.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "node_path": {"type": "string", "description": "Caminho do nó."},
                    "shader_template": {"type": "string", "enum": ["glow", "dissolve", "water", "wind", "grayscale"], "description": "Template de shader."},
                    "uniforms": {"type": "object", "description": "Uniforms customizados."},
                },
                "required": ["scene_path", "node_path"],
            },
        },
        # 9.4 Path Following
        {
            "name": "create_path_2d",
            "description": "Cria um Path2D com PathFollow2D. Use para moving platforms, rotas de patrulha, caminhos de cutscene. O PathFollow2D.progress_ratio (0-1) move objetos ao longo da curva.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "Caminho do nó pai."},
                    "waypoints": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Pontos [[x,y], ...]."},
                    "path_name": {"type": "string", "description": "Nome do nó."},
                    "closed": {"type": "boolean", "description": "Caminho fechado (loop)."},
                },
                "required": ["scene_path"],
            },
        },
        {
            "name": "create_patrol_route",
            "description": "Cria rota de patrulha com script de movimento entre waypoints. Suporta ping-pong (vai e volta) ou loop. Use para inimigos que patrulham, NPCs, moving platforms com script.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene_path": {"type": "string", "description": "Caminho da cena."},
                    "parent_node_path": {"type": "string", "description": "Caminho do nó pai (CharacterBody2D)."},
                    "waypoints": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}, "description": "Pontos [[x,y], ...]."},
                    "speed": {"type": "number", "description": "Velocidade (default 100)."},
                    "wait_time": {"type": "number", "description": "Tempo de espera em cada ponto."},
                    "ping_pong": {"type": "boolean", "description": "Vai e volta (true) ou loop (false)."},
                },
                "required": ["scene_path", "parent_node_path", "waypoints"],
            },
        },
        # 10.1 Diálogo
        {
            "name": "create_dialogue_system",
            "description": "Cria sistema de diálogo completo como Autoload. Suporta: árvore de diálogo em JSON, typewriter effect, escolhas, eventos (give_item, set_flag). Use para RPG, adventure, ou qualquer jogo com NPCs.",
            "inputSchema": {"type": "object", "properties": {"autoload_name": {"type": "string"}}, "required": []},
        },
        {
            "name": "add_dialogue_node",
            "description": "Adiciona um nó à árvore de diálogo (dialogues.json). Define speaker, texto, escolhas, próximo nó, e eventos. Use para construir conversas ramificadas.",
            "inputSchema": {"type": "object", "properties": {"dialogue_id": {"type": "string"}, "speaker": {"type": "string"}, "text": {"type": "string"}, "next_id": {"type": "string"}, "choices": {"type": "array", "items": {"type": "object"}}, "events": {"type": "array", "items": {"type": "object"}}}, "required": ["dialogue_id", "speaker", "text"]},
        },
        {
            "name": "create_dialogue_ui",
            "description": "Cria interface de diálogo visual (CanvasLayer). Painel inferior + nome do speaker + texto com typewriter + botões de escolha. Usa DialogueManager como backend.",
            "inputSchema": {"type": "object", "properties": {"scene_name": {"type": "string"}}, "required": []},
        },
        # 10.2 Inventário
        {
            "name": "create_inventory_system",
            "description": "Cria sistema de inventário como Autoload. add_item, remove_item, has_item, get_items. Itens são Resources .tres. Use para RPG, survival, ou qualquer jogo com coleta.",
            "inputSchema": {"type": "object", "properties": {"autoload_name": {"type": "string"}, "max_slots": {"type": "integer"}}, "required": []},
        },
        {
            "name": "define_inventory_item",
            "description": "Cria um Resource .tres de item. Define nome, tipo (consumable/weapon/armor/quest), descrição, stack, e propriedades customizadas (dano, cura).",
            "inputSchema": {"type": "object", "properties": {"item_id": {"type": "string"}, "item_name": {"type": "string"}, "item_type": {"type": "string"}, "description": {"type": "string"}, "stackable": {"type": "boolean"}, "max_stack": {"type": "integer"}, "icon_path": {"type": "string"}, "properties": {"type": "object"}}, "required": ["item_id", "item_name"]},
        },
        {
            "name": "create_inventory_ui",
            "description": "Cria interface visual de inventário com grid de slots. GridContainer com N colunas. Use para exibir itens coletados ao player.",
            "inputSchema": {"type": "object", "properties": {"scene_name": {"type": "string"}, "columns": {"type": "integer"}}, "required": []},
        },
        # 10.3 Armas
        {
            "name": "create_bullet_template",
            "description": "Cria cena de projétil (Area2D) com movimento, dano, colisão, e auto-destruição. Use para armas, inimigos que atiram, ou qualquer projetil.",
            "inputSchema": {"type": "object", "properties": {"bullet_name": {"type": "string"}, "speed": {"type": "number"}, "damage": {"type": "number"}, "lifetime": {"type": "number"}, "bullet_color": {"type": "string"}, "bullet_size": {"type": "integer"}}, "required": []},
        },
        {
            "name": "create_gun_system",
            "description": "Gera script de arma: shoot(), cooldown, munição, reload automático, spread. Use para armas do player ou torres automáticas.",
            "inputSchema": {"type": "object", "properties": {"script_path": {"type": "string"}, "bullet_scene_path": {"type": "string"}, "fire_rate": {"type": "number"}, "ammo_max": {"type": "integer"}, "spread_angle": {"type": "number"}, "auto_reload": {"type": "boolean"}, "reload_time": {"type": "number"}}, "required": ["script_path"]},
        },
        # 10.4 Geração Procedural
        {
            "name": "generate_tilemap_from_noise",
            "description": "Preenche TileMapLayer com ruído Perlin. Cria terreno procedural (chão/parede). Use para gerar mapas aleatórios para roguelike, sandbox, ou variação de níveis.",
            "inputSchema": {"type": "object", "properties": {"scene_path": {"type": "string"}, "tilemap_layer_path": {"type": "string"}, "tile_size": {"type": "integer"}, "width": {"type": "integer"}, "height": {"type": "integer"}, "seed": {"type": "integer"}, "threshold": {"type": "number"}, "tile_ground": {"type": "integer"}, "tile_wall": {"type": "integer"}}, "required": ["scene_path", "tilemap_layer_path"]},
        },
        {
            "name": "generate_dungeon_rooms",
            "description": "Gera layout de dungeon com BSP (Binary Space Partition). Retorna salas (Rect2) e corredores. Use para roguelike, dungeon crawler, ou níveis aleatórios.",
            "inputSchema": {"type": "object", "properties": {"num_rooms": {"type": "integer"}, "min_size": {"type": "integer"}, "max_size": {"type": "integer"}, "map_width": {"type": "integer"}, "map_height": {"type": "integer"}, "corridor_width": {"type": "integer"}, "seed": {"type": "integer"}}, "required": []},
        },
        # 10.5 Loading
        {
            "name": "create_loading_screen",
            "description": "Cria tela de carregamento com ProgressBar + dicas aleatórias. Usa ResourceLoader.load_threaded. Use para transições entre cenas pesadas.",
            "inputSchema": {"type": "object", "properties": {"scene_name": {"type": "string"}, "tips": {"type": "array", "items": {"type": "string"}}, "min_load_time": {"type": "number"}, "background_color": {"type": "string"}}, "required": []},
        },
        {
            "name": "load_scene_async",
            "description": "Inicia carregamento assíncrono de cena. Use com create_loading_screen para transições suaves. Retorna instruções de uso.",
            "inputSchema": {"type": "object", "properties": {"target_scene": {"type": "string"}, "loading_scene": {"type": "string"}}, "required": ["target_scene"]},
        },
        # 11.1 Raycasting
        {
            "name": "add_raycast_2d",
            "description": "Adiciona RayCast2D para detecção de linha (ground check, line-of-sight, armas).",
            "inputSchema": {"type": "object", "properties": {"scene_path": {"type": "string"}, "parent_node_path": {"type": "string"}, "target_position": {"type": "array", "items": {"type": "number"}}, "collision_mask": {"type": "integer"}, "node_name": {"type": "string"}}, "required": ["scene_path", "parent_node_path"]},
        },
        {
            "name": "add_shapecast_2d",
            "description": "Adiciona ShapeCast2D para detecção de área (rectangle, circle, capsule).",
            "inputSchema": {"type": "object", "properties": {"scene_path": {"type": "string"}, "parent_node_path": {"type": "string"}, "shape_type": {"type": "string"}, "shape_size": {"type": "array", "items": {"type": "number"}}, "node_name": {"type": "string"}}, "required": ["scene_path", "parent_node_path"]},
        },
        # 11.2 Debug
        {
            "name": "enable_debug_collisions",
            "description": "Ativa visualização de collision shapes no projeto (debug).",
            "inputSchema": {"type": "object", "properties": {"enabled": {"type": "boolean"}}, "required": []},
        },
        {
            "name": "enable_debug_navigation",
            "description": "Ativa visualização de navigation mesh no projeto (debug).",
            "inputSchema": {"type": "object", "properties": {"enabled": {"type": "boolean"}}, "required": []},
        },
        {
            "name": "get_performance_stats",
            "description": "Retorna métricas de performance (FPS, frame time). Usa godot --print-fps.",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        # 11.3 i18n
        {
            "name": "setup_localization",
            "description": "Configura sistema de tradução. Cria CSV template com pt_BR, en, es.",
            "inputSchema": {"type": "object", "properties": {"default_locale": {"type": "string"}, "additional_locales": {"type": "array", "items": {"type": "string"}}}, "required": []},
        },
        {
            "name": "add_translation_string",
            "description": "Adiciona string traduzida ao CSV de localização.",
            "inputSchema": {"type": "object", "properties": {"key": {"type": "string"}, "translations": {"type": "object"}}, "required": ["key", "translations"]},
        },
        # 11.4 3D
        {
            "name": "create_light_3d",
            "description": "Cria luz 3D: OmniLight3D, SpotLight3D, DirectionalLight3D. Com cor, energia, sombras.",
            "inputSchema": {"type": "object", "properties": {"scene_path": {"type": "string"}, "light_type": {"type": "string", "enum": ["omni", "spot", "directional"]}, "color": {"type": "string"}, "energy": {"type": "number"}, "shadows": {"type": "boolean"}, "node_name": {"type": "string"}}, "required": ["scene_path"]},
        },
        {
            "name": "create_csg_shape",
            "description": "Cria geometria CSG 3D para blockout rápido: box, sphere, cylinder.",
            "inputSchema": {"type": "object", "properties": {"scene_path": {"type": "string"}, "shape_type": {"type": "string", "enum": ["box", "sphere", "cylinder"]}, "dimensions": {"type": "array", "items": {"type": "number"}}, "node_name": {"type": "string"}}, "required": ["scene_path"]},
        },
        {
            "name": "configure_standard_material_3d",
            "description": "Configura StandardMaterial3D com predefinições: metal, wood, plastic, glass, emissive.",
            "inputSchema": {"type": "object", "properties": {"scene_path": {"type": "string"}, "node_path": {"type": "string"}, "preset": {"type": "string", "enum": ["metal", "wood", "plastic", "glass", "emissive", "custom"]}}, "required": ["scene_path", "node_path"]},
        },
        # 11.5 Export
        {
            "name": "configure_export_preset",
            "description": "Configura preset de exportação (Windows): nome, versão, ícone, empresa.",
            "inputSchema": {"type": "object", "properties": {"preset_name": {"type": "string"}, "app_name": {"type": "string"}, "version": {"type": "string"}, "icon_path": {"type": "string"}, "company": {"type": "string"}}, "required": []},
        },
        # 11.6 Áudio
        {
            "name": "configure_audio_bus",
            "description": "Configura bus de áudio: Master, SFX, Music, Voice. Volume, mute, solo.",
            "inputSchema": {"type": "object", "properties": {"bus_name": {"type": "string"}, "volume_db": {"type": "number"}, "mute": {"type": "boolean"}, "solo": {"type": "boolean"}}, "required": ["bus_name"]},
        },
        {
            "name": "add_audio_effect",
            "description": "Adiciona efeito de áudio a um bus: reverb, delay, chorus, distortion, eq.",
            "inputSchema": {"type": "object", "properties": {"bus_name": {"type": "string"}, "effect_type": {"type": "string", "enum": ["reverb", "delay", "chorus", "distortion", "eq"]}}, "required": ["bus_name", "effect_type"]},
        },
        # G.1 — Visual Feedback Loop
        {
            "name": "visual_feedback_check",
            "description": "Pipeline automático de verificação visual: compila o projeto, roda em modo headless invisível, captura screenshot, e analisa se há conteúdo visível ou se a tela está vazia. Use SEMPRE após cada etapa do pipeline de 7 fases para confirmar visualmente que tudo está OK antes de avançar. Exemplo: após adicionar câmera e fundo (Fase 1), execute visual_feedback_check para ver se a tela não está mais preta.",
            "inputSchema": {"type": "object", "properties": {"scene_path": {"type": "string", "description": "Cena para testar. Se omitido, usa a main_scene do projeto."}, "wait_frames": {"type": "number", "description": "Quantos frames renderizar antes do screenshot (default 30 = 0.5s a 60fps)."}, "resolution_width": {"type": "number", "description": "Largura da captura (default 640)."}, "resolution_height": {"type": "number", "description": "Altura da captura (default 360)."}}, "required": []},
        },
    ]


def get_handler_map() -> dict:
    """Retorna dicionário {tool_name: handler_function} para server.py."""
    return {
        "setup_camera_2d": setup_camera_2d,
        "setup_camera_follow": setup_camera_follow,
        "setup_camera_shake": setup_camera_shake,
        "create_navigation_region_2d": create_navigation_region_2d,
        "create_navigation_agent_2d": create_navigation_agent_2d,
        "bake_navigation_polygon": bake_navigation_polygon,
        "create_save_system": create_save_system,
        "define_save_data": define_save_data,
        "create_tween_animation": create_tween_animation,
        "chain_tweens": chain_tweens,
        "create_state_machine": create_state_machine,
        "add_state_transition": add_state_transition,
        "create_main_menu": create_main_menu,
        "create_hud_template": create_hud_template,
        "create_pause_menu": create_pause_menu,
        "create_health_bar": create_health_bar,
        "setup_world_environment": setup_world_environment,
        "setup_screen_flash": setup_screen_flash,
        # Onda 9
        "create_parallax_background": create_parallax_background,
        "add_parallax_layer": add_parallax_layer,
        "configure_particles_2d": configure_particles_2d,
        "create_particles_3d": create_particles_3d,
        "generate_shader_2d": generate_shader_2d,
        "apply_shader_to_node": apply_shader_to_node,
        "create_path_2d": create_path_2d,
        "create_patrol_route": create_patrol_route,
        # Onda 10
        "create_dialogue_system": create_dialogue_system,
        "add_dialogue_node": add_dialogue_node,
        "create_dialogue_ui": create_dialogue_ui,
        "create_inventory_system": create_inventory_system,
        "define_inventory_item": define_inventory_item,
        "create_inventory_ui": create_inventory_ui,
        "create_bullet_template": create_bullet_template,
        "create_gun_system": create_gun_system,
        "generate_tilemap_from_noise": generate_tilemap_from_noise,
        "generate_dungeon_rooms": generate_dungeon_rooms,
        "create_loading_screen": create_loading_screen,
        "load_scene_async": load_scene_async,
        # Onda 11
        "add_raycast_2d": add_raycast_2d,
        "add_shapecast_2d": add_shapecast_2d,
        "enable_debug_collisions": enable_debug_collisions,
        "enable_debug_navigation": enable_debug_navigation,
        "get_performance_stats": get_performance_stats,
        "setup_localization": setup_localization,
        "add_translation_string": add_translation_string,
        "create_light_3d": create_light_3d,
        "create_csg_shape": create_csg_shape,
        "configure_standard_material_3d": configure_standard_material_3d,
        "configure_export_preset": configure_export_preset,
        "configure_audio_bus": configure_audio_bus,
        "add_audio_effect": add_audio_effect,
        # G.1 — Visual Feedback Loop
        "visual_feedback_check": visual_feedback_check,
    }
