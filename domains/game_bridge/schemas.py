"""domains/game_bridge/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {}, "required": []} for k in ["call_method","spawn_node","raycast","get_camera","find_by_class","await_signal","pause","play_animation","performance","window","input_state","http_request","multiplayer","serialize_state"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
