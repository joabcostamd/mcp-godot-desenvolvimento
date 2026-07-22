## test_storage.gd — Testes do Storage | GdUnit4.
## Cobre set/get com tipos variados, erase, has_key, clear, sinais.

extends GdUnitTestSuite

func _make_s() -> Storage: return Storage.new()

func test_default_parameters() -> void:
	var s := _make_s()
	assert_str(s.file_path).is_equal("user://storage.cfg")
	assert_bool(s.auto_save).is_true()
	assert_str(s.section).is_equal("data")
	s.queue_free()

func test_set_get_int() -> void:
	var s := _make_s(); add_child(s)
	s.set_data("hp", 100)
	assert_int(s.get_data("hp", 0)).is_equal(100)
	remove_child(s); s.queue_free()

func test_set_get_float() -> void:
	var s := _make_s(); add_child(s)
	s.set_data("volume", 0.75)
	assert_float(s.get_data("volume", 0.0)).is_equal(0.75)
	remove_child(s); s.queue_free()

func test_set_get_string() -> void:
	var s := _make_s(); add_child(s)
	s.set_data("name", "Hero")
	assert_str(s.get_data("name", "")).is_equal("Hero")
	remove_child(s); s.queue_free()

func test_set_get_bool() -> void:
	var s := _make_s(); add_child(s)
	s.set_data("completed", true)
	assert_bool(s.get_data("completed", false)).is_true()
	remove_child(s); s.queue_free()

func test_default_value_when_missing() -> void:
	var s := _make_s(); add_child(s)
	assert_int(s.get_data("nonexistent", 42)).is_equal(42)
	remove_child(s); s.queue_free()

func test_has_key() -> void:
	var s := _make_s(); add_child(s)
	assert_bool(s.has_key("hp")).is_false()
	s.set_data("hp", 50)
	assert_bool(s.has_key("hp")).is_true()
	remove_child(s); s.queue_free()

func test_erase_key() -> void:
	var s := _make_s(); add_child(s)
	s.set_data("hp", 100)
	s.erase_key("hp")
	assert_bool(s.has_key("hp")).is_false()
	remove_child(s); s.queue_free()

func test_clear_all() -> void:
	var s := _make_s(); add_child(s)
	s.set_data("a", 1); s.set_data("b", 2)
	s.clear_all()
	assert_bool(s.has_key("a")).is_false()
	assert_bool(s.has_key("b")).is_false()
	remove_child(s); s.queue_free()

func test_data_changed_signal() -> void:
	var s := _make_s(); add_child(s)
	var emitted := false
	var key := ""
	s.data_changed.connect(func(k): emitted = true; key = k)
	s.set_data("score", 999)
	assert_bool(emitted).is_true()
	assert_str(key).is_equal("score")
	remove_child(s); s.queue_free()
