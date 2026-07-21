extends GdUnitTestSuite
func test_add_recipe() -> void:
	var cr:=Crafting.new(); add_child(cr); cr.add_recipe("potion","health_potion",1,{"herb":2})
	assert_bool(cr.can_craft("potion")).is_false()  # sem inventory
	remove_child(cr); cr.queue_free()
