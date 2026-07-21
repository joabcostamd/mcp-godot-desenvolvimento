extends GdUnitTestSuite
func _make_rl() -> RandomLoot:
	var rl:=RandomLoot.new(); rl.loot_table=[{"id":"sword","weight":5.0},{"id":"shield","weight":3.0,"rarity":"rare"}]; return rl
func test_roll_returns_item() -> void:
	var rl:=_make_rl(); var id:=rl.roll(); assert_bool(id in["sword","shield"]).is_true(); rl.queue_free()
func test_empty_table() -> void:
	var rl:=RandomLoot.new(); assert_str(rl.roll()).is_equal(""); rl.queue_free()
func test_signals() -> void:
	var rl:=_make_rl(); var dropped:=false; rl.loot_dropped.connect(func(_id): dropped=true); rl.roll(); assert_bool(dropped).is_true(); rl.queue_free()
