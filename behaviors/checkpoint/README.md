# Checkpoint

Ponto de salvamento via `Area2D` + `SaveLoad`. `body_entered` ativa e salva posição. `respawn(player)` estático teleporta para o último checkpoint.

**Parâmetros:** `checkpoint_id`, `spawn_offset`.

**Uso:** Posicione na cena. `Checkpoint.respawn(player)` restaura posição. Sinal `checkpoint_reached`.

**Fontes:** Godot 4.7 ClassDB (`Area2D`, `SaveLoad`).
