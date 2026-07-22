# Hand — Mão de Cartas

> Node | Godot 4.7 | v1.0.0 | Grupo: GÊNEROS

## 📝 Descrição

Node que gerencia a mão de cartas do jogador. Suporta compra do deck (sibling Deck),
jogar/descartar cartas, limite máximo e layout em leque com ângulo e espaçamento
configuráveis. Integra com Card e Deck siblings.

## 🎯 Quando Usar

- Jogos de cartas (CCG, TCG, deck-building)
- Qualquer jogo com mão de cartas (Slay the Spire, Hearthstone, Magic)
- Sistemas de habilidade baseados em cartas

## ⚡ Quick Start

```gdscript
# Setup: Deck + Hand como irmãos
var deck := Deck.new()
var hand := Hand.new()
add_child(deck)
add_child(hand)

# Popular deck
for i in range(30):
    deck.add_card(Card.new())
deck.shuffle()

# Comprar 5 cartas iniciais
for i in range(5):
    hand.draw_from_deck()

# Jogar/descartar
hand.play_card(0)
hand.discard_card(1)

# Layout em leque
for i in hand.get_count():
    var pos := hand.get_card_position(i)
    var rot := hand.get_card_rotation(i)
    # Aplicar pos/rot ao sprite da carta...
```

## 🔧 Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `max_cards` | int | 1–10 | 7 | Máximo de cartas na mão |
| `fan_angle` | float | 0°–180° | 30° | Ângulo total do leque |
| `card_spacing` | float | 10–500 | 80 | Espaçamento entre cartas (px) |

## 📡 Sinais

| Nome | Params | Quando Emitido |
|------|--------|----------------|
| `card_added` | `card: Card` | Carta adicionada à mão |
| `card_removed` | `card: Card` | Carta removida da mão |

## 🔗 Dependências

- `card` — tipo das cartas gerenciadas
- `deck` (recomendado) — sibling para draw/discard automático

## 🧩 Exemplo de Composição

```
Node2D (GameBoard)
  ├── Deck
  ├── Hand
  │     [Card, Card, Card, Card, Card]
  └── PlayArea
```

## ⚠️ Edge Cases

| Cenário | Comportamento |
|---------|---------------|
| Mão cheia + `draw_from_deck()` | push_warning, retorna null |
| `add_card(null)` | Retorna false |
| Carta duplicada | push_warning, retorna false |
| `play_card(-1)` ou índice inválido | Retorna false |
| Sem Deck sibling | draw/discard funcionam parcialmente (sem baralho) |
| `get_card_position(0)` com mão vazia | Retorna Vector2.ZERO |
| `fan_angle = 0` | Linha reta, sem curvatura |

## ✅ Cobertura de Testes

- `test_add_card` — Adição básica
- `test_add_card_full` — Limite max_cards
- `test_add_duplicate_card` — Duplicata rejeitada
- `test_remove_card` — Remoção básica
- `test_remove_nonexistent_card` — Remoção de carta não presente
- `test_draw_from_deck` — Compra do deck
- `test_draw_from_deck_full_hand` — Compra com mão cheia
- `test_draw_from_deck_no_deck` — Compra sem deck
- `test_play_card` — Jogar carta (emite played)
- `test_play_card_invalid_index` — Índices inválidos
- `test_discard_card` — Descartar para deck
- `test_discard_card_no_deck` — Descartar sem deck
- `test_card_added_signal` — Sinal card_added
- `test_card_removed_signal` — Sinal card_removed
- `test_draw_emits_card_added` — Draw emite sinal
- `test_get_card_position_single_card` — Posição com 1 carta
- `test_get_card_position_multiple` — Simetria do leque
- `test_get_card_rotation` — Rotações simétricas
- `test_get_card_position_empty_hand` — Mão vazia
- `test_get_card_rotation_single` — Rotação com 1 carta
- `test_get_card_invalid_index` — Índices inválidos
- `test_is_full` — Verificação de mão cheia
- `test_add_null_card` — Carta nula
- `test_remove_null_card` — Remoção nula

## 📚 Fonte

- Godot 4.7 ClassDB: Node, Array
- Pattern: Card game hand management (Hearthstone, Slay the Spire, Magic: The Gathering)
- Deck/Card integration do próprio projeto
