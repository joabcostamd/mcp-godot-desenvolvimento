@tool class_name Localization extends Node
@export var locale: String = "en": set(v)=locale=v; _apply_locale()
@export var fallback_locale: String = "en"
signal locale_changed(new_locale: String)
var _initialized: bool = false
func _ready() -> void: if _initialized: return; _apply_locale(); _initialized=true
func set_locale(loc: String) -> void: locale=loc; locale_changed.emit(loc)
func get_locale() -> String: return locale
func translate(key: String) -> String: return tr(key) if not key.is_empty() else ""
func _apply_locale() -> void: if TranslationServer.get_locale()!=locale: TranslationServer.set_locale(locale)
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if TranslationServer.get_loaded_locales().is_empty(): w.append("Nenhuma traducao carregada.")
	return w
