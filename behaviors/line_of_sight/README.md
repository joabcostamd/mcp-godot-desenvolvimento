# LineOfSight — Visão em Cone

Componente de visão para NPCs que detecta alvos dentro de um cone
definido por ângulo e alcance. Usa `Area2D` com `CircleShape2D` e
verificação de ângulo via dot product.

## Uso

1. Instancie `line_of_sight.tscn` como filho de um NPC (Node2D)
2. O NPC deve estar no grupo definido em `target_group` (padrão: "player")
3. Rote o NPC para mirar o cone de visão
4. Conecte `target_spotted` ao `enemy_chase` para perseguir ao ver

## Sinais

| Sinal | Quando | Parâmetros |
|-------|--------|------------|
| `target_spotted` | Alvo entra no cone de visão | `target: Node2D` |
| `target_lost` | Alvo sai do cone de visão | `target: Node2D` |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `view_angle` | float | 1–360° | 90 |
| `view_range` | float | 10–3000 px | 300 |
| `ray_count` | int | 0–10 | 0 |
| `target_group` | String | — | "player" |

> **Nota:** O cone de visão usa `CircleShape2D` para detecção de área e
> verifica o ângulo no código. `ray_count > 0` ativa verificação de oclusão
> (paredes bloqueiam a visão). A direção de visão segue a rotação do pai.
>
> **Oclusão:** Com `ray_count > 0`, um `PhysicsRayQueryParameters2D` é
> disparado do sensor até o alvo. Se houver colisão com algo que não é o
> alvo, a visão é bloqueada.

## Dependências

Nenhuma. Funciona independente.

## Exemplo de composição

```
NPC (Node2D, rotacionável)
  ├── LineOfSight (este)     ← detecta player no cone
  ├── EnemyChase (Node)      ← persegue ao ver
  └── Sprite2D
```

## Referência

Fonte: Nodot ViewCone3D (adaptado para 2D).
Padrão: *Game Development Patterns with Godot 4* — Composição sobre herança.
