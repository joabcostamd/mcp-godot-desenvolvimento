extends GdUnitTestSuite
func test_start_stop() -> void:
	var bt:=BehaviorTree.new(); bt.start(); assert_bool(bt.is_running()).is_true()
	bt.stop(); assert_bool(bt.is_running()).is_false(); bt.queue_free()
func test_sequence_all_success() -> void:
	var bt:=BehaviorTree.new(); bt.tree_data=[{"type":"sequence","name":"root","children":[{"type":"action","name":"a"},{"type":"action","name":"b"}]}]
	var results:=[]; bt.node_executed.connect(func(n,s): results.append({"n":n,"s":s}))
	bt._tick()
	assert_bool(results.size()>=2).is_true(); bt.queue_free()
func test_selector_first_success() -> void:
	var bt:=BehaviorTree.new(); bt.tree_data=[{"type":"selector","name":"root","children":[{"type":"action","name":"first"},{"type":"action","name":"second"}]}]
	var results:=[]; bt.node_executed.connect(func(n,s): results.append({"n":n,"s":s}))
	bt._tick(); assert_int(results.size()).is_equal(2); bt.queue_free()
