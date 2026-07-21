extends GdUnitTestSuite
func test_combo_sequence() -> void: var cd:=ComboDetector.new(); cd.set_sequence(["punch","punch","kick"]); var e:=false; cd.combo_finished.connect(func(_s): e=true); cd.register_input("punch"); cd.register_input("punch"); cd.register_input("kick"); assert_bool(e).is_true(); cd.queue_free()
func test_wrong_input() -> void: var cd:=ComboDetector.new(); cd.set_sequence(["punch","kick"]); cd.register_input("punch"); cd.register_input("punch"); assert_int(cd._current_step).is_equal(0); cd.queue_free()
