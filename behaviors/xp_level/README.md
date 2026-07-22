# XPLevel — Sistema de XP e Nível

Gerencia XP e nível com tabela de progressão (`xp_table`). `add_xp(value)` acumula
XP e sobe de nível automaticamente, emitindo `xp_gained` e `leveled_up`. Suporta
múltiplos level ups. `get_xp_to_next()` e `is_max_level()` para UI. Plugável.
