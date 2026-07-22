## test_wave_system.gd
extends GdUnitTestSuite

func _make_ws() -> WaveSystem:
	var ws := WaveSystem.new()
	ws.total_waves = 3
	ws.spawn_interval = 0.5
	ws.wave_duration = 3.0
	ws.rest_duration = 0.5
	ws.enemies_per_wave_base = 3
	ws.enemies_increment = 2
	return ws

func test_start_first_wave() -> void:
	var ws := _make_ws()
	var emitted := false
	ws.wave_started.connect(func(_w): emitted=true)
	ws.start()
	assert_bool(emitted).is_true()
	assert_int(ws.get_current_wave()).is_equal(1)
	ws.queue_free()

func test_spawn_enemy_signal() -> void:
	var ws := _make_ws()
	var spawns := []
	ws.spawn_enemy.connect(func(w): spawns.append(w))
	ws.start()
	ws._process(2.0)
	assert_bool(spawns.size() > 0).is_true()
	ws.queue_free()

func test_wave_cleared_and_next() -> void:
	var ws := _make_ws()
	ws.wave_duration = 0.5
	ws.rest_duration = 0.1
	var cleared := []
	ws.wave_cleared.connect(func(w): cleared.append(w))
	ws.start()
	ws._process(1.0)  # fim onda 1 + descanso + início onda 2
	assert_int(cleared.size()).is_equal(1)
	assert_int(ws.get_current_wave()).is_equal(2)
	ws.queue_free()

func test_all_waves_cleared() -> void:
	var ws := _make_ws()
	ws.total_waves = 1
	ws.wave_duration = 0.1
	var emitted := false
	ws.all_waves_cleared.connect(func(): emitted=true)
	ws.start()
	ws._process(1.0)
	assert_bool(emitted).is_true()
	assert_str(ws.get_state()).is_equal("idle")
	ws.queue_free()
