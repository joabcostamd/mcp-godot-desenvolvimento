"""domains/network/examples.py"""

EXAMPLES = {
    "setup_peer": {"peer_type": "ENetMultiplayerPeer", "port": 10567, "max_players": 4},
    "create_rpc": {"script_path": "res://scripts/player.gd", "method_name": "sync_position", "mode": "any_peer"},
    "create_ws": {"url": "ws://127.0.0.1:9080", "autoconnect": True},
    "config_server": {"port": 10567, "max_players": 32, "headless": True},
    "create_lobby": {"scene_path": "scenes/lobby.tscn", "max_players": 4},
}
