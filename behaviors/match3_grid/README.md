# Match3Grid — Núcleo de Lógica Match-3

> Node | Godot 4.7 | v1.0.0 | Grupo: GÊNEROS

## 📝 Descrição

Node que implementa a lógica central de um jogo match-3 (Bejeweled/Candy Crush).
Grade 2D com tipos de gemas, detecção de combinações horizontais/verticais,
remoção, gravidade, preenchimento e cascata em cadeia.

## 🎯 Quando Usar

- Jogos match-3 (Bejeweled, Candy Crush, Puzzle Quest)
- Minigames de combinação
- Sistemas de crafting baseados em grade

## ⚡ Quick Start

```gdscript
var grid := Match3Grid.new()
add_child(grid)

# Inicializar grade
grid.grid_width = 8
grid.grid_height = 8
grid.gem_types = 5
grid.initialize()

# Conectar sinais
grid.match_found.connect(func(positions, type):
    print("Match de %d gemas tipo %d!" % [positions.size(), type])
)
grid.grid_settled.connect(func():
    print("Grade estabilizada.")
)

# Processar jogada (swap player)
var total := grid.process_turn(3, 4, 4, 4)
if total == 0:
    print("Jogada inválida!")
```

## 🔧 Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `grid_width` | int | 3–12 | 8 | Colunas |
| `grid_height` | int | 3–12 | 8 | Linhas |
| `gem_types` | int | 3–7 | 5 | Tipos de gemas |
| `min_match` | int | 3–5 | 3 | Mínimo para combo |

## 📡 Sinais

| Nome | Params | Quando Emitido |
|------|--------|----------------|
| `match_found` | `positions: Array, gem_type: int` | Cada combinação detectada |
| `grid_settled` | — | Grade estabilizada após cascata |
| `combo` | `count: int` | Cada cascata (count ≥ 2) |

## ⚠️ Edge Cases

| Cenário | Comportamento |
|---------|---------------|
| Swap não-adjacente | Retorna false, sem efeito |
| Swap com célula vazia (-1) | Retorna false |
| `process_turn` sem match | Desfaz swap, retorna 0 |
| `initialize` garante sem match inicial | Verifica 2 à esquerda e 2 acima |
| Posição fora da grade | `get_gem` retorna -1 |

## ✅ Cobertura de Testes

- `test_initialize_creates_grid` — Grid populado
- `test_initialize_no_pre_existing_matches` — Sem matches iniciais
- `test_is_adjacent` — Verificação de adjacência
- `test_swap_valid` — Swap bem-sucedido
- `test_swap_invalid_not_adjacent` — Swap não-adjacente rejeitado
- `test_swap_empty_cell` — Swap com vazio rejeitado
- `test_find_horizontal_match` — Match horizontal detectado
- `test_find_vertical_match` — Match vertical detectado
- `test_no_matches` — Grade sem matches
- `test_apply_gravity` — Gemas caem
- `test_refill_fills_empty` — Preenchimento
- `test_process_turn_with_match` — Turno completo
- `test_process_turn_invalid_swap` — Swap inválido desfeito
- `test_match_found_signal` — Sinal match_found
- `test_grid_settled_signal` — Sinal grid_settled
- `test_get_gem_out_of_bounds` — Fora da grade
- `test_is_valid_position` — Validação de posição
- `test_find_matches_empty_grid` — Grade vazia
- `test_min_match_4` — min_match=4 ignora runs de 3

## 📚 Fonte

- Godot 4.7 ClassDB: Node, Array, Vector2i
- Pattern: Match-3 game logic (Bejeweled, Candy Crush Saga)
