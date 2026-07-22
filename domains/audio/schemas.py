"""domains/audio/schemas.py"""
INPUT_SCHEMAS = {
    "configure_bus": {"type": "object", "properties": {"bus_name": {"type": "string"}}, "required": []},
    "add_effect": {"type": "object", "properties": {"effect_type": {"type": "string"}}, "required": []},
    "route_bus": {"type": "object", "properties": {"source_bus": {"type": "string"}, "target_bus": {"type": "string"}}, "required": ["source_bus", "target_bus"]},
    "spatial_player": {"type": "object", "properties": {"scene_path": {"type": "string"}}, "required": ["scene_path"]},
}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
