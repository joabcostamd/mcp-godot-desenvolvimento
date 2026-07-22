## test_object_pool.gd — GdUnit4.

extends GdUnitTestSuite


func test_take_returns_object() -> void:
	var pool := _make_pool(5, true)
	assert_int(pool._available.size()).is_equal(5)
	var obj := pool.take()
	assert_object(obj).is_not_null()
	assert_int(pool._active.size()).is_equal(1)
	assert_int(pool._available.size()).is_equal(4)


func test_take_exhausts_pool() -> void:
	var pool := _make_pool(2, false)
	pool.take()
	pool.take()
	var obj := pool.take()
	assert_object(obj).is_null()


func test_expandable_creates_more() -> void:
	var pool := _make_pool(1, true)
	pool.take()
	assert_int(pool._available.size()).is_equal(0)
	var obj := pool.take()
	assert_object(obj).is_not_null()


func test_return_reuses_object() -> void:
	var pool := _make_pool(2, false)
	var obj := pool.take()
	pool.return_object(obj)
	var obj2 := pool.take()
	assert_object(obj2).is_equal(obj)


func test_return_deactivates() -> void:
	var pool := _make_pool(2, false)
	var obj := pool.take()
	pool.return_object(obj)
	assert_int(obj.process_mode).is_equal(Node.PROCESS_MODE_DISABLED)


func test_object_taken_signal() -> void:
	var pool := _make_pool(2, false)
	var emitted := false
	pool.object_taken.connect(func(_o): emitted = true)
	pool.take()
	assert_bool(emitted).is_true()


func test_object_returned_signal() -> void:
	var pool := _make_pool(2, false)
	var obj := pool.take()
	var emitted := false
	pool.object_returned.connect(func(_o): emitted = true)
	pool.return_object(obj)
	assert_bool(emitted).is_true()


func test_pool_empty_signal() -> void:
	var pool := _make_pool(1, false)
	pool.take()
	var emitted := false
	pool.pool_empty.connect(func(): emitted = true)
	pool.take()
	assert_bool(emitted).is_true()


func test_purge_stale() -> void:
	var pool := _make_pool(2, false)
	var obj := pool.take()
	remove_child(obj)
	obj.free()
	pool._purge_stale()
	assert_int(pool._active.size()).is_equal(0)


func test_no_prefab_no_crash() -> void:
	var pool := ObjectPool.new()
	pool.pool_size = 2
	pool.expandable = false
	add_child(pool)
	assert_object(pool.take()).is_null()


func test_ready_guard_no_double_init() -> void:
	var pool := _make_pool(2, false)
	var count_before := pool._available.size()
	pool._ready()
	assert_int(pool._available.size()).is_equal(count_before)


func _make_pool(size: int, expandable: bool) -> ObjectPool:
	var pool := ObjectPool.new()
	pool.pool_size = size
	pool.expandable = expandable
	# Cria um prefab mínimo: Node2D vazio
	var scene := PackedScene.new()
	var dummy := Node2D.new()
	scene.pack(dummy)
	dummy.free()
	pool.prefab = scene
	add_child(pool)
	return pool
