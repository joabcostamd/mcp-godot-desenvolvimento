## Hand — Mão de Cartas | Godot 4.7.
##
## Node que gerencia a mão de cartas do jogador. Suporta compra
## do deck (sibling Deck), jogar/descartar cartas, limite máximo
## e layout em leque com ângulo e espaçamento configuráveis.
## Integra com Card e Deck siblings.
##
## @behavior: hand
## @genres: card
## @tutorial: behaviors/hand/README.md

@tool
class_name Hand
extends Node

## Número máximo de cartas na mão.
@export var max_cards: int = 7:
	set(v):
		max_cards = clampi(v, 1, 10)

## Ângulo total do leque em graus (0 = linha reta, 180 = semicírculo).
@export var fan_angle: float = 30.0:
	set(v):
		fan_angle = clampf(v, 0.0, 180.0)

## Espaçamento horizontal entre cartas em pixels.
@export var card_spacing: float = 80.0:
	set(v):
		card_spacing = clampf(v, 10.0, 500.0)

signal card_added(card: Card)
signal card_removed(card: Card)

var _cards: Array[Card] = []
var _deck: Deck = null
var _initialized: bool = false


func _ready() -> void:
	if _initialized:
		return
	_find_deck()
	_initialized = true


func _find_deck() -> void:
	var parent := get_parent()
	if not parent:
		return
	for child in parent.get_children():
		if child is Deck and not _deck:
			_deck = child as Deck
			return


# ---------------------------------------------------------------------------
# CARD MANAGEMENT
# ---------------------------------------------------------------------------

## Adiciona uma carta à mão. Retorna true se adicionada.
## Falha se a mão estiver cheia ou a carta já estiver na mão.
func add_card(card: Card) -> bool:
	if not card:
		return false
	if is_full():
		push_warning("Hand: mão cheia (%d/%d)." % [_cards.size(), max_cards])
		return false
	if _cards.has(card):
		push_warning("Hand: carta já está na mão.")
		return false

	_cards.append(card)
	card_added.emit(card)
	return true


## Remove uma carta da mão. Retorna true se removida.
func remove_card(card: Card) -> bool:
	if not card:
		return false
	var idx := _cards.find(card)
	if idx == -1:
		return false

	_cards.remove_at(idx)
	card_removed.emit(card)
	return true


## Compra uma carta do Deck sibling e adiciona à mão.
## Retorna a carta comprada, ou null se falhar.
func draw_from_deck() -> Card:
	if not _deck:
		push_warning("Hand: nenhum Deck sibling encontrado.")
		return null
	if is_full():
		push_warning("Hand: mão cheia — não é possível comprar.")
		return null

	var card := _deck.draw()
	if not card:
		return null

	_cards.append(card)
	card_added.emit(card)
	return card


## Joga uma carta da mão pelo índice.
## A carta emite played e é removida da mão.
## Retorna true se jogada com sucesso.
func play_card(index: int) -> bool:
	var card := _get_card_safe(index)
	if not card:
		return false

	_cards.remove_at(index)
	card.play()
	card_removed.emit(card)
	return true


## Descarta uma carta da mão para o Deck sibling.
## Retorna true se descartada com sucesso.
func discard_card(index: int) -> bool:
	var card := _get_card_safe(index)
	if not card:
		return false

	_cards.remove_at(index)

	if _deck:
		_deck.discard(card)

	card_removed.emit(card)
	return true


## Retorna a carta no índice especificado (null se inválido).
func get_card(index: int) -> Card:
	return _get_card_safe(index)


## Retorna o array de cartas na mão (cópia).
func get_cards() -> Array[Card]:
	return _cards.duplicate()


## Retorna o número de cartas na mão.
func get_count() -> int:
	return _cards.size()


## Retorna true se a mão está cheia.
func is_full() -> bool:
	return _cards.size() >= max_cards


# ---------------------------------------------------------------------------
# LAYOUT
# ---------------------------------------------------------------------------

## Calcula a posição visual de uma carta no leque.
## Retorna Vector2 com a posição relativa ao centro da mão.
## Índice 0 = carta mais à esquerda.
func get_card_position(index: int) -> Vector2:
	var n := _cards.size()
	if n == 0 or index < 0 or index >= n:
		return Vector2.ZERO

	if n == 1:
		return Vector2.ZERO

	# Distribuição angular: do canto esquerdo ao direito do leque
	var total_angle_rad := deg_to_rad(fan_angle)
	var start_angle := -total_angle_rad / 2.0
	var angle_step := total_angle_rad / float(n - 1)
	var angle := start_angle + angle_step * float(index)

	# Posição horizontal: centralizada
	var total_width := card_spacing * float(n - 1)
	var start_x := -total_width / 2.0
	var x := start_x + card_spacing * float(index)

	# Curvatura vertical (arco): cartas das pontas ficam levemente abaixo
	var radius := card_spacing * float(n) / total_angle_rad if total_angle_rad > 0.001 else card_spacing * float(n)
	var y := radius * (1.0 - cos(angle))

	return Vector2(x, y)


## Retorna a rotação (em radianos) que uma carta deve ter no leque.
## Índice 0 = carta mais à esquerda.
func get_card_rotation(index: int) -> float:
	var n := _cards.size()
	if n == 0 or index < 0 or index >= n:
		return 0.0

	if n == 1:
		return 0.0

	var total_angle_rad := deg_to_rad(fan_angle)
	var start_angle := -total_angle_rad / 2.0
	var angle_step := total_angle_rad / float(n - 1)
	return start_angle + angle_step * float(index)


## Retorna a ordem Z (y-sort) para renderização correta do leque.
## Cartas mais à direita ficam acima das da esquerda.
func get_card_z_index(index: int) -> int:
	return index


# ---------------------------------------------------------------------------
# INTERNAL
# ---------------------------------------------------------------------------

func _get_card_safe(index: int) -> Card:
	if index < 0 or index >= _cards.size():
		return null
	return _cards[index]


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if not _deck:
		w.append("Nenhum Deck sibling detectado — draw_from_deck() e discard_card() não terão efeito no baralho.")
	if _cards.size() > max_cards:
		w.append("Mão excede max_cards (%d > %d) — novas cartas serão rejeitadas." % [_cards.size(), max_cards])
	return w
