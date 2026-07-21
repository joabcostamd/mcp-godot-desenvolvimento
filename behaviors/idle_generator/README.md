# IdleGenerator — Gerador de Recursos Idle/Clicker

> Node | Godot 4.7 | v1.0.0 | Grupo: GÊNEROS

## 📝 Descrição

Node que gera recursos automaticamente ao longo do tempo (idle/clicker).
Acumula até max_storage. Transfere para Currency sibling via collect().
Suporta upgrade com custo escalável que aumenta a taxa de produção.
Ideal para jogos idle, clicker e sistemas de produção passiva.

## 🎯 Quando Usar

- Jogos idle/clicker (Cookie Clicker, Adventure Capitalist)
- Sistemas de produção passiva (fábricas, mineração)
- Recursos que aumentam com o tempo (energia, mana, gold passivo)
- Qualquer sistema de "ganho por segundo"

## ⚡ Quick Start

```gdscript
# Setup: Currency + IdleGenerator como irmãos
var currency := Currency.new()
var generator := IdleGenerator.new()
add_child(currency)
add_child(generator)

# Configurar produção
generator.resource_per_second = 5.0
generator.max_storage = 500.0

# Coletar periodicamente (botão, timer, etc.)
func _on_collect_button_pressed():
    var collected := generator.collect()
    print("Coletado: ", collected)

# Upgrade
func _on_upgrade_button_pressed():
    if generator.upgrade():
        print("Nível: ", generator.get_level())
```

## 🔧 Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `resource_per_second` | float | 0.1–1000 | 1.0 | Taxa base de produção |
| `max_storage` | float | 1–1M | 100 | Capacidade máxima |
| `upgrade_cost` | int | 1–999999 | 10 | Custo base do upgrade |
| `upgrade_cost_multiplier` | float | 1.0–10.0 | 1.5 | Escala do custo (+50%/nível) |
| `upgrade_rate_multiplier` | float | 1.0–5.0 | 2.0 | Escala da taxa (dobra/ nível) |
| `enabled` | bool | — | true | Pausa/retoma produção |

## 📡 Sinais

| Nome | Params | Quando Emitido |
|------|--------|----------------|
| `generated` | `amount: int` | Ao coletar recursos |
| `storage_full` | — | Armazenamento no máximo |
| `upgraded` | `new_level: int, new_rate: float` | Upgrade bem-sucedido |

## 🔗 Dependências

- `currency` (recomendado) — sibling para depósito dos recursos coletados

## 🧩 Exemplo de Composição

```
Node (Manager)
  ├── Currency (gold)
  ├── IdleGenerator (Gold Mine)
  │     level: 5, rate: 16.0/s
  └── IdleGenerator (Mana Well)
        level: 2, rate: 2.0/s
```

## ⚠️ Edge Cases

| Cenário | Comportamento |
|---------|---------------|
| `collect()` com < 1.0 armazenado | Retorna 0, fração preservada |
| Sem Currency sibling | `collect()` retorna amount mas não transfere |
| `_physics_process` com `enabled=false` | No-op, não acumula |
| `_physics_process` antes de `_ready()` | Guard `_initialized`, no-op |
| `upgrade()` sem moeda suficiente | Retorna false, nível mantido |
| Armazenamento atinge `max_storage` | Para de acumular, emite `storage_full` |
| Múltiplos `collect()` | Fração residual preservada entre collects |

## ✅ Cobertura de Testes

- `test_initial_state` — Estado inicial (level=1, rate=1.0, stored=0)
- `test_collect_no_stored` — Coleta com 0 armazenado
- `test_collect_with_currency` — Coleta com Currency sibling
- `test_collect_without_currency` — Coleta sem Currency
- `test_accumulation_over_time` — Acumulação em _physics_process
- `test_accumulation_disabled` — Desabilitado não acumula
- `test_accumulation_not_initialized` — Pré-_ready não acumula
- `test_storage_cap` — Teto de armazenamento
- `test_storage_full_signal` — Sinal storage_full
- `test_storage_ratio` — Cálculo da proporção
- `test_upgrade_cost_formula` — Fórmula de custo (10 * 2^(level-1))
- `test_upgrade_success` — Upgrade bem-sucedido
- `test_upgrade_insufficient_funds` — Sem moeda suficiente
- `test_upgrade_no_currency` — Sem Currency sibling
- `test_upgrade_rate_scaling` — Escala da taxa de produção
- `test_generated_signal` — Sinal generated
- `test_upgraded_signal` — Sinal upgraded
- `test_multiple_collects` — Coletas consecutivas com fração
- `test_collect_fraction_only` — Coleta com < 1.0
- `test_get_storage_ratio_zero_max` — Ratio com max_storage mínimo

## 📚 Fonte

- Godot 4.7 ClassDB: Node, _physics_process
- Pattern: Idle/clicker game mechanics (Cookie Clicker, Adventure Capitalist)
- Currency integration do próprio projeto
