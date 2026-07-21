## test_health_bar.gd — Testes do behavior HealthBar | GdUnit4.

extends GdUnitTestSuite


func _make_hb() -> HealthBar:
	return HealthBar.new()


func test_script_compiles() -> void:
	var hb := HealthBar.new(); assert_object(hb).is_not_null(); hb.queue_free()


func test_creates_visuals() -> void:
	var hb := _make_hb(); add_child(hb)
	assert_object(hb.get_node_or_null("Background")).is_not_null()
	assert_object(hb.get_node_or_null("Fill")).is_not_null()
	remove_child(hb); hb.queue_free()


func test_finds_sibling_health() -> void:
	var parent := Node2D.new(); add_child(parent)
	var health := Health.new(); health.max_hp = 100; health.current_hp = 50
	parent.add_child(health)
	var hb := _make_hb(); parent.add_child(hb)
	assert_object(hb._health).is_not_null()
	remove_child(parent); parent.queue_free()


func test_show_text_creates_label() -> void:
	var hb := _make_hb(); hb.show_text = true; add_child(hb)
	assert_object(hb.get_node_or_null("HPLabel")).is_not_null()
	remove_child(hb); hb.queue_free()
