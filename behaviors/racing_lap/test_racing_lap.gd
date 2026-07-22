extends GdUnitTestSuite
func test_start() -> void: var r:=RacingLap.new(); r.start_race(); assert_bool(r._race_started).is_true(); r.queue_free()
func test_lap() -> void: var r:=RacingLap.new(); r.total_laps=2; r.start_race(); r.complete_lap(); assert_int(r.get_current_lap()).is_equal(1); r.complete_lap(); assert_int(r.get_current_lap()).is_equal(2); r.queue_free()
func test_elapsed() -> void: var r:=RacingLap.new(); r.start_race(); r._process(1.0); assert_float(r.get_elapsed()).is_equal(1.0); r.queue_free()
