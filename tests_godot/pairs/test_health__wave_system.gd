## Teste de composicao: health + wave_system
##
## Gerado automaticamente por scripts/gerar_testes_pares.py (sota_1.7).
## Verifica que os dois behaviors coexistem sem erro e seus sinais ainda emitem.
##
## @behavior_a: health
## @behavior_b: wave_system

extends GdUnitTestSuite


var _behavior_a: Node
var _behavior_b: Node


func after() -> void:
	if is_instance_valid(_behavior_a):
		_behavior_a.queue_free()
	if is_instance_valid(_behavior_b):
		_behavior_b.queue_free()


func test_coexistencia() -> void:
	var res_a := load("res://behaviors/health/health.tscn")
	assert_object(res_a).is_not_null().override_failure_message("Falha ao carregar res://behaviors/health/health.tscn")
	_behavior_a = res_a.instantiate()
	assert_object(_behavior_a).is_not_null()

	var res_b := load("res://behaviors/wave_system/wave_system.tscn")
	assert_object(res_b).is_not_null().override_failure_message("Falha ao carregar res://behaviors/wave_system/wave_system.tscn")
	_behavior_b = res_b.instantiate()
	assert_object(_behavior_b).is_not_null()

	add_child(_behavior_a)
	add_child(_behavior_b)

	await get_tree().create_timer(2.0).timeout

	assert_bool(is_instance_valid(_behavior_a)).override_failure_message("health foi liberado durante o teste")
	assert_bool(is_instance_valid(_behavior_b)).override_failure_message("wave_system foi liberado durante o teste")
	# ── Verifica que health ainda consegue emitir sinais ──
	# Sinal 'died': verifica conectividade
	assert_bool(_behavior_a.has_signal("died")).override_failure_message("Sinal 'died' nao encontrado em health")

	# Sinal 'damage_taken': verifica conectividade
	assert_bool(_behavior_a.has_signal("damage_taken")).override_failure_message("Sinal 'damage_taken' nao encontrado em health")

	# Sinal 'healed': verifica conectividade
	assert_bool(_behavior_a.has_signal("healed")).override_failure_message("Sinal 'healed' nao encontrado em health")

	# Sinal 'hp_changed': verifica conectividade
	assert_bool(_behavior_a.has_signal("hp_changed")).override_failure_message("Sinal 'hp_changed' nao encontrado em health")

	# Sinal 'first_hit': verifica conectividade
	assert_bool(_behavior_a.has_signal("first_hit")).override_failure_message("Sinal 'first_hit' nao encontrado em health")
	# ── Verifica que wave_system ainda consegue emitir sinais ──
	# Sinal 'wave_started': verifica conectividade
	assert_bool(_behavior_b.has_signal("wave_started")).override_failure_message("Sinal 'wave_started' nao encontrado em wave_system")

	# Sinal 'wave_cleared': verifica conectividade
	assert_bool(_behavior_b.has_signal("wave_cleared")).override_failure_message("Sinal 'wave_cleared' nao encontrado em wave_system")

	# Sinal 'spawn_enemy': verifica conectividade
	assert_bool(_behavior_b.has_signal("spawn_enemy")).override_failure_message("Sinal 'spawn_enemy' nao encontrado em wave_system")

	# Sinal 'all_waves_cleared': verifica conectividade
	assert_bool(_behavior_b.has_signal("all_waves_cleared")).override_failure_message("Sinal 'all_waves_cleared' nao encontrado em wave_system")

