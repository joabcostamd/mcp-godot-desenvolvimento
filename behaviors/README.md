# Behaviors — Componentes Verificados

Catálogo de comportamentos prontos para Godot 4.7. Cada behavior é um
**componente independente** (nó filho, nunca herança) que se pluga em
qualquer entidade do jogo.

## Estrutura de um behavior

```
behaviors/<nome>/
  behavior.json     — metadados: nome, descrição PT/EN, sinônimos, parâmetros,
                      sinais, dependências, gêneros, conflitos, versão
  <nome>.tscn       — cena do componente
  <nome>.gd         — script GDScript (@tool, @export)
  test_<nome>.gd    — teste GdUnit4 obrigatório
  README.md         — 1 parágrafo para busca semântica
```

## Regras

- **Composição sobre herança.** Behavior é nó filho, nunca classe base.
- **Parâmetro tem faixa.** Todo `@export` declarado no `behavior.json` com
  `min`, `max` e `default`.
- **Teste obrigatório.** Behavior sem teste não passa no `auditar.py`.
- **Nome distinguível.** Nome não pode se confundir com outro termo existente.
- **Um por fatia.** Cada behavior novo é uma fatia separada, nunca em lote.

## Termo padrão-ouro

`health/` — Componente de vida com dano, cura e sinal de morte.
Implementado à mão, completo, com teste. Serve de molde para todos os outros.
