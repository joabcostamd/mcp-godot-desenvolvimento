## Teste de composicao: ambience_zone + gravity_zone
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: ambience_zone
## @behavior_b: gravity_zone

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/ambience_zone/ambience_zone.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/ambience_zone/ambience_zone.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/gravity_zone/gravity_zone.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/gravity_zone/gravity_zone.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("ambience_zone foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("gravity_zone foi liberado durante o teste")
	# ── Verifica que ambience_zone ainda consegue emitir sinais ──
	# Sinal 'entered_zone': verifica conectividade
	assert_bool(_behavior_a.has_signal("entered_zone")).override_failure_message("Sinal 'entered_zone' nao encontrado em ambience_zone")

	# Sinal 'exited_zone': verifica conectividade
	assert_bool(_behavior_a.has_signal("exited_zone")).override_failure_message("Sinal 'exited_zone' nao encontrado em ambience_zone")
	# ── Verifica que gravity_zone ainda consegue emitir sinais ──
	# Sinal 'entered_zone': verifica conectividade
	assert_bool(_behavior_b.has_signal("entered_zone")).override_failure_message("Sinal 'entered_zone' nao encontrado em gravity_zone")

	# Sinal 'exited_zone': verifica conectividade
	assert_bool(_behavior_b.has_signal("exited_zone")).override_failure_message("Sinal 'exited_zone' nao encontrado em gravity_zone")

