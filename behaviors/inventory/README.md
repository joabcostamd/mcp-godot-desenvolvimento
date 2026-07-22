# Inventory — Sistema de Inventário v1.0.1

Sistema de inventário baseado em slots: adiciona, remove e consulta itens por ID
(`add_item`, `remove_item`, `has_item`, `get_item_count`). Cada slot comporta até
`max_stack` itens. Quando cheio (total ou parcial), emite `inventory_full`.
Redimensionar `slot_count` para menos emite `item_removed` para slots truncados.
`_set_slot` centralizado emite delta (não remove+add) para mesmo ID. Plugável em
qualquer nó como filho — sem dependências.
