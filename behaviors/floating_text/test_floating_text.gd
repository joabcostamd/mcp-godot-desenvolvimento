## test_floating_text.gd — Testes do behavior FloatingText | GdUnit4.
##
## Cobre: show_text, cor, active, text_shown, subida, parâmetros, composição.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests na cena behaviors/floating_text/test_floating_text.gd

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_ft(speed := 100.0, lifetime := 1.0, fade := 0.3) -> FloatingText:
	var ft := FloatingText.new()
	ft.speed = speed
	ft.lifetime = lifetime
	ft.fade_duration = fade
	return ft


# ═══════════════════════════════════════════════════════════════════════════════
# ESTÁTICO — Compilação e defaults
# ═══════════════════════════════════════════════════════════════════════════════

func test_script_compiles() -> void:
	var ft := FloatingText.new()
	assert_object(ft).is_not_null()
	ft.queue_free()


func test_default_parameters() -> void:
	var ft := FloatingText.new()
	assert_float(ft.speed).is_equal(100.0)
	assert_float(ft.lifetime).is_equal(1.0)
	assert_float(ft.fade_duration).is_equal(0.3)
	assert_int(ft.font_size).is_equal(24)
	assert_int(ft.outline_size).is_equal(2)
	ft.queue_free()


func test_parameter_clamping() -> void:
	var ft := FloatingText.new()
	ft.speed = 9999.0
	assert_float(ft.speed).is_equal(500.0)
	ft.speed = -5.0
	assert_float(ft.speed).is_equal(10.0)
	ft.lifetime = 0.01
	assert_float(ft.lifetime).is_equal(0.1)
	ft.lifetime = 99.0
	assert_float(ft.lifetime).is_equal(5.0)
	ft.font_size = 999
	assert_int(ft.font_size).is_equal(128)
	ft.font_size = 3
	assert_int(ft.font_size).is_equal(8)
	ft.outline_size = -1
	assert_int(ft.outline_size).is_equal(0)
	ft.outline_size = 99
	assert_int(ft.outline_size).is_equal(10)
	ft.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# UNITÁRIO — show_text e estado
# ═══════════════════════════════════════════════════════════════════════════════

func test_show_text_creates_label() -> void:
	var ft := _make_ft()
	add_child(ft)
	var ok := ft.show_text("10", Color.RED)
	assert_bool(ok).is_true()
	assert_bool(ft.is_active()).is_true()
	var label := ft.get_node_or_null("FloatingLabel")
	assert_object(label).is_not_null()
	if label:
		assert_str(label.text).is_equal("10")
	remove_child(ft)
	ft.queue_free()


func test_show_text_rejects_when_active() -> void:
	var ft := _make_ft()
	add_child(ft)
	ft.show_text("10", Color.RED)
	var ok := ft.show_text("20", Color.GREEN)
	assert_bool(ok).is_false()
	remove_child(ft)
	ft.queue_free()


func test_show_text_default_color_white() -> void:
	var ft := _make_ft()
	add_child(ft)
	ft.show_text("Test")
	var label: Label = ft.get_node_or_null("FloatingLabel")
	if label:
		var font_color: Color = label.get_theme_color("font_color")
		assert_that(font_color).is_equal(Color.WHITE)
	remove_child(ft)
	ft.queue_free()


func test_show_text_custom_color() -> void:
	var ft := _make_ft()
	add_child(ft)
	ft.show_text("Crit!", Color.YELLOW)
	var label: Label = ft.get_node_or_null("FloatingLabel")
	if label:
		var font_color: Color = label.get_theme_color("font_color")
		assert_that(font_color).is_equal(Color.YELLOW)
	remove_child(ft)
	ft.queue_free()


func test_is_active_initially_false() -> void:
	var ft := _make_ft()
	assert_bool(ft.is_active()).is_false()
	ft.queue_free()


func test_label_has_outline_when_configured() -> void:
	var ft := _make_ft()
	ft.outline_size = 3
	add_child(ft)
	ft.show_text("Test")
	var label: Label = ft.get_node_or_null("FloatingLabel")
	if label:
		var outline: int = label.get_theme_constant("outline_size")
		assert_int(outline).is_equal(3)
	remove_child(ft)
	ft.queue_free()


func test_zero_outline_skips_outline() -> void:
	var ft := _make_ft()
	ft.outline_size = 0
	add_child(ft)
	ft.show_text("Test")
	assert_bool(ft.is_active()).is_true()
	remove_child(ft)
	ft.queue_free()


func test_font_size_applied() -> void:
	var ft := _make_ft()
	ft.font_size = 48
	add_child(ft)
	ft.show_text("Big")
	var label: Label = ft.get_node_or_null("FloatingLabel")
	if label:
		var size: int = label.get_theme_font_size("font_size")
		assert_int(size).is_equal(48)
	remove_child(ft)
	ft.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# CENA — Comportamento em árvore
# ═══════════════════════════════════════════════════════════════════════════════

func test_text_moves_upward() -> void:
	var ft := _make_ft(200.0, 0.5, 0.0)
	add_child(ft)
	var start_y: float = ft.position.y
	ft.show_text("UP", Color.GREEN)
	# Simula alguns frames de _process
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame
	assert_float(ft.position.y).is_less(start_y)
	remove_child(ft)
	ft.queue_free()


func test_text_shown_emitted_after_lifetime() -> void:
	var ft := _make_ft(1000.0, 0.05, 0.0)  # lifetime muito curto
	add_child(ft)
	var emitted := false
	ft.text_shown.connect(func(): emitted = true)
	ft.show_text("42", Color.WHITE)
	# Espera mais que o lifetime
	await get_tree().create_timer(0.1).timeout
	assert_bool(emitted).is_true()
	# Já deu queue_free, não precisa remover


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSIÇÃO — Com outros behaviors
# ═══════════════════════════════════════════════════════════════════════════════

func test_composes_with_health() -> void:
	var parent := Node2D.new()
	add_child(parent)

	var health := Health.new()
	health.max_hp = 100
	parent.add_child(health)

	var ft := _make_ft()
	parent.add_child(ft)

	ft.show_text("-10", Color.RED)
	assert_bool(ft.is_active()).is_true()

	remove_child(parent)
	parent.queue_free()


func test_composes_with_screen_shake() -> void:
	var parent := Node2D.new()
	add_child(parent)

	var shake := ScreenShake.new()
	parent.add_child(shake)

	var ft := _make_ft()
	parent.add_child(ft)

	ft.show_text("BOOM", Color.ORANGE)
	assert_bool(ft.is_active()).is_true()

	remove_child(parent)
	parent.queue_free()


func test_multiple_floating_texts_independent() -> void:
	var parent := Node2D.new()
	add_child(parent)

	var ft1 := _make_ft(100.0, 1.0, 0.3)
	var ft2 := _make_ft(150.0, 0.8, 0.2)
	parent.add_child(ft1)
	parent.add_child(ft2)

	ft1.show_text("10", Color.RED)
	ft2.show_text("20", Color.GREEN)

	assert_bool(ft1.is_active()).is_true()
	assert_bool(ft2.is_active()).is_true()

	remove_child(parent)
	parent.queue_free()


func test_text_shown_cleans_up() -> void:
	var ft := _make_ft(1000.0, 0.03, 0.0)
	add_child(ft)
	ft.show_text("x", Color.WHITE)
	await get_tree().create_timer(0.1).timeout
	# Após text_shown, queue_free foi chamado — não deve estar mais na árvore
	assert_bool(is_instance_valid(ft)).is_false()
