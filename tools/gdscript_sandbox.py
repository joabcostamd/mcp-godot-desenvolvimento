"""gdscript_sandbox — Validação de segurança para código GDScript dinâmico.

Impede que execute_gdscript_runtime execute código malicioso.
Implementa allowlist de classes GDScript permitidas e blocklist de
operações perigosas.

Usado por: tools/game_bridge.py (inject, execute, watch)
"""

import re

# ── Classes BLOQUEADAS (acesso a sistema, arquivos, rede) ──────────

_BLOCKED_CLASSES = {
    "OS", "OS2",           # execução de processos, shell, variáveis de ambiente
    "FileAccess",          # leitura/escrita de arquivos arbitrários
    "DirAccess",           # navegação/manipulação de diretórios
    "ResourceLoader",      # carregamento de recursos arbitrários
    "ResourceSaver",       # salvamento de recursos arbitrários
    "JavaClass",           # acesso à JVM (Android)
    "JavaScript",          # acesso à JS bridge (Web)
    "JavaScriptBridge",    # acesso à JS bridge (Web)
    "Engine",              # acesso interno à engine
    "EngineDebugger",      # debugger interno
    "ClassDB",             # acesso à base de classes interna
    "ProjectSettings",     # modificação de configs do projeto
    "TranslationServer",   # manipulação de traduções
    "IP",                  # acesso a rede/endereços IP
    "HTTPRequest",         # requisições HTTP
    "WebSocketPeer",       # WebSocket
    "TCPServer",           # servidor TCP
    "TCPSocket",           # socket TCP
    "UDPSocket",           # socket UDP
    "PacketPeer",          # peer de rede genérico
    "StreamPeer",          # peer de stream genérico
    "ENetMultiplayerPeer", # multiplayer ENet
    "WebRTCPeer",          # WebRTC
}

# ── Patterns BLOQUEADOS (operações perigosas) ─────────────────────

_BLOCKED_PATTERNS = [
    # Chamadas de sistema e shell
    (r'OS\.execute\s*\(', "OS.execute() — execução de processos"),
    (r'OS\.shell_open\s*\(', "OS.shell_open() — abertura de URLs/arquivos"),
    (r'OS\.create_process\s*\(', "OS.create_process() — criação de processos"),
    (r'OS\.kill\s*\(', "OS.kill() — encerramento de processos"),
    (r'OS\.set_environment\s*\(', "OS.set_environment() — modificação de variáveis de ambiente"),

    # Acesso a arquivos
    (r'FileAccess\.open\s*\(', "FileAccess.open() — acesso a arquivos"),
    (r'FileAccess\.open_compressed\s*\(', "FileAccess.open_compressed() — acesso a arquivos"),
    (r'FileAccess\.open_encrypted\s*\(', "FileAccess.open_encrypted() — acesso a arquivos"),
    (r'DirAccess\.open\s*\(', "DirAccess.open() — acesso a diretórios"),
    (r'DirAccess\.make_dir_absolute\s*\(', "DirAccess.make_dir_absolute() — criação de diretórios"),
    (r'DirAccess\.remove_absolute\s*\(', "DirAccess.remove_absolute() — remoção de diretórios"),

    # Acesso a recursos externos
    (r'ResourceLoader\.load\s*\(', "ResourceLoader.load() — carregamento de recursos"),
    (r'ResourceSaver\.save\s*\(', "ResourceSaver.save() — salvamento de recursos"),

    # Rede
    (r'HTTPRequest\.(new|request)\s*\(', "HTTPRequest — requisições de rede"),
    (r'WebSocketPeer\.', "WebSocketPeer — conexões WebSocket"),
    (r'TCPServer\.', "TCPServer — servidor TCP"),
    (r'TCPSocket\.', "TCPSocket — socket TCP"),
    (r'(?<!_)IP\.(resolve|get_)', "IP — resolução de rede"),

    # Acesso perigoso à engine
    (r'Engine\.(get_singleton|get_main_loop|set_meta)\s*\(', "Engine — acesso interno"),
    (r'EngineDebugger\.', "EngineDebugger — debug interno"),
    (r'ClassDB\.(instantiate|class_get)\s*\(', "ClassDB — instanciação dinâmica"),

    # Modificação de projeto
    (r'ProjectSettings\.(set_setting|save|load)\s*\(', "ProjectSettings — modificação de configurações"),

    # Chamadas eval/execute dinâmicas
    (r'Expression\.new\s*\(', "Expression.new() — execução dinâmica"),
    (r'GDScript\.new\s*\(', "GDScript.new() — compilação dinâmica"),
    (r'\.call\s*\(\s*[\'"]', "call() com string dinâmica — potencial RCE"),
]

# ── Classes PERMITIDAS (safe para jogos) ───────────────────────────

_ALLOWED_CLASSES = {
    # Core
    "Node", "Node2D", "Node3D", "CanvasItem", "Control",
    # 2D
    "Sprite2D", "AnimatedSprite2D", "CharacterBody2D", "RigidBody2D",
    "StaticBody2D", "Area2D", "CollisionShape2D", "Camera2D",
    "AudioStreamPlayer2D", "Timer", "Marker2D", "RayCast2D",
    "TileMap", "TileMapLayer", "TileSet",
    # 3D
    "CharacterBody3D", "RigidBody3D", "StaticBody3D", "Area3D",
    "CollisionShape3D", "MeshInstance3D", "Camera3D",
    "AudioStreamPlayer3D", "SpringArm3D",
    # UI
    "Button", "Label", "LineEdit", "Panel", "HBoxContainer",
    "VBoxContainer", "GridContainer", "MarginContainer",
    "CanvasLayer", "Popup", "PopupMenu", "OptionButton",
    "CheckBox", "HSlider", "VSlider", "ProgressBar",
    "ColorRect", "TextureRect", "TextureButton",
    # Animação
    "AnimationPlayer", "AnimationTree", "Tween",
    # Input & Math
    "Input", "InputEvent", "InputEventKey", "InputEventMouseButton",
    "InputEventMouseMotion", "InputEventAction",
    # Data
    "Vector2", "Vector3", "Color", "Rect2", "Transform2D",
    "Basis", "Quaternion", "AABB",
    # Resources
    "Resource", "PackedScene", "Texture2D", "Font", "FontFile",
    # Signals
    "Signal",
    # Collections
    "Array", "Dictionary", "PackedByteArray", "PackedInt32Array",
    "PackedFloat32Array", "PackedFloat64Array", "PackedStringArray",
    "PackedVector2Array", "PackedVector3Array", "PackedColorArray",
    # Utils
    "Math", "Time", "RandomNumberGenerator",
    "JSON", "Marshalls",
}

# ── API Pública ─────────────────────────────────────────────────────

def validate_gdscript_code(code: str, mode: str = "runtime") -> dict:
    """Valida se um snippet GDScript é seguro para execução.

    Args:
        code: Código GDScript a validar.
        mode: "runtime" (jogo rodando, mais restrito) ou "editor" (menos restrito).

    Returns:
        {"status": "success", "safe": True}
        ou {"status": "error", "safe": False, "message": str, "violations": [...]}
    """
    violations = []

    # ── Verifica classes bloqueadas ──────────────────────────────
    for cls in _BLOCKED_CLASSES:
        # Verifica uso como tipo (ClassName. ou ClassName()
        if re.search(rf'\b{cls}\.', code) or re.search(rf'\b{cls}\s*\(', code):
            violations.append({
                "type": "blocked_class",
                "class": cls,
                "message": f"Classe bloqueada '{cls}' detectada. "
                           f"Esta classe pode acessar o sistema de arquivos, "
                           f"rede, ou executar processos. Use classes da Godot API segura.",
            })

    # ── Verifica patterns bloqueados ─────────────────────────────
    for pattern, description in _BLOCKED_PATTERNS:
        if re.search(pattern, code):
            violations.append({
                "type": "blocked_pattern",
                "pattern": pattern,
                "message": f"Operação bloqueada: {description}. "
                           f"Esta operação pode comprometer o sistema.",
            })

    # ── Verifica se usa apenas classes seguras ───────────────────
    # Extrai nomes de classe do código (ClassName.member ou ClassName())
    class_usage = set()
    for m in re.finditer(r'\b([A-Z][a-zA-Z0-9_]{1,30})\s*[.\(]', code):
        name = m.group(1)
        if name not in _ALLOWED_CLASSES and name not in _BLOCKED_CLASSES:
            class_usage.add(name)

    # Se encontrarmos classes não reconhecidas, verificamos se são tipos built-in GDScript
    _BUILTIN_TYPES = {
        "int", "float", "bool", "String", "void", "null",
        "true", "false", "self", "super", "PI", "TAU", "INF", "NAN",
        "print", "prints", "printt", "push_error", "push_warning",
        "assert", "breakpoint", "get_node", "get_tree", "get_viewport",
        "queue_free", "free", "set", "get", "has_node", "is_instance_valid",
        "is_equal_approx", "lerp", "clamp", "wrap", "wrapf",
        "move_toward", "move_towardf", "range_lerp", "remap",
        "deg_to_rad", "rad_to_deg", "abs", "sign", "ceil", "floor",
        "round", "roundf", "snapped", "snappedf",
        "pow", "log", "exp", "sqrt", "sin", "cos", "tan",
        "asin", "acos", "atan", "atan2", "sinh", "cosh", "tanh",
        "fmod", "fposmod", "posmod", "ease",
        "str", "typeof", "type_exists", "instance_from_id",
        "weakref", "is_same", "char", "len", "ord",
        "var", "func", "extends", "class", "class_name",
        "static", "const", "enum", "signal", "export",
        "onready", "tool", "icon", "master", "puppet", "remote",
        "return", "if", "elif", "else", "for", "while", "break",
        "continue", "pass", "match", "when", "in", "not", "and", "or",
        "as", "is", "new", "preload", "load",
    }

    unknown_classes = class_usage - _ALLOWED_CLASSES - _BLOCKED_CLASSES - _BUILTIN_TYPES
    # Não bloqueamos classes desconhecidas — podem ser classes de usuário

    if violations:
        return {
            "status": "error",
            "safe": False,
            "message": f"Código GDScript bloqueado por segurança. "
                       f"{len(violations)} violação(ões) encontrada(s). "
                       f"Use apenas classes seguras da Godot API (Node, Node2D, Input, etc.).",
            "violations": violations,
        }

    return {"status": "success", "safe": True}


def get_allowed_classes() -> list[str]:
    """Retorna a lista de classes permitidas no sandbox."""
    return sorted(_ALLOWED_CLASSES)


def get_blocked_classes() -> list[str]:
    """Retorna a lista de classes bloqueadas e o motivo."""
    return sorted(_BLOCKED_CLASSES)
