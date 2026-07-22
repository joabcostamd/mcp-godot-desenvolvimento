## Node que gerencia um baralho de cartas.
## Generos: card.
## Tags: card.
## Extends: Node.
## Sinais: shuffled(), card_drawn(), empty().
## Dependencias: nenhuma.
## @behavior: deck
@tool class_name Deck extends Node
@export var shuffle_on_init: bool = true
signal shuffled(); signal card_drawn(card: Card); signal empty()
var _cards: Array[Card] = []; var _discard: Array[Card] = []
var _initialized: bool = false

func _ready() -> void:
	if _initialized: return
	if shuffle_on_init: shuffle()
	_initialized = true

func add_card(card: Card) -> void: _cards.append(card)
func shuffle() -> void: _cards.shuffle(); shuffled.emit()
func draw() -> Card:
	if _cards.is_empty() and _discard.is_empty(): empty.emit(); return null
	if _cards.is_empty(): _cards=_discard.duplicate(); _discard.clear(); shuffle()
	var c:=_cards.pop_back(); card_drawn.emit(c); return c
func discard(card: Card) -> void: _discard.append(card)
func get_remaining() -> int: return _cards.size()
func get_discard_size() -> int: return _discard.size()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
	if _cards.is_empty() and _discard.is_empty():
		w.append("Deck is empty — use add_card() to populate.")
	return w
