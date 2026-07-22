## test_input_manager.gd — Testes do InputManager | GdUnit4.

extends GdUnitTestSuite


func _make_im() -> InputManager:
	return InputManager.new()


# ---------------------------------------------------------------------------
# DEVICE DETECTION
# ---------------------------------------------------------------------------

func test_detect_keyboard() -> void:
	var im := _make_im()
	var event := InputEventKey.new()
	event.keycode = KEY_A
	im._input(event)
	assert_str(im.get_device_type()).is_equal("keyboard")
	im.queue_free()


func test_detect_gamepad() -> void:
	var im := _make_im()
	var event := InputEventJoypadButton.new()
	event.button_index = JOY_BUTTON_A
	im._input(event)
	assert_str(im.get_device_type()).is_equal("gamepad")
	im.queue_free()


func test_detect_touch() -> void:
	var im := _make_im()
	var event := InputEventScreenTouch.new()
	im._input(event)
	assert_str(im.get_device_type()).is_equal("touch")
	im.queue_free()


func test_device_changed_signal() -> void:
	var im := _make_im()
	var emitted := false
	var dev_type := ""
	im.device_changed.connect(func(d): emitted = true; dev_type = d)

	im._input(InputEventJoypadButton.new())
	assert_bool(emitted).is_true()
	assert_str(dev_type).is_equal("gamepad")
	im.queue_free()


func test_device_changed_no_duplicate() -> void:
	"""PADRÃO 10: mesmo dispositivo não re-emite sinal."""
	var im := _make_im()
	im._input(InputEventKey.new())  # keyboard

	var count := 0
	im.device_changed.connect(func(_d): count += 1)
	im._input(InputEventKey.new())  # ainda keyboard

	assert_int(count).is_equal(0)
	im.queue_free()


# ---------------------------------------------------------------------------
# REBINDING
# ---------------------------------------------------------------------------

func test_rebind_action() -> void:
	# Registra ação de teste no InputMap
	var action_name := "test_rebind_action"
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name)

	var im := _make_im()
	var event := InputEventKey.new()
	event.keycode = KEY_SPACE

	assert_bool(im.rebind_action(action_name, event)).is_true()

	var events := im.get_action_events(action_name)
	assert_bool(events.size() >= 1).is_true()

	# Limpeza
	im.reset_action(action_name)
	InputMap.erase_action(action_name)
	im.queue_free()


func test_rebind_nonexistent_action() -> void:
	var im := _make_im()
	var event := InputEventKey.new()
	assert_bool(im.rebind_action("does_not_exist_xyz", event)).is_false()
	im.queue_free()


func test_action_rebound_signal() -> void:
	var action_name := "test_signal_action"
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name)

	var im := _make_im()
	var emitted := false
	var rebound_action := ""
	im.action_rebound.connect(func(name, _e): emitted = true; rebound_action = name)

	var event := InputEventKey.new()
	event.keycode = KEY_ENTER
	im.rebind_action(action_name, event)

	assert_bool(emitted).is_true()
	assert_str(rebound_action).is_equal(action_name)

	im.reset_action(action_name)
	InputMap.erase_action(action_name)
	im.queue_free()


# ---------------------------------------------------------------------------
# SAVE / LOAD BINDINGS
# ---------------------------------------------------------------------------

func test_save_and_load_bindings() -> void:
	var action_name := "test_save_action"
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name)

	var im := _make_im()
	im.bindings_path = "user://test_bindings.cfg"

	# Configura binding
	var event := InputEventKey.new()
	event.keycode = KEY_Q
	im.rebind_action(action_name, event)

	# Salva
	assert_bool(im.save_bindings()).is_true()

	# Reseta e recarrega
	im.reset_action(action_name)
	assert_bool(im.load_bindings()).is_true()

	var events := im.get_action_events(action_name)
	assert_bool(events.size() >= 1).is_true()

	# Limpeza
	im.reset_action(action_name)
	InputMap.erase_action(action_name)
	DirAccess.remove_absolute("user://test_bindings.cfg")
	im.queue_free()


func test_load_nonexistent_file() -> void:
	var im := _make_im()
	im.bindings_path = "user://nonexistent_bindings_xyz.cfg"
	assert_bool(im.load_bindings()).is_false()
	im.queue_free()


# ---------------------------------------------------------------------------
# EDGE CASES
# ---------------------------------------------------------------------------

func test_rebind_null_event() -> void:
	var im := _make_im()
	assert_bool(im.rebind_action("ui_accept", null)).is_false()
	im.queue_free()


func test_reset_action() -> void:
	var action_name := "test_reset_action"
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name)

	var im := _make_im()
	var event := InputEventKey.new()
	event.keycode = KEY_F
	im.rebind_action(action_name, event)
	assert_bool(im.get_action_events(action_name).size() > 0).is_true()

	im.reset_action(action_name)
	assert_int(im.get_action_events(action_name).size()).is_equal(0)

	InputMap.erase_action(action_name)
	im.queue_free()


func test_reset_all() -> void:
	var action1 := "test_reset_a"
	var action2 := "test_reset_b"
	if not InputMap.has_action(action1): InputMap.add_action(action1)
	if not InputMap.has_action(action2): InputMap.add_action(action2)

	var im := _make_im()
	im.rebind_action(action1, InputEventKey.new())
	im.rebind_action(action2, InputEventKey.new())

	im.reset_all()

	assert_int(im.get_action_events(action1).size()).is_equal(0)
	assert_int(im.get_action_events(action2).size()).is_equal(0)

	InputMap.erase_action(action1)
	InputMap.erase_action(action2)
	im.queue_free()
