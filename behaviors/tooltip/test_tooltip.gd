## test_tooltip.gd — Testes do behavior Tooltip | GdUnit4.
##
## Testa exibição/ocultação, delay, posição, edge cases.
## Fonte: Godot 4.7 ClassDB — Control, PanelContainer, Label, Timer.

extends GdUnitTestSuite


func _make_tip() -> Tooltip:
	return Tooltip.new()


func _make_parent() -> Control:
	var ctrl := Control.new()
	ctrl.size = Vector2(200, 60)
	return ctrl


# ── Compilação e defaults ─────────────────────────────────────────────────────

func test_script_compiles() -> void:
	var tip := Tooltip.new()
	assert_object(tip).is_not_null()
	tip.queue_free()


func test_default_parameters() -> void:
	var tip := _make_tip()
	assert_str(tip.tooltip_text).is_equal("")
	assert_float(tip.show_delay).is_equal(0.5)
	assert_bool(tip.follow_mouse).is_true()
	assert_that(tip.position_offset).is_equal(Vector2(0, -40))
	tip.queue_free()


func test_starts_hidden() -> void:
	var tip := _make_tip()
	assert_bool(tip.is_visible_tooltip()).is_false()
	tip.queue_free()


# ── show_tooltip / hide_tooltip ───────────────────────────────────────────────

func test_show_tooltip_manual() -> void:
	var parent := _make_parent()
	add_child(parent)
	var tip := _make_tip()
	parent.add_child(tip)

	tip.show_tooltip("Dica de teste")
	assert_bool(tip.is_visible_tooltip()).is_true()

	remove_child(parent)
	parent.queue_free()
	tip.queue_free()


func test_hide_tooltip_manual() -> void:
	var parent := _make_parent()
	add_child(parent)
	var tip := _make_tip()
	parent.add_child(tip)

	tip.show_tooltip("Dica")
	assert_bool(tip.is_visible_tooltip()).is_true()
	tip.hide_tooltip()
	assert_bool(tip.is_visible_tooltip()).is_false()

	remove_child(parent)
	parent.queue_free()
	tip.queue_free()


func test_show_empty_text_does_nothing() -> void:
	var parent := _make_parent()
	add_child(parent)
	var tip := _make_tip()
	tip.tooltip_text = ""
	parent.add_child(tip)

	tip.show_tooltip()  # texto vazio → não mostra
	assert_bool(tip.is_visible_tooltip()).is_false()

	remove_child(parent)
	parent.queue_free()
	tip.queue_free()


func test_show_tooltip_with_param_updates_text() -> void:
	var parent := _make_parent()
	add_child(parent)
	var tip := _make_tip()
	parent.add_child(tip)

	tip.show_tooltip("Novo texto")
	assert_str(tip.tooltip_text).is_equal("Novo texto")
	assert_bool(tip.is_visible_tooltip()).is_true()

	remove_child(parent)
	parent.queue_free()
	tip.queue_free()


# ── Delay ─────────────────────────────────────────────────────────────────────

func test_zero_delay_shows_immediately() -> void:
	var parent := _make_parent()
	add_child(parent)
	var tip := _make_tip()
	tip.tooltip_text = "Instantâneo"
	tip.show_delay = 0.0
	parent.add_child(tip)

	# Simula mouse enter — delay zero → mostra imediatamente
	tip._on_mouse_entered()
	assert_bool(tip.is_visible_tooltip()).is_true()

	remove_child(parent)
	parent.queue_free()
	tip.queue_free()


func test_delay_starts_timer() -> void:
	var parent := _make_parent()
	add_child(parent)
	var tip := _make_tip()
	tip.tooltip_text = "Com delay"
	tip.show_delay = 1.0
	parent.add_child(tip)

	tip._on_mouse_entered()
	# Ainda não visível (timer não disparou)
	assert_bool(tip.is_visible_tooltip()).is_false()

	remove_child(parent)
	parent.queue_free()
	tip.queue_free()


func test_mouse_exit_cancels_delay() -> void:
	var parent := _make_parent()
	add_child(parent)
	var tip := _make_tip()
	tip.tooltip_text = "Cancelado"
	tip.show_delay = 1.0
	parent.add_child(tip)

	tip._on_mouse_entered()
	assert_bool(tip.is_visible_tooltip()).is_false()

	tip._on_mouse_exited()
	# Ainda não visível (timer cancelado)
	assert_bool(tip.is_visible_tooltip()).is_false()

	remove_child(parent)
	parent.queue_free()
	tip.queue_free()


func test_show_delay_clamped() -> void:
	var tip := _make_tip()
	tip.show_delay = 10.0  # acima do max
	assert_float(tip.show_delay).is_equal(5.0)
	tip.show_delay = -1.0  # abaixo do min
	assert_float(tip.show_delay).is_equal(0.0)
	tip.queue_free()


# ── Signals ───────────────────────────────────────────────────────────────────

func test_emits_shown_signal() -> void:
	var parent := _make_parent()
	add_child(parent)
	var tip := _make_tip()
	parent.add_child(tip)

	var shown := false
	tip.tooltip_shown.connect(func(): shown = true)

	tip.show_tooltip("Sinal")
	assert_bool(shown).is_true()

	remove_child(parent)
	parent.queue_free()
	tip.queue_free()


func test_emits_hidden_signal() -> void:
	var parent := _make_parent()
	add_child(parent)
	var tip := _make_tip()
	parent.add_child(tip)

	var hidden := false
	tip.tooltip_hidden.connect(func(): hidden = true)

	tip.show_tooltip("Sinal")
	tip.hide_tooltip()
	assert_bool(hidden).is_true()

	remove_child(parent)
	parent.queue_free()
	tip.queue_free()


# ── Sem parent ────────────────────────────────────────────────────────────────

func test_no_parent_does_not_crash() -> void:
	var tip := _make_tip()
	# Sem add_child — sem parent
	tip.show_tooltip("Sem parent")
	# Não deve crashar — _show_panel só atualiza posição, não quebra
	assert_bool(tip.is_visible_tooltip()).is_true()
	tip.queue_free()
