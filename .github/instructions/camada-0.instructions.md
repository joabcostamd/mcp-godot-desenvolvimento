---
applyTo: '**'
---

# 01 — CAMADA 0 — FUNDAÇÃO E SEGURANÇA

> Lê-se junto com `00-mestre.md`. Nada nesta camada é opcional. **Nenhuma feature das camadas 1–7 pode começar antes da Camada 0 estar completa** (exceto a Camada 2 de testes, que roda intercalada). Esta camada destrava a auditoria de tudo e protege o que já funciona.

Formato de cada fatia abaixo: **Objetivo · Por quê · Arquivos prováveis · O que fazer · Critério de aceite específico · Marcação**. A spec de código concreta é gerada sob demanda, no momento de fazer a fatia — aqui está o *o quê* e o *como auditar*, não o código.

> ⚠️ **AVISO SOBRE "ARQUIVOS PROVÁVEIS"** — em todas as camadas deste roadmap, os caminhos de arquivo citados são **palpite**, feitos a partir do catálogo de tools e do documento de contexto, **não de leitura do repositório real**. Trate-os como pista, nunca como fato. Confirme onde as coisas realmente estão antes de editar (é o passo 2 do fluxo, mestre seção 7).
>
> **Consequência esperada e normal:** as 2–3 primeiras fatias provavelmente vão revelar que parte deste plano precisa de ajuste — um rollup que não esconde o que eu supus, um arquivo que não existe, uma tool que já cobre o que eu marquei como buraco. **Isso é o plano funcionando, não falhando.** Ajuste o documento e siga.

Lembrete permanente: rode o fluxo da seção 7 do mestre em toda fatia (definir pronto → checkpoint git → snapshot → implementar → 6 critérios → cross-model → decidir/escalar).

---

## FATIA 0.1 — Inventário nível-op dos rollups **[SÊNIOR]**

**Objetivo:** gerar um inventário completo, nível de op, de todos os ~24 rollups (`audio_manage`, `physics_manage`, `ui_manage`, `scene_manage`, `d3_manage`, etc.), extraído do dispatch real de cada um.

**Por quê:** hoje os rollups são caixa-preta. Não dá para auditar cobertura real, nem confirmar buracos vs. mercado (ex.: se `audio_manage` já tem bus routing ou não), sem saber quais ops cada rollup esconde. Toda comparação de "buraco" nas camadas seguintes depende disto. É pré-requisito de planejamento, não muda comportamento.

**Arquivos prováveis:** varredura de `tools/*.py` (o dispatch/roteamento de op dentro de cada `*_manage`), `server.py` para o mapeamento tool→handler.

**O que fazer:**
1. Para cada rollup, extrair a lista de ops que ele aceita (do dispatch real no código, não do README nem de memória).
2. Para cada op: nome, handler, arquivo, parâmetros de entrada.
3. Gerar `INVENTARIO_OPS_ROLLUPS.md` na raiz: tabela `rollup → op → handler → arquivo → params`.
4. Cabeçalho com contagem de ops por rollup e total de ops.

**Critério de aceite específico:**
- C1 (contrato): nenhuma tool mudou — esta fatia só lê e gera um `.md`, não toca em schema. Snapshot antes/depois idêntico.
- C2 (canary): não aplicável (não cria tool). Em vez disso: prova de que o inventário foi extraído do código real — cole 1 exemplo de op mostrando o trecho do dispatch de onde ela veio (prova de que não é de memória).
- C3 (regressão): `smoke_test` verde (nada foi tocado).
- C4/C5: trivialmente ok (não toca rede, não cria tool).
- **Prova extra exigida:** contagem de ops por rollup + total. Se o total de ops for muito maior que o número de rollups (esperado), confirma que havia capacidade escondida.

**Marcação:** [SÊNIOR] — o inventário precisa de revisão humana/Claude porque as decisões das camadas seguintes se baseiam nele. Escale o `INVENTARIO_OPS_ROLLUPS.md` para revisão antes de seguir.

---

## FATIA 0.2 — Impacto do MCP spec 2026-07-28 **[SÊNIOR]**

**Objetivo:** verificar se o breaking change da especificação MCP de 28/07/2026 afeta este servidor.

**Por quê:** a spec MCP 2026-07-28 mudou `inputSchema`/`outputSchema` para JSON Schema 2020-12 completo (permite `oneOf`/`anyOf`/`$ref`) e mudou um código de erro (`-32002` → `-32602` para params inválidos). Se o servidor ou o SDK usado tem lógica que compara código de erro por valor literal, quebra silenciosamente.

**Arquivos prováveis:** `server.py` (tratamento de erro, definição de schema), o SDK MCP usado (verificar versão), qualquer lugar que compare código de erro literal.

**O que fazer:**
1. Buscar no código toda referência literal a `-32002` (ou comparação de código de erro por número).
2. Verificar a versão do SDK MCP e se ela já suporta / exige a spec nova.
3. Verificar se algum `inputSchema` do projeto depende de comportamento que mudou.
4. Reportar: o que precisa mudar, se algo, e o risco.

**Critério de aceite específico:**
- Prova: cole o resultado da busca por `-32002` (grep real). Se aparecer, cole o trecho e a correção. Se não aparecer, cole o grep vazio como prova de ausência.
- C3 (regressão): se mudou algo no tratamento de erro, `smoke_test` verde + um teste que provoca o erro e confirma o código novo.

**Marcação:** [SÊNIOR] — é diagnóstico de compatibilidade com prazo real; revisar antes de qualquer mudança.

---

## FATIA 0.3 — Comportamento do Cline (list_changed + hooks) **[SÊNIOR]**

**Objetivo:** confirmar dois comportamentos do Cline que afetam o funcionamento do MCP.

**Por quê:**
1. O filtro dinâmico de tools por fase (PHASE_TOOLSETS) só funciona se o cliente **re-lê** a lista de tools quando ela muda (`notifications/tools/list_changed`). Se o Cline cacheia a lista e só lê uma vez na conexão, o filtro de fase não atualiza no meio da sessão — o dev vê lista velha.
2. O hook Stop do EARS (Feature 7) disparava no Claude Code; o Cline tem outro ciclo. O session gate (Feature 10) é server-side e sobrevive; o Stop hook pode não disparar.

**O que fazer:**
1. Testar na prática: mudar de fase no meio de uma sessão Cline e verificar se a lista de tools visível muda sem reiniciar.
2. Verificar se o Cline honra `list_changed`. Se não honrar, documentar o workaround (ex.: instruir reconexão, ou aceitar que a curadoria de fase é por-sessão).
3. Verificar se o hook Stop do EARS dispara no Cline. Se não, documentar que o gate real é o session gate server-side.
4. Reportar as duas respostas com evidência (o que aconteceu no teste real).

**Critério de aceite específico:**
- Prova: descrição do teste real feito + resultado observado (não teoria). Ex.: "mudei IDEIA→DESIGN, a lista no Cline [mudou / não mudou] sem reiniciar."
- Não toca em código do MCP necessariamente — pode ser só diagnóstico. Se exigir workaround em código, C1/C3 se aplicam.

**Marcação:** [SÊNIOR] — decide como o filtro de fase e o EARS funcionam no Cline; revisar.

---

## FATIA 0.4 — Bind loopback 127.0.0.1 **[AUTO]** *(rebalanceado de [SÊNIOR] — portão auditar.py cobre)*

**Objetivo:** garantir que o servidor MCP, o Runtime Bridge (8790) e o Addon Bridge (9082) bindam em `127.0.0.1`, nunca `0.0.0.0`.

**Por quê:** default de rede em `0.0.0.0` expõe o servidor na rede — qualquer um na rede local pode dirigir seu Godot. Foi a causa raiz de CVEs reais de MCP em 2026. Bind loopback é obrigatório (mestre 3.1).

**Arquivos prováveis:** onde os bridges/servidor abrem socket — provavelmente `tools/bridge.py`, `runtime_bridge_client.py`, `tools/addon_bridge.py`, e o bind do servidor em `server.py`.

**O que fazer:**
1. Buscar todo bind de socket / host de servidor.
2. Onde estiver `0.0.0.0` (ou vazio, que às vezes significa todas as interfaces), trocar por `127.0.0.1`.
3. Se algum bind precisar ser configurável (ex.: dev remoto), o default é `127.0.0.1` e a exposição exige flag explícita.

**Critério de aceite específico:**
- C4 (segurança): resposta "sim" para "todos os binds em 127.0.0.1?". Cole o grep real mostrando que não sobrou `0.0.0.0`.
- C2 (canary): os bridges ainda conectam localmente (heartbeat/ping funciona) após a mudança.
- C3 (regressão): `smoke_test` verde.

**Marcação:** [AUTO] — mudança mecânica e verificável; se os 6 critérios passam, fecha sozinha.

---

## FATIA 0.5 — Git como rede de segurança **[SÊNIOR]**

**Objetivo:** checkpoint/commit git automático antes de toda operação destrutiva.

**Por quê:** o backup do `safety_manage` não pode viver só na pasta do projeto (mesmo raio de explosão). A lição de 2026: a camada de recuperação, não a de credencial, é o que salva. Git é a rede independente. Antes de edição em lote, delete, correção automática de erro: checkpoint.

**Arquivos prováveis:** `tools/safety.py`, `tools/orchestrator.py` (onde operações destrutivas passam), o Saga Engine.

**O que fazer:**
1. Identificar as operações destrutivas (edição em lote, delete de arquivo/nó, sobrescrita, correção automática).
2. Antes de cada uma, garantir um checkpoint git automático (commit ou stash nomeado), fora do raio de explosão da operação.
3. Se a operação falha, expor rollback para esse checkpoint.
4. Não substituir o UndoRedo do editor — é uma segunda rede, independente.

**Critério de aceite específico:**
- C2 (canary): rodar uma operação destrutiva de teste e provar que houve checkpoint git antes (cole `git log` mostrando o checkpoint) e que o rollback restaura.
- C4 (segurança): "checkpoint antes de destrutiva?" = sim.
- C3 (regressão): operações não-destrutivas não ganham overhead desnecessário; `smoke_test` verde.

**Marcação:** [SÊNIOR] — toca no caminho de segurança central; revisar.

---

## FATIA 0.6 — Gestão de segredo + scan de vazamento **[AUTO]**

**Objetivo:** garantir que nenhuma chave de API viva em código/commit, e criar um scan que detecta segredo vazado.

**Por quê:** as camadas 3+ integram APIs externas (música, arte, 3D, voz) = muitas chaves. Vazamento em commit é risco real. Isto vira infra antes das integrações, não depois.

**Arquivos prováveis:** onde config/credenciais são lidas (`tools/config_loader.py`?), `.gitignore`, um módulo novo de scan (op em rollup de segurança).

**O que fazer:**
1. Definir o padrão: chaves via variável de ambiente / arquivo não-versionado, nunca em código.
2. Garantir que o arquivo de credenciais está no `.gitignore`.
3. Criar op de scan de segredo vazado (padrões de chave de API conhecidos) — como op de um rollup de segurança existente, não tool nova de topo.
4. Rodar o scan no repo atual e confirmar zero vazamento.

**Critério de aceite específico:**
- C2 (canary): o scan detecta um segredo plantado de teste, e passa limpo no repo real. Cole ambos os outputs.
- C4 (segurança): "sem segredo em código/commit?" = sim, com o scan do repo real como prova.
- C1 (contrato): se virou op de rollup, só essa op aparece no diff de schema.

**Marcação:** [AUTO] — critérios objetivos; fecha sozinha se passar.

---

## FATIA 0.7 — Consolidar PROTOTIPO **[SÊNIOR]**

**Objetivo:** baixar a fase PROTOTIPO de ~92 tools visíveis para ~50, consolidando tools atômicas em rollups.

**Por quê:** PROTOTIPO já passou da zona segura (precisão de escolha de tool cai depois de 30–50). Adicionar features nela sem consolidar antes piora a escolha de tool do Cline. Regra 2 do teto (mestre 2).

**Candidatos a consolidar (confirmar com o inventário da 0.1):**
- Os ~18 `game_*` (freeze_game_clock, step_game_time, game_call_method, game_await_signal, game_raycast, etc.) → um rollup `game_bridge_manage` com ops.
- Os ~11 `godot_*` de runtime (godot_run_project, godot_stop_project, godot_screenshot, godot_exec, etc.) → consolidar em `runtime_manage` (que já existe como rollup) ou um novo.

**O que fazer:**
1. Com base na 0.1, agrupar as tools atômicas de PROTOTIPO em rollups por família.
2. Cada tool vira uma op do rollup. Manter compatibilidade: a chamada antiga deve continuar funcionando OU haver aviso claro (decidir com o humano — mudança de nome de tool é breaking).
3. Recontar PROTOTIPO. Alvo: ≤ 50 visíveis.

**Critério de aceite específico:**
- C1 (contrato): esta fatia MUDA schema de propósito (consolidação). O diff deve mostrar exatamente as tools removidas viram ops. Nada além do planejado.
- C3 (regressão): **crítico** — toda funcionalidade que existia antes precisa continuar acessível via a op nova. Rodar `smoke_test` sobre cada op consolidada. Se algo que funcionava parou, rollback.
- C5 (orçamento): PROTOTIPO ≤ 50. Cole o número antes e depois.
- **Prova extra:** como a compatibilidade foi tratada (as chamadas antigas quebram? há alias? aviso?). Isto é uma decisão que o humano precisa aprovar.

**Marcação:** [SÊNIOR] — é a maior mudança estrutural da camada e mexe em muitas tools existentes. Revisão obrigatória. Consolidação mal feita quebra tudo que usa essas tools.

---

## FATIA 0.8 — Gate de orçamento de tools no CI **[AUTO]**

**Objetivo:** um teste que falha o build se qualquer fase passar de 50 tools visíveis ou o total passar de 75 tools de topo.

**Por quê:** torna o teto (mestre 2) impossível de estourar por acidente. O processo barra, não a memória do dev.

**Arquivos prováveis:** um teste em `tests/` ou script de CI; lê `PHASE_TOOLSETS` e `_tool_defs()`.

**O que fazer:**
1. Escrever um teste que conta tools visíveis por fase e total de topo.
2. Falha se fase > 50 ou total > 75.
3. Rodar no CI (ligar ao pipeline de verificação).

**Critério de aceite específico:**
- C2 (canary): o gate falha quando você planta uma tool a mais que estoura o teto (teste negativo), e passa no estado atual. Cole ambos.
- C3 (regressão): `smoke_test` verde.

**Marcação:** [AUTO] — objetivo e verificável.

---

## FATIA 0.9 — Cliente HTTP compartilhado para geração externa **[SÊNIOR]**

**Objetivo:** uma camada única que toda tool de geração externa (música, arte, 3D, voz) usa para chamar API, com rate-limit, retry, timeout e rastreio de custo.

**Por quê:** em vez de 10 integrações frágeis separadas, uma abstração robusta. Evita que a fragilidade de transporte (o `postMessage` frágil da linha 348) se multiplique por 10. E resolve o dado da pesquisa: 5 chamadas a 71% de sucesso = 18% ponta a ponta — retry e idempotência são obrigatórios em chamada externa.

**Arquivos prováveis:** módulo novo `tools/external_client.py` (não é tool MCP, é infra); usado por art_ops, audio_ops, tts_ops, e futuras.

**O que fazer:**
1. Criar o cliente: rate-limit, retry com backoff, timeout, tratamento de erro que devolve resultado estruturado (não crash).
2. Rastreio de custo por chamada (para o orçamento).
3. Idempotência onde possível (mesma requisição não gera cobrança dupla).
4. As tools de geração existentes (`generate_game_art`, `generate_audio_sfx`, `generate_voice`) passam a usar o cliente.

**Critério de aceite específico:**
- C2 (canary): simular uma falha de API (timeout, 500) e provar que o cliente faz retry e não crasha o servidor. Cole o log.
- C4 (segurança): idempotente? sim, com prova (mesma chamada 2x não duplica efeito/custo).
- C3 (regressão): as tools de geração existentes continuam funcionando via o cliente novo.

**Marcação:** [SÊNIOR] — infra central que muitas fatias futuras dependem; revisar o design antes de as camadas 3 construírem em cima.

---

## FATIA 0.10 — Migração de schema de estado **[AUTO]**

**Objetivo:** versionar o `.mcp_*_state.json` e ter migração para schema antigo.

**Por quê:** cada feature nova mexe no estado por projeto. Sem migração, um projeto criado com MCP antigo quebra ao abrir com MCP novo.

**Arquivos prováveis:** `tools/project_state.py`, onde o estado é lido/escrito.

**O que fazer:**
1. Adicionar campo `schema_version` ao estado.
2. Ao ler um estado, se a versão for antiga, migrar para a nova (preservando dados).
3. Nunca sobrescrever estado antigo sem migrar.

**Critério de aceite específico:**
- C2 (canary): abrir um estado de versão antiga (fixture) e provar que migra sem perder dados. Cole antes/depois.
- C3 (regressão): estado atual continua sendo lido normalmente.

**Marcação:** [AUTO].

---

## FATIA 0.11 — Contract snapshot + diff no CI **[AUTO]**

**Objetivo:** snapshot do `tools/list` (hash + JSON dos schemas) versionado no repo, com diff automático que classifica mudança em breaking/warning/cosmético.

**Por quê:** 38% das falhas de MCP em produção são schema mismatch. Snapshot de contrato pega drift silencioso — inclusive mudança só de descrição (que muda a probabilidade do modelo escolher a tool). É a base do critério C1 da autoauditoria — esta fatia constrói a ferramenta que C1 usa.

**Arquivos prováveis:** script/teste em `tests/`; gera `CONTRACT_SNAPSHOT.json` versionado.

**O que fazer:**
1. Serializar `tools/list` (nomes, descrições, inputSchemas) num snapshot com hash.
2. Diff contra o snapshot anterior, classificando: breaking (tool removida, param obrigatório novo, tipo restringido), warning (mudança que pode afetar comportamento), cosmético.
3. Rodar no CI: falha se houver breaking não intencional.

**Critério de aceite específico:**
- C2 (canary): plantar uma mudança breaking e provar que o diff a detecta e classifica como breaking; plantar cosmética e provar que classifica certo. Cole ambos.
- Este é o ferramental que C1 usa — depois desta fatia, C1 de toda fatia futura roda com isto.

**Marcação:** [AUTO].

---

## FATIA 0.12 — Kill switch por feature **[AUTO]**

**Objetivo:** cada feature nova nasce com uma flag própria (`FEATURE_<nome>_enabled`), independente de fase, que a liga/desliga.

**Por quê:** hoje o filtro é só por fase. Falta um segundo eixo: se uma feature nova quebra algo, desligar **só ela**, sem reverter código nem tirar a fase inteira do ar. A literatura de 2026 trata o kill switch como a peça mais importante do rollout seguro.

**Arquivos prováveis:** `server.py` (registro de tools consulta a flag), um módulo de flags.

**O que fazer:**
1. Sistema de flags de feature (lê de config/estado).
2. `_tool_defs()` e/ou `_build_handlers()` consultam a flag: feature desligada = tool não aparece / não executa.
3. Toda feature nova das camadas seguintes nasce com sua flag.

**Critério de aceite específico:**
- C2 (canary): ligar/desligar uma flag e provar que a tool aparece/some (ou executa/bloqueia) conforme. Cole os dois estados.
- C3 (regressão): features existentes sem flag continuam funcionando (default ligado).

**Marcação:** [AUTO].

---

## FATIA 0.13 — Idempotência/retry para tools em cadeia **[SÊNIOR]**

**Objetivo:** regra de arquitetura + implementação: toda tool que participa de uma cadeia (Saga Engine) é idempotente e tem retry.

**Por quê:** o dado da pesquisa — 5 chamadas a 71% = 18% ponta a ponta. Suas cadeias (create_entity, verification_pipeline, export gate) são longas. Cada tool precisa ser projetada para idempotência e retry, não só para o caminho feliz.

**Arquivos prováveis:** `tools/orchestrator.py`, o Saga Engine, tools que fazem parte de cadeias.

**O que fazer:**
1. Definir a regra: toda tool em cadeia = idempotente (rodar 2x = mesmo resultado) + retry seguro.
2. Auditar as tools de cadeia atuais contra essa regra; corrigir as que não são.
3. Documentar a regra para as fatias futuras (elas herdam isto na autoauditoria C4).

**Critério de aceite específico:**
- C4 (segurança): "idempotente?" = sim, com prova (rodar 2x, mesmo resultado) para cada tool de cadeia tocada.
- C3 (regressão): as cadeias inteiras (Saga) continuam funcionando e agora sobrevivem a uma falha intermediária com retry. Cole um teste de cadeia com falha injetada que se recupera.

**Marcação:** [SÊNIOR] — regra de arquitetura que afeta o Saga central; revisar.

---

## FATIA 0.14 — Governador de autonomia como infra real **[SÊNIOR]**

**Objetivo:** transformar os guardrails da seção 4 do mestre em mecanismo real, não só texto que a IA deve lembrar.

**Por quê:** "cola o documento e deixa rodar" só é seguro se os freios forem reais. Sem eles, sessão roda o fim de semana e você acorda com projeto quebrado ou conta de API estourada (padrão documentado em 2026).

**Arquivos prováveis:** um módulo de governança que envolve o loop de execução das fatias; pode ligar ao Circuit Breaker existente.

**O que fazer:**
1. Teto de iteração por fatia (8) — contador que para e escala.
2. Detector de repetição (2 chamadas idênticas que falham → para).
3. Detector de não-progresso (3 passagens sem critério novo passar → para).
4. Orçamento de custo/chamadas por fatia (hard stop).
5. Registro de estado para o pacote de escalação (4.7).
6. Ligar ao Circuit Breaker que já existe, se fizer sentido.

**Critério de aceite específico:**
- C2 (canary): provar cada freio: forçar 2 falhas idênticas e mostrar que para; forçar 8 iterações e mostrar que escala; estourar orçamento e mostrar hard stop. Cole os logs.
- C4 (segurança): o governador nunca deixa uma operação destrutiva rodar sem checkpoint.

**Marcação:** [SÊNIOR] — é o que torna a autonomia segura; precisa de revisão cuidadosa. Idealmente, esta fatia é feita cedo na Camada 0, porque protege todas as fatias seguintes.

---

## FATIA 0.15 — Perfil lean + meta-tools **[SÊNIOR]**

**Objetivo:** um perfil de execução que expõe só CORE + 3 meta-tools (`catalog_search`, `describe_tool`, `invoke_by_name`) e carrega o resto sob demanda.

**Por quê:** é a **solução real** do problema de teto (mestre 2, Regra 4). No modo lean o modelo vê ~5 tools sempre; ele busca a tool que precisa (`catalog_search`), lê o schema dela (`describe_tool`), e a invoca por nome (`invoke_by_name`). O teto por fase quase deixa de importar — você poderia ter centenas de ops e o contexto ficaria pequeno. O teto de contagem (40/70) é só a rede para quando NÃO se está em lean.

**Arquivos prováveis:** `server.py` (registro de perfil), `tools/dynamic_groups.py` (já tem `tool_catalog` — base do `catalog_search`), um handler novo `invoke_by_name` que despacha para qualquer tool pelo nome.

**O que fazer:**
1. `catalog_search`: busca de tool por linguagem natural (já existe como `tool_catalog` — reusar/expor como meta-tool).
2. `describe_tool`: dado um nome de tool, retorna o schema completo dela sob demanda.
3. `invoke_by_name`: dado nome + argumentos, despacha para o handler real (reusa `_build_handlers()`).
4. Perfil `lean`: quando ativo, `_tool_defs()` expõe só CORE + essas 3 meta-tools.
5. Cuidado de segurança: `invoke_by_name` respeita as travas de fase e os gates — não é um bypass. Uma tool escondida por fase continua bloqueada na execução real; `invoke_by_name` não fura isso.

**Critério de aceite específico:**
- C2 (canary): no modo lean, provar o ciclo completo — buscar uma tool, descrever, invocar, e obter o mesmo resultado de chamá-la direto. Cole os 3 passos.
- C4 (segurança): provar que `invoke_by_name` NÃO fura gate de fase nem gate de verificação (tentar invocar algo bloqueado por fase e mostrar que é barrado igual).
- C5 (orçamento): no modo lean, contar tools visíveis = CORE + 3. Cole o número.
- C3 (regressão): fora do modo lean, tudo continua igual.

**Marcação:** [SÊNIOR] — é arquitetura central e `invoke_by_name` é sensível (não pode virar bypass de gate). Revisão obrigatória.

---

## FATIA 0.16 — Medição de tokens de definição como teto primário **[AUTO]**

**Objetivo:** uma checagem que soma os tokens das definições de tool visíveis e falha se passar de ~10–15% da janela de contexto. Vira o teto primário, aposentando a contagem como métrica principal.

**Por quê:** contar tools é proxy grosseira — o que degrada a performance é o custo em tokens das definições. Esta é a métrica correta. **Só fazer DEPOIS da 0.15**, porque medir o cenário não-lean (que será abandonado) é desperdício; medir o cenário lean real é o que vale.

**Arquivos prováveis:** o teste de orçamento de tools (0.8), estendido para somar tokens em vez de só contar.

**O que fazer:**
1. Somar os tokens das definições de tool visíveis (nome + descrição + inputSchema serializado) por perfil/fase.
2. Comparar contra um teto de fração da janela de contexto (~10–15%).
3. Estender o gate de CI (0.8) para usar esta medição como teto primário; manter a contagem 40/70 como teto secundário/grosseiro.

**Critério de aceite específico:**
- C2 (canary): medir o estado atual e o estado lean; mostrar a diferença de tokens. Plantar tools pesadas e mostrar que o gate dispara pelo custo em tokens, não pela contagem. Cole os números.
- C3 (regressão): o gate de contagem (0.8) continua valendo como segundo limite.

**Marcação:** [AUTO] — objetivo e mensurável. **Dependência dura: só depois da 0.15.**

---

## ORDEM SUGERIDA DENTRO DA CAMADA 0

**Antes de tudo (ver mestre, seções 8 e 9):** Fatia 0.0 (bootstrap) → **0.0.1 (verificação de ambiente, bloqueadora)** → **0.0.5 (`auditar.py`, o portão)** → rebalanceamento das marcações [SÊNIOR]/[AUTO].

Depois disso, dentro da Camada 0:
1. **0.14** (governador) — **primeiro**, porque a 0.1 é uma varredura grande e deve rodar já protegida pelos freios (teto de iteração, anti-spiral, não-progresso).
2. **0.1** (inventário) — destrava o planejamento de todas as camadas seguintes.
3. **0.4, 0.6** (bind loopback, segredo) — segurança rápida, [AUTO].
4. **0.2, 0.3** (spec MCP, Cline) — diagnósticos com prazo.
5. **0.5, 0.13** (git safety, idempotência) — segurança de cadeia.
6. **0.11, 0.12, 0.10, 0.8** (contract snapshot, kill switch, migração, gate de orçamento) — o ferramental de auditoria.
7. **0.15** (perfil lean + meta-tools) — a solução real do teto; priorizado, não deixado para o fim.
8. **0.9** (cliente HTTP) — antes das camadas 3.
9. **0.7** (consolidar PROTOTIPO) — depois do lean e do inventário, porque é a maior e se beneficia de tudo acima.
10. **0.16** (medição por tokens) — por último, porque depende do 0.15 já estar de pé.

**Lembrete:** a Camada 2 (testes) começa intercalada com esta. Não deixe testes para depois.

---

*Fim da Camada 0. Próximo documento: `02-camada-1-experiencia-dev.md`.*
