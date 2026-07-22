"""domains/editor/examples.py"""
EXAMPLES = {k: {} for k in ["connect","disconnect","is_available","ping","create_node","delete_node","set_property","reparent_node","duplicate_node","batch_edit","take_screenshot","get_scene_tree"]}
EXAMPLES["create_node"] = {"node_type": "Sprite2D", "node_name": "Player"}
EXAMPLES["delete_node"] = {"node_path": "./OldNode"}
EXAMPLES["batch_edit"] = {"operations": [{"op": "create", "type": "Sprite2D"}]}
