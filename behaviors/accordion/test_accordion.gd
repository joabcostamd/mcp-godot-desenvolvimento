## test_accordion.gd — Testes do behavior Accordion | GdUnit4.
##
## Testa add/remove/toggle, allow_multiple, sinais, edge cases.
## Fonte: Godot 4.7 ClassDB — VBoxContainer, Button, Control.

extends GdUnitTestSuite


func _make_acc() -> Accordion:
	return Accordion.new()


func _make_label(text: String = "Conteúdo") -> Label:
	var lbl := Label.new()
	lbl.text = text
	return lbl


# ── Compilação e defaults ─────────────────────────────────────────────────────

func test_script_compiles() -> void:
	var acc := Accordion.new()
	assert_object(acc).is_not_null()
	acc.queue_free()


func test_default_parameters() -> void:
	var acc := _make_acc()
	assert_float(acc.animation_duration).is_equal(0.2)
	assert_bool(acc.allow_multiple).is_false()
	acc.queue_free()


func test_starts_empty() -> void:
	var acc := _make_acc()
	assert_int(acc.get_section_count()).is_equal(0)
	acc.queue_free()


# ── add_section ───────────────────────────────────────────────────────────────

func test_add_section() -> void:
	var acc := _make_acc()
	add_child(acc)

	var idx := acc.add_section("Seção 1", _make_label("Conteúdo 1"))
	assert_int(idx).is_equal(0)
	assert_int(acc.get_section_count()).is_equal(1)
	assert_bool(acc.is_section_collapsed(0)).is_false()

	remove_child(acc)
	acc.queue_free()


func test_add_section_collapsed() -> void:
	var acc := _make_acc()
	add_child(acc)

	acc.add_section("Recolhida", _make_label("X"), true)
	assert_bool(acc.is_section_collapsed(0)).is_true()

	remove_child(acc)
	acc.queue_free()


func test_add_multiple_sections() -> void:
	var acc := _make_acc()
	add_child(acc)

	acc.add_section("A", _make_label("a"))
	acc.add_section("B", _make_label("b"))
	acc.add_section("C", _make_label("c"))
	assert_int(acc.get_section_count()).is_equal(3)

	remove_child(acc)
	acc.queue_free()


# ── toggle_section ────────────────────────────────────────────────────────────

func test_toggle_collapses() -> void:
	var acc := _make_acc()
	add_child(acc)
	acc.add_section("Toggle", _make_label("X"))

	assert_bool(acc.is_section_collapsed(0)).is_false()
	acc.toggle_section(0)
	assert_bool(acc.is_section_collapsed(0)).is_true()

	remove_child(acc)
	acc.queue_free()


func test_toggle_expands() -> void:
	var acc := _make_acc()
	add_child(acc)
	acc.add_section("Toggle", _make_label("X"), true)

	assert_bool(acc.is_section_collapsed(0)).is_true()
	acc.toggle_section(0)
	assert_bool(acc.is_section_collapsed(0)).is_false()

	remove_child(acc)
	acc.queue_free()


func test_toggle_invalid_index() -> void:
	var acc := _make_acc()
	add_child(acc)
	# Não deve crashar
	acc.toggle_section(-1)
	acc.toggle_section(99)
	assert_bool(true).is_true()
	remove_child(acc)
	acc.queue_free()


# ── allow_multiple ────────────────────────────────────────────────────────────

func test_single_mode_closes_others() -> void:
	var acc := _make_acc()
	add_child(acc)
	acc.allow_multiple = false
	acc.add_section("A", _make_label("a"))
	acc.add_section("B", _make_label("b"))

	# A está aberta (default), B também
	# Expande B → deve fechar A
	acc.toggle_section(1)  # abre B (já está aberta → fecha)
	# Vamos testar de forma mais direta:
	# Primeiro fecha B, depois expande B → A deve fechar
	acc.toggle_section(0)  # fecha A
	acc.toggle_section(1)  # abre B
	assert_bool(acc.is_section_collapsed(0)).is_true()  # A fechada
	assert_bool(acc.is_section_collapsed(1)).is_false()  # B aberta

	# Agora abre A → B deve fechar
	acc.toggle_section(0)
	assert_bool(acc.is_section_collapsed(0)).is_false()  # A aberta
	assert_bool(acc.is_section_collapsed(1)).is_true()   # B fechada

	remove_child(acc)
	acc.queue_free()


func test_multiple_mode_allows_all_open() -> void:
	var acc := _make_acc()
	add_child(acc)
	acc.allow_multiple = true
	acc.add_section("A", _make_label("a"))
	acc.add_section("B", _make_label("b"))

	# Ambas começam abertas
	assert_bool(acc.is_section_collapsed(0)).is_false()
	assert_bool(acc.is_section_collapsed(1)).is_false()

	remove_child(acc)
	acc.queue_free()


# ── collapse_all / expand_all ─────────────────────────────────────────────────

func test_collapse_all() -> void:
	var acc := _make_acc()
	add_child(acc)
	acc.add_section("A", _make_label("a"))
	acc.add_section("B", _make_label("b"))

	acc.collapse_all()
	assert_bool(acc.is_section_collapsed(0)).is_true()
	assert_bool(acc.is_section_collapsed(1)).is_true()

	remove_child(acc)
	acc.queue_free()


func test_expand_all() -> void:
	var acc := _make_acc()
	add_child(acc)
	acc.add_section("A", _make_label("a"), true)
	acc.add_section("B", _make_label("b"), true)

	acc.expand_all()
	assert_bool(acc.is_section_collapsed(0)).is_false()
	assert_bool(acc.is_section_collapsed(1)).is_false()

	remove_child(acc)
	acc.queue_free()


# ── Signal ────────────────────────────────────────────────────────────────────

func test_emits_section_toggled() -> void:
	var acc := _make_acc()
	add_child(acc)
	acc.add_section("Sinal", _make_label("x"))

	var toggled_index := -1
	var toggled_collapsed := false
	acc.section_toggled.connect(func(idx, col):
		toggled_index = idx
		toggled_collapsed = col
	)

	acc.toggle_section(0)
	assert_int(toggled_index).is_equal(0)
	assert_bool(toggled_collapsed).is_true()

	remove_child(acc)
	acc.queue_free()


# ── remove_section ────────────────────────────────────────────────────────────

func test_remove_section() -> void:
	var acc := _make_acc()
	add_child(acc)
	acc.add_section("A", _make_label("a"))
	acc.add_section("B", _make_label("b"))
	assert_int(acc.get_section_count()).is_equal(2)

	acc.remove_section(0)
	assert_int(acc.get_section_count()).is_equal(1)

	remove_child(acc)
	acc.queue_free()


func test_remove_section_invalid() -> void:
	var acc := _make_acc()
	add_child(acc)
	acc.add_section("A", _make_label("a"))
	acc.remove_section(99)  # não crasha
	assert_int(acc.get_section_count()).is_equal(1)
	remove_child(acc)
	acc.queue_free()
