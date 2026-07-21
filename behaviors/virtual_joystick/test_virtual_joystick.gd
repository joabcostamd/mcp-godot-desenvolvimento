extends GdUnitTestSuite
func test_defaults() -> void: var v:=VirtualJoystick.new(); assert_float(v.radius).is_equal(80.0); v.queue_free()
func test_release() -> void: var v:=VirtualJoystick.new(); var e:=false; v.joystick_released.connect(func(): e=true); v._input(create_touch(false)); assert_bool(e).is_true(); v.queue_free()
func create_touch(pressed: bool) -> InputEventScreenTouch: var ev:=InputEventScreenTouch.new(); ev.pressed=pressed; return ev
