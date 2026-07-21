extends GdUnitTestSuite
func test_update_progress() -> void:
	var at:=AchievementTracker.new(); at.achievements=[{"id":"kill_10","target":10.0}]
	at.update_progress("kill_10",5.0)
	assert_float(at.get_progress("kill_10")).is_equal(0.5); at.queue_free()
func test_unlock() -> void:
	var at:=AchievementTracker.new(); at.achievements=[{"id":"test","target":1.0}]
	var emitted:=false; at.unlocked.connect(func(_id): emitted=true)
	at.update_progress("test",1.0)
	assert_bool(emitted).is_true(); assert_bool(at.is_unlocked("test")).is_true(); at.queue_free()
func test_cant_reunlock() -> void:
	var at:=AchievementTracker.new(); at.achievements=[{"id":"once","target":1.0}]
	at.update_progress("once",2.0); var count:=0
	at.unlocked.connect(func(_id): count+=1); at.update_progress("once",5.0)
	assert_int(count).is_equal(0); at.queue_free()
