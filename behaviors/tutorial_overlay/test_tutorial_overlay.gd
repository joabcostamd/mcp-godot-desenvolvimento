extends GdUnitTestSuite
func test_start() -> void: var t:=TutorialOverlay.new(); t.steps=[{"text":"a"},{"text":"b"}]; t.start(); assert_bool(t._active).is_true(); t.queue_free()
func test_finish() -> void: var t:=TutorialOverlay.new(); t.steps=[{"text":"a"}]; var e:=false; t.tutorial_finished.connect(func(): e=true); t.start(); t.next_step(); t.next_step(); assert_bool(e).is_true(); t.queue_free()
