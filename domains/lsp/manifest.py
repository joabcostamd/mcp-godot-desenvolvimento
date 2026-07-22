"""domains/lsp/manifest.py — Manifesto do domínio lsp (F5.10).

Migração concluída em 2026-07-21.
"""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    domain="lsp",
    tool_name="lsp_manage",
    title="Introspecção GDScript (LSP)",
    namespace="project",
    version="1.0.0",
    description=(
        "Introspecção GDScript via LSP: conecta ao Godot, analisa código, busca definições, "
        "referências, símbolos, diagnósticos e renomeia com segurança semântica.\n"
        "QUANDO USAR: para navegar código, encontrar usos, renomear símbolos, verificar erros.\n"
        "QUANDO NÃO USAR: para editar código (use script_manage), para compilar (use godot_manage).\n"
        "PRÉ-CONDIÇÕES: Godot editor ABERTO com o projeto carregado (porta LSP 6005).\n"
        "ERRO COMUM: LSP não conectado — abra o editor Godot primeiro, depois use connect."
    ),
    phases=[Phase.DESIGN],
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
    ops=[
        OpSpec(name="connect", fn=handlers.gdscript_lsp_connect, summary="Conecta ao Language Server do Godot na porta 6005",
               schema={"project_root": {"type": "string", "required": False, "description": "Raiz do projeto"}},
               examples=[{}], rollback=None),
        OpSpec(name="disconnect", fn=handlers.gdscript_lsp_disconnect, summary="Desconecta do Language Server do Godot",
               schema={}, examples=[{}], rollback=None),
        OpSpec(name="sync", fn=handlers.gdscript_sync_file, summary="Notifica o LSP sobre alterações em um arquivo",
               schema={"file_path": {"type": "string", "required": True, "description": "Caminho do arquivo .gd"},
                       "content": {"type": "string", "required": False, "description": "Conteúdo atualizado"}},
               examples=[{"file_path": "res://scripts/player.gd"}], rollback=None),
        OpSpec(name="definition", fn=handlers.gdscript_definition, summary="Navega para a definição de um símbolo",
               schema={"file_path": {"type": "string", "required": True}, "line": {"type": "integer", "required": True},
                       "character": {"type": "integer", "required": True}},
               examples=[{"file_path": "res://scripts/player.gd", "line": 10, "character": 5}], rollback=None),
        OpSpec(name="references", fn=handlers.gdscript_references, summary="Encontra todas as referências a um símbolo",
               schema={"file_path": {"type": "string", "required": True}, "line": {"type": "integer", "required": True},
                       "character": {"type": "integer", "required": True}},
               examples=[{"file_path": "res://scripts/player.gd", "line": 10, "character": 5}], rollback=None),
        OpSpec(name="hover", fn=handlers.gdscript_hover, summary="Exibe tipo e documentação de um símbolo",
               schema={"file_path": {"type": "string", "required": True}, "line": {"type": "integer", "required": True},
                       "character": {"type": "integer", "required": True}},
               examples=[{"file_path": "res://scripts/player.gd", "line": 10, "character": 5}], rollback=None),
        OpSpec(name="symbols", fn=handlers.gdscript_symbols, summary="Lista símbolos de um arquivo GDScript",
               schema={"file_path": {"type": "string", "required": True, "description": "Caminho do arquivo .gd"}},
               examples=[{"file_path": "res://scripts/player.gd"}], rollback=None),
        OpSpec(name="rename", fn=handlers.gdscript_rename, summary="Renomeia símbolo com segurança semântica",
               schema={"file_path": {"type": "string", "required": True}, "line": {"type": "integer", "required": True},
                       "character": {"type": "integer", "required": True}, "new_name": {"type": "string", "required": True}},
               examples=[{"file_path": "res://scripts/player.gd", "line": 10, "character": 5, "new_name": "new_func"}], rollback="safety_manage(op=undo)"),
        OpSpec(name="diagnostics", fn=handlers.gdscript_diagnostics, summary="Retorna erros e warnings do compilador GDScript",
               schema={"file_path": {"type": "string", "required": True, "description": "Caminho do arquivo .gd"}},
               examples=[{"file_path": "res://scripts/player.gd"}], rollback=None),
    ],
    tags=["lsp", "gdscript", "análise", "código"],
)
