## test_victory_condition.gd — Testes do behavior VictoryCondition | GdUnit4.

extends GdUnitTestSuite


func _make_vc() -> VictoryCondition:
	return VictoryCondition.new()


func test_script_compiles() -> void:
	var vc := VictoryCondition.new()
	assert_object(vc).is_not_null()
	vc.queue_free()


func test_default_parameters() -> void:
	var vc := VictoryCondition.new()
	assert_int(vc.condition_type).is_equal(0)
	assert_float(vc.target_value).is_equal(0.0)
	assert_str(vc.enemy_group).is_equal("enemies")
	assert_bool(vc.is_achieved()).is_false()
	vc.queue_free()


func test_check_score_triggers() -> void:
	var vc := _make_vc()
	vc.condition_type = VictoryCondition.ConditionType.SCORE_REACHED
	vc.target_value = 10.0
	add_child(vc)
	vc.check(10.0)
	assert_bool(vc.is_achieved()).is_true()
	remove_child(vc)
	vc.queue_free()


func test_check_below_target_noop() -> void:
	var vc := _make_vc()
	vc.condition_type = VictoryCondition.ConditionType.SCORE_REACHED
	vc.target_value = 10.0
	vc.check(5.0)
	assert_bool(vc.is_achieved()).is_false()
	vc.queue_free()


func test_trigger_manual() -> void:
	var vc := _make_vc()
	vc.trigger()
	assert_bool(vc.is_achieved()).is_true()
	vc.queue_free()
