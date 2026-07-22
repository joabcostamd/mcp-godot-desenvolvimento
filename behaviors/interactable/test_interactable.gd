## test_interactable.gd — GdUnit4.

extends GdUnitTestSuite

func _make_ia() -> Interactable: return Interactable.new()

func test_defaults() -> void:
	var ia := _make_ia()
	assert_str(ia.prompt_text).is_equal("")
	assert_str(ia.player_group).is_equal("players")
	assert_float(ia.hold_duration).is_equal(0); ia.queue_free()

func test_focus_on_player_enter() -> void:
	var ia := _make_ia(); add_child(ia)
	var body := Node2D.new(); body.add_to_group("players")
	var focused := false
	ia.focused.connect(func(_b): focused = true)
	ia._on_enter(body)
	assert_bool(focused).is_true()
	assert_object(ia.get_focused_body()).is_not_null()
	body.queue_free(); remove_child(ia); ia.queue_free()

func test_ignore_non_player() -> void:
	var ia := _make_ia(); add_child(ia)
	var body := Node2D.new()  # sem grupo
	ia._on_enter(body)
	assert_object(ia.get_focused_body()).is_null()
	body.queue_free(); remove_child(ia); ia.queue_free()

func test_unfocus_on_exit() -> void:
	var ia := _make_ia(); add_child(ia)
	var body := Node2D.new(); body.add_to_group("players")
	ia._on_enter(body)
	ia._on_exit(body)
	assert_object(ia.get_focused_body()).is_null()
	body.queue_free(); remove_child(ia); ia.queue_free()

func test_interact_emits_signal() -> void:
	var ia := _make_ia(); add_child(ia)
	var body := Node2D.new(); body.add_to_group("players")
	ia._on_enter(body)
	var emitted := false
	ia.interacted.connect(func(_b): emitted = true)
	Input.action_press("ui_accept")
	ia._physics_process(0.1)
	Input.action_release("ui_accept")
	assert_bool(emitted).is_true()
	body.queue_free(); remove_child(ia); ia.queue_free()

func test_hold_duration() -> void:
	var ia := _make_ia(); ia.hold_duration = 0.5; add_child(ia)
	var body := Node2D.new(); body.add_to_group("players")
	ia._on_enter(body)
	var emitted := false
	ia.interacted.connect(func(_b): emitted = true)
	Input.action_press("ui_accept")
	ia._physics_process(0.3)  # abaixo do hold
	assert_bool(emitted).is_false()
	ia._physics_process(0.3)  # passa do hold
	assert_bool(emitted).is_true()
	Input.action_release("ui_accept")
	body.queue_free(); remove_child(ia); ia.queue_free()
