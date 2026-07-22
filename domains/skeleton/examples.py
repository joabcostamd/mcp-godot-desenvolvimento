"""domains/skeleton/examples.py — Exemplos de uso do domínio skeleton (F5.8)."""

EXAMPLES = {
    "get_info": {
        "scene_path": "scenes/player.tscn",
        "skeleton_path": "Player/Armature/Skeleton3D",
    },
    "list_bones": {
        "scene_path": "scenes/player.tscn",
        "skeleton_path": "Player/Armature",
    },
    "get_pose": {
        "scene_path": "scenes/player.tscn",
        "skeleton_path": "Player/Armature",
        "bone_name": "UpperArm_L",
    },
    "set_pose": {
        "scene_path": "scenes/player.tscn",
        "skeleton_path": "Player/Armature",
        "bone_name": "UpperArm_L",
        "rotation": [0, 0, 1.57],
    },
    "create_bone": {
        "scene_path": "scenes/player.tscn",
        "skeleton_path": "Player/Armature",
        "bone_name": "Weapon_Bone",
        "parent_bone": "UpperArm_R",
    },
    "create_ik": {
        "scene_path": "scenes/player.tscn",
        "skeleton_path": "Player/Armature",
        "bone_name": "UpperArm_R",
        "chain_length": 2,
        "iterations": 10,
    },
}
