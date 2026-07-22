## bt_tree_resource.gd — MCP BT Editor | Resource para salvar/carregar arvores.
##
## Armazena os dados serializados do grafo: nos, conexoes, metadados.
## Usado pelo bt_editor_serializer.gd para persistencia em .tres.

@tool
class_name BTTreeResource
extends Resource

## Dicionario com estrutura completa da arvore:
## { "version": "1.0.0", "nodes": [...], "connections": [...] }
@export var tree_data: Dictionary = {}

## Nome amigavel da arvore
@export var display_name: String = ""

## Descricao da arvore
@export_multiline var description: String = ""

## Data de criacao
@export var created_at: String = ""

## Versao do formato
@export var format_version: String = "1.0.0"
