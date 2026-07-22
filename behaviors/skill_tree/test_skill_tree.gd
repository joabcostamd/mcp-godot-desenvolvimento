## test_skill_tree.gd — Testes do SkillTree | GdUnit4.
## Cobre add_node, unlock, prerequisitos, custo, reset, bonuses, sinais.

extends GdUnitTestSuite

func _make_st() -> SkillTree:
	return SkillTree.new()


func test_default_parameters() -> void:
	var st := _make_st()
	assert_int(st.available_points).is_equal(0)
	assert_int(st.get_total_spent()).is_equal(0)
	st.queue_free()


func test_add_node() -> void:
	var st := _make_st()
	st.add_node("fireball", "Bola de Fogo", 3)
	assert_bool(st._nodes.has("fireball")).is_true()
	st.queue_free()


func test_unlock_spends_points() -> void:
	var st := _make_st()
	st.available_points = 5
	st.add_node("str1", "Forca I", 3)
	assert_bool(st.unlock_node("str1")).is_true()
	assert_int(st.available_points).is_equal(2)
	assert_int(st.get_total_spent()).is_equal(3)
	st.queue_free()


func test_unlock_fails_without_points() -> void:
	var st := _make_st()
	st.available_points = 1
	st.add_node("expensive", "Caro", 5)
	assert_bool(st.unlock_node("expensive")).is_false()
	assert_int(st.available_points).is_equal(1)
	st.queue_free()


func test_unlock_fails_if_already_unlocked() -> void:
	var st := _make_st()
	st.available_points = 5
	st.add_node("str1", "Forca", 2)
	st.unlock_node("str1")
	assert_bool(st.unlock_node("str1")).is_false()
	st.queue_free()


func test_unlock_fails_nonexistent_node() -> void:
	var st := _make_st()
	st.available_points = 5
	assert_bool(st.unlock_node("ghost")).is_false()
	st.queue_free()


func test_prerequisite_required() -> void:
	var st := _make_st()
	st.available_points = 5
	st.add_node("str1", "Forca I", 2)
	st.add_node("str2", "Forca II", 3, ["str1"])
	assert_bool(st.can_unlock("str2")).is_false()  # str1 nao desbloqueado
	assert_bool(st.unlock_node("str2")).is_false()
	st.unlock_node("str1")
	assert_bool(st.can_unlock("str2")).is_true()
	assert_bool(st.unlock_node("str2")).is_true()
	st.queue_free()


func test_is_unlocked() -> void:
	var st := _make_st()
	st.available_points = 3
	st.add_node("a", "A", 1)
	assert_bool(st.is_unlocked("a")).is_false()
	st.unlock_node("a")
	assert_bool(st.is_unlocked("a")).is_true()
	st.queue_free()


func test_reset_refunds_all_points() -> void:
	var st := _make_st()
	st.available_points = 10
	st.add_node("a", "A", 3)
	st.add_node("b", "B", 4)
	st.unlock_node("a")
	st.unlock_node("b")
	assert_int(st.available_points).is_equal(3)
	st.reset_tree()
	assert_int(st.available_points).is_equal(10)
	assert_int(st.get_total_spent()).is_equal(0)
	assert_bool(st.is_unlocked("a")).is_false()
	assert_bool(st.is_unlocked("b")).is_false()
	st.queue_free()


func test_add_points() -> void:
	var st := _make_st()
	st.add_points(5)
	assert_int(st.available_points).is_equal(5)
	st.add_points(-3)  # negativo = 0
	assert_int(st.available_points).is_equal(5)
	st.queue_free()


func test_node_unlocked_signal() -> void:
	var st := _make_st()
	st.available_points = 3
	st.add_node("a", "A", 1)
	var emitted := false
	var node_id := ""
	st.node_unlocked.connect(func(id): emitted = true; node_id = id)
	st.unlock_node("a")
	assert_bool(emitted).is_true()
	assert_str(node_id).is_equal("a")
	st.queue_free()


func test_tree_reset_signal() -> void:
	var st := _make_st()
	st.available_points = 2
	st.add_node("a", "A", 1)
	st.unlock_node("a")
	var emitted := false
	st.tree_reset.connect(func(): emitted = true)
	st.reset_tree()
	assert_bool(emitted).is_true()
	st.queue_free()


func test_points_changed_signal() -> void:
	var st := _make_st()
	var emitted := false
	var pts := -1
	st.points_changed.connect(func(p): emitted = true; pts = p)
	st.available_points = 7
	assert_bool(emitted).is_true()
	assert_int(pts).is_equal(7)
	st.queue_free()


func test_get_unlocked_nodes() -> void:
	var st := _make_st()
	st.available_points = 5
	st.add_node("a", "A", 1)
	st.add_node("b", "B", 1)
	st.unlock_node("a")
	var unlocked := st.get_unlocked_nodes()
	assert_int(unlocked.size()).is_equal(1)
	assert_str(unlocked[0]).is_equal("a")
	# Modificar copia nao afeta original
	unlocked.clear()
	assert_int(st.get_unlocked_nodes().size()).is_equal(1)
	st.queue_free()


func test_bonuses_applied() -> void:
	var parent := Node2D.new()
	add_child(parent)
	var stats := CharacterStats.new()
	parent.add_child(stats)
	var st := _make_st()
	st.available_points = 5
	parent.add_child(st)

	st.add_node("str_boost", "Forca", 2, [], {"strength": 10})
	st.unlock_node("str_boost")

	assert_int(stats.get_stat("strength")).is_greater(10)  # 10 + 10% = 11

	remove_child(parent)
	parent.queue_free()
	stats.queue_free()
	st.queue_free()


func test_cannot_unlock_without_deps() -> void:
	var st := _make_st()
	st.available_points = 10
	st.add_node("root", "Raiz", 2)
	st.add_node("child", "Filho", 3, ["root", "missing"])
	assert_bool(st.can_unlock("child")).is_false()
	st.unlock_node("root")
	assert_bool(st.can_unlock("child")).is_false()  # "missing" nao existe
	st.queue_free()
