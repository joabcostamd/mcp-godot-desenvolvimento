## test_fire_rate.gd — Testes do behavior FireRate | GdUnit4.
##
## Cobre: try_fire, cooldown, burst, sinais fired/ready,
##        is_ready, reset, warnings.
##
## Requer: GdUnit4 instalado como addon.

extends GdUnitTestSuite


# ── try_fire básico ──────────────────────────────────────────────────────────

func test_try_fire_returns_true_when_ready() -> void:
	var fr := _make_fire_rate(0.5, 1, 0.1)
	add_child(fr)

	var result := fr.try_fire()
	assert_bool(result).is_true()


func test_try_fire_returns_false_during_cooldown() -> void:
	var fr := _make_fire_rate(99.0, 1, 0.1)
	add_child(fr)

	fr.try_fire()
	var result := fr.try_fire()
	assert_bool(result).is_false()


func test_try_fire_emits_fired_signal() -> void:
	var fr := _make_fire_rate(0.5, 1, 0.1)
	add_child(fr)

	var signal_fired := false
	fr.fired.connect(func(): signal_fired = true)

	fr.try_fire()
	assert_bool(signal_fired).is_true()


# ── Cooldown ─────────────────────────────────────────────────────────────────

func test_is_ready_false_during_cooldown() -> void:
	var fr := _make_fire_rate(99.0, 1, 0.1)
	add_child(fr)

	fr.try_fire()
	assert_bool(fr.is_ready()).is_false()


func test_is_ready_true_initially() -> void:
	var fr := _make_fire_rate(0.5, 1, 0.1)
	assert_bool(fr.is_ready()).is_true()


func test_ready_signal_after_cooldown() -> void:
	var fr := _make_fire_rate(0.01, 1, 0.1)
	add_child(fr)

	var ready_fired := false
	fr.cooldown_ready.connect(func(): ready_fired = true)

	fr.try_fire()
	await get_tree().create_timer(0.05).timeout

	assert_bool(ready_fired).is_true()
	assert_bool(fr.is_ready()).is_true()


# ── Burst ────────────────────────────────────────────────────────────────────

func test_burst_emits_multiple_fired_signals() -> void:
	var fr := _make_fire_rate(99.0, 3, 0.01)
	add_child(fr)

	var fire_count := 0
	fr.fired.connect(func(): fire_count += 1)

	fr.try_fire()
	# Espera a rajada completa (3 tiros × 0.01s)
	await get_tree().create_timer(0.1).timeout

	assert_int(fire_count).is_equal(3)


func test_burst_count_one_single_shot() -> void:
	var fr := _make_fire_rate(0.5, 1, 0.1)
	add_child(fr)

	var fire_count := 0
	fr.fired.connect(func(): fire_count += 1)

	fr.try_fire()
	await get_tree().create_timer(0.05).timeout

	assert_int(fire_count).is_equal(1)


func test_cannot_fire_during_burst() -> void:
	var fr := _make_fire_rate(99.0, 5, 0.05)
	add_child(fr)

	fr.try_fire()  # Inicia rajada de 5 tiros
	# Imediatamente após o primeiro tiro, ainda está em burst
	var result := fr.try_fire()
	assert_bool(result).is_false()


# ── Reset ────────────────────────────────────────────────────────────────────

func test_reset_allows_immediate_fire() -> void:
	var fr := _make_fire_rate(99.0, 1, 0.1)
	add_child(fr)

	fr.try_fire()  # Entra em cooldown longo
	assert_bool(fr.is_ready()).is_false()

	fr.reset()
	assert_bool(fr.is_ready()).is_true()

	var result := fr.try_fire()
	assert_bool(result).is_true()


func test_reset_during_burst_stops_burst() -> void:
	var fr := _make_fire_rate(99.0, 5, 0.1)
	add_child(fr)

	var fire_count := 0
	fr.fired.connect(func(): fire_count += 1)

	fr.try_fire()  # Inicia burst de 5
	fr.reset()      # Cancela o burst
	await get_tree().create_timer(0.3).timeout

	# Deve ter disparado apenas o primeiro tiro (antes do reset)
	assert_int(fire_count).is_equal(1)


# ── Setters ──────────────────────────────────────────────────────────────────

func test_fire_interval_clamped() -> void:
	var fr := _make_fire_rate(0.5, 1, 0.1)
	fr.fire_interval = -1.0
	assert_float(fr.fire_interval).is_equal(0.05)  # clamp mínimo

	fr.fire_interval = 999.0
	assert_float(fr.fire_interval).is_equal(60.0)  # clamp máximo


func test_burst_count_clamped() -> void:
	var fr := _make_fire_rate(0.5, 1, 0.1)
	fr.burst_count = 0
	assert_int(fr.burst_count).is_equal(1)

	fr.burst_count = 999
	assert_int(fr.burst_count).is_equal(20)


func test_burst_delay_clamped() -> void:
	var fr := _make_fire_rate(0.5, 1, 0.1)
	fr.burst_delay = 0.0
	assert_float(fr.burst_delay).is_equal(0.01)

	fr.burst_delay = 999.0
	assert_float(fr.burst_delay).is_equal(5.0)


# ── Warnings ─────────────────────────────────────────────────────────────────

func test_warning_burst_delay_vs_interval() -> void:
	var fr := _make_fire_rate(0.1, 3, 0.5)  # burst_delay > fire_interval
	var warnings := fr._get_configuration_warnings()
	assert_bool(warnings.size() > 0).is_true()


func test_no_warning_when_config_valid() -> void:
	var fr := _make_fire_rate(0.5, 1, 0.1)
	var warnings := fr._get_configuration_warnings()
	assert_bool(warnings.size()).is_equal(0)


# ── Robustez ─────────────────────────────────────────────────────────────────

func test_reset_safe_before_ready() -> void:
	var fr := FireRate.new()
	fr.fire_interval = 0.5
	# reset() antes de add_child — não deve crashar
	fr.reset()
	assert_bool(fr.is_ready()).is_true()


func test_try_fire_safe_before_ready() -> void:
	var fr := FireRate.new()
	fr.fire_interval = 0.5
	fr.burst_count = 1
	# try_fire() antes de add_child — deve retornar false, não crashar
	var result := fr.try_fire()
	# Sem timers, não pode atirar
	assert_bool(result).is_false()


# ── Helpers ──────────────────────────────────────────────────────────────────

func _make_fire_rate(interval: float, burst: int, delay: float) -> FireRate:
	var fr := FireRate.new()
	fr.fire_interval = interval
	fr.burst_count = burst
	fr.burst_delay = delay
	return fr
