## test_element_system.gd — Testes do ElementSystem | GdUnit4.

extends GdUnitTestSuite

func _make_es() -> ElementSystem:
	return ElementSystem.new()


func test_default_parameters() -> void:
	var es := _make_es()
	assert_str(es.entity_element).is_equal("physical")
	assert_float(es.weakness_multiplier).is_equal(2.0)
	assert_float(es.resistance_multiplier).is_equal(0.5)
	es.queue_free()


func test_physical_always_neutral() -> void:
	var es := _make_es()
	es.entity_element = "fire"
	assert_float(es.get_multiplier("physical")).is_equal(1.0)
	es.queue_free()


func test_same_element_neutral() -> void:
	var es := _make_es()
	es.entity_element = "fire"
	assert_float(es.get_multiplier("fire")).is_equal(1.0)
	es.queue_free()


func test_weakness() -> void:
	var es := _make_es()
	es.entity_element = "ice"
	assert_float(es.get_multiplier("fire")).is_equal(2.0)  # fire > ice
	es.queue_free()


func test_resistance() -> void:
	var es := _make_es()
	es.entity_element = "fire"
	assert_float(es.get_multiplier("ice")).is_equal(0.5)  # ice < fire
	es.queue_free()


func test_calculate_damage_weakness() -> void:
	var es := _make_es()
	es.entity_element = "ice"
	var dmg := es.calculate_damage(100, "fire")
	assert_int(dmg).is_equal(200)  # 100 * 2.0
	es.queue_free()


func test_calculate_damage_resistance() -> void:
	var es := _make_es()
	es.entity_element = "fire"
	var dmg := es.calculate_damage(100, "ice")
	assert_int(dmg).is_equal(50)  # 100 * 0.5
	es.queue_free()


func test_is_strong_against() -> void:
	var es := _make_es()
	assert_bool(es.is_strong_against("fire", "ice")).is_true()
	assert_bool(es.is_strong_against("ice", "fire")).is_false()
	es.queue_free()


func test_custom_weakness_table() -> void:
	var es := _make_es()
	es.set_weaknesses("light", ["dark"])
	es.entity_element = "dark"
	assert_float(es.get_multiplier("light")).is_equal(2.0)
	es.queue_free()


func test_damage_modified_signal() -> void:
	var es := _make_es()
	es.entity_element = "ice"
	var emitted := false
	var orig := 0
	var mod := 0
	es.damage_modified.connect(func(o, m, _e): emitted = true; orig = o; mod = m)
	es.calculate_damage(50, "fire")
	assert_bool(emitted).is_true()
	assert_int(orig).is_equal(50)
	assert_int(mod).is_equal(100)
	es.queue_free()


func test_multiplier_clamped() -> void:
	var es := _make_es()
	es.weakness_multiplier = -1.0
	assert_float(es.weakness_multiplier).is_equal(1.0)
	es.weakness_multiplier = 99.0
	assert_float(es.weakness_multiplier).is_equal(5.0)
	es.resistance_multiplier = -1.0
	assert_float(es.resistance_multiplier).is_equal(0.0)
	es.resistance_multiplier = 2.0
	assert_float(es.resistance_multiplier).is_equal(1.0)
	es.queue_free()
