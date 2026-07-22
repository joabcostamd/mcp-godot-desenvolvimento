# ElementSystem — Fraquezas e Resistencias Elementais

Modifica dano por elemento: fogo > gelo > raio > agua > fogo.

## Quick Start

```gdscript
var elem := ElementSystem.new()
elem.entity_element = "ice"
var dmg := elem.calculate_damage(100, "fire")  # 200 (fraqueza)
```

## Metodos

| Metodo | Descricao |
|--------|-----------|
| `calculate_damage(base, element)` | Dano modificado |
| `get_multiplier(element)` | Multiplicador (0.5, 1.0, 2.0) |
| `set_weaknesses(element, [weak_against])` | Tabela custom |
| `is_strong_against(a, b)` | A > B? |
