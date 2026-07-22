# TriggerZone — Zona de Gatilho

Area2D com sinais `zone_entered`/`zone_exited`. Filtro por grupo.
`trigger_once` desativa após primeiro uso. CollisionShape2D automático.

## Quick Start

```gdscript
var zone := TriggerZone.new()
zone.trigger_group = "players"
zone.trigger_once = true
zone.zone_entered.connect(func(b): print("Player entrou!"))
add_child(zone)
```

## Propriedades

| Nome | Tipo | Default | Descrição |
|------|------|---------|-----------|
| `trigger_group` | String | `""` | Grupo alvo |
| `trigger_once` | bool | `false` | Descartável |
| `shape_size` | Vector2 | (64,64) | Tamanho da área |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `zone_entered` | `body: Node2D` | Corpo elegível entra |
| `zone_exited` | `body: Node2D` | Corpo elegível sai |

## Fonte

Godot 4.7 ClassDB: `Area2D`, `body_entered`/`body_exited`, `CollisionShape2D`.
