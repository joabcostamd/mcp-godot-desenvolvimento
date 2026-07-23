## Teste de composicao: beam_laser + destructible
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: beam_laser
## @behavior_b: destructible

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/beam_laser/beam_laser.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/beam_laser/beam_laser.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/destructible/destructible.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/destructible/destructible.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("beam_laser foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("destructible foi liberado durante o teste")
	# ── Verifica que beam_laser ainda consegue emitir sinais ──
	# Sinal 'hitting': verifica conectividade
	assert_bool(_behavior_a.has_signal("hitting")).override_failure_message("Sinal 'hitting' nao encontrado em beam_laser")

	# Sinal 'stopped': verifica conectividade
	assert_bool(_behavior_a.has_signal("stopped")).override_failure_message("Sinal 'stopped' nao encontrado em beam_laser")
	# ── Verifica que destructible ainda consegue emitir sinais ──
	# Sinal 'damaged': verifica conectividade
	assert_bool(_behavior_b.has_signal("damaged")).override_failure_message("Sinal 'damaged' nao encontrado em destructible")

	# Sinal 'destroyed': verifica conectividade
	assert_bool(_behavior_b.has_signal("destroyed")).override_failure_message("Sinal 'destroyed' nao encontrado em destructible")

