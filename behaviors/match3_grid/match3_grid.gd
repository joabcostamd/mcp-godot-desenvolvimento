## Match3Grid — Núcleo de Lógica Match-3 | Godot 4.7.
##
## Node que implementa a lógica central de um jogo match-3
## (Bejeweled/Candy Crush). Grade 2D com tipos de gemas,
## detecção de combinações, remoção, gravidade, preenchimento
## e cascata em cadeia.
##
## @behavior: match3_grid
## @genres: puzzle, casual, match3
## @tutorial: behaviors/match3_grid/README.md

@tool
class_name Match3Grid
extends Node

## Largura da grade (colunas).
@export var grid_width: int = 8:
	set(v):
		grid_width = clampi(v, 3, 12)

## Altura da grade (linhas).
@export var grid_height: int = 8:
	set(v):
		grid_height = clampi(v, 3, 12)

## Número de tipos de gemas diferentes.
@export var gem_types: int = 5:
	set(v):
		gem_types = clampi(v, 3, 7)

## Mínimo de gemas iguais consecutivas para formar combinação.
@export var min_match: int = 3:
	set(v):
		min_match = clampi(v, 3, 5)

signal match_found(positions: Array, gem_type: int)
signal grid_settled()
signal combo(count: int)

var _grid: Array[Array] = []  # _grid[y][x] = gem_type (int), -1 = vazio
var _combo_count: int = 0
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_initialized = true


# ---------------------------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------------------------

## Inicializa a grade com gemas aleatórias, garantindo que não há
## combinações pré-existentes. seed < 0 usa random sem seed.
func initialize(seed_val: int = -1) -> void:
	if seed_val >= 0:
		seed(seed_val)

	_grid.clear()
	for y in range(grid_height):
		var row: Array[int] = []
		for x in range(grid_width):
			var gem := _random_gem_without_match(x, y)
			row.append(gem)
		_grid.append(row)


func _random_gem_without_match(x: int, y: int) -> int:
	var forbidden: Array[int] = []

	# Verifica 2 à esquerda (evita match horizontal de 3)
	if x >= min_match - 1:
		var t := _get_gem(x - 1, y)
		if t >= 0 and _get_gem(x - 2, y) == t:
			forbidden.append(t)

	# Verifica 2 acima (evita match vertical de 3)
	if y >= min_match - 1:
		var vt := _get_gem(x, y - 1)
		if vt >= 0 and _get_gem(x, y - 2) == vt:
			forbidden.append(vt)

	var available: Array[int] = []
	for t in range(gem_types):
		if not forbidden.has(t):
			available.append(t)

	if available.is_empty():
		return randi() % gem_types

	return available[randi() % available.size()]


# ---------------------------------------------------------------------------
# GRID ACCESS
# ---------------------------------------------------------------------------

## Retorna o tipo de gema na posição (-1 se vazio ou inválido).
func get_gem(x: int, y: int) -> int:
	return _get_gem(x, y)


## Retorna true se a posição está dentro da grade.
func is_valid_position(x: int, y: int) -> bool:
	return x >= 0 and x < grid_width and y >= 0 and y < grid_height


# ---------------------------------------------------------------------------
# SWAP
# ---------------------------------------------------------------------------

## Retorna true se (x1,y1) e (x2,y2) são adjacentes (4-dir, não diagonal).
func is_adjacent(x1: int, y1: int, x2: int, y2: int) -> bool:
	var dx := absi(x1 - x2)
	var dy := absi(y1 - y2)
	return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)


## Troca duas gemas de posição. Retorna true se a troca é válida
## (adjacentes, ambas dentro da grade e não vazias).
func swap(x1: int, y1: int, x2: int, y2: int) -> bool:
	if not is_valid_position(x1, y1) or not is_valid_position(x2, y2):
		return false
	if not is_adjacent(x1, y1, x2, y2):
		return false

	var t1 := _get_gem(x1, y1)
	var t2 := _get_gem(x2, y2)
	if t1 < 0 or t2 < 0:
		return false

	_grid[y1][x1] = t2
	_grid[y2][x2] = t1
	return true


# ---------------------------------------------------------------------------
# MATCH DETECTION
# ---------------------------------------------------------------------------

## Encontra todas as combinações atuais na grade.
## Retorna Array[Dictionary] com {positions: Array[Vector2i], type: int}.
func find_matches() -> Array:
	var matches: Array = []
	var visited: Dictionary = {}  # "x,y" -> bool

	for y in range(grid_height):
		for x in range(grid_width):
			var key := "%d,%d" % [x, y]
			if visited.get(key, false):
				continue

			var gem_type := _get_gem(x, y)
			if gem_type < 0:
				continue

			# Scan horizontal
			var h_run: Array[Vector2i] = []
			var hx := x
			while hx < grid_width and _get_gem(hx, y) == gem_type:
				h_run.append(Vector2i(hx, y))
				hx += 1

			if h_run.size() >= min_match:
				var v_match := {"positions": v_run, "type": gem_type}
				matches.append(v_match)
				for pos in h_run:
					visited["%d,%d" % [pos.x, pos.y]] = true

			# Scan vertical (só se não foi visitado pelo scan horizontal)
			if not visited.get(key, false):
				var v_run: Array[Vector2i] = []
				var vy := y
				while vy < grid_height and _get_gem(x, vy) == gem_type:
					v_run.append(Vector2i(x, vy))
					vy += 1

				if v_run.size() >= min_match:
					var match_dict := {"positions": v_run, "type": gem_type}
					matches.append(match_dict)
					for pos in v_run:
						visited["%d,%d" % [pos.x, pos.y]] = true

	return matches


# ---------------------------------------------------------------------------
# BOARD OPERATIONS
# ---------------------------------------------------------------------------

## Remove as gemas nas posições especificadas (define como -1).
func remove_gems(positions: Array) -> void:
	for pos in positions:
		var p: Vector2i = pos as Vector2i
		if is_valid_position(p.x, p.y):
			_grid[p.y][p.x] = -1


## Aplica gravidade: gemas caem para preencher espaços vazios abaixo.
func apply_gravity() -> void:
	for x in range(grid_width):
		var write_y := grid_height - 1
		for y in range(grid_height - 1, -1, -1):
			var gem := _get_gem(x, y)
			if gem >= 0:
				if write_y != y:
					_grid[write_y][x] = gem
					_grid[y][x] = -1
				write_y -= 1


## Preenche espaços vazios no topo com gemas aleatórias.
func refill_grid() -> void:
	for x in range(grid_width):
		for y in range(grid_height):
			if _get_gem(x, y) < 0:
				_grid[y][x] = randi() % gem_types


# ---------------------------------------------------------------------------
# TURN PROCESSING
# ---------------------------------------------------------------------------

## Executa um turno completo: swap → detecta matches → remove → gravity
## → refill → cascade (repete até estabilizar).
## Retorna o número total de combinações encontradas no turno.
func process_turn(x1: int, y1: int, x2: int, y2: int) -> int:
	# 1. Swap
	if not swap(x1, y1, x2, y2):
		return 0

	# 2. Detecta combinações iniciais
	var initial_matches := find_matches()
	if initial_matches.is_empty():
		# Swap inválido: desfaz
		swap(x1, y1, x2, y2)
		return 0

	# 3. Processa cascata
	_combo_count = 0
	var total_matches := 0
	var current_matches := initial_matches

	while not current_matches.is_empty():
		_combo_count += 1
		total_matches += current_matches.size()

		for match_dict in current_matches:
			var m: Dictionary = match_dict as Dictionary
			match_found.emit(m["positions"], m["type"])

		# Remove gemas combinadas
		for match_dict in current_matches:
			var md: Dictionary = match_dict as Dictionary
			remove_gems(md["positions"])

		apply_gravity()
		refill_grid()

		if _combo_count > 1:
			combo.emit(_combo_count)

		current_matches = find_matches()

	grid_settled.emit()
	return total_matches


## Retorna o número de combos (cascatas) do último turno.
func get_combo_count() -> int:
	return _combo_count


# ---------------------------------------------------------------------------
# INTERNAL
# ---------------------------------------------------------------------------

func _get_gem(x: int, y: int) -> int:
	if not is_valid_position(x, y):
		return -1
	if y >= _grid.size():
		return -1
	var row: Array = _grid[y]
	if x >= row.size():
		return -1
	return row[x] as int


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if _grid.is_empty():
		w.append("Grade não inicializada — chame initialize() para popular a grade.")
	if gem_types < 3:
		w.append("gem_types < 3 — poucos tipos podem gerar combinações excessivas.")
	return w
