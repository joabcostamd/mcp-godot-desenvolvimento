## test_crafting.gd — Testes do Crafting | GdUnit4.

extends GdUnitTestSuite

func _make_cr() -> Crafting: return Crafting.new()

func test_add_recipe_unlocks() -> void:
	var cr := _make_cr(); add_child(cr)
	var unlocked := false
	cr.recipe_unlocked.connect(func(_id): unlocked = true)
	cr.add_recipe("potion", "heal", 1, {"herb": 2})
	assert_bool(unlocked).is_true()
	remove_child(cr); cr.queue_free()

func test_add_recipe_locked() -> void:
	var cr := _make_cr(); add_child(cr)
	cr.add_recipe("secret", "elixir", 1, {"herb": 5}, false)
	assert_bool(cr.can_craft("secret")).is_false()
	remove_child(cr); cr.queue_free()

func test_unlock_recipe() -> void:
	var cr := _make_cr(); add_child(cr)
	cr.add_recipe("potion", "heal", 1, {"herb": 2}, false)
	assert_bool(cr.can_craft("potion")).is_false()
	cr.unlock_recipe("potion")
	remove_child(cr); cr.queue_free()

func test_craft_fails_without_inventory() -> void:
	var cr := _make_cr(); add_child(cr)
	cr.add_recipe("potion", "heal", 1, {"herb": 2})
	assert_bool(cr.craft("potion")).is_false()
	remove_child(cr); cr.queue_free()

func test_craft_locked_fails() -> void:
	var cr := _make_cr(); add_child(cr)
	cr.add_recipe("secret", "elixir", 1, {"herb": 5}, false)
	assert_bool(cr.craft("secret")).is_false()
	remove_child(cr); cr.queue_free()

func test_craft_nonexistent_fails() -> void:
	var cr := _make_cr(); add_child(cr)
	assert_bool(cr.craft("ghost")).is_false()
	remove_child(cr); cr.queue_free()

func test_can_craft_false_without_inventory() -> void:
	var cr := _make_cr(); add_child(cr)
	cr.add_recipe("potion", "heal", 1, {"herb": 2})
	assert_bool(cr.can_craft("potion")).is_false()
	remove_child(cr); cr.queue_free()

func test_get_recipes_returns_copy() -> void:
	var cr := _make_cr(); add_child(cr)
	cr.add_recipe("a", "out_a", 1, {"x": 1})
	var recipes := cr.get_recipes(); recipes.clear()
	assert_bool(cr.get_recipes().has("a")).is_true()
	remove_child(cr); cr.queue_free()

func test_signal_recipe_unlocked() -> void:
	var cr := _make_cr(); add_child(cr)
	var emitted := false
	cr.recipe_unlocked.connect(func(_id): emitted = true)
	cr.add_recipe("test", "out", 1, {"x": 1})
	assert_bool(emitted).is_true()
	remove_child(cr); cr.queue_free()

func test_unlock_nonexistent_no_crash() -> void:
	var cr := _make_cr(); add_child(cr)
	cr.unlock_recipe("ghost")  # não crasha
	assert_bool(true).is_true()
	remove_child(cr); cr.queue_free()
