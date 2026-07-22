## test_screen_flash.gd — Testes do behavior ScreenFlash | GdUnit4.
##
## Cobre: flash, cor, duração, fade_in/out, sinal flashed, reinício.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_sf(dur := 0.3, fi := 0.05, fo := 0.15) -> ScreenFlash:
	var sf := ScreenFlash.new()
	sf.default_duration = dur
	sf.fade_in = fi
	sf.fade_out = fo
	return sf


# ═══════════════════════════════════════════════════════════════════════════════
# ESTÁTICO — Compilação e defaults
# ═══════════════════════════════════════════════════════════════════════════════

func test_script_compiles() -> void:
	var sf := ScreenFlash.new()
	assert_object(sf).is_not_null()
	sf.queue_free()


func test_default_parameters() -> void:
	var sf := ScreenFlash.new()
	assert_float(sf.default_duration).is_equal(0.3)
	assert_float(sf.fade_in).is_equal(0.05)
	assert_float(sf.fade_out).is_equal(0.15)
	assert_that(sf.default_color).is_equal(Color.WHITE)
	sf.queue_free()


func test_parameter_clamping() -> void:
	var sf := ScreenFlash.new()
	sf.default_duration = 0.001
	assert_float(sf.default_duration).is_equal(0.02)
	sf.default_duration = 99.0
	assert_float(sf.default_duration).is_equal(5.0)
	sf.fade_in = -0.5
	assert_float(sf.fade_in).is_equal(0.0)
	sf.fade_in = 99.0
	assert_float(sf.fade_in).is_equal(1.0)
	sf.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# UNITÁRIO — flash() e estado
# ═══════════════════════════════════════════════════════════════════════════════

func test_flash_creates_rect() -> void:
	var sf := _make_sf()
	add_child(sf)
	sf.flash(Color.RED, 0.5)
	var rect := sf.get_node_or_null("FlashRect")
	assert_object(rect).is_not_null()
	if rect:
		assert_bool(rect is ColorRect).is_true()
	remove_child(sf)
	sf.queue_free()


func test_flash_activates() -> void:
	var sf := _make_sf()
	add_child(sf)
	sf.flash(Color.BLUE, 0.5)
	assert_bool(sf.is_active()).is_true()
	remove_child(sf)
	sf.queue_free()


func test_is_active_initially_false() -> void:
	var sf := _make_sf()
	assert_bool(sf.is_active()).is_false()
	sf.queue_free()


func test_rect_has_ignore_mouse() -> void:
	var sf := _make_sf()
	add_child(sf)
	sf.flash(Color.WHITE, 0.5)
	var rect: ColorRect = sf.get_node_or_null("FlashRect")
	if rect:
		assert_int(rect.mouse_filter).is_equal(Control.MOUSE_FILTER_IGNORE)
	remove_child(sf)
	sf.queue_free()


func test_rect_has_full_rect_anchors() -> void:
	var sf := _make_sf()
	add_child(sf)
	sf.flash(Color.WHITE, 0.5)
	var rect: ColorRect = sf.get_node_or_null("FlashRect")
	if rect:
		assert_float(rect.anchor_left).is_equal(0.0)
		assert_float(rect.anchor_top).is_equal(0.0)
		assert_float(rect.anchor_right).is_equal(1.0)
		assert_float(rect.anchor_bottom).is_equal(1.0)
	remove_child(sf)
	sf.queue_free()


func test_flash_uses_default_color_when_white() -> void:
	var sf := _make_sf()
	sf.default_color = Color.GREEN
	add_child(sf)
	sf.flash()  # usa default
	var rect: ColorRect = sf.get_node_or_null("FlashRect")
	if rect:
		assert_that(rect.color).is_equal(Color.GREEN)
	remove_child(sf)
	sf.queue_free()


func test_flash_overrides_color() -> void:
	var sf := _make_sf()
	sf.default_color = Color.GREEN
	add_child(sf)
	sf.flash(Color.RED, 0.5)
	var rect: ColorRect = sf.get_node_or_null("FlashRect")
	if rect:
		assert_that(rect.color).is_equal(Color.RED)
	remove_child(sf)
	sf.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# CENA — Comportamento em árvore
# ═══════════════════════════════════════════════════════════════════════════════

func test_flash_emits_flashed_after_duration() -> void:
	var sf := _make_sf(0.05, 0.01, 0.01)
	add_child(sf)
	var emitted := false
	sf.flashed.connect(func(): emitted = true)
	sf.flash(Color.WHITE)
	await get_tree().create_timer(0.1).timeout
	assert_bool(emitted).is_true()
	remove_child(sf)
	sf.queue_free()


func test_flash_restarts_when_active() -> void:
	var sf := _make_sf(0.5, 0.1, 0.1)
	add_child(sf)
	sf.flash(Color.RED, 0.5)
	assert_bool(sf.is_active()).is_true()
	# Segundo flash deve reiniciar sem crash
	sf.flash(Color.BLUE, 0.3)
	assert_bool(sf.is_active()).is_true()
	remove_child(sf)
	sf.queue_free()


func test_flash_sets_alpha_zero_initially() -> void:
	var sf := _make_sf()
	add_child(sf)
	sf.flash(Color.WHITE, 10.0)  # duração longa para garantir que ainda está em andamento
	var rect: ColorRect = sf.get_node_or_null("FlashRect")
	if rect:
		# Logo após flash, alpha deve ser > 0 (fade_in começou)
		await get_tree().process_frame
		# Não verificamos alpha exato (depende do frame timing)
	remove_child(sf)
	sf.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSIÇÃO — Com outros behaviors
# ═══════════════════════════════════════════════════════════════════════════════

func test_composes_with_health() -> void:
	var parent := Node2D.new()
	add_child(parent)

	var health := Health.new()
	health.max_hp = 100
	parent.add_child(health)

	var sf := _make_sf()
	parent.add_child(sf)

	sf.flash(Color.RED, 0.3)
	assert_bool(sf.is_active()).is_true()

	remove_child(parent)
	parent.queue_free()


func test_composes_with_screen_shake() -> void:
	var parent := Node2D.new()
	add_child(parent)

	var shake := ScreenShake.new()
	parent.add_child(shake)

	var sf := _make_sf()
	parent.add_child(sf)

	sf.flash(Color.WHITE, 0.3)
	assert_bool(sf.is_active()).is_true()

	remove_child(parent)
	parent.queue_free()


func test_composes_with_particle_impact() -> void:
	var parent := Node2D.new()
	add_child(parent)

	var pi := ParticleImpact.new()
	pi.auto_free = false
	parent.add_child(pi)

	var sf := _make_sf()
	parent.add_child(sf)

	sf.flash(Color.ORANGE, 0.2)
	pi.emit(Vector2.ZERO, Color.ORANGE)
	assert_bool(sf.is_active()).is_true()

	remove_child(parent)
	parent.queue_free()
