extends GdUnitTestSuite
func test_defaults() -> void: var o:=PatchSystem.new(); o.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := PatchSystem.new()
	var b := PatchSystem.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()

func test_integration_add_child() -> void:
	var c := PatchSystem.new()
	add_child(c)
	# Deve inicializar sem crash quando adicionado a arvore
	assert_bool(c.is_inside_tree()).is_true()
	remove_child(c)
	c.queue_free()
