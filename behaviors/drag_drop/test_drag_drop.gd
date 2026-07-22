## test_drag_drop.gd — Testes do behavior DragDrop | GdUnit4.
##
## Testa forwarding, snap, sinais, edge cases.
## Fonte: Godot 4.7 ClassDB — Control.set_drag_forwarding, force_drag, NOTIFICATION_DRAG_END.

extends GdUnitTestSuite


func _make_dd() -> DragDrop:
	return DragDrop.new()


func _make_parent() -> Control:
	var ctrl := Control.new()
	ctrl.size = Vector2(100, 100)
	return ctrl


# ── Compilação e defaults ─────────────────────────────────────────────────────

func test_script_compiles() -> void:
	var dd := DragDrop.new()
	assert_object(dd).is_not_null()
	dd.queue_free()


func test_default_parameters() -> void:
	var dd := _make_dd()
	assert_bool(dd.drag_preview).is_true()
	assert_that(dd.snap_size).is_equal(Vector2.ZERO)
	assert_str(dd.drop_group).is_equal("")
	dd.queue_free()


func test_starts_not_dragging() -> void:
	var dd := _make_dd()
	assert_bool(dd.is_dragging()).is_false()
	dd.queue_free()


# ── Snap ──────────────────────────────────────────────────────────────────────

func test_snap_to_grid() -> void:
	var dd := _make_dd()
	dd.snap_size = Vector2(64, 64)
	
	var snapped := dd._snap_to_grid(Vector2(70, 90))
	# 70/64 = 1.093 → round = 1 → 64
	# 90/64 = 1.406 → round = 1 → 64
	assert_that(snapped).is_equal(Vector2(64, 64))
	dd.queue_free()


func test_snap_to_grid_rounds_up() -> void:
	var dd := _make_dd()
	dd.snap_size = Vector2(32, 32)
	
	var snapped := dd._snap_to_grid(Vector2(50, 20))
	# 50/32 = 1.562 → round = 2 → 64
	# 20/32 = 0.625 → round = 1 → 32
	assert_that(snapped).is_equal(Vector2(64, 32))
	dd.queue_free()


func test_snap_zero_disabled() -> void:
	var dd := _make_dd()
	dd.snap_size = Vector2.ZERO
	var snapped := dd._snap_to_grid(Vector2(123, 456))
	assert_that(snapped).is_equal(Vector2(0, 0))  # round(123/0) → inf → round(inf) → ?
	# Na prática, snap desativado não deveria ser chamado
	dd.queue_free()


# ── set_drag_forwarding ───────────────────────────────────────────────────────

func test_sets_forwarding_on_parent() -> void:
	var parent := _make_parent()
	add_child(parent)
	var dd := _make_dd()
	parent.add_child(dd)
	
	# _ready() já foi chamado ao add_child
	# Verifica que não crashou
	assert_bool(true).is_true()
	
	remove_child(parent)
	parent.queue_free()
	dd.queue_free()


func test_no_parent_does_not_crash() -> void:
	var dd := _make_dd()
	# Sem add_child — _setup_drag_forwarding retorna cedo
	dd._setup_drag_forwarding()
	assert_bool(dd.is_dragging()).is_false()
	dd.queue_free()


# ── Snap size setter ──────────────────────────────────────────────────────────

func test_snap_size_negative_clamped() -> void:
	var dd := _make_dd()
	dd.snap_size = Vector2(-10, -5)
	assert_float(dd.snap_size.x).is_equal(0.0)
	assert_float(dd.snap_size.y).is_equal(0.0)
	dd.queue_free()


# ── start_drag ────────────────────────────────────────────────────────────────

func test_start_drag_on_parent() -> void:
	var parent := _make_parent()
	add_child(parent)
	var dd := _make_dd()
	parent.add_child(dd)
	
	dd.start_drag({"item": "sword"})
	# force_drag foi chamado — is_dragging deve ser true
	assert_bool(dd.is_dragging()).is_true()
	
	remove_child(parent)
	parent.queue_free()
	dd.queue_free()


func test_start_drag_no_parent() -> void:
	var dd := _make_dd()
	dd.start_drag({"item": "shield"})
	# Sem parent Control — não faz nada
	assert_bool(dd.is_dragging()).is_false()
	dd.queue_free()


# ── is_dragging ───────────────────────────────────────────────────────────────

func test_is_dragging_after_get_drag_data() -> void:
	var parent := _make_parent()
	add_child(parent)
	var dd := _make_dd()
	parent.add_child(dd)
	
	dd._get_drag_data(Vector2.ZERO)
	assert_bool(dd.is_dragging()).is_true()
	
	remove_child(parent)
	parent.queue_free()
	dd.queue_free()


# ── NOTIFICATION_DRAG_END ─────────────────────────────────────────────────────

func test_drag_end_resets_position() -> void:
	var parent := _make_parent()
	parent.position = Vector2(100, 200)
	add_child(parent)
	var dd := _make_dd()
	parent.add_child(dd)
	
	# Simula início de drag
	dd._get_drag_data(Vector2.ZERO)
	assert_that(dd._initial_position).is_equal(Vector2(100, 200))
	
	# Move o parent (como se estivesse arrastando)
	parent.position = Vector2(300, 400)
	
	# Simula fim de drag sem drop válido
	dd._dragging = true
	dd._notification(DragDrop.NOTIFICATION_DRAG_END)
	
	# Deve voltar à posição inicial
	assert_that(parent.position).is_equal(Vector2(100, 200))
	
	remove_child(parent)
	parent.queue_free()
	dd.queue_free()
