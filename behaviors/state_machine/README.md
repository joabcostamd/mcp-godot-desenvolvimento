# StateMachine — FSM Leve

**PT:** Máquina de estados finita baseada em condições. Configure estados e transições com `configure()`, dispare condições com `trigger()`. Outros behaviors usam `get_state()` / `is_state()` para decidir comportamento (ex: hitbox só ativa no estado `"attack"`).

**EN:** Condition-based Finite State Machine. Configure states and transitions with `configure()`, fire conditions with `trigger()`. Other behaviors use `get_state()` / `is_state()` to decide behavior (e.g., hitbox only active in `"attack"` state).

## Uso Rápido

```gdscript
var sm := StateMachine.new()
sm.configure(
    ["idle", "attack", "hurt", "dead"],
    [
        {"from": "idle", "to": "attack", "condition": "player_spotted"},
        {"from": "attack", "to": "idle", "condition": "player_lost"},
        {"from": "any", "to": "hurt", "condition": "took_damage"},
        {"from": "any", "to": "dead", "condition": "died"}
    ],
    "idle"
)
add_child(sm)

# Em outro behavior:
if sm.is_state("attack"):
    hitbox.set_active(true)

# Disparar condição:
sm.trigger("player_spotted")
```

## Sinais
- `state_changed(from, to)` — toda transição
- `state_entered(state)` — ao entrar
- `state_exited(state)` — ao sair

## ⚠️ Dicas
- Use `"any"` como `from` para transições globais (ex: `"any" → "hurt"`).
- `set_state("x")` força transição ignorando condições — use com cautela.
- `trigger()` processa UMA transição por chamada — sem loop infinito.
