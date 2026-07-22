## test_quest.gd — Testes do behavior Quest | GdUnit4.

extends GdUnitTestSuite


func _make_quest(quests := []) -> Quest:
	var q := Quest.new()
	q.quests = quests.duplicate(true)
	return q


func _make_inventory(slots := 10) -> Inventory:
	var inv := Inventory.new()
	inv.slot_count = slots
	return inv


func _make_currency(ctype := "gold") -> Currency:
	var c := Currency.new()
	c.currency_type = ctype
	return c


func _sample_quest() -> Dictionary:
	return {
		"id": "q1",
		"name": "Collect 3 Swords",
		"objectives": [
			{"type": "collect", "target_id": "sword", "required": 3}
		],
		"rewards": [
			{"type": "currency", "target_id": "gold", "quantity": 100}
		]
	}


func _spend_quest() -> Dictionary:
	return {
		"id": "q2",
		"name": "Spend 50 Gold",
		"objectives": [
			{"type": "spend", "target_id": "gold", "required": 50}
		],
		"rewards": [
			{"type": "item", "target_id": "medal", "quantity": 1}
		]
	}


# ── start_quest ───────────────────────────────────────────────────────────────

func test_start_quest_success() -> void:
	var root := Node.new()
	add_child(root)
	var q := _make_quest([_sample_quest()])
	var inv := _make_inventory()
	var cur := _make_currency()
	root.add_child(inv)
	root.add_child(cur)
	root.add_child(q)
	assert_bool(q.start_quest("q1")).is_true()
	assert_bool(q.is_active("q1")).is_true()
	root.queue_free()


func test_start_quest_twice_fails() -> void:
	var q := _make_quest([_sample_quest()])
	add_child(q)
	q.start_quest("q1")
	assert_bool(q.start_quest("q1")).is_false()


func test_start_quest_invalid_id() -> void:
	var q := _make_quest([_sample_quest()])
	add_child(q)
	assert_bool(q.start_quest("nonexistent")).is_false()
	assert_bool(q.start_quest("")).is_false()


func test_start_quest_emits_signal() -> void:
	var q := _make_quest([_sample_quest()])
	add_child(q)
	var emitted := ""
	q.quest_started.connect(func(id): emitted = id)
	q.start_quest("q1")
	assert_str(emitted).is_equal("q1")


# ── Progress with Inventory ───────────────────────────────────────────────────

func test_collect_objective_progresses() -> void:
	var root := Node.new()
	add_child(root)
	var inv := _make_inventory()
	var cur := _make_currency()
	var q := _make_quest([_sample_quest()])
	root.add_child(inv)
	root.add_child(cur)
	root.add_child(q)
	q.start_quest("q1")
	inv.add_item("sword", 2)
	var prog := q.get_progress("q1")
	var objs := prog.objectives as Array
	assert_int((objs[0] as Dictionary).current).is_equal(2)
	root.queue_free()


func test_collect_objective_completes_quest() -> void:
	var root := Node.new()
	add_child(root)
	var inv := _make_inventory()
	var cur := _make_currency()
	var q := _make_quest([_sample_quest()])
	root.add_child(inv)
	root.add_child(cur)
	root.add_child(q)
	var completed := ""
	q.quest_completed.connect(func(id): completed = id)
	q.start_quest("q1")
	inv.add_item("sword", 3)
	assert_str(completed).is_equal("q1")
	assert_bool(q.is_completed("q1")).is_true()
	root.queue_free()


# ── Progress with Currency ────────────────────────────────────────────────────

func test_spend_objective_progresses() -> void:
	var root := Node.new()
	add_child(root)
	var inv := _make_inventory()
	var cur := _make_currency("gold")
	cur.amount = 200
	var q := _make_quest([_spend_quest()])
	root.add_child(inv)
	root.add_child(cur)
	root.add_child(q)
	q.start_quest("q2")
	cur.spend(30)
	var prog := q.get_progress("q2")
	var objs := prog.objectives as Array
	assert_int((objs[0] as Dictionary).current).is_equal(30)
	root.queue_free()


func test_spend_objective_completes_quest() -> void:
	var root := Node.new()
	add_child(root)
	var inv := _make_inventory()
	var cur := _make_currency("gold")
	cur.amount = 200
	var q := _make_quest([_spend_quest()])
	root.add_child(inv)
	root.add_child(cur)
	root.add_child(q)
	var completed := ""
	q.quest_completed.connect(func(id): completed = id)
	q.start_quest("q2")
	cur.spend(60)
	assert_str(completed).is_equal("q2")
	root.queue_free()


# ── Rewards ───────────────────────────────────────────────────────────────────

func test_quest_rewards_currency() -> void:
	var root := Node.new()
	add_child(root)
	var inv := _make_inventory()
	var cur := _make_currency()
	var q := _make_quest([_sample_quest()])
	root.add_child(inv)
	root.add_child(cur)
	root.add_child(q)
	q.start_quest("q1")
	inv.add_item("sword", 3)
	assert_int(cur.get_amount()).is_equal(100)
	root.queue_free()


func test_quest_rewards_item() -> void:
	var root := Node.new()
	add_child(root)
	var inv := _make_inventory()
	var cur := _make_currency("gold")
	cur.amount = 200
	var q := _make_quest([_spend_quest()])
	root.add_child(inv)
	root.add_child(cur)
	root.add_child(q)
	q.start_quest("q2")
	cur.spend(50)
	assert_int(inv.get_item_count("medal")).is_equal(1)
	root.queue_free()


# ── Edge cases ────────────────────────────────────────────────────────────────

func test_completed_quest_cannot_restart() -> void:
	var root := Node.new()
	add_child(root)
	var inv := _make_inventory()
	var cur := _make_currency()
	var q := _make_quest([_sample_quest()])
	root.add_child(inv)
	root.add_child(cur)
	root.add_child(q)
	q.start_quest("q1")
	inv.add_item("sword", 3)
	assert_bool(q.start_quest("q1")).is_false()
	root.queue_free()


func test_no_dependencies_no_crash() -> void:
	var q := _make_quest([_sample_quest()])
	add_child(q)
	assert_bool(q.start_quest("q1")).is_true()
