## test_hurtbox.gd — Testes do behavior Hurtbox | GdUnit4.
##
## Cobre: dano via Hitbox e Projectile, multiplicador, health_path,
##        bloqueio, sinais hit_received/hit_blocked, _extract_damage_info,
##        hurt_type, warnings.
##
## Requer: GdUnit4 instalado como addon.
## Executar: GdUnit4 > Run Tests na cena behaviors/hurtbox/test_hurtbox.gd

extends GdUnitTestSuite


# ── Dano via Hitbox ──────────────────────────────────────────────────────────

func test_receives_damage_from_active_hitbox() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.name = "Enemy"
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	var hitbox := _make_hitbox(30)
	hitbox.active = true

	add_child(owner_node)
	add_child(hitbox)

	hurtbox._apply_damage(hitbox.damage, hitbox.hit_type)

	assert_int(health.current_hp).is_equal(70)


func test_damage_multiplier_doubles_damage() -> void:
	var hurtbox := _make_hurtbox(2.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	var hitbox := _make_hitbox(25)
	hitbox.active = true

	add_child(owner_node)
	add_child(hitbox)

	hurtbox._apply_damage(hitbox.damage, hitbox.hit_type)

	assert_int(health.current_hp).is_equal(50)


func test_damage_multiplier_halves_damage() -> void:
	var hurtbox := _make_hurtbox(0.5)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	var hitbox := _make_hitbox(30)
	hitbox.active = true

	add_child(owner_node)
	add_child(hitbox)

	hurtbox._apply_damage(hitbox.damage, hitbox.hit_type)

	assert_int(health.current_hp).is_equal(85)


func test_damage_multiplier_zero_blocks_all() -> void:
	var hurtbox := _make_hurtbox(0.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	var hitbox := _make_hitbox(999)
	hitbox.active = true

	add_child(owner_node)
	add_child(hitbox)

	hurtbox._apply_damage(hitbox.damage, hitbox.hit_type)

	assert_int(health.current_hp).is_equal(100)


# ── Dano via Projectile ──────────────────────────────────────────────────────

func test_receives_damage_from_projectile() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	var proj := _make_projectile(40)

	add_child(owner_node)
	add_child(proj)

	hurtbox._apply_damage(proj.damage, "ranged")

	assert_int(health.current_hp).is_equal(60)


func test_projectile_damage_with_multiplier() -> void:
	var hurtbox := _make_hurtbox(2.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	var proj := _make_projectile(30)

	add_child(owner_node)
	add_child(proj)

	hurtbox._apply_damage(proj.damage, "ranged")

	assert_int(health.current_hp).is_equal(40)


# ── Extract damage info ──────────────────────────────────────────────────────

func test_extract_info_from_active_hitbox() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var hitbox := _make_hitbox(25)
	hitbox.active = true

	var info := hurtbox._extract_damage_info(hitbox)
	assert_bool(info.is_empty()).is_false()
	assert_int(info["damage"]).is_equal(25)
	assert_str(info["hit_type"]).is_equal("melee")


func test_extract_info_from_inactive_hitbox_returns_empty() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var hitbox := _make_hitbox(25)
	hitbox.active = false

	var info := hurtbox._extract_damage_info(hitbox)
	assert_bool(info.is_empty()).is_true()


func test_extract_info_from_projectile() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var proj := _make_projectile(50)

	var info := hurtbox._extract_damage_info(proj)
	assert_bool(info.is_empty()).is_false()
	assert_int(info["damage"]).is_equal(50)
	assert_str(info["hit_type"]).is_equal("ranged")


func test_extract_info_from_unknown_area_returns_empty() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var generic := Area2D.new()

	var info := hurtbox._extract_damage_info(generic)
	assert_bool(info.is_empty()).is_true()


# ── Hitbox inativa / nao-damage area ────────────────────────────────────────

func test_ignores_inactive_hitbox() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	var hitbox := _make_hitbox(30)
	hitbox.active = false

	add_child(owner_node)
	add_child(hitbox)

	hurtbox._on_area_entered(hitbox)

	assert_int(health.current_hp).is_equal(100)


func test_ignores_non_damage_area() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	var generic_area := Area2D.new()

	add_child(owner_node)
	add_child(generic_area)

	hurtbox._on_area_entered(generic_area)

	assert_int(health.current_hp).is_equal(100)


# ── health_path ──────────────────────────────────────────────────────────────

func test_health_path_invalid_blocks_damage() -> void:
	var hurtbox := _make_hurtbox(1.0)
	hurtbox.health_path = NodePath("../Inexistente")

	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)

	add_child(owner_node)

	hurtbox._apply_damage(30, "melee")

	assert_int(health.current_hp).is_equal(100)


func test_health_path_empty_blocks_damage() -> void:
	var hurtbox := _make_hurtbox(1.0)

	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)

	add_child(owner_node)

	hurtbox._apply_damage(30, "melee")

	assert_int(health.current_hp).is_equal(100)


# ── Sinais ───────────────────────────────────────────────────────────────────

func test_hit_received_signal_emitted() -> void:
	var hurtbox := _make_hurtbox(1.5)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	add_child(owner_node)

	var signal_fired := false
	var captured_original := 0
	var captured_modified := 0
	var captured_type := ""
	hurtbox.hit_received.connect(func(orig, mod, htype):
		signal_fired = true
		captured_original = orig
		captured_modified = mod
		captured_type = htype
	)

	hurtbox._apply_damage(20, "melee")

	assert_bool(signal_fired).is_true()
	assert_int(captured_original).is_equal(20)
	assert_int(captured_modified).is_equal(30)
	assert_str(captured_type).is_equal("melee")


func test_hit_received_with_projectile_hit_type() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	add_child(owner_node)

	var captured_type := ""
	hurtbox.hit_received.connect(func(_o, _m, htype):
		captured_type = htype
	)

	hurtbox._apply_damage(10, "ranged")

	assert_str(captured_type).is_equal("ranged")


func test_hit_blocked_signal_when_multiplier_zero() -> void:
	var hurtbox := _make_hurtbox(0.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	add_child(owner_node)

	var blocked_fired := false
	var blocked_reason := ""
	hurtbox.hit_blocked.connect(func(dmg, reason):
		blocked_fired = true
		blocked_reason = reason
	)

	hurtbox._apply_damage(50, "melee")

	assert_bool(blocked_fired).is_true()
	assert_str(blocked_reason).is_equal("damage_multiplier_zero")


func test_hit_blocked_signal_when_health_path_invalid() -> void:
	var hurtbox := _make_hurtbox(1.0)
	hurtbox.health_path = NodePath("../NaoExiste")

	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)

	add_child(owner_node)

	var blocked_fired := false
	var blocked_reason := ""
	hurtbox.hit_blocked.connect(func(dmg, reason):
		blocked_fired = true
		blocked_reason = reason
	)

	hurtbox._apply_damage(50, "melee")

	assert_bool(blocked_fired).is_true()
	assert_str(blocked_reason).is_equal("health_path_invalid")


func test_hit_received_not_emitted_when_multiplier_zero() -> void:
	var hurtbox := _make_hurtbox(0.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	add_child(owner_node)

	var received_fired := false
	hurtbox.hit_received.connect(func(_a, _b, _c): received_fired = true)

	hurtbox._apply_damage(50, "melee")

	assert_bool(received_fired).is_false()


# ── Tipo de hurtbox ──────────────────────────────────────────────────────────

func test_hurt_type_default_is_body() -> void:
	var hurtbox := _make_hurtbox(1.0)
	assert_str(hurtbox.hurt_type).is_equal("body")


# ── Configuration warnings ──────────────────────────────────────────────────

func test_warning_empty_health_path() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var warnings := hurtbox._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "health_path" in w:
			found = true
			break
	assert_bool(found).is_true()


func test_warning_multiplier_zero() -> void:
	var hurtbox := _make_hurtbox(0.0)
	hurtbox.health_path = NodePath("../Health")
	var warnings := hurtbox._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "damage_multiplier" in w:
			found = true
			break
	assert_bool(found).is_true()


func test_warning_hurt_type_invalid() -> void:
	var hurtbox := _make_hurtbox(1.0)
	hurtbox.hurt_type = "wing"
	var warnings := hurtbox._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "hurt_type" in w:
			found = true
			break
	assert_bool(found).is_true()


func test_warning_default_collision_mask() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var warnings := hurtbox._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "collision_mask" in w:
			found = true
			break
	assert_bool(found).is_true()


func test_warning_health_sibling_detected() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var health := _make_health(100)
	var parent := Node2D.new()
	parent.add_child(health)
	parent.add_child(hurtbox)
	add_child(parent)

	var warnings := hurtbox._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "double-damage" in w:
			found = true
			break
	assert_bool(found).is_true()


# ── _resolve_health ──────────────────────────────────────────────────────────

func test_resolve_health_finds_sibling() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var health := _make_health(100)
	var owner_node := Node2D.new()
	owner_node.add_child(health)
	owner_node.add_child(hurtbox)
	hurtbox.health_path = NodePath("../Health")

	add_child(owner_node)

	var resolved := hurtbox._resolve_health()
	assert_object(resolved).is_not_null()
	assert_int(resolved.max_hp).is_equal(100)


func test_resolve_health_returns_null_for_empty_path() -> void:
	var hurtbox := _make_hurtbox(1.0)
	var resolved := hurtbox._resolve_health()
	assert_object(resolved).is_null()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_hurtbox(mult: float) -> Hurtbox:
	var hb := Hurtbox.new()
	hb.damage_multiplier = mult
	return hb


func _make_hitbox(dmg: int) -> Hitbox:
	var hb := Hitbox.new()
	hb.damage = dmg
	return hb


func _make_projectile(dmg: int) -> Projectile:
	var p := Projectile.new()
	p.damage = dmg
	return p


func _make_health(hp: int) -> Health:
	var h := Health.new()
	h.max_hp = hp
	h.current_hp = hp
	return h
