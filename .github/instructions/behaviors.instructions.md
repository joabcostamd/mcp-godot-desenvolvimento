---
applyTo: 'behaviors/**'
---

# Regras de Conteúdo — Behaviors, Blueprints, Seeds e Testes

> Extraído do extinto `agente-02-extensoes.agent.md`. Aplica-se a behaviors/,
> blueprints/, seeds/, addons/ e tests/.

---

## 🧩 ESTRUTURA DE UM BEHAVIOR

```
behaviors/<nome>/
  behavior.json     ← Nome, descrição PT/EN, parâmetros (tipo, faixa, padrão),
                       sinais emitidos, dependências, gêneros, conflitos
  <nome>.tscn        ← O componente (cena Godot)
  <nome>.gd          ← O script
  test_<nome>.gd     ← Teste GdUnit4 obrigatório
  README.md          ← 1 parágrafo para busca semântica
```

O `behavior.json` liga **linguagem natural → componente verificado**.
"Quero que o inimigo morra em 3 tiros" → busca → `health` com `max_hp: 3`.

---

## 🧪 TESTES (GdUnit4) — 4 níveis obrigatórios

Cada behavior precisa passar por estes 4 níveis. Sem teste, o behavior não fecha.

1. **Estático** — JSON válido, script compila, nome não colide
2. **Unitário** — Lógica pura (ex.: vida chega a zero → emite sinal)
3. **Scene Runner** — Simula input real e espera sinal. **É aqui que se prova
   que funciona no jogo.**
4. **Composição** — O behavior junto de outros 3 não quebra

Teste instável (flaky) é regra, não exceção — ligue o tratamento desde o início.

---

## 🧱 REGRA DE OURO DO CONTEÚDO

**Comportamento é componente, não herança.** Um componente de vida é um nó
filho que se pluga em qualquer coisa. Classe gigante é o erro clássico.

---

## ✅ VALIDAÇÃO

```bash
python auditar.py  # Critérios C1-C6
```

---

## 🚫 NUNCA

- Criar behavior sem teste.
- Usar herança em vez de composição.
- "Melhorar" texto durante migração de documento.
