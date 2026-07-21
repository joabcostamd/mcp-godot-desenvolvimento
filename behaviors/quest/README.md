# Quest — Sistema de Quests

Gerencia quests com objetivos rastreáveis (`collect` via Inventory, `spend` via
Currency) e recompensas automáticas. Auto-detecta irmãos Inventory/Currency.
`start_quest(id)` ativa tracking, `get_progress(id)` retorna estado. Emite
`quest_started`, `quest_completed`, `quest_failed`. Depende de inventory + currency.
