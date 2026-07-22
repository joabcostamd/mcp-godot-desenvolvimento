"""domains/skeleton/schemas.py — Schemas de input/output do domínio skeleton (F5.8)."""

INPUT_SCHEMAS = {
    "get_info": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string"},
            "skeleton_path": {"type": "string"},
        },
        "required": ["scene_path", "skeleton_path"],
    },
    "list_bones": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string"},
            "skeleton_path": {"type": "string"},
        },
        "required": ["scene_path", "skeleton_path"],
    },
    "get_pose": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string"},
            "skeleton_path": {"type": "string"},
            "bone_name": {"type": "string"},
        },
        "required": ["scene_path", "skeleton_path", "bone_name"],
    },
    "set_pose": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string"},
            "skeleton_path": {"type": "string"},
            "bone_name": {"type": "string"},
            "position": {"type": "array"},
            "rotation": {"type": "array"},
            "scale": {"type": "array"},
        },
        "required": ["scene_path", "skeleton_path", "bone_name"],
    },
    "create_bone": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string"},
            "skeleton_path": {"type": "string"},
            "bone_name": {"type": "string"},
            "parent_bone": {},
            "position": {"type": "array"},
            "rotation": {"type": "array"},
        },
        "required": ["scene_path", "skeleton_path", "bone_name"],
    },
    "create_ik": {
        "type": "object",
        "properties": {
            "scene_path": {"type": "string"},
            "skeleton_path": {"type": "string"},
            "bone_name": {"type": "string"},
            "target_node_path": {"type": "string"},
            "chain_length": {"type": "integer"},
            "iterations": {"type": "integer"},
        },
        "required": ["scene_path", "skeleton_path", "bone_name"],
    },
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "ok": {"type": "boolean"},
        "error": {"type": "string"},
    },
}
