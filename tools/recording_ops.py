"""recording_ops.py — Recording/Replay + Serialize State (Fase 3).

Recording/replay de sessão (wangdiandao) + serialize state (tugcantopaloglu).

Tools:
    - start_recording / stop_recording / replay_recording
    - game_serialize_state: salva/restaura árvore como JSON
"""

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECORDINGS_DIR = ROOT / "recordings"


def _ensure_dir():
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


def start_recording(session_name: str = "") -> dict:
    """Inicia gravação de sessão (inputs e estados)."""
    _ensure_dir()
    name = session_name or f"session_{int(time.time())}"
    file = RECORDINGS_DIR / f"{name}.json"
    file.write_text("[]", encoding="utf-8")
    return {"status": "success", "recording": name, "file": str(file)}


def stop_recording(session_name: str) -> dict:
    """Para gravação e retorna resumo."""
    _ensure_dir()
    file = RECORDINGS_DIR / f"{session_name}.json"
    if not file.exists():
        return {"status": "error", "message": "Gravação não encontrada"}
    data = json.loads(file.read_text(encoding="utf-8"))
    return {"status": "success", "recording": session_name, "frames": len(data), "duration_approx_ms": len(data) * 16}


def replay_recording(session_name: str, speed: float = 1.0) -> dict:
    """Replay de sessão gravada."""
    _ensure_dir()
    file = RECORDINGS_DIR / f"{session_name}.json"
    if not file.exists():
        return {"status": "error", "message": "Gravação não encontrada"}
    data = json.loads(file.read_text(encoding="utf-8"))
    return {"status": "success", "replay_ready": True, "frames": len(data), "speed": speed, "note": "Use inject_input_event para reproduzir cada frame"}


def game_serialize_state(action: str = "save", file_name: str = "game_state.json") -> dict:
    """Salva/restaura estado completo da árvore de jogo como JSON.

    Args:
        action: "save" ou "load".
        file_name: Nome do arquivo de estado.

    Returns:
        dict com estado serializado.
    """
    if action == "save":
        code = """
        var root = get_tree().root
        var state = _serialize_node(root)
        return JSON.stringify(state)
        
        func _serialize_node(node):
            var data = {
                "name": node.name,
                "type": node.get_class(),
                "path": node.get_path(),
                "properties": {},
                "children": []
            }
            for prop in node.get_property_list():
                if prop.usage & PROPERTY_USAGE_SCRIPT_VARIABLE:
                    data.properties[prop.name] = str(node.get(prop.name))
            for child in node.get_children():
                data.children.append(_serialize_node(child))
            return data
        """

        try:
            from tools.runtime_ops import execute_gdscript_runtime
            result = execute_gdscript_runtime(code)
            if result:
                _ensure_dir()
                state_file = RECORDINGS_DIR / file_name
                state_file.write_text(str(result), encoding="utf-8")
                return {"status": "success", "action": "save", "file": str(state_file), "state": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    elif action == "load":
        state_file = RECORDINGS_DIR / file_name
        if not state_file.exists():
            return {"status": "error", "message": f"Estado '{file_name}' não encontrado"}

        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            return {"status": "success", "action": "load", "state": state}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {"status": "error", "message": f"Ação desconhecida: {action}"}
