## test_enemy_patrol.gd — Testes do EnemyPatrol | GdUnit4.
##
## Cobre: movimento, waypoint_reached, loop, ping_pong,
##        patrol_complete, edge cases, state_machine integration.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── Movimento ─────────────────────────────────────────────────────────────────

func test_moves_toward_waypoint() -> void:
	var ep := _make_patrol([Vector2(100, 0)], 200.0, 1.0, false, false)
	var parent := CharacterBody2D.new()
	parent.add_child(ep)
	add_child(parent)

	var start := parent.global_position
	ep._physics_process(0.016)
	assert_float(parent.global_position.x).is_greater(start.x)


func test_stops_at_waypoint() -> void:
	var ep := _make_patrol([Vector2(6, 0)], 200.0, 0.0, false, false)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(5, 0)
	parent.add_child(ep)
	add_child(parent)

	# Deve identificar que está perto o suficiente (dist < 4.0)
	ep._physics_process(0.016)
	assert_str(ep._state).is_equal("idle")


func test_empty_waypoints_no_crash() -> void:
	var ep := _make_patrol([], 100.0, 1.0, true, false)
	var parent := CharacterBody2D.new()
	parent.add_child(ep)
	add_child(parent)

	ep._physics_process(0.016)
	assert_bool(true)


# ── Sinais ────────────────────────────────────────────────────────────────────

func test_waypoint_reached_signal() -> void:
	var ep := _make_patrol([Vector2(5, 0)], 200.0, 0.0, false, false)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(5, 0)
	parent.add_child(ep)
	add_child(parent)

	var reached := false
	var reached_idx := -1
	ep.waypoint_reached.connect(func(i): reached = true; reached_idx = i)
	ep._physics_process(0.016)

	assert_bool(reached).is_true()
	assert_int(reached_idx).is_equal(0)


func test_patrol_complete_signal() -> void:
	var ep := _make_patrol([Vector2(5, 0)], 200.0, 0.0, false, false)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(5, 0)
	parent.add_child(ep)
	add_child(parent)

	var complete := false
	ep.patrol_complete.connect(func(): complete = true)
	ep._physics_process(0.016)

	assert_bool(complete).is_true()


# ── Loop ──────────────────────────────────────────────────────────────────────

func test_loop_resets_index() -> void:
	var ep := _make_patrol([Vector2(5, 0)], 200.0, 0.0, true, false)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(5, 0)
	parent.add_child(ep)
	add_child(parent)

	ep._physics_process(0.016)

	# Com loop=true, deve resetar para 0 após último waypoint
	assert_int(ep._current_index).is_equal(0)


func test_no_loop_no_ping_pong_emits_complete() -> void:
	var ep := _make_patrol([Vector2(5, 0)], 200.0, 0.0, false, false)
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(5, 0)
	parent.add_child(ep)
	add_child(parent)

	var complete := false
	ep.patrol_complete.connect(func(): complete = true)
	ep._physics_process(0.016)

	assert_bool(complete).is_true()


# ── Ping-pong ─────────────────────────────────────────────────────────────────

func test_ping_pong_reverses_direction() -> void:
	var ep := _make_patrol([Vector2(5, 0), Vector2(100, 0)], 200.0, 0.0, false, true)
	ep._current_index = 0
	ep._direction = 1
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(5, 0)
	parent.add_child(ep)
	add_child(parent)

	# Chega no waypoint 0 indo para direita → deve inverter
	# Mas wait, o índice 0 é o primeiro. Vamos testar chegando no último
	ep._current_index = 1
	ep._direction = 1
	parent.global_position = Vector2(100, 0)

	ep._physics_process(0.016)

	# Ping-pong: ao chegar no último waypoint indo pra direita,
	# _advance_index inverte _direction para -1
	assert_int(ep._direction).is_equal(-1)


# ── State machine ─────────────────────────────────────────────────────────────

func test_syncs_with_state_machine() -> void:
	var sm := StateMachine.new()
	sm.configure(["patrol", "idle"], [], "patrol")
	var ep := _make_patrol([Vector2(100, 0)], 100.0, 1.0, false, false)
	var parent := CharacterBody2D.new()
	parent.add_child(sm)
	parent.add_child(ep)
	add_child(parent)

	# EnemyPatrol deve encontrar o StateMachine sibling
	assert_object(ep._state_machine).is_not_null()
	assert_str(sm.get_state()).is_equal("patrol")


# ── Timer ─────────────────────────────────────────────────────────────────────

func test_timer_resumes_patrol() -> void:
	var ep := _make_patrol([Vector2(5, 0), Vector2(100, 0)], 100.0, 0.0, false, false)
	ep._current_index = 0
	ep._state = "idle"
	var parent := CharacterBody2D.new()
	parent.global_position = Vector2(5, 0)
	parent.add_child(ep)
	add_child(parent)

	ep._resume_patrol()
	assert_str(ep._state).is_equal("patrol")


# ── Warnings ──────────────────────────────────────────────────────────────────

func test_warning_empty_waypoints() -> void:
	var ep := _make_patrol([], 100.0, 1.0, true, false)
	add_child(ep)

	var found := false
	for w in ep._get_configuration_warnings():
		if "vazio" in w:
			found = true
	assert_bool(found).is_true()


func test_warning_parent_not_character_body() -> void:
	var ep := _make_patrol([Vector2(100, 0)], 100.0, 1.0, false, false)
	var parent := Node2D.new()
	parent.add_child(ep)
	add_child(parent)

	var found := false
	for w in ep._get_configuration_warnings():
		if "CharacterBody2D" in w:
			found = true
	assert_bool(found).is_true()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_patrol(wpts: Array, spd: float, wait: float, loop_val: bool, pp_val: bool) -> EnemyPatrol:
	var ep := EnemyPatrol.new()
	var arr := PackedVector2Array()
	for w in wpts:
		arr.append(w)
	ep.waypoints = arr
	ep.speed = spd
	ep.wait_time = wait
	ep.loop = loop_val
	ep.ping_pong = pp_val
	return ep
