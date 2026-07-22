# Knockback — Impulso de Recuo

**PT:** Node que aplica impulso ao `velocity` do `CharacterBody2D` pai. Conecte ao sinal `hit_dealt` do hitbox ou chame `apply_knockback(direction)` manualmente. Cooldown evita empilhamento de knockbacks.

**EN:** Node that applies impulse to the parent `CharacterBody2D`'s `velocity`. Connect to the hitbox's `hit_dealt` signal or call `apply_knockback(direction)` manually. Cooldown prevents knockback stacking.

## Uso Rápido

```gdscript
# Exemplo: inimigo que recua ao ser atingido
# Enemy (CharacterBody2D)
#   ├── Health
#   ├── Hurtbox
#   └── Knockback

var kb := Knockback.new()
kb.force = 300.0
kb.duration = 0.2
add_child(kb)

# Conecta ao hitbox:
hitbox.hit_dealt.connect(func(target, _dmg):
    var dir := (target.global_position - global_position).normalized()
    target.get_node("Knockback").apply_knockback(dir)
)
```

## ⚠️ Requisitos
- O pai DEVE ser `CharacterBody2D` (ou subclasse). Caso contrário, `apply_knockback` retorna false.
- A dissipação do knockback é controlada pela física do CharacterBody2D (friction, gravity).
