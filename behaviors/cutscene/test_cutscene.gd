extends GdUnitTestSuite
func test_play_emits_started() -> void:
	var c:=Cutscene.new(); var s:=false; c.cutscene_started.connect(func(): s=true)
	c.add_step({}); c.play(); assert_bool(s).is_true(); c.queue_free()
func test_ends_after_steps() -> void:
	var c:=Cutscene.new(); var e:=false; c.cutscene_ended.connect(func(): e=true)
	c.add_step({}); c.play(); c.next_step(); assert_bool(e).is_true(); c.queue_free()
func test_skip() -> void:
	var c:=Cutscene.new(); var e:=false; c.cutscene_ended.connect(func(): e=true)
	c.add_step({}); c.play(); c.skip(); assert_bool(e).is_true(); assert_bool(c.is_playing()).is_false(); c.queue_free()
