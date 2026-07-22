extends GdUnitTestSuite
func test_play_sequence() -> void:
	var cs:=CameraSequence.new(); cs.shots=[{"target":"a"},{"target":"b"}]
	var count:=0; cs.shot_changed.connect(func(_i): count+=1); cs.play()
	assert_int(count).is_equal(1); cs.queue_free()
func test_end_after_all_shots() -> void:
	var cs:=CameraSequence.new(); cs.shots=[{"target":"a"}]
	var e:=false; cs.sequence_finished.connect(func(): e=true)
	cs.play(); cs.next_shot(); assert_bool(e).is_true(); cs.queue_free()
func test_stop() -> void:
	var cs:=CameraSequence.new(); cs.shots=[{"target":"a"}]; cs.play(); cs.stop()
	assert_bool(cs.is_playing()).is_false(); cs.queue_free()
