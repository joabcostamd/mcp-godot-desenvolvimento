## test_projectile.gd — Testes do behavior Projectile | GdUnit4.
##
## Cobre: movimento, dano, expiração por tempo, expiração por distância,
##        piercing, sinal hit, sinal expired, set_direction, set_target.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── Movimento ─────────────────────────────────────────────────────────────────

func test_moves_in_set_direction() -> void:
	var proj := _make_projectile()
	proj.set_direction(Vector2.RIGHT)
	add_child(proj)

	# Avança 1 frame de física
	await get_tree().physics_frame
	var moved := proj.global_position.x
	assert_float(moved).is_greater(0.0)


func test_set_target_calculates_direction() -> void:
	var proj := _make_projectile()
	var target := Node2D.new()
	target.global_position = Vector2(100, 0)
	add_child(proj)
	add_child(target)

	proj.set_target(target)
	# A direção deve apontar para a direita
	assert_float(proj._direction.x).is_greater(0.9)
	assert_float(proj._direction.y).is_equal(0.0).override_failure_message("y=0")


# ── Dano ──────────────────────────────────────────────────────────────────────

func test_deals_damage_to_health() -> void:
	var proj := _make_projectile()
	proj.damage = 30
	var target := Node2D.new()
	var health := Health.new()
	health.max_hp = 100
	health.current_hp = 100
	target.add_child(health)

	add_child(proj)
	add_child(target)

	proj._handle_hit(target)
	assert_int(health.current_hp).is_equal(70)


func test_damage_overkill_clamped() -> void:
	var proj := _make_projectile()
	proj.damage = 999
	var health := Health.new()
	health.max_hp = 50
	health.current_hp = 50

	var damage_dealt := 0
	proj.hit.connect(func(_t, d): damage_dealt = d)

	proj._handle_hit(health)
	assert_int(damage_dealt).is_equal(50)
	assert_int(health.current_hp).is_equal(0)


# ── Sinal hit ─────────────────────────────────────────────────────────────────

func test_hit_signal_emitted() -> void:
	var proj := _make_projectile()
	var target := Node2D.new()
	var hit_received := false
	proj.hit.connect(func(_t, _d): hit_received = true)

	add_child(proj)
	proj._handle_hit(target)
	assert_bool(hit_received).is_true()


func test_hit_signal_params() -> void:
	var proj := _make_projectile()
	proj.damage = 25
	var health := Health.new()
	health.max_hp = 100
	health.current_hp = 100

	var captured_damage := 0
	proj.hit.connect(func(_t, d): captured_damage = d)

	proj._handle_hit(health)
	assert_int(captured_damage).is_equal(25)


# ── Piercing ──────────────────────────────────────────────────────────────────

func test_piercing_does_not_destroy() -> void:
	var proj := _make_projectile()
	proj.piercing = true
	add_child(proj)

	var target1 := Node2D.new()
	var target2 := Node2D.new()
	add_child(target1)
	add_child(target2)

	proj._handle_hit(target1)
	assert_bool(is_instance_valid(proj)).is_true().override_failure_message("piercing: projétil não deve ser destruído")

	proj._handle_hit(target2)
	assert_bool(is_instance_valid(proj)).is_true()


func test_non_piercing_destroys_on_hit() -> void:
	var proj := _make_projectile()
	proj.piercing = false
	add_child(proj)

	proj._handle_hit(Node2D.new())
	# Nota: queue_free() é deferred; o nó pode ainda ser válido neste frame
	await get_tree().physics_frame
	assert_bool(not is_instance_valid(proj)).is_true().override_failure_message("sem piercing: projétil deve ser destruído")


# ── Expiração ─────────────────────────────────────────────────────────────────

func test_expires_by_lifetime() -> void:
	var proj := _make_projectile()
	proj.lifetime = 0.1
	proj.max_distance = 0  # desabilita distância
	var expired_signal := false
	proj.expired.connect(func(): expired_signal = true)
	add_child(proj)

	await get_tree().create_timer(0.2).timeout
	assert_bool(expired_signal).is_true()


func test_expires_by_distance() -> void:
	var proj := _make_projectile()
	proj.max_distance = 50.0
	proj.lifetime = 0  # desabilita tempo
	proj.speed = 500.0
	proj.set_direction(Vector2.RIGHT)
	var expired_signal := false
	proj.expired.connect(func(): expired_signal = true)
	add_child(proj)

	# Espera distância suficiente
	await get_tree().create_timer(0.3).timeout
	assert_bool(expired_signal).is_true()


# ── Edge cases ────────────────────────────────────────────────────────────────

func test_zero_damage_does_nothing() -> void:
	var proj := _make_projectile()
	proj.damage = 0
	var health := Health.new()
	health.max_hp = 100
	health.current_hp = 100

	proj._handle_hit(health)
	assert_int(health.current_hp).is_equal(100)


func test_target_without_health() -> void:
	var proj := _make_projectile()
	var target := Node2D.new()
	var damage_dealt := -1
	proj.hit.connect(func(_t, d): damage_dealt = d)

	proj._handle_hit(target)
	assert_int(damage_dealt).is_equal(0)


func test_set_direction_normalizes() -> void:
	var proj := _make_projectile()
	proj.set_direction(Vector2(3, 4))
	assert_float(proj._direction.length()).is_equal(1.0)


# ── Helper ────────────────────────────────────────────────────────────────────

func _make_projectile() -> Projectile:
	var proj := Projectile.new()
	proj.speed = 400.0
	proj.damage = 10
	proj.lifetime = 5.0
	proj.max_distance = 1000.0
	proj.piercing = false
	return proj
