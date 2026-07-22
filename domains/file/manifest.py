"""domains/file/manifest.py"""
from registry.types import DomainManifest, OpSpec, Phase; from . import handlers
MANIFEST = DomainManifest(domain="file", tool_name="file_manage", title="Arquivos", namespace="project", version="1.0.0",
    description="Gerencia arquivos: deletar, mover e inspecionar.\nQUANDO USAR: para organizar estrutura de pastas.\nQUANDO NÃO USAR: para ler/escrever conteúdo (use read_file/write_file).",
    phases=[Phase.DESIGN, Phase.PROTOTIPO, Phase.CONTEUDO], annotations={"destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    ops=[OpSpec("delete", handlers.delete_file, "Deleta arquivo", {"file_path": {"type": "string", "required": True}}, [{"file_path": "res://old_scene.tscn"}]),
         OpSpec("move", handlers.move_file, "Move/renomeia", {"source_path": {"type": "string", "required": True}, "dest_path": {"type": "string", "required": True}}, [{"source_path": "res://old.tscn", "dest_path": "res://new.tscn"}]),
         OpSpec("inspect", handlers.inspect_project, "Inspeciona projeto", {}, [{}])],
    tags=["arquivo", "projeto", "fs"])
