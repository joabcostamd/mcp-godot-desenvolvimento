"""domains/safety/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {"backup_id" if k == "restore" else "message" if k == "checkpoint" else "": {"type": "string"}}, "required": []} for k in ["list_backups", "restore", "checkpoint", "undo", "undo_history"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
