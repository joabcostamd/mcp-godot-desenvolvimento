# CharacterStats — Atributos RPG

Node com STR/DEX/INT/VIT. Derivados: dano físico/mágico, atk speed, HP.

## Quick Start

```gdscript
var stats := CharacterStats.new()
stats.strength = 15
print(stats.get_physical_damage())  # 30
stats.add_modifier("strength", 1.5)  # +50% dano físico
```

## Propriedades

| Nome | Range | Default | Descrição |
|------|-------|---------|-----------|
| `strength` | 1–999 | 10 | Dano físico base |
| `dexterity` | 1–999 | 10 | Velocidade de ataque |
| `intelligence` | 1–999 | 10 | Dano mágico base |
| `vitality` | 1–999 | 10 | HP máximo (×10) |

## Métodos

| Método | Descrição |
|--------|-----------|
| `get_physical_damage()` | STR × 2 × modifier |
| `get_magic_damage()` | INT × 2 × modifier |
| `get_attack_speed()` | 1.0 + DEX × 0.02 × modifier |
| `add_modifier(stat, mult)` | Modificador multiplicativo |
| `clear_modifiers(stat)` | Remove modificadores |
| `get_stat(name)` | Valor com modificadores |
