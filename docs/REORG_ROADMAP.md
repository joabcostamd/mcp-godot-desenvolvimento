# REORG_ROADMAP.md — Reorganização das Tools do MCP Godot

**Versão:** 1.0 · **Data:** 2026-07-23
**Substitui:** `MASTER_IMPLEMENTATION_ROADMAP.md` (v1.0, 2026-07-21) como plano de execução.
O MASTER continua valendo como **referência de arquitetura** (seções 1–16). O que muda é a
**ordem**: ele assumia começar do zero na F0; o reconhecimento de 2026-07-23 provou que
F5 já rodou 13 vezes sem F1–F4 terem fechado.

---

## O QUE ESTE DOCUMENTO **NÃO** MUDA

Registrado no topo de propósito. Nada aqui altera o seu fluxo de trabalho:

- Os 6 comandos globais (`/plan`, `/act`, `/audit`, `/handoff`, `/encerrar`, `/seguir-roadmap`)
  continuam vivendo em `%APPDATA%\Code\User\prompts\`. **Nenhum é reescrito por este plano.**
- A ficha de 10 campos continua sendo o formato único de fatia.
- `.roadmap_progress.json` continua sendo a fonte única de status.
- Os 3 status continuam sendo `concluida` / `escalada` / `nao verificado`.
- O ciclo continua `/plan` → aprovação → `/act` → aprovação.
- `AGENTS.md`, `auditar.py` e `.github/instructions/` continuam existindo e sendo lidos.

O que este plano faz é **plugar dentro** desse fluxo, não substituí-lo.

---

## 1. POR QUE ESTE DOCUMENTO EXISTE (fatos medidos, 2026-07-23)

Reconhecimento executado (`RECON_MCP.md`, 508 KB, 46 blocos). Achados que invalidam a
premissa do MASTER:

| # | Fato | Prova (bloco do recon) |
|---|---|---|
| 1 | `server.py` ainda tem `TOOLSETS` (l.60), `TOOL_PROFILES` (l.295), `PHASE_TOOLSETS` (l.353), `PHASE_TOOLS_CORE` (l.530) | B29 |
| 2 | `_apply_hints` (l.1363), `_HINT_RULES` (l.1323), `_READONLY` (l.1491), `_TITLES` (l.1566), `_TAGS` (l.1607) vivos e em uso nas l.1700–1715 | B30 |
| 3 | `.roadmap_progress.json` marca F5.1–F5.13 `concluida` — mas o critério de aceite da F1 exige que (1) não exista | B20 |
| 4 | `server.py:1715` faz `t.annotations = {"tags": ...}` — substitui o dict inteiro e apaga os 4 hints MCP | B30 |
| 5 | `ToolAnnotations.model_config` = `{'extra': 'allow'}` — o SDK não rejeita campo fora da spec | B37 |
| 6 | `auditar.py` C1 tolera 5 tools novas por fatia sem alarme | arquivo `auditar.py` |
| 7 | `auditar.py --skip-c5` desliga o teto com desculpa fixa; usado dezenas de vezes | `auditar.py` + B20 |
| 8 | 3 arquivos de estado coexistem: `.roadmap_progress.json` (77 KB), `.reorg_progress.json`, `.roadmap_progress_a2.json` | B23, B43 |
| 9 | `.github/prompts/{act,audit,handoff,plan}.prompt.md` voltaram como **untracked** após o commit `3c28cfb` que os removeu | B17 |
| 10 | Hooks `PreToolUse` não disparam com a extensão DeepSeek v0.6.2 (regra R20) | HANDOFF.md |
| 11 | `git diff --stat main..agente2/behaviors-onda2` = 7.386 inserções / **31.705 remoções** — a branch remove `registry/`, `domains/`, `adapters/`, `experimental/`, `scripts/audit_*.py` | EXTRA |
| 12 | 13 `_manage` escritos à mão em `core/tool_definitions.py` | B33 |
| 13 | `pytest --collect-only` = **362** testes; HANDOFF reporta 166 | B38 |
| 14 | `config.local.json` não existe | B43 |
| 15 | Pasta `.githooks` já existe na raiz (uso não confirmado) | B23 |
| 16 | Zero pastas `.mcp_proof`; transições de fase 80% forçadas (`force=True`) | HANDOFF.md |

**Conclusão:** o problema não é falta de plano. É que o plano rodou fora de ordem, sem trava
mecânica, com um auditor que tinha dois vazamentos. A ordem correta agora começa por
reconciliar, não por medir.

---

## 2. AS 6 DECISÕES JÁ TOMADAS

Aprovadas pelo humano em 2026-07-23. **A IA executora não reabre nenhuma sem escalar.**

| ID | Decisão | Razão |
|---|---|---|
| **DR-1** | Commit automático liberado **só depois** da Fatia R1 (gate git instalado e testado) | Autonomia sem trava foi o que produziu 143→287 tools |
| **DR-2** | Branch `agente2/behaviors-onda2`: **tag de arquivo morto, sem merge** | Os 249 behaviors já estão na main; o merge traria 31.705 remoções |
| **DR-3** | Prompts locais em `.github/prompts/` são removidos (movidos para `journal/`) | Proibição 9.3.1 da constituição; causavam `/plan` triplicado |
| **DR-4** | Em conflito, **`/act` vence** `/seguir-roadmap` | `/act` é a fonte da regra de prova; `/seguir-roadmap` diverge dela |
| **DR-5** | `--skip-c5` sai; entra **baseline travado** (métrica pode melhorar, nunca piorar) | Remover seco travaria tudo: 5 de 6 fases estão acima do teto hoje |
| **DR-6** | Tolerância do C1 cai de 5 para **0**; tool nova exige justificativa escrita | 5 por fatia × ~30 fatias = 150 tools invisíveis ao auditor |

Complemento: **um arquivo de estado só** (`.roadmap_progress.json`). Os outros dois viram
arquivo morto em `journal/estado-antigo/`, preservados, não apagados.

---

## 3. ORDEM DE EXECUÇÃO

```
ONDA R   RECONCILIAR        ← PORTÃO DURO. Nada começa antes.
   │
   ├── R1  gate git real (a única trava que dispara neste ambiente)
   ├── R2  estado único
   ├── R3  consertar auditar.py (DR-5 + DR-6)
   ├── R4  consertar caminhos e a contradição dos comandos
   ├── R5  reauditar as fatias marcadas concluida
   ├── R6  branch do Agente 2 (DR-2)
   ├── R7  medição real (o antigo F0, com os nomes de função certos)
   └── R8  gerar as fichas das ondas seguintes a partir dos números reais
   ▼
ONDA 1   REGISTRY           ← fonte única de verdade
ONDA 2   CONFORMIDADE MCP   ← inclui o bug do _TAGS (fato 4)
ONDA 3   UNIFICAR ROLLUPS   ← 13 _manage manuais + COLISAO playtest_manage
ONDA 4   DESCOBERTA         ← 4.2 a 4.5 (4.1 já está feito: B29 l.540)
ONDA 8   CURADORIA          ← 59 tools sem fase
ONDA 9   QUARENTENA         ← verticais prematuras
ONDA 10  CONGELAR           ← CI + freio de entrada + docs
ONDA P   PENDÊNCIAS         ← tudo que ficou solto (seção 5)
```

**Por que ONDA 5 (migrar domínios) sumiu:** 38 domínios já existem em `domains/`. A F5 não é
mais execução, é **verificação** — vira a Fatia R5. Se a reauditoria mostrar domínio
incompleto, ele entra como fatia da ONDA P, não como onda inteira.

**Por que a ONDA R é portão:** o MASTER já dizia que nenhuma fase começa antes de números
medidos. Só que hoje há um passo antes da medição: garantir que a medição não vai ser
falsificada. R1 e R3 existem para isso.

---

## 4. AS ONDAS

### ONDA R — RECONCILIAR
Fichas completas em `.github/roadmap/ONDA_R_reconciliacao.md`. Resumo:

| Fatia | O que é | Marcação |
|---|---|---|
| R1 | Gate git real em `.githooks/`, com teste que prova que bloqueia | `[SÊNIOR]` |
| R2 | Estado único — os outros 2 JSON viram arquivo morto | `[AUTO]` |
| R3 | `auditar.py`: C1 tolerância 0, `--skip-c5` → baseline travado | `[SÊNIOR]` |
| R4 | Caminho do roadmap + contradição `/seguir-roadmap` × `/act` | `[SÊNIOR]` |
| R5 | Reauditar F1–F5 contra o critério real de cada uma | `[SÊNIOR]` |
| R6 | Branch do Agente 2 — tag + prova de merge sem executar | `[SÊNIOR]` |
| R7 | Medição real por fase, via `_get_phase_tools()` | `[AUTO]` |
| R8 | Gerar as fichas das ondas seguintes com os números da R7 | `[AUTO]` |

### ONDA 1 — REGISTRY
Fazer `tools/list`, handlers, fases e namespaces serem **derivados** de manifesto.
`registry/` já existe (`types.py`, `discovery.py`, `invariants.py`, `legacy_adapter.py`,
`annotations.py` — B45/EXTRA confirmam). Falta: `server.py` parar de declarar.

Fatias: 1.1 confirmar o que `registry/` já faz · 1.2 `server.py` passa a chamar
`registry.build_tool_defs()` · 1.3 remover `TOOLSETS`/`PHASE_TOOLSETS`/`TOOL_PROFILES`/
`PHASE_TOOLS_CORE` de `server.py` · 1.4 `gen_catalog.py` gera o catálogo do registry.

**Prova de cada fatia:** `dump_toollist.py` antes e depois, `fc` idêntico nas 6 fases.

### ONDA 2 — CONFORMIDADE MCP
Fatias: 2.1 corrigir `server.py:1715` (o `_TAGS` que apaga os hints — tags saem das
annotations, viram campo do manifesto) · 2.2 `registry/annotations.py` valida e rejeita
campo fora da spec (o SDK não rejeita: `extra: allow`) · 2.3 congelar `_HINT_RULES` em
dados revisados (`registry/legacy_annotations.py`) · 2.4 deletar `_apply_hints`,
`_READONLY`, `_DESTRUCTIVE`, `_IDEMPOTENT`, `_TITLES`, `_TAGS` · 2.5 `rollback` preenchido
em toda op destrutiva.

### ONDA 3 — UNIFICAR ROLLUPS
Os 13 `_manage` manuais (B33, linhas exatas): `budget_manage`(30), `mcp_telemetry_manage`(61),
`playtest_manage`(2193), `fun_report_manage`(2248), `complexity_gate_manage`(2273),
`teacher_manage`(2296), `scope_manage`(2315), `reviewer_manage`(2333), `polish_manage`(2352),
`quickstart_manage`(4180), `version_history_manage`(4218), `publish_manage`(4253),
`community_manage`(4285).

Uma fatia por tool: provar uso com `findstr`, classificar em migrar / quarentena / deletar.
Mais: resolver `COLISAO_ROLLUP` do `playtest_manage` (definido em `_raw_tool_defs()` **e**
em `rollups.py` — B31 l.1165 + B33 l.2193).

### ONDA 4 — DESCOBERTA PROGRESSIVA
4.1 **já feito** — o trio está em `PHASE_TOOLS_CORE` (B29, l.540). Faltam:
4.2 fundir `tool_catalog`/`tool_groups` em `catalog_search` · 4.3 indexar **ops**, não só
tools · 4.4 `describe_tool({tool, op})` · 4.5 guia no `AGENTS.md` (não em `.clinerules` —
essa pasta não existe mais, B26).

**Regressão obrigatória:** `catalog_search("erro no script")` não pode devolver `node_manage`
(o falso positivo `"no"→"node"` já corrigido).

### ONDA 8 — CURADORIA
59 tools sem fase (acessibilidade, gameplay, telemetria, onboarding). INV-04: toda tool em
≥1 fase ou `internal=True`. Reduzir de 3 filtros (`profile`/`toolsets`/`phase`) para 2 eixos.
Documentar e testar a precedência **atual** antes de mudar.

### ONDA 9 — QUARENTENA
`experimental/` já existe (B26 = True). Mover as verticais nunca exercitadas por um jogo real.
Critério de saída escrito: um jogo real precisou da capacidade.

### ONDA 10 — CONGELAR
CI rodando as invariantes em todo push · freio de entrada (tool nova exige justificativa) ·
`ARQUITETURA_MCP.md` reescrito do registry real · zero contagem escrita à mão em `.md` ·
`LEARNINGS.md` com as causas-raiz.

### ONDA P — PENDÊNCIAS
Tudo que estava solto, para a casa ficar arrumada:

| Item | Origem |
|---|---|
| Feature 9 — trava de exportação (`build_export` ← `release_checklist`) | Fase 1 do MCP, nunca iniciada |
| Feature 10 — próximo passo obrigatório no início da sessão | Fase 1 do MCP, nunca iniciada |
| `set_node_property` grava mas `get_node_property` devolve null | backlog antigo |
| INV-03 falhando (`execute_gdscript_runtime` sem namespace) — alegado falso positivo **sem prova** | B38 / HANDOFF |
| Divergência 362 testes coletados × 166 reportados | B38 |
| `AGENTS.md` seção 2 com cerca de código quebrada (fecha sem abrir) | B22 |
| `config.local.json` ausente | B43 |
| Auditoria de consistência dos 38 domínios (nem todos têm os 6 arquivos) | HANDOFF |
| `.mcp_proof` nunca exercitado; transições 80% forçadas | HANDOFF |
| 22 menções residuais a "cline" em `instalar.py` e `instalar_roadmap.py` | B45 |
| `ruff` não instalado no venv (A02 fica em warning) | HANDOFF |

---

## 5. DOIS AGENTES OU UM SÓ

Toda ficha carrega uma segunda marcação, além de `[AUTO]`/`[SÊNIOR]`:

- **`[EIXO-CENTRAL]`** — toca `server.py`, `registry/`, `core/tool_definitions.py`,
  `_meta_tool.py`, `auditar.py` ou `tools/rollups.py`. **Só o Agente 1. Sequencial.**
- **`[PERIFERIA]`** — toca um `domains/<x>/` isolado, `tests/`, `docs/`, `behaviors/`.
  **Paralelizável.**

Com um agente só: roda tudo em sequência, a marcação não atrapalha nada.
Com dois: o Agente 2 pega só `[PERIFERIA]`, e o `coordenacao.json` que já existe no
`--git-common-dir` continua sendo o mecanismo de claim. Nenhuma mudança no protocolo atual.

**Regra dura:** a ONDA R inteira é `[EIXO-CENTRAL]`. Um agente só, do começo ao fim.
Paralelismo só a partir da ONDA 3.

---

## 6. CRITÉRIO DE PARADA

Herdado do MASTER (Apêndice C), sem mudança:

1. INV-01..15 passam; **e**
2. INV-05 (≤33 tools) e INV-06 (≤12.000 tokens) passam nas 6 fases; **e**
3. a taxa de correção manual num jogo pequeno fica **abaixo de 15–20%**.

**(3) tem precedência.** Se o Shardbreaker sair com correção abaixo de 20%, as ondas
restantes são declaradas retorno decrescente e vão para backlog — não são executadas por
completude.

---

## 7. REGRA SOBRE ESTE DOCUMENTO

Números aqui vêm do recon de 2026-07-23. A Fatia R7 vai medir de novo. **Se a medição
divergir em mais de 20%, este documento é corrigido antes de qualquer ONDA começar** —
não ignorado, não contornado. Decisão tomada durante a execução que não esteja aqui
precisa ser registrada aqui antes de prosseguir.

---

*Fim. Aplicar junto com `PROTOCOLO_AUTOGOVERNANCA.md` e `CONSTITUICAO-SISTEMA-WORKFLOW.md`.*
