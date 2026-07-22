# Health — Componente de Vida (Padrão-Ouro) v1.1

Componente plugável de vida para Godot 4.7. Adicione como nó filho de qualquer
entidade que precise tomar dano, curar ou morrer.

## Uso

1. Adicione `health.tscn` como filho do nó (inimigo, player, objeto destrutível)
2. Ajuste `max_hp` no inspetor
3. Conecte o sinal `died` para tocar animação de morte, soltar loot, etc.
4. Chame `take_damage(amount)` de qualquer script externo

## Sinais

| Sinal | Quando | Parâmetros |
|-------|--------|------------|
| `died` | HP chega a 0 | — |
| `damage_taken` | Após tomar dano | `amount: int`, `remaining: int` |
| `healed` | Após receber cura | `amount: int`, `current: int` |
| `hp_changed` | Sempre que HP muda | `old_hp: int`, `new_hp: int` |
| `first_hit` | Primeiro dano recebido | — |
| `full` | HP atinge o máximo | — |
| `damage_blocked` | Dano bloqueado | `amount: int` |
| `heal_blocked` | Cura bloqueada | `amount: int` |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `max_hp` | int | 1–9999 | 100 |
| `current_hp` | int | 0–9999 | 100 |
| `invulnerable_time` | float | 0–10s | 0.0 |

## Booleans de Controle (v1.1)

| Controle | Padrão | Quando false |
|----------|--------|-------------|
| `damageable` | true | Ignora todo dano (invencível) |
| `healable` | true | Ignora toda cura |
| `killable` | true | HP mínimo = 1 (nunca morre) |
| `revivable` | true | Impede curar após morte (morte permanente) |

## Multiplier (Critical Hit)

`take_damage(amount, multiplier)` e `heal(amount, multiplier)` aceitam
um segundo parâmetro opcional para dano/cura multiplicado:

```gdscript
health.take_damage(10, 2.0)  # Dano crítico: 20
health.heal(10, 1.5)         # Cura turbinada: 15
```

## Auto-documentação

O componente implementa `_get_configuration_warnings()` — se `max_hp <= 0`
ou `damageable` e `healable` estiverem ambos desabilitados, o nó mostra
⚠️ no editor com a mensagem apropriada.
