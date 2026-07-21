## Hitbox — Área de Ataque | Godot 4.7 Style Guide compliant.
##
## Area2D que causa dano ao sobrepor entidades com componente Health.
## Componente plugável: adicione como nó filho de personagem ou arma.
## Ative/desative via set_active() ou propriedade active.
##
## @behavior: hitbox
## @genres: platformer, topdown_shooter, rpg, roguelike, fighting,
##          metroidvania, bullet_hell, generic
## @tutorial: behaviors/hitbox/README.md

@tool
class_name Hitbox
extends Area2D

## Dano causado ao atingir um alvo com Health.
@export var damage: int = 10:
	set(value):
		damage = maxi(0, value)

## Força de knockback (0 = sem). O movimento real é do behavior knockback (#14).
@export var knockback_force: float = 200.0:
	set(value):
		knockback_force = maxf(0.0, value)

## Tipo do golpe: "melee", "ranged", "magic", "explosive".
@export var hit_type: String = "melee":
	set(v):
		var valid := ["melee", "ranged", "magic", "explosive"]
		hit_type = v if v in valid else "melee"

## Se true, a hitbox está ativa e detecta colisões.
@export var active: bool = false:
	set(value):
		active = value
		monitoring = value
		if value:
			activated.emit()
		else:
			deactivated.emit()

## Emitido quando a hitbox causa dano a um alvo.
signal hit_dealt(target: Node, damage_dealt: int)

## Emitido quando a hitbox é ativada.
signal activated()

## Emitido quando a hitbox é desativada.
signal deactivated()

var _hit_targets: Array[Node] = []  # Evita multi-hit no mesmo frame
var _initialized: bool = false


func _ready() -> void:
	if _initialized: return
	monitoring = active
	area_entered.connect(_on_area_entered)
	body_entered.connect(_on_body_entered)
	_initialized = true


## Ativa a hitbox. Equivalente a active = true.
func set_active(enabled: bool) -> void:
	active = enabled


## Remove referências a nós já destruídos do array de alvos.
func _purge_stale_targets() -> void:
	var i := _hit_targets.size() - 1
	while i >= 0:
		if not is_instance_valid(_hit_targets[i]):
			_hit_targets.remove_at(i)
		i -= 1


## Desativa e limpa a lista de alvos já atingidos (pronto para próximo swing).
func reset_hits() -> void:
	_hit_targets.clear()


func _on_area_entered(area: Area2D) -> void:
	_handle_hit(area)


func _on_body_entered(body: Node2D) -> void:
	_handle_hit(body)


func _handle_hit(target: Node) -> void:
	if not active:
		return
	if not is_instance_valid(target):
		return

	# Limpa referências a nós já destruídos antes de verificar duplicata
	_purge_stale_targets()

	# Evita atingir o mesmo alvo múltiplas vezes no mesmo swing
	if target in _hit_targets:
		return

	# Busca componente Health no nó ou nos filhos
	var health := _find_health(target)
	if not health or not is_instance_valid(health):
		return

	var damage_dealt := health.take_damage(damage)
	if damage_dealt > 0:
		_hit_targets.append(target)
		hit_dealt.emit(target, damage_dealt)


## Busca recursivamente por um componente Health no nó ou em seus filhos.
func _find_health(node: Node) -> Health:
	if node is Health:
		return node
	for child in node.get_children():
		var found := _find_health(child)
		if found:
			return found
	return null


## Auto-documentação no editor: ⚠️ avisa quando o nó está mal configurado.
func _get_configuration_warnings() -> PackedStringArray:
	var warnings: PackedStringArray = []
	if damage <= 0:
		warnings.append("damage é 0 — hitbox não causa dano.")
	if hit_type not in ["melee", "ranged", "magic", "explosive"]:
		warnings.append("hit_type não é um valor reconhecido (melee, ranged, magic, explosive).")
	if collision_mask == 1 and collision_layer == 1:
		warnings.append("collision_mask e collision_layer estão no default (1). Configure para evitar self-hit e separar aliados de inimigos.")
	return warnings
