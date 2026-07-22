## test_spawner_wave.gd — GdUnit4.

extends GdUnitTestSuite


func test_spawns_enemy() -> void:
	var pool := _make_pool(5)
	var sw := _make_spawner(3, 10.0, 0.1, 50)
	sw._pool = pool
	add_child(sw)

	var spawned := false
	sw.enemy_spawned.connect(func(_e): spawned = true)
	sw._try_spawn()
	assert_bool(spawned).is_true()


func test_wave_started_signal() -> void:
	var pool := _make_pool(5)
	var sw := _make_spawner(3, 10.0, 0.1, 50)
	sw._pool = pool
	add_child(sw)

	var wave := 0
	sw.wave_started.connect(func(w): wave = w)
	sw._start_next_wave()
	assert_int(wave).is_equal(1)


func test_respects_max_active() -> void:
	var pool := _make_pool(10)
	var sw := _make_spawner(100, 10.0, 0.1, 2)
	sw._pool = pool
	add_child(sw)
	sw._spawning = true

	sw._try_spawn()
	sw._try_spawn()
	var count_after := sw._active_enemies
	assert_int(count_after).is_equal(2)
	sw._try_spawn()  # bloqueado por max_active=2
	assert_int(sw._active_enemies).is_equal(2)


func test_spawn_count_per_wave() -> void:
	var pool := _make_pool(10)
	var sw := _make_spawner(3, 10.0, 0.1, 50)
	sw._pool = pool
	add_child(sw)
	sw._spawning = true

	sw._try_spawn()
	sw._try_spawn()
	sw._try_spawn()
	assert_int(sw._spawned_this_wave).is_equal(3)
	sw._try_spawn()  # não deve spawnar mais
	assert_int(sw._spawned_this_wave).is_equal(3)


func test_wave_cleared_signal() -> void:
	var pool := _make_pool(5)
	var sw := _make_spawner(1, 10.0, 0.1, 50)
	sw._pool = pool
	add_child(sw)
	sw._spawning = true
	sw._try_spawn()
	sw._spawning = false
	sw._active_enemies = 1

	var cleared := 0
	sw.wave_cleared.connect(func(w): cleared = w)
	sw._on_enemy_died(sw)  # simula morte (decrementa _active_enemies)
	assert_int(cleared).is_equal(1)


func test_no_pool_no_crash() -> void:
	var sw := _make_spawner(3, 10.0, 0.1, 50)
	add_child(sw)
	sw._spawning = true
	sw._try_spawn()
	assert_bool(true)


func test_get_current_wave() -> void:
	var sw := _make_spawner(3, 10.0, 0.1, 50)
	var pool := _make_pool(5)
	sw._pool = pool
	add_child(sw)
	sw._start_next_wave()
	assert_int(sw.get_current_wave()).is_equal(1)


func test_warning_no_pool() -> void:
	var sw := _make_spawner(3, 10.0, 0.1, 50)
	add_child(sw)
	var found := false
	for w in sw._get_configuration_warnings():
		if "ObjectPool" in w:
			found = true
	assert_bool(found).is_true()


func test_all_waves_done_signal() -> void:
	var pool := _make_pool(5)
	var sw := _make_spawner(1, 10.0, 0.1, 50)
	sw._pool = pool
	sw.total_waves = 1
	sw._current_wave = 1
	add_child(sw)

	var done := false
	sw.all_waves_done.connect(func(): done = true)
	sw._finish_wave()
	assert_bool(done).is_true()


func test_ready_guard_no_double_init() -> void:
	var pool := _make_pool(5)
	var sw := _make_spawner(3, 10.0, 0.1, 50)
	sw._pool = pool
	add_child(sw)
	sw._ready()
	assert_int(sw._current_wave).is_equal(1)


func _make_spawner(count: int, interval: float, delay: float, max_act: int) -> SpawnerWave:
	var sw := SpawnerWave.new()
	sw.spawn_count_per_wave = count
	sw.wave_interval = interval
	sw.spawn_delay = delay
	sw.max_active = max_act
	sw.spawn_radius = 300.0
	return sw


func _make_pool(size: int) -> ObjectPool:
	var pool := ObjectPool.new()
	pool.pool_size = size
	pool.expandable = false
	var scene := PackedScene.new()
	var dummy := Node2D.new()
	scene.pack(dummy)
	dummy.free()
	pool.prefab = scene
	add_child(pool)
	return pool
