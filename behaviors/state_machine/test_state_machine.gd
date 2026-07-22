## test_state_machine.gd — Testes do behavior StateMachine | GdUnit4.
##
## Cobre: configure, trigger, set_state, get_state, is_state,
##        transição "any", sinais, estado inexistente.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── configure ────────────────────────────────────────────────────────────────

func test_configure_states_and_transitions() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack", "hurt"], [
		{"from": "idle", "to": "attack", "condition": "player_spotted"},
		{"from": "attack", "to": "idle", "condition": "player_lost"}
	], "idle")

	assert_str(sm.get_state()).is_equal("idle")
	assert_int(sm.get_states().size()).is_equal(3)


func test_default_state_used_when_not_specified() -> void:
	var sm := _make_sm()
	sm.default_state = "patrol"
	sm.configure(["patrol", "chase"], [
		{"from": "patrol", "to": "chase", "condition": "found"}
	])

	assert_str(sm.get_state()).is_equal("patrol")


# ── trigger ──────────────────────────────────────────────────────────────────

func test_trigger_applies_transition() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack"], [
		{"from": "idle", "to": "attack", "condition": "go"}
	], "idle")

	var result := sm.trigger("go")
	assert_bool(result).is_true()
	assert_str(sm.get_state()).is_equal("attack")


func test_trigger_no_match_returns_false() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack"], [
		{"from": "idle", "to": "attack", "condition": "go"}
	], "idle")

	var result := sm.trigger("unknown_condition")
	assert_bool(result).is_false()
	assert_str(sm.get_state()).is_equal("idle")


func test_trigger_wrong_from_state_returns_false() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack"], [
		{"from": "attack", "to": "idle", "condition": "stop"}
	], "idle")

	# Estamos em "idle", mas a transição é from "attack"
	var result := sm.trigger("stop")
	assert_bool(result).is_false()


# ── "any" wildcard ───────────────────────────────────────────────────────────

func test_any_from_matches_all_states() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack", "hurt"], [
		{"from": "idle", "to": "attack", "condition": "go"},
		{"from": "any", "to": "hurt", "condition": "damaged"}
	], "idle")

	sm.trigger("go")
	assert_str(sm.get_state()).is_equal("attack")

	# "any" deve funcionar de "attack" também
	var result := sm.trigger("damaged")
	assert_bool(result).is_true()
	assert_str(sm.get_state()).is_equal("hurt")


# ── set_state ────────────────────────────────────────────────────────────────

func test_set_state_valid() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack", "dead"], [], "idle")

	var result := sm.set_state("dead")
	assert_bool(result).is_true()
	assert_str(sm.get_state()).is_equal("dead")


func test_set_state_invalid_returns_false() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack"], [], "idle")

	var result := sm.set_state("nonexistent")
	assert_bool(result).is_false()
	assert_str(sm.get_state()).is_equal("idle")


# ── is_state ─────────────────────────────────────────────────────────────────

func test_is_state() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack"], [], "idle")

	assert_bool(sm.is_state("idle")).is_true()
	assert_bool(sm.is_state("attack")).is_false()


# ── Sinais ───────────────────────────────────────────────────────────────────

func test_state_changed_signal() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack"], [
		{"from": "idle", "to": "attack", "condition": "go"}
	], "idle")

	var signal_fired := false
	var captured_from := ""
	var captured_to := ""
	sm.state_changed.connect(func(f, t):
		signal_fired = true
		captured_from = f
		captured_to = t
	)

	sm.trigger("go")
	assert_bool(signal_fired).is_true()
	assert_str(captured_from).is_equal("idle")
	assert_str(captured_to).is_equal("attack")


func test_state_entered_signal() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack"], [
		{"from": "idle", "to": "attack", "condition": "go"}
	], "idle")

	var captured_state := ""
	sm.state_entered.connect(func(s): captured_state = s)

	sm.trigger("go")
	assert_str(captured_state).is_equal("attack")


func test_state_exited_signal() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack"], [
		{"from": "idle", "to": "attack", "condition": "go"}
	], "idle")

	var captured_state := ""
	sm.state_exited.connect(func(s): captured_state = s)

	sm.trigger("go")
	assert_str(captured_state).is_equal("idle")


# ── trigger antes de configure ──────────────────────────────────────────────

func test_trigger_before_configure_returns_false() -> void:
	var sm := _make_sm()
	var result := sm.trigger("anything")
	assert_bool(result).is_false()


# ── Warnings ─────────────────────────────────────────────────────────────────

func test_warning_no_states() -> void:
	var sm := _make_sm()
	var warnings := sm._get_configuration_warnings()
	assert_bool(warnings.size() > 0).is_true()


func test_no_warning_when_configured() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "run"], [
		{"from": "idle", "to": "run", "condition": "scared"}
	], "idle")
	var warnings := sm._get_configuration_warnings()
	assert_bool(warnings.size()).is_equal(0)


# ── Edge cases ──────────────────────────────────────────────────────────────

func test_configure_default_not_in_states_falls_back() -> void:
	var sm := _make_sm()
	sm.default_state = "ghost"  # não está na lista
	sm.configure(["attack", "hurt"], [
		{"from": "attack", "to": "hurt", "condition": "ouch"}
	])
	# Deve usar o primeiro estado da lista como fallback
	assert_str(sm.get_state()).is_equal("attack")


func test_set_state_same_state_no_signals() -> void:
	var sm := _make_sm()
	sm.configure(["idle", "attack"], [], "idle")

	var signal_fired := false
	sm.state_changed.connect(func(_f, _t): signal_fired = true)

	# Transição para o mesmo estado não deve emitir sinais
	sm.set_state("idle")
	assert_bool(signal_fired).is_false()


func test_warning_transition_to_invalid_state() -> void:
	var sm := _make_sm()
	sm.configure(["idle"], [
		{"from": "idle", "to": "ghost", "condition": "spook"}
	], "idle")
	var warnings := sm._get_configuration_warnings()
	var found := false
	for w in warnings:
		if "ghost" in w:
			found = true
			break
	assert_bool(found).is_true()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_sm() -> StateMachine:
	return StateMachine.new()
