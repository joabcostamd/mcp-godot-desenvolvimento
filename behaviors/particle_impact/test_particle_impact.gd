## test_particle_impact.gd — Testes do behavior ParticleImpact | GdUnit4.
##
## Cobre: emit com e sem particle_scene, auto_free, spread, cor, sinais.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests

extends GdUnitTestSuite


# ── Helpers ───────────────────────────────────────────────────────────────────

func _make_pi(count := 10, spd := 30.0, auto := true) -> ParticleImpact:
	var pi := ParticleImpact.new()
	pi.default_count = count
	pi.spread = spd
	pi.auto_free = auto
	return pi


# ═══════════════════════════════════════════════════════════════════════════════
# ESTÁTICO — Compilação e defaults
# ═══════════════════════════════════════════════════════════════════════════════

func test_script_compiles() -> void:
	var pi := ParticleImpact.new()
	assert_object(pi).is_not_null()
	pi.queue_free()


func test_default_parameters() -> void:
	var pi := ParticleImpact.new()
	assert_int(pi.default_count).is_equal(10)
	assert_float(pi.spread).is_equal(30.0)
	assert_bool(pi.auto_free).is_true()
	assert_object(pi.particle_scene).is_null()
	pi.queue_free()


func test_parameter_clamping() -> void:
	var pi := ParticleImpact.new()
	pi.default_count = 999
	assert_int(pi.default_count).is_equal(100)
	pi.default_count = 0
	assert_int(pi.default_count).is_equal(1)
	pi.spread = 9999.0
	assert_float(pi.spread).is_equal(500.0)
	pi.spread = -5.0
	assert_float(pi.spread).is_equal(0.0)
	pi.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# UNITÁRIO — emit() sem scene
# ═══════════════════════════════════════════════════════════════════════════════

func test_emit_without_scene_creates_default() -> void:
	var pi := _make_pi(3, 0.0, false)  # spread=0, sem auto_free
	add_child(pi)
	var spawned := pi.emit(Vector2.ZERO, Color.WHITE)
	assert_int(spawned.size()).is_equal(3)
	for p in spawned:
		assert_bool(p is GPUParticles2D).is_true()
	remove_child(pi)
	pi.queue_free()


func test_emit_respects_default_count() -> void:
	var pi := _make_pi(5, 0.0, false)
	add_child(pi)
	var spawned := pi.emit(Vector2.ZERO)
	assert_int(spawned.size()).is_equal(5)
	remove_child(pi)
	pi.queue_free()


func test_emit_count_override() -> void:
	var pi := _make_pi(10, 0.0, false)
	add_child(pi)
	var spawned := pi.emit(Vector2.ZERO, Color.WHITE, 3)
	assert_int(spawned.size()).is_equal(3)
	remove_child(pi)
	pi.queue_free()


func test_emit_signals_particles_emitted() -> void:
	var pi := _make_pi(2, 0.0, false)
	add_child(pi)
	var emitted_count := 0
	pi.particles_emitted.connect(func(c: int): emitted_count = c)
	pi.emit(Vector2.ZERO)
	assert_int(emitted_count).is_equal(2)
	remove_child(pi)
	pi.queue_free()


func test_emit_with_spread_positions_vary() -> void:
	var pi := _make_pi(20, 50.0, false)
	add_child(pi)
	var spawned := pi.emit(Vector2.ZERO)
	# Pelo menos uma partícula deve ter posição diferente da origem
	var all_same := true
	for p in spawned:
		if p.position != Vector2.ZERO:
			all_same = false
			break
	assert_bool(all_same).is_false()
	remove_child(pi)
	pi.queue_free()


func test_emit_applies_color() -> void:
	var pi := _make_pi(1, 0.0, false)
	add_child(pi)
	var spawned := pi.emit(Vector2.ZERO, Color.RED)
	assert_int(spawned.size()).is_equal(1)
	assert_that(spawned[0].modulate).is_equal(Color.RED)
	remove_child(pi)
	pi.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# CENA — Comportamento em árvore
# ═══════════════════════════════════════════════════════════════════════════════

func test_auto_free_cleans_up() -> void:
	var pi := _make_pi(1, 0.0, true)
	add_child(pi)
	var spawned := pi.emit(Vector2.ZERO)
	assert_int(spawned.size()).is_equal(1)
	var p := spawned[0]
	# Força o sinal finished (simula o fim da partícula)
	if p is GPUParticles2D:
		(p as GPUParticles2D).finished.emit()
	await get_tree().process_frame
	assert_bool(is_instance_valid(p)).is_false()
	remove_child(pi)
	pi.queue_free()


func test_emit_adds_children_to_tree() -> void:
	var pi := _make_pi(3, 0.0, false)
	add_child(pi)
	var before := pi.get_child_count()
	pi.emit(Vector2.ZERO)
	var after := pi.get_child_count()
	assert_int(after).is_greater(before)
	remove_child(pi)
	pi.queue_free()


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSIÇÃO — Com outros behaviors
# ═══════════════════════════════════════════════════════════════════════════════

func test_composes_with_health() -> void:
	var parent := Node2D.new()
	add_child(parent)

	var health := Health.new()
	health.max_hp = 100
	parent.add_child(health)

	var pi := _make_pi(2, 0.0, false)
	parent.add_child(pi)

	var spawned := pi.emit(Vector2.ZERO)
	assert_int(spawned.size()).is_equal(2)

	remove_child(parent)
	parent.queue_free()


func test_composes_with_screen_shake() -> void:
	var parent := Node2D.new()
	add_child(parent)

	var shake := ScreenShake.new()
	parent.add_child(shake)

	var pi := _make_pi(3, 0.0, false)
	parent.add_child(pi)

	var spawned := pi.emit(Vector2.ZERO)
	assert_int(spawned.size()).is_equal(3)

	remove_child(parent)
	parent.queue_free()


func test_multiple_emits_independent() -> void:
	var pi := _make_pi(2, 0.0, false)
	add_child(pi)

	var s1 := pi.emit(Vector2(0, 0), Color.RED)
	var s2 := pi.emit(Vector2(100, 0), Color.BLUE)

	assert_int(s1.size()).is_equal(2)
	assert_int(s2.size()).is_equal(2)
	assert_that(s1[0].modulate).is_equal(Color.RED)
	assert_that(s2[0].modulate).is_equal(Color.BLUE)

	remove_child(pi)
	pi.queue_free()


func test_emit_returns_empty_when_count_zero() -> void:
	var pi := _make_pi(10, 0.0, false)
	add_child(pi)
	var spawned := pi.emit(Vector2.ZERO, Color.WHITE, 0)
	assert_int(spawned.size()).is_equal(10)  # usa default_count
	remove_child(pi)
	pi.queue_free()
