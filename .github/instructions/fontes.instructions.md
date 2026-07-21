---
applyTo: '**'
---

# Fontes obrigatorias de consulta

**Regra:** antes de implementar, leia a fonte do tema e **cite qual usou**
no relatorio. Sem fonte citada, a fatia nao fecha.

**Motivo:** a causa raiz da maioria dos erros deste projeto e inventar API do
Godot que nao existe. Ler a fonte custa minutos. Inventar custa a sessao inteira.

---

## Como usar

1. Ache o tema da sua fatia na tabela.
2. Leia a fonte antes de escrever a primeira linha.
3. No relatorio, escreva duas linhas: qual fonte usou e o que aprendeu dela.
4. Se a fonte contradiz o plano, **pare e escale.** A fonte ganha do plano.

Se o tema nao estiver na tabela: diga isso, proponha uma fonte, e peca aprovacao
antes de implementar. Nao invente.

**Protocolo de pesquisa:** Para pesquisas mais profundas, use o comando `/pesquise`
ou consulte `.github/instructions/pesquisa.instructions.md`.

---

## Godot — engine e API

| Tema | Onde |
|---|---|
| Qualquer classe, metodo ou sinal | Documentacao oficial do Godot, **versao 4.7** |
| ClassDB local | O cache do proprio MCP (`classdb_cache`) — mais confiavel que memoria |
| Plugin de editor, dock | Doc oficial: "Making plugins" e "Running code in the editor" |
| `@tool` e execucao no editor | Doc oficial: "Running code in the editor" |
| Depurador e erros em runtime | Doc oficial: classe `EditorDebuggerPlugin` |
| Arvore remota, editar com jogo rodando | Doc oficial: "Debugger panel" → Remote Scene Tree |
| Janela do jogo embutida | Doc oficial 4.4+: aba "Game" e embedding |
| Import de arte e audio | Doc oficial: "Import process" e presets de import |
| Export e templates | Doc oficial: "Exporting projects" |

**Aviso permanente:** a memoria do modelo sobre a API do Godot esta desatualizada
e mistura versoes 3.x com 4.x. Sempre confira na doc da versao 4.7.
Se a doc de 4.7 nao existir para o item, diga isso em vez de assumir.

---

## Padroes de arquitetura de jogo

| Tema | Onde |
|---|---|
| Padroes gerais (Command, Observer, State, Object Pool, Flyweight) | *Game Programming Patterns*, Robert Nystrom — texto completo gratis online |
| Padroes em Godot (composicao, sinais, autoload, FSM, strategy, decorator) | *Game Development Patterns with Godot 4*, Henrique Campos |
| Composicao sobre heranca | Mesma fonte acima. **Regra do projeto:** comportamento e componente (no filho), nunca classe gigante |
| Behavior trees e maquina de estado com editor | Plugin LimboAI |
| Biblioteca de composicao de nos | Nodot |

---

## Comportamentos de referencia (ler antes de escrever um termo novo)

| Onde | O que tem |
|---|---|
| `godotengine/godot-demo-projects` | Demos oficiais, com branch por versao |
| GDQuest Demos | Combate JRPG, builder isometrico, rhythm, tower defense, RPG tatico com pathfinding, plataforma de acao, visual novel |
| `awesome-godot-games` | Templates de FPS multiplayer, shooter top-down, boomer shooter com FSM e save, Open RPG, RTS |

**Regra:** leia a implementacao de referencia, entenda o padrao, e **escreva a sua
versao adaptada ao formato `behavior.json` do projeto.** Nao copie e cole cego —
codigo de demo raramente tem tratamento de erro nem parametros expostos.

---

## Testes

| Tema | Onde |
|---|---|
| Framework de teste | GdUnit4 — documentacao oficial |
| Simular input, esperar sinal | GdUnit4 → Scene Runner |
| Teste instavel (flaky) | GdUnit4 → retry e marcacao de teste nao deterministico |
| Rodar em CI | GdUnit4 → linha de comando, JUnit XML, action de GitHub |

**Regra do projeto:** teste de jogo e instavel por natureza (fisica, tempo).
Use o tratamento de flaky desde o comeco, ou a trava perde credibilidade.

---

## Assets

| Tema | Onde |
|---|---|
| Distribuicao de addon | AssetLib oficial do Godot (so licenca aberta) |
| Instalacao com versao travada | gd-plug |
| Empacotar em `.pck` separado | GodotAssetBundle |
| Assets CC0 | Kenney, KayKit, Poly Haven |

**Regra:** todo asset importado precisa de licenca declarada no manifesto.
Asset sem licenca clara e passivo juridico para quem publicar.

---

## Distribuicao e Mundo (ONDA 4)

| Tema | Onde |
|---|---|
| AssetLib oficial do Godot | godotengine.org/asset-library — submissao via formulario web |
| itch.io para ferramentas | itch.io/docs/creators — getting started, payments, pricing |
| gd-plug (plugin manager) | github.com/imjp94/gd-plug — 296★, MIT, version freeze |
| GitHub Sponsors | github.com/sponsors — $40M+ distribuidos, 4.2K+ orgs |
| Open source monetizacao | opensource.guide/getting-paid — modelos, casos reais |
| Steam Direct (Steamworks) | partner.steamgames.com/steamdirect — $100/fee, 30 dias |
| Metricas open source | opensource.guide/metrics — CHAOSS, discovery/usage/retention |
| Comunidade open source | opensource.guide/best-practices — moderacao, governanca |
| GitHub Discussions | docs.github.com/discussions — nativo, indexado pelo Google |
| Naming de produto | Analise de 50+ dev tools — padroes: metafora, composto, sigla |

**Regra:** ao publicar em qualquer plataforma, declare a licenca (MIT) e a versao do Godot testada.
Nunca publique sem o Shardbreaker como prova — sem jogo publicado, nao tem credibilidade.

---

## Design de jogo

| Tema | Onde |
|---|---|
| Core loop, MDA, curvas de dificuldade | Game Design Library |
| Modos de falha do loop | Sem escalada · sem escolha real · recompensa distante demais · estrategia degenerada |

**Regra:** ao avaliar design, nomeie qual dos quatro modos de falha aparece.
"Esta chato" nao e achado. "Nao tem escalada: a decima onda e igual a primeira" e.

---

## MCP e Copilot

| Tema | Onde |
|---|---|
| Protocolo MCP | Especificacao oficial do Model Context Protocol |
| Instrucoes, prompts e agentes do Copilot | Doc oficial do VS Code: customizacao do chat |
| Trabalho paralelo com varios agentes | Doc do git: `git worktree` |

**Fato registrado:** o mecanismo de *sampling* do MCP foi descontinuado na
especificacao de 2026-07-28. Nao construa nada que dependa dele.

---

## Ordem de confianca quando as fontes discordam

1. Codigo real deste repositorio (leia com `git show`, nao de memoria)
2. Documentacao oficial do Godot 4.7
3. Especificacao oficial do MCP / doc do VS Code
4. Livros e demos de referencia
5. Discussoes de comunidade
6. **Memoria do modelo — ultimo lugar, sempre**

Se 1 e 2 discordam, o codigo do repositorio ganha, mas **avise**: pode ser bug.

