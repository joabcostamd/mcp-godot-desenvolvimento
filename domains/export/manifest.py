"""domains/export/manifest.py — F5.21."""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="export", tool_name="export_manage", title="Exportação", namespace="project", version="1.0.0",
    description="Gerencia exportação: listar presets, validar templates, build.\nQUANDO USAR: para publicar o jogo.\nQUANDO NÃO USAR: para AssetLib (use publish_manage).\nPRÉ-CONDIÇÕES: export templates instalados.",
    phases=[Phase.PRONTO_PARA_LANCAR], annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("list_presets", handlers.list_export_presets, "Lista presets de exportação", {}, [{}]),
         OpSpec("validate_templates", handlers.validate_export_templates, "Valida templates instalados", {}, [{}]),
         OpSpec("build", handlers.build_export, "Executa build de exportação", {"preset": {"type": "string", "required": False}}, [{"preset": "HTML5"}])],
    tags=["export", "build", "deploy"])
