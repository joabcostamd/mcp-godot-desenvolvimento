## test_health.gd — Testes do behavior Health | GdUnit4.
##
## Cobre: dano, morte, cura, invulnerabilidade, sinais, full_heal, hp_percent.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests na cena behaviors/health/test_health.gd

extends GdUnitTestSuite


# ── Dano básico ───────────────────────────────────────────────────────────────

func test_take_damage_reduces_hp() -> void:
	var health := _make_health(100)
	var result := health.take_damage(30)
	assert_int(result).is_equal(30)
	assert_int(health.current_hp).is_equal(70)


func test_take_damage_zero_does_nothing() -> void:
	var health := _make_health(100)
	var result := health.take_damage(0)
	assert_int(result).is_equal(0)
	assert_int(health.current_hp).is_equal(100)


func test_take_damage_negative_does_nothing() -> void:
	var health := _make_health(100)
	var result := health.take_damage(-10)
	assert_int(result).is_equal(0)
	assert_int(health.current_hp).is_equal(100)


# ── Morte ─────────────────────────────────────────────────────────────────────

func test_damage_exact_kill() -> void:
	var health := _make_health(50)
	var died := false
	health.died.connect(func(): died = true)
	health.take_damage(50)
	assert_bool(died).is_true()
	assert_int(health.current_hp).is_equal(0)
	assert_bool(health.is_alive()).is_false()


func test_damage_overkill() -> void:
	var health := _make_health(50)
	var effective := health.take_damage(999)
	assert_int(effective).is_equal(50)  # Só 50 de dano efetivo (restante ignorado)
	assert_int(health.current_hp).is_equal(0)
	assert_bool(health.is_alive()).is_false()


func test_died_signal_only_once() -> void:
	var health := _make_health(10)
	var died_count := 0
	health.died.connect(func(): died_count += 1)
	health.take_damage(10)
	assert_int(died_count).is_equal(1)
	# Segundo dano em entidade já morta não reemite died
	health.take_damage(10)
	assert_int(died_count).is_equal(1)


# ── Cura ──────────────────────────────────────────────────────────────────────

func test_heal_restores_hp() -> void:
	var health := _make_health(100)
	health.take_damage(40)
	var healed_amount := health.heal(20)
	assert_int(healed_amount).is_equal(20)
	assert_int(health.current_hp).is_equal(80)


func test_heal_cannot_exceed_max() -> void:
	var health := _make_health(100)
	health.take_damage(10)
	var healed_amount := health.heal(999)
	assert_int(healed_amount).is_equal(10)
	assert_int(health.current_hp).is_equal(100)


func test_full_heal() -> void:
	var health := _make_health(100)
	health.take_damage(70)
	health.full_heal()
	assert_int(health.current_hp).is_equal(100)


func test_heal_dead_entity() -> void:
	var health := _make_health(50)
	health.take_damage(50)  # morto
	var healed_amount := health.heal(20)
	assert_int(healed_amount).is_equal(20)
	assert_int(health.current_hp).is_equal(20)
	assert_bool(health.is_alive()).is_true()


# ── Invulnerabilidade ─────────────────────────────────────────────────────────

func test_invulnerability_blocks_damage() -> void:
	var health := _make_health(100)
	add_child(health)  # Precisa estar na arvore para get_tree().create_timer()
	health.invulnerable_time = 999.0  # invulnerabilidade longa
	health.take_damage(30)
	var second := health.take_damage(20)
	assert_int(second).is_equal(0)
	assert_int(health.current_hp).is_equal(70)
	remove_child(health)
	health.queue_free()


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_damage_taken_signal_params() -> void:
	var health := _make_health(100)
	var received_amount := 0
	var received_remaining := 0
	health.damage_taken.connect(func(amount, remaining):
		received_amount = amount
		received_remaining = remaining
	)
	health.take_damage(25)
	assert_int(received_amount).is_equal(25)
	assert_int(received_remaining).is_equal(75)


func test_healed_signal_params() -> void:
	var health := _make_health(100)
	health.take_damage(30)
	var received_amount := 0
	var received_current := 0
	health.healed.connect(func(amount, current):
		received_amount = amount
		received_current = current
	)
	health.heal(15)
	assert_int(received_amount).is_equal(15)
	assert_int(received_current).is_equal(85)


func test_hp_changed_signal() -> void:
	var health := _make_health(100)
	var changes: Array[Dictionary] = []
	health.hp_changed.connect(func(old, new):
		changes.append({"old": old, "new": new})
	)
	health.take_damage(20)
	health.heal(5)
	assert_int(changes.size()).is_equal(2)
	assert_int(changes[0].old).is_equal(100)
	assert_int(changes[0].new).is_equal(80)
	assert_int(changes[1].old).is_equal(80)
	assert_int(changes[1].new).is_equal(85)


# ── Utilidades ────────────────────────────────────────────────────────────────

func test_hp_percent() -> void:
	var health := _make_health(200)
	assert_float(health.hp_percent()).is_equal(1.0)
	health.take_damage(50)
	assert_float(health.hp_percent()).is_equal(0.75)
	health.take_damage(150)
	assert_float(health.hp_percent()).is_equal(0.0)


func test_max_hp_setter_clamps() -> void:
	var health := _make_health(100)
	health.max_hp = 50
	assert_int(health.max_hp).is_equal(50)
	assert_int(health.current_hp).is_equal(50)  # current_hp reduzido


func test_max_hp_cannot_be_zero() -> void:
	var health := _make_health(100)
	health.max_hp = 0
	assert_int(health.max_hp).is_equal(1)


# ── Helper ────────────────────────────────────────────────────────────────────

func _make_health(hp: int) -> Health:
	var health := Health.new()
	health.max_hp = hp
	health.current_hp = hp
	return health
