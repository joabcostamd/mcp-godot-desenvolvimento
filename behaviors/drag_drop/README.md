# DragDrop — Arrastar e Soltar

Control que torna o parent arrastável via `set_drag_forwarding()`. Detecta drop
em zonas do grupo `drop_group`. Snap em grid opcional.

## Quick Start

```gdscript
# No _ready() do seu Control arrastável:
var dd := DragDrop.new()
dd.drop_group = "slots"
dd.snap_size = Vector2(64, 64)
add_child(dd)
```

## Propriedades

| Nome | Tipo | Default | Descrição |
|------|------|---------|-----------|
| `drag_preview` | bool | `true` | Mostra preview durante arrasto |
| `snap_size` | Vector2 | `(0,0)` | Grid snap (0,0 = sem snap) |
| `drop_group` | String | `""` | Grupo de alvos válidos |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `drag_started` | — | Início do arrasto |
| `dropped` | `target: NodePath` | Solto sobre alvo válido |
| `drag_cancelled` | — | Cancelado (fora de zona) |

## Edge Cases

- **Sem parent Control:** `_ready()` não conecta drag forwarding
- **`drop_group` vazio:** qualquer Control aceita drop
- **Arrasto cancelado:** volta à posição inicial

## Fonte

Godot 4.7 ClassDB: `Control.set_drag_forwarding()`, `force_drag()`, `NOTIFICATION_DRAG_END`.
