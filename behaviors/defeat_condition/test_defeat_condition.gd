## test_defeat_condition.gd — Testes do behavior DefeatCondition | GdUnit4.

extends GdUnitTestSuite


func _make_dc() -> DefeatCondition:
	return DefeatCondition.new()


func test_script_compiles() -> void:
	var dc := DefeatCondition.new()
	assert_object(dc).is_not_null()
	dc.queue_free()


func test_default_parameters() -> void:
	var dc := DefeatCondition.new()
	assert_int(dc.condition_type).is_equal(0)
	assert_str(dc.player_group).is_equal("players")
	assert_bool(dc.is_triggered()).is_false()
	dc.queue_free()


func test_check_triggers() -> void:
	var dc := _make_dc()
	dc.check(true)
	assert_bool(dc.is_triggered()).is_true()
	dc.queue_free()


func test_check_false_noop() -> void:
	var dc := _make_dc()
	dc.check(false)
	assert_bool(dc.is_triggered()).is_false()
	dc.queue_free()


func test_trigger_manual() -> void:
	var dc := _make_dc()
	dc.trigger()
	assert_bool(dc.is_triggered()).is_true()
	dc.queue_free()
