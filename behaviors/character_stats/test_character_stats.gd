## test_character_stats.gd — Testes do CharacterStats | GdUnit4.

extends GdUnitTestSuite

func _make_cs() -> CharacterStats:
	return CharacterStats.new()


func test_default_parameters() -> void:
	var cs := _make_cs()
	assert_int(cs.strength).is_equal(10)
	assert_int(cs.dexterity).is_equal(10)
	assert_int(cs.intelligence).is_equal(10)
	assert_int(cs.vitality).is_equal(10)
	cs.queue_free()


func test_physical_damage() -> void:
	var cs := _make_cs()
	cs.strength = 20
	assert_int(cs.get_physical_damage()).is_equal(40)  # 20 * 2
	cs.queue_free()


func test_magic_damage() -> void:
	var cs := _make_cs()
	cs.intelligence = 15
	assert_int(cs.get_magic_damage()).is_equal(30)  # 15 * 2
	cs.queue_free()


func test_attack_speed() -> void:
	var cs := _make_cs()
	cs.dexterity = 50
	assert_float(cs.get_attack_speed()).is_equal(2.0)  # 1 + 50*0.02
	cs.queue_free()


func test_modifier_affects_damage() -> void:
	var cs := _make_cs()
	cs.strength = 10
	assert_int(cs.get_physical_damage()).is_equal(20)
	cs.add_modifier("strength", 2.0)
	assert_int(cs.get_physical_damage()).is_equal(40)
	cs.queue_free()


func test_multiple_modifiers_stack() -> void:
	var cs := _make_cs()
	cs.strength = 10
	cs.add_modifier("strength", 1.5)
	cs.add_modifier("strength", 2.0)  # 1.5 * 2.0 = 3.0
	assert_int(cs.get_physical_damage()).is_equal(60)  # 10*2*3
	cs.queue_free()


func test_clear_modifiers() -> void:
	var cs := _make_cs()
	cs.strength = 10
	cs.add_modifier("strength", 3.0)
	cs.clear_modifiers("strength")
	assert_int(cs.get_physical_damage()).is_equal(20)
	cs.queue_free()


func test_get_stat_with_modifier() -> void:
	var cs := _make_cs()
	cs.intelligence = 10
	cs.add_modifier("intelligence", 2.0)
	assert_int(cs.get_stat("intelligence")).is_equal(20)
	cs.queue_free()


func test_stat_changed_signal() -> void:
	var cs := _make_cs()
	var emitted := false
	var stat_name := ""
	cs.stat_changed.connect(func(n, _v): emitted = true; stat_name = n)
	cs.strength = 25
	assert_bool(emitted).is_true()
	assert_str(stat_name).is_equal("strength")
	cs.queue_free()


func test_vitality_updates_max_hp() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var health := Health.new()
	health.max_hp = 50
	parent.add_child(health)
	var cs := _make_cs()
	cs.vitality = 20
	parent.add_child(cs)  # _ready chama _update_max_hp

	assert_int(health.max_hp).is_equal(200)  # 20 * 10

	remove_child(parent)
	parent.queue_free()
	health.queue_free()
	cs.queue_free()


func test_clamped_stats() -> void:
	var cs := _make_cs()
	cs.strength = 0
	assert_int(cs.strength).is_equal(1)
	cs.strength = 9999
	assert_int(cs.strength).is_equal(999)
	cs.queue_free()


func test_get_stat_unknown() -> void:
	var cs := _make_cs()
	assert_int(cs.get_stat("unknown")).is_equal(0)
	cs.queue_free()
