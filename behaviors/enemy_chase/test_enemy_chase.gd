## test_enemy_chase.gd — Testes do behavior EnemyChase | GdUnit4.
##
## Cobre: perseguição, chase_range, lose_range, sinais,
##        set_target, is_chasing, stop, warnings.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── Perseguição ──────────────────────────────────────────────────────────────

func test_chases_when_player_in_range() -> void:
	var ec := _make_enemy_chase(150.0, 300.0, 500.0)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2.ZERO
	parent.add_child(ec)
	add_child(parent)

	var player := Node2D.new()
	player.global_position = Vector2(200, 0)  # Dentro do chase_range (200 < 300)
	player.add_to_group("player")
	add_child(player)

	ec._physics_process(0.0)

	assert_bool(ec.is_chasing()).is_true()
	assert_float(parent.velocity.x).is_greater(0.0)
	assert_float(parent.velocity.y).is_equal(0.0)


func test_does_not_chase_when_player_out_of_range() -> void:
	var ec := _make_enemy_chase(150.0, 300.0, 500.0)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2.ZERO
	parent.add_child(ec)
	add_child(parent)

	var player := Node2D.new()
	player.global_position = Vector2(400, 0)  # Fora do chase_range (400 > 300)
	player.add_to_group("player")
	add_child(player)

	ec._physics_process(0.0)

	assert_bool(ec.is_chasing()).is_false()
	assert_float(parent.velocity.x).is_equal(0.0)


# ── Lose range ───────────────────────────────────────────────────────────────

func test_stops_chasing_when_player_exceeds_lose_range() -> void:
	var ec := _make_enemy_chase(150.0, 200.0, 400.0)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2.ZERO
	parent.add_child(ec)
	add_child(parent)

	var player := Node2D.new()
	player.global_position = Vector2(100, 0)  # Dentro do chase_range
	player.add_to_group("player")
	add_child(player)

	# Entra em perseguição
	ec._physics_process(0.0)
	assert_bool(ec.is_chasing()).is_true()

	# Move player para fora do lose_range
	player.global_position = Vector2(500, 0)
	ec._physics_process(0.0)

	assert_bool(ec.is_chasing()).is_false()
	assert_float(parent.velocity.x).is_equal(0.0)


# ── Sinais ───────────────────────────────────────────────────────────────────

func test_target_acquired_signal() -> void:
	var ec := _make_enemy_chase(150.0, 300.0, 500.0)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2.ZERO
	parent.add_child(ec)
	add_child(parent)

	var player := Node2D.new()
	player.global_position = Vector2(100, 0)
	player.add_to_group("player")
	add_child(player)

	var signal_fired := false
	ec.target_acquired.connect(func(): signal_fired = true)

	ec._physics_process(0.0)
	assert_bool(signal_fired).is_true()


func test_target_lost_signal() -> void:
	var ec := _make_enemy_chase(150.0, 100.0, 200.0)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2.ZERO
	parent.add_child(ec)
	add_child(parent)

	var player := Node2D.new()
	player.global_position = Vector2(50, 0)
	player.add_to_group("player")
	add_child(player)

	# Entra em perseguição
	ec._physics_process(0.0)

	var signal_fired := false
	ec.target_lost.connect(func(): signal_fired = true)

	# Move player para fora
	player.global_position = Vector2(300, 0)
	ec._physics_process(0.0)

	assert_bool(signal_fired).is_true()


# ── set_target ───────────────────────────────────────────────────────────────

func test_set_target_overrides_group() -> void:
	var ec := _make_enemy_chase(150.0, 300.0, 500.0)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2.ZERO
	parent.add_child(ec)
	add_child(parent)

	var custom_target := Node2D.new()
	custom_target.global_position = Vector2(100, 0)
	add_child(custom_target)

	ec.set_target(custom_target)
	ec._physics_process(0.0)

	assert_bool(ec.is_chasing()).is_true()


# ── stop ─────────────────────────────────────────────────────────────────────

func test_stop_ends_chase() -> void:
	var ec := _make_enemy_chase(150.0, 300.0, 500.0)
	var parent := CharacterBody2D.new()
	parent.add_child(ec)
	add_child(parent)

	var player := Node2D.new()
	player.global_position = Vector2(100, 0)
	player.add_to_group("player")
	add_child(player)

	ec._physics_process(0.0)
	assert_bool(ec.is_chasing()).is_true()

	ec.stop()
	assert_bool(ec.is_chasing()).is_false()
	assert_float(parent.velocity.x).is_equal(0.0)


func test_stop_prevents_reacquisition() -> void:
	var ec := _make_enemy_chase(150.0, 300.0, 500.0)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2.ZERO
	parent.add_child(ec)
	add_child(parent)

	var player := Node2D.new()
	player.global_position = Vector2(100, 0)
	player.add_to_group("player")
	add_child(player)

	ec._physics_process(0.0)
	assert_bool(ec.is_chasing()).is_true()

	ec.stop()
	# Mesmo com player dentro do range, não deve re-adquirir
	ec._physics_process(0.0)
	assert_bool(ec.is_chasing()).is_false()


func test_resume_allows_reacquisition() -> void:
	var ec := _make_enemy_chase(150.0, 300.0, 500.0)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2.ZERO
	parent.add_child(ec)
	add_child(parent)

	var player := Node2D.new()
	player.global_position = Vector2(100, 0)
	player.add_to_group("player")
	add_child(player)

	ec._physics_process(0.0)
	ec.stop()
	ec.resume()
	ec._physics_process(0.0)

	assert_bool(ec.is_chasing()).is_true()


# ── Player inválido (P8) ────────────────────────────────────────────────────

func test_recovers_when_player_freed() -> void:
	var ec := _make_enemy_chase(150.0, 300.0, 500.0)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2.ZERO
	parent.add_child(ec)
	add_child(parent)

	var player := Node2D.new()
	player.global_position = Vector2(100, 0)
	player.add_to_group("player")
	add_child(player)

	ec._physics_process(0.0)
	assert_bool(ec.is_chasing()).is_true()

	# Remove o player
	remove_child(player)
	player.free()

	ec._physics_process(0.0)
	assert_bool(ec.is_chasing()).is_false()


# ── Setters ──────────────────────────────────────────────────────────────────

func test_speed_clamped() -> void:
	var ec := _make_enemy_chase(150.0, 300.0, 500.0)
	ec.speed = 0.0
	assert_float(ec.speed).is_equal(10.0)


# ── Warnings ─────────────────────────────────────────────────────────────────

func test_warning_lose_less_than_chase() -> void:
	var ec := _make_enemy_chase(150.0, 500.0, 200.0)  # lose < chase
	var warnings := ec._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "lose_range" in w:
			found = true
			break
	assert_bool(found).is_true()


func test_warning_parent_not_characterbody() -> void:
	var ec := _make_enemy_chase(150.0, 300.0, 500.0)
	var parent := Node2D.new()
	parent.add_child(ec)
	add_child(parent)

	var warnings := ec._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "CharacterBody2D" in w:
			found = true
			break
	assert_bool(found).is_true()


# ── Robustez ─────────────────────────────────────────────────────────────────

func test_physics_process_safe_before_ready() -> void:
	var ec := EnemyChase.new()
	ec.speed = 150.0
	# Não deve crashar
	ec._physics_process(0.0)
	assert_bool(ec.is_chasing()).is_false()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_enemy_chase(spd: float, chase: float, lose: float) -> EnemyChase:
	var ec := EnemyChase.new()
	ec.speed = spd
	ec.chase_range = chase
	ec.lose_range = lose
	return ec
