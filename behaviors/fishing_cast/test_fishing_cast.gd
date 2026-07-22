extends GdUnitTestSuite
func test_cast() -> void: var f:=FishingCast.new(); var e:=false; f.cast.connect(func(_p): e=true); f.start_cast(); assert_bool(e).is_true(); f.queue_free()
func test_catch() -> void: var f:=FishingCast.new(); f.start_cast(); var e:=false; f.caught.connect(func(_id): e=true); f.catch_fish("salmon"); assert_bool(e).is_true(); assert_bool(f.is_casting()).is_false(); f.queue_free()
func test_bite() -> void: var f:=FishingCast.new(); f.start_cast(); var e:=false; f.bite.connect(func(): e=true); f.on_bite(); assert_bool(e).is_true(); f.queue_free()
