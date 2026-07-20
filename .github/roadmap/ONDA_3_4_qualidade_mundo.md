---
applyTo: '**'
---

# ONDAS 3 e 4 — QUALIDADE DE JOGO e MUNDO

---

# ONDA 3 — QUALIDADE DE JOGO

**Objetivo:** o MCP passa a opinar se o jogo esta **bom**, nao so se compila.
**Criterio de saida:** o relatorio automatico acusa pelo menos um problema real
de design num jogo de teste, confirmado depois por playtest humano.

Este e o segundo fosso do produto. Todo concorrente verifica codigo.
Nenhum critica design.

---

## O que a pesquisa estabelece (base das fatias 3.A a 3.G)

**Playtest manual nao escala.** Testar um jogo grande a mao chega a centenas de
milhares de horas. Bots por script tambem tem teto: nao aprendem, exigem
especialista para escrever, e certos casos nao sao scriptaveis.

**Agentes conseguem substituir parte do playtest humano.** Agentes de IA jogando
funcionam como proxy de testador para mapear curva de dificuldade e balanceamento,
com desempenho correlacionado as avaliacoes humanas.

**Nao existe medidor de diversao — existem proxies.** O mais forte e a relacao
entre **taxa de abandono** e **taxa de aprovacao** de fase. Prever abandono medio
serve para corrigir fases pouco engajantes **antes** de lancar.

**O vale e mais perigoso que o pico.** Trecho sem desafio esvazia o engajamento em
silencio: o jogador nao abandona com raiva, ele se afasta. Esse abandono por tedio
e mais lento e mais dificil de diagnosticar que o por frustracao.
O relatorio precisa acusar **os dois**.

**A curva inicial decide tudo.** Retencao dos primeiros dias correlaciona
fortemente com como se sentem as primeiras sessoes.

---

## Fatia 3.A — Playtest camada 1: smoke automatico

**5. Como fazer** Rodar o jogo sem interface grafica e verificar: abre, nao trava,
FPS minimo, console sem erro. Custo quase zero — a maior parte ja existe no MCP.

**7. Criterios** Jogo quebrado e reprovado; jogo saudavel passa. **Marcacao** `[AUTO]`

---

## Fatia 3.B — Playtest camada 2: personas scriptadas

**5. Como fazer** Use o Scene Runner do GdUnit4 para simular input real e esperar
sinais. Tres personas fixas: **apressado** (avanca sempre), **cauteloso**
(espera, evita risco), **explorador** (testa os limites do cenario).

Cada persona gera: terminou ou nao, tempo, tentativas, caminho percorrido.

Isto sozinho cobre a maior parte do valor do playtest automatizado.

**6. Armadilhas** Teste instavel e regra, nao excecao — ligue o tratamento de
flaky desde o inicio.

**7. Criterios** As 3 personas rodam num jogo-semente e produzem metrica.
**Marcacao** `[SENIOR]`

---

## Fatia 3.C — Playtest camada 3: agente LLM pontual

**5. Como fazer** O MCP envia screenshot e estado; o modelo decide a acao.
Caro em token → use pontualmente (validar um nivel novo), **nunca** continuamente.

**Aprendizado por reforco fica fora de escopo permanente:** custo altissimo,
retorno baixo para jogo indie pequeno.

**7. Criterios** Roda sob demanda, com custo estimado antes de comecar.
**Marcacao** `[SENIOR]`

---

## Fatia 3.D — `fun_report`

**1. O que e** Relatorio com os quatro sinais medidos por agentes, sem jogador humano.

**5. Como fazer**

| Sinal | Como medir | O que indica |
|---|---|---|
| Taxa de aprovacao | % de agentes que terminam | Facil demais (>95%) ou frustrante (<20%) |
| Tentativas ate vencer | media e desvio | Pico de dificuldade escondido |
| Variedade de estrategia | quantas rotas distintas vencem | Estrategia degenerada (uma domina) |
| Escalada | comparar inicio, meio e fim | Repeticao sem progressao |

Os quatro mapeiam exatamente nos quatro modos de falha do core loop:
**sem escalada · sem escolha real · recompensa distante demais · estrategia degenerada.**

O relatorio **nomeia o modo de falha**, nao diz "esta chato".
Errado: "o nivel 3 esta ruim".
Certo: "nivel 3 sem escalada: a decima onda e igual a primeira".

**6. Armadilhas — honestidade e vantagem competitiva.**
O relatorio precisa dizer, com todas as letras: *isto mede indicios de engajamento,
nao diversao; playtest humano continua necessario.* Quem promete "medidor de
diversao" perde credibilidade no primeiro teste.

Acuse tambem o **vale**, nao so o pico.

**7. Criterios** Num jogo com problema plantado de proposito, o relatorio acusa
o modo de falha certo. **Marcacao** `[SENIOR]`

---

## Fatia 3.E — Gate dos primeiros 5 minutos

**2. Por que** E a maior alavanca de retencao que existe.

**5. Como fazer** Rodar as personas so no comeco do jogo e exigir: a pessoa
entende o que fazer, tem uma vitoria pequena, e nao morre repetidamente antes
de entender. Bloqueia avanco de fase se falhar.

**Marcacao** `[SENIOR]`

---

## Fatias 3.F a 3.K — resumidas

| # | Fatia | Essencial | Marcacao |
|---|---|---|---|
| 3.F | Gate de divida de complexidade | Codigo assistido por IA acumula complexidade e warnings que nao voltam a cair. Medir por fase e travar crescimento sem justificativa | `[SENIOR]` |
| 3.G | Gate de design do core loop | Os 4 modos de falha viram checklist automatico | `[SENIOR]` |
| 3.H | Modo professor | Depois de gerar, explicar em 3 linhas o que foi feito e por que. Reduz dependencia da IA | `[AUTO]` |
| 3.I | O "primeiro nao" bem feito | "MMO open world" nao pode receber "nao da". Recebe: "isso sao 2 anos; a versao de 2 semanas e X — topa?" | `[SENIOR]` |
| 3.J | Disclosure de conteudo IA | A Steam exige declarar uso de IA na publicacao. O produto inteiro gera conteudo por IA. Sem isso, voce entrega usuarios a uma rejeicao | `[AUTO]` |
| 3.K | Modo revisor adversarial | Em fatia critica, o Agente 2 audita em vez de implementar. Metade da velocidade, ataca o problema numero um: evidencia fabricada | `[SENIOR]` |

---

# ONDA 4 — MUNDO

**Objetivo:** outras pessoas descobrem, usam e sustentam o projeto.
**Criterio de saida:** 3 jogos publicados por pessoas que nao sao voce.

---

## O que a pesquisa estabelece

**Comunidade nao cresce por feature, cresce por prova.** A coisa mais persuasiva
nao e documentacao: e **publicar um jogo feito com a ferramenta**. Ferramenta de
gamedev se vende pelo jogo que produziu.

**Canais que funcionam:** AssetLib oficial (instalacao de dentro do editor, exige
licenca aberta) · itch.io (publicar sem custo, "pague quanto quiser") ·
redes com GIF curto de gameplay · comunidades de Godot e gamedev · game jam.

**Monetizacao viavel para solo:** patrocinio recorrente com camadas **especificas**
("resposta a issue em 48h" converte muito mais que "apoie meu trabalho") ·
open core (nucleo aberto, pacotes de assets e blueprints pagos) · venda de assets
fora da AssetLib, que so aceita licenca aberta.

**Nao viavel agora:** servico hospedado e consultoria — consomem o tempo que
voce nao tem.

---

## Fatias 4.A a 4.G

| # | Fatia | Essencial | Marcacao |
|---|---|---|---|
| 4.A | Publicar na AssetLib | **Bloqueado ate a Fatia 0.E (LICENSE) existir** | `[AUTO]` |
| 4.B | itch.io | Pacotes de assets e templates. Canal para o que nao cabe na AssetLib | `[AUTO]` |
| 4.C | Patrocinio com camadas | Beneficio nomeado, nunca generico | `[AUTO]` |
| 4.D | Nome e identidade | `mcp-godot-desenvolvimento` descreve, nao vende, e nao e pesquisavel | `[SENIOR]` |
| 4.E | Publicar o Shardbreaker | **A prova mais forte que existe.** Publique o jogo e mostre o processo | `[SENIOR]` |
| 4.F | Canal de comunidade | Discussions ou Discord + `CONTRIBUTING` (ja feito em 0.E) | `[AUTO]` |
| 4.G | Metrica de produto | **Quantas pessoas terminam um jogo.** Definir e medir. Terminar vale mais que gerar | `[SENIOR]` |

---

## Ordem sugerida da Onda 4

1. LICENSE (ja na Onda 0) — destrava tudo
2. Publicar o Shardbreaker — a prova
3. AssetLib — o canal de instalacao
4. Comunidade — onde as pessoas pedem socorro
5. Patrocinio — so depois de existir gente usando
6. Nome — quando houver o que nomear

Patrocinio antes de usuario nao funciona. Nome antes de produto tambem nao.

