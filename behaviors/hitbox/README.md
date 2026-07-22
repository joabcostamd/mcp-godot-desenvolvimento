# Hitbox — Área de Ataque

**PT:** Componente Area2D que causa dano a entidades com Health. Ative/desative durante animações de ataque. Suporta tipo de golpe (melee, ranged, magic, explosive) e força de knockback. Previne multi-hit no mesmo frame.

**EN:** Area2D component that deals damage to entities with Health. Toggle on/off during attack animations. Supports hit type (melee, ranged, magic, explosive) and knockback force. Prevents multi-hit in the same frame.

## Uso Rápido

```gdscript
var hitbox := Hitbox.new()
hitbox.damage = 25
hitbox.hit_type = "melee"
add_child(hitbox)

# Durante animação de ataque:
hitbox.set_active(true)
await get_tree().create_timer(0.3).timeout
hitbox.set_active(false)
```

## Dependências
- `health` (#9) — componente de vida do alvo

## ⚠️ Configuração Importante
- **Collision Layers:** Configure `collision_mask` para detectar apenas as camadas dos inimigos. O default (layer 1) detecta tudo, incluindo o próprio dono.
- **Self-hit:** A hitbox NÃO detecta o próprio pai (Godot impede), mas PODE detectar irmãos (ex: hurtbox no mesmo personagem). Use layers diferentes para hitbox e hurtbox.
- **Ativação:** Chame `set_active(true)` no início da animação de ataque e `set_active(false)` + `reset_hits()` ao final.
