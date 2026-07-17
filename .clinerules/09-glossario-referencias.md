# 09 — GLOSSÁRIO E REFERÊNCIAS

> Consulta para a IA e para o dev. Define os termos técnicos usados nos documentos `00`–`08`, para que ninguém dependa da memória da conversa que gerou este roadmap. Se um documento usa um termo, a definição operacional está aqui.

---

## TERMOS DE PROCESSO E AUTOAUDITORIA

**Fatia** — a menor unidade de implementação: um rollup, 2–4 ops, ou uma peça de infra. Implementada e auditada de uma vez, sozinha. Nunca "várias features de uma vez" (batch não funciona neste projeto — comprovado).

**Autoauditoria** — os 6 critérios objetivos (mestre seção 6) que toda fatia passa para fechar. Todos passa/falha por teste, nunca por opinião. Se um critério não vira teste automático, ele escala para revisão sênior.

**Os 6 critérios:**
- **C1 Contrato** — o schema de `tools/list` não mudou além do planejado (diff de snapshot).
- **C2 Canary** — 2–3 chamadas conhecidas-boas da tool nova, com saída esperada declarada antes, batem.
- **C3 Regressão** — o que passava antes continua passando (smoke test).
- **C4 Segurança/não-intrusão** — checklist binária (loopback, checkpoint, sem roubar foco, idempotência, sem segredo, rollup).
- **C5 Orçamento** — teto de tools respeitado (≤40 por fase / ≤70 total; depois: tokens de definição ≤ ~10–15% do contexto).
- **C6 Distinguibilidade** — a tool nova não se confunde com nenhuma existente (nome/descrição).

**Verificação cross-model (Pro↔Flash)** — Pro implementa; Flash verifica em contexto novo, sem ver o raciocínio do Pro, rodando os 6 critérios contra o resultado. Reduz o viés de auto-preferência (o modelo tende a aprovar o próprio trabalho). Divergência = escalar.

**Marcações de fatia:**
- **[AUTO]** — se os 6 critérios passam e Flash confirma, a IA fecha sozinha e segue.
- **[SÊNIOR]** — a IA implementa e audita, mas não fecha sozinha: prepara pacote e escala para revisão (dev / Claude Opus como crítico sênior).
- **[MARGINAL]** — retorno decrescente / Campo A: só implementar com confirmação humana explícita.

**Pacote de escalação** — o que a IA entrega ao escalar: o que a fatia deveria fazer, o que tentou, o output real da falha, a hipótese de causa, o estado preservado. Faz a retomada ser útil (mestre 4.7).

**Regra de prova** — diff real (`git diff --no-color` com `@@`), código real colado (nunca "Read lines X-Y"), teste com output real (nunca "passou!"). Alegação de "pré-existente" exige `git blame`/`git log -p`. Prova enxuta por padrão (asserção + resultado curto), não colagem de centenas de linhas.

---

## TERMOS DE TETO DE FERRAMENTAS

**Rollup** — uma tool `nome_manage` que agrupa várias operações sob um parâmetro `op` (ex.: `audio_manage` com op `create_bus`, `add_effect`...). É como se adiciona capacidade sem adicionar contagem de tools. **Regra 1 do teto: toda feature nova é op de rollup, não tool de topo.**

**Op** — uma operação dentro de um rollup. `audio_manage(op="add_effect", ...)`.

**Tool de topo** — uma tool registrada diretamente em `_tool_defs()`, que conta para o teto. Rollups são tools de topo; suas ops não contam individualmente.

**Teto em camadas:**
- **Primário (tokens)** — as definições de tool visíveis ≤ ~10–15% da janela de contexto. A métrica correta. Só vale depois da fatia 0.16.
- **Secundário (contagem)** — ≤40 tools visíveis por fase, ≤70 de topo total. A precisão de escolha de tool cai entre 30 e 50; 40 dá margem.
- **Distinguibilidade** — tool ambígua degrada a escolha mais que tool a mais; nome/descrição não pode confundir com existente.

**Perfil lean** — modo que expõe só CORE + 3 meta-tools (`catalog_search`, `describe_tool`, `invoke_by_name`), carregando o resto sob demanda. A solução real do teto (o modelo vê ~5 tools). Fatia 0.15.

**Meta-tools:**
- `catalog_search` — busca tool por linguagem natural (base: `tool_catalog` existente).
- `describe_tool` — retorna o schema de uma tool sob demanda.
- `invoke_by_name` — invoca uma tool pelo nome. **Não fura gate de fase/verificação** — respeita as travas.

**PHASE_TOOLSETS** — o mecanismo existente que filtra quais tools são visíveis por fase (`_tool_defs()`). É curadoria de visibilidade, **não** bloqueio de execução (`_build_handlers()` não é filtrado por fase). Uma tool escondida por fase ainda pode ser chamada direto — o bloqueio real de progressão é da máquina de estados de fase (Feature 1).

---

## TERMOS DE SEGURANÇA E CONFIABILIDADE

**Loopback (127.0.0.1)** — bind de rede que só aceita conexão da própria máquina. O oposto de `0.0.0.0` (todas as interfaces), que expõe o servidor na rede. Todos os bridges/servidor bindam loopback (mestre 3.1).

**Raio de explosão (blast radius)** — o conjunto de coisas que uma operação destrutiva pode destruir de uma vez. Backup dentro do raio (mesma pasta/credencial que a produção) é apagado junto quando a produção é apagada. Por isso git (fora do raio) é a rede real (mestre 3.2).

**Checkpoint antes de destrutiva** — commit/checkpoint git automático antes de qualquer operação que sobrescreve/apaga. Permite rollback (mestre 3.3, fatia 0.5).

**Idempotência** — rodar a mesma operação 2x produz o mesmo resultado (sem efeito duplicado/cobrança dupla). Obrigatória para tools em cadeia (Saga), porque cadeias longas com falha intermediária precisam de retry seguro (fatia 0.13).

**Contract snapshot** — um JSON versionado (hash + schemas de `tools/list`) que serve de baseline. Diff automático detecta drift de schema — inclusive mudança só de descrição, que muda a probabilidade do modelo escolher a tool. Base do critério C1. Fatia 0.11.

**Canary query** — 2–3 chamadas conhecidas-boas de uma tool, com saída esperada, rodadas periodicamente. Pega drift de **comportamento** (a tool tem o mesmo schema mas passou a retornar coisa diferente). Base do critério C2. Fatia 2.7.

**Schema drift / mismatch** — quando o schema de uma tool muda e quebra quem dependia dele. 38% das falhas de MCP em produção. Pego pelo contract snapshot.

**Compounding de falha** — 5 chamadas em cadeia a 71% de sucesso cada = 18% de sucesso ponta a ponta. Por isso tools em cadeia precisam de idempotência + retry.

---

## TERMOS DO GOVERNADOR DE AUTONOMIA

**Governador de Autonomia** — o conjunto de freios que impede a IA de virar loop descontrolado (mestre seção 4, fatia 0.14). Sem ele, "cola e deixa rodar" é imprudente.

**Teto de iteração** — máximo de 8 tentativas por fatia. Ao atingir: para, preserva estado, escala.

**Anti-spiral (detector de repetição)** — se a mesma chamada com os mesmos argumentos falha 2x, para. Repetir a ação idêntica que já falhou não é estratégia, é o bug. "Tentar com mais força até a falência" é o padrão de runaway.

**Detector de não-progresso** — 3 passagens seguidas sem nenhum critério novo passar = para. "Continuar pensando" sem progresso mensurável é loop.

**Orçamento por fatia** — teto de custo/chamadas por fatia. Hard stop, sem negociação.

**Escalar vs. repetir** — só tente de novo se a próxima tentativa tiver informação nova. Se repetiria a mesma coisa, escale.

**Durable execution** — o estado do trabalho não vive só no processo; passos concluídos têm resultado gravado, e a retomada pega no primeiro passo não-concluído, sem refazer o que passou. Fatias 1.8, 1.9.

---

## TERMOS DE EXPERIÊNCIA DO DEV

**Modo híbrido** — tools falam com o editor Godot vivo (via Addon Bridge) quando ele está aberto, e caem para ler/escrever arquivos quando fechado. Evita abrir/fechar o processo do Godot a cada operação. Fatia 1.1.

**Heartbeat** — ping/pong bidirecional que mantém o WebSocket vivo. Sem ele, a conexão morre e o servidor "resolve" reabrindo o processo (a engine "piscando").

**Dispatch editor-aberto-primeiro** — política: se o editor está aberto, a operação vai pela conexão viva (aplica na cena sem reiniciar); só cai para headless quando fechado.

**Set-of-Marks (SoM)** — técnica de agente visual: desenhar caixas numeradas sobre cada elemento de UI antes de mandar o screenshot para a IA. A IA raciocina sobre "elemento 3 cobre elemento 7" em vez de adivinhar coordenadas. Correção documentada para erro de raciocínio espacial. Fatia 1.5.

**Detecção geométrica de sobreposição** — achar, por interseção de retângulos (Rect2), quais elementos de UI se cobrem indevidamente. Determinístico, não depende da IA — pega o bug antes de a IA olhar. Fatia 1.4.

**Não-intrusão / focus stealing** — focus stealing é uma janela pulando na frente e roubando o teclado (erro de design clássico). Não-intrusão é o oposto: a IA trabalha invisível, sem roubar foco/aba/seleção, salvo quando a operação exige. Fatia 1.6.

**Captura por viewport interno** — `get_viewport().get_texture().get_image()` — captura o que o jogo renderiza por dentro, sem tocar na tela do dev, sem trazer janela para frente. O oposto de printscreen do SO (que exige janela em foco).

**Scope creep** — adicionar features continuamente até o projeto inchar além da conclusão. Causa nº1 nomeada de abandono de projeto solo. Combatido pelo `scope_guard` (1.13) e pelo buffer de escopo (1.16).

**Greybox / arte-confirmatória / arte final** — os três momentos da arte: placeholder desde o dia 1 (formas), arte-confirmatória cedo (rápida, valida se a direção visual funciona, não final), arte final só depois da mecânica travada. Fatias da Camada 3.

**Patch-and-rerun** — o laço de correção de erro: ler o erro real, aplicar patch, re-rodar, confirmar que o erro específico sumiu. Fatias 1.10–1.12.

---

## TERMOS DE CRIAÇÃO (ARTE E ÁUDIO)

**Style lock / contrato de estilo** — paleta + referência + nível de detalhe + estilo fixados no brief, injetados automaticamente em toda geração. Resolve ~80% do problema de "cara de colagem". Fatia 3.6.

**Game-ready** — um asset pronto para o jogo: escala correta, colisão, material sob a luz da engine, polycount no orçamento, rig se personagem. "Um asset gerado não é um asset de jogo" até passar nisso. Fatia 3.5.

**Loop sem emenda (seamless loop)** — faixa de música processada (ponto de loop + crossfade) para tocar em repetição sem emenda audível. "Uma faixa gerada não é música de jogo" até loopar + volume certo + tocar no evento. Fatia 3.2.

**Pipeline travado** — orquestração encadeada com gate: gerar → processar → importar → validar → só então liberar. Se a validação falha, trava. Fatias 3.7 (arte).

**gdtoolkit** — ferramenta Python padrão para GDScript: `gdlint` (análise estática), `gdformat` (formatação), `gdradon` (complexidade). Detecta god_class, função longa, nomenclatura, etc. Integrada como **gate** no verification_pipeline (não relatório avulso). Fatia 4.3. Instalação: `pip install "gdtoolkit==4.*"` (casar major com Godot).

**god_class** — uma classe/autoload que faz coisa demais e acopla tudo. Padrão nº1 de degradação em projeto Godot que cresce rápido com IA gerando código. Detectado pelo gdtoolkit.

---

## CONCORRENTES DE MERCADO (referência da auditoria)

- **tugcantopaloglu/godot-mcp** — 149 tools, MIT, Godot 4.7. Profundidade bruta de engine (áudio bus/efeitos/espacial, 3D, skeleton IK, física, rede, UI granular). Zero processo/gate, zero geração de arte/áudio. É o "Campo A".
- **youichi-uda/godot-mcp-pro** — ~175 tools, proprietário ($15), WebSocket:6505, tempo real com editor.
- **hi-godot/godot-ai** — ~43 tools/120+ ops, grátis, FastMCP + HTTP, install 1-clique.
- **IvanMurzak/Godot-MCP** — 39 tools, C#, cloud.
- **Coding-Solo/godot-mcp** — 20 tools, base fundadora.
- **Summer Engine** — engine-level; gera asset no editor, coloca áudio no nó, autocorrige de erro de runtime.
- **PurpleJelly, mkdevkit, alexmeckes, LuoxuanLove** — MCPs com plugin de editor persistente / modo híbrido (a referência para a fatia 1.1).
- **Onde você está sozinho (Campo C):** o único MCP que é dono do processo do jogo inteiro (fase, gate, GDD, milestone, prova, export travado). Proteger isto é a estratégia.

**Ferramentas de criação (referência):**
- Arte 3D: Meshy (pipeline completo + auto-rig + GLB), Tripo (rápido), Rodin (hero), Hunyuan3D/TRELLIS (open source local), 3D AI Studio (remesh).
- Arte 2D: Scenario (estilo consistente treinado), PixelLab (sprite com esqueleto), SEELE AI, Kenney (packs CC0 consistentes).
- Música: Suno v5 (qualidade), Stable Audio 2.5 (loop royalty-clear), MiniMax Music 2.5 (API ~$0.035/gen), AIVA (MIDI/game scoring), ElevenLabs Music. Existe `mcp-suno` no PyPI.
- Verdade comum a arte e música: o gerador entrega arquivo cru e para; "pronto para jogo" (game-ready / loop+volume+evento) é trabalho de processo+engine = o fosso do seu MCP.

---

## FONTES DA PESQUISA (8 rodadas, 07/2026)

Concorrentes e mercado: godotengine.org/asset-library, github.com/tugcantopaloglu/godot-mcp, github.com/youichi-uda/godot-mcp-pro, github.com/hi-godot/godot-ai, github.com/IvanMurzak/Godot-MCP, github.com/mkdevkit/godot-mcp, purplejelly.itch.io/godot-mcp, summerengine.com.

Arte/áudio: meshy.ai, 3daistudio.com, teamday.ai, chartlex.com, PyPI mcp-suno, github.com/topics/game-audio, kenney.nl, unity.com/blog/placeholder-asset-problem.

Confiabilidade/regressão MCP: digitalapplied.com (100-server stress test; SLO framework), dev.to/nesquikm (schema drift), medium/@binarEx (contract snapshot), blog.modelcontextprotocol.io (spec 2026-07-28).

Organização de código: Scony/godot-gdscript-toolkit (gdtoolkit), godot asset library (gdlint).

Teto de ferramentas: cline discussions #8855, startdebugging.net (tool search), glama.ai (MCP Gateway), demiliani.com.

Autonomia/self-critique: Kamoi et al. TACL 2024, Huang et al. ICLR 2024, arxiv 2606.20093 (self-preference), datasciencedojo.com (loop engineering), nexgismo.com/bmdpat.com (budget guards), cline docs (memory bank).

DeepSeek V4: mindstudio.ai, skywork.ai, techjacksolutions.com (overreliance risk).

Anti-abandono / solo dev: dev.to/jacklehamster, mysterygamedev.substack.com, múltiplos devlogs itch.io, strayspark.studio, gamedevaihub.com.

Visão/UI: arunbaby.com (screenshot understanding / Set-of-Marks), dev.to/getstreamhq (visual agents), godot forums (viewport screenshot), en.wikipedia.org (focus stealing).

Inventário interno: CATALOGO_COMPLETO_MCP_GODOT.md (aprovado 17/07/2026), CONTEXTO_PROJETO_MCP_GODOT.md.

---

*Fim do glossário. Este é o último documento de referência. O prompt de início para o Cline é entregue separadamente.*
