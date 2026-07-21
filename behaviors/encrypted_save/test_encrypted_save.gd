extends GdUnitTestSuite
func test_save_load() -> void: var e:=EncryptedSave.new(); e.save_encrypted("user://test_enc.cfg",{"hp":100}); var d:=e.load_encrypted("user://test_enc.cfg"); DirAccess.remove_absolute("user://test_enc.cfg"); e.queue_free()
