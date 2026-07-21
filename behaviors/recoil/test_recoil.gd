extends GdUnitTestSuite
func _make_r() -> Recoil: return Recoil.new()
func test_defaults() -> void:
	var r := _make_r(); assert_float(r.recoil_amount).is_equal(20); assert_float(r.recovery_speed).is_equal(100); r.queue_free()
func test_apply_recoil() -> void:
	var r := _make_r(); r.apply_recoil(); assert_float(r._offset.length()).is_greater(0); r.queue_free()
func test_recovery() -> void:
	var p := Node2D.new(); add_child(p); var r := _make_r(); p.add_child(r)
	r.apply_recoil(); r._process(0.5); assert_float(r._offset.length()).is_less(20); remove_child(p); p.queue_free(); r.queue_free()
func test_amount_clamped() -> void:
	var r := _make_r(); r.recoil_amount = 0; assert_float(r.recoil_amount).is_equal(1); r.queue_free()
