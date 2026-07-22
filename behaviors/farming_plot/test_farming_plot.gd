extends GdUnitTestSuite
func test_plant() -> void: var f:=FarmingPlot.new(); f.plant("wheat"); assert_bool(f.is_planted()).is_true(); f.queue_free()
func test_growth() -> void: var f:=FarmingPlot.new(); f.growth_time=3.0; f.stages=3; f.plant("corn"); f._process(3.0); assert_int(f.get_stage()).is_equal(3); f.queue_free()
func test_harvest() -> void: var f:=FarmingPlot.new(); f.growth_time=1.0; f.stages=1; f.plant("tomato"); f._process(2.0); assert_str(f.harvest()).is_equal("tomato"); f.queue_free()
