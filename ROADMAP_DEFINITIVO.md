
# ROADMAP DEFINITIVO — MCP Godot Agent

> **Público:** IA agêntica (GitHub Copilot no VS Code) e o humano responsável.
> **Este arquivo manda.** Se qualquer outro documento discordar deste, este vence.
> **Local correto:** raiz do repositório.

---

## 0. COMO LER ESTE DOCUMENTO

Este roadmap tem 5 ondas. Cada onda tem fatias. Cada fatia tem uma **ficha de 10 campos**
com o "como fazer", e essas fichas vivem em `.github/roadmap/ONDA_N_*.md`.

Aqui você encontra: a ordem, as dependências, o critério de saída de cada onda,
e a lista completa das 80 pendências com seu destino.

**Regra de ouro:** nenhuma fatia começa antes da anterior estar fechada e aprovada
pelo humano. Onda só abre quando o critério de saída da anterior for atingido.

---

## 1. O QUE ESTAMOS CONSTRUINDO (e o que não estamos)

**Somos:** o único MCP que é dono do processo inteiro de fazer um jogo em Godot —
da ideia ao lançamento — com travas reais que impedem pular etapa e com verificação
que a IA não consegue fabricar.

**Não somos:** um cliente de chat, uma engine nova, um editor visual, um gerador de
código sem verificação.

**Métrica de engenharia (já atingida uma vez):** taxa de correção manual abaixo de 15–20%
num jogo pequeno testado ponta a ponta. Resultado real no Breakout: 0%.

**Métrica de produto (nova, ainda não medida):** quantas pessoas **terminam** um jogo.
Terminar vale mais que gerar. Toda decisão de prioridade responde a esta pergunta.

**Decisões declaradas (não reabrir sem motivo forte):**

| Decisão | Escolha | Motivo |
|---|---|---|
| Cliente de IA | Copilot no VS Code | Sampling do MCP foi descontinuado na spec 2026-07-28; construir cliente próprio = reconstruir o Cline |
| Plataforma | **Windows primeiro** | Todo o LEARNINGS e os workarounds são Windows. Linux/Mac depois, declarado |
| Dimensão | **2D primeiro** | 3D custa 3–5x por comportamento. 3D só depois de 30 termos 2D maduros |
| Aprendizado por reforço para playtest | **Fora de escopo permanente** | Custo altíssimo, retorno baixo para jogo indie pequeno |
| Netcode, matchmaking, dificuldade adaptativa | **Fora de escopo** até um jogo real exigir | Já classificados como marginais |
| Editor visual de HUD próprio | **Fora de escopo permanente** | É reconstruir o editor do Godot |

---

## 2. AS 5 ONDAS

```
ONDA 0  Destravar          dias      — nada avança sem isto
ONDA 1  Acessibilidade     semanas   — o produto vira usável por outra pessoa
ONDA 2  O fosso            meses     — a barreira dos 70% cai
ONDA 3  Qualidade de jogo  semanas   — o jogo fica bom, não só funcional
ONDA 4  Mundo              contínuo  — outras pessoas descobrem e usam
```

---

## ONDA 0 — DESTRAVAR

**Objetivo:** consertar o que está quebrado ou contraditório antes de construir por cima.
**Ficha detalhada:** `.github/roadmap/ONDA_0_destravar.md`
**Critério de saída:** `auditar.py` passa 6/6, `/plan` e `/act` funcionam no Copilot,
zero referência a Cline, LICENSE existe, números dos documentos batem com o código.

| # | Fatia | Marcação | Pendências que fecha |
|---|---|---|---|
| 0.A | Corrigir bug do Passo 8 (ramo SÊNIOR sem encadeamento) | AUTO | P1 |
| 0.B | Auditar fechamento da Fatia 0.9 (3 provas faltantes) | SÊNIOR | P2 |
| 0.C | Decidir 0.7b (lean vs full) e registrar | SÊNIOR | P3 |
| 0.D | Migração `.clinerules` → `.github/` + expurgo de Cline | AUTO | P29 parcial, L26 |
| 0.E | LICENSE (MIT) + CONTRIBUTING + CODE_OF_CONDUCT + SECURITY | AUTO | P49, D4, L15 |
| 0.F | `docs_sync`: números gerados do código, nunca à mão | AUTO | D1 |
| 0.G | Expurgo de caminhos pessoais + `journal/` no gitignore | AUTO | D2, D6 |
| 0.H | Protocolo anti-conflito MCP ↔ editor aberto | SÊNIOR | **L1** |
| 0.I | Detecção de pasta sincronizada (OneDrive) | AUTO | **L2** |
| 0.J | Normalização de nome com acento e espaço | AUTO | L12 |
| 0.K | Guarda de propriedade intelectual de terceiros | SÊNIOR | **L6** |
| 0.L | Bug `set_node_property` / `get_node_property` | SÊNIOR | P4 |

---

## ONDA 1 — ACESSIBILIDADE

**Objetivo:** uma pessoa que não é você consegue instalar, abrir e jogar algo.
**Ficha detalhada:** `.github/roadmap/ONDA_1_acessibilidade.md`
**Critério de saída:** uma pessoa não-programadora, sem ajuda sua, sai de zero
até um jogo rodando em menos de 20 minutos. Testado com gente de verdade, não simulado.

| # | Fatia | Marcação | Pendências |
|---|---|---|---|
| 1.A | Instalador de um comando (`init`) | SÊNIOR | P7, P25 |
| 1.B | Instalar export templates no init | AUTO | P42, L7 |
| 1.C | Suporte a mais de um provedor de IA no init | AUTO | L14 |
| 1.D | Custo e orçamento de tokens visível | SÊNIOR | **L4** |
| 1.E | Dock v1 — 3 zonas + 4 botões | SÊNIOR | P28, P40, P48 |
| 1.F | Erro amigável universal (todo erro passa pelo tradutor) | AUTO | P13 |
| 1.G | Reestruturação documental (executar o plano) | SÊNIOR | D3, D5, D7, P18–P24 |
| 1.H | Manual do usuário gerado por código | AUTO | Manual |
| 1.I | Tutoriais 1 a 4 (só depois do instalador) | SÊNIOR | Tutorial |
| 1.J | `quick_start`: frase → jogável em 10 min | SÊNIOR | P9 |
| 1.K | Modo remix: clonar jogo-semente | AUTO | P14 |
| 1.L | Vitrine de gêneros (prompts prontos) | AUTO | P15 |
| 1.M | Skills exportáveis + modo guiado conversacional | SÊNIOR | P8, P11, P33 |
| 1.N | `llms.txt` + README bilíngue | AUTO | P17, D3, D5 |
| 1.O | Degradação elegante sem internet | AUTO | L13 |
| 1.P | Telemetria opt-in do próprio MCP | SÊNIOR | **L9** |
| 1.Q | Histórico de versões jogáveis (por screenshot) | SÊNIOR | **L17** |

---

## ONDA 2 — O FOSSO

**Objetivo:** derrubar a barreira dos 70%. É a onda mais longa e a mais valiosa.
**Ficha detalhada:** `.github/roadmap/ONDA_2_fosso.md`
**Critério de saída:** 30 comportamentos com teste passando, 3 blueprints de gênero,
3 jogos-semente, e taxa de correção manual abaixo de 15% num jogo novo do zero.

| # | Fatia | Marcação | Pendências |
|---|---|---|---|
| 2.A | Formato canônico `behavior.json` + 1 termo padrão-ouro | SÊNIOR | P35 |
| 2.B | Adotar GdUnit4 (Scene Runner + flaky handling) | SÊNIOR | P36 |
| 2.C | Critério novo no `auditar.py` para behaviors | AUTO | P37 |
| 2.D | Parâmetros de comportamento em `.tres` | SÊNIOR | P46 |
| 2.E–2.Z | 30 comportamentos, **um por fatia** | AUTO/SÊNIOR | P10 |
| 2.AA | Teste de composição e de contrato | SÊNIOR | P38 |
| 2.AB | Blueprints de gênero (3 primeiros) | SÊNIOR | Modelos |
| 2.AC | Jogos-semente (3 primeiros) | SÊNIOR | Sementes |
| 2.AD | Versionamento e migração de behaviors | SÊNIOR | P44, L10 |
| 2.AE | Memória semântica do projeto (RAG local) | SÊNIOR | P5 |
| 2.AF | Índice de entidades ("quais nós são inimigos") | SÊNIOR | P12 |
| 2.AG | Docs do Godot offline como tool | AUTO | P6 |
| 2.AH | Classificador editar-ao-vivo vs reiniciar | SÊNIOR | P39 |
| 2.AI | Ajuste ao vivo (código inverso) com aprovação | SÊNIOR | P45, P47 |
| 2.AJ | Captura unificada de erro em tempo real | SÊNIOR | Autocorreção |
| 2.AK | Receitas de conserto + loop com trava | SÊNIOR | Autocorreção |
| 2.AL | Pacote de assets com style lock e licença | SÊNIOR | P32, P41 |
| 2.AM | Segurança de asset de terceiros | SÊNIOR | L23 |
| 2.AN | Unificar as 4 taxonomias de tools | SÊNIOR | P29 |
| 2.AO | Auditoria de descrições + lean como padrão | AUTO | P30 |
| 2.AP | Ops de roteiro/batch | AUTO | P31 |
| 2.AQ | Compactação automática de contexto | SÊNIOR | L21 |
| 2.AR | Roteamento de modelo por tarefa | SÊNIOR | L22 |
| 2.AS | Semente de reprodutibilidade | AUTO | L20 |
| 2.AT | Unificar os 3 históricos de desfazer | SÊNIOR | **L3** |
| 2.AU | Orçamento de tempo por gate | AUTO | L11 |

---

## ONDA 3 — QUALIDADE DE JOGO

**Objetivo:** o MCP passa a opinar sobre se o jogo está bom, não só se compila.
**Ficha detalhada:** `.github/roadmap/ONDA_3_4_qualidade_mundo.md`
**Critério de saída:** o `fun_report` roda sozinho e acusa pelo menos um problema
real de design num jogo de teste, confirmado por playtest humano.

| # | Fatia | Marcação | Pendências |
|---|---|---|---|
| 3.A | Playtest camada 1: smoke automático | AUTO | P52 |
| 3.B | Playtest camada 2: personas scriptadas (Scene Runner) | SÊNIOR | P52 |
| 3.C | Playtest camada 3: agente LLM pontual | SÊNIOR | P52 |
| 3.D | `fun_report` com 4 sinais + modo de falha nomeado | SÊNIOR | P53 |
| 3.E | Gate dos primeiros 5 minutos | SÊNIOR | P54 |
| 3.F | Gate de dívida de complexidade | SÊNIOR | P16 |
| 3.G | Gate de design do core loop | SÊNIOR | P43 |
| 3.H | Modo professor (explicar o que foi feito) | AUTO | L18 |
| 3.I | O "primeiro não" bem feito (escopo conversacional) | SÊNIOR | L19 |
| 3.J | Disclosure de conteúdo IA no release_checklist | AUTO | **L5** |
| 3.K | Modo revisor adversarial para o Agente 2 | SÊNIOR | L24 |

---

## ONDA 4 — MUNDO

**Objetivo:** outras pessoas descobrem, usam e sustentam o projeto.
**Ficha detalhada:** `.github/roadmap/ONDA_3_4_qualidade_mundo.md`
**Critério de saída:** 3 jogos publicados por pessoas que não são você.

| # | Fatia | Marcação | Pendências |
|---|---|---|---|
| 4.A | Publicar na AssetLib oficial | AUTO | P50 |
| 4.B | Pacotes e templates no itch.io | AUTO | P50 |
| 4.C | GitHub Sponsors com camadas específicas | AUTO | P51 |
| 4.D | Nome e identidade do produto | SÊNIOR | L16 |
| 4.E | Publicar o Shardbreaker como prova | SÊNIOR | Distribuição |
| 4.F | Canal de comunidade (Discussions/Discord) | AUTO | L15 |
| 4.G | Definir e medir a métrica de produto | SÊNIOR | **L25** |

---

## 3. ÍNDICE DAS 80 PENDÊNCIAS

**P1–P8** processo e gaps iniciais · **P9–P17** experiência de não-programador ·
**P18–P24** documentos (D1–D7) · **P25–P34** interface e host ·
**P35–P44** biblioteca e testes · **P45–P54** dock, inverso, distribuição, diversão ·
**L1–L26** lacunas da análise final.

Nenhuma pendência foi descartada. Todas aparecem em alguma onda acima.

---

## 4. REGRAS QUE VALEM O TEMPO TODO

1. **Uma fatia por vez.** Nunca comece N+1 antes de N estar aprovada pelo humano.
2. **Prova, nunca alegação.** `git diff` real com `@@`, código colado, output de teste completo.
   "Passou!" sem prova não vale. "É bug pré-existente" exige `git blame` ou `git log -p`.
3. **Quem decide se está pronto é o portão, não a IA.** `auditar.py` é fail-closed.
4. **Nunca commitar sozinha.** Propor o commit e esperar aprovação.
5. **Checkpoint antes de operação destrutiva.** Sempre.
6. **Consultar a fonte antes de implementar** (ver `.github/instructions/fontes.instructions.md`)
   e citar qual usou. Sem fonte citada, a fatia não fecha.
7. **Parar e escalar é sucesso**, não fracasso. Insistir num loop é fracasso.
8. **Rollup-first:** feature nova entra como `op` de rollup, não como tool de topo.
9. **Mover é mover.** Em fatia de migração, não "melhore" o texto — melhoria é fatia separada.
10. **Territórios:** ver `AGENTS.md`. Nunca edite fora do seu.

---

## 5. O QUE FAZER QUANDO O ROADMAP ESTIVER ERRADO

Ele vai estar. O Shardbreaker (jogo real de teste) manda mais que este documento:
se uma fatia da Onda 2 nunca doeu no uso real, ela desce; se uma dor apareceu e
não está aqui, ela vira fatia nova e sobe. Registre a mudança e o motivo em
`.roadmap_progress.json`, não altere a ordem em silêncio.

**Sinal de parar de construir:** quando novas fatias deixarem de mover a métrica de
produto (pessoas que terminam jogos), pare. Lista acabar não é critério.

