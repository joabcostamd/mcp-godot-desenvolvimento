## test_line_of_sight.gd — Testes do LineOfSight | GdUnit4.
##
## Cobre: detecção dentro/foda do ângulo, alcance, sinais,
##        oclusão, edge cases, warnings.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── Ângulo ────────────────────────────────────────────────────────────────────

func test_detects_within_angle() -> void:
	var los := _make_los(90.0, 300.0, 0, "player")
	var parent := Node2D.new()
	parent.add_child(los)
	add_child(parent)

	var player := CharacterBody2D.new()
	player.add_to_group("player")
	player.global_position = Vector2(100, 0)  # bem na frente (0°)
	add_child(player)

	los._on_body_entered(player)
	assert_int(los._targets.size()).is_equal(1)


func test_ignores_outside_angle() -> void:
	var los := _make_los(90.0, 300.0, 0, "player")
	var parent := Node2D.new()
	parent.add_child(los)
	add_child(parent)

	var player := CharacterBody2D.new()
	player.add_to_group("player")
	player.global_position = Vector2(-100, 0)  # atrás (180°)
	add_child(player)

	los._on_body_entered(player)
	assert_int(los._targets.size()).is_equal(0)


func test_ignores_outside_range() -> void:
	var los := _make_los(360.0, 100.0, 0, "player")
	var parent := Node2D.new()
	parent.add_child(los)
	add_child(parent)

	var player := CharacterBody2D.new()
	player.add_to_group("player")
	player.global_position = Vector2(200, 0)  # além do range
	add_child(player)

	los._on_body_entered(player)
	assert_int(los._targets.size()).is_equal(0)


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_target_spotted_signal() -> void:
	var los := _make_los(90.0, 300.0, 0, "player")
	var parent := Node2D.new()
	parent.add_child(los)
	add_child(parent)

	var player := CharacterBody2D.new()
	player.add_to_group("player")
	player.global_position = Vector2(50, 0)
	add_child(player)

	var spotted := false
	los.target_spotted.connect(func(_t): spotted = true)
	los._on_body_entered(player)
	assert_bool(spotted).is_true()


func test_target_lost_signal() -> void:
	var los := _make_los(90.0, 300.0, 0, "player")
	var parent := Node2D.new()
	parent.add_child(los)
	add_child(parent)

	var player := CharacterBody2D.new()
	player.add_to_group("player")
	player.global_position = Vector2(50, 0)
	add_child(player)

	los._on_body_entered(player)
	var lost := false
	los.target_lost.connect(func(_t): lost = true)
	los._on_body_exited(player)
	assert_bool(lost).is_true()


# ── Grupo ─────────────────────────────────────────────────────────────────────

func test_ignores_wrong_group() -> void:
	var los := _make_los(360.0, 300.0, 0, "player")
	var parent := Node2D.new()
	parent.add_child(los)
	add_child(parent)

	var enemy := CharacterBody2D.new()
	enemy.add_to_group("enemy")
	enemy.global_position = Vector2(50, 0)
	add_child(enemy)

	los._on_body_entered(enemy)
	assert_int(los._targets.size()).is_equal(0)


func test_empty_target_group_ignores_all() -> void:
	var los := _make_los(360.0, 300.0, 0, "")
	var parent := Node2D.new()
	parent.add_child(los)
	add_child(parent)

	var player := CharacterBody2D.new()
	player.add_to_group("player")
	player.global_position = Vector2(50, 0)
	add_child(player)

	los._on_body_entered(player)
	assert_int(los._targets.size()).is_equal(0)


# ── Não duplicar ──────────────────────────────────────────────────────────────

func test_no_duplicate_targets() -> void:
	var los := _make_los(90.0, 300.0, 0, "player")
	var parent := Node2D.new()
	parent.add_child(los)
	add_child(parent)

	var player := CharacterBody2D.new()
	player.add_to_group("player")
	player.global_position = Vector2(50, 0)
	add_child(player)

	los._on_body_entered(player)
	los._on_body_entered(player)  # segunda entrada → ignorada
	assert_int(los._targets.size()).is_equal(1)


# ── Stale targets ─────────────────────────────────────────────────────────────

func test_purges_stale_targets() -> void:
	var los := _make_los(90.0, 300.0, 0, "player")
	var parent := Node2D.new()
	parent.add_child(los)
	add_child(parent)

	# Adiciona um target que será liberado
	var player := CharacterBody2D.new()
	player.add_to_group("player")
	player.global_position = Vector2(50, 0)
	add_child(player)
	los._on_body_entered(player)
	assert_int(los._targets.size()).is_equal(1)

	# Libera o player sem chamar body_exited
	remove_child(player)
	player.free()

	# Próximo body_entered deve limpar stale refs
	var player2 := CharacterBody2D.new()
	player2.add_to_group("player")
	player2.global_position = Vector2(50, 0)
	add_child(player2)
	los._on_body_entered(player2)

	assert_int(los._targets.size()).is_equal(1)
	assert_object(los._targets[0]).is_equal(player2)


func test_is_within_angle_edge() -> void:
	var los := _make_los(90.0, 300.0, 0, "player")
	var parent := Node2D.new()
	parent.add_child(los)
	add_child(parent)

	# Player exatamente na borda do cone (45° de cada lado)
	var player := CharacterBody2D.new()
	player.add_to_group("player")
	player.global_position = Vector2(71, 71)  # ~45° (dentro do cone de 90°)
	add_child(player)

	los._on_body_entered(player)
	assert_int(los._targets.size()).is_equal(1)


# ── Warnings ──────────────────────────────────────────────────────────────────

func test_warning_collision_mask_zero() -> void:
	var los := _make_los(90.0, 300.0, 0, "player")
	los.collision_mask = 0
	add_child(los)
	var found := false
	for w in los._get_configuration_warnings():
		if "collision_mask" in w:
			found = true
	assert_bool(found).is_true()


func test_warning_empty_target_group() -> void:
	var los := _make_los(90.0, 300.0, 0, "")
	add_child(los)
	var found := false
	for w in los._get_configuration_warnings():
		if "target_group" in w:
			found = true
	assert_bool(found).is_true()


# ── CollisionShape ────────────────────────────────────────────────────────────

func test_creates_collision_shape() -> void:
	var los := _make_los(90.0, 200.0, 0, "player")
	add_child(los)

	var has_shape := false
	for child in los.get_children():
		if child is CollisionShape2D:
			has_shape = true
			var shape := (child as CollisionShape2D).shape
			if shape is CircleShape2D:
				assert_float(shape.radius).is_equal(200.0)
			break
	assert_bool(has_shape).is_true()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_los(angle: float, range_val: float, rays: int, group: String) -> LineOfSight:
	var los := LineOfSight.new()
	los.view_angle = angle
	los.view_range = range_val
	los.ray_count = rays
	los.target_group = group
	return los
