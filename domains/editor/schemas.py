"""domains/editor/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {}, "required": []} for k in ["connect","disconnect","is_available","ping","create_node","delete_node","set_property","reparent_node","duplicate_node","batch_edit","take_screenshot","get_scene_tree"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
