## test_pause_menu.gd — Testes do behavior PauseMenu | GdUnit4.

extends GdUnitTestSuite


func _make_pm() -> PauseMenu:
	return PauseMenu.new()


func test_pause_emits_signal() -> void:
	var pm := _make_pm(); add_child(pm)
	var emitted := false; pm.paused.connect(func(): emitted = true)
	pm.pause()
	assert_bool(emitted).is_true()
	assert_bool(pm.is_paused()).is_true()
	pm.resume()  # cleanup


func test_resume_emits_signal() -> void:
	var pm := _make_pm(); add_child(pm)
	pm.pause()
	var emitted := false; pm.resumed.connect(func(): emitted = true)
	pm.resume()
	assert_bool(emitted).is_true()
	assert_bool(pm.is_paused()).is_false()


func test_toggle_alternates() -> void:
	var pm := _make_pm(); add_child(pm)
	pm.toggle()
	assert_bool(pm.is_paused()).is_true()
	pm.toggle()
	assert_bool(pm.is_paused()).is_false()


func test_pause_twice_noop() -> void:
	var pm := _make_pm(); add_child(pm)
	pm.pause()
	var count := 0; pm.paused.connect(func(): count += 1)
	pm.pause()
	assert_int(count).is_equal(0)
	pm.resume()


func test_resume_twice_noop() -> void:
	var pm := _make_pm(); add_child(pm)
	pm.resume()  # já está rodando
	assert_bool(pm.is_paused()).is_false()


func test_is_paused_initially_false() -> void:
	var pm := _make_pm(); add_child(pm)
	assert_bool(pm.is_paused()).is_false()
