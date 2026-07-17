# 00 — DOCUMENTO MESTRE — MCP Godot Agent

> **Este arquivo é lido primeiro, em toda tarefa, sem exceção.** Ele define as regras que valem para tudo. Nenhuma fatia pode ser implementada violando o que está aqui.

---

## 0. PARA A IA AGÊNTICA — LEIA ISTO ANTES DE QUALQUER COISA

Você é a IA agêntica (DeepSeek V4 Pro / Flash) rodando dentro do Cline, no VS Code, no repositório `mcp-godot-desenvolvimento`. Seu trabalho é implementar um roadmap de features para um servidor MCP de desenvolvimento de jogos Godot, uma fatia de cada vez, auditando cada fatia no mesmo momento em que a implementa.

Regras absolutas do seu comportamento:

1. **Uma fatia por vez.** Nunca comece a fatia N+1 antes da fatia N estar 100% fechada e aprovada pelos critérios objetivos deste documento.
2. **Você NÃO decide sozinha que uma fatia está boa.** "Boa" é definido por testes que passam ou falham, nunca pela sua opinião. Se um critério não pode virar um teste automático de passa/falha, ele não é auto-avaliável — você escala para o humano.
3. **Você para e escala quando os guardrails mandarem** (seção 4). Parar e reportar é sucesso, não fracasso. Insistir num loop é fracasso.
4. **Você nunca faz operação destrutiva sem checkpoint antes** (seção 3).
5. **Prova sempre, nunca alegação.** "Funcionou", "está certo", "é bug pré-existente" — nada disso vale sem output real colado. Ver seção 5.

Se em qualquer momento você não tiver certeza se pode prosseguir: **pare e escale.** O custo de parar é baixo. O custo de prosseguir errado com confiança é alto — e a pesquisa mostra que modelos do seu tipo erram com confiança justamente quando estão errados.

---

## 1. O QUE É ESTE PROJETO

O MCP Godot Agent é um servidor MCP que atua como "dono do processo" de desenvolvimento de um jogo Godot inteiro — da ideia ao lançamento. Ele não é só uma ponte entre IA e engine: ele é arquiteto, engenheiro e guia do processo, com travas reais (gates de fase, verificação, export) que impedem pular etapas.

Estado atual: ~212 tools, Godot 4.7, com máquina de estados de fase (IDEIA → DESIGN → PROTOTIPO → CONTEUDO → POLIMENTO → PRONTO_PARA_LANCAR), gate de verificação, export gate, session gate, Saga Engine, Circuit Breaker, DAP debugger, LSP bridge, Runtime Bridge (porta 8790), Addon Bridge (WebSocket 9082). A Fase 1 (núcleo do processo) está completa e validada.

Este roadmap adiciona features novas **sem quebrar o que já funciona e sem inchar o MCP a ponto de degradar a escolha de tool**. Essas duas restrições são a espinha dorsal de tudo aqui.

O "projeto" que você edita é o **próprio MCP** (`server.py`, `tools/*.py`), não um jogo. A raiz é `mcp-godot-desenvolvimento/`.

---

## 2. AS QUATRO REGRAS DE TETO DE FERRAMENTAS (nunca violar)

O problema: cada tool exposta consome tokens de contexto em toda requisição, e a precisão de escolha de tool despenca depois de 30–50 tools disponíveis. O Cline não tem limite artificial de tools, mas tem esse problema de degradação. A fase PROTOTIPO já mostra ~92 tools — quase o dobro da zona segura. Portanto:

**Regra 1 — Rollup-first, é lei.** Toda feature nova entra como **op dentro de um rollup** (`nome_manage` com parâmetro `op`), nunca como tool nova de topo. Exceção só com justificativa explícita registrada na fatia e aprovada em revisão sênior. Exemplo: 9 features de música = 1 tool `music_manage` com 9 ops, não 9 tools.

**Regra 2 — Consolidar o que já estourou, antes de adicionar.** Antes de adicionar features numa fase, se essa fase já passou do teto, consolidar tools existentes em rollups primeiro. (A Camada 0 trata a consolidação de PROTOTIPO.)

**Regra 3 — Gate de orçamento de tools no CI.** Existe um teste que **falha o build** se qualquer fase passar de ~40 tools visíveis ou se o total de tools de topo passar de ~70 (teto secundário; ver seção 2). Toda fatia roda esse gate na autoauditoria (critério 5). Estourar o teto por acidente é impossível — o processo barra.

**Regra 4 — Perfil "lean" + meta-tools é a solução real, não uma válvula opcional.** Um perfil que expõe só CORE + 3 meta-tools (`catalog_search`, `describe_tool`, `invoke_by_name`) e carrega o resto sob demanda. Nesse modo o modelo vê ~5 tools sempre, e o teto por fase quase deixa de importar. **Este perfil é fatia priorizada da Camada 0 (0.15), não reserva** — é a solução definitiva do problema de teto. O teto de contagem abaixo é a rede de segurança para quando NÃO se está em modo lean.

**Teto oficial deste projeto — em camadas (medir a coisa certa, não só contar):**

Contar tools é uma proxy grosseira: duas tools podem custar contextos muito diferentes (uma com schema/descrição enorme pesa como cinco simples). E tool ambígua degrada a escolha mais que tool a mais. Por isso o teto tem três níveis:

- **Teto primário (a métrica correta) — orçamento de tokens de definição.** As definições de tool visíveis não devem passar de **~10–15% da janela de contexto**. Esta é a medida que de fato protege a performance. *Implementação: só passa a valer quando existir a tool que soma os tokens dos schemas — ver nota abaixo. Até lá, vale o teto secundário.*
- **Teto secundário (guarda-costas grosseiro) — contagem.** Máximo **~40 tools visíveis por fase** (CORE + exclusivas). Máximo **~70 tools de topo no total**. 40 tira você da zona de risco (a precisão de escolha cai entre 30 e 50); 50 estaria no topo dela, por isso 40, não 50.
- **Teto de distinguibilidade (o que a pesquisa diz importar mais que o número).** Nenhuma tool/op nova pode ter nome ou descrição que se confunda com uma existente. Tool ambígua multiplica loops de escolha errada. Isto é critério de autoauditoria (ver C6, seção 6).

**Regra de decisão:** se uma fatia faria ultrapassar o teto secundário (contagem) OU falharia o teste de distinguibilidade, ela **não pode** ser tool de topo — vira op de rollup, sem exceção.

**Nota de sequência (evitar refinamento antes da hora):** a medição por tokens (teto primário) só é construída **depois** do perfil lean (0.15) estar de pé — medir o cenário não-lean, que será abandonado, é desperdício. Até lá, o teto secundário de 40/70 governa. Ordem: (1) já vale 40/70 + distinguibilidade; (2) Camada 0 entrega o perfil lean; (3) depois do lean, a medição por tokens vira o teto primário e aposenta a contagem.

---

## 3. REGRAS DE SEGURANÇA (nunca violar)

Baseadas em incidentes reais de 2026 (agentes autônomos apagando produção + backups em segundos; servidores MCP expostos por default de rede errado).

**3.1 — Rede em loopback.** O servidor MCP, o Runtime Bridge (8790) e o Addon Bridge (9082) devem bindar em `127.0.0.1`, **nunca** `0.0.0.0`. Toda fatia que toca em bind de rede verifica isso na autoauditoria. Bind em `0.0.0.0` = falha automática, sem discussão.

**3.2 — Backup fora do raio de explosão.** Checkpoint/backup nunca vive só dentro da pasta do projeto que pode ser apagada/corrompida. A rede de segurança real é **git**: antes de qualquer operação destrutiva, um commit/checkpoint automático. Duas redes independentes: UndoRedo do editor (para mudanças de cena/nó) + git (para tudo).

**3.3 — Commit/checkpoint antes de operação destrutiva, obrigatório.** Operação destrutiva = edição em lote, delete de arquivo/nó, correção automática de erro, qualquer coisa que sobrescreve. Antes: checkpoint. Se a operação quebra algo, rollback. Sem checkpoint prévio, a operação não roda.

**3.4 — Segredos nunca em commit.** Com integrações de API externas (música, arte, 3D, voz), chaves de API são risco. Nenhuma chave em código ou em arquivo versionado. Toda fatia que adiciona integração externa verifica isso (scan de segredo) na autoauditoria.

**3.5 — Nada de auto-aprovar servidor MCP ou rodar comando de shell não solicitado.** Você não altera `.mcp.json`, `settings.json` do Cline, nem adiciona hooks que rodam shell, sem aprovação explícita do humano na fatia.

---

## 4. GOVERNADOR DE AUTONOMIA (o que te impede de virar um loop descontrolado)

Todo loop autônomo sem teto duro não é um sistema, é uma esperança. Estes são os freios. Eles valem em **toda fatia**, o tempo todo.

**4.1 — Teto de iteração por fatia.** Máximo de **8 tentativas** de fazer uma fatia passar em seus critérios. Ao atingir 8 sem passar: **pare, preserve o estado, escale.** Não tente a nona.

**4.2 — Detector de repetição (anti-spiral).** Se você fizer a mesma chamada / a mesma edição com os mesmos argumentos e ela falhar **2 vezes**, **PARE. Não tente uma terceira vez.** Repetir a ação idêntica que já falhou não é estratégia — é o bug. Escale com o log das 2 tentativas.

**4.3 — Detector de não-progresso.** Se **3 passagens seguidas** não fizerem nenhum critério novo passar (nenhuma mudança mensurável no estado), pare e escale. "Continuar pensando" sem progresso mensurável é loop.

**4.4 — Orçamento por fatia.** Cada fatia tem um teto de custo/chamadas. Ao atingir, **hard stop.** Sem negociação, sem "só mais uma". Registre o orçamento consumido no relatório da fatia.

**4.5 — "Pronto" é definido antes de começar.** Antes de tocar em código, escreva os critérios de aceite objetivos da fatia (os testes que vão provar que ficou certo). Você não pode redefinir "pronto" no meio para se encaixar no que você fez. "Pronto" = os testes pré-definidos passam.

**4.6 — Checkpoint humano antes de irreversível.** Commit, push, delete em massa, mudança de arquivo de config do projeto: **espere aprovação humana.** Você prepara e propõe; o humano confirma.

**4.7 — Escalação entrega pacote, não só "parei".** Ao escalar, entregue: (a) o que a fatia deveria fazer, (b) o que você tentou, (c) o output real da falha, (d) sua hipótese da causa, (e) estado atual preservado. Isso faz a retomada ser útil, não um recomeço do zero.

**Escalar vs. repetir — a regra que decide:** só tente de novo se a próxima tentativa tiver **informação nova**. Se você repetiria a mesma coisa, não tente — escale. Repetição idêntica nunca ajuda.

---

## 5. REGRA DE PROVA (como você demonstra que algo é verdade)

Herdada do processo já validado deste projeto. Vale para toda alegação.

- **Diff real:** `git diff --no-color`, texto literal com marcadores `@@`. Nunca resumo ou tabela do que mudou.
- **Código real quando necessário:** trecho colado do arquivo. Nunca "Read lines X to Y" (isso é log de ferramenta, não código) — se aparecer isso, está errado, cole o texto real.
- **Teste com output real:** stdout literal colado. Nunca "passou!" sem o output.
- **Alegação exige prova.** "É bug pré-existente" / "sem relação com essa fatia" / "já estava assim" → só vale com `git blame` ou `git log -p`, output colado. Sem isso, a alegação é tratada como não confirmada e a fatia não fecha.

**Regra de prova enxuta (o normal):** a prova padrão é **programática e curta** — um teste que afirma o comportamento esperado e cola só o resultado (passa/falha + poucas linhas de output), OU o trecho-chave. **Nunca** colar centenas/milhares de linhas por padrão. Colagem literal completa só quando: a mudança é pequena e pontual, ou há disputa sobre uma alegação específica. Prova inteligente, não volume.

---

## 6. O BLOCO-PADRÃO DE AUTOAUDITORIA (o coração do controle de qualidade)

**Toda fatia, sem exceção, só fecha se passar por estes 6 critérios.** Todos são objetivos — passa ou falha, nunca opinião. Se você não consegue reduzir um critério a passa/falha automático, ele vira escalação para revisão sênior.

Por que isto e não "você acha que ficou bom?": a pesquisa acadêmica (Kamoi et al. 2024; Huang et al. 2024) é conclusiva — um modelo que julga o próprio trabalho sem verificação externa frequentemente não corrige seus erros, e às vezes piora. O modelo que gerou o erro carrega o mesmo ponto cego para achá-lo. Por isso a autoauditoria aqui é **por teste determinístico**, nunca por autojulgamento.

### Os 6 critérios (rodar nesta ordem)

**C1 — Contrato (schema não driftou).**
Antes da fatia, capture o snapshot de `tools/list` (hash + JSON dos schemas). Depois da fatia, capture de novo e faça o diff.
- ✅ Passa se: **só** a tool/op nova aparece no diff. Nada mais mudou.
- ❌ Falha se: qualquer outra tool teve schema, descrição ou parâmetro alterado sem intenção. (Mudança de descrição conta como quebra de contrato — ela muda a probabilidade do modelo escolher a tool.)
- Prova: cole o diff do snapshot (curto, poucas linhas).

**C2 — Canary (comportamento certo).**
Antes de rodar, declare 2–3 chamadas conhecidas-boas da tool/op nova, com entrada fixa e saída esperada. Rode. Compare.
- ✅ Passa se: as 2–3 saídas batem com o esperado declarado antes.
- ❌ Falha se: qualquer uma diverge.
- Prova: cole o stdout real das 2–3 chamadas (poucas linhas cada).

**C3 — Regressão (não quebrou o que existia).**
Rode `smoke_test` sobre os rollups/features que a fatia tocou + os vizinhos diretos.
- ✅ Passa se: tudo que passava antes continua passando.
- ❌ Falha se: qualquer coisa que passava agora falha → **rollback automático**, e escale.
- Prova: cole o resumo (N testadas, N passaram, 0 falharam).

**C4 — Segurança / não-intrusão (checklist binária).**
Responda sim/não para a fatia:
- Bind de rede em `127.0.0.1` (se tocou em rede)? 
- Checkpoint/commit antes de operação destrutiva (se destrutiva)?
- Não roubou foco / não mudou aba/seleção ativa do editor (se tocou no editor)?
- Idempotente (rodar 2x = mesmo resultado)?
- Sem segredo em código/commit (se integrou API externa)?
- Passou pelo caminho do rollup, não criou tool de topo sem justificativa?
- Cada **"não"** bloqueia o fechamento.

**C5 — Orçamento (teto de tools).**
Conte as tools de topo agora. (Enquanto a medição por tokens não existir, vale a contagem; depois dela, vale o orçamento de tokens de definição — ver mestre seção 2.)
- ✅ Passa se: fase ≤ 40 visíveis E total ≤ 70. (Depois do teto primário: definições ≤ ~10–15% do contexto.)
- ❌ Falha se: passou de qualquer um.
- Prova: o número real.

**C6 — Distinguibilidade (a tool nova não se confunde com nenhuma existente).**
A pesquisa mostra que tool ambígua degrada a escolha mais que tool a mais — "quando as tools são difusas, os loops se multiplicam".
- Rode `catalog_search` (ou o contract snapshot) com o nome/descrição da tool/op nova e veja se ela colide semanticamente com uma vizinha.
- ✅ Passa se: o nome é único e a descrição deixa claro o limite dela vs. as tools próximas (sem sobreposição de propósito).
- ❌ Falha se: nome/descrição se confunde com tool existente, ou duas tools ficam "intercambiáveis" para o modelo.
- Prova: o resultado da busca mostrando que não há colisão, OU o ajuste de nome/descrição feito para eliminar a colisão.

### Segunda camada — verificação cross-model (Pro ↔ Flash)

A pesquisa mostra que usar um modelo diferente para verificar reduz o viés de auto-preferência (o modelo tende a aprovar o próprio trabalho). Você tem dois modelos. Use-os:

- **Pro implementa** a fatia.
- **Flash verifica**, em **contexto novo** (sessão/tarefa nova, não continuando a conversa do Pro), rodando os 6 critérios contra o resultado do Pro, **sem ver o raciocínio do Pro** — só o resultado e os testes.
- Se Flash reprova onde Pro aprovou: escale. A divergência é sinal, não ruído.

Isto não é cross-model perfeito (mesma família de modelo), mas é muito melhor que a mesma instância se auto-avaliando na mesma janela de contexto, que é onde o viés é mais forte.

### Marcação de cada fatia

Cada fatia no roadmap é marcada:
- **[AUTO]** — autofechável: se os 6 critérios passam (e Flash confirma), a IA fecha sozinha e segue.
- **[SÊNIOR]** — requer revisão sênior humana (o Claude/Opus como crítico, ou o dev): a IA implementa e roda os 6 critérios, mas **não fecha sozinha** — prepara o pacote e escala para revisão antes de seguir.
- **[MARGINAL]** — retorno decrescente / Campo A: a fatia está no roadmap para completude, mas a auditoria recomenda questionar se vale fazer. A IA **não implementa sem confirmação humana explícita** de que essa fatia deve ser feita.

---

## 7. FLUXO DE TRABALHO DE CADA FATIA (o loop que você executa)

Para cada fatia, nesta ordem:

1. **Ler** o documento da camada da fatia + este mestre.
2. **Definir "pronto"**: escrever os critérios de aceite objetivos (os testes que vão provar). (Governador 4.5)
3. **Checkpoint git** do estado atual. (Segurança 3.3)
4. **Snapshot de contrato** antes (C1).
5. **Implementar** a fatia (Pro).
6. **Rodar os 6 critérios de autoauditoria** (seção 6).
7. **Verificação cross-model** (Flash, contexto novo).
8. **Decidir pela marcação:**
   - [AUTO] + tudo passou → atualizar o mestre (marcar fatia como feita), commit proposto ao humano, seguir para a próxima.
   - [SÊNIOR] ou qualquer critério falhou ou Flash divergiu → montar pacote de escalação (Governador 4.7), parar, escalar.
9. **Respeitar os guardrails** (seção 4) o tempo todo: teto de iteração, anti-spiral, não-progresso, orçamento.

Nunca pule etapas. Nunca faça duas fatias "de uma vez" — a pesquisa e o histórico deste projeto provam que batch não funciona aqui.

---

## 8. ROADMAP COMPLETO — TODAS AS FATIAS EM ORDEM DE PRIORIDADE

Legenda: **[AUTO]** autofechável · **[SÊNIOR]** requer revisão sênior · **[MARGINAL]** retorno decrescente, confirmar antes.

Os detalhes de cada fatia (arquivos, ops, critério específico) estão no documento da camada correspondente. A spec de código concreto de cada fatia é gerada sob demanda, uma por vez, no momento de fazê-la — não está pré-escrita, de propósito (código escrito cedo demais envelhece antes do uso).

### FATIA 0.0 — BOOTSTRAP [AUTO]
Ler os documentos colados na raiz, criar a estrutura `.clinerules/`, mover cada documento para lá com o nome/prefixo correto, verificar que o Cline os lê, reportar. (É a primeira coisa a rodar. Detalhe no fim deste documento, seção 10.)

### CAMADA 0 — FUNDAÇÃO E SEGURANÇA (documento `01`)
Vem antes de qualquer feature. Destrava tudo e protege o que existe.
- 0.1 — Inventário nível-op dos rollups **[SÊNIOR]**
- 0.2 — Verificar impacto do MCP spec 2026-07-28 (breaking changes de schema/erro) **[SÊNIOR]**
- 0.3 — Verificar comportamento do Cline (re-fetch em `list_changed`; hooks) **[SÊNIOR]**
- 0.4 — Bind loopback 127.0.0.1 em todos os bridges/servidor **[AUTO]**
- 0.5 — Git como rede de segurança: checkpoint automático antes de operação destrutiva **[SÊNIOR]**
- 0.6 — Gestão de segredo + scan de segredo vazado **[AUTO]**
- 0.7 — Consolidar PROTOTIPO (game_bridge_manage, runtime_manage) para baixar de ~92 para ~50 **[SÊNIOR]**
- 0.8 — Gate de orçamento de tools no CI (falha build se passar do teto) **[AUTO]**
- 0.9 — Cliente HTTP compartilhado para geração externa (rate-limit, retry, timeout, custo) **[SÊNIOR]**
- 0.10 — Migração de schema de estado (`.mcp_*_state.json` versionado) **[AUTO]**
- 0.11 — Contract snapshot + diff automático de `tools/list` no CI **[AUTO]**
- 0.12 — Kill switch por feature (segundo eixo, além de fase) **[AUTO]**
- 0.13 — Regra de idempotência/retry para toda tool que participa de cadeia (Saga) **[SÊNIOR]**
- 0.14 — Governador de autonomia como infra real (teto iteração, anti-spiral, não-progresso, orçamento) **[SÊNIOR]**
- 0.15 — Perfil lean + meta-tools (catalog_search/describe_tool/invoke_by_name) — solução real do teto **[SÊNIOR]**
- 0.16 — Medição de tokens de definição como teto primário (só DEPOIS de 0.15) **[AUTO]**

### CAMADA 1 — EXPERIÊNCIA DO DEV (documento `02`)
Dores que você sente toda sessão. Alta prioridade.
- 1.1 — Dispatch "editor-aberto-primeiro" + heartbeat no Addon Bridge (engine não fecha/reabre) **[SÊNIOR]**
- 1.2 — Screenshot retornado como imagem à IA + captura por viewport interno **[AUTO]**
- 1.3 — `capture_ui_snapshot` (dump de Control + Rect2) **[AUTO]**
- 1.4 — Detecção geométrica determinística de sobreposição indevida de UI **[SÊNIOR]**
- 1.5 — Overlay Set-of-Marks para a IA validar layout visual **[SÊNIOR]**
- 1.6 — Regra de não-intrusão por tool (não roubar foco/seleção/aba) + modo silencioso default **[SÊNIOR]**
- 1.7 — Edição via UndoRedo do editor + debounce de re-import + status passivo no dock **[SÊNIOR]**
- 1.8 — `resume_session` (recuperação de sessão: "você parou aqui, próximo passo é X") **[SÊNIOR]**
- 1.9 — Registro de passo concluído por fatia (durable execution: retomar sem repetir) **[SÊNIOR]**
- 1.10 — Correção automática de erro: captura unificada (parse/runtime/editor → estrutura única) **[SÊNIOR]**
- 1.11 — Correção automática de erro: classificador + diagnóstico de causa raiz **[SÊNIOR]**
- 1.12 — `auto_resolve_errors` (modo seguro/autônomo, checkpoint antes, regressão depois, "corrigido" vs "silenciado") **[SÊNIOR]**
- 1.13 — `scope_guard` (guia de escopo: classifica ideia nova como MVP/pós-MVP/fora) **[SÊNIOR]**
- 1.14 — `project_progress` (termômetro de progresso do milestone) **[AUTO]**
- 1.15 — `get_next_step` evoluído (próximo passo + porquê + o que NÃO fazer + "menor passo possível") **[SÊNIOR]**
- 1.16 — Buffer de escopo em `create_milestone_plan` (folga + corte de escopo ativo) **[SÊNIOR]**

### CAMADA 2 — TESTES (documento `03`)
Intercalada, começa junto da Camada 0. Corrige o risco de 88% de tools não testadas.
- 2.1 — Cobertura Tier-1: testar as tools do fluxo padrão ainda não testadas **[SÊNIOR]**
- 2.2 — Smoke test automatizado sobre o inventário inteiro **[AUTO]**
- 2.3 — `test_coverage_report` (cobertura por tool/handler) **[AUTO]**
- 2.4 — `generate_test_cases_from_gdd` **[SÊNIOR]**
- 2.5 — Regressão visual (comparar screenshot contra baseline) **[SÊNIOR]**
- 2.6 — `perf_regression_track` (usando profile_frame/profile_memory entre commits) **[AUTO]**
- 2.7 — Canary queries por tool crítica (drift de comportamento) **[AUTO]**

### CAMADA 3 — CRIAÇÃO COM FOSSO (documento `04`)
Maior diferencial de produto. Ninguém no mercado tem isso com rigor de processo.
- 3.1 — `music_manage`: gerar música (API barata) **[SÊNIOR]**
- 3.2 — `music_manage`: loop sem emenda (make_seamless_loop) **[SÊNIOR]**
- 3.3 — `music_manage`: colocar no nó + normalizar volume **[SÊNIOR]**
- 3.4 — `music_manage`: disparo por evento de jogo **[SÊNIOR]**
- 3.5 — `validate_asset_game_ready` (escala, colisão, material, rig, orçamento de peso) **[SÊNIOR]**
- 3.6 — Style lock no project_brief (paleta/referência aplicadas a toda geração) **[SÊNIOR]**
- 3.7 — Pipeline de arte travado (gerar→remove_bg→optimize→import→validar→gate) **[SÊNIOR]**
- 3.8 — Preset de import por categoria de asset (pixel/3D/UI) **[SÊNIOR]**
- 3.9 — Asset placement inteligente (personagem→AnimatedSprite2D, ambiente→TileMapLayer, UI→TextureRect) **[SÊNIOR]**
- 3.10 — Áudio de engine: bus/efeitos/espacial em audio_manage (se gap confirmado no inventário 0.1) **[SÊNIOR]**
- 3.11 — SFX em lote por evento de cena **[SÊNIOR]**
- 3.12 — Sprite com esqueleto (animação multi-frame consistente) **[SÊNIOR]**
- 3.13 — `license_audit` como gate automático no import de asset externo **[SÊNIOR]**
- 3.14 — `playtest_manage`: self-play (agente joga sozinho para achar bug) **[SÊNIOR]**
- 3.15 — `playtest_manage`: suíte de regressão a partir de gravação de gameplay **[SÊNIOR]**
- 3.16 — `playtest_manage`: curva de dificuldade a partir de playtest simulado **[SÊNIOR]**

### CAMADA 4 — EXTENSÕES DE PROCESSO (documento `05`)
On-brand, esforço médio.
- 4.1 — Teste de i18n (traduções faltantes, overflow de texto, contraste) **[SÊNIOR]**
- 4.2 — Gatilho de CI da verificação a cada commit/push **[AUTO]**
- 4.3 — `code_quality_manage`: integrar gdtoolkit (gdlint/gdformat/gdradon) como gate no verification_pipeline **[SÊNIOR]**
- 4.4 — `code_quality_manage`: função não usada, bloco duplicado, antipadrão Godot, sinal órfão, ciclo de cena, nomenclatura, refactor, busca semântica **[SÊNIOR]**
- 4.5 — Segurança/supply-chain: scan_addon_vulnerabilities, check_addon_license, consistência de import **[SÊNIOR]**
- 4.6 — `agent_manage`: file lock, fila de tarefa, revisão cruzada, comparar outputs, context pack, onboarding brief **[SÊNIOR]**
- 4.7 — Save schema (generate_save_schema) + migração de save antigo **[SÊNIOR]**
- 4.8 — Dead-end de quest/diálogo (validação de beco sem saída) **[SÊNIOR]**
- 4.9 — Doc automática: changelog, readme, wiki do projeto **[AUTO]**

### CAMADA 5 — GAMEPLAY (documento `06`) — [MARGINAL]
Fase 2 do roadmap original. Questionar cada uma antes de fazer.
- 5.1 — Conquistas + cloud save/Steam Cloud **[MARGINAL]**
- 5.2 — Suporte a mods (manifest, validação de compatibilidade) **[MARGINAL]**
- 5.3 — Sequenciador de cutscene/cinemática com câmera **[MARGINAL]**
- 5.4 — Telemetria com opt-in + replay (gravar/reproduzir) **[MARGINAL]**
- 5.5 — Dificuldade adaptativa + quest/diálogo procedural + balance remoto **[MARGINAL]**
- 5.6 — Acessibilidade (daltônico, legendas, remapeamento) + cert de plataforma **[MARGINAL]**
- 5.7 — Trailer/store capsule + onboarding tutorial **[MARGINAL]**
- 5.8 — Pré-geração de diálogo de NPC (cache, não runtime ao vivo) **[MARGINAL]**

### CAMADA 6 — PROFUNDIDADE DE ENGINE (documento `07`) — [MARGINAL / Campo A]
A auditoria diz: quase tudo aqui dilui o fosso. Não é seu jogo competir em profundidade bruta de engine. Fazer só se houver razão explícita.
- 6.1 — Skeleton IK / bone pose (a única com valor real: liga a auto-rig de arte) **[MARGINAL]**
- 6.2 — 3D depth (CSG, multimesh, procedural mesh, GI, probes, sky, camera attrs) **[MARGINAL]**
- 6.3 — Física (joints, body config, area queries) **[MARGINAL]**
- 6.4 — UI granular (tree, item_list, tabs, menu, range, popup, text) **[MARGINAL]**
- 6.5 — Rede (RPC, websocket, anti-cheat, netcode, lobby) **[MARGINAL]**
- 6.6 — Runtime signals (connect/disconnect/emit em runtime) **[MARGINAL]**
- 6.7 — Render settings (MSAA/FXAA/TAA/scaling) **[MARGINAL]**
- 6.8 — C#/.NET scaffold completo **[MARGINAL]**

### CAMADA 7 — POLIMENTO FINO (documento `08`) — [MARGINAL]
Fase 4 do roadmap original. Adiar.
- 7.1 — Detecção de vazamento de memória em sessão longa **[MARGINAL]**
- 7.2 — Migração de versão de engine **[MARGINAL]**
- 7.3 — Grafo de dependência entre addons **[MARGINAL]**
- 7.4 — Modo somente-leitura no início de projeto novo **[MARGINAL]**
- 7.5 — Trava de branch (bloquear escrita direta na main) **[MARGINAL]**
- 7.6 — Orçamento de tokens/custo em tempo real **[MARGINAL]**
- 7.7 — Simulação de diff antes de edição em lote **[MARGINAL]**
- 7.8 — Paridade de input (teclado/controle/touch) **[MARGINAL]**
- 7.9 — Relator de crash pós-lançamento **[MARGINAL]**
- 7.10 — Conformidade de privacidade para telemetria **[MARGINAL]**
- 7.11 — Definition-of-ready (checklist de entrada da fase de design) **[MARGINAL]**
- 7.12 — Live ops (feature flags, patch notes automático, análise de sentimento, A/B) **[MARGINAL]**
- 7.13 — Build matrix multiplataforma **[MARGINAL]**
- 7.14 — Resolução de conflito de edição multiusuário **[MARGINAL]**

---

## 9. ORDEM DE EXECUÇÃO (resumo)

1. Fatia 0.0 (bootstrap) primeiro, sempre.
2. Camada 0 inteira (fundação + segurança) — **não pule.** Nada de feature antes disso.
3. Camada 2 (testes) começa **intercalada** com a Camada 0 — não deixe testes para depois (erro já cometido neste projeto).
4. Camada 1 (experiência do dev) — resolve dores de toda sessão.
5. Camada 3 (criação com fosso) — maior valor de produto.
6. Camada 4 (extensões de processo).
7. Camadas 5, 6, 7 — só com confirmação humana explícita por fatia (são [MARGINAL]).

Dentro de cada camada, siga a ordem numérica das fatias, salvo instrução em contrário no documento da camada.

---

## 10. FATIA 0.0 — BOOTSTRAP (instruções literais)

Esta é a primeira tarefa. Execute assim:

1. Liste os arquivos `.md` colados na raiz `mcp-godot-desenvolvimento/` cujo nome começa com prefixo numérico (`00-`, `01-`, ... `09-`).
2. Crie a pasta `.clinerules/` na raiz, se não existir.
3. **Verifique o `.gitignore`**: garanta que `.clinerules/` NÃO está sendo ignorado. Se estiver, adicione exceção. (Estes arquivos precisam ser versionados — são a fonte de verdade do processo.)
4. Mova cada documento numerado para dentro de `.clinerules/`, mantendo o nome exato.
5. Verifique que os arquivos estão em `.clinerules/` e legíveis.
6. Faça um commit git: `chore: bootstrap roadmap Memory Bank`.
7. Reporte ao humano: quais arquivos foram movidos, confirmação de que o `.gitignore` está correto, e a mensagem: **"Bootstrap completo. Li o mestre. Próximo passo: Fatia 0.1 (inventário nível-op dos rollups), marcada [SÊNIOR] — vou preparar e escalar para revisão. Confirma?"**
8. **Pare e espere confirmação humana** antes da Fatia 0.1. (A primeira fatia real é [SÊNIOR]; não a feche sozinha.)

Bootstrap é operação de arquivo pura — baixo risco. As fatias de implementação (a partir da 0.1) seguem todos os guardrails e a autoauditoria deste documento.

---

## 11. QUANDO ESCALAR PARA O HUMANO (e para o Claude/Opus como crítico sênior)

Escale — pare e monte o pacote da seção 4.7 — sempre que:
- A fatia é **[SÊNIOR]** (não fecha sozinha).
- Qualquer critério de autoauditoria falhou e você não resolveu em ≤ 8 tentativas / 2 repetições / 3 sem-progresso.
- Flash divergiu do Pro na verificação cross-model.
- Uma alegação de "pré-existente" não tem prova (`git blame`/`git log -p`).
- Você tocou em código de feature já aprovada e a regressão não está 100% verde.
- Qualquer dúvida sobre segurança, teto de tools, ou operação irreversível.
- A fatia é **[MARGINAL]** e não há confirmação humana explícita de fazê-la.

O humano usa o Claude (Opus) como crítico sênior de qualidade nos pontos de escalação. Seu pacote de escalação (4.7) é o que alimenta essa revisão — quanto melhor o pacote, mais útil a revisão.

---

*Fim do documento mestre. Os documentos de camada (`01`–`08`) detalham cada fatia. O `09` traz glossário e referências. A spec de código de cada fatia é gerada sob demanda, uma por vez.*
