---
applyTo: '**'
---

# ONDA 2 — O FOSSO

**Objetivo:** derrubar a barreira dos 70% — o ponto em que codigo gerado por IA
parece bom no primeiro rascunho e comeca a quebrar conforme features sao somadas.
**Criterio de saida:** 30 comportamentos com teste passando, 3 blueprints de genero,
3 jogos-semente, e taxa de correcao manual abaixo de 15% num jogo novo do zero.

Esta e a onda mais longa e a mais valiosa. Ela e o que nenhum concorrente tem.

---

## A ideia central (leia antes de qualquer fatia desta onda)

A IA nao deve **gerar codigo do zero** para coisas que ja se sabe como fazer.
Ela deve **instanciar e parametrizar blocos ja verificados**.

```
1. BLUEPRINT (genero)   JSON: loop, sistemas, criterios de pronto
2. BEHAVIOR (termo)     cena + script + parametros + TESTE
3. SEED (semente)       jogo minimo completo, clonavel
```

Regra estrutural: **comportamento e componente, nao heranca.** Um componente de
vida e um no filho que se pluga em qualquer coisa. E isso que permite combinar
30 termos em milhares de jogos. Classe gigante e o erro que a IA comete sozinha.

---

## Fatia 2.A — Formato canonico e o primeiro termo

**1. O que e** Definir o formato de um comportamento e implementar **um** a mao,
completo, como padrao-ouro.

**2. Por que agora** Sem padrao-ouro, os 30 termos saem em 30 formatos diferentes.

**3. Arquivos** `behaviors/health/` (novo) · `schemas/behavior.schema.json`

**4. Fonte** *Game Development Patterns with Godot 4* (composicao sobre heranca) ·
`godot-demo-projects` · Nodot.

**5. Como fazer**

Estrutura de cada termo:
```
behaviors/<nome>/
  behavior.json     nome, descricao em linguagem natural, sinonimos PT/EN,
                    parametros (tipo, faixa, padrao), sinais emitidos,
                    dependencias, generos aplicaveis, conflitos
  <nome>.tscn       o componente
  <nome>.gd         o script
  test_<nome>.gd    teste obrigatorio
  README.md         1 paragrafo, para busca semantica
```

O `behavior.json` e o coracao: e ele que liga **linguagem natural → componente
verificado**. "Quero que o inimigo morra em 3 tiros" → busca → `health` com
`max_hp: 3`.

Implemente `health` inteiro, a mao, com teste rodando. Ele vira o molde.

**6. Armadilhas**
- Nao use heranca. Componente e no filho.
- Parametro sem faixa declarada gera valor absurdo depois.
- Nome que se confunde com outro termo degrada a busca — exija distinguibilidade.

**7. Criterios de aceite**
- `behavior.json` valida contra o schema
- O componente funciona numa cena de teste
- O teste passa com output colado
- O termo e parametrizavel sem editar codigo

**8. Como provar** Teste rodando + cena de demonstracao + JSON validado.

**9. Regressao** Nenhuma (codigo novo).

**10. Marcacao** `[SENIOR]` — define o padrao de tudo que vem depois.

---

## Fatia 2.B — Adotar o framework de teste

**1. O que e** GdUnit4 como framework oficial dos comportamentos.

**2. Por que agora** 30 termos sem teste sao 30 formas novas de quebrar.

**3. Arquivos** `addons/gdUnit4/` · `tests/` · configuracao de CI

**4. Fonte** Documentacao oficial do GdUnit4, em especial **Scene Runner**
e o tratamento de **teste instavel**.

**5. Como fazer**
Instale o framework. Configure execucao por linha de comando com relatorio.

Quatro niveis de teste por termo:
1. **Estatico** — JSON valida, script compila, nome nao colide
2. **Unitario** — logica pura (vida chega a zero → emite sinal)
3. **De cena (Scene Runner)** — simula input real e espera o sinal.
   E aqui que se prova que funciona **no jogo**
4. **De composicao** — o termo junto de outros 3 nao quebra.
   E o teste que ninguem faz e que evita a barreira dos 70%

Ligue o tratamento de teste instavel desde o inicio: jogo tem fisica e tempo,
teste que passa 9 de 10 vezes destroi a confianca na trava.

**6. Armadilhas** Teste que passaria mesmo com implementacao vazia nao vale nada.
Todo teste precisa de assert sobre comportamento, nao sobre existencia.

**7. Criterios de aceite**
- Os 4 niveis rodam no termo `health`
- Roda por linha de undo e gera relatorio
- Teste instavel e marcado, nao mascarado

**8. Como provar** Saida completa da suite.

**9. Regressao** Testes Python existentes continuam passando.

**10. Marcacao** `[SENIOR]`

---

## Fatia 2.C — Portao para comportamentos

**1. O que e** Criterio novo no `auditar.py`.

**5. Como fazer**
Adicione verificacao fail-closed: todo diretorio em `behaviors/` precisa ter
`behavior.json` valido, teste existente, e nome distinguivel dos demais
(distancia minima de similaridade). Falta qualquer um → falha.

**7. Criterios de aceite** Termo sem teste faz `auditar.py` falhar.
**8. Como provar** Crie um termo incompleto de proposito e cole a falha.
**10. Marcacao** `[AUTO]`

---

## Fatia 2.D — Parametros em recurso de dados

**1. O que e** Cada comportamento expoe seus numeros num `.tres`, nao no script.

**2. Por que agora** **E o pre-requisito do ajuste ao vivo (2.AI).** Escrever num
arquivo de dados e seguro; reescrever codigo a partir de estado de runtime nao e.

**3. Arquivos** `behaviors/*/`

**4. Fonte** Doc oficial do Godot: `Resource` e `@export`.

**5. Como fazer**
Crie um `Resource` por comportamento com os parametros exportados.
O componente le do recurso. O jogo rodando le do mesmo recurso.
Assim, mudar um numero e alterar **dados**, nunca codigo.

**6. Armadilhas** Sub-recurso pode ser substituido pela versao em cache ao salvar,
apagando a edicao. Nunca salve com o jogo rodando (ver 2.AI).

**7. Criterios de aceite** Trocar valor no `.tres` muda o jogo sem editar script.
**8. Como provar** Antes e depois, com o `.tres` colado.
**10. Marcacao** `[SENIOR]`

---

## Fatias 2.E a 2.Z — os 30 comportamentos

**Uma fatia por termo. Nunca em lote.**

Pedir "crie 30 comportamentos" produz 30 esqueletos falsos — e o padrao de falha
ja conhecido deste projeto.

**Processo por termo:**
1. Leia a implementacao de referencia na fonte (demo oficial ou GDQuest)
2. Escreva a sua versao no formato de 2.A
3. Escreva os 4 niveis de teste
4. Rode e cole o output
5. Cite a fonte que usou

**Lista inicial (30):**

| Grupo | Termos |
|---|---|
| Movimento | plataforma · top-down · primeira pessoa · veiculo |
| Combate | vida/dano · hitbox/hurtbox · projetil · cadencia · knockback · invulnerabilidade temporaria |
| Inimigo | perseguir · patrulhar · linha de visao · spawner de ondas · maquina de estados |
| Progressao | inventario · coleta · XP/nivel · upgrade · moeda |
| Sistema | save/load · pausa · menu principal · transicao de cena · audio com bus · configuracoes |
| Feedback | screen shake · texto flutuante · particula de impacto · hit stop |
| Estrutura | timer de rodada · condicao de vitoria · condicao de derrota |

**30 termos com teste valem mais que 130 sem.** Nao acelere pulando teste.

Ritmo realista: 1 a 2 termos por sessao.

**Marcacao:** `[AUTO]` para termos simples, `[SENIOR]` para os que envolvem fisica,
maquina de estados ou persistencia.

---

## Fatias 2.AA a 2.AC — composicao, blueprints e sementes

| # | Fatia | Essencial |
|---|---|---|
| 2.AA | Teste de composicao e contrato | Termos combinados nao quebram. Se um termo muda parametro, o CI acusa em todos os blueprints que o usam. Estenda o `contract_snapshot.py` existente |
| 2.AB | Blueprints de genero (3) | JSON declarativo: loop, sistemas, criterios de pronto. Reaproveite os `game_patterns` que ja existem |
| 2.AC | Jogos-semente (3) | Jogo minimo completo e comentado por genero. O Breakout ja e o primeiro |

---

## Fatias 2.AD a 2.AU — fichas resumidas

Serao expandidas pelo `/plan` quando chegar a vez.

| # | Fatia | Essencial | Marcacao |
|---|---|---|---|
| 2.AD | Versionamento de behaviors | Mudar um termo quebra jogos ja criados. Versao por termo + migracao | `[SENIOR]` |
| 2.AE | Memoria semantica (RAG local) | Indexar GDD, decisoes e codigo. Elimina o ritual de colar documentos | `[SENIOR]` |
| 2.AF | Indice de entidades | Mapa "inimigo" → quais nos. Sem isso, "deixa os inimigos mais rapidos" nao funciona | `[SENIOR]` |
| 2.AG | Docs do Godot offline | Ataca a causa raiz de inventar API. Complementa o `classdb_cache` | `[AUTO]` |
| 2.AH | Classificador editar-ao-vivo | Valor → arvore remota, sem reiniciar. Estrutura → reiniciar. Hoje a IA reinicia sempre | `[SENIOR]` |
| 2.AI | Ajuste ao vivo (codigo inverso) | Capturar → acumular → mostrar → **humano aprova** → parar o jogo → checkpoint → escrever no `.tres` → verificar. **Nunca escrever com o jogo rodando** | `[SENIOR]` |
| 2.AJ | Captura de erro em tempo real | `EditorDebuggerPlugin` (estruturado) + autoload de log + LSP (antes de rodar) | `[SENIOR]` |
| 2.AK | Receitas de conserto | 7 receitas cobrem a maioria: no nao encontrado · sinal para metodo inexistente · tipo incompativel · recurso ausente · autoload faltando · divisao por zero · null por ordem de init. **Automatize so a confirmacao, nunca a aplicacao** | `[SENIOR]` |
| 2.AL | Pacote de assets | Pasta + manifesto com licenca e style kit (paleta, resolucao, pivo). Fora do repo principal | `[SENIOR]` |
| 2.AM | Seguranca de asset externo | Verificar origem. A sandbox de GDScript tem bypasses conhecidos e documentados | `[SENIOR]` |
| 2.AN | Unificar taxonomias | Hoje sao 4 paralelas. Uma so, por **intencao**, 5–7 grupos: descobrir · criar · ver · testar · consertar · publicar · processo | `[SENIOR]` |
| 2.AO | Auditoria de descricoes | Descricao inchada custa token em toda requisicao e piora a escolha. Modo lean como padrao | `[AUTO]` |
| 2.AP | Ops de roteiro | "Criar inimigo completo" = 6 passos internos, 1 chamada | `[AUTO]` |
| 2.AQ | Compactacao de contexto | Resumo rolante automatico. Evita degradacao em projeto de mais de um mes | `[SENIOR]` |
| 2.AR | Roteamento de modelo | Tarefa simples no modelo barato, diagnostico no bom | `[SENIOR]` |
| 2.AS | Semente de reprodutibilidade | Mesma frase, mesmo resultado. Permite testar regressao de comportamento | `[AUTO]` |
| 2.AT | Unificar os 3 desfazer | UndoRedo + git + botao Reverter sao 3 historicos independentes hoje. Definir quem manda e mostrar **um** historico | `[SENIOR]` |
| 2.AU | Orcamento de tempo por gate | Gate de 3 minutos ninguem usa. Teto de tempo + modo rapido/completo | `[AUTO]` |
| 2.AV | **Editor visual de BT no Godot** | Editor dock integrado ao Godot para montar behaviors visualmente (drag-and-drop). Inspirado no LimboAI (2.9k⭐): nos, conexoes, blackboard, debug ao vivo. Permite nao-programadores ajustarem comportamentos sem codigo. GDScript puro (sem C++). | `[SENIOR]` |
| 2.AW | **Preparar estrutura para AssetLib** | Organizar addons/ para publicacao na AssetLib oficial do Godot: plugin.cfg, icone, descricao, tags, capturas de tela, tutorial. **Sem publicar** — apenas deixar a estrutura pronta para quando a ONDA 4 chegar. | `[AUTO]` |
| 2.AX | **+4 jogos-exemplo** | Criar 4 jogos completos usando behaviors do arsenal: (1) platformer — pulo, inimigos, moedas, (2) rpg — combate, npcs, xp, loja, (3) puzzle — combinacao, grid, (4) shooter — top-down, waves, power-ups. Cada um em `example_project/<genero>/`. Complementam o Breakout existente. | `[SENIOR]` |

