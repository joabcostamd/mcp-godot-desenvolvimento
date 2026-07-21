# SpawnerWave — Spawner de Ondas

Cria inimigos em ondas via `ObjectPool`. Controla intervalo entre
ondas, spawn delay, e máximo de ativos simultâneos.

## Uso

1. Instancie `spawner_wave.tscn` na cena
2. Adicione `ObjectPool` como sibling com o prefab do inimigo
3. Ajuste `spawn_count_per_wave`, `wave_interval`, `max_active`
4. Conecte `enemy_spawned` para lógica de jogo

## Sinais

| Sinal | Quando |
|-------|--------|
| `wave_started` | Nova onda iniciada |
| `wave_cleared` | Todos inimigos da onda morreram |
| `all_waves_done` | Última onda concluída |
| `enemy_spawned` | Inimigo spawnado |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `spawn_count_per_wave` | int | 1–500 | 10 |
| `wave_interval` | float | 1–300 s | 10 |
| `spawn_delay` | float | 0.05–5 s | 0.5 |
| `max_active` | int | 1–1000 | 50 |
| `spawn_radius` | float | 10–3000 px | 300 |

## Dependências

- `object_pool` — fornece instâncias de inimigos
- `health` — detecta morte para devolver ao pool

## Referência

Fonte: Nodot Spawner3D.
