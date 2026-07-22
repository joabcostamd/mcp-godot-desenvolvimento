## test_score.gd — Testes do behavior Score | GdUnit4.

extends GdUnitTestSuite


func _make_sc() -> Score:
	return Score.new()


func test_script_compiles() -> void:
	var sc := Score.new(); assert_object(sc).is_not_null(); sc.queue_free()


func test_default_parameters() -> void:
	var sc := Score.new()
	assert_float(sc.combo_multiplier).is_equal(0.1)
	assert_float(sc.combo_window).is_equal(2.0)
	assert_int(sc.get_score()).is_equal(0)
	sc.queue_free()


func test_add_score_increments() -> void:
	var sc := _make_sc(); add_child(sc)
	sc.add_score(100)
	assert_int(sc.get_score()).is_equal(100)
	remove_child(sc); sc.queue_free()


func test_add_score_emits_signal() -> void:
	var sc := _make_sc(); add_child(sc)
	var val := 0
	sc.score_changed.connect(func(v: int): val = v)
	sc.add_score(50)
	assert_int(val).is_equal(50)
	remove_child(sc); sc.queue_free()


func test_combo_increments() -> void:
	var sc := _make_sc(); add_child(sc)
	sc.add_score(10); sc.add_score(10)
	assert_int(sc.get_combo()).is_equal(2)
	remove_child(sc); sc.queue_free()


func test_reset_score() -> void:
	var sc := _make_sc(); add_child(sc)
	sc.add_score(500); sc.reset_score()
	assert_int(sc.get_score()).is_equal(0)
	assert_int(sc.get_combo()).is_equal(0)
	remove_child(sc); sc.queue_free()
