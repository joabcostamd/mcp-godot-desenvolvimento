extends GdUnitTestSuite
func test_can_claim() -> void:
	var dr:=DailyReward.new(); dr._claimed_today=false; dr._last_claim_date=""
	assert_bool(dr.can_claim()).is_true(); dr.queue_free()
func test_claim_first_day() -> void:
	var dr:=DailyReward.new(); dr.rewards=[{"id":"gold","quantity":100}]
	dr._last_claim_date="2024-01-01"; dr._claimed_today=false
	var r:=dr.claim()
	assert_int(dr.get_streak()).is_equal(1); dr.queue_free()
func test_streak_reset() -> void:
	var dr:=DailyReward.new(); dr._streak=5; dr.reset_streak()
	assert_int(dr.get_streak()).is_equal(0); dr.queue_free()
