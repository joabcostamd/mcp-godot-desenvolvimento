## test_dissolve.gd — Testes do Dissolve | GdUnit4.

extends GdUnitTestSuite

func _make_d() -> Dissolve: return Dissolve.new()

func test_default_parameters() -> void:
	var d := _make_d()
	assert_float(d.edge_width).is_equal(0.1)
	d.queue_free()

func test_set_progress() -> void:
	var d := _make_d()
	d.set_progress(0.5)
	assert_float(d._progress).is_equal(0.5)
	d.queue_free()

func test_progress_clamped() -> void:
	var d := _make_d()
	d.set_progress(-0.5)
	assert_float(d._progress).is_equal(0.0)
	d.set_progress(2.0)
	assert_float(d._progress).is_equal(1.0)
	d.queue_free()

func test_dissolve_finished_signal() -> void:
	var d := _make_d()
	var finished := false
	d.dissolve_finished.connect(func(): finished = true)
	d.set_progress(1.0)
	assert_bool(finished).is_true()
	d.queue_free()

func test_dissolve_not_finished_at_partial() -> void:
	var d := _make_d()
	var finished := false
	d.dissolve_finished.connect(func(): finished = true)
	d.set_progress(0.99)
	assert_bool(finished).is_false()
	d.queue_free()

func test_edge_width_clamped() -> void:
	var d := _make_d()
	d.edge_width = -0.5; assert_float(d.edge_width).is_equal(0.0)
	d.edge_width = 2.0; assert_float(d.edge_width).is_equal(0.5)
	d.queue_free()

func test_no_parent_does_not_crash() -> void:
	var d := _make_d()
	d.set_progress(0.5)  # sem parent CanvasItem
	assert_bool(true).is_true()
	d.queue_free()
