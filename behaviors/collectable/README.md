# Collectable — Componente de Coleta v1.0.1

Area2D que detecta o jogador (`body_entered`) e coleta itens para um `Inventory`
no nó pai. Suporta auto-pickup (colisão, com setter dinâmico), pickup manual
(`pickup(body)`), atração magnética automática (`magnet_range` com detecção via
`get_overlapping_bodies`) e cooldown anti-flood em `pickup_failed`. Depende de
`inventory`.
