## test_knockback.gd — Testes do behavior Knockback | GdUnit4.
##
## Cobre: apply_knockback, cooldown, sinais, direção zero,
##        parent inválido, is_ready, reset, warnings.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── apply_knockback ──────────────────────────────────────────────────────────

func test_apply_knockback_adds_velocity() -> void:
	var kb := _make_knockback(200.0, 0.3)
	var parent := CharacterBody2D.new()
	parent.add_child(kb)
	add_child(parent)

	var result := kb.apply_knockback(Vector2.RIGHT)
	assert_bool(result).is_true()
	assert_float(parent.velocity.x).is_equal(200.0)
	assert_float(parent.velocity.y).is_equal(0.0)


func test_apply_knockback_diagonal() -> void:
	var kb := _make_knockback(100.0, 0.3)
	var parent := CharacterBody2D.new()
	parent.add_child(kb)
	add_child(parent)

	kb.apply_knockback(Vector2(1, 1))
	# Direção normalizada: (0.707, 0.707) * 100 ≈ (70.7, 70.7)
	assert_float(parent.velocity.x).is_greater(70.0)
	assert_float(parent.velocity.y).is_greater(70.0)


func test_apply_knockback_zero_direction_fails() -> void:
	var kb := _make_knockback(200.0, 0.3)
	var parent := CharacterBody2D.new()
	parent.add_child(kb)
	add_child(parent)

	var result := kb.apply_knockback(Vector2.ZERO)
	assert_bool(result).is_false()
	assert_float(parent.velocity.x).is_equal(0.0)


# ── Cooldown ─────────────────────────────────────────────────────────────────

func test_cannot_knockback_during_cooldown() -> void:
	var kb := _make_knockback(200.0, 99.0)
	var parent := CharacterBody2D.new()
	parent.add_child(kb)
	add_child(parent)

	kb.apply_knockback(Vector2.RIGHT)
	var result := kb.apply_knockback(Vector2.LEFT)
	assert_bool(result).is_false()


func test_is_ready_false_during_cooldown() -> void:
	var kb := _make_knockback(200.0, 99.0)
	var parent := CharacterBody2D.new()
	parent.add_child(kb)
	add_child(parent)

	kb.apply_knockback(Vector2.RIGHT)
	assert_bool(kb.is_ready()).is_false()


func test_cooldown_expires() -> void:
	var kb := _make_knockback(200.0, 0.01)
	var parent := CharacterBody2D.new()
	parent.add_child(kb)
	add_child(parent)

	kb.apply_knockback(Vector2.RIGHT)
	await get_tree().create_timer(0.05).timeout

	assert_bool(kb.is_ready()).is_true()
	var result := kb.apply_knockback(Vector2.LEFT)
	assert_bool(result).is_true()


# ── Sinal ────────────────────────────────────────────────────────────────────

func test_knocked_back_signal_emitted() -> void:
	var kb := _make_knockback(200.0, 0.3)
	var parent := CharacterBody2D.new()
	parent.add_child(kb)
	add_child(parent)

	var signal_fired := false
	var captured_dir := Vector2.ZERO
	kb.knocked_back.connect(func(dir):
		signal_fired = true
		captured_dir = dir
	)

	kb.apply_knockback(Vector2.UP)
	assert_bool(signal_fired).is_true()
	assert_float(captured_dir.x).is_equal(0.0)
	assert_float(captured_dir.y).is_equal(-1.0)


func test_knocked_back_emits_normalized_direction() -> void:
	var kb := _make_knockback(200.0, 0.3)
	var parent := CharacterBody2D.new()
	parent.add_child(kb)
	add_child(parent)

	var captured_dir := Vector2.ZERO
	kb.knocked_back.connect(func(dir):
		captured_dir = dir
	)

	# Direção não normalizada: (10, 0) → normalizada: (1, 0)
	kb.apply_knockback(Vector2(10, 0))
	assert_float(captured_dir.length()).is_equal(1.0)
	assert_float(captured_dir.x).is_equal(1.0)


# ── Parent inválido ──────────────────────────────────────────────────────────

func test_apply_knockback_fails_without_characterbody() -> void:
	var kb := _make_knockback(200.0, 0.3)
	var parent := Node2D.new()  # NÃO é CharacterBody2D
	parent.add_child(kb)
	add_child(parent)

	var result := kb.apply_knockback(Vector2.RIGHT)
	assert_bool(result).is_false()


# ── Reset ────────────────────────────────────────────────────────────────────

func test_reset_allows_immediate_knockback() -> void:
	var kb := _make_knockback(200.0, 99.0)
	var parent := CharacterBody2D.new()
	parent.add_child(kb)
	add_child(parent)

	kb.apply_knockback(Vector2.RIGHT)
	assert_bool(kb.is_ready()).is_false()

	kb.reset()
	assert_bool(kb.is_ready()).is_true()

	var result := kb.apply_knockback(Vector2.LEFT)
	assert_bool(result).is_true()


# ── Setters ──────────────────────────────────────────────────────────────────

func test_force_clamped() -> void:
	var kb := _make_knockback(200.0, 0.3)
	kb.force = -100.0
	assert_float(kb.force).is_equal(0.0)
	kb.force = 99999.0
	assert_float(kb.force).is_equal(5000.0)


func test_duration_clamped() -> void:
	var kb := _make_knockback(200.0, 0.3)
	kb.duration = 0.0
	assert_float(kb.duration).is_equal(0.01)
	kb.duration = 999.0
	assert_float(kb.duration).is_equal(5.0)


# ── Warnings ─────────────────────────────────────────────────────────────────

func test_warning_parent_not_characterbody() -> void:
	var kb := _make_knockback(200.0, 0.3)
	var parent := Node2D.new()
	parent.add_child(kb)
	add_child(parent)

	var warnings := kb._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "CharacterBody2D" in w:
			found = true
			break
	assert_bool(found).is_true()


func test_warning_force_zero() -> void:
	var kb := _make_knockback(0.0, 0.3)
	var parent := CharacterBody2D.new()
	parent.add_child(kb)
	add_child(parent)

	var warnings := kb._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "force" in w:
			found = true
			break
	assert_bool(found).is_true()


# ── Robustez ─────────────────────────────────────────────────────────────────

func test_reset_safe_before_ready() -> void:
	var kb := Knockback.new()
	kb.force = 200.0
	kb.reset()
	assert_bool(kb.is_ready()).is_true()


func test_apply_knockback_safe_before_ready() -> void:
	var kb := Knockback.new()
	kb.force = 200.0
	var result := kb.apply_knockback(Vector2.RIGHT)
	assert_bool(result).is_false()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_knockback(f: float, d: float) -> Knockback:
	var kb := Knockback.new()
	kb.force = f
	kb.duration = d
	return kb
