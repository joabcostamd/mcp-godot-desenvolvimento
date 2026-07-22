"""domains/lsp/examples.py — Exemplos de uso do domínio lsp (F5.10)."""

EXAMPLES = {
    "connect": {},
    "disconnect": {},
    "sync": {"file_path": "res://scripts/player.gd"},
    "definition": {"file_path": "res://scripts/player.gd", "line": 10, "character": 5},
    "references": {"file_path": "res://scripts/player.gd", "line": 10, "character": 5},
    "hover": {"file_path": "res://scripts/player.gd", "line": 10, "character": 5},
    "symbols": {"file_path": "res://scripts/player.gd"},
    "rename": {"file_path": "res://scripts/player.gd", "line": 10, "character": 5, "new_name": "new_func"},
    "diagnostics": {"file_path": "res://scripts/player.gd"},
}
