## test_trail.gd — Testes do behavior Trail | GdUnit4.
##
## Cobre: pontos, max_points, spacing, fade, clear.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


func _make_tr(max_pts := 20, spacing := 5.0) -> Trail:
	var tr := Trail.new()
	tr.max_points = max_pts
	tr.point_spacing = spacing
	return tr


# ═══════════════════════════════════════════════════════════════════════════════
# ESTÁTICO
# ═══════════════════════════════════════════════════════════════════════════════

func test_script_compiles() -> void:
	var tr := Trail.new()
	assert_object(tr).is_not_null()
	tr.queue_free()


func test_default_parameters() -> void:
	var tr := Trail.new()
	assert_int(tr.max_points).is_equal(20)
	assert_float(tr.point_spacing).is_equal(5.0)
	assert_bool(tr.fade).is_true()
	assert_float(tr.trail_width).is_equal(3.0)
	tr.queue_free()


func test_parameter_clamping() -> void:
	var tr := Trail.new()
	tr.max_points = 1
	assert_int(tr.max_points).is_equal(2)
	tr.max_points = 9999
	assert_int(tr.max_points).is_equal(200)
	tr.point_spacing = 0.5
	assert_float(tr.point_spacing).is_equal(1.0)
	tr.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# UNITÁRIO
# ═══════════════════════════════════════════════════════════════════════════════

func test_trail_follows_parent() -> void:
	var parent := Node2D.new()
	add_child(parent)
	parent.position = Vector2(100, 0)
	var tr := _make_tr(10, 1.0)
	tr.fade = false
	parent.add_child(tr)
	# Simula um frame para adicionar ponto
	await get_tree().process_frame
	assert_int(tr.points.size()).is_greater(0)
	remove_child(parent)
	parent.queue_free()


func test_trail_respects_max_points() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var tr := _make_tr(3, 1.0)
	tr.fade = false
	parent.add_child(tr)
	# Move parent várias vezes
	for x in range(0, 50, 5):
		parent.position = Vector2(x, 0)
		await get_tree().process_frame
	assert_int(tr.points.size()).is_less_equal(3)
	remove_child(parent)
	parent.queue_free()


func test_clear_removes_all_points() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var tr := _make_tr(10, 1.0)
	tr.fade = false
	parent.add_child(tr)
	parent.position = Vector2(100, 0)
	await get_tree().process_frame
	tr.clear()
	assert_int(tr.points.size()).is_equal(0)
	remove_child(parent)
	parent.queue_free()


func test_fade_enabled_creates_gradient() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var tr := _make_tr(10, 1.0)
	tr.fade = true
	parent.add_child(tr)
	for x in range(0, 50, 5):
		parent.position = Vector2(x, 0)
		await get_tree().process_frame
	var g := tr.gradient
	assert_object(g).is_not_null()
	remove_child(parent)
	parent.queue_free()


func test_no_fade_no_gradient() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var tr := _make_tr(10, 1.0)
	tr.fade = false
	parent.add_child(tr)
	parent.position = Vector2(100, 0)
	await get_tree().process_frame
	assert_object(tr.gradient).is_null()
	remove_child(parent)
	parent.queue_free()
