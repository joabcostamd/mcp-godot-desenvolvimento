# MASTER_IMPLEMENTATION_ROADMAP.md

> **Documento mestre da reorganização da arquitetura de Tools do MCP Godot Agent.**
> Fonte única de verdade. Substitui qualquer instrução conflitante em
> `ARQUITETURA_MCP.md`, `README.md` ou `CONTEXTO_PROJETO_MCP_GODOT.md`.
>
> **Público:** IA agêntica executora (Cline + DeepSeek V4) e revisor humano.
> **Repositório:** `github.com/joabcostamd/mcp-godot-desenvolvimento`
> **Versão:** 1.0 · **Data:** 2026-07-21

---

## AVISO DE BLOQUEIO — LEIA ANTES DE TUDO

Este roadmap foi escrito sobre um estado do código que **ainda não foi medido**.
Todo número marcado `[NÃO MEDIDO]` vem de leitura de código, não de execução.

**A FASE 0 é um portão duro.** Nenhuma outra fase começa antes de a FASE 0 produzir
números medidos por script executado. Se a FASE 0 revelar que a realidade difere das
estimativas, **este documento deve ser corrigido antes de prosseguir** — não ignorado.

A IA executora está **proibida** de:
- pular a FASE 0;
- substituir medição por análise estática de código;
- preencher um critério de aceite com raciocínio no lugar de saída de comando.

Se a IA não conseguir executar comandos no terminal, ela **para e reporta**. Não improvisa.

---

## ÍNDICE

1. [Visão geral da arquitetura final](#1-visão-geral-da-arquitetura-final)
2. [Objetivos da reorganização](#2-objetivos-da-reorganização)
3. [Estado atual vs. estado desejado](#3-estado-atual-vs-estado-desejado)
4. [Princípios arquiteturais obrigatórios](#4-princípios-arquiteturais-obrigatórios)
5. [Invariantes do sistema](#5-invariantes-do-sistema)
6. [Convenções e nomenclatura](#6-convenções-e-nomenclatura)
7. [Estrutura definitiva de diretórios](#7-estrutura-definitiva-de-diretórios)
8. [Estrutura definitiva das tools](#8-estrutura-definitiva-das-tools)
9. [Responsabilidades por módulo](#9-responsabilidades-por-módulo)
10. [Fluxo completo de execução](#10-fluxo-completo-de-execução)
11. [Estratégias transversais](#11-estratégias-transversais)
12. [Decisões técnicas fechadas](#12-decisões-técnicas-fechadas)
13. [Protocolo obrigatório de pesquisa](#13-protocolo-obrigatório-de-pesquisa)
14. [Protocolo obrigatório de prova](#14-protocolo-obrigatório-de-prova)
15. [Protocolo obrigatório de auditoria](#15-protocolo-obrigatório-de-auditoria)
16. [Protocolo obrigatório de testes](#16-protocolo-obrigatório-de-testes)
17. [Fases de implementação](#17-fases-de-implementação)
18. [Guia de resolução de problemas](#18-guia-de-resolução-de-problemas)
19. [Checklist global de qualidade](#19-checklist-global-de-qualidade)
20. [Glossário](#20-glossário)
- [Apêndice A — Ordem resumida](#apêndice-a--ordem-de-execução-resumida)
- [Apêndice B — Métricas](#apêndice-b--métricas-de-acompanhamento)
- [Apêndice C — Critério de parada](#apêndice-c--critério-de-parada-do-projeto)

---

## 1. VISÃO GERAL DA ARQUITETURA FINAL

### 1.1 O problema em uma frase

O MCP tem capacidade técnica sobrando e **superfície de exposição demais**. O modelo
enxerga entre 50 e 100 tools por fase, quando o estado da arte recomenda 3–5 sempre
carregadas e o resto descoberto sob demanda. A meta de ~33 tools já estava escrita no
próprio código (`_meta_tool.py`, linha 6) e o sistema andou na direção oposta:
143 → 287.

### 1.2 O modelo alvo em 4 camadas

```
┌──────────────────────────────────────────────────────────────────┐
│ L0 — SUPERFÍCIE (o que o modelo vê em tools/list)                │
│      ≤ 33 tools. Garantido por invariante, não por disciplina.   │
│      = 10 sempre-visíveis + ≤ 12 rollups da fase atual           │
│        + 3 meta-tools de descoberta                              │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│ L1 — REGISTRY (fonte única de verdade)                           │
│      registry/ deriva tools/list, handlers, fases e namespaces   │
│      a partir de UM manifesto por domínio.                       │
│      Divergência entre camadas passa a ser impossível.           │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│ L2 — DOMÍNIOS (~33 domínios, ~300 ops)                           │
│      manifest.py + ops.py + handlers.py + schemas.py             │
│      + examples.py + tests/                                      │
│      Ops NUNCA aparecem no wire. Acesso só via rollup.           │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│ L3 — ADAPTADORES (transporte)                                    │
│      headless CLI · editor TCP :9080 · game TCP :9081            │
│      addon WS :9082 · runtime bridge TCP :8790 · LSP :6005       │
│      Seleção AUTOMÁTICA. O modelo nunca escolhe transporte.      │
└──────────────────────────────────────────────────────────────────┘
```

### 1.3 A superfície L0 detalhada

**Grupo A — Sempre visíveis (10 tools, em toda fase):**

| Tool | Substitui | Ops |
|---|---|---|
| `godot` | intent router existente | (linguagem natural livre) |
| `catalog_search` | `tool_catalog`, `tool_groups` | `search`, `list_domains` |
| `describe_tool` | — | `describe` |
| `invoke_by_name` | — | `invoke` |
| `session_manage` | `get_next_step`, `resume_session`, `health_check`, `ping`, `self_test`, `workflow_handoff`, `workflow_snapshot` | `start`, `resume`, `health`, `handoff`, `snapshot` |
| `phase_manage` | `get_current_phase`, `advance_phase`, `get_phase_history` | `get`, `advance`, `history`, `criteria` |
| `milestone_manage` | `create_milestone_plan`, `get_milestone_plan`, `advance_milestone`, `project_progress` | `plan`, `get`, `advance`, `progress` |
| `proof_manage` | `capture_proof`, `verify_proof` | `capture`, `verify`, `ledger` |
| `safety_manage` | (já existe) | `checkpoint`, `undo`, `backup`, `restore`, `policy`, `status` |
| `vcs_manage` | **NOVO** (ver D-11) | `diff`, `blame`, `log`, `status`, `commit_checkpoint` |

**Grupo B — Rollups de domínio, trocados por fase (≤ 12 simultâneos):**

| Fase | Rollups visíveis |
|---|---|
| IDEIA | `gdd_manage`, `analysis_manage`, `project_manage` |
| DESIGN | `scene_manage`, `node_manage`, `script_manage`, `ui_manage`, `lsp_manage`, `gdd_manage`, `config_manage` |
| PROTOTIPO | `scene_manage`, `node_manage`, `script_manage`, `editor_manage`, `runtime_manage`, `physics_manage`, `anim_manage`, `asset_manage`, `vfx_manage`, `audio_manage`, `camera_manage`, `shader_manage` |
| CONTEUDO | `scene_manage`, `node_manage`, `asset_manage`, `audio_manage`, `world_manage`, `balance_manage`, `i18n_manage`, `gameplay_manage`, `tilemap_manage`, `navigation_manage`, `dialogue_manage`, `inventory_manage` |
| POLIMENTO | `test_manage`, `verify_manage`, `profile_manage`, `debug_manage`, `analysis_manage`, `screenshot_manage` |
| PRONTO_PARA_LANCAR | `export_manage`, `publish_manage`, `release_manage`, `editor_manage` |

**Teto matemático:** 10 + 12 = 22 na pior fase. INV-05 fixa o limite em **33** para
dar folga a exceções justificadas.

### 1.4 Estado read-only migra para Resources

Tudo que só lê estado sai de Tools e vira Resource MCP. Zero perda de funcionalidade,
redução direta de superfície:

```
godot://phase/current       godot://milestone/plan      godot://project/status
godot://gdd                 godot://brief               godot://console/output
godot://editor/state        godot://scene/current       godot://proof/ledger
godot://registry/health     godot://roadmap
```

---

## 2. OBJETIVOS DA REORGANIZAÇÃO

**Objetivos primários (medíveis, com critério de aceite):**

| # | Objetivo | Métrica | Meta |
|---|---|---|---|
| O1 | Reduzir superfície de wire | tools visíveis na pior fase | ≤ 33 |
| O2 | Eliminar divergência de registro | divergências em `validate_mcp_registry` | 0 |
| O3 | Fonte única de verdade | lugares onde uma tool é declarada | 1 |
| O4 | Conformidade com a spec MCP | campos fora da spec em `annotations` | 0 |
| O5 | Eliminar duplicação de capacidade | famílias com rollup + atômicas no wire | 0 |
| O6 | Descoberta progressiva ativa | trio `search`/`describe`/`invoke` visível | em toda fase |
| O7 | Custo de contexto controlado | tokens de `tools/list` por fase | ≤ 12.000 |
| O8 | Prevenir regressão do problema | invariantes falhando o build | 0 |

**Objetivos secundários:**

- **O9.** Reduzir escolha errada de tool (transporte deixa de ser decisão do modelo).
- **O10.** Registro auditável por script, não por leitura humana.
- **O11.** Documentação refletindo o código (hoje descreve um sistema morto).
- **O12.** Freio de entrada: tool nova só entra como `op`, salvo justificativa escrita.

**Não-objetivos (explicitamente fora de escopo):**

- Reescrever handlers ou lógica de negócio.
- Mudar o protocolo de transporte com o Godot.
- Implementar `defer_loading` da API Anthropic (não funciona com Cline + DeepSeek).
- Implementar paginação de `tools/list` (não economiza contexto — ver D-07).
- Implementar programmatic tool calling / code mode (exige sandbox e cliente compatível).

---

## 3. ESTADO ATUAL VS. ESTADO DESEJADO

### 3.1 Estado atual conhecido `[PARCIALMENTE NÃO MEDIDO]`

| Item | Valor | Origem | Confiança |
|---|---|---|---|
| `Tool()` em `core/tool_definitions.py` | 287 | grep `name=` | Média |
| Rollup builders em `tools/rollups.py` | 32 | `_ROLLUP_BUILDERS` | Alta |
| `_manage` escritos à mão em `_raw_tool_defs()` | 13 | grep | Média |
| Handlers em `_build_handlers()` | ~184 | regex frágil | **Baixa** |
| Handlers de rollup | 32 | `get_rollup_handlers()` | Alta |
| Namespaces (`TOOLSETS`) | 5 | `server.py:59` | Alta |
| Entradas somadas em `TOOLSETS` | 306 | soma | Média |
| **Delta entradas − tools** | **19** | 306 − 287 | **Não explicado** |
| Fases (`PHASE_TOOLSETS`) | 6 | `server.py:385` | Alta |
| `PHASE_TOOLS_CORE` | 31 (comentário diz 27) | `server.py:569` | Alta |
| Perfis (`TOOL_PROFILES`) | 4: core=15, dev=46, lean=14, full | `server.py:328` | Média |
| Tools sem fase ("órfãs") | 75 (26%) | catálogo | Média |
| Tools visíveis na maior fase | 100 (PROTOTIPO) | catálogo | Média |
| Invalidação de cache por fase | **Funciona** | código colado | **Alta** |
| Meta original documentada em código | ~33 tools | `_meta_tool.py:6` | **Alta** |

**Contradições documentais confirmadas — 7 números diferentes para "quantas tools":**

| Fonte | Valor |
|---|---|
| `_meta_tool.py` (meta declarada) | 33 |
| `README.md` (rodapé) | 143+ |
| `README.md` (topo) | 171 |
| `ARQUITETURA_MCP.md` (rodapé) | 189 |
| `ARQUITETURA_MCP.md` (corpo) | 191 |
| `CONTEXTO_PROJETO_MCP_GODOT.md` | 248 |
| Catálogo 21/07 | 287 |

**Contradições internas dentro de `ARQUITETURA_MCP.md`:**
- §2 diz `core=31, dev=80`; §3.5.1 e §7.1 dizem `core=16, dev=31`.
- §2 diz "69 módulos"; §10 e rodapé dizem "64 módulos".
- §2 diz "27 rollups"; o catálogo conta 44 marcadores `[R]`.
- §3.3 diz que `_TOOL_DEFS_CACHE` "nunca invalida"; §7.0b diz que invalida por callback.
- §3.5.2 descreve 10 toolsets (`scene_ops`, `script_ops`, `git_ops`…) que **não existem no código**.
- §4.3 e §6 (Passo 3) ensinam a usar `_READONLY`, `_TITLES`, `_TAGS` — suspeitos de código morto.
- `core/tool_definitions.py`, onde vivem as 272 `Tool()` (236 visíveis após filtros), **não é mencionado em nenhum documento**.

### 3.2 Estado desejado

| Item | Alvo |
|---|---|
| Tools no wire (pior fase) | ≤ 33 |
| Fontes de declaração por tool | 1 (`domains/<x>/manifest.py`) |
| Caminhos de criação de rollup | 1 (`_meta_tool.create_manage_tool`) |
| Tools sem handler | 0 |
| Handlers sem tool | 0 |
| Nomes duplicados entre namespaces | 0 |
| Campos fora da spec em `ToolAnnotations` | 0 |
| Famílias com rollup **e** atômicas no wire | 0 |
| Código morto (`_READONLY`, `_TITLES`, `_TAGS`) | 0 |
| Documentos com contagem divergente | 0 |
| Invariantes verificadas em CI | 15 |

---

## 4. PRINCÍPIOS ARQUITETURAIS OBRIGATÓRIOS

**P1 — Uma fonte de verdade.** Toda propriedade de uma tool (nome, descrição, schema,
hints, ops, fase, namespace) é declarada em exatamente um lugar. `tools/list`,
handlers, curadoria por fase e catálogo são **derivados**, nunca mantidos à mão.
*Consequência:* se `validate_mcp_registry` precisa existir para detectar divergência,
o design está errado. Divergência deve ser impossível, não detectável.

**P2 — Superfície mínima, capacidade máxima.** Reduzir o que o modelo vê nunca
significa remover capacidade. Capacidade sai do wire e entra em `op`.

**P3 — O transporte é invisível para o modelo.** O agente pede `node_manage(op=create)`.
Quem decide entre addon WebSocket, arquivo `.tscn` ou TCP é o adaptador. O modelo não
tem informação para essa escolha e por isso erra.

**P4 — Visibilidade ≠ bloqueio.** Curadoria por fase esconde, não impede. Bloqueio real
é responsabilidade exclusiva de gates (`advance_phase`, `run_verification_pipeline`,
`release_checklist`). Nunca confundir os dois ao avaliar se uma trava é real ou cosmética.

**P5 — Estado sempre consistente.** Cada fatia entra e sai com o servidor funcionando.
É proibido um commit intermediário onde `tools/list` está quebrado.

**P6 — Invariante > convenção.** Regra que não é verificada por script não existe.
Toda regra deste documento que puder virar invariante executável deve virar.

**P7 — Prova mecânica > alegação.** Nenhuma etapa fecha com "funcionou". Fecha com
saída de comando colada.

**P8 — Reversibilidade.** Toda fatia tem rollback de um comando. Se não tem, quebra em
fatias menores.

**P9 — Dogfooding decide prioridade.** Fricção encontrada construindo um jogo real tem
precedência sobre item de lista teórica.

**P10 — Retorno decrescente é critério de parada.** Quando um objetivo mensurável for
atingido, parar. Não refinar além do necessário.

---

## 5. INVARIANTES DO SISTEMA

Estas 15 regras viram código em `registry/invariants.py` e **falham o build**.
Cada fase declara quais invariantes passa a satisfazer.

| ID | Invariante | Fase que ativa |
|---|---|---|
| INV-01 | Toda tool em `tools/list` tem handler registrado | F0 (mede), F2 (corrige) |
| INV-02 | Todo handler registrado corresponde a uma tool em `tools/list` | F0, F2 |
| INV-03 | Toda tool pertence a exatamente 1 namespace | F2 |
| INV-04 | Toda tool está em ≥ 1 fase OU tem flag `internal=True` | F8 |
| INV-05 | Nenhuma fase expõe mais de 33 tools distintas | F5 |
| INV-06 | `tokens(tools/list)` por fase ≤ 12.000 | F5 |
| INV-07 | Se existe `X_manage` no wire, nenhuma `X_*` atômica está no wire | F5 |
| INV-08 | Toda tool tem os 4 hints MCP dentro de `annotations` | F2 |
| INV-09 | `annotations` contém **apenas** campos da spec `ToolAnnotations` | F2 |
| INV-10 | Todo nome em `PHASE_TOOLSETS` existe em `tools/list` | F1 |
| INV-11 | Todo nome em `TOOLSETS` existe em `tools/list` | F1 |
| INV-12 | Nenhum nome aparece em 2+ namespaces | F1 |
| INV-13 | Nenhum nome é definido em 2+ lugares (colisão de registro) | F3 |
| INV-14 | Nenhum par de tools tem similaridade de descrição ≥ 0.80 | F5 |
| INV-15 | Toda tool com `destructiveHint=true` tem rollback documentado | F2 |

**Como INV-14 é calculado:** `difflib.SequenceMatcher` sobre descrições normalizadas
(minúsculas, sem acento, sem pontuação). Limiar 0.80. A falha lista os pares.

**Como INV-06 é calculado:** serializar `tools/list` de cada fase em JSON e dividir o
tamanho por 4 (aproximação de tokens). `estimate_tool_tokens` já faz isso — reaproveitar.

---

## 6. CONVENÇÕES E NOMENCLATURA

### 6.1 Regras de nome

```
ROLLUP        <dominio>_manage        snake_case, singular, sufixo _manage
              ✅ scene_manage, physics_manage, vcs_manage
              ❌ scene, d3_manage (ver 6.2), sceneManage

OP            <verbo>_<objeto>        verbo no infinitivo, inglês
              ✅ create_node, set_property, list_bones, run_headless
              ❌ node_create, doCreate, criar_no

META-TOOL     nome curto sem sufixo
              ✅ godot, catalog_search, describe_tool, invoke_by_name

PROIBIDO      prefixo de transporte no nome
              ❌ addon_create_node, game_raycast, godot_screenshot
              ✅ node_manage(op=create), physics_manage(op=raycast)

PROIBIDO      dimensão no nome → vira parâmetro
              ❌ create_light_2d + create_light_3d
              ✅ node_manage(op=create_light, params={"dim":"2d"})

PROIBIDO      sinônimos para o mesmo conceito
              Um conceito, um nome. "screenshot" nunca "capture" nem "snapshot".

PROIBIDO      abreviação não óbvia
              ❌ d3_manage      ✅ scene3d_manage
```

### 6.2 Renomeações obrigatórias

| Atual | Novo | Motivo |
|---|---|---|
| `d3_manage` | `scene3d_manage` | `d3` é ambíguo (D3.js? 3D?) |
| `game_bridge_manage` | fundir em `runtime_manage` | duplica capacidade |
| `vision_manage` | `screenshot_manage` | "vision" não descreve a capacidade |

Toda renomeação carrega alias por uma fase (§11.9).

### 6.3 Padrão de descrição (obrigatório para toda tool e op)

Seis blocos, nesta ordem, sem exceção:

```
1. O QUE FAZ      — uma frase, verbo primeiro
2. QUANDO USAR    — cenário típico concreto
3. QUANDO NÃO     — nome da ferramenta alternativa
4. PRÉ-CONDIÇÕES  — o que precisa existir antes
5. EXEMPLO        — JSON real, valores plausíveis (nunca "string"/"value")
6. ERRO COMUM     — o erro mais frequente e como resolver
```

A descrição do rollup é montada automaticamente por `create_manage_tool` a partir das
docstrings das ops. **Toda op precisa ter docstring de primeira linha útil**, senão a
descrição do rollup degrada e a busca de `catalog_search` piora.

### 6.4 Padrão de retorno

```python
{"status": "success", "backend": "addon_ws", ...}          # sucesso
{"status": "error", "message": "...",                       # erro
 "error_code": 1001, "hint": "como resolver"}
```

A mensagem de erro diz **o que fazer**, não só o que falhou.
Ruim: `"parâmetro inválido"`.
Bom: `"scene_path deve começar com res://; recebido 'C:/x.tscn'"`.

---

## 7. ESTRUTURA DEFINITIVA DE DIRETÓRIOS

```
mcp-godot-desenvolvimento/
│
├── server.py                     # ≤ 300 linhas. SÓ bootstrap e roteamento.
│                                 # Zero Tool(), zero constante de curadoria.
│
├── registry/                     # ◄── FONTE ÚNICA DE VERDADE
│   ├── __init__.py               # build_tool_defs(), build_handlers()
│   ├── types.py                  # DomainManifest, OpSpec, Phase
│   ├── discovery.py              # varre domains/ e agrega os manifests
│   ├── phases.py                 # PHASE → [domínios] + ops permitidas
│   ├── profiles.py               # PROFILE → subconjunto (2 perfis, ver D-06)
│   ├── annotations.py            # ToolAnnotations conforme spec, sem extras
│   ├── errors.py                 # ok() / err() padronizados
│   ├── invariants.py             # INV-01..15, executável, falha o build
│   ├── legacy_adapter.py         # lê o legado até a migração terminar
│   └── tokens.py                 # medição de custo de tools/list por fase
│
├── domains/                      # ◄── UM DIRETÓRIO POR DOMÍNIO
│   ├── __init__.py
│   ├── _template/                # esqueleto para copiar
│   │   ├── manifest.py
│   │   ├── ops.py
│   │   ├── handlers.py
│   │   ├── schemas.py
│   │   ├── examples.py
│   │   └── tests/test_manifest.py
│   ├── scene/       node/        script/      physics/
│   ├── ui/          anim/        asset/       audio/
│   ├── vfx/         shader/      camera/      tilemap/
│   ├── navigation/  dialogue/    inventory/   scene3d/
│   ├── editor/      runtime/     test/        verify/
│   ├── profile/     debug/       export/      publish/
│   ├── i18n/        world/       balance/     gameplay/
│   ├── gdd/         analysis/    lsp/         config/
│   └── screenshot/
│
├── core/                         # tools de processo, sempre visíveis
│   ├── session.py   phase.py     milestone.py  brief.py
│   ├── proof.py     safety.py    vcs.py        router.py
│
├── meta/                         # descoberta progressiva (padrão MCP 3 camadas)
│   ├── catalog_search.py         # camada 1 — buscar
│   ├── describe_tool.py          # camada 2 — inspecionar
│   └── invoke_by_name.py         # camada 3 — executar
│
├── adapters/                     # transporte, invisível para o modelo
│   ├── transport.py              # ◄── SELEÇÃO AUTOMÁTICA
│   ├── headless_cli.py           editor_tcp.py     # :9080
│   ├── game_tcp.py               # :9081
│   ├── addon_ws.py               # :9082
│   ├── runtime_bridge.py         # :8790
│   └── lsp.py                    # :6005
│
├── resources/                    # MCP Resources (estado read-only)
│   ├── __init__.py
│   └── uris.py
│
├── experimental/                 # verticais construídas antes da demanda
│   ├── telemetry/  accessibility/  onboarding/  cutscene/
│   ├── quest/      mods/           trailer/     achievements/
│   └── README.md                 # critério de saída da quarentena
│
├── _meta_tool.py                 # fábrica de rollup — ÚNICO caminho permitido
├── tools/                        # legado, esvaziado progressivamente
├── tests/
│   ├── test_invariants.py  test_registry.py  test_aliases.py
│   ├── test_failures.py    test_rollback.py  test_edge.py
│   └── domains/
├── scripts/
│   ├── audit_registro.py         # medição (FASE 0)
│   ├── audit_fase.py             # auditoria pós-fase
│   ├── dump_toollist.py          # snapshot de tools/list para comparação
│   └── gen_catalog.py            # gera o catálogo A PARTIR do registry
└── MASTER_IMPLEMENTATION_ROADMAP.md
```

**Regra de migração:** `tools/` não é deletado de uma vez. Cada domínio migrado move
seus arquivos para `domains/<x>/` e `tools/` encolhe. Só é removido quando estiver vazio.

---

## 8. ESTRUTURA DEFINITIVA DAS TOOLS

### 8.1 O manifesto — o coração da arquitetura

`domains/scene/manifest.py`:

```python
"""Manifesto do domínio scene. FONTE ÚNICA DE VERDADE deste domínio."""

from registry.types import DomainManifest, OpSpec, Phase
from . import handlers

MANIFEST = DomainManifest(
    # ── Identidade ──────────────────────────────────────────────
    domain="scene",
    tool_name="scene_manage",
    title="Gerenciar Cenas (.tscn)",
    namespace="project",
    version="1.0.0",
    aliases=[],                       # nomes antigos, removidos após 1 fase

    description=(
        "Cria, abre, salva e modifica cenas Godot (.tscn).\n"
        "QUANDO USAR: qualquer operação estrutural em arquivo de cena.\n"
        "QUANDO NÃO USAR: para nós dentro de uma cena, use node_manage.\n"
        "PRÉ-CONDIÇÕES: projeto ativo configurado.\n"
        "ERRO COMUM: caminho sem prefixo res:// — sempre use res://cenas/x.tscn."
    ),

    # ── Curadoria ───────────────────────────────────────────────
    phases=[Phase.DESIGN, Phase.PROTOTIPO, Phase.CONTEUDO],
    always_visible=False,
    internal=False,
    named_justification=None,         # obrigatório se não for rollup (ver O12)

    # ── Anotações MCP (SOMENTE campos da spec) ──────────────────
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },

    # ── Operações ───────────────────────────────────────────────
    ops=[
        OpSpec(
            name="create",
            fn=handlers.create_scene,
            summary="Cria arquivo .tscn com nó raiz",
            schema={
                "path":      {"type": "string", "required": True,
                              "description": "Caminho res:// do .tscn"},
                "root_type": {"type": "string", "required": True,
                              "description": "Classe do nó raiz (ex: Node2D)"},
            },
            examples=[{"path": "res://cenas/player.tscn",
                       "root_type": "CharacterBody2D"}],
            annotations={"destructiveHint": False, "idempotentHint": False},
            rollback="safety_manage(op=undo)",
        ),
        OpSpec(
            name="save",
            fn=handlers.save_scene,
            summary="Salva a cena aberta no editor",
            schema={"path": {"type": "string", "required": False}},
            examples=[{"path": "res://cenas/player.tscn"}],
            annotations={"destructiveHint": True, "idempotentHint": True},
            rollback="safety_manage(op=restore, params={'file': path})",
        ),
        # ...
    ],
)
```

### 8.2 O que o manifesto elimina

| Antes (3+ lugares) | Depois (1 lugar) |
|---|---|
| `Tool()` em `core/tool_definitions.py` | `MANIFEST.description` + `MANIFEST.ops[].schema` |
| entrada em `_build_handlers()` | `MANIFEST.ops[].fn` |
| entrada em `TOOLSETS[ns]` | `MANIFEST.namespace` |
| entrada em `PHASE_TOOLSETS[fase]` | `MANIFEST.phases` |
| entrada em `_READONLY` / `_TAGS` / `_TITLES` | `MANIFEST.annotations` / `MANIFEST.title` |
| builder em `tools/rollups.py` | gerado por `registry.discovery` |

**INV-13 passa a ser garantida por construção**, não verificada a posteriori.

### 8.3 Handlers — funções puras

`domains/scene/handlers.py`:

```python
"""Handlers do domínio scene. NÃO conhecem MCP, nem Tool, nem annotations."""

from adapters.transport import pick          # ◄── nunca importa adapter direto
from registry.errors import ok, err

def create_scene(*, path: str, root_type: str) -> dict:
    """Cria arquivo .tscn com nó raiz."""      # ◄── vira o summary da op
    if not path.startswith("res://"):
        return err(1001, "path deve começar com res://",
                   hint=f"use res://cenas/{path.lstrip('/')}")
    backend = pick(capability="scene.write", prefer=None)
    return ok(backend.create_scene(path=path, root_type=root_type))
```

**Regras duras para handlers:**
- Argumentos **keyword-only** (`*`). Elimina de vez a classe de bug posicional-vs-nomeado.
- Nunca importam `mcp.types`.
- Nunca escolhem transporte diretamente — sempre via `adapters.transport.pick()`.
- Sempre retornam `ok()` ou `err()`, nunca levantam exceção para o chamador.
- Docstring de primeira linha é o `summary` da op — é lida pelo modelo.

---

## 9. RESPONSABILIDADES POR MÓDULO

| Módulo | Faz | **Não** faz |
|---|---|---|
| `server.py` | bootstrap MCP, roteia `call_tool`, rate limit | declarar tools, filtrar por fase, aplicar hints |
| `registry/discovery.py` | varre `domains/`, agrega manifests | conhecer domínio específico |
| `registry/phases.py` | mapeia fase → domínios | decidir se a fase pode avançar |
| `registry/annotations.py` | valida contra a spec `ToolAnnotations` | inventar campo |
| `registry/invariants.py` | verifica INV-01..15 | corrigir automaticamente |
| `domains/<x>/manifest.py` | declara tudo do domínio | conter lógica |
| `domains/<x>/handlers.py` | lógica de negócio | conhecer MCP ou transporte |
| `adapters/transport.py` | escolhe backend por capacidade | lógica de domínio |
| `core/proof.py` | coleta evidência mecânica | gerar texto sobre a evidência |
| `core/vcs.py` | diff/blame/log mecânicos | interpretar o diff |
| `meta/*` | descoberta progressiva | executar lógica de domínio |
| `experimental/*` | verticais em quarentena | aparecer em qualquer fase |

**Regra de dependência (unidirecional, verificada por invariante):**

```
server.py → registry → domains → adapters
                    ↘ core
                    ↘ meta
```

- `domains/` **nunca** importa `server.py` nem `registry/`.
- `adapters/` **nunca** importa `domains/`.
- `domains/a` **nunca** importa `domains/b`.

Qualquer import que viole isso é erro de build.

---

## 10. FLUXO COMPLETO DE EXECUÇÃO

### 10.1 Startup

```
1. server.py inicia
2. registry.discovery varre domains/*/manifest.py  → lista de DomainManifest
3. registry.annotations valida cada MANIFEST        → falha se inválido
4. registry.invariants roda INV-01..15              → falha se violado
5. registry.phases lê .mcp_phase_state.json         → fase atual
6. build_tool_defs(fase) devolve ≤ 33 Tool(), ordenadas por nome
7. build_handlers() devolve dict completo (NÃO filtrado por fase — P4)
8. registry.tokens mede o custo e loga
```

Ordenação determinística por nome no passo 6 é **obrigatória**: protege a comparação
`fc` das fatias e evita invalidar prompt caching sem necessidade.

### 10.2 Chamada normal

```
Agente → scene_manage({op:"create", params:{path:"res://x.tscn", root_type:"Node2D"}})
   ↓ server.py: rate limit → busca handler
   ↓ _meta_tool.build_manage_handler: valida op contra o enum
   ↓                                  op inválida → difflib sugere as 3 mais próximas
   ↓ domains/scene/handlers.create_scene(**params)   ← keyword-only
   ↓ adapters.transport.pick("scene.write")
   ↓   addon conectado?  → addon_ws (ganha UndoRedo nativo)
   ↓   senão             → headless_cli (escreve .tscn direto)
   ↓ ok({...})
Agente ← {"status":"success", "scene_path":"res://x.tscn", "backend":"addon_ws"}
```

`backend` no retorno é **obrigatório** — é como o humano audita qual transporte rodou.

### 10.3 Descoberta progressiva (o agente não vê a tool que precisa)

```
1. catalog_search({query:"gerar shader de dissolve"})
   → [{tool:"shader_manage", op:"generate", summary:"..."}]        ~200 tokens

2. describe_tool({tool:"shader_manage", op:"generate"})
   → schema completo + examples da op                              ~400 tokens

3. shader_manage({op:"generate", params:{...}})
```

Este é o padrão de três camadas da documentação oficial MCP (Catálogo → Inspeção →
Execução), implementado **server-side** — obrigatório, porque Cline + DeepSeek não
suportam `defer_loading` da API Anthropic.

### 10.4 Avanço de fase

```
1. phase_manage({op:"advance"})
2. core/phase.py verifica critério objetivo da fase
   → falhou? devolve o que falta e NÃO avança
3. avançou → grava .mcp_phase_state.json
4. → chama _invalidate_tool_caches()   (já implementado e confirmado funcionando)
5. próximo tools/list reflete a nova fase, sem reiniciar o servidor
```

---

## 11. ESTRATÉGIAS TRANSVERSAIS

### 11.1 Modularização
A unidade é o **domínio**, não o arquivo. Um domínio é autossuficiente: manifesto,
handlers, schemas, exemplos e testes no mesmo diretório.
Critério para existir como domínio: **≥ 3 ops coesas** que compartilham pré-condições.
Menos que isso → vira op de um domínio existente.

### 11.2 Compartilhamento de código
Lógica usada por 2+ domínios sobe para `registry/` (infraestrutura) ou `core/`
(processo). **Nunca** import cruzado entre domínios. Se dois domínios precisam da mesma
função, ela sobe. Verificado por invariante de dependência.

### 11.3 Evitar duplicação
Três mecanismos em camadas:
1. **INV-07** — rollup e atômica não coexistem no wire.
2. **INV-14** — descrições com similaridade ≥ 0.80 falham o build.
3. **Freio de entrada** — tool nova só entra como `op`; virar tool nomeada exige
   `named_justification` preenchido no manifesto.

### 11.4 Reduzir acoplamento
- Handlers não conhecem MCP → testáveis sem servidor.
- Handlers não conhecem transporte → testáveis sem Godot.
- Registry não conhece domínio específico → domínio novo não altera o registry.
- Grafo de dependência unidirecional, verificado por script.

### 11.5 Maximizar coesão
Teste da coesão: *"esta op pode ser explicada sem citar outro domínio?"*
Se não, está no domínio errado. Exemplo: `add_raycast_2d` cria um **nó**, mas o
conceito raycast é de física → domínio `physics`, op `add_raycast`.

### 11.6 Escalabilidade
Adicionar um domínio: copiar `domains/_template/`, preencher o manifesto, pronto.
Nenhum arquivo central é editado. O custo marginal de um domínio novo é **constante**,
não linear — é isso que impede a volta do crescimento de 143 → 287.

### 11.7 Extensibilidade
Adicionar uma op: uma entrada em `MANIFEST.ops`. **Zero impacto no wire** (a op não
aparece em `tools/list`, só na descrição do rollup). Esta é a razão de ser da
arquitetura inteira: capacidade cresce sem que a superfície cresça.

### 11.8 Versionamento interno
Cada manifesto declara `version` (semver do domínio). Cada op pode declarar
`deprecated_since` e `replaced_by`. Op deprecada:
1. continua funcionando;
2. some da descrição do rollup;
3. retorna aviso em `warnings[]` no resultado;
4. é removida após 2 fases fechadas do projeto de jogo.

### 11.9 Compatibilidade retroativa
Fatias que renomeiam algo mantêm **alias por uma fase** via `MANIFEST.aliases`.
O alias resolve para o novo nome, loga `deprecated_alias_used`, e é removido na fase
seguinte. Isso protege `.clinerules/workflows/act.md`, `plan.md` e prompts salvos.

---

## 12. DECISÕES TÉCNICAS FECHADAS

Decisões já tomadas. A IA executora **não deve reabrir** nenhuma delas sem escalar (§18.2).

| ID | Decisão | Justificativa | Alternativa rejeitada |
|---|---|---|---|
| **D-01** | Manter o sufixo `_manage` nos rollups | Renomear 32 tools quebra `.clinerules`, prompts salvos e hábito do agente. A economia de tokens é irrelevante (~7 chars × 12 tools). Risco real, benefício nulo. | Renomear para `scene`, `node` etc. |
| **D-02** | Rollup com `op` enum + `params` livre | Declarar todos os params de todas as ops num único `inputSchema` explode o schema. Validação fica no handler, com erro didático. Mitigado por `examples` por op. | `oneOf` por op no JSON Schema |
| **D-03** | UM rollup por domínio, não `X_read` + `X_write` | Separar dobra a contagem (12 → 24) para resolver um problema de granularidade de anotação que ainda não incomodou. Anotar conservador e reavaliar. | Split read/write |
| **D-04** | Progressive discovery **server-side** | Cline + DeepSeek não suportam `defer_loading` (feature da API Anthropic). O trio `catalog_search`/`describe_tool`/`invoke_by_name` já existe — só está órfão. | `defer_loading`, Tool Search Tool |
| **D-05** | Fase controla **domínios**, não tools | Trocar 12 rollups é o que colapsa 100 → 22. Trocar tools individuais é o desenho atual e não escala. | Manter `PHASE_TOOLSETS` por tool |
| **D-06** | Reduzir de 4 perfis para 2: `standard` e `full` | `core=15`, `dev=46`, `lean=14` são estáticos, escolhidos uma vez e esquecidos. Três filtros no mesmo eixo geram drift e precedência indefinida. `full` fica como escape hatch de debug. | Manter 4 perfis |
| **D-07** | **Não** implementar paginação de `tools/list` | Paginação da spec é cursor-based e serve a transporte. Clientes seguem os cursores até o fim e carregam tudo. Zero economia de contexto. | Paginar |
| **D-08** | Anotações **apenas** com campos da spec `ToolAnnotations` | `audience`, `priority` e `lastModified` pertencem a `ResourceAnnotations`, não a tool. `intrusiveHint` é SEP proposta, não aceita. Campos fora da spec quebram em upgrade de SDK. | Manter os campos extras |
| **D-09** | Substituir `_HINT_RULES` (heurística por nome) por declaração explícita | Inferir hint por prefixo do nome, sobre nomenclatura comprovadamente inconsistente, produz anotação errada em massa. Anotação errada é **pior** que ausente: dá falsa confiança ao cliente sobre pedir ou não confirmação. | Manter inferência por prefixo |
| **D-10** | Verticais prematuras → `experimental/`, não deletar | 43 tools (telemetria, acessibilidade, onboarding, cutscene, quest, mods, trailer) nunca foram exercitadas por um jogo real. Deletar perde trabalho; manter no wire polui. Quarentena resolve os dois. | Deletar / distribuir em fases |
| **D-11** | Criar domínio `vcs` | O processo de prova do projeto depende de `git diff`/`blame`/`log -p` executados pelo agente via shell — exatamente onde a evidência é forjada. Tool mecânica alimentando `capture_proof` ataca o gargalo real do projeto. | Continuar via shell |
| **D-12** | Estado read-only → MCP Resources | ~10 tools saem do wire com zero perda. Aderente à spec. Infra de Resources já existe (6 URIs `godot://`). | Manter como tools |
| **D-13** | `validate_mcp_registry` vira teste de CI, não tool de runtime | Consistência de registro é invariante, não consulta. Após F1 a divergência é impossível por construção. | Manter como tool |
| **D-14** | Migração **por domínio**, um por fatia | Migrar tudo de uma vez viola P5 (estado consistente) e torna o rollback impossível. | Big bang |

---

## 13. PROTOCOLO OBRIGATÓRIO DE PESQUISA

Antes de **qualquer** alteração que envolva a spec MCP, o SDK Python, o protocolo ou a
API do Godot, executar os 7 passos. Sem exceção.

```
1. CONFIRMAR COMPORTAMENTO ESPERADO na documentação oficial
2. IDENTIFICAR BREAKING CHANGES entre a versão instalada e a documentada
3. IDENTIFICAR BOAS PRÁTICAS recomendadas pelos mantenedores
4. VERIFICAR EXEMPLOS OFICIAIS (repositório oficial, não blog)
5. VERIFICAR LIMITAÇÕES CONHECIDAS (issues abertas)
6. VERIFICAR PROBLEMAS RECORRENTES (issues fechadas, changelog)
7. SÓ ENTÃO IMPLEMENTAR
```

### 13.1 Fontes, em ordem de prioridade

| Prioridade | Fonte | Onde |
|---|---|---|
| 1 | Spec MCP (revisão vigente) | `modelcontextprotocol.io/specification` |
| 1 | Boas práticas de cliente MCP | `modelcontextprotocol.io/docs/develop/clients/client-best-practices` |
| 1 | SDK Python MCP (código-fonte) | `github.com/modelcontextprotocol/python-sdk` |
| 2 | Engenharia Anthropic — tool use avançado | `anthropic.com/engineering/advanced-tool-use` |
| 2 | Engenharia Anthropic — escrever tools para agentes | `anthropic.com/engineering` |
| 2 | Blog oficial MCP — anotações | `blog.modelcontextprotocol.io` |
| 3 | Referência de arquitetura Godot MCP | `github.com/hi-godot/godot-ai` (~43 tools / 120+ ops) |
| 3 | Referência de composição extrema | `github.com/n24q02m/better-godot-mcp` (17 mega-tools) |
| 4 | Docs Godot 4.7 | `docs.godotengine.org` |
| 5 | Artigos e blogs | só se consistentes com as fontes 1–3 |

### 13.2 Palavras-chave por tema

| Tema | Buscar |
|---|---|
| Anotações (spec) | `MCP ToolAnnotations spec readOnlyHint destructiveHint fields` |
| Anotações (SDK) | `modelcontextprotocol python-sdk types.py ToolAnnotations` |
| Descoberta | `MCP progressive discovery search_tools get_tool_details` |
| Contexto | `MCP tool definitions token cost context bloat` |
| Resources | `MCP resources uri template read-only server capabilities` |
| Schema | `MCP inputSchema JSON Schema client compatibility $ref` |
| Rollup / ops | `MCP composite tool op enum dispatch pattern` |

### 13.3 Como validar se uma solução é confiável

Confiável se satisfaz **todos** os quatro:
1. Aparece na spec ou no código do SDK oficial (não só num blog).
2. A versão citada é compatível com a instalada (`mcp==1.28.1` — reconfirmar).
3. Existe exemplo oficial que a usa.
4. Não há issue aberta relatando que quebra.

Falhou em qualquer um → **não implementar**. Registrar a incerteza no relatório da
fatia e escalar.

### 13.4 Regra anti-alucinação

Se a IA não encontrar a informação na documentação oficial, ela escreve
`NÃO ENCONTRADO NA DOCUMENTAÇÃO OFICIAL` e escala. **É proibido** inferir o
comportamento de uma API a partir do nome do campo.

---

## 14. PROTOCOLO OBRIGATÓRIO DE PROVA

Regras fixas do projeto. Uma entrega sem os itens abaixo está **incompleta** e não deve
ser aprovada — por mais convincente que seja o relatório.

| # | Exigência | Formato aceito | Formato **rejeitado** |
|---|---|---|---|
| 1 | Diff real | `git diff --no-color`, texto literal com `@@` | tabela do que mudou, resumo, "alterei X e Y" |
| 2 | Código real | bloco de código colado do arquivo | `Read [...] lines X to Y` ← **frase banida** |
| 3 | Teste real | saída completa e literal do comando | "passou!", "funcionou", "✅" |
| 4 | Alegação de pré-existência | `git blame` ou `git log -p` com saída colada | "isso já estava assim antes" |

**Regra 5 — medição.** Todo número num relatório vem acompanhado do comando que o
produziu e da saída literal. Número com `~` (aproximadamente) ou "a verificar" é
**estimativa**, não medição, e não fecha critério de aceite.

**Regra 6 — sem terminal, sem entrega.** Se a IA não conseguir executar comandos, ela
**para e reporta**. É proibido substituir execução por análise estática e depois
responder a uma pergunta que exigia saída de comando.

**Regra 7 — regressão.** Toda fatia que toca código de fatia aprovada anteriormente
exige reteste da anterior, com saída colada, antes de aprovar a nova.

**Regra 8 — sem commit antes de aprovação.**

**Regra 9 — reversão silenciosa.** Se a IA desfizer, sem avisar, uma decisão já
aprovada, isso é apontado na hora e revertido ao estado aprovado.

### 14.1 Ambiente Windows/PowerShell

```
❌ comando1 && comando2          # operador incompatível com PowerShell antigo
✅ cmd /c "comando1 && comando2"
✅ comando1 ; comando2

❌ git log                        # output grande sem paginação trava o Cline
✅ git log --oneline -20
✅ git diff --no-color > diff.txt ; type diff.txt

❌ esperar timeout real de rede
✅ mockar a falha
```

Todo subprocess usa `run_subprocess_safe()` de `tools/subprocess_utils.py` com
`stdin=DEVNULL` — obrigatório para evitar deadlock no Windows.

---

## 15. PROTOCOLO OBRIGATÓRIO DE AUDITORIA

Executado ao final de **cada fase**, via `scripts/audit_fase.py`.
**Nenhuma fase fecha com auditoria reprovada.**

| # | Auditoria | Como verificar | Aprovado quando |
|---|---|---|---|
| A01 | Arquitetural | grafo de imports respeita §9 | 0 violações de direção |
| A02 | Qualidade | `ruff check .` | 0 erros |
| A03 | Consistência | INV-01..15 | todas as ativas na fase passam |
| A04 | Nomenclatura | script valida §6.1 | 0 violações |
| A05 | Modularização | todo domínio tem os 6 arquivos do template | 100% |
| A06 | Acoplamento | 0 imports cruzados entre `domains/` | 0 |
| A07 | Duplicação | INV-14 (similaridade < 0.80) | 0 pares |
| A08 | Dependências | `pip check` + nenhuma lib não usada | limpo |
| A09 | Regressão | suíte completa + `smoke_test` | 100% verde |
| A10 | Documentação | contagem de tools bate em todos os `.md` | 0 divergências |
| A11 | Cobertura | cobertura dos handlers migrados | ≥ 70% |
| A12 | Desempenho | tempo de `tools/list` e tokens por fase | ≤ baseline; tokens ≤ 12.000 |

### 15.1 Comando único de auditoria

```
cmd /c ".venv\Scripts\python scripts\audit_fase.py --fase F<N> > audit_F<N>.txt 2>&1"
cmd /c "type audit_F<N>.txt"
```

A saída deve terminar com `AUDITORIA F<N>: APROVADA` ou `REPROVADA: <lista>`.
Colar a saída inteira no relatório da fatia.

---

## 16. PROTOCOLO OBRIGATÓRIO DE TESTES

| Tipo | Quando | O que cobre | Comando |
|---|---|---|---|
| **Unitário** | toda fase | handlers isolados, sem MCP nem Godot | `pytest tests/domains/ -v` |
| **Integração** | F1+ | registry monta `tools/list` correto por fase | `pytest tests/test_registry.py -v` |
| **Invariantes** | toda fase | INV-01..15 | `pytest tests/test_invariants.py -v` |
| **End-to-end** | F3+ | chamada real de rollup contra projeto Godot | `run_scripted_tests` |
| **Regressão** | toda fase | tudo que já foi aprovado | `regression_test` + `smoke_test` |
| **Compatibilidade** | F3+, F5+ | aliases antigos ainda resolvem | `pytest tests/test_aliases.py` |
| **Desempenho** | F5+, F8+ | tokens e latência de `tools/list` | `estimate_tool_tokens` |
| **Estabilidade** | F10 | 50 chamadas seguidas sem vazamento | `run_stress_test` |
| **Falhas** | F2+, F6+ | op inválida, transporte fora do ar, param faltando | `pytest tests/test_failures.py` |
| **Recuperação** | F2+ | rollback de cada fatia restaura o estado | `pytest tests/test_rollback.py` |
| **Casos extremos** | F5+ | schema vazio, `params` ausente, unicode, path com espaço | `pytest tests/test_edge.py` |

### 16.1 Os 8 testes obrigatórios por domínio migrado

```python
def test_manifest_valido():          # manifesto passa em registry.annotations
def test_todas_ops_tem_docstring():  # senão a descrição do rollup degrada
def test_todas_ops_tem_exemplo():    # examples não vazio
def test_dispatch_op_valida():       # op conhecida executa
def test_dispatch_op_invalida():     # op errada devolve sugestão do difflib
def test_params_faltando():          # erro didático, não TypeError cru
def test_handlers_keyword_only():    # inspect.signature confirma o `*`
def test_paridade_com_legado():      # mesmo input → mesmo output do código antigo
```

`test_paridade_com_legado` é o mais importante: é a prova de que a migração não mudou
comportamento. **Se falhar, corrigir o handler — nunca o teste.**

---

## 17. FASES DE IMPLEMENTAÇÃO

Onze fases, **sequenciais**. Cada fase é dividida em fatias de **uma feature cada** —
nunca lotes.

```
F0  MEDIR ──────────► F1  REGISTRY ────► F2  CONFORMIDADE MCP
                                              │
F3  UNIFICAR ROLLUPS ◄────────────────────────┘
     │
     ▼
F4  DESCOBERTA ──► F5  MIGRAR DOMÍNIOS ──► F6  TRANSPORTE
                        (iterativa)             │
                                                ▼
F7  RESOURCES ──► F8  CURADORIA ──► F9  QUARENTENA ──► F10 CONGELAR
```

---

### FASE 0 — MEDIR (PORTÃO DURO)

**Objetivo.** Substituir toda estimativa por número medido.

**Justificativa técnica.** As contagens disponíveis vêm de regex frágeis
(`"[a-z_]+": .*_handle_`) que perdem handlers registrados por lambda, referência direta
ou `dict.update`. A diferença entre ~319 definições e ~216 handlers pode significar
(a) ~100 tools quebradas em produção, ou (b) método de contagem inválido. São conclusões
opostas, e a decisão de todo o roadmap depende de qual é verdadeira.

**Benefícios.** Elimina a possibilidade de refatorar sobre premissa falsa.

**Pré-requisitos.** Terminal funcional.

**Dependências.** Nenhuma.

**Impactos.** Nenhum — fase somente-leitura.

**Escopo.** Nenhum arquivo de produção alterado. Cria `scripts/audit_registro.py`.

**Passo a passo.**

1. Verificar terminal:
   ```
   cmd /c "python --version"
   cmd /c ".venv\Scripts\python --version"
   ```
   Falhou → **PARAR**, colar erro exato, escalar.

2. Criar `scripts/audit_registro.py`. Importa `server`, `tools.rollups` e
   `core.tool_definitions` sem executar o loop MCP. Imprime no formato `CHAVE = VALOR`:
   ```
   defs_total  defs_raw  defs_rollup  handlers_total  handlers_rollup
   manage_em_raw  manage_em_rollup  toolsets_entradas_soma
   toolsets_nomes_unicos  phase_nomes_unicos
   ```

3. Imprimir as **listas completas de nomes** (não contagem):
   ```
   SEM_HANDLER       em tools/list, sem handler
   SEM_DEF           handler sem tool
   DUPLICADOS_NS     nome → [ns1, ns2]
   NS_FANTASMA       em TOOLSETS, inexistente em tools/list
   PHASE_FANTASMA    em PHASE_TOOLSETS, inexistente em tools/list
   SEM_NAMESPACE     tool sem namespace
   SEM_FASE          tool sem fase e fora de PHASE_TOOLS_CORE
   COLISAO_ROLLUP    definida em _raw_tool_defs() E em rollups.py
   ```

4. Imprimir, por fase, o número de tools **distintas** (união com `PHASE_TOOLS_CORE`,
   sem duplicar). *Atenção: as contagens do catálogo somam CORE sobre listas que já
   contêm CORE — IDEIA e DESIGN estão inflados em 18 e 9.*

5. Imprimir `model_dump_json(indent=2)` de `read_file`, `scene_manage` e `godot_exec`
   após todo o pós-processamento.

6. Executar e capturar:
   ```
   cmd /c ".venv\Scripts\python scripts\audit_registro.py > audit_out.txt 2>&1"
   cmd /c "type audit_out.txt"
   ```

7. Verificar código morto, com saída colada de cada:
   ```
   cmd /c "findstr /S /N /C:\"_READONLY\" *.py"
   cmd /c "findstr /S /N /C:\"_DESTRUCTIVE\" *.py"
   cmd /c "findstr /S /N /C:\"_IDEMPOTENT\" *.py"
   cmd /c "findstr /S /N /C:\"_TITLES\" *.py"
   cmd /c "findstr /S /N /C:\"_TAGS\" *.py"
   ```
   Símbolo que aparece só na linha de definição = código morto.

8. Colar literalmente: `tools/rollups.py` inteiro, os blocos completos de `TOOLSETS`,
   `PHASE_TOOLSETS` e `TOOL_PROFILES`, a função `_apply_hints()` inteira, e as 30
   primeiras linhas de `core/tool_definitions.py`.

**Arquivos envolvidos.** Cria `scripts/audit_registro.py`. Lê `server.py`,
`core/tool_definitions.py`, `tools/rollups.py`, `_meta_tool.py`, `tools/phase_ops.py`.

**Critérios de validação.** Todo número tem comando e saída literal. Zero `~`.
Zero "a verificar".

**Critérios de aceite.**
- [ ] `audit_out.txt` completo colado
- [ ] `SEM_HANDLER` listado por extenso (nomes, não contagem)
- [ ] `DUPLICADOS_NS` explica o delta de 19
- [ ] `COLISAO_ROLLUP` verificado (suspeita: `playtest_manage`)
- [ ] Código morto confirmado ou refutado com saída de `findstr`
- [ ] Os 3 JSON colados
- [ ] Contagem real por fase (sem inflação de CORE)

**Possíveis falhas.**
- *Import circular ao importar `server`* → importar `core.tool_definitions` e
  `tools.rollups` diretamente, e chamar `_tool_defs()` via `importlib`.
- *`_tool_defs()` exige projeto ativo* → apontar `config.local.json` para um projeto
  de teste vazio.
- *Filtro de fase distorce a contagem* → medir com `MCP_TOOL_PROFILE=full` e sem
  `.mcp_phase_state.json`.

**Rollback.** Deletar `scripts/audit_registro.py` e `audit_out.txt`. Nada mais mudou.

**Como auditar.** Rodar o script duas vezes; a saída deve ser idêntica (determinismo).

**Critério para iniciar F1.** Todos os aceites marcados **e** decisão humana registrada
sobre a bifurcação abaixo.

> ### BIFURCAÇÃO OBRIGATÓRIA
> `SEM_HANDLER` **vazio ou ≤ 3** → sistema estruturalmente são. Seguir para F1.
> `SEM_HANDLER` **> 3** → F2 vira prioridade absoluta, executada **antes** de F1.
> Corrigir tools quebradas precede reorganizar. Atualizar este documento com o número real.

---

### FASE 1 — REGISTRY: FONTE ÚNICA DE VERDADE

**Objetivo.** Criar `registry/` e fazer `tools/list`, handlers, fases e namespaces serem
**derivados** de manifestos, não mantidos à mão.

**Justificativa.** Existir uma tool (`validate_mcp_registry`) cujo único trabalho é
detectar divergência entre três registros prova que os três registros não deveriam ser
três. Divergência deve ser impossível por construção (P1).

**Benefícios.** Elimina a classe inteira de bug de INV-01, 02, 10, 11, 12, 13.
Domínio novo deixa de exigir edição de arquivo central.

**Pré-requisitos.** F0 aprovada.

**Impactos.** `server.py` encolhe. `core/tool_definitions.py` passa a ser lido pelo
adaptador de legado, não pelo servidor.

**Escopo.** Criar `registry/`. **Nenhum domínio é migrado nesta fase.** O registry
começa lendo o legado através de um adaptador — comportamento externo idêntico.

**Passo a passo.**

1. **Fatia 1.1** — `registry/types.py`: `DomainManifest`, `OpSpec`, `Phase`.
   Só tipos, sem lógica. Testes de construção.
2. **Fatia 1.2** — `registry/legacy_adapter.py`: lê `core/tool_definitions.py`,
   `tools/rollups.py`, `TOOLSETS`, `PHASE_TOOLSETS` e produz `DomainManifest` sintéticos.
   *Prova obrigatória:* `tools/list` antes e depois **byte-idêntico**.
   ```
   cmd /c ".venv\Scripts\python scripts\dump_toollist.py > antes.json"
   REM aplicar a fatia
   cmd /c ".venv\Scripts\python scripts\dump_toollist.py > depois.json"
   cmd /c "fc antes.json depois.json"
   ```
   `fc` deve reportar arquivos idênticos.
3. **Fatia 1.3** — `registry/discovery.py`: agrega manifests (legado + `domains/`,
   ainda vazio).
4. **Fatia 1.4** — `registry/invariants.py` com INV-01, 02, 10, 11, 12.
   *Espera-se que falhem.* Marcar `xfail` com o número medido em F0 e um TODO apontando
   a fase que corrige. Invariante que falha silenciosamente é pior que ausente.
5. **Fatia 1.5** — `server.py` passa a chamar `registry.build_tool_defs()` e
   `registry.build_handlers()`. Deletar a construção antiga.
   *Prova:* `fc` idêntico + `smoke_test` verde.
6. **Fatia 1.6** — `scripts/gen_catalog.py` gera o catálogo **a partir do registry**.
   Substitui o gerador antigo, que produziu 7 números divergentes.

**Arquivos envolvidos.** Cria `registry/*` e `scripts/dump_toollist.py`.
Altera `server.py`. Não altera `core/tool_definitions.py`, `tools/rollups.py`,
`_meta_tool.py`.

**Ordem correta.** 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6. Estrita.

**Critérios de aceite.**
- [ ] `registry/` existe com os módulos de §7
- [ ] `server.py` não contém `Tool(`, `TOOLSETS`, `PHASE_TOOLSETS`, `TOOL_PROFILES`
- [ ] `tools/list` idêntico ao de F0 nas 6 fases (`fc` colado)
- [ ] INV-01, 02, 10, 11, 12 implementadas (mesmo falhando, com `xfail` numerado)
- [ ] Catálogo gerado bate com `audit_out.txt`

**Possíveis falhas.**
- *Import circular `registry` ↔ `server`* → `registry` **nunca** importa `server`;
  o registro do invalidador de cache continua por callback (padrão já funcional).
- *Ordem das tools muda e quebra o `fc`* → ordenar deterministicamente por nome em
  `build_tool_defs()`. Ordem estável também protege prompt caching.

**Rollback.** `git revert` da fatia. Cada fatia é um commit isolado.

**Recuperação.** Se `fc` divergir e a causa não for identificada em 30 min: reverter,
reduzir o escopo da fatia pela metade, repetir.

**Como auditar.** `audit_fase.py --fase F1` (A01, A02, A03 parcial, A09, A10).

---

### FASE 2 — CONFORMIDADE MCP E LIMPEZA

**Objetivo.** Anotações conformes à spec, código morto removido, tools sem handler
corrigidas.

**Justificativa.** `_apply_hints()` injeta `audience`, `priority` e `lastModified`
(campos de `ResourceAnnotations`, não de tool) e `intrusiveHint` (SEP proposta, não
aceita) dentro de `ToolAnnotations`; e grava um `dict` cru onde o modelo espera
`ToolAnnotations`, sem validação (`validate_assignment=False` é o default do pydantic v2).
Além disso, `_HINT_RULES` **infere** hints por prefixo do nome — sobre uma nomenclatura
comprovadamente inconsistente. Anotação errada é pior que ausente: o cliente confia nela
para decidir se pede confirmação (D-09).

**Benefícios.** Confirmações do Cline calibradas. Imunidade a upgrade de SDK.
INV-01, 02, 08, 09, 15 passam.

**Pré-requisitos.** F1 aprovada — ou F0, se a bifurcação disparar.

**Impactos.** O comportamento de confirmação no cliente **muda**. É o objetivo. Documentar.

**Passo a passo.**

1. **Fatia 2.1** — Pesquisa obrigatória (§13). Confirmar no SDK instalado quais campos
   `ToolAnnotations` aceita:
   ```
   cmd /c ".venv\Scripts\python -c \"from mcp.types import ToolAnnotations; print(ToolAnnotations.model_fields.keys()); print(ToolAnnotations.model_config)\""
   ```
   Colar a saída. **Ela decide o resto da fase.**
2. **Fatia 2.2** — `registry/annotations.py`: valida e constrói `ToolAnnotations` real.
   Rejeita campo fora da spec com erro claro.
3. **Fatia 2.3** — Corrigir `_meta_tool.py`: hints **dentro** de `annotations` via
   `ToolAnnotations`, nunca `setattr` no topo do `Tool`; `tags` **não** sobrescrevem
   `annotations`. Se `ToolAnnotations` não aceitar `tags`, mover tags para fora das
   annotations (campo do manifesto, usado só por `catalog_search`) — **não inventar
   campo fora da spec**.
4. **Fatia 2.4** — Remover `_apply_hints()`. Anotações passam a vir do manifesto.
   Para o legado ainda não migrado, o `legacy_adapter` traduz `_HINT_RULES` **uma única
   vez** para valores explícitos, gerando `registry/legacy_annotations.py` como **dados**,
   não como heurística em runtime.
   *Este arquivo é revisado manualmente.* Atenção especial a:
   `godot_exec`, `execute_gdscript_runtime`, `game_http_request` → `openWorldHint=true`;
   `deploy_itch` → `destructiveHint=true` e `openWorldHint=true`;
   `write_file`, `safe_write_gdscript` → `destructiveHint=true`.
5. **Fatia 2.5** — Deletar o código morto confirmado em F0
   (`_READONLY`, `_DESTRUCTIVE`, `_IDEMPOTENT`, `_TITLES`, `_TAGS`).
   *Prova obrigatória:* `findstr` mostrando 0 ocorrências após a remoção.
6. **Fatia 2.6** — Corrigir `SEM_HANDLER` e `SEM_DEF` medidos em F0.
   Para cada nome: registrar handler, ou remover a definição. Decisão caso a caso,
   justificada, uma linha por tool.
7. **Fatia 2.7** — Preencher `rollback` no manifesto de toda op com
   `destructiveHint=true` (INV-15).

**Arquivos envolvidos.** `_meta_tool.py`, `server.py`, `registry/annotations.py`,
`registry/legacy_annotations.py` (novo), `core/tool_definitions.py`.

**Critérios de validação.**
```
cmd /c ".venv\Scripts\python -c \"import json;from server import _tool_defs;[print(t.name, json.dumps(t.model_dump().get('annotations'))) for t in _tool_defs()]\" > ann.txt"
cmd /c "type ann.txt"
```
Nenhuma linha pode conter `audience`, `priority`, `lastModified` ou `intrusiveHint`.

**Critérios de aceite.**
- [ ] Saída de `ToolAnnotations.model_fields` colada
- [ ] 100% das tools com os 4 hints dentro de `annotations`
- [ ] 0 campos fora da spec
- [ ] `SEM_HANDLER` = 0 e `SEM_DEF` = 0, medidos
- [ ] `findstr` prova 0 ocorrências dos 5 símbolos mortos
- [ ] INV-01, 02, 08, 09, 15 passam
- [ ] `regression_test` + `smoke_test` verdes

**Possíveis falhas.**
- *`ToolAnnotations` com `extra="forbid"` rejeita `tags`* → tags saem das annotations.
  Esse é o comportamento correto. **Não contornar com `setattr`.**
- *Cliente passa a pedir confirmação onde não pedia* → comportamento correto.
  Reavaliar o valor do hint, não desligar o hint.
- *Remover `_apply_hints()` derruba tools sem anotação* → `registry/annotations.py`
  aplica os defaults da spec (`readOnly=false`, `destructive=true`, `idempotent=false`,
  `openWorld=true`) e **loga** quem usou default, para revisão manual.

**Rollback.** `git revert` por fatia. 2.4 e 2.5 são as mais arriscadas — commits
separados, obrigatoriamente.

**Como auditar.** `audit_fase.py --fase F2` (A03, A09, A12), mais revisão humana do
diff de `legacy_annotations.py`.

---

### FASE 3 — UNIFICAR OS TRÊS CAMINHOS DE ROLLUP

**Objetivo.** Um único caminho de criação de rollup.

**Justificativa.** Hoje existem três: `_meta_tool.create_manage_tool`,
`tools/rollups.py` (32 builders) e 13 `_manage` escritos à mão em
`core/tool_definitions.py`. Os 13 manuais são **exatamente** os que ficaram órfãos de
namespace e de fase — nasceram fora do caminho oficial e por isso ninguém os
classificou. Múltiplos caminhos garantem que o problema se repita.

**Benefícios.** INV-13 passa. Órfãos deixam de ser produzíveis.

**Pré-requisitos.** F2 aprovada.

**Escopo.** Os 13 `_manage` manuais: `budget_manage`, `mcp_telemetry_manage`,
`playtest_manage`, `fun_report_manage`, `complexity_gate_manage`, `teacher_manage`,
`scope_manage`, `reviewer_manage`, `polish_manage`, `quickstart_manage`,
`version_history_manage`, `publish_manage`, `community_manage`.

**Passo a passo.**

1. **Fatia 3.1** — Para cada um dos 13, provar uso real:
   ```
   cmd /c "findstr /S /N /C:\"budget_manage\" *.py *.md"
   ```
   Classificar em três baldes, com a saída colada como justificativa:
   - **A) Usado** → migrar para `create_manage_tool`, atribuir namespace e fase
   - **B) Não usado, capacidade útil** → `experimental/`
   - **C) Não usado, sem capacidade** → deletar
2. **Fatia 3.2** — Resolver `COLISAO_ROLLUP` de F0 (suspeita: `playtest_manage`
   definido duas vezes). Uma definição sobrevive; a outra é removida.
   *Prova:* INV-13 passa.
3. **Fatia 3.3** — Migrar o balde A. Um por commit.
4. **Fatia 3.4** — Mover o balde B para `experimental/` com `internal=True`.
5. **Fatia 3.5** — Deletar o balde C, com `git log -p` provando ausência de uso.
6. **Fatia 3.6** — Converter `tools/rollups.py` para consumir manifestos em vez de
   builders imperativos. Os 32 builders viram 32 manifestos mínimos.
   **Ainda sem migrar handlers** — só a declaração.

**Critérios de aceite.**
- [ ] `findstr /S "_manage" core/tool_definitions.py` → 0 resultados
- [ ] `COLISAO_ROLLUP` = 0
- [ ] INV-13 passa
- [ ] Contagem de tools no wire **cai**, com número antes/depois medido
- [ ] `tools/list` de cada fase difere do de F2 **apenas** pelas tools removidas

**Possíveis falhas.**
- *Uma das 13 é chamada por `.clinerules/workflows/act.md`* → balde A obrigatório, com
  alias (§11.9).
- *Deletar quebra import em cascata* → o `findstr` da fatia 3.1 previne. Se ocorrer,
  reverter e reclassificar.

**Rollback.** Um commit por tool. Reverter individualmente.

---

### FASE 4 — ATIVAR A DESCOBERTA PROGRESSIVA

**Objetivo.** Tornar visível, em toda fase, o trio
`catalog_search` / `describe_tool` / `invoke_by_name`.

**Justificativa.** Estas três tools **já existem** e implementam exatamente o padrão de
três camadas da documentação oficial MCP (Catálogo → Inspeção → Execução). Estão
marcadas `fase=ORFA` — invisíveis em todas as fases. O padrão recomendado pela spec
está implementado e desligado. Enquanto isso, `tool_catalog` e `tool_groups`, versões
mais fracas, ocupam o CORE.

Esta é a fatia de **maior razão retorno/esforço do roadmap inteiro**: uma linha de
configuração que habilita todas as fases seguintes de redução de superfície.

**Benefícios.** Reduzir a superfície deixa de significar perder acesso. É o
pré-requisito de F5.

**Pré-requisitos.** F3 aprovada.

**Passo a passo.**

1. **Fatia 4.1** — Promover os 3 para sempre-visíveis. Medir tokens antes/depois.
2. **Fatia 4.2** — Fundir `tool_catalog` e `tool_groups` dentro de `catalog_search`
   como ops (`search`, `list_domains`, `activate_group`). Aliases por uma fase.
3. **Fatia 4.3** — `catalog_search` passa a indexar **ops**, não só tools.
   Buscar "criar cena" deve devolver `{tool: "scene_manage", op: "create"}`.
   Reaproveitar o scoring já existente (nome +3, ops +2, descrição +1, bônus rollup +1)
   e `QUERY_ALIASES_ACCENT_ONLY` (a solução do falso positivo `"no"→"node"`).
4. **Fatia 4.4** — `describe_tool` aceita `{tool, op}` e devolve schema + examples da op.
5. **Fatia 4.5** — Guia no system prompt / `.clinerules`:
   *"Você vê ~22 tools. Existem ~300 operações. Use `catalog_search` para achar o que
   não está visível."*

**Critérios de aceite.**
- [ ] Trio visível nas 6 fases (medido)
- [ ] `catalog_search("criar cena")` devolve `scene_manage/create` em #1 — saída colada
- [ ] `catalog_search("erro no script")` **não** devolve `node_manage` (regressão do
      falso positivo já corrigido) — saída colada
- [ ] `catalog_search("adicionar nó")` devolve `node_manage` em #1 — saída colada
- [ ] `describe_tool({tool, op})` devolve schema + exemplo — saída colada
- [ ] Aliases de `tool_catalog`/`tool_groups` funcionam

**Possíveis falhas.**
- *Busca em português degrada ao indexar ops* → reteste obrigatório dos casos conhecidos.
- *`invoke_by_name` burla gates* → confirmar que respeita fase, sessão, kill switch e
  governador. Teste explícito, saída colada.

---

### FASE 5 — MIGRAR DOMÍNIOS (ITERATIVA)

**Objetivo.** Migrar os ~33 domínios para `domains/<x>/` e aplicar
**rollup XOR atômicas** (INV-07).

**Justificativa.** A migração de rollup já aconteceu **pela metade**. `scene`, `script`,
`safety`, `inventory`, `dialogue`, `anim` e `tilemap` colapsaram corretamente — as
atômicas sumiram do wire. Mas `physics`, `ui`, `shader`, `camera`, `navigation` e
`particles` mantêm rollup **e** atômicas simultaneamente: pagando o custo de token
integral e adicionando ambiguidade de seleção. Não é arquitetura errada — é **migração
incompleta**.

**Benefícios.** O2 e O5 atingidos. Redução de ~100 para ~22 na pior fase.

**Pré-requisitos.** F4 aprovada. Sem descoberta progressiva ativa, esconder tools é
perda de acesso.

**Escopo.** Uma fatia = um domínio. Ordem por relação impacto/risco:

| Ordem | Domínio | Atômicas a absorver | Risco |
|---|---|---|---|
| 5.1 | `physics` | 6 | baixo |
| 5.2 | `ui` | 5 | baixo |
| 5.3 | `shader` | 6 | baixo |
| 5.4 | `camera` | 3 | baixo |
| 5.5 | `navigation` | 2 | baixo |
| 5.6 | `vfx` (partículas) | 4 | baixo |
| 5.7 | `screenshot` | 5 (de 3 namespaces) | **médio** |
| 5.8 | `runtime` (sinais) | 8 | **médio** |
| 5.9 | `test` + `verify` | 9 | **médio** |
| 5.10 | `lsp` (`gdscript_*`) | 8 | baixo |
| 5.11 | `debug` (`debugger_*`) | 5 | baixo |
| 5.12 | `scene3d` (`d3_manage`) | 6 | baixo |
| 5.13+ | demais domínios | — | baixo |

**Receita fixa por domínio.**

1. `cp -r domains/_template domains/<x>`
2. Preencher `manifest.py`: nome, descrição (6 blocos), namespace, fases, annotations.
3. Mover funções para `handlers.py`. **Converter para keyword-only (`*`).**
4. Cada op recebe docstring de primeira linha útil (vira o `summary`).
5. Cada op recebe ao menos 1 exemplo realista em `examples.py`.
6. Escrever `tests/` — os 8 testes obrigatórios de §16.1.
7. **Rodar `test_paridade_com_legado`.** Mesmo input → mesmo output do código antigo.
8. Remover as atômicas do wire (INV-07). Adicionar aliases (§11.9).
9. Medir tokens antes/depois: `estimate_tool_tokens`.
10. Rodar `regression_test` + `smoke_test`.

**Critérios de aceite (por domínio).**
- [ ] `domains/<x>/` com os 6 arquivos
- [ ] Todas as ops com docstring e exemplo
- [ ] 8/8 testes obrigatórios passam
- [ ] `test_paridade_com_legado` verde — saída colada
- [ ] INV-07 passa para este domínio
- [ ] Tokens da fase caem — número antes/depois colado
- [ ] Aliases funcionam
- [ ] `regression_test` verde

**Critérios de aceite (fase inteira).**
- [ ] INV-05 (≤ 33 por fase) passa
- [ ] INV-06 (≤ 12.000 tokens por fase) passa
- [ ] INV-07 passa globalmente
- [ ] INV-14 (similaridade < 0.80) passa

**Possíveis falhas.**
- *Op absorvida tinha schema incompatível* → `params` livre absorve; validação e erro
  didático no handler.
- *Agente continua chamando a atômica antiga* → alias resolve e loga. Se o log mostrar
  uso persistente após uma fase, revisar a descrição do rollup: a op não está sendo
  descoberta.
- *Paridade falha* → **NÃO** ajustar o teste. Ajustar o handler. Se o comportamento
  antigo estava errado, isso é uma correção separada, em fatia própria.

**Rollback.** Um commit por domínio. O alias garante que reverter não quebra chamadas.

**Critério de parada (P10).** Quando INV-05 e INV-06 passarem em todas as fases,
**parar**. Migrar domínios restantes vira retorno decrescente — declarar explicitamente
e mover para backlog.

---

### FASE 6 — TRANSPORTE ATRÁS DE ADAPTADOR

**Objetivo.** O modelo nunca escolhe transporte.

**Justificativa.** `addon_create_node` (WebSocket), `node_manage(create)` (arquivo),
`add_nodes_batch` e `batch_atomic_edit` são **quatro maneiras de criar um nó diferindo
só pelo transporte**. O agente não tem informação para escolher — precisaria chamar
`addon_is_available` antes. Sintoma: as 12 tools `addon_*` estão todas na fase
PRONTO_PARA_LANCAR, o que é semanticamente absurdo (manipular nós ao vivo é útil em
PROTOTIPO, não no lançamento). A classificação foi feita por afinidade de **nome**, não
por momento de uso.

**Benefícios.** ~25 tools eliminadas. Elimina a maior fonte de escolha errada de tool.

**Pré-requisitos.** F5 com pelo menos `scene`, `node`, `editor` e `runtime` migrados.

**Passo a passo.**

1. **Fatia 6.1** — `adapters/transport.py` com registro de capacidades:
   ```python
   CAPABILITIES = {
       "scene.write":  ["addon_ws", "headless_cli"],   # ordem = preferência
       "node.create":  ["addon_ws", "headless_cli"],
       "screenshot":   ["addon_ws", "runtime_bridge", "editor_tcp"],
       "runtime.exec": ["runtime_bridge", "game_tcp"],
   }
   def pick(capability: str, prefer: str | None = None) -> Backend: ...
   ```
   `pick()` testa disponibilidade em ordem, com cache curto, e devolve o primeiro vivo.
2. **Fatia 6.2** — `editor_manage` absorve os 12 `addon_*` como ops.
3. **Fatia 6.3** — `runtime_manage` absorve os 13 `game_*` como ops.
4. **Fatia 6.4** — `screenshot_manage` absorve as 5 variantes de screenshot.
5. **Fatia 6.5** — Toda resposta passa a incluir `"backend": "<nome>"`.
6. **Fatia 6.6** — Corrigir as fases: `editor_manage` → PROTOTIPO + CONTEUDO.

**Critérios de aceite.**
- [ ] Nenhum nome começando com `addon_` ou `game_` no wire
- [ ] Toda resposta traz `backend`
- [ ] Teste: addon desligado → operação **funciona** via fallback, saída colada
- [ ] Teste: addon ligado → usa addon e o UndoRedo nativo funciona, saída colada
- [ ] `editor_manage` visível em PROTOTIPO (medido)

**Possíveis falhas.**
- *Fallback silencioso mascara addon caído* → `backend` no retorno + log de warning.
- *`pick()` fica lento testando portas* → cache de 5s por capacidade, invalidado em
  falha de conexão.

---

### FASE 7 — ESTADO READ-ONLY VIRA RESOURCES

**Objetivo.** Mover leitura pura de estado de Tools para MCP Resources.

**Justificativa.** A infra de Resources já existe (6 URIs `godot://`). Estado read-only
em Tools é uso incorreto da spec e custa superfície sem necessidade. Ganho puro.

**Pré-requisitos.** F5 parcial.

**Escopo.** `project_status`, `get_current_phase`, `get_milestone_plan`,
`dump_mcp_state`, `read_console_output`, `get_project_brief`, `project_progress`,
`get_phase_history`, `get_vibe_context`, `security_status`.

**Passo a passo.**
1. Pesquisa obrigatória (§13): capacidades de Resources no SDK instalado e suporte do
   Cline a `resources/list` e `resources/read`.
   **Se o Cline não suportar Resources, PARAR e pular F7** — registrar a decisão.
2. Criar as URIs em `resources/uris.py`.
3. Manter as tools como alias por uma fase (§11.9).
4. Remover as tools do wire.
5. Medir a queda de tokens.

**Critérios de aceite.**
- [ ] Suporte do cliente a Resources **confirmado por teste**, não assumido
- [ ] 10 URIs respondem — saída colada
- [ ] Tools removidas do wire
- [ ] Tokens caem — número medido

**Possíveis falhas.**
- *Cline ignora Resources* → **abortar F7**. Manter como tools. Registrar em
  `LEARNINGS.md`. Não é falha de arquitetura; é limitação de cliente.

---

### FASE 8 — SIMPLIFICAR A CURADORIA

**Objetivo.** De 3 filtros no mesmo eixo para 2 eixos com papéis distintos.

**Justificativa.** `profile`, `toolsets` e `phase` filtram todos a mesma coisa
(visibilidade), compostos por interseção, com **precedência indefinida** — nada no
código diz o que acontece se `--profile lean` (14) e a fase PROTOTIPO (100) discordarem.
Interseção, união e precedência de fase são todas defensáveis, e nenhuma foi escolhida.
Semântica indefinida em ponto crítico é bug latente.

**Pré-requisitos.** F5 completa.

**Passo a passo.**
1. **Fatia 8.1** — Documentar e testar a precedência **atual** antes de mudar
   (evidência do comportamento real).
2. **Fatia 8.2** — `phase` passa a controlar **domínios** (D-05), não tools.
3. **Fatia 8.3** — Reduzir para 2 perfis: `standard` (default) e `full` (debug).
   Aposentar `core`, `dev`, `lean` com aviso de deprecação por uma versão.
4. **Fatia 8.4** — `--toolsets` sai do runtime. Namespace vira só organização de código.
5. **Fatia 8.5** — INV-04: toda tool em ≥1 fase ou `internal=True`. Zerar as 75 órfãs.

**Critérios de aceite.**
- [ ] Precedência documentada e testada
- [ ] 2 perfis
- [ ] `--toolsets` removido, com aviso por uma versão
- [ ] INV-04 passa: 0 tools órfãs de fase
- [ ] Todas as 6 fases ≤ 33 tools

---

### FASE 9 — QUARENTENA DAS VERTICAIS PREMATURAS

**Objetivo.** Isolar as ~43 tools construídas antes da demanda.

**Justificativa.** Telemetria (5), acessibilidade (5), onboarding (3), cutscene (3),
diálogo procedural (4), quest (1), mods (2), trailer/loja (3), achievements (2),
cloud save (1), balance remoto (1) e dificuldade adaptativa (1) são literalmente a
Fase 2/3 do roadmap do projeto, implementadas antecipadamente. Nenhuma foi exercitada
pelo teste que fechou a Fase 1. É a violação materializada do princípio P9 do próprio
projeto: *dogfooding decide prioridade*.

**Passo a passo.**
1. Mover para `experimental/<vertical>/`.
2. `internal=True` no manifesto → fora de toda fase.
3. Acessíveis só via `--profile full`.
4. `experimental/README.md` define o critério de saída: **um jogo real precisou da
   capacidade**. Enquanto isso não acontecer, fica na quarentena.

**Critérios de aceite.**
- [ ] `experimental/` com as verticais
- [ ] 0 delas visíveis em qualquer fase com `--profile standard`
- [ ] Acessíveis com `--profile full` — teste colado
- [ ] Critério de saída escrito

---

### FASE 10 — CONGELAR E DOCUMENTAR

**Objetivo.** Impedir a regressão do problema.

**Justificativa.** O sistema já teve a meta de 33 tools escrita em código e chegou a
287. Sem freio, volta. Além disso, `ARQUITETURA_MCP.md` descreve hoje um sistema que
não existe (10 toolsets inexistentes, cache que "nunca invalida", `core/tool_definitions.py`
ausente do mapa, receita que ensina a adicionar código morto) — e é o documento que a
IA agêntica lê como verdade.

**Passo a passo.**
1. **Fatia 10.1** — CI (GitHub Actions) rodando INV-01..15 em todo push.
   `generate_ci_snippet` já existe — reaproveitar.
2. **Fatia 10.2** — Freio de entrada: tool nova exige `named_justification` no manifesto;
   sem isso, invariante falha.
3. **Fatia 10.3** — Reescrever `ARQUITETURA_MCP.md` a partir **deste** documento e do
   registry real. Nova receita "como adicionar uma tool" = "adicione uma op ao manifesto".
4. **Fatia 10.4** — Números gerados automaticamente. Nenhum `.md` contém contagem
   escrita à mão. `gen_catalog.py` injeta.
5. **Fatia 10.5** — Atualizar `.clinerules/workflows/act.md` e `plan.md`.
   *Nota:* corrigir também o bug conhecido do Passo 8 — o ramo `[SÊNIOR]` não tem o
   encadeamento pós-aprovação que o `[AUTO]` já tem.
6. **Fatia 10.6** — `LEARNINGS.md`: registrar as causas-raiz —
   (a) três caminhos de criação de rollup produziram os órfãos;
   (b) heurística de hint por nome sobre nomenclatura inconsistente;
   (c) documentação divergindo do código virou fonte de erro para a IA agêntica;
   (d) meta arquitetural escrita em docstring, sem invariante, não segura nada.

**Critérios de aceite.**
- [ ] CI falha se qualquer invariante quebrar — provado com PR de teste
- [ ] 0 contagens escritas à mão em `.md`
- [ ] `ARQUITETURA_MCP.md` reescrito e conferido contra o registry
- [ ] `LEARNINGS.md` atualizado
- [ ] `.clinerules` refletindo a nova arquitetura

---

## 18. GUIA DE RESOLUÇÃO DE PROBLEMAS

### 18.1 Tabela de erros comuns

| Sintoma | Causa provável | Diagnóstico | Correção | Confirmação |
|---|---|---|---|---|
| `tools/list` vazio | `registry.discovery` não achou `domains/` | `python -c "from registry.discovery import scan; print(scan())"` | corrigir caminho de varredura | lista não vazia |
| Tool some da fase errada | `MANIFEST.phases` errado | `registry.phases.debug("<tool>")` | corrigir manifesto | tool aparece na fase certa |
| `TypeError: unexpected keyword` | handler não é keyword-only | `inspect.signature(fn)` | adicionar `*` | `test_handlers_keyword_only` passa |
| Op válida devolve "desconhecida" | nome no manifesto ≠ nome chamado | `print(MANIFEST.ops)` | alinhar nomes | dispatch funciona |
| Cliente pede confirmação demais | `destructiveHint` default é `true` | inspecionar `annotations` no JSON | declarar hint explícito | confirmação some |
| Cliente **não** pede confirmação em op destrutiva | hint gravado fora de `annotations` | `model_dump_json` da tool | mover para `ToolAnnotations` | hint dentro de `annotations` |
| `tools/list` muda entre chamadas sem mudar fase | ordenação não determinística | comparar dois dumps com `fc` | ordenar por nome | `fc` idêntico |
| Cache não invalida ao avançar fase | callback não registrado | `findstr "set_cache_invalidator" *.py` | registrar no boot | fase nova reflete |
| Import circular | `domains/` importando `registry/` | ler o traceback | inverter a dependência | import resolve |
| Cline congela em comando git | output grande sem paginação | — | `git log --oneline -20`; redirecionar para arquivo | comando retorna |
| `&&` falha no PowerShell | operador incompatível | — | `cmd /c "a && b"` ou `;` | comando roda |
| Subprocess trava no Windows | stdin não fechado | — | `run_subprocess_safe(stdin=DEVNULL)` | retorna |
| Contagem de tools diverge entre `.md` | número escrito à mão | rodar `gen_catalog.py` | injetar automaticamente | contagens batem |
| INV-14 falha | duas tools fazem a mesma coisa | ler o par reportado | fundir em ops | INV-14 passa |
| `test_paridade_com_legado` falha | migração mudou comportamento | diff dos outputs | corrigir **handler**, nunca o teste | paridade verde |
| Agente ignora o rollup e chama a atômica | descrição do rollup não descreve a op | `catalog_search` pela capacidade | melhorar `summary` da op | busca encontra a op |

### 18.2 Quando parar e escalar

A IA **para e pede decisão humana** quando:

1. Uma invariante falha e a correção exigiria mudar a invariante.
2. `test_paridade_com_legado` falha e o comportamento antigo parece errado.
3. A documentação oficial contradiz este roadmap.
4. Uma fatia exigiria mais de 5 arquivos alterados no mesmo commit.
5. O rollback de uma fatia não restaura o estado anterior.
6. Uma decisão de §12 pareceria precisar ser reaberta.
7. O terminal não está disponível.
8. Um número medido difere em mais de 20% do estimado neste documento.

**Formato da escalação:**
```
ESCALAÇÃO — Fatia <N>
Situação:   <o que aconteceu, com saída colada>
Bloqueio:   <por que não consigo decidir sozinho>
Opções:     A) <opção> — prós/contras
            B) <opção> — prós/contras
Recomendo:  <A ou B> porque <razão técnica>
Reversível: <sim/não; como>
```

---

## 19. CHECKLIST GLOBAL DE QUALIDADE

Validado continuamente, não só ao final da fase.

**Arquitetura**
- [ ] Uma tool declarada em exatamente um lugar
- [ ] Grafo de dependência unidirecional respeitado
- [ ] Nenhum import cruzado entre domínios
- [ ] Domínio novo não exige editar arquivo central

**Legibilidade e simplicidade**
- [ ] `server.py` ≤ 300 linhas
- [ ] Nenhum arquivo de domínio > 500 linhas
- [ ] Nenhuma função > 50 linhas
- [ ] Descrição de tool segue os 6 blocos

**Manutenibilidade**
- [ ] Adicionar uma op = editar 1 arquivo
- [ ] Adicionar um domínio = copiar template + preencher
- [ ] Nenhuma regra existe só em prosa (P6)

**Modularidade e reutilização**
- [ ] Todo domínio tem os 6 arquivos
- [ ] Lógica compartilhada em `registry/` ou `core/`, nunca duplicada
- [ ] Handlers testáveis sem MCP e sem Godot

**Isolamento de responsabilidades**
- [ ] Handlers não conhecem MCP
- [ ] Handlers não escolhem transporte
- [ ] Registry não conhece domínio específico
- [ ] `manifest.py` não contém lógica

**Observabilidade**
- [ ] Toda resposta traz `backend`
- [ ] Uso de alias deprecado é logado
- [ ] Tokens por fase medidos e versionados em `metrics.csv`
- [ ] Tool que usou anotação default aparece no log

**Documentação**
- [ ] Toda op com docstring útil
- [ ] Toda op com ao menos 1 exemplo realista
- [ ] Nenhuma contagem escrita à mão em `.md`
- [ ] `ARQUITETURA_MCP.md` bate com o registry

**Desempenho**
- [ ] `tools/list` ≤ 12.000 tokens por fase
- [ ] `tools/list` ≤ 33 tools por fase
- [ ] Latência de `tools/list` ≤ baseline de F0

**Segurança**
- [ ] `openWorldHint=true` em tudo que acessa rede
- [ ] `destructiveHint=true` em tudo que sobrescreve ou publica
- [ ] Toda op destrutiva tem `rollback` documentado
- [ ] Nenhuma chave de API hardcoded — verificado por script
- [ ] Tools de segurança visíveis desde IDEIA, não só POLIMENTO

**Aderência a boas práticas**
- [ ] Zero campo fora da spec em `annotations`
- [ ] Padrão de 3 camadas de descoberta ativo
- [ ] Fonte oficial consultada antes de cada mudança de protocolo (§13)

---

## 20. GLOSSÁRIO

| Termo | Definição |
|---|---|
| **Wire** | O que aparece em `tools/list`. Custa tokens em toda requisição. |
| **Rollup** | Tool que agrupa N operações sob um parâmetro `op`. Sufixo `_manage`. |
| **Op** | Operação dentro de um rollup. Não aparece no wire. |
| **Atômica** | Tool de operação única. Alvo de absorção por rollup. |
| **Manifesto** | `domains/<x>/manifest.py`. Fonte única de verdade do domínio. |
| **Domínio** | Agrupamento coeso de ≥3 ops que compartilham pré-condições. |
| **Namespace** | Agrupamento organizacional. Após F8, só organização de código. |
| **Fase** | Estado do projeto de jogo (IDEIA→PRONTO). Controla visibilidade. |
| **Perfil** | Modo de deploy. Após F8: `standard` e `full`. |
| **Órfã** | Tool sem fase — invisível por curadoria, mas ainda chamável. |
| **Fatia** | Unidade de trabalho. Uma feature. Um commit. Um rollback. |
| **Invariante** | Regra verificada por script que falha o build. |
| **Paridade** | Migração produz o mesmo output do código antigo para o mesmo input. |
| **Progressive discovery** | Padrão MCP: buscar → inspecionar → executar. |
| **Quarentena** | `experimental/` — capacidade construída antes da demanda. |

---

## APÊNDICE A — ORDEM DE EXECUÇÃO RESUMIDA

```
F0   MEDIR                      ← PORTÃO. Bifurca o roadmap.
F1   REGISTRY                   ← fonte única de verdade
F2   CONFORMIDADE MCP           ← annotations + código morto + handlers órfãos
F3   UNIFICAR ROLLUPS           ← um caminho só
F4   DESCOBERTA                 ← MAIOR RETORNO/ESFORÇO DO ROADMAP
F5   MIGRAR DOMÍNIOS            ← iterativa, um domínio por fatia
F6   TRANSPORTE                 ← ~25 tools eliminadas
F7   RESOURCES                  ← condicional a suporte do cliente
F8   CURADORIA                  ← 3 filtros → 2 eixos
F9   QUARENTENA                 ← verticais prematuras
F10  CONGELAR                   ← CI + docs + freio de entrada
```

**Se houver tempo para apenas três fases:** F0, F4 e F5.
F0 porque nada é confiável sem ela. F4 porque é uma linha de configuração que ativa uma
capacidade já construída e paga. F5 porque é onde a superfície realmente cai.

---

## APÊNDICE B — MÉTRICAS DE ACOMPANHAMENTO

Registrar a cada fase fechada, em `metrics.csv`:

```
fase,data,tools_wire_max,tokens_max,dominios_migrados,inv_passando,sem_handler,duplicados_ns
F0,,,,,0/15,,
F1,,,,,5/15,,
F2,,,,,10/15,,
F3,,,,,11/15,0,
F4,,,,,11/15,0,0
F5,,<=33,<=12000,,14/15,0,0
...
F10,,<=33,<=12000,~33,15/15,0,0
```

---

## APÊNDICE C — CRITÉRIO DE PARADA DO PROJETO

Este roadmap está **completo** — não "quando a lista acabar", mas quando:

1. INV-01..15 passarem; **e**
2. INV-05 (≤ 33 tools) e INV-06 (≤ 12.000 tokens) passarem em todas as fases; **e**
3. a taxa de correção manual do código gerado ficar **abaixo de 15–20%** num jogo
   pequeno construído do início ao fim.

**O critério (3) tem precedência sobre (1) e (2).** Se a taxa de correção já estiver no
alvo, as fases restantes viram retorno decrescente e devem ser **declaradas como tal e
movidas para backlog**, não executadas por completude (P10).

Traduzindo: se o Shardbreaker sair com correção manual abaixo de 20%, o MCP já está bom
o bastante. Continuar reorganizando tools depois disso é otimização estética, e o tempo
rende mais no jogo.

---

*Fim do documento. Versão 1.0 — 2026-07-21.*
*Atualizar ao final de cada fase com os números medidos. O documento é vivo: decisão
tomada durante a execução que não esteja aqui deve ser registrada aqui antes de prosseguir.*
