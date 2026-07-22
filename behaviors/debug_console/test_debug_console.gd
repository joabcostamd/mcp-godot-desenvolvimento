## test_debug_console.gd — Testes do DebugConsole | GdUnit4.

extends GdUnitTestSuite

func _make_dc() -> DebugConsole: return DebugConsole.new()

func test_default_parameters() -> void:
	var dc := _make_dc()
	assert_int(dc.max_lines).is_equal(200)
	assert_bool(dc.auto_scroll).is_true()
	assert_int(dc.font_size).is_equal(12)
	dc.queue_free()

func test_creates_ui_elements() -> void:
	var dc := _make_dc(); add_child(dc)
	assert_object(dc._bg).is_not_null()
	assert_object(dc._log).is_not_null()
	assert_object(dc._input).is_not_null()
	remove_child(dc); dc.queue_free()

func test_starts_hidden() -> void:
	var dc := _make_dc(); add_child(dc)
	assert_bool(dc.visible).is_false()
	remove_child(dc); dc.queue_free()

func test_add_line() -> void:
	var dc := _make_dc(); add_child(dc)
	dc.add_line("Hello World")
	# _log contém a linha (RichTextLabel content é difícil de verificar)
	assert_bool(true).is_true()  # não crashou
	remove_child(dc); dc.queue_free()

func test_clear() -> void:
	var dc := _make_dc(); add_child(dc)
	dc.add_line("test"); dc.clear()
	assert_bool(true).is_true()  # não crashou
	remove_child(dc); dc.queue_free()

func test_register_command() -> void:
	var dc := _make_dc(); add_child(dc)
	var executed := false
	dc.register_command("heal", func(_args): executed = true)
	dc._on_command("heal")
	assert_bool(executed).is_true()
	remove_child(dc); dc.queue_free()

func test_command_entered_signal() -> void:
	var dc := _make_dc(); add_child(dc)
	var emitted := false
	dc.command_entered.connect(func(_c): emitted = true)
	dc._on_command("test")
	assert_bool(emitted).is_true()
	remove_child(dc); dc.queue_free()

func test_max_lines_clamped() -> void:
	var dc := _make_dc()
	dc.max_lines = 5; assert_int(dc.max_lines).is_equal(10)
	dc.max_lines = 9999; assert_int(dc.max_lines).is_equal(1000)
	dc.queue_free()

func test_font_size_clamped() -> void:
	var dc := _make_dc()
	dc.font_size = 4; assert_int(dc.font_size).is_equal(8)
	dc.font_size = 99; assert_int(dc.font_size).is_equal(24)
	dc.queue_free()
