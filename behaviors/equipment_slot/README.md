# EquipmentSlot — Slot de equipamento RPG

Gerencia 1 item equipado por slot. Integra Inventory + CharacterStats.

## Quick Start

```gdscript
var weapon_slot := EquipmentSlot.new()
weapon_slot.slot_type = "weapon"
weapon_slot.slot_bonus = 1.2  # 20% extra
entity.add_child(weapon_slot)
weapon_slot.equip("iron_sword")
```

## Propriedades

| Nome | Range | Default | Descrição |
|------|-------|---------|-----------|
| `slot_type` | — | `"weapon"` | Tipo do slot |
| `slot_bonus` | 0–5 | 1.0 | Multiplicador de bônus |

## Sinais

| Nome | Params | Quando |
|------|--------|--------|
| `equipped` | `item_id: String` | Item equipado |
| `unequipped` | `item_id: String` | Item desequipado |
