# Currency — Componente de Moeda

Gerencia moeda genérica com tipo nomeado (`currency_type`). Operações: `add(value)`
(emite `gained`), `spend(value) → bool` (emite `spent` ou `insufficient`),
`can_afford(value)`. Múltiplas instâncias com tipos diferentes coexistem no mesmo
nó. Plugável em qualquer nó como filho — sem dependências.
