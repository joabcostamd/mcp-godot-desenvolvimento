"""domains/safety/manifest.py — F5.24."""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="safety", tool_name="safety_manage", title="Segurança", namespace="project", version="1.0.0",
    description="Gerencia segurança: backups, restore, checkpoint git e undo/redo.\nQUANDO USAR: antes de operações destrutivas.\nQUANDO NÃO USAR: para versionamento completo (use vcs_manage).",
    phases=[Phase.IDEIA, Phase.DESIGN, Phase.PROTOTIPO, Phase.CONTEUDO, Phase.POLIMENTO, Phase.PRONTO_PARA_LANCAR],
    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("list_backups", handlers.list_backups, "Lista backups", {}, [{}]),
         OpSpec("restore", handlers.restore_backup, "Restaura backup", {"backup_id": {"type": "string", "required": False}}, [{}]),
         OpSpec("checkpoint", handlers.git_checkpoint, "Checkpoint git", {"message": {"type": "string", "required": False}}, [{"message": "antes-da-mudanca"}]),
         OpSpec("undo", handlers.undo_last_action, "Desfaz última ação", {}, [{}]),
         OpSpec("undo_history", handlers.get_undo_history, "Histórico de undo", {}, [{}])],
    tags=["backup", "git", "undo", "segurança"])
