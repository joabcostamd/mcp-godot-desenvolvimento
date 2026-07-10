"""runtime_rich.py — Runtime Rico (Fase 3 / tugcantopaloglu).

Ferramentas avançadas de runtime: CRUD em nodes vivos, raycast,
câmera, animação, tween, query de nós, sinais, controle de jogo.
Inspirado no tugcantopaloglu/godot-mcp (157 tools).

Tools (15):
    game_call_method, game_get_property, game_set_property,
    game_spawn_node, game_remove_node, game_change_scene,
    game_raycast, game_get_camera, game_set_camera,
    game_play_animation, game_tween_property,
    game_find_nodes_by_class, game_get_nodes_in_group,
    game_await_signal, game_pause, game_wait
"""

import json
from pathlib import Path


def _run(code: str) -> dict:
    """Executa GDScript no jogo em execução."""
    try:
        from tools.runtime_ops import execute_gdscript_runtime
        result = execute_gdscript_runtime(code)
        if isinstance(result, dict) and result.get("status") == "error":
            return result
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── CRUD Runtime ─────────────────────────────────────────────────────

def game_call_method(node_path: str, method: str, args: list | None = None) -> dict:
    """Chama um método em um nó no jogo rodando.
    
    Args:
        node_path: Path do nó (ex: "./Player").
        method: Nome do método.
        args: Lista de argumentos.
    """
    args_str = json.dumps(args or [])
    code = f"""
    var node = get_node("{node_path}")
    if not node: return {{"status":"error","message":"Nó não encontrado"}}
    if not node.has_method("{method}"): return {{"status":"error","message":"Método não encontrado"}}
    var result = node.callv("{method}", {args_str})
    return {{"status":"success","result":str(result)}}
    """
    return _run(code)


def game_get_property(node_path: str, property_name: str) -> dict:
    """Lê propriedade de nó no jogo rodando."""
    code = f"""
    var node = get_node("{node_path}")
    if not node: return {{"status":"error","message":"Nó não encontrado"}}
    var val = node.get("{property_name}")
    return {{"status":"success","property":"{property_name}","value":str(val),"type":typeof(val)}}
    """
    return _run(code)


def game_set_property(node_path: str, property_name: str, value: str, value_type: str = "auto") -> dict:
    """Define propriedade em nó no jogo rodando com coerção de tipo.
    
    Args:
        value_type: "auto", "int", "float", "bool", "Vector2", "Vector3", "Color", "String".
    """
    type_coercion = {
        "int": f"int({value})",
        "float": f"float({value})",
        "bool": "true" if value.lower() in ("true","1","yes") else "false",
        "Vector2": f"Vector2{value}" if value.startswith("(") else f"Vector2({value})",
        "Vector3": f"Vector3{value}" if value.startswith("(") else f"Vector3({value})",
    }
    coerced = type_coercion.get(value_type, f'"{value}"')
    
    code = f"""
    var node = get_node("{node_path}")
    if not node: return {{"status":"error","message":"Nó não encontrado"}}
    node.set("{property_name}", {coerced})
    var check = node.get("{property_name}")
    return {{"status":"success","property":"{property_name}","set_to":"{value}","verified":str(check)}}
    """
    return _run(code)


def game_spawn_node(parent_path: str, node_type: str, node_name: str = "", properties: dict | None = None) -> dict:
    """Cria nó dinamicamente no jogo rodando."""
    props_str = json.dumps(properties or {})
    code = f"""
    var parent = get_node("{parent_path}")
    if not parent: return {{"status":"error","message":"Parent não encontrado"}}
    var node = ClassDB.instantiate("{node_type}")
    if not node: return {{"status":"error","message":"Tipo inválido: {node_type}"}}
    if "{node_name}": node.name = "{node_name}"
    var props = {props_str}
    for key in props: node.set(key, props[key])
    parent.add_child(node)
    return {{"status":"success","node":node.name,"path":str(node.get_path())}}
    """
    return _run(code)


def game_remove_node(node_path: str) -> dict:
    """Remove nó no jogo rodando."""
    code = f"""
    var node = get_node("{node_path}")
    if not node: return {{"status":"error","message":"Nó não encontrado"}}
    var path = str(node.get_path())
    node.queue_free()
    return {{"status":"success","removed":path}}
    """
    return _run(code)


def game_change_scene(scene_path: str) -> dict:
    """Troca de cena no jogo rodando."""
    code = f"""
    var err = get_tree().change_scene_to_file("{scene_path}")
    if err != OK: return {{"status":"error","message":"Falha ao trocar cena: " + str(err)}}
    return {{"status":"success","scene":"{scene_path}"}}
    """
    return _run(code)


# ── Raycast ──────────────────────────────────────────────────────────

def game_raycast(
    origin_x: float, origin_y: float,
    target_x: float, target_y: float,
    collision_mask: int = 1,
    mode: str = "2d",
) -> dict:
    """Ray cast no jogo rodando (2D ou 3D)."""
    if mode == "2d":
        code = f"""
        var space = get_tree().root.world_2d.direct_space_state
        var query = PhysicsRayQueryParameters2D.create(
            Vector2({origin_x},{origin_y}), Vector2({target_x},{target_y}),
            {collision_mask}
        )
        var result = space.intersect_ray(query)
        if result:
            return {{"status":"success","hit":true,"position":str(result.position),"collider":result.collider.name,"normal":str(result.normal)}}
        return {{"status":"success","hit":false}}
        """
    else:
        code = f"""
        var space = get_tree().root.world_3d.direct_space_state
        var query = PhysicsRayQueryParameters3D.create(
            Vector3({origin_x},{origin_y},0), Vector3({target_x},{target_y},0),
            {collision_mask}
        )
        var result = space.intersect_ray(query)
        if result:
            return {{"status":"success","hit":true,"position":str(result.position),"collider":result.collider.name}}
        return {{"status":"success","hit":false}}
        """
    return _run(code)


# ── Camera ───────────────────────────────────────────────────────────

def game_get_camera(mode: str = "2d") -> dict:
    """Obtém posição/rotação/zoom da câmera ativa."""
    if mode == "2d":
        code = """
        var cam = get_viewport().get_camera_2d()
        if not cam: return {"status":"error","message":"Sem câmera 2D ativa"}
        return {"status":"success","position":str(cam.global_position),"zoom":str(cam.zoom)}
        """
    else:
        code = """
        var cam = get_viewport().get_camera_3d()
        if not cam: return {"status":"error","message":"Sem câmera 3D ativa"}
        return {"status":"success","position":str(cam.global_position),"rotation":str(cam.rotation)}
        """
    return _run(code)


def game_set_camera(target_x: float = 0, target_y: float = 0, target_z: float = 0, mode: str = "2d") -> dict:
    """Move a câmera para posição alvo."""
    if mode == "2d":
        code = f"""
        var cam = get_viewport().get_camera_2d()
        if not cam: return {{"status":"error","message":"Sem câmera 2D ativa"}}
        cam.global_position = Vector2({target_x},{target_y})
        return {{"status":"success","new_position":str(cam.global_position)}}
        """
    else:
        code = f"""
        var cam = get_viewport().get_camera_3d()
        if not cam: return {{"status":"error","message":"Sem câmera 3D ativa"}}
        cam.global_position = Vector3({target_x},{target_y},{target_z})
        return {{"status":"success","new_position":str(cam.global_position)}}
        """
    return _run(code)


# ── Animation ────────────────────────────────────────────────────────

def game_play_animation(node_path: str, action: str = "play", animation_name: str = "") -> dict:
    """Controla AnimationPlayer no jogo rodando.
    
    Args:
        action: "play", "stop", "pause", "list", "info".
        animation_name: Nome da animação.
    """
    if action == "list":
        code = f"""
        var ap = get_node("{node_path}")
        if not ap or not ap is AnimationPlayer: return {{"status":"error","message":"Não é AnimationPlayer"}}
        var list = ap.get_animation_list()
        return {{"status":"success","animations":Array(list)}}
        """
    elif action == "info":
        code = f"""
        var ap = get_node("{node_path}")
        if not ap or not ap is AnimationPlayer: return {{"status":"error","message":"Não é AnimationPlayer"}}
        return {{"status":"success","current":ap.current_animation,"playing":ap.is_playing(),"position":ap.current_animation_position,"speed":ap.speed_scale}}
        """
    else:
        code = f"""
        var ap = get_node("{node_path}")
        if not ap or not ap is AnimationPlayer: return {{"status":"error","message":"Não é AnimationPlayer"}}
        if "{action}" == "play": ap.play("{animation_name}")
        elif "{action}" == "stop": ap.stop()
        elif "{action}" == "pause": ap.pause()
        return {{"status":"success","action":"{action}"}}
        """
    return _run(code)


def game_tween_property(node_path: str, property_name: str, final_value: str, duration: float = 1.0, easing: str = "linear") -> dict:
    """Cria tween de propriedade no jogo rodando."""
    easing_map = {"linear": "Tween.EASE_IN_OUT", "bounce": "Tween.EASE_OUT", "elastic": "Tween.EASE_OUT", "back": "Tween.EASE_OUT"}
    e = easing_map.get(easing, "Tween.EASE_IN_OUT")
    
    code = f"""
    var node = get_node("{node_path}")
    if not node: return {{"status":"error","message":"Nó não encontrado"}}
    var tween = create_tween()
    tween.tween_property(node, "{property_name}", {final_value}, {duration}).set_ease({e})
    return {{"status":"success","tweening":"{property_name}","duration":{duration}}}
    """
    return _run(code)


# ── Query ────────────────────────────────────────────────────────────

def game_find_nodes_by_class(class_name: str, limit: int = 20) -> dict:
    """Encontra todos os nós de uma classe no jogo rodando."""
    code = f"""
    var nodes = get_tree().root.find_children("*", "{class_name}", true, false)
    var result = []
    for n in nodes:
        result.append(str(n.get_path()))
        if result.size() >= {limit}: break
    return {{"status":"success","class":"{class_name}","count":result.size(),"paths":result}}
    """
    return _run(code)


def game_get_nodes_in_group(group_name: str) -> dict:
    """Lista nós em um grupo no jogo rodando."""
    code = f"""
    var nodes = get_tree().get_nodes_in_group("{group_name}")
    var result = []
    for n in nodes:
        result.append({{"name":n.name,"path":str(n.get_path()),"type":n.get_class()}})
    return {{"status":"success","group":"{group_name}","count":result.size(),"nodes":result}}
    """
    return _run(code)


# ── Signals ──────────────────────────────────────────────────────────

def game_await_signal(node_path: str, signal_name: str, timeout_ms: int = 5000) -> dict:
    """Espera um sinal ser emitido com timeout."""
    code = f"""
    var node = get_node("{node_path}")
    if not node: return {{"status":"error","message":"Nó não encontrado"}}
    var emitted = false
    var args = []
    node.{signal_name}.connect(func(a=[]): emitted = true; args = a, CONNECT_ONE_SHOT)
    
    var elapsed = 0.0
    while not emitted and elapsed < {timeout_ms}/1000.0:
        await get_tree().process_frame
        elapsed += get_process_delta_time()
    
    if emitted:
        return {{"status":"success","signal":"{signal_name}","emitted":true,"elapsed_ms":elapsed*1000}}
    return {{"status":"timeout","signal":"{signal_name}","elapsed_ms":elapsed*1000}}
    """
    return _run(code)


def game_pause(action: str = "toggle") -> dict:
    """Pausa/despausa o jogo."""
    code = f"""
    var tree = get_tree()
    if "{action}" == "toggle":
        tree.paused = not tree.paused
    elif "{action}" == "pause":
        tree.paused = true
    else:
        tree.paused = false
    return {{"status":"success","paused":tree.paused}}
    """
    return _run(code)


def game_wait(frames: int = 60) -> dict:
    """Espera N frames (útil para timing)."""
    code = f"""
    for i in range({frames}):
        await get_tree().process_frame
    return {{"status":"success","frames_waited":{frames}}}
    """
    return _run(code)
