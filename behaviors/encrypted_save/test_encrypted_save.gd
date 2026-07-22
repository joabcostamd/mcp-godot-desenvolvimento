extends GdUnitTestSuite
func test_save_load() -> void: var e:=EncryptedSave.new(); e.save_encrypted("user://test_enc.cfg",{"hp":100}); var d:=e.load_encrypted("user://test_enc.cfg"); DirAccess.remove_absolute("user://test_enc.cfg"); e.queue_free()

func test_edge_case_multiple_instances() -> void:
	var a := EncryptedSave.new()
	var b := EncryptedSave.new()
	assert_object(a).is_not_null()
	assert_object(b).is_not_null()
	a.queue_free()
	b.queue_free()

func test_integration_add_child() -> void:
	var c := EncryptedSave.new()
	add_child(c)
	# Deve inicializar sem crash quando adicionado a arvore
	assert_bool(c.is_inside_tree()).is_true()
	remove_child(c)
	c.queue_free()
