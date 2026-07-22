# SaveLoad — Sistema de Save/Load v1.0.1

Salva/restaura estado de behaviors irmãos (Inventory, Currency, XPLevel) via
`ConfigFile` em `save_dir/<slot>.cfg`. `save(slot)`, `load(slot)`,
`has_save(slot)`, `delete_save(slot)`, `get_save_slots()`. Emite `saved`/`loaded`.
`save_dir` com setter de validação (nunca vazio, sempre termina com `/`).
Sem dependências.
