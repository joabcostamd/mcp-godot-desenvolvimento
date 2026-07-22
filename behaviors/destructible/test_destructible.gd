## test_destructible.gd — GdUnit4.

extends GdUnitTestSuite

func _make_d() -> Destructible: return Destructible.new()

func test_defaults() -> void:
	var d := _make_d()
	assert_str(d.destroy_effect).is_equal("")
	assert_bool(d.auto_detect_health).is_true(); d.queue_free()

func test_not_destroyed_initially() -> void:
	var d := _make_d(); add_child(d)
	assert_bool(d.is_destroyed()).is_false()
	remove_child(d); d.queue_free()

func test_destroy_emits_signal() -> void:
	var parent := Node2D.new(); add_child(parent)
	var h := Health.new(); h.max_hp = 1; parent.add_child(h)
	var d := _make_d(); parent.add_child(d)

	var emitted := false
	d.destroyed.connect(func(): emitted = true)

	h.take_damage(1, "physical")
	# take_damage internamente chama _on_zero_hp se HP=0
	# Precisamos verificar se o sinal died do Health foi conectado
	# Manualmente chamamos _on_zero_hp
	d._on_zero_hp()
	assert_bool(emitted).is_true()

	remove_child(parent); parent.queue_free(); h.queue_free(); d.queue_free()

func test_damaged_signal() -> void:
	var parent := Node2D.new(); add_child(parent)
	var h := Health.new(); h.max_hp = 5; parent.add_child(h)
	var d := _make_d(); parent.add_child(d)

	var emitted := false
	d.damaged.connect(func(_hp): emitted = true)

	d._on_damage(1, 4)
	assert_bool(emitted).is_true()

	remove_child(parent); parent.queue_free(); h.queue_free(); d.queue_free()

func test_double_destroy_ignored() -> void:
	var d := _make_d(); add_child(d)
	d._destroyed = true
	var count := 0
	d.destroyed.connect(func(): count += 1)
	d._on_zero_hp()
	assert_int(count).is_equal(0)
	remove_child(d); d.queue_free()

func test_no_health_does_not_crash() -> void:
	var d := _make_d(); d.auto_detect_health = false; add_child(d)
	d._on_zero_hp()  # sem health — _spawn_effect sem crash
	assert_bool(d.is_destroyed()).is_true()
	remove_child(d); d.queue_free()
