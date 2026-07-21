## test_hitbox.gd — Testes do behavior Hitbox | GdUnit4.
##
## Cobre: dano, ativação/desativação, sinal hit_dealt, hit_type,
##        knockback_force, multi-hit prevention, _find_health recursivo.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests na cena behaviors/hitbox/test_hitbox.gd

extends GdUnitTestSuite


# ── Dano básico ───────────────────────────────────────────────────────────────

func test_active_hitbox_deals_damage() -> void:
	var hitbox := _make_hitbox(30)
	var health := _make_health(100)
	var target := Node2D.new()
	target.add_child(health)

	add_child(hitbox)
	add_child(target)

	hitbox.active = true
	hitbox._handle_hit(target)

	assert_int(health.current_hp).is_equal(70)


func test_inactive_hitbox_does_not_deal_damage() -> void:
	var hitbox := _make_hitbox(30)
	var health := _make_health(100)
	var target := Node2D.new()
	target.add_child(health)

	add_child(hitbox)
	add_child(target)

	hitbox.active = false
	hitbox._handle_hit(target)

	assert_int(health.current_hp).is_equal(100)


func test_damage_zero_does_nothing() -> void:
	var hitbox := _make_hitbox(0)
	var health := _make_health(100)
	var target := Node2D.new()
	target.add_child(health)

	add_child(hitbox)
	add_child(target)

	hitbox.active = true
	hitbox._handle_hit(target)

	assert_int(health.current_hp).is_equal(100)


# ── Sinal hit_dealt ───────────────────────────────────────────────────────────

func test_hit_dealt_signal_emitted() -> void:
	var hitbox := _make_hitbox(25)
	var health := _make_health(100)
	var target := Node2D.new()
	target.add_child(health)

	add_child(hitbox)
	add_child(target)

	var signal_fired := false
	var captured_damage := 0
	hitbox.hit_dealt.connect(func(_t, d):
		signal_fired = true
		captured_damage = d
	)

	hitbox.active = true
	hitbox._handle_hit(target)

	assert_bool(signal_fired).is_true()
	assert_int(captured_damage).is_equal(25)


# ── Ativação / Desativação ───────────────────────────────────────────────────

func test_set_active_enables_hitbox() -> void:
	var hitbox := _make_hitbox(10)
	add_child(hitbox)

	hitbox.set_active(true)
	assert_bool(hitbox.active).is_true()
	assert_bool(hitbox.monitoring).is_true()


func test_set_active_false_disables_hitbox() -> void:
	var hitbox := _make_hitbox(10)
	add_child(hitbox)

	hitbox.set_active(true)
	hitbox.set_active(false)
	assert_bool(hitbox.active).is_false()
	assert_bool(hitbox.monitoring).is_false()


func test_activated_signal_emitted() -> void:
	var hitbox := _make_hitbox(10)
	add_child(hitbox)

	var signal_fired := false
	hitbox.activated.connect(func(): signal_fired = true)

	hitbox.set_active(true)
	assert_bool(signal_fired).is_true()


func test_deactivated_signal_emitted() -> void:
	var hitbox := _make_hitbox(10)
	add_child(hitbox)

	hitbox.set_active(true)  # ativa primeiro
	var signal_fired := false
	hitbox.deactivated.connect(func(): signal_fired = true)

	hitbox.set_active(false)
	assert_bool(signal_fired).is_true()


# ── Multi-hit prevention ─────────────────────────────────────────────────────

func test_same_target_hit_only_once_per_frame() -> void:
	var hitbox := _make_hitbox(10)
	var health := _make_health(100)
	var target := Node2D.new()
	target.add_child(health)

	add_child(hitbox)
	add_child(target)

	hitbox.active = true
	hitbox._handle_hit(target)
	hitbox._handle_hit(target)  # Segundo hit no mesmo frame

	assert_int(health.current_hp).is_equal(90)  # Só um hit


func test_reset_hits_allows_new_hit() -> void:
	var hitbox := _make_hitbox(10)
	var health := _make_health(100)
	var target := Node2D.new()
	target.add_child(health)

	add_child(hitbox)
	add_child(target)

	hitbox.active = true
	hitbox._handle_hit(target)
	hitbox.reset_hits()
	hitbox._handle_hit(target)  # Deve atingir de novo

	assert_int(health.current_hp).is_equal(80)


# ── _find_health recursivo ───────────────────────────────────────────────────

func test_find_health_in_direct_child() -> void:
	var hitbox := _make_hitbox(10)
	var health := _make_health(100)
	var target := Node2D.new()
	target.add_child(health)

	var found := hitbox._find_health(target)
	assert_object(found).is_not_null()
	assert_int(found.max_hp).is_equal(100)


func test_find_health_returns_null_when_absent() -> void:
	var hitbox := _make_hitbox(10)
	var target := Node2D.new()  # Sem Health

	var found := hitbox._find_health(target)
	assert_object(found).is_null()


# ── Alvo sem Health ──────────────────────────────────────────────────────────

func test_handle_hit_no_health_component() -> void:
	var hitbox := _make_hitbox(30)
	var target := Node2D.new()  # Sem Health

	add_child(hitbox)
	add_child(target)

	hitbox.active = true
	hitbox._handle_hit(target)

	# Não deve crashar e _hit_targets deve continuar vazio
	assert_int(hitbox._hit_targets.size()).is_equal(0)


func test_hit_dealt_not_emitted_without_health() -> void:
	var hitbox := _make_hitbox(30)
	var target := Node2D.new()  # Sem Health

	add_child(hitbox)
	add_child(target)

	var signal_fired := false
	hitbox.hit_dealt.connect(func(_t, _d): signal_fired = true)

	hitbox.active = true
	hitbox._handle_hit(target)

	assert_bool(signal_fired).is_false()


# ── Hit type e knockback ────────────────────────────────────────────────────

func test_hit_type_default_is_melee() -> void:
	var hitbox := _make_hitbox(10)
	assert_str(hitbox.hit_type).is_equal("melee")


func test_knockback_force_default() -> void:
	var hitbox := _make_hitbox(10)
	assert_float(hitbox.knockback_force).is_equal(200.0)


# ── configuration warnings ───────────────────────────────────────────────────

func test_warning_damage_zero() -> void:
	var hitbox := _make_hitbox(0)
	var warnings := hitbox._get_configuration_warnings()
	assert_bool(warnings.size() > 0).is_true()


func test_warning_hit_type_invalid() -> void:
	var hitbox := _make_hitbox(10)
	hitbox.hit_type = "laser"
	var warnings := hitbox._get_configuration_warnings()
	assert_bool(warnings.size() > 0).is_true()


func test_warning_default_collision_mask() -> void:
	var hitbox := _make_hitbox(10)
	# Default: collision_layer=1, collision_mask=1
	var warnings := hitbox._get_configuration_warnings()
	var has_mask_warning := false
	for w in warnings:
		if "collision_mask" in w:
			has_mask_warning = true
			break
	assert_bool(has_mask_warning).is_true()


func test_purge_stale_targets_removes_freed_nodes() -> void:
	var hitbox := _make_hitbox(10)
	var target := Node2D.new()
	add_child(hitbox)
	add_child(target)

	# Adiciona target manualmente ao array
	hitbox._hit_targets.append(target)
	assert_int(hitbox._hit_targets.size()).is_equal(1)

	# Libera o target
	remove_child(target)
	target.free()

	# Purga deve remover
	hitbox._purge_stale_targets()
	assert_int(hitbox._hit_targets.size()).is_equal(0)


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_hitbox(dmg: int) -> Hitbox:
	var hb := Hitbox.new()
	hb.damage = dmg
	return hb


func _make_health(hp: int) -> Health:
	var h := Health.new()
	h.max_hp = hp
	h.current_hp = hp
	return h
