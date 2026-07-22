extends GdUnitTestSuite
func test_submit() -> void:
	var lb:=Leaderboard.new(); lb.submit_score("A",100); lb.submit_score("B",200)
	assert_int(lb.get_entries().size()).is_equal(2); lb.queue_free()
func test_top_order() -> void:
	var lb:=Leaderboard.new(); lb.submit_score("A",100); lb.submit_score("B",200)
	var top:=lb.get_top(1); assert_int(top[0].score).is_equal(200); lb.queue_free()
func test_max_entries() -> void:
	var lb:=Leaderboard.new(); lb.max_entries=3
	for i in 5: lb.submit_score("P%d"%i,i*10)
	assert_int(lb.get_entries().size()).is_equal(3); lb.queue_free()
