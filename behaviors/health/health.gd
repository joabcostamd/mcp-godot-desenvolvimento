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
@export var invulnerable_time: float = 0.0:
	set(v): invulnerable_time = clampf(v, 0.0, 60.0)

## Se false, ignora todo dano (take_damage retorna 0). Ex: NPC invencível.
@export var damageable: bool = true:
	set(v): damageable = v

## Se false, ignora toda cura (heal retorna 0). Ex: inimigo que não se cura.
@export var healable: bool = true:
	set(v): healable = v

## Se false, current_hp nunca chega a 0 (entidade fica com 1 HP mínimo).
@export var killable: bool = true:
	set(v): killable = v

## Se true, permite curar após morte para reviver. false = morte permanente.
@export var revivable: bool = true:
	set(v): revivable = v

## Emitido quando current_hp chega a 0.
signal died()

## Emitido ao tomar dano.
signal damage_taken(amount: int, remaining: int)

## Emitido ao receber cura.
signal healed(amount: int, current: int)

## Emitido sempre que current_hp muda.
signal hp_changed(old_hp: int, new_hp: int)

## Emitido no primeiro hit (dano > 0) da vida do componente.
signal first_hit()

## Emitido quando HP atinge o máximo (cura completa).
signal full()

## Emitido quando dano é bloqueado (damageable=false ou invulnerável).
signal damage_blocked(amount: int)

## Emitido quando cura é bloqueada (healable=false ou não revivable).
signal heal_blocked(amount: int)

var _invulnerable: bool = false
var _has_taken_first_hit: bool = false


## Aplica dano. Respeita damageable, invulnerabilidade e killable.
## Suporta multiplier para critical hits: take_damage(10, 2.0) = 20 de dano.
func take_damage(amount: int, multiplier: float = 1.0) -> int:
	if not damageable:
		damage_blocked.emit(amount)
		return 0
	if _invulnerable:
		damage_blocked.emit(amount)
		return 0
	if amount <= 0:
		return 0

	var final_amount := ceili(amount * multiplier)
	var old_hp := current_hp
	current_hp -= final_amount
	var effective := old_hp - current_hp

	if effective > 0:
		if not _has_taken_first_hit:
			_has_taken_first_hit = true
			first_hit.emit()
		damage_taken.emit(effective, current_hp)
		if invulnerable_time > 0.0:
			_start_invulnerability()
		# killable: se não pode morrer, garante pelo menos 1 HP
		if not killable and current_hp == 0:
			current_hp = 1

	return effective


## Cura o personagem. Respeita healable e revivable. Suporta multiplier.
func heal(amount: int, multiplier: float = 1.0) -> int:
	if not healable:
		heal_blocked.emit(amount)
		return 0
	if not revivable and current_hp == 0:
		heal_blocked.emit(amount)
		return 0
	if amount <= 0:
		return 0

	var final_amount := ceili(amount * multiplier)
	var old_hp := current_hp
	current_hp += final_amount
	var effective := current_hp - old_hp

	if effective > 0:
		healed.emit(effective, current_hp)
		if current_hp >= max_hp:
			full.emit()

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


## Auto-documentação no editor: ⚠️ avisa quando o nó está mal configurado.
func _get_configuration_warnings() -> PackedStringArray:
	var warnings: PackedStringArray = []
	if max_hp <= 0:
		warnings.append("max_hp deve ser maior que 0.")
	if not damageable and not healable:
		warnings.append("damageable e healable desabilitados — componente não reage a nada.")
	return warnings
