## Hurtbox — Área Receptora de Dano | Godot 4.7 Style Guide compliant.
##
## Area2D passiva que detecta fontes de dano (Hitbox, Projectile)
## entrando em sua área, aplica um multiplicador e encaminha ao Health.
## Permite múltiplas hurtboxes por entidade (cabeça, corpo, pernas).
##
## @behavior: hurtbox
## @genres: platformer, topdown_shooter, rpg, roguelike, fighting,
##          metroidvania, bullet_hell, generic
## @tutorial: behaviors/hurtbox/README.md

@tool
class_name Hurtbox
extends Area2D

## Multiplicador de dano: 2.0 = headshot, 0.5 = armadura, 0.0 = bloqueio.
@export var damage_multiplier: float = 1.0:
	set(value):
		damage_multiplier = clampf(value, 0.0, 10.0)

## Tipo da hurtbox: "body", "head", "legs", "shield", "weak_point".
@export var hurt_type: String = "body":
	set(v):
		var valid := ["body", "head", "legs", "shield", "weak_point"]
		hurt_type = v if v in valid else "body"

## Caminho relativo para o nó Health do dono (ex: "../Health").
@export var health_path: NodePath

## Emitido quando dano é aplicado ao Health.
signal hit_received(original_damage: int, modified_damage: int, hit_type: String)

## Emitido quando dano é bloqueado (multiplier=0 ou health_path inválido).
signal hit_blocked(original_damage: int, reason: String)
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	# Hurtbox é sempre passiva: monitoring=true, monitorable=true
	monitoring = true
	monitorable = true
	area_entered.connect(_on_area_entered)

	if health_path.is_empty():
		push_warning("[Hurtbox] health_path está vazio — hurtbox não aplicará dano.")
	_initialized = true


## Detecta fontes de dano (Hitbox, Projectile) que entram na área.
func _on_area_entered(area: Area2D) -> void:
	var info := _extract_damage_info(area)
	if info.is_empty():
		return

	_apply_damage(info["damage"], info["hit_type"])


## Extrai (damage, hit_type) de uma Area2D. Suporta Hitbox e Projectile.
## Retorna Dictionary vazio se a área não for uma fonte de dano reconhecida.
func _extract_damage_info(area: Area2D) -> Dictionary:
	if area is Hitbox:
		var hitbox := area as Hitbox
		if not hitbox.active:
			return {}
		return {"damage": hitbox.damage, "hit_type": hitbox.hit_type}

	if area is Projectile:
		var proj := area as Projectile
		return {"damage": proj.damage, "hit_type": "ranged"}

	return {}


## Aplica o multiplicador ao dano e encaminha ao Health.
func _apply_damage(damage_amount: int, hit_type_str: String) -> void:
	if damage_multiplier == 0.0:
		hit_blocked.emit(damage_amount, "damage_multiplier_zero")
		return

	var health := _resolve_health()
	if not health or not is_instance_valid(health):
		hit_blocked.emit(damage_amount, "health_path_invalid")
		return

	var modified := ceili(damage_amount * damage_multiplier)
	var dealt := health.take_damage(modified)

	if dealt > 0:
		hit_received.emit(damage_amount, dealt, hit_type_str)
	else:
		hit_blocked.emit(damage_amount, "health_blocked_damage")


## Resolve o health_path para o nó Health.
func _resolve_health() -> Health:
	if health_path.is_empty():
		return null
	if not is_inside_tree():
		return null
	var node := get_node_or_null(health_path)
	if node is Health:
		return node
	return null


## Auto-documentação no editor.
func _get_configuration_warnings() -> PackedStringArray:
	var warnings: PackedStringArray = []
	if health_path.is_empty():
		warnings.append("health_path está vazio — hurtbox não aplicará dano.")
	if damage_multiplier == 0.0:
		warnings.append("damage_multiplier é 0 — todo dano será bloqueado.")
	if hurt_type not in ["body", "head", "legs", "shield", "weak_point"]:
		warnings.append("hurt_type não é um valor reconhecido (body, head, legs, shield, weak_point).")
	if collision_mask == 1 and collision_layer == 1:
		warnings.append("collision_mask e collision_layer no default (1). Configure para detectar apenas hitboxes inimigas.")
	if monitoring == false:
		warnings.append("monitoring está false — hurtbox não detectará fontes de dano.")
	# Alerta sobre risco de double-damage: se o dono tem Health como filho direto
	# e tem collision body na mesma layer, hitbox/projectile podem causar dano via body_entered.
	var parent := get_parent()
	if parent:
		for child in parent.get_children():
			if child is Health and child != self:
				warnings.append("Health detectado como irmão no mesmo pai. Risco de double-damage: configure collision layers diferentes para o corpo e para as hurtboxes.")
				break
	return warnings
