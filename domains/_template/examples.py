"""domains/_template/examples.py — Exemplos de uso do domínio template."""

EXAMPLES = {
    "example_op": [
        {
            "description": "Exemplo básico",
            "input": {"op": "example_op", "params": {"param1": "valor_exemplo"}},
            "expected_output": {"status": "success", "message": "Template handler called with param1=valor_exemplo"},
        },
    ],
}
