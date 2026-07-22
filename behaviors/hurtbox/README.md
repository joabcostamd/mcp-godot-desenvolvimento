# Hurtbox — Área Receptora de Dano

**PT:** Area2D passiva que detecta Hitboxes e aplica um multiplicador de dano antes de encaminhar ao componente Health do dono. Permite múltiplas hurtboxes por entidade (ex: cabeça = 2× dano, corpo = 1×, perna = 0.5×). Configurada via `health_path` (NodePath relativo).

**EN:** Passive Area2D that detects Hitboxes and applies a damage multiplier before forwarding to the owner's Health component. Allows multiple hurtboxes per entity (e.g., head = 2× damage, body = 1×, leg = 0.5×). Configured via `health_path` (relative NodePath).

## Uso Rápido

```gdscript
# Exemplo: inimigo com headshot e corpo
# Estrutura:
#   Enemy (CharacterBody2D)
#     ├── Health
#     ├── Hurtbox (head, damage_multiplier=2.0, health_path="../Health")
#     └── Hurtbox (body, damage_multiplier=1.0, health_path="../Health")

var head_hurtbox := Hurtbox.new()
head_hurtbox.damage_multiplier = 2.0
head_hurtbox.hurt_type = "head"
head_hurtbox.health_path = NodePath("../Health")
head_hurtbox.collision_layer = 4   # camada de hurtbox
head_hurtbox.collision_mask = 2    # detecta hitboxes inimigas
add_child(head_hurtbox)
```

## Dependências
- `health` (#9) — recebe o dano modificado
- `hitbox` (#11) — detectada pela hurtbox (via `area_entered`)

## ⚠️ Configuração Importante
- **`health_path`:** Obrigatório. Use NodePath relativo (ex: `"../Health"`). Sem ele, a hurtbox não aplica dano.
- **Collision Layers:** Configure `collision_mask` para detectar apenas hitboxes inimigas. O default (layer 1) detecta TODAS as hitboxes.
- **Multiplicador:** `1.0` = dano normal, `2.0` = headshot, `0.5` = armadura, `0.0` = bloqueio total.
