## test_trigger_zone.gd — Testes do TriggerZone | GdUnit4.

extends GdUnitTestSuite

func _make_tz() -> TriggerZone: return TriggerZone.new()

func test_defaults() -> void:
	var tz := _make_tz()
	assert_str(tz.trigger_group).is_equal("")
	assert_bool(tz.trigger_once).is_false()
	assert_that(tz.shape_size).is_equal(Vector2(64,64))
	tz.queue_free()

func test_creates_collision_shape() -> void:
	var tz := _make_tz(); add_child(tz)
	var found := false
	for c in tz.get_children():
		if c is CollisionShape2D: found = true
	assert_bool(found).is_true()
	remove_child(tz); tz.queue_free()

func test_no_duplicate_shape() -> void:
	var tz := _make_tz(); add_child(tz)
	tz._setup_shape()  # segunda chamada = no-op
	var count := 0
	for c in tz.get_children():
		if c is CollisionShape2D: count += 1
	assert_int(count).is_equal(1)
	remove_child(tz); tz.queue_free()

func test_valid_body_no_group() -> void:
	var tz := _make_tz(); tz.trigger_group = ""
	var body := Node2D.new()
	assert_bool(tz._is_valid(body)).is_true()
	body.queue_free(); tz.queue_free()

func test_valid_body_wrong_group() -> void:
	var tz := _make_tz(); tz.trigger_group = "players"
	var body := Node2D.new()
	assert_bool(tz._is_valid(body)).is_false()
	body.queue_free(); tz.queue_free()

func test_valid_body_correct_group() -> void:
	var tz := _make_tz(); tz.trigger_group = "players"
	var body := Node2D.new(); body.add_to_group("players")
	assert_bool(tz._is_valid(body)).is_true()
	body.queue_free(); tz.queue_free()

func test_trigger_once_disables() -> void:
	var tz := _make_tz(); tz.trigger_once = true; add_child(tz)
	var body := Node2D.new(); add_child(body)
	tz._on_body_entered(body)
	assert_bool(tz._triggered).is_true()
	# Segundo corpo não deve emitir
	var emitted := false
	tz.zone_entered.connect(func(_b): emitted = true)
	tz._on_body_entered(body)
	assert_bool(emitted).is_false()
	remove_child(body); remove_child(tz)
	body.queue_free(); tz.queue_free()

func test_reset_trigger() -> void:
	var tz := _make_tz(); tz.trigger_once = true; add_child(tz)
	var body := Node2D.new(); add_child(body)
	tz._on_body_entered(body)
	assert_bool(tz._triggered).is_true()
	tz.reset_trigger()
	assert_bool(tz._triggered).is_false()
	remove_child(body); remove_child(tz)
	body.queue_free(); tz.queue_free()

func test_zone_entered_signal() -> void:
	var tz := _make_tz(); add_child(tz)
	var body := Node2D.new()
	var emitted := false
	tz.zone_entered.connect(func(_b): emitted = true)
	tz._on_body_entered(body)
	assert_bool(emitted).is_true()
	body.queue_free(); remove_child(tz); tz.queue_free()

func test_zone_exited_signal() -> void:
	var tz := _make_tz(); add_child(tz)
	var body := Node2D.new()
	var emitted := false
	tz.zone_exited.connect(func(_b): emitted = true)
	tz._on_body_exited(body)
	assert_bool(emitted).is_true()
	body.queue_free(); remove_child(tz); tz.queue_free()

func test_shape_size_clamped() -> void:
	var tz := _make_tz()
	tz.shape_size = Vector2(1,1)
	assert_float(tz.shape_size.x).is_equal(8.0)
	tz.queue_free()
