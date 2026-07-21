@tool class_name SaveMigration extends Node
@export var from_version: String = "1.0.0"
@export var to_version: String = "1.1.0"
signal migration_complete(); signal migration_failed()
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _initialized=true
func migrate(data: Dictionary) -> Dictionary: migration_complete.emit(); return data
func report_migration_error() -> void: migration_failed.emit()
func needs_migration(version: String) -> bool: return version!=to_version
func _get_configuration_warnings() -> PackedStringArray: return []
