"""domains/_template/schemas.py — Schemas de input/output do domínio template."""

INPUT_SCHEMAS = {
    "example_op": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Descrição do parâmetro",
            },
        },
        "required": ["param1"],
    },
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["success", "error"]},
        "message": {"type": "string"},
    },
    "required": ["status"],
}
