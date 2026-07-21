## test_wind_zone.gd
extends GdUnitTestSuite
func test_no_crash() -> void:
	var wz := WindZone.new(); add_child(wz); wz._physics_process(0.1); remove_child(wz); wz.queue_free()
