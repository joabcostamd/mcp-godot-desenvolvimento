"""domains/_template/manifest.py — Template de manifesto de domínio.

Copie este diretório para criar um novo domínio:
    cp -r domains/_template domains/<nome>

Preencha MANIFEST com os dados do domínio.
"""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="template",
    tool_name="template_manage",
    title="Template",
    namespace="project",
    version="1.0.0",
    description=(
        "DESCREVA o que este domínio faz.\n"
        "QUANDO USAR: cenário típico.\n"
        "QUANDO NÃO USAR: use X_manage para Y.\n"
        "PRÉ-CONDIÇÕES: o que precisa existir.\n"
        "ERRO COMUM: descrição do erro e como resolver."
    ),
    phases=[Phase.DESIGN],
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    ops=[
        OpSpec(
            name="example_op",
            fn=handlers.example_handler,
            summary="Resumo de uma linha do que esta op faz",
            schema={
                "param1": {"type": "string", "required": True,
                           "description": "Descrição do parâmetro"},
            },
            examples=[{"param1": "valor_exemplo"}],
            rollback="safety_manage(op=undo)",
        ),
    ],
    tags=["template"],
)
