## test_camera_zoom.gd — Testes do behavior CameraZoom | GdUnit4.
##
## Cobre: zoom_to, reset, sem câmera, cancelamento, sinais.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_cz(dur := 0.5) -> CameraZoom:
	var cz := CameraZoom.new()
	cz.default_duration = dur
	return cz


# ═══════════════════════════════════════════════════════════════════════════════
# ESTÁTICO — Compilação e defaults
# ═══════════════════════════════════════════════════════════════════════════════

func test_script_compiles() -> void:
	var cz := CameraZoom.new()
	assert_object(cz).is_not_null()
	cz.queue_free()


func test_default_parameters() -> void:
	var cz := CameraZoom.new()
	assert_float(cz.default_duration).is_equal(0.5)
	assert_that(cz.default_zoom).is_equal(Vector2(1.0, 1.0))
	cz.queue_free()


func test_parameter_clamping() -> void:
	var cz := CameraZoom.new()
	cz.default_duration = -1.0
	assert_float(cz.default_duration).is_equal(0.0)
	cz.default_duration = 99.0
	assert_float(cz.default_duration).is_equal(5.0)
	cz.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# UNITÁRIO — zoom_to e estado
# ═══════════════════════════════════════════════════════════════════════════════

func test_zoom_to_instant_with_camera() -> void:
	var camera := Camera2D.new()
	add_child(camera)
	var cz := _make_cz()
	camera.add_child(cz)

	var target := Vector2(2.0, 2.0)
	cz.zoom_to(target, 0.0)
	assert_that(camera.zoom).is_equal(target)

	remove_child(camera)
	camera.queue_free()


func test_zoom_to_no_camera_is_noop() -> void:
	var cz := _make_cz()
	add_child(cz)
	cz.zoom_to(Vector2(3.0, 3.0), 0.0)
	# Não crasha — câmera não encontrada
	assert_bool(cz.is_active()).is_false()
	remove_child(cz)
	cz.queue_free()


func test_reset_restores_default() -> void:
	var camera := Camera2D.new()
	add_child(camera)
	camera.zoom = Vector2(3.0, 3.0)
	var cz := _make_cz()
	camera.add_child(cz)
	cz.default_zoom = Vector2(1.5, 1.5)
	cz.reset(0.0)
	assert_that(camera.zoom).is_equal(Vector2(1.5, 1.5))
	remove_child(camera)
	camera.queue_free()


func test_zoom_to_emits_signals_instant() -> void:
	var camera := Camera2D.new()
	add_child(camera)
	var cz := _make_cz()
	camera.add_child(cz)

	var started_v := Vector2.ZERO
	var finished_v := Vector2.ZERO
	cz.zoom_started.connect(func(t: Vector2): started_v = t)
	cz.zoom_finished.connect(func(c: Vector2): finished_v = c)

	var target := Vector2(0.5, 0.5)
	cz.zoom_to(target, 0.0)
	assert_that(started_v).is_equal(target)
	assert_that(finished_v).is_equal(target)

	remove_child(camera)
	camera.queue_free()


func test_get_current_zoom_no_camera() -> void:
	var cz := _make_cz()
	assert_that(cz.get_current_zoom()).is_equal(Vector2.ONE)
	cz.queue_free()


func test_get_current_zoom_with_camera() -> void:
	var camera := Camera2D.new()
	add_child(camera)
	camera.zoom = Vector2(2.0, 1.5)
	var cz := _make_cz()
	camera.add_child(cz)
	assert_that(cz.get_current_zoom()).is_equal(Vector2(2.0, 1.5))
	remove_child(camera)
	camera.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSIÇÃO — Com outros behaviors
# ═══════════════════════════════════════════════════════════════════════════════

func test_composes_with_screen_shake() -> void:
	var camera := Camera2D.new()
	add_child(camera)

	var shake := ScreenShake.new()
	camera.add_child(shake)

	var cz := _make_cz()
	camera.add_child(cz)

	cz.zoom_to(Vector2(2.0, 2.0), 0.0)
	assert_that(camera.zoom).is_equal(Vector2(2.0, 2.0))

	remove_child(camera)
	camera.queue_free()
