## Collectable — Componente de Coleta | Godot 4.7 Style Guide compliant.
##
## Area2D que detecta o jogador (PhysicsBody2D) e coleta um item,
## adicionando-o ao Inventory no nó pai. Suporta auto-pickup,
## pickup manual e atração magnética (magnet_range).
##
## @behavior: collectable
## @genres: platformer, topdown_shooter, rpg, roguelike, tower_defense, metroidvania, generic
## @tutorial: behaviors/collectable/README.md

@tool
class_name Collectable
extends Area2D

## ID do item a ser coletado.
@export var item_id: String = ""

## Quantidade por coleta.
@export var quantity: int = 1:
	set(v):
		quantity = clampi(v, 1, 999)

## Se true, coleta automaticamente quando um corpo entra na área.
@export var auto_pickup: bool = true:
	set(v):
		auto_pickup = v
		if not is_inside_tree():
			return
		if v and not body_entered.is_connected(_on_body_entered):
			body_entered.connect(_on_body_entered)
		elif not v and body_entered.is_connected(_on_body_entered):
			body_entered.disconnect(_on_body_entered)

## Distância de atração magnética (0 = sem atração).
@export var magnet_range: float = 0.0:
	set(v):
		magnet_range = clampf(v, 0.0, 500.0)

## Emitido quando o item é coletado com sucesso.
signal collected(item_id: String, quantity: int)

## Emitido quando a coleta falha.
signal pickup_failed(reason: String)

var _magnet_target: Node2D = null
var _magnet_speed: float = 300.0
var _collected: bool = false
var _initialized: bool = false
var _last_fail_time: float = 0.0
const FAIL_COOLDOWN: float = 0.5


func _ready() -> void:
	if _initialized:
		return
	if auto_pickup and not body_entered.is_connected(_on_body_entered):
		body_entered.connect(_on_body_entered)
	_initialized = true


## Tenta coletar manualmente (útil para interação por input, não colisão).
## O body é o nó do jogador que está coletando.
func pickup(body: Node2D) -> void:
	if _collected:
		return
	_try_collect(body)


func _on_body_entered(body: Node2D) -> void:
	if not auto_pickup:
		return
	_try_collect(body)


func _physics_process(delta: float) -> void:
	if _collected:
		return

	# Magnet: detectar corpos no range automaticamente
	if magnet_range > 0.0 and not _magnet_target:
		var bodies := get_overlapping_bodies()
		if not bodies.is_empty():
			_start_magnet(bodies[0])

	if not _magnet_target:
		return
	if not is_instance_valid(_magnet_target):
		_magnet_target = null
		return

	var dir := _magnet_target.global_position - global_position
	var dist := dir.length()
	if dist < 4.0:
		_try_collect(_magnet_target)
		return

	global_position += dir.normalized() * _magnet_speed * delta


## Tenta adicionar o item ao inventário mais próximo.
func _try_collect(body: Node2D) -> void:
	if _collected:
		return

	# Validar item
	if item_id.is_empty():
		pickup_failed.emit("invalid_item")
		return
	if quantity <= 0:
		pickup_failed.emit("invalid_quantity")
		return

	# Buscar Inventory: primeiro no pai do collectable, depois no pai do body
	var inventory := _find_inventory(body)
	if not inventory:
		pickup_failed.emit("no_inventory")
		return

	var added := inventory.add_item(item_id, quantity)
	if added > 0:
		_collected = true
		collected.emit(item_id, added)
		call_deferred("queue_free")
	else:
		# Cooldown para evitar flood de pickup_failed
		var now := Time.get_ticks_msec() / 1000.0
		if now - _last_fail_time >= FAIL_COOLDOWN:
			pickup_failed.emit("inventory_full")
			_last_fail_time = now

	# Se magnet_range > 0 e falhou, resetar target para retentar
	if _magnet_target and added == 0:
		_magnet_target = null


## Busca Inventory: no próprio pai, depois no pai do body.
func _find_inventory(body: Node2D) -> Inventory:
	# 1. Inventory como irmão (mesmo pai)
	var parent_node := get_parent()
	if parent_node:
		for child in parent_node.get_children():
			if child is Inventory:
				return child as Inventory

	# 2. Inventory no pai do body (ex: Player tem Inventory filho)
	if body:
		for child in body.get_children():
			if child is Inventory:
				return child as Inventory

	return null


## Inicia atração magnética em direção ao body alvo.
func _start_magnet(body: Node2D) -> void:
	if magnet_range <= 0.0 or _magnet_target:
		return
	var dist := body.global_position.distance_to(global_position)
	if dist <= magnet_range:
		_magnet_target = body


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if item_id.is_empty():
		w.append("item_id está vazio — o item não será coletável.")
	if not auto_pickup:
		w.append("auto_pickup desabilitado — use pickup(body) manualmente.")
	var parent_node := get_parent()
	if parent_node and not _has_inventory_in_parent(parent_node):
		w.append("Nenhum Inventory encontrado no nó pai — a coleta falhará com 'no_inventory'.")
	return w


func _has_inventory_in_parent(node: Node) -> bool:
	for child in node.get_children():
		if child is Inventory:
			return true
	return false
