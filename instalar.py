#!/usr/bin/env python3
"""
instalar.py - Instalador automatico da nova estrutura de documentos.

O QUE FAZ (sem voce precisar mexer em nada):
  1. Cria as pastas .github/, docs/, journal/
  2. ESCREVE sozinho os 4 documentos do Lote 1 (estao embutidos aqui dentro)
  3. Migra estrutura antiga -> .github/instructions/ e .github/prompts/
  4. Adiciona frontmatter applyTo em cada instructions
  5. Move os diarios pessoais para journal/ e poe journal/ no .gitignore
  6. Remove arquivos obsoletos
  7. Relata tudo que fez e o que ficou pendente

COMO USAR:
  Coloque SOMENTE este arquivo na RAIZ do repositorio e rode:

      python instalar.py --teste     (mostra o que faria, nao muda nada)
      python instalar.py             (executa de verdade)

SEGURANCA:
  - Nao apaga nada, exceto arquivos explicitamente listados como obsoletos
  - Usa 'git mv' quando possivel, para preservar historico
  - Cria checkpoint git antes de comecar
  - Se algo der errado, use: git reset --hard HEAD
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTE = False

# ─────────────────────────────────────────────────────────────
# Mapa de-para
# ─────────────────────────────────────────────────────────────

PASTAS = [
    ".github",
    ".github/instructions",
    ".github/prompts",
    ".github/agents",
    ".github/roadmap",
    "docs",
    "journal",
]

# Arquivos do Lote 1 que voce baixou -> destino final
LOTE_1 = {
    "ROADMAP_DEFINITIVO.md": "ROADMAP_DEFINITIVO.md",
    "PLANO_REESTRUTURACAO_DOCS.md": "PLANO_REESTRUTURACAO_DOCS.md",
    "AGENTS.md": "AGENTS.md",
    "copilot-instructions.md": ".github/copilot-instructions.md",
}

# Mapeamento de estrutura antiga -> .github/instructions
CAMADAS = {
    "00-mestre.md": "journal/00-mestre-original.md",  # preservado, ja virou copilot-instructions
    "01-camada-0-fundacao-seguranca.md": ".github/instructions/camada-0.instructions.md",
    "02-camada-1-experiencia-dev.md": ".github/instructions/camada-1.instructions.md",
    "03-camada-2-testes.md": ".github/instructions/camada-2.instructions.md",
    "04-camada-3-criacao-com-fosso.md": ".github/instructions/camada-3.instructions.md",
    "05-camada-4-extensoes-processo.md": ".github/instructions/camada-4.instructions.md",
    "06-camada-5-gameplay.md": ".github/instructions/camada-5.instructions.md",
    "07-camada-6-profundidade-engine.md": ".github/instructions/camada-6.instructions.md",
    "08-camada-7-polimento.md": ".github/instructions/camada-7.instructions.md",
    "09-glossario-referencias.md": ".github/instructions/glossario.instructions.md",
}

# Workflows antigos: preservados: serao substituidos pelo Lote 2
WORKFLOWS = {
    "act.md": "journal/act-original.md",
    "plan.md": "journal/plan-original.md",
}

# Raiz -> .github/instructions
PARA_INSTRUCTIONS = {
    "LEARNINGS.md": ".github/instructions/aprendizados.instructions.md",
}

# Raiz -> docs
PARA_DOCS = {
    "ARQUITETURA_MCP.md": "docs/arquitetura.md",
}

# Raiz -> journal (diarios pessoais e docs que mentem numeros)
PARA_JOURNAL = [
    "NEXT_SESSION.md",
    "SESSION_SUMMARY_2026-07-17.md",
    "AUDITORIA-PENDENCIAS-RESPOSTAS.md",
    "pendencias.md",
    "CONTEXTO_PROJETO_MCP_GODOT.md",
    "CATALOGO_COMPLETO_MCP_GODOT.md",
    "INVENTARIO_OPS_ROLLUPS.md",
    "MCP_ESTADO_ATUAL.md",
    "GUIA_CONEXAO.md",
    "GUIA_INSTALACAO.md",
    "FEATURES.md",
    "AUDIT_PROTOCOL.md",
]

APAGAR = []

GITIGNORE_LINHAS = [
    "",
    "# Diario de trabalho pessoal - nao vai para o repositorio publico",
    "journal/",
    "",
]

FRONTMATTER = "---\napplyTo: '**'\n---\n\n"

# ─────────────────────────────────────────────────────────────
# Utilitarios
# ─────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────
# DOCUMENTOS EMBUTIDOS (escritos automaticamente pelo script)
# ────────────────────────────────────────────────────────────

DOCUMENTOS: dict[str, str] = {}

DOCUMENTOS['ROADMAP_DEFINITIVO.md'] = r"""DOC0
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
| Cliente de IA | Copilot no VS Code | Sampling do MCP foi descontinuado na spec 2026-07-28; construir cliente proprio = reconstruir a IA agentica |
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
zero referência a IA agentica, LICENSE existe, números dos documentos batem com o código.

| # | Fatia | Marcação | Pendências que fecha |
|---|---|---|---|
| 0.A | Corrigir bug do Passo 8 (ramo SÊNIOR sem encadeamento) | AUTO | P1 |
| 0.B | Auditar fechamento da Fatia 0.9 (3 provas faltantes) | SÊNIOR | P2 |
| 0.C | Decidir 0.7b (lean vs full) e registrar | SÊNIOR | P3 |
| 0.D | Migração de estrutura + expurgo de IA agentica | AUTO | P29 parcial, L26 |
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

DOC0"""[len('DOC0'):-len('DOC0')]

DOCUMENTOS['PLANO_REESTRUTURACAO_DOCS.md'] = r"""DOC1
# PLANO DE REESTRUTURAÇÃO DOCUMENTAL

> **Público:** IA agêntica.
> **Validade:** temporário. Apague este arquivo quando a Fatia 1.G estiver concluída.
> **Local correto:** raiz do repositório.

---

## 1. O PROBLEMA (leia antes de mover qualquer coisa)

Os 17 documentos atuais (5.563 linhas) foram escritos como diário de bordo pessoal.
Eles servem a públicos diferentes no mesmo arquivo, e por isso se contradizem.

Divergências reais já confirmadas por leitura do código:

| Documento | Diz que tem | Código real (auditoria 2026-07-23) |
|---|---|---|
| README (antes) | 193 tools, v3.4.0 | 236 tools visíveis, 272 brutas |
| MCP_ESTADO_ATUAL (antes) | 191 tools, v3.3.0 | 236 tools visíveis |
| NEXT_SESSION (antes) | 212 tools | 236 tools visíveis |
| CONTEXTO_PROJETO (antes) | 248 / 201 | 236 tools visíveis |

**A causa não é desleixo: é número escrito à mão.** A correção estrutural é gerar
todo número a partir do código. Depois desta reestruturação, número escrito à mão
em documento é violação de regra.

---

## 2. PRINCÍPIO: 1 DOCUMENTO = 1 PÚBLICO

Todo documento declara o público na primeira linha. Se serve a dois, parte em dois.

| Público | Precisa de | Onde vive |
|---|---|---|
| Usuário final | O que faço e como faço | `README.md` + `docs/manual/` (gerado) |
| IA agêntica | Regras, fatias, como implementar | `.github/` |
| Contribuidor | Como funciona por dentro | `docs/arquitetura.md` |
| Você (humano) | Onde parei, o que aprendi | `journal/` (fora do git) |

Segunda divisão: **escrito à mão** vs **gerado por código**.
Gerado: catálogo de tools, estado atual, inventário de rollups, manual, changelog.

---

## 3. MAPA DE-PARA (a tabela que a IA executa)

### 3.1 Vira instrução da IA

| De | Para | Ação |
|---|---|---|
| `.clinerules/00-mestre.md` | `.github/copilot-instructions.md` | Já entregue pronto. Preservar o conteúdo original em `journal/` |
| `.clinerules/01-camada-0-*.md` | `.github/instructions/camada-0.instructions.md` | Mover + frontmatter `applyTo` |
| `.clinerules/02` a `08` | `.github/instructions/camada-1..7.instructions.md` | Mover + frontmatter |
| `.clinerules/09-glossario-referencias.md` | `.github/instructions/glossario.instructions.md` | Mover |
| `.clinerules/workflows/act.md` | `.github/prompts/act.prompt.md` | Substituído pelo arquivo do Lote 2 |
| `.clinerules/workflows/plan.md` | `.github/prompts/plan.prompt.md` | Substituído pelo arquivo do Lote 2 |
| `LEARNINGS.md` | `.github/instructions/aprendizados.instructions.md` | Mover. **Documento mais valioso para a IA** — não editar conteúdo |
| `AUDIT_PROTOCOL.md` | fundir em `copilot-instructions.md` | Verificar se algo não coberto; se sim, anexar |

**Frontmatter obrigatório** em cada `.instructions.md`:

```markdown
---
applyTo: '**'
---
```

Use glob mais específico quando a camada só valer para certos arquivos
(exemplo: camada do dock → `applyTo: 'addons/**'`).

### 3.2 Vira documentação pública

| De | Para | Ação |
|---|---|---|
| `ARQUITETURA_MCP.md` | `docs/arquitetura.md` | Mover. Reescrita é fatia separada |
| `GUIA_CONEXAO.md` | `journal/` | Aposentar quando o instalador (1.A) existir |
| `GUIA_INSTALACAO.md` | `journal/` | Idem. Substituto: `docs/instalacao.md` de 20 linhas |
| `FEATURES.md` | `journal/` | Absorvido pelo manual gerado (1.H) |
| `README.md` | `README.md` | Reescrita total é fatia separada (1.N) |

### 3.3 Passa a ser gerado

| Arquivo | Fonte de geração |
|---|---|
| `CATALOGO_COMPLETO_MCP_GODOT.md` | `_tool_defs()` |
| `INVENTARIO_OPS_ROLLUPS.md` | rollups + `_meta_tool.py` |
| `MCP_ESTADO_ATUAL.md` | código + `.roadmap_progress.json` |
| `CHANGELOG.md` | commits |
| `docs/manual/` | `behavior.json` + blueprints + prompts + fases |

Enquanto o gerador não existir (Fatia 0.F), **mova os quatro primeiros para `journal/`**
para não continuarem mentindo.

### 3.4 Sai do repositório público

Mover para `journal/` (que entra no `.gitignore`):
`NEXT_SESSION.md` · `SESSION_SUMMARY_*.md` · `AUDITORIA-PENDENCIAS-RESPOSTAS.md` ·
`pendencias.md` · `CONTEXTO_PROJETO_MCP_GODOT.md`

Motivo: são logs de trabalho pessoais, contêm caminhos do seu disco e rotina,
e confundem quem chega no repositório.

### 3.5 Morre

`RELOGIO_CLINE_COMPORTAMENTO.md` — apagar (ja removido).
Além disso: **toda referência a IA agentica** nas camadas 01–08 deve ser trocada por
"IA agêntica (Copilot)". Buscar por: `Cline`, `.clinerules`, `cline_mcp_settings`.

### 3.6 Nasce

| Arquivo | Fatia | Observação |
|---|---|---|
| `LICENSE` | 0.E | MIT. Bloqueia AssetLib e Sponsors enquanto não existir |
| `CONTRIBUTING.md` | 0.E | Como contribuir, padrão de commit, como rodar testes |
| `CODE_OF_CONDUCT.md` | 0.E | Contributor Covenant padrão |
| `SECURITY.md` | 0.E | Como reportar vulnerabilidade |
| `AGENTS.md` | 0.D | Já entregue pronto |
| `llms.txt` | 1.N | Fatos estruturados para agentes de IA |
| `docs/manual/` | 1.H | Gerado |
| `docs/tutorial/` | 1.I | Escrito à mão, testado com pessoas |

---

## 4. ESTRUTURA FINAL

```
raiz/
  README.md              ← vitrine (usuário)
  LICENSE
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  SECURITY.md
  AGENTS.md              ← convivência das IAs
  ROADMAP_DEFINITIVO.md
  llms.txt
  server.py, tools/, addons/, ...

  .github/
    copilot-instructions.md
    instructions/        ← camadas + aprendizados + fontes + glossário
    prompts/             ← /plan /act /handoff /manual
    agents/              ← implementador, revisor
    roadmap/             ← fichas das ondas

  docs/
    instalacao.md
    arquitetura.md
    manual/              ← GERADO
    tutorial/            ← escrito à mão

  journal/               ← NO GITIGNORE, só seu
```

Raiz sai de 17 arquivos confusos para 8 arquivos com propósito claro.

---

## 5. AS 5 FATIAS DE EXECUÇÃO

Não faça tudo de uma vez. Cinco fatias, nesta ordem:

**R1 — Criar estrutura e mover sem editar** `[AUTO]`
Criar pastas, `git mv` de tudo conforme a seção 3, criar `journal/` e adicionar ao
`.gitignore`. **Zero edição de conteúdo.** Prova: `git status` mostrando apenas
renomeações, e `ls` da nova estrutura.

**R2 — Frontmatter e expurgo de IA agentica** `[AUTO]`
Adicionar `applyTo` em cada `.instructions.md`. Substituir toda menção a IA agentica.
Prova: `grep -ri "cline" .` retornando zero (fora de `journal/`).

**R3 — Arquivos que nascem** `[AUTO]`
LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY. Prova: arquivos existem e
`release_checklist` do próprio MCP reconhece o LICENSE.

**R4 — `docs_sync`** `[AUTO]`
Script que extrai números reais do código e injeta nos documentos gerados.
Prova: rodar o script e mostrar que as 4 contagens divergentes viraram uma só,
igual ao número real de `Tool()` em `server.py`.

**R5 — Reescrita do README e da arquitetura** `[SÊNIOR]`
Só depois que o instalador (1.A) existir, senão o README documenta algo que
não existe mais. Prova: revisão humana.

---

## 6. ARMADILHAS (a IA erra aqui)

1. **"Melhorar" o texto ao mover.** Proibido. Mover é `git mv` e nada mais.
   Regras que custaram meses de aprendizado somem quando a IA "resume".
2. **Apagar em vez de arquivar.** Nada é apagado, exceto `RELOGIO_CLINE_*` (ja removido).
   Tudo o mais vai para `journal/`.
3. **Esquecer o `.gitignore`.** Se `journal/` for commitado, o expurgo não serviu de nada.
4. **`git mv` vs mover no explorador.** Use `git mv` — preserva histórico.
5. **Instruções em subpasta não funcionam.** O VS Code só lê
   `.github/copilot-instructions.md` do workspace aberto. Se você abrir uma subpasta
   como workspace, as regras somem. Por isso os dois agentes usam `git worktree`
   (pastas completas), nunca subpastas.

DOC1"""[len('DOC1'):-len('DOC1')]

DOCUMENTOS['AGENTS.md'] = r"""DOC2
# AGENTS.md — Como as IAs trabalham neste repositório

> **Público:** IA agêntica (GitHub Copilot no VS Code).
> **O VS Code lê este arquivo automaticamente.** Ele vale para todo agente,
> em qualquer pasta de trabalho deste repositório.
> **Local correto:** raiz do repositório.

---

## 1. DESCUBRA QUEM VOCÊ É — FAÇA ISTO PRIMEIRO

Antes de qualquer coisa, rode:

```bash
git branch --show-current
```

| Branch | Você é | Território |
|---|---|---|
| `main` | **Agente 1 — Núcleo** | `server.py`, `tools/`, `.github/`, `docs/`, raiz |
| `agente2/*` | **Agente 2 — Conteúdo** | `behaviors/`, `blueprints/`, `seeds/`, `addons/`, `tests/` |

Se a branch não bater com nenhum padrão: **pare e pergunte ao humano.**

Se você é o único agente rodando (modo solo), você é o **Agente 1** e tem
todos os territórios. O fluxo é idêntico — nada muda.

---

## 2. TERRITÓRIOS (a regra que evita colisão)

A divisão é **por arquivo, não por assunto**. Isso importa: dois agentes podem
trabalhar no mesmo assunto desde que não toquem no mesmo arquivo.

### Agente 1 — Núcleo
```
server.py
tools/**
resources/**
auditar.py, install.py, launch.py
.github/**
docs/**
README.md, ROADMAP_DEFINITIVO.md, AGENTS.md, LICENSE
.roadmap_progress.json          ← EXCLUSIVO. Agente 2 nunca escreve aqui
```

### Agente 2 — Conteúdo
```
behaviors/**
blueprints/**
seeds/**
addons/**
tests/**
templates/**
.roadmap_progress_a2.json       ← o Agente 2 escreve aqui
```

### Terra de ninguém (exige combinação explícita)
`requirements.txt`, `pyproject.toml`, `.gitignore`, `CHANGELOG.md`

Quem precisar mexer nestes: **avise no pacote de escalação antes**, não depois.

---

## 3. AS 6 REGRAS DE CONVIVÊNCIA

**1. Nunca edite fora do seu território.**
Se a fatia exige tocar arquivo do outro, ela não é sua. Escale.

**2. Cheque conflito ANTES de terminar, não depois.**
```bash
git merge-tree $(git merge-base main HEAD) main HEAD
```
Saída vazia = sem conflito. Saída com marcadores = **pare e escale**.
Isolamento de pasta não elimina conflito, ele adia o conflito para o merge.
Você pode criar conflito com o outro agente sem perceber.

**3. Só o Agente 1 escreve em `.roadmap_progress.json`.**
O Agente 2 escreve em `.roadmap_progress_a2.json`. O Agente 1 consolida os dois
quando faz merge. Arquivo de estado é a causa número um de colisão.

**4. Nunca commite sozinha.** Proponha o commit ao humano com a mensagem sugerida
e espere aprovação. Vale para os dois agentes, sempre.

**5. Merge um de cada vez.** Nunca dois merges em paralelo.
Ordem: Agente 2 → `main`, resolver conflito, testar, só então o próximo.

**6. Passe o bastão por escrito.** Ao terminar uma fatia, rode `/handoff`.
O outro agente não tem o seu histórico de conversa — só o que estiver em arquivo.

---

## 4. COMO CRIAR O SEGUNDO AGENTE (humano faz isto uma vez)

Na pasta principal do repositório:

```bash
git worktree add ../mcp-agente2 -b agente2/trabalho
```

Isso cria uma pasta irmã completa, com o mesmo `.git` e todo o `.github/` junto —
por isso o Agente 2 herda estas regras automaticamente.

Abra uma segunda janela do VS Code em `../mcp-agente2`.

**Não use subpasta com um documento apontando para o MCP.** O VS Code só aplica
`.github/copilot-instructions.md` do workspace aberto; uma subpasta perderia todas
as regras. Worktree é pasta completa, por isso funciona.

Para desligar o segundo agente:
```bash
git worktree remove ../mcp-agente2
```

Quando existir apenas um agente, ele é o Agente 1 e nada mais muda.

---

## 5. FLUXO DE TRABALHO (idêntico para os dois)

```
/plan   → leio o roadmap, escolho a próxima fatia do MEU território,
          checo conflito com o outro agente, apresento o plano e PARO
  ↓
humano aprova
  ↓
/act    → implemento UMA fatia, rodo auditar.py, colo as provas,
          proponho o commit e PARO
  ↓
humano aprova
  ↓
/handoff → escrevo o resumo para o outro agente (ou para a próxima sessão)
```

Nunca pule `/plan`. Nunca faça duas fatias no mesmo `/act`.

---

## 6. MODO REVISOR ADVERSARIAL (opcional, para fatias críticas)

Em fatias marcadas `[SÊNIOR]` de alto risco, o humano pode pedir que o Agente 2
**audite** o trabalho do Agente 1 em vez de implementar a sua própria fatia.

Nesse modo o Agente 2 usa o agente customizado `revisor` e:
- não escreve código;
- roda `auditar.py` de forma independente;
- tenta **quebrar** a implementação, não confirmá-la;
- verifica se as provas coladas correspondem ao que o código realmente faz.

Custa metade da velocidade e ataca o problema número um do projeto:
evidência fabricada com confiança.

---

## 7. O QUE NUNCA FAZER

- Commitar sem aprovação humana.
- Editar arquivo fora do seu território.
- Fechar fatia `[SÊNIOR]` sozinha.
- Dizer "passou" sem colar o output real.
- Dizer "é bug pré-existente" sem `git blame` ou `git log -p` colado.
- Fazer duas fatias na mesma execução.
- "Melhorar" texto durante uma fatia de migração de documento.
- Redefinir os critérios de aceite no meio para caber no que você fez.

**Parar e escalar é sucesso. Insistir num loop é fracasso.**

DOC2"""[len('DOC2'):-len('DOC2')]

DOCUMENTOS['copilot-instructions.md'] = r"""DOC3
# Instruções do projeto — MCP Godot Agent

> **Local correto:** `.github/copilot-instructions.md`
> O VS Code aplica este arquivo automaticamente a todas as requisições de chat
> deste workspace. Mantenha-o curto: regra que não cabe aqui vai para
> `.github/instructions/`.

---

## 1. O QUE É ESTE PROJETO

Um servidor MCP em Python que é o **dono do processo** de desenvolvimento de um jogo
Godot inteiro — da ideia ao lançamento. Não é só uma ponte entre IA e engine: tem
travas reais (fase, verificação, export, sessão) que impedem pular etapa.

O projeto que você edita é o **próprio MCP**, não um jogo.

Estado: Godot 4.7, 236 ferramentas visíveis (272 definições brutas em
`core/tool_definitions.py`, 189 depreciadas, 80 aliases), 249 behaviors,
38 domínios, máquina de estados de 6 fases
(IDEIA → DESIGN → PROTOTIPO → CONTEUDO → POLIMENTO → PRONTO_PARA_LANCAR),
Saga Engine, proof ledger, `auditar.py` como portão fail-closed.

Objetivo final: um não-programador, usando linguagem natural, começa, desenvolve
e **termina** um jogo indie.

---

## 2. LEIA NESTA ORDEM, SEMPRE

1. `AGENTS.md` — descubra qual agente você é e qual é o seu território
2. `ROADMAP_DEFINITIVO.md` — a ordem das ondas e fatias
3. `.github/roadmap/ONDA_*.md` — a ficha da fatia atual
4. `.github/instructions/aprendizados.instructions.md` — o que já quebrou antes
5. `.github/instructions/fontes.instructions.md` — onde pesquisar antes de escrever

---

## 3. AS 5 REGRAS ABSOLUTAS

**1. Uma fatia por vez.** Nunca comece N+1 antes de N estar 100% fechada e aprovada
pelo humano.

**2. Você não decide que está bom.** "Bom" é teste que passa ou falha, nunca a sua
opinião. Se um critério não vira teste de passa/falha, ele não é auto-avaliável —
escale para o humano.

**3. Prova sempre, nunca alegação.**
- `git diff --no-color` literal, com marcadores `@@` — nunca resumo ou tabela
- Código real colado em bloco — nunca "Read lines X to Y" (isso é log de ferramenta)
- Output de teste completo — nunca "passou!" sozinho
- "É bug pré-existente" / "sem relação com a fatia" exige `git blame` ou `git log -p`
  com output colado

**4. Nunca commite sozinha.** Proponha o commit com a mensagem sugerida e pare.

**5. Checkpoint antes de qualquer operação destrutiva.** Git é a rede de segurança real.

Se não tiver certeza se pode prosseguir: **pare e escale.** O custo de parar é baixo.
O custo de prosseguir errado com confiança é alto.

---

## 4. CONSULTE A FONTE ANTES DE IMPLEMENTAR

Antes de escrever código de uma feature, leia a fonte correspondente em
`.github/instructions/fontes.instructions.md` e **cite qual usou** no relatório.
Sem fonte citada, a fatia não fecha.

Motivo: a causa raiz da maioria dos erros neste projeto é a IA inventar API do Godot
que não existe (regra R9 dos aprendizados).

---

## 5. TETO DE FERRAMENTAS (nunca violar)

A precisão de escolha de tool despenca acima de 30–50 tools visíveis.

- **Rollup-first é lei.** Feature nova entra como `op` dentro de um rollup
  (`nome_manage` com parâmetro `op`), nunca como tool de topo. Exceção só com
  justificativa registrada e aprovada.
- Rollup se cria com a factory `create_manage_tool()` de `_meta_tool.py`.
  Não invente outro padrão.
- Registro: `Tool(name=..., description=..., inputSchema=...)` em `_tool_defs()`
  **e** handler correspondente em `_build_handlers()`.
- Teto: ~40 tools visíveis por fase, ~70 tools de topo no total.
- **Distinguibilidade:** nome ou descrição que se confunda com tool existente
  é falha automática. Tool ambígua degrada a escolha mais que tool a mais.
- Descrição e schema enxutos. Descrição inchada custa token em toda requisição
  e piora a escolha.

---

## 6. PADRÕES TÉCNICOS DO REPOSITÓRIO (fatos, não sugestões)

- Estado por projeto vive em `<project_root>/.mcp_<nome>_state.json`,
  **nunca** em config global do MCP.
- Escrita concorrente em arquivo compartilhado exige lock via `tools/config_lock.py`.
- Subprocess sempre por `tools/subprocess_utils.py::run_subprocess_safe()`,
  com `stdin=DEVNULL` (evita deadlock no Windows).
- Rede sempre em `127.0.0.1`. Bind em `0.0.0.0` é falha automática.
- **Visibilidade de tool ≠ bloqueio de execução.** `_tool_defs()` é filtrado por fase;
  `_build_handlers()` não é. Tool escondida ainda pode ser chamada. Não confunda
  curadoria com trava real ao avaliar se um gate é de verdade.
- Provas por `capture_proof` / `verify_proof`, rodadas **antes** do commit
  (`git_diff` fica vazio depois do commit).

---

## 7. AMBIENTE (Windows)

- PowerShell antigo não aceita `&&`. Use `;` ou `cmd /c "a && b"`.
- `git commit` / `git log` com saída grande sem feedback trava a sessão.
  Use `--oneline`, `-n`, ou redirecione.
- Falhas de rede devem ser simuladas por mock, nunca esperando timeout real.
- `godot --headless --script` e `--check-only` não funcionam no Windows com 4.7
  (regra R12). Use os workarounds documentados nos aprendizados.
- Nomes de arquivo e projeto: sem acento e sem espaço nos caminhos.

---

## 8. FLUXO

`/plan` → planejo e paro · humano aprova · `/act` → implemento uma fatia, provo,
proponho commit e paro · humano aprova · `/handoff` → escrevo o resumo.

Nunca pule `/plan`. Nunca faça duas fatias no mesmo `/act`.

---

## 9. LINGUAGEM

Responda ao humano em **português, linguagem simples e direta**. Sem jargão
desnecessário, sem preâmbulo, sem elogio, sem resumo redundante. Comando pedido
é comando entregue — sem explicação em volta.

DOC3"""[len('DOC3'):-len('DOC3')]


feitos: list[str] = []
avisos: list[str] = []


def log(msg: str) -> None:
    print(msg)


def ok(msg: str) -> None:
    feitos.append(msg)
    print(f"  [OK] {msg}")


def aviso(msg: str) -> None:
    avisos.append(msg)
    print(f"  [!!] {msg}")


def rodar(cmd: list[str]) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            cmd, cwd=ROOT, capture_output=True, text=True,
            stdin=subprocess.DEVNULL, timeout=60,
        )
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def eh_repo_git() -> bool:
    sucesso, _ = rodar(["git", "rev-parse", "--git-dir"])
    return sucesso


def mover(origem: Path, destino: Path) -> None:
    """Move preservando historico do git quando possivel."""
    if not origem.exists():
        return
    if destino.exists():
        aviso(f"{destino.relative_to(ROOT)} ja existe - pulado")
        return
    if TESTE:
        ok(f"[teste] moveria {origem.relative_to(ROOT)} -> {destino.relative_to(ROOT)}")
        return

    destino.parent.mkdir(parents=True, exist_ok=True)
    sucesso, saida = rodar(["git", "mv", str(origem.relative_to(ROOT)),
                            str(destino.relative_to(ROOT))])
    if sucesso:
        ok(f"{origem.name} -> {destino.relative_to(ROOT)}")
    else:
        shutil.move(str(origem), str(destino))
        ok(f"{origem.name} -> {destino.relative_to(ROOT)} (sem git)")


def add_frontmatter(caminho: Path) -> None:
    if not caminho.exists() or TESTE:
        return
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    if texto.lstrip().startswith("---"):
        return
    caminho.write_text(FRONTMATTER + texto, encoding="utf-8")


# ─────────────────────────────────────────────────────────────
# Passos
# ─────────────────────────────────────────────────────────────

def passo_0_checkpoint() -> None:
    log("\n[0/8] Checkpoint de seguranca")
    if not eh_repo_git():
        aviso("Nao e um repositorio git - seguindo sem checkpoint")
        return
    sucesso, saida = rodar(["git", "status", "--porcelain"])
    if sucesso and saida.strip():
        aviso("Existem mudancas nao commitadas. Recomendado commitar antes.")
        if not TESTE and sys.stdin.isatty():
            resposta = input("  Continuar mesmo assim? (s/N): ").strip().lower()
            if resposta != "s":
                log("\nAbortado pelo usuario. Nada foi alterado.")
                sys.exit(0)
        elif not TESTE:
            aviso("Sem terminal interativo - seguindo automaticamente")
    else:
        ok("Arvore de trabalho limpa")


def passo_1_pastas() -> None:
    log("\n[1/8] Criando pastas")
    for p in PASTAS:
        caminho = ROOT / p
        if caminho.exists():
            continue
        if TESTE:
            ok(f"[teste] criaria {p}/")
        else:
            caminho.mkdir(parents=True, exist_ok=True)
            ok(f"{p}/")


def passo_2_lote1() -> None:
    log("\n[2/8] Escrevendo os documentos do Lote 1")
    for nome, destino_rel in LOTE_1.items():
        destino = ROOT / destino_rel
        conteudo = DOCUMENTOS.get(nome)
        if conteudo is None:
            aviso(f"documento {nome} nao esta embutido")
            continue
        if destino.exists():
            atual = destino.read_text(encoding="utf-8", errors="replace")
            if atual.strip() == conteudo.strip():
                ok(f"{destino_rel} ja esta atualizado")
                continue
            backup = ROOT / "journal" / (destino.name + ".anterior")
            if not TESTE:
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destino, backup)
            aviso(f"{destino_rel} existia - copia salva em journal/{backup.name}")
        if TESTE:
            ok(f"[teste] escreveria {destino_rel} ({len(conteudo)} chars)")
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(conteudo, encoding="utf-8")
        ok(f"{destino_rel} escrito ({len(conteudo)} chars)")


def passo_3_camadas() -> None:
    log("\n[3/8] Migrando .clinerules -> .github")
    base = ROOT / ".clinerules"
    if not base.exists():
        aviso(".clinerules/ nao encontrado - talvez ja migrado")
        return

    for nome, destino_rel in CAMADAS.items():
        mover(base / nome, ROOT / destino_rel)

    wf = base / "workflows"
    if wf.exists():
        for nome, destino_rel in WORKFLOWS.items():
            mover(wf / nome, ROOT / destino_rel)

    # sobras
    restantes = [p for p in base.rglob("*") if p.is_file()]
    for p in restantes:
        mover(p, ROOT / "journal" / p.name)

    if not TESTE:
        try:
            for d in sorted(base.rglob("*"), reverse=True):
                if d.is_dir():
                    d.rmdir()
            base.rmdir()
            ok(".clinerules/ removida (vazia)")
        except OSError:
            aviso(".clinerules/ nao ficou vazia - verifique manualmente")


def passo_4_outros_moves() -> None:
    log("\n[4/8] Movendo os demais documentos")
    for nome, destino_rel in PARA_INSTRUCTIONS.items():
        mover(ROOT / nome, ROOT / destino_rel)
    for nome, destino_rel in PARA_DOCS.items():
        mover(ROOT / nome, ROOT / destino_rel)
    for nome in PARA_JOURNAL:
        mover(ROOT / nome, ROOT / "journal" / nome)


def passo_5_frontmatter() -> None:
    log("\n[5/8] Adicionando frontmatter applyTo")
    pasta = ROOT / ".github" / "instructions"
    if not pasta.exists():
        return
    n = 0
    for arq in sorted(pasta.glob("*.instructions.md")):
        add_frontmatter(arq)
        n += 1
    ok(f"{n} arquivo(s) de instrucoes processado(s)")


def passo_6_apagar() -> None:
    log("\n[6/8] Removendo arquivos obsoletos")
    for nome in APAGAR:
        caminho = ROOT / nome
        if not caminho.exists():
            continue
        if TESTE:
            ok(f"[teste] apagaria {nome}")
            continue
        sucesso, _ = rodar(["git", "rm", "-f", nome])
        if not sucesso:
            caminho.unlink()
        ok(f"{nome} removido")


def passo_7_gitignore() -> None:
    log("\n[7/8] Atualizando .gitignore")
    gi = ROOT / ".gitignore"
    atual = gi.read_text(encoding="utf-8", errors="replace") if gi.exists() else ""
    if "journal/" in atual:
        ok("journal/ ja estava no .gitignore")
        return
    if TESTE:
        ok("[teste] adicionaria journal/ ao .gitignore")
        return
    gi.write_text(atual.rstrip() + "\n" + "\n".join(GITIGNORE_LINHAS), encoding="utf-8")
    ok("journal/ adicionado ao .gitignore")


def passo_8_verificar_cline() -> None:
    log("\n[8/8] Procurando referencias a Cline")
    sucesso, saida = rodar(["git", "grep", "-ril", "cline", "--",
                            ".github", "docs", "*.md"])
    if saida.strip():
        arquivos = [l for l in saida.splitlines() if "journal/" not in l]
        if arquivos:
            aviso(f"Ainda ha mencoes a Cline em {len(arquivos)} arquivo(s):")
            for a in arquivos[:10]:
                print(f"       - {a}")
            aviso("Isto e a Fatia R2 - a IA deve corrigir com /act")
        else:
            ok("Nenhuma mencao a Cline fora de journal/")
    else:
        ok("Nenhuma mencao a Cline encontrada")


def relatorio() -> None:
    log("\n" + "=" * 62)
    log(f"  CONCLUIDO - {len(feitos)} acao(oes), {len(avisos)} aviso(s)")
    log("=" * 62)
    if avisos:
        log("\nAVISOS:")
        for a in avisos:
            log(f"  - {a}")
    log("""
PROXIMOS PASSOS:

  1. Confira a estrutura:      git status
  2. Se estiver bom, commite:  git add -A
                               git commit -m "docs: nova estrutura .github"
  3. Se algo deu errado:       git reset --hard HEAD

  4. Reinicie o VS Code para o Copilot carregar as novas instrucoes.
  5. Peca o Lote 2 (comandos /plan e /act) ao Claude.

  Enquanto o Lote 2 nao chegar, /plan e /act ainda NAO funcionam.
""")


def main() -> int:
    global TESTE
    ap = argparse.ArgumentParser(description="Instalador da nova estrutura de documentos")
    ap.add_argument("--teste", action="store_true",
                    help="mostra o que faria, sem alterar nada")
    args = ap.parse_args()
    TESTE = args.teste

    log("=" * 62)
    log("  INSTALADOR DE ESTRUTURA - MCP Godot Agent")
    log(f"  Pasta: {ROOT}")
    if TESTE:
        log("  MODO TESTE - nada sera alterado")
    log("=" * 62)

    passo_0_checkpoint()
    passo_1_pastas()
    passo_2_lote1()
    passo_3_camadas()
    passo_4_outros_moves()
    passo_5_frontmatter()
    passo_6_apagar()
    passo_7_gitignore()
    passo_8_verificar_cline()
    relatorio()
    return 0


if __name__ == "__main__":
    sys.exit(main())
