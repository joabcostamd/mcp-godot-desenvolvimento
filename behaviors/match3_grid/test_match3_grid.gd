## test_match3_grid.gd — Testes do Match3Grid | GdUnit4.

extends GdUnitTestSuite


func _make_grid(w: int = 4, h: int = 4, types: int = 4) -> Match3Grid:
	var g := Match3Grid.new()
	g.grid_width = w
	g.grid_height = h
	g.gem_types = types
	g.min_match = 3
	return g


func _populate_manual(grid: Match3Grid, data: Array[Array]) -> void:
	"""Popula a grade manualmente com dados fornecidos (evita _random_gem_without_match)."""
	grid._grid.clear()
	for row in data:
		var r: Array[int] = []
		for val in row:
			r.append(val as int)
		grid._grid.append(r)


# ---------------------------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------------------------

func test_initialize_creates_grid() -> void:
	var g := _make_grid(5, 4, 4)
	g.initialize()
	assert_int(g._grid.size()).is_equal(4)
	assert_int(g._grid[0].size()).is_equal(5)

	# Todas as células preenchidas
	for y in range(4):
		for x in range(5):
			assert_bool(g.get_gem(x, y) >= 0).is_true()

	g.queue_free()


func test_initialize_no_pre_existing_matches() -> void:
	var g := _make_grid(6, 6, 4)
	g.initialize()

	var matches := g.find_matches()
	assert_array(matches).is_empty()  # grade limpa

	g.queue_free()


# ---------------------------------------------------------------------------
# ADJACENCY & SWAP
# ---------------------------------------------------------------------------

func test_is_adjacent() -> void:
	var g := _make_grid()
	assert_bool(g.is_adjacent(0, 0, 1, 0)).is_true()   # direita
	assert_bool(g.is_adjacent(0, 0, 0, 1)).is_true()   # baixo
	assert_bool(g.is_adjacent(0, 0, 0, 0)).is_false()  # mesma
	assert_bool(g.is_adjacent(0, 0, 1, 1)).is_false()  # diagonal
	assert_bool(g.is_adjacent(0, 0, 2, 0)).is_false()  # distante
	g.queue_free()


func test_swap_valid() -> void:
	var g := _make_grid()
	_populate_manual(g, [[0, 1], [2, 3]])
	assert_bool(g.swap(0, 0, 1, 0)).is_true()
	assert_int(g.get_gem(0, 0)).is_equal(1)
	assert_int(g.get_gem(1, 0)).is_equal(0)
	g.queue_free()


func test_swap_invalid_not_adjacent() -> void:
	var g := _make_grid()
	_populate_manual(g, [[0, 1, 2], [3, 4, 5], [6, 7, 8]])
	assert_bool(g.swap(0, 0, 2, 0)).is_false()
	g.queue_free()


func test_swap_empty_cell() -> void:
	var g := _make_grid()
	_populate_manual(g, [[0, -1]])
	assert_bool(g.swap(0, 0, 1, 0)).is_false()
	g.queue_free()


# ---------------------------------------------------------------------------
# MATCH DETECTION
# ---------------------------------------------------------------------------

func test_find_horizontal_match() -> void:
	var g := _make_grid(5, 3, 4)
	_populate_manual(g, [
		[0, 0, 0, 1, 2],
		[3, 2, 1, 0, 3],
		[1, 1, 1, 1, 0]   # match de 4 na linha 2
	])

	var matches := g.find_matches()
	assert_bool(matches.size() >= 1).is_true()

	# Deve haver um match horizontal
	var found_h4 := false
	for m in matches:
		var md := m as Dictionary
		if md["type"] == 1 and md["positions"].size() >= 4:
			found_h4 = true
	assert_bool(found_h4).is_true()

	g.queue_free()


func test_find_vertical_match() -> void:
	var g := _make_grid(3, 5, 4)
	_populate_manual(g, [
		[0, 1, 2],
		[0, 3, 2],
		[0, 1, 2],
		[3, 1, 2],
		[1, 0, 3]
	])

	var matches := g.find_matches()
	# Coluna 0: 0,0,0 vertical = match de 3
	# Coluna 2: 2,2,2,2 vertical = match de 4
	assert_bool(matches.size() >= 2).is_true()

	g.queue_free()


func test_no_matches() -> void:
	var g := _make_grid(3, 3, 3)
	_populate_manual(g, [
		[0, 1, 2],
		[1, 2, 0],
		[2, 0, 1]
	])

	var matches := g.find_matches()
	assert_array(matches).is_empty()

	g.queue_free()


# ---------------------------------------------------------------------------
# GRAVITY & REFILL
# ---------------------------------------------------------------------------

func test_apply_gravity() -> void:
	var g := _make_grid(3, 4, 3)
	_populate_manual(g, [
		[0, -1, 2],
		[1, -1, -1],
		[-1, 3, -1],
		[2, 1, 0]
	])

	g.apply_gravity()

	# Gemas devem cair para baixo
	assert_int(g.get_gem(0, 3)).is_equal(0)
	assert_int(g.get_gem(0, 2)).is_equal(1)
	assert_int(g.get_gem(0, 1)).is_equal(2)
	assert_int(g.get_gem(0, 0)).is_equal(-1)

	g.queue_free()


func test_refill_fills_empty() -> void:
	var g := _make_grid(3, 3, 3)
	g.initialize(42)

	# Esvazia algumas posições
	g._grid[0][0] = -1
	g._grid[1][1] = -1

	g.refill_grid()

	assert_bool(g.get_gem(0, 0) >= 0).is_true()
	assert_bool(g.get_gem(1, 1) >= 0).is_true()

	g.queue_free()


# ---------------------------------------------------------------------------
# PROCESS TURN
# ---------------------------------------------------------------------------

func test_process_turn_with_match() -> void:
	var g := _make_grid(4, 4, 3)
	# Configura grade com swap que gera match
	_populate_manual(g, [
		[0, 0, 1, 2],
		[1, 2, 0, 1],
		[2, 1, 0, 2],  # (2,2)=0 está abaixo de (2,1)=0 — swap (2,0)=1↔(2,1)=0 gera coluna 0,0,0
		[0, 2, 1, 0]
	])

	# Swap (2,0) com (2,1): 1↔0
	var total := g.process_turn(2, 0, 2, 1)
	assert_bool(total > 0).is_true()
	assert_bool(g.get_combo_count() > 0).is_true()

	g.queue_free()


func test_process_turn_invalid_swap() -> void:
	var g := _make_grid(3, 3, 3)
	_populate_manual(g, [
		[0, 1, 2],
		[1, 2, 0],
		[2, 0, 1]
	])

	# Swap que não gera match
	var total := g.process_turn(0, 0, 1, 0)
	assert_int(total).is_equal(0)

	# Grade deve voltar ao estado original
	assert_int(g.get_gem(0, 0)).is_equal(0)
	assert_int(g.get_gem(1, 0)).is_equal(1)

	g.queue_free()


# ---------------------------------------------------------------------------
# SIGNALS
# ---------------------------------------------------------------------------

func test_match_found_signal() -> void:
	var g := _make_grid(5, 3, 3)
	_populate_manual(g, [
		[0, 0, 0, 1, 2],
		[1, 2, 0, 2, 1],
		[2, 1, 0, 0, 1]
	])

	var emitted := false
	g.match_found.connect(func(_pos, _type): emitted = true)

	g.process_turn(0, 1, 1, 1)  # swap que gera match

	assert_bool(emitted).is_true()
	g.queue_free()


func test_grid_settled_signal() -> void:
	var g := _make_grid(5, 3, 3)
	_populate_manual(g, [
		[0, 1, 2, 0, 1],
		[2, 2, 2, 1, 0],  # match horizontal de 3
		[0, 1, 0, 2, 1]
	])

	var emitted := false
	g.grid_settled.connect(func(): emitted = true)

	g.process_turn(0, 0, 1, 0)  # qualquer swap — já tem match

	assert_bool(emitted).is_true()
	g.queue_free()


# ---------------------------------------------------------------------------
# EDGE CASES
# ---------------------------------------------------------------------------

func test_get_gem_out_of_bounds() -> void:
	var g := _make_grid(3, 3, 3)
	g.initialize()
	assert_int(g.get_gem(-1, 0)).is_equal(-1)
	assert_int(g.get_gem(0, 99)).is_equal(-1)
	assert_int(g.get_gem(3, 0)).is_equal(-1)
	g.queue_free()


func test_is_valid_position() -> void:
	var g := _make_grid(4, 3, 3)
	assert_bool(g.is_valid_position(0, 0)).is_true()
	assert_bool(g.is_valid_position(3, 2)).is_true()
	assert_bool(g.is_valid_position(-1, 0)).is_false()
	assert_bool(g.is_valid_position(4, 0)).is_false()
	assert_bool(g.is_valid_position(0, 3)).is_false()
	g.queue_free()


func test_find_matches_empty_grid() -> void:
	var g := _make_grid(3, 3, 3)
	var matches := g.find_matches()
	assert_array(matches).is_empty()
	g.queue_free()


func test_min_match_4() -> void:
	var g := _make_grid(5, 3, 3)
	g.min_match = 4
	_populate_manual(g, [
		[0, 0, 0, 1, 2],  # match de 3 — não conta com min_match=4
		[1, 1, 1, 1, 2],  # match de 4
		[2, 0, 1, 0, 1]
	])

	var matches := g.find_matches()
	assert_bool(matches.size() >= 1).is_true()

	# Só o match de 4 deve ser detectado
	for m in matches:
		var md := m as Dictionary
		assert_bool(md["positions"].size() >= 4).is_true()

	g.queue_free()
