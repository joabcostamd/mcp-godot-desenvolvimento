# Upgrade — Sistema de Upgrade

Escuta `leveled_up` do `XPLevel` irmão, oferece `choices_per_level` opções
aleatórias de `upgrade_options` e aplica a escolhida via `apply_upgrade(index)`.
Cada upgrade tem `max_level`. Emite `choices_ready` e `upgrade_applied`.
Estilo Survivors-like. Depende de `xp_level`.
