## test_runner.gd — GdUnit4 Runner para behaviors.
##
## Descobre automaticamente todos os test_*.gd em behaviors/*/ e os executa.
## Use com GdUnit4: adicione esta cena como TestSuite e rode via linha de comando.
##
## Requer: GdUnit4 instalado em addons/gdUnit4/
## Executar: Godot --headless --script res://tests/behaviors/test_runner.gd
##
## @tutorial: https://mikeschulze.github.io/gdUnit4/

@tool
extends GdUnitTestSuite


# ── Descoberta automática ─────────────────────────────────────────────────────

## Retorna todos os diretórios de behavior com teste.
static func discover_behavior_tests() -> Array[String]:
	var tests: Array[String] = []
	var behaviors_dir := "res://behaviors"
	var dir := DirAccess.open(behaviors_dir)
	if not dir:
		push_warning("[TestRunner] Diretório behaviors/ não encontrado.")
		return tests

	dir.list_dir_begin()
	var entry := dir.get_next()
	while entry != "":
		if dir.current_is_dir() and not entry.begins_with("."):
			var test_path := "%s/%s/test_%s.gd" % [behaviors_dir, entry, entry]
			if ResourceLoader.exists(test_path):
				tests.append(test_path)
		entry = dir.get_next()
	dir.list_dir_end()

	return tests


# ── Smoke test ────────────────────────────────────────────────────────────────

## Verifica que behaviors/ existe e tem pelo menos um test_*.gd.
func test_behavior_tests_exist() -> void:
	var tests := discover_behavior_tests()
	assert_array(tests).is_not_empty().override_failure_message(
		"Nenhum test_*.gd encontrado em behaviors/. Cada behavior precisa de teste."
	)


# ── Validação de schema ───────────────────────────────────────────────────────

## Verifica que behavior.schema.json é um JSON válido.
func test_schema_is_valid_json() -> void:
	var file := FileAccess.open("res://behaviors/behavior.schema.json", FileAccess.READ)
	assert_object(file).is_not_null().override_failure_message(
		"behavior.schema.json não encontrado ou não pode ser lido."
	)
	var text := file.get_as_text()
	var json := JSON.new()
	var err := json.parse(text)
	assert_int(err).is_equal(OK).override_failure_message(
		"behavior.schema.json não é JSON válido: " + json.get_error_message()
	)


# ── Validação de behavior.json ────────────────────────────────────────────────

## Verifica que cada behavior.json existe e tem os campos obrigatórios.
func test_all_behaviors_have_valid_json() -> void:
	var dir := DirAccess.open("res://behaviors")
	if not dir:
		return  # test_behavior_tests_exist já cobre este caso

	dir.list_dir_begin()
	var entry := dir.get_next()
	while entry != "":
		if dir.current_is_dir() and not entry.begins_with("."):
			var json_path := "res://behaviors/%s/behavior.json" % entry
			if ResourceLoader.exists(json_path):
				var file := FileAccess.open(json_path, FileAccess.READ)
				var text := file.get_as_text()
				var json := JSON.new()
				var err := json.parse(text)
				assert_int(err).is_equal(OK).override_failure_message(
					"%s/behavior.json não é JSON válido." % entry
				)
				if err == OK:
					var data: Dictionary = json.get_data()
					# Campos obrigatórios
					assert_bool(data.has("name")).is_true().override_failure_message(
						"%s/behavior.json: campo 'name' ausente." % entry
					)
					assert_bool(data.has("description_pt")).is_true().override_failure_message(
						"%s/behavior.json: campo 'description_pt' ausente." % entry
					)
					assert_bool(data.has("version")).is_true().override_failure_message(
						"%s/behavior.json: campo 'version' ausente." % entry
					)
					# Nome do diretório bate com name
					if data.has("name"):
						assert_str(data["name"]).is_equal(entry).override_failure_message(
							"%s/behavior.json: 'name' (%s) não bate com diretório (%s)." % [entry, data["name"], entry]
						)
		entry = dir.get_next()
	dir.list_dir_end()


# ── Verificação de distinguibilidade ──────────────────────────────────────────

## Verifica que nomes de behaviors não são ambíguos entre si.
func test_behavior_names_are_distinct() -> void:
	var names: Array[String] = []
	var dir := DirAccess.open("res://behaviors")
	if not dir:
		return

	dir.list_dir_begin()
	var entry := dir.get_next()
	while entry != "":
		if dir.current_is_dir() and not entry.begins_with("."):
			names.append(entry)
		entry = dir.get_next()
	dir.list_dir_end()

	# Verifica por nomes muito similares
	for i in names.size():
		for j in names.size():
			if i >= j:
				continue
			var a: String = names[i]
			var b: String = names[j]
			var similarity := _levenshtein_ratio(a, b)
			assert_float(similarity).is_less(0.75).override_failure_message(
				"Nomes muito similares: '%s' e '%s' (%.0f%%). Risco de confusão na busca semântica." % [a, b, similarity * 100]
			)


# ── Helpers ───────────────────────────────────────────────────────────────────

static func _levenshtein_ratio(a: String, b: String) -> float:
	var la := a.length()
	var lb := b.length()
	if la == 0:
		return 1.0 if lb == 0 else 0.0
	if lb == 0:
		return 0.0

	var matrix: Array[Array] = []
	for i in range(la + 1):
		matrix.append([])
		for j in range(lb + 1):
			if i == 0:
				matrix[i].append(j)
			elif j == 0:
				matrix[i].append(i)
			else:
				matrix[i].append(0)

	for i in range(1, la + 1):
		for j in range(1, lb + 1):
			var cost := 0 if a[i - 1] == b[j - 1] else 1
			matrix[i][j] = mini(
				matrix[i - 1][j] + 1,
				mini(matrix[i][j - 1] + 1, matrix[i - 1][j - 1] + cost)
			)

	var distance: int = matrix[la][lb]
	var max_len: int = maxi(la, lb)
	return 1.0 - float(distance) / float(max_len)
