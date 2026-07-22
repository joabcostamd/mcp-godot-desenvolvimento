## test_character_creator.gd — Testes do CharacterCreator | GdUnit4.

extends GdUnitTestSuite


func _make_cc() -> CharacterCreator:
	return CharacterCreator.new()


# ---------------------------------------------------------------------------
# PART MANAGEMENT
# ---------------------------------------------------------------------------

func test_add_part_and_set_option() -> void:
	var cc := _make_cc()
	assert_bool(cc.add_part("hair", ["hair_01", "hair_02", "hair_03"])).is_true()
	assert_int(cc.get_part_option("hair")).is_equal(0)

	cc.set_part_option("hair", 2)
	assert_int(cc.get_part_option("hair")).is_equal(2)
	cc.queue_free()


func test_add_part_empty_options() -> void:
	var cc := _make_cc()
	assert_bool(cc.add_part("body", [])).is_true()
	assert_int(cc.get_part_option("body")).is_equal(-1)

	# Set option on empty part: no-op, stays -1
	cc.set_part_option("body", 0)
	assert_int(cc.get_part_option("body")).is_equal(-1)
	cc.queue_free()


func test_add_duplicate_part() -> void:
	var cc := _make_cc()
	assert_bool(cc.add_part("hair", ["a", "b"])).is_true()
	assert_bool(cc.add_part("hair", ["c", "d"])).is_false()
	assert_int(cc.get_part_options("hair").size()).is_equal(2)  # original preserved
	cc.queue_free()


func test_remove_part() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1"])
	cc.add_part("eyes", ["e1"])
	assert_int(cc.get_part_names().size()).is_equal(2)
	assert_bool(cc.remove_part("hair")).is_true()
	assert_int(cc.get_part_names().size()).is_equal(1)
	assert_bool(cc.remove_part("nonexistent")).is_false()
	cc.queue_free()


func test_set_option_clamped() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1", "h2", "h3"])

	cc.set_part_option("hair", 999)
	assert_int(cc.get_part_option("hair")).is_equal(2)  # clamped to last

	cc.set_part_option("hair", -999)
	assert_int(cc.get_part_option("hair")).is_equal(0)  # clamped to first
	cc.queue_free()


# ---------------------------------------------------------------------------
# COLOR
# ---------------------------------------------------------------------------

func test_set_part_color() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1", "h2"])
	assert_color(cc.get_part_color("hair")).is_equal(Color.WHITE)

	cc.set_part_color("hair", Color.RED)
	assert_color(cc.get_part_color("hair")).is_equal(Color.RED)
	cc.queue_free()


func test_part_color_nonexistent() -> void:
	var cc := _make_cc()
	assert_color(cc.get_part_color("ghost")).is_equal(Color.WHITE)
	cc.queue_free()


# ---------------------------------------------------------------------------
# SIGNALS
# ---------------------------------------------------------------------------

func test_part_changed_signal_on_option() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1", "h2", "h3"])

	var emitted := false
	var part_name := ""
	cc.part_changed.connect(func(n): emitted = true; part_name = n)

	cc.set_part_option("hair", 1)
	assert_bool(emitted).is_true()
	assert_str(part_name).is_equal("hair")
	cc.queue_free()


func test_part_changed_signal_on_color() -> void:
	var cc := _make_cc()
	cc.add_part("eyes", ["e1"])

	var emitted := false
	cc.part_changed.connect(func(_n): emitted = true)

	cc.set_part_color("eyes", Color.BLUE)
	assert_bool(emitted).is_true()
	cc.queue_free()


func test_part_changed_no_duplicate_signal() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1", "h2"])

	var count := 0
	cc.part_changed.connect(func(_n): count += 1)

	cc.set_part_option("hair", 0)  # já é 0 — não deve emitir
	assert_int(count).is_equal(0)

	cc.set_part_color("hair", Color.WHITE)  # já é WHITE — não deve emitir
	assert_int(count).is_equal(0)
	cc.queue_free()


# ---------------------------------------------------------------------------
# CHARACTER DATA IMPORT/EXPORT
# ---------------------------------------------------------------------------

func test_get_character_data() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1", "h2"])
	cc.add_part("eyes", ["e1"])

	cc.set_part_option("hair", 1)
	cc.set_part_color("hair", Color.BLUE)

	var data := cc.get_character_data()
	assert_bool(data.has("hair")).is_true()
	assert_bool(data.has("eyes")).is_true()
	assert_int(data["hair"]["option"]).is_equal(1)
	cc.queue_free()


func test_load_character_data() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1", "h2", "h3"])
	cc.add_part("eyes", ["e1", "e2"])

	var data := {
		"hair": {"option": 2, "color": {"r": 0.0, "g": 1.0, "b": 0.0, "a": 1.0}},
		"eyes": {"option": 0, "color": {"r": 0.0, "g": 0.0, "b": 1.0, "a": 1.0}},
		"unknown_part": {"option": 0, "color": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}}
	}
	assert_bool(cc.load_character_data(data)).is_true()

	assert_int(cc.get_part_option("hair")).is_equal(2)
	assert_color(cc.get_part_color("hair")).is_equal(Color.GREEN)
	assert_int(cc.get_part_option("eyes")).is_equal(0)
	assert_color(cc.get_part_color("eyes")).is_equal(Color.BLUE)
	cc.queue_free()


func test_load_character_data_empty() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1"])
	assert_bool(cc.load_character_data({})).is_false()
	cc.queue_free()


# ---------------------------------------------------------------------------
# PRESET SAVE / LOAD / DELETE
# ---------------------------------------------------------------------------

func test_preset_save_and_load() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1", "h2", "h3"])
	cc.add_part("eyes", ["e1", "e2"])
	cc.set_part_option("hair", 2)
	cc.set_part_color("hair", Color.RED)

	assert_bool(cc.save_preset("test_char")).is_true()

	# Modifica estado
	cc.set_part_option("hair", 0)
	cc.set_part_color("hair", Color.BLUE)

	# Carrega preset
	assert_bool(cc.load_preset("test_char")).is_true()
	assert_int(cc.get_part_option("hair")).is_equal(2)
	assert_color(cc.get_part_color("hair")).is_equal(Color.RED)

	# Limpeza
	cc.delete_preset("test_char")
	cc.queue_free()


func test_preset_signal() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1"])

	var saved_name := ""
	var loaded_name := ""
	cc.saved.connect(func(n): saved_name = n)
	cc.loaded.connect(func(n): loaded_name = n)

	cc.save_preset("sig_test")
	assert_str(saved_name).is_equal("sig_test")

	cc.set_part_option("hair", 0)
	cc.load_preset("sig_test")
	assert_str(loaded_name).is_equal("sig_test")

	cc.delete_preset("sig_test")
	cc.queue_free()


func test_preset_nonexistent() -> void:
	var cc := _make_cc()
	assert_bool(cc.load_preset("does_not_exist_xyz")).is_false()
	cc.queue_free()


func test_delete_nonexistent_preset() -> void:
	var cc := _make_cc()
	assert_bool(cc.delete_preset("does_not_exist")).is_false()
	cc.queue_free()


func test_get_preset_names() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1"])

	# Lista inicial vazia
	assert_array(cc.get_preset_names()).is_empty()

	cc.save_preset("p1")
	cc.save_preset("p2")

	var names := cc.get_preset_names()
	assert_bool(names.has("p1")).is_true()
	assert_bool(names.has("p2")).is_true()

	cc.delete_preset("p1")
	cc.delete_preset("p2")
	cc.queue_free()


# ---------------------------------------------------------------------------
# RANDOMIZE
# ---------------------------------------------------------------------------

func test_randomize_character() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1", "h2", "h3"])
	cc.add_part("eyes", ["e1", "e2"])

	cc.randomize_character()

	# Valores devem estar dentro dos ranges válidos
	assert_bool(cc.get_part_option("hair") >= 0).is_true()
	assert_bool(cc.get_part_option("hair") < 3).is_true()
	assert_bool(cc.get_part_option("eyes") >= 0).is_true()
	assert_bool(cc.get_part_option("eyes") < 2).is_true()
	cc.queue_free()


func test_randomize_empty_parts() -> void:
	var cc := _make_cc()
	cc.randomize_character()  # no-op, sem crash
	assert_int(cc.get_part_names().size()).is_equal(0)
	cc.queue_free()


# ---------------------------------------------------------------------------
# RESET TO DEFAULTS
# ---------------------------------------------------------------------------

func test_reset_to_defaults() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1", "h2", "h3"])
	cc.add_part("eyes", ["e1"])

	cc.set_part_option("hair", 2)
	cc.set_part_color("hair", Color.RED)
	cc.set_part_color("eyes", Color.BLUE)

	cc.reset_to_defaults()

	assert_int(cc.get_part_option("hair")).is_equal(0)
	assert_int(cc.get_part_option("eyes")).is_equal(0)
	assert_color(cc.get_part_color("hair")).is_equal(Color.WHITE)
	assert_color(cc.get_part_color("eyes")).is_equal(Color.WHITE)
	cc.queue_free()


# ---------------------------------------------------------------------------
# EDGE CASES
# ---------------------------------------------------------------------------

func test_nonexistent_part_option() -> void:
	var cc := _make_cc()
	assert_int(cc.get_part_option("ghost")).is_equal(-1)
	cc.queue_free()


func test_nonexistent_part_options_array() -> void:
	var cc := _make_cc()
	assert_array(cc.get_part_options("ghost")).is_empty()
	cc.queue_free()


func test_empty_part_name() -> void:
	var cc := _make_cc()
	assert_bool(cc.add_part("", ["a"])).is_false()
	assert_int(cc.get_part_names().size()).is_equal(0)
	cc.queue_free()


func test_save_preset_empty_name() -> void:
	var cc := _make_cc()
	cc.add_part("hair", ["h1"])
	assert_bool(cc.save_preset("")).is_false()
	cc.queue_free()


func test_load_preset_empty_name() -> void:
	var cc := _make_cc()
	assert_bool(cc.load_preset("")).is_false()
	cc.queue_free()


func test_color_palette_fallback() -> void:
	var cc := _make_cc()
	cc.color_palette = PackedColorArray()  # força fallback
	assert_bool(not cc.color_palette.is_empty())  # setter garante WHITE
	cc.add_part("hair", ["h1"])
	assert_color(cc.get_part_color("hair")).is_equal(Color.WHITE)
	cc.queue_free()


func test_set_part_option_noop() -> void:
	"""PADRÃO 10: same-state transition não deve emitir sinal."""
	var cc := _make_cc()
	cc.add_part("hair", ["h1", "h2", "h3"])
	cc.set_part_option("hair", 2)

	var emitted := false
	cc.part_changed.connect(func(_n): emitted = true)

	cc.set_part_option("hair", 2)  # mesmo valor
	assert_bool(emitted).is_false()
	cc.queue_free()
