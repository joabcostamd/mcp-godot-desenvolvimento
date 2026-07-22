"""domains/gamestate/examples.py"""
EXAMPLES = {"create_save": {"scene_path": "scenes/game.tscn"}, "define_save": {"scene_path": "scenes/game.tscn", "data_name": "player_save"}, "create_fsm": {"scene_path": "scenes/game.tscn", "states": ["idle", "run"]}, "add_transition": {"scene_path": "scenes/game.tscn", "from_state": "idle", "to_state": "run", "condition": "is_moving"}}
