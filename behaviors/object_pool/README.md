# ObjectPool — Pool de Objetos

Pré-instancia N cópias de uma `PackedScene` e gerencia reuso.
Evita custo de `instantiate()`/`queue_free()` repetidos.

## Uso

1. Instancie `object_pool.tscn` na cena
2. Defina `prefab` com a cena a ser pooled
3. Chame `take()` para obter um objeto, `return_object(obj)` para devolver

## Sinais

| Sinal | Quando |
|-------|--------|
| `object_taken` | Objeto retirado do pool |
| `object_returned` | Objeto devolvido |
| `pool_empty` | Pool esgotado (não expansível) |

## Parâmetros

| Parâmetro | Tipo | Faixa | Padrão |
|-----------|------|-------|--------|
| `pool_size` | int | 1–1000 | 20 |
| `prefab` | PackedScene | — | null |
| `expandable` | bool | — | true |

## Dependências

Nenhuma.

## Referência

Fonte: Nodot NodePool. *Game Programming Patterns* — Robert Nystrom.
