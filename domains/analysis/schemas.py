"""domains/analysis/schemas.py"""
INPUT_SCHEMAS = {k: {"type": "object", "properties": {"query" if k == "search" else "": {"type": "string"}}, "required": []} for k in ["structure", "next_steps", "missing_refs", "validate_design", "estimate_scope", "search", "history"]}
OUTPUT_SCHEMA = {"type": "object", "properties": {"status": {"type": "string"}}}
