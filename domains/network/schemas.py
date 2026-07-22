"""domains/network/schemas.py"""

INPUT_SCHEMAS = {
    "setup_peer": {"type": "object", "properties": {"peer_type": {"type": "string"}, "port": {"type": "integer"}, "max_players": {"type": "integer"}}, "required": []},
    "create_rpc": {"type": "object", "properties": {"script_path": {"type": "string"}, "method_name": {"type": "string"}, "params": {"type": "array"}, "mode": {"type": "string"}}, "required": ["script_path", "method_name"]},
    "create_ws": {"type": "object", "properties": {"url": {"type": "string"}, "autoconnect": {"type": "boolean"}}, "required": []},
    "config_server": {"type": "object", "properties": {"port": {"type": "integer"}, "max_players": {"type": "integer"}, "headless": {"type": "boolean"}}, "required": []},
    "create_lobby": {"type": "object", "properties": {"scene_path": {"type": "string"}, "max_players": {"type": "integer"}, "use_steam": {"type": "boolean"}}, "required": ["scene_path"]},
}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}, "message": {"type": "string"}}}
