# FireRate — Controlador de Cadência

**PT:** Node puro que gerencia cooldown entre disparos com suporte a rajada (burst). Chame `try_fire()` — se o cooldown terminou, emite `fired`. Conecte o sinal `fired` ao seu spawner de projéteis. Suporta rajadas de múltiplos tiros (`burst_count > 1`).

**EN:** Pure Node that manages cooldown between shots with burst support. Call `try_fire()` — if cooldown is done, emits `fired`. Connect the `fired` signal to your projectile spawner. Supports multi-shot bursts (`burst_count > 1`).

## Uso Rápido

```gdscript
# Exemplo: arma com 3 tiros por rajada, 0.1s entre tiros, 0.5s de cooldown
var fire_rate := FireRate.new()
fire_rate.fire_interval = 0.5
fire_rate.burst_count = 3
fire_rate.burst_delay = 0.1
fire_rate.fired.connect(_spawn_projectile)
add_child(fire_rate)

# No _process ou _input:
if Input.is_action_pressed("shoot"):
    fire_rate.try_fire()
```

## Sinais
- `fired()` — a cada tiro (individual, inclusive na rajada)
- `cooldown_ready()` — cooldown terminou, pode atirar de novo

## ⚠️ Atenção
- `burst_delay` deve ser menor que `fire_interval`, ou a rajada nunca termina antes do próximo cooldown.
- Use `reset()` para cancelar cooldown/burst (ex: ao trocar de arma).
