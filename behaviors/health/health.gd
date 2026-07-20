## Health — Componente de Vida | Godot 4.7 Style Guide compliant.
##
## Componente plugável: adicione como nó filho de qualquer entidade.
## Usa composição, NUNCA herança. Sinais: died, damage_taken, healed, hp_changed.
##
## @behavior: health
## @genres: platformer, topdown_shooter, rpg, roguelike, tower_defense, fighting,
##          metroidvania, bullet_hell, generic
## @tutorial: behaviors/health/README.md

@tool
class_name Health
extends Node

## Vida máxima. Reduzida apenas por take_damage(), nunca diretamente.
@export var max_hp: int = 100:
	set(value):
		max_hp = maxi(1, value)
		if current_hp > max_hp:
			current_hp = max_hp

## Vida atual. Use take_damage() e heal() para alterar.
@export var current_hp: int = 100:
	set(value):
		var old := current_hp
		current_hp = clampi(value, 0, max_hp)
		if current_hp != old:
			hp_changed.emit(old, current_hp)
		if current_hp == 0 and old > 0:
			died.emit()

## Tempo de invulnerabilidade após dano. 0 = sem invulnerabilidade.
@export var invulnerable_time: float = 0.0

## Emitido quando current_hp chega a 0.
signal died()

## Emitido ao tomar dano.
signal damage_taken(amount: int, remaining: int)

## Emitido ao receber cura.
signal healed(amount: int, current: int)

## Emitido sempre que current_hp muda.
signal hp_changed(old_hp: int, new_hp: int)

var _invulnerable: bool = false


## Aplica dano. Respeita invulnerabilidade. Retorna o dano efetivo aplicado.
func take_damage(amount: int) -> int:
	if _invulnerable:
		return 0
	if amount <= 0:
		return 0

	var old_hp := current_hp
	current_hp -= amount
	var effective := old_hp - current_hp

	if effective > 0:
		damage_taken.emit(effective, current_hp)
		if invulnerable_time > 0.0:
			_start_invulnerability()

	return effective


## Cura o personagem. Não excede max_hp. Retorna a cura efetiva.
func heal(amount: int) -> int:
	if amount <= 0:
		return 0

	var old_hp := current_hp
	current_hp += amount
	var effective := current_hp - old_hp

	if effective > 0:
		healed.emit(effective, current_hp)

	return effective


## Cura até o máximo (full heal).
func full_heal() -> void:
	heal(max_hp - current_hp)


## Retorna true se o personagem está vivo.
func is_alive() -> bool:
	return current_hp > 0


## Retorna a porcentagem de vida (0.0 a 1.0).
func hp_percent() -> float:
	if max_hp == 0:
		return 0.0
	return float(current_hp) / float(max_hp)


func _start_invulnerability() -> void:
	if not is_inside_tree():
		return
	_invulnerable = true
	await get_tree().create_timer(invulnerable_time).timeout
	_invulnerable = false
