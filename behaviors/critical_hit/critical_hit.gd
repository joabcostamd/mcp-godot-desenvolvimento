## CriticalHit — Chance de Crítico | Godot 4.7 Style Guide compliant.
##
## Node que aplica chance de crítico ao dano.
## Use try_critical(base_damage) para obter o dano final.
## Compatível com health.take_damage(amount, multiplier).
##
## @behavior: critical_hit
## @genres: rpg, roguelike, fighting, platformer, topdown_shooter, generic
## @tutorial: behaviors/critical_hit/README.md

@tool
class_name CriticalHit
extends Node

## Probabilidade de crítico (0.0 = nunca, 1.0 = sempre).
@export var crit_chance: float = 0.1:
	set(value):
		crit_chance = clampf(value, 0.0, 1.0)

## Multiplicador de dano no crítico.
@export var crit_multiplier: float = 2.0:
	set(value):
		crit_multiplier = clampf(value, 1.0, 10.0)

## Emitido quando um crítico é ativado.
signal crit_landed(damage: int)

var _last_crit: bool = false


## Aplica chance de crítico ao dano base. Retorna o dano final.
func try_critical(base_damage: int) -> int:
	if base_damage <= 0:
		return base_damage

	_last_crit = randf() < crit_chance
	if _last_crit:
		var final_damage := ceili(base_damage * crit_multiplier)
		crit_landed.emit(final_damage)
		return final_damage

	return base_damage


## Retorna true se o último try_critical() ativou crítico.
func is_critical() -> bool:
	return _last_crit


## Apenas rola a chance, sem calcular dano e sem emitir sinal.
func roll() -> bool:
	_last_crit = randf() < crit_chance
	return _last_crit


## Auto-documentação no editor.
func _get_configuration_warnings() -> PackedStringArray:
	var warnings: PackedStringArray = []
	if crit_chance <= 0.0:
		warnings.append("crit_chance é 0 — nunca critará.")
	if crit_multiplier <= 1.0:
		warnings.append("crit_multiplier é 1.0 — crítico não altera o dano.")
	return warnings
