---
applyTo: '**'
---

# 02 — CAMADA 1 — EXPERIÊNCIA DO DEV

> Lê-se junto com `00-mestre.md`. Estas são as dores que o dev sente **toda sessão** — engine que fecha, IA que não vê o jogo, UI sobreposta, IA roubando foco, erro vermelho do nada, perder o fio ao voltar. Alta prioridade: resolvem atrito recorrente, não features de produto.

Roda depois da Camada 0 (a fundação precisa estar de pé). Formato de cada fatia: **Objetivo · Por quê · Arquivos prováveis · O que fazer · Critério de aceite específico · Marcação**. Spec de código gerada sob demanda.

Lembrete permanente: fluxo da seção 7 do mestre em toda fatia. Guardrails da seção 4 sempre ativos.

---

## BLOCO A — A ENGINE NÃO FECHA E REABRE

### FATIA 1.1 — Dispatch "editor-aberto-primeiro" + heartbeat no Addon Bridge **[SÊNIOR]**

**Objetivo:** parar de abrir/fechar o processo do Godot a cada operação. Quando o editor está aberto, aplicar mudanças ao vivo pela conexão persistente; só cair para o modo headless (abre/fecha processo) quando o editor está fechado.

**Por quê:** hoje o MCP provavelmente opera em modo headless CLI (abre `godot --headless --script` por operação, aplica, fecha) — é isso que faz a engine "piscar". Os MCPs bons de 2026 usam **modo híbrido**: falam com o editor vivo quando aberto, caem para arquivos quando fechado. Você já tem o Addon Bridge (WS 9082) e os 12 `addon_*` — a infra existe. Falta a política de dispatch priorizar o addon vivo, + heartbeat para a conexão não morrer (sem heartbeat, a conexão cai e o servidor "resolve" reabrindo processo — o que você vê).

**Arquivos prováveis:** `tools/addon_bridge.py`, `tools/bridge.py`, o dispatch de `scene_manage`/`node_manage`/`create_entity`, o registro de conexão.

**O que fazer:**
1. Detectar se o Addon Bridge está conectado (editor aberto).
2. Política de dispatch: editor aberto → operação vai pelo addon vivo (aplica na cena sem reiniciar). Editor fechado → cai para headless/arquivo.
3. Heartbeat ping/pong bidirecional para manter o WebSocket vivo.
4. Reconexão com backoff exponencial (1s→60s) em vez de reabrir processo.

**Critério de aceite específico:**
- C2 (canary): com editor aberto, aplicar uma mudança de nó e provar que a cena atualiza **sem** o processo reiniciar (cole evidência de que o PID do Godot não mudou). Com editor fechado, provar que cai para o modo arquivo e funciona.
- C4 (não-intrusão): a operação ao vivo não rouba foco nem muda a aba ativa (ver 1.6).
- C3 (regressão): as tools de cena/nó continuam funcionando nos dois modos.

**Marcação:** [SÊNIOR] — muda o caminho de dispatch central de muitas tools. Revisão obrigatória; consolidação/dispatch mal feito quebra todas as edições de cena.

---

## BLOCO B — A IA VÊ O JOGO DE VERDADE

### FATIA 1.2 — Screenshot retornado como imagem à IA + captura por viewport interno **[AUTO]**

**Objetivo:** garantir que os screenshots (`take_screenshot`, `capture_game_screenshot`, `auto_screenshot`, `godot_screenshot`, `addon_take_screenshot`) **retornam a imagem para o modelo ver**, não só salvam em disco. E que a captura é feita pelo viewport interno, não printscreen do SO.

**Por quê:** a IA já é multimodal — ela lê PNG, incluindo micro-texto e ícones. Mas captura que só salva em disco é captura cega: a IA não vê nada. Além disso, captura por viewport interno (`get_viewport().get_texture().get_image()`) não toca na sua tela, não traz janela para frente, não rouba foco — diferente de printscreen do SO, que exigiria a janela em foco.

**Arquivos prováveis:** as tools de screenshot em `runtime_ops`, `screenshot_ops`, `addon_bridge`.

**O que fazer:**
1. Auditar cada tool de captura: ela retorna a imagem (base64 PNG) no resultado, ou só salva o caminho?
2. Onde só salva, fazer retornar a imagem para o modelo (respeitando limite de tamanho).
3. Garantir que a captura usa viewport interno / SubViewport, não printscreen do SO.

**Critério de aceite específico:**
- C2 (canary): chamar uma tool de captura e provar que o retorno contém a imagem (não só um caminho de arquivo). Cole o tipo do retorno.
- C4 (não-intrusão): a captura não rouba foco nem traz janela para frente. Confirme o método (viewport interno).
- C3 (regressão): as tools de captura continuam salvando em disco onde isso já era esperado.

**Marcação:** [AUTO].

---

### FATIA 1.3 — `capture_ui_snapshot` (dump de Control + Rect2) **[AUTO]**

**Objetivo:** uma op que captura, além do screenshot, o **dump estruturado de todos os nós `Control`** com seus `Rect2` (posição + tamanho), nome, e ordem de desenho.

**Por quê:** é a base da detecção de sobreposição de UI (1.4) e do Set-of-Marks (1.5). Sem os retângulos de cada elemento, não dá para detectar sobreposição de forma determinística nem marcar os elementos para a IA. Hoje `take_screenshot` só captura pixel, sem introspecção de layout.

**Arquivos prováveis:** op nova em `vision_ops` ou `ui_ops` (rollup, não tool de topo); usa o Addon Bridge / Runtime Bridge para ler a árvore de `Control`.

**O que fazer:**
1. Percorrer a árvore, coletar todos os `Control`: nome, caminho, `Rect2` global (posição+tamanho), visível sim/não, ordem de desenho (z/ordem na árvore).
2. Retornar o dump estruturado + o screenshot correspondente.

**Critério de aceite específico:**
- C2 (canary): rodar numa cena com UI conhecida e provar que o dump lista os `Control` certos com Rect2 plausível. Cole o dump.
- C1 (contrato): virou op de rollup — só ela aparece no diff.

**Marcação:** [AUTO].

---

### FATIA 1.4 — Detecção geométrica determinística de sobreposição indevida **[SÊNIOR]**

**Objetivo:** a partir do dump de Rect2 (1.3), detectar por **matemática pura** (interseção de retângulos) quais elementos de UI se sobrepõem quando não deveriam.

**Por quê:** sua dor real — menu/HUD sobreposto errado, cobrindo algo que não devia. A detecção de sobreposição é **determinística, não depende da IA** — você pega o bug antes mesmo de a IA olhar. É exatamente o tipo de trava dura que é a identidade do projeto.

**Arquivos prováveis:** op em `vision_ops`/`ui_ops`; lógica de interseção de Rect2.

**O que fazer:**
1. Definir o que é "sobreposição indevida" (dois elementos interativos/visíveis se cobrindo; ou um elemento cobrindo outro marcado como "não deve ser coberto").
2. Interseção de retângulos entre os `Control` visíveis.
3. Reportar as colisões: quais elementos, quanto de área, qual cobre qual.
4. Opcional: permitir marcar pares que PODEM se sobrepor (ex.: um painel e seu fundo) para não gerar falso positivo.

**Critério de aceite específico:**
- C2 (canary): montar uma cena com uma sobreposição proposital e provar que a detecção a encontra; montar uma sem e provar que passa limpo. Cole ambos.
- C4 (segurança): determinístico (rodar 2x = mesmo resultado).

**Marcação:** [SÊNIOR] — a definição de "indevida" precisa de julgamento (evitar falso positivo com sobreposições legítimas). Revisar.

---

### FATIA 1.5 — Overlay Set-of-Marks para a IA validar layout **[SÊNIOR]**

**Objetivo:** antes de mandar o screenshot para a IA, desenhar **caixas numeradas** em cada elemento de UI. A IA então raciocina sobre "elemento 3 cobre elemento 7" em vez de adivinhar coordenadas.

**Por quê:** a pesquisa de agentes visuais de 2026 nomeia os três modos de falha de "ler tela"; o seu caso (raciocínio espacial) tem correção documentada: **Set-of-Marks**. Marcar os elementos elimina a adivinhação de coordenadas — a IA vê, marcado, o que sobrepõe o quê. Combina com a detecção determinística (1.4): a matemática pega a colisão, o Set-of-Marks deixa a IA validar/entender visualmente.

**Arquivos prováveis:** op em `vision_ops`; desenha overlay sobre a imagem (a partir dos Rect2 de 1.3).

**O que fazer:**
1. A partir do dump (1.3), desenhar caixas numeradas sobre o screenshot.
2. Retornar a imagem marcada + a legenda (número → nome do elemento).
3. Combinar com 1.4: destacar em cor diferente os elementos que a detecção geométrica marcou como sobrepostos.

**Critério de aceite específico:**
- C2 (canary): gerar a imagem marcada de uma cena de UI e provar que os números batem com os elementos certos. Cole a legenda.
- C4 (não-intrusão): a marcação é feita sobre a imagem capturada, não altera a UI real do jogo/editor.

**Marcação:** [SÊNIOR] — parte visual, revisar a utilidade real da marcação.

---

## BLOCO C — A IA NÃO ATRAPALHA O DEV

### FATIA 1.6 — Regra de não-intrusão por tool + modo silencioso default **[SÊNIOR]**

**Objetivo:** nenhuma tool de editor rouba foco, muda a aba/seleção ativa, ou abre cena, a menos que a operação exija de verdade. Operações de leitura/inspeção/captura rodam em silêncio, sem efeito visível para o dev.

**Por quê:** o que você quer é a IA trabalhar **invisível**. Focus stealing (janela pulando na frente, roubando teclado) é reconhecido como erro de design há décadas. Isso é UX pura para você; não tira liberdade da IA — ela continua podendo tudo, só sem te interromper.

**Arquivos prováveis:** transversal — toda tool que toca no editor via Addon Bridge; uma regra/checklist + ajustes nas tools que hoje mexem em seleção/aba.

**O que fazer:**
1. Definir a regra: leitura/inspeção/captura = silenciosas (sem `set_selected`, sem abrir cena, sem trazer janela). Só operações explicitamente pedidas podem tocar na UI ativa.
2. Auditar as tools de editor atuais: quais mudam seleção/aba/foco sem necessidade? Corrigir.
3. Modo silencioso como default para as tools de leitura.
4. Esta regra entra no C4 da autoauditoria de toda fatia futura que toca no editor.

**Critério de aceite específico:**
- C4 (não-intrusão): para cada tool de leitura tocada, "não rouba foco/aba/seleção?" = sim, com prova (rodar e observar que a aba/seleção do editor não mudou).
- C3 (regressão): as tools continuam entregando o resultado, só sem o efeito colateral visual.

**Marcação:** [SÊNIOR] — regra transversal que afeta muitas tools; revisar.

---

### FATIA 1.7 — Edição via UndoRedo + debounce de re-import + status passivo no dock **[SÊNIOR]**

**Objetivo:** três melhorias de convivência: (a) edições de nó passam pelo `UndoRedo` do editor (Ctrl+Z desfaz o que a IA fez); (b) escritas em lote agrupadas para não disparar re-import em cascata (a engine "piscando"); (c) um status passivo no dock do addon ("IA aplicando X") em vez de roubar foco.

**Por quê:**
- UndoRedo: te devolve controle — se a IA fez algo que você não gostou, Ctrl+Z desfaz como qualquer edição sua. Sem isso, mudança da IA é irreversível pela via normal.
- Debounce: Godot re-importa asset quando arquivo muda; várias escritas rápidas = re-import em cascata = travadas/piscadas. Agrupar + um `EditorFileSystem.scan()` único no fim evita isso.
- Status passivo: o jeito certo de sinalizar "estou trabalhando" é passivo (ícone/notificação no dock), não roubar foco.

**Arquivos prováveis:** `tools/addon_bridge.py` (edição via UndoRedo do editor), o caminho de escrita de arquivos, o addon Godot (dock com status).

**O que fazer:**
1. Fazer edições de nó/propriedade passarem pelo `UndoRedo` do editor.
2. Debounce: agrupar escritas próximas, disparar um scan único no fim.
3. Status passivo no dock do addon (opcional/leve).

**Critério de aceite específico:**
- C2 (canary): fazer uma edição via IA e provar que Ctrl+Z a desfaz. Fazer 5 escritas rápidas e provar que houve 1 re-import, não 5. Cole evidência.
- C4 (não-intrusão): o status é passivo (não rouba foco).
- C3 (regressão): edições continuam corretas.

**Marcação:** [SÊNIOR] — mexe no caminho de edição; revisar.

---

## BLOCO D — RECUPERAÇÃO DE SESSÃO (NÃO PERDER O FIO)

### FATIA 1.8 — `resume_session` (recuperação de sessão) **[SÊNIOR]**

**Objetivo:** ao abrir um chat/sessão novo, o MCP lê o estado (fase, milestone, último passo aprovado, o que estava em andamento) e devolve **"você parou aqui, o próximo passo é X"** — automaticamente, sem você colar documento.

**Por quê:** você já sofre isso — os documentos de continuidade existem porque a sessão morre e você reconstrói contexto na mão. Isto é durable execution: o estado não vive só no processo. Funde o `get_next_step` + os documentos de continuidade num mecanismo. Mata uma dor real e recorrente.

**Arquivos prováveis:** `tools/phase_ops.py`, `tools/milestone_ops.py`, `tools/project_state.py`; op nova (rollup).

**O que fazer:**
1. Ler o estado persistente: fase atual, milestone, último passo aprovado, fatia/tarefa em andamento.
2. Montar um resumo de retomada: onde parou + próximo passo concreto.
3. Expor como op chamável no início de sessão (e/ou como Resource `godot://session/resume`).

**Critério de aceite específico:**
- C2 (canary): simular "parei na fatia X" e provar que `resume_session` devolve o ponto certo. Cole o output.
- C3 (regressão): não altera o estado, só lê.

**Marcação:** [SÊNIOR] — é a peça de "não me perder"; revisar o formato do resumo.

---

### FATIA 1.9 — Registro de passo concluído por fatia (durable execution) **[SÊNIOR]**

**Objetivo:** se a implementação de uma fatia trava no meio, ao retomar o MCP sabe o que já foi feito e o que falta — não recomeça do zero nem refaz o que passou.

**Por quê:** durable execution — passos concluídos têm resultado gravado; a retomada pega no primeiro passo não-concluído. Protege contra sessão que morre no meio de uma fatia longa.

**Arquivos prováveis:** o estado por projeto + o governador de autonomia (0.14); registro de progresso de fatia.

**O que fazer:**
1. Registrar, por fatia em andamento, os passos já concluídos (com resultado).
2. Ao retomar, ler o registro e continuar do passo pendente.
3. Ligar ao pacote de escalação (mestre 4.7) — o estado preservado alimenta a retomada.

**Critério de aceite específico:**
- C2 (canary): simular uma fatia interrompida no passo 3 de 5 e provar que a retomada continua do 4, sem refazer 1–3. Cole o registro.

**Marcação:** [SÊNIOR] — liga ao governador; revisar.

---

## BLOCO E — CORREÇÃO AUTOMÁTICA DE ERRO (OS VERMELHOS)

### FATIA 1.10 — Captura de erro unificada **[SÊNIOR]**

**Objetivo:** consolidar a captura de erro (parse/compilação, runtime/`push_error`, editor/referência quebrada) numa **estrutura única**: mensagem literal, arquivo, linha, stack, e **reprodutível sim/não**.

**Por quê:** você já tem `capture_runtime_errors`, `read_console_output`, `gdscript_diagnostics`, os `audit_*`. Falta um formato único que alimente o laço de correção. E o campo "reprodutível" é o que evita corrigir erro fantasma (armadilha 1).

**Arquivos prováveis:** `runtime_ops`, `console_ops`, `lsp_ops`, `audit_*`; um coletor unificado.

**O que fazer:**
1. Coletar erro das três fontes num formato comum.
2. Classificar em parse / runtime / editor.
3. Marcar reprodutível (aparece de novo ao re-rodar) sim/não.

**Critério de aceite específico:**
- C2 (canary): provocar um erro de cada tipo e provar que o coletor os captura no formato único com a classificação certa. Cole os três.
- C4 (não-intrusão): captura não roda o jogo desnecessariamente / não rouba foco.

**Marcação:** [SÊNIOR] — base do laço de correção; revisar o formato.

---

### FATIA 1.11 — Classificador + diagnóstico de causa raiz **[SÊNIOR]**

**Objetivo:** dado o erro capturado, diagnosticar a causa provável usando o que já existe (`gdscript_diagnostics` para parse, o stack para runtime, `audit_*` para referência quebrada) e **propor** a correção com a causa raiz explicada. Este passo é totalmente automático e sem risco (só propõe, não aplica).

**Por quê:** separar "diagnosticar" (seguro, automático) de "aplicar" (arriscado, semi-automático). Diagnóstico com causa raiz é o que evita corrigir sintoma em vez de causa (armadilha 2).

**Arquivos prováveis:** liga 1.10 aos diagnósticos existentes; lógica de diagnóstico.

**O que fazer:**
1. Rotear cada tipo de erro para o diagnóstico certo.
2. Produzir: causa provável + patch proposto + rótulo "corrige causa" vs "só silencia".
3. Não aplicar nada ainda.

**Critério de aceite específico:**
- C2 (canary): para um erro conhecido, provar que o diagnóstico aponta a causa certa e distingue "corrige" de "silencia". Cole.

**Marcação:** [SÊNIOR] — a qualidade do diagnóstico precisa de revisão.

---

### FATIA 1.12 — `auto_resolve_errors` (aplicar com trava) **[SÊNIOR]**

**Objetivo:** o laço completo — detectar → diagnosticar → aplicar → confirmar que o erro sumiu — com dois modos: **seguro** (aplica só correções triviais e inequívocas; propõe o resto) e **autônomo** (aplica tudo, mas sempre com checkpoint antes e regressão depois; rollback se quebrar). Marca claramente "corrigido" vs "silenciado".

**Por quê:** é o "patch-and-rerun". O passo crítico que a maioria pula: **confirmar que o erro específico sumiu ao re-rodar**. As três armadilhas (fantasma, sintoma, quebrar o que funcionava) são tratadas pelas travas: só age sobre erro reprodutível, distingue corrigir de silenciar, e passa pela regressão + rollback.

**Arquivos prováveis:** liga 1.10 + 1.11; usa `safety_manage` (checkpoint), o `verification_pipeline` (regressão), o governador (0.14, anti-spiral).

**O que fazer:**
1. Modo seguro (default): correções triviais e inequívocas (typo de nome de nó, import quebrado com destino óbvio, indentação) aplica sozinho; correções que mudam lógica → propõe e espera confirmação.
2. Modo autônomo: aplica tudo, checkpoint antes (mestre 3.3), regressão depois; se quebrou, rollback.
3. Sempre: só age sobre erro **reprodutível**; re-roda e **confirma que o erro específico sumiu**; marca "corrigido" (causa) vs "silenciado" (sintoma).
4. Respeita o anti-spiral (0.14): se a mesma correção falha 2x, para e escala.

**Critério de aceite específico:**
- C2 (canary): corrigir automaticamente um erro mecânico reprodutível e provar que ele sumiu ao re-rodar. Cole antes/depois. Provar que um erro de aparição única NÃO é "corrigido" (não age sobre fantasma).
- C4 (segurança): checkpoint antes de aplicar? sim. Rollback se regressão? sim, com prova.
- C3 (regressão): correção não quebra o que passava; se quebrar, rollback automático.

**Marcação:** [SÊNIOR] — aplica mudança de código automaticamente; a mais sensível do bloco. Revisão obrigatória. **Aviso de retorno decrescente honesto:** correção 100% automática de qualquer erro é miragem — erro de lógica de jogo ("inimigo atravessa parede") não é pegável por console. O alvo realista: eliminar os vermelhos mecânicos e repetitivos (null check, referência quebrada, typo, import) que são ~80% dos erros chatos, e **propor com diagnóstico** o resto.

---

## BLOCO F — GUIA / ARQUITETO / ANTI-ABANDONO

### FATIA 1.13 — `scope_guard` (guia de escopo) **[SÊNIOR]**

**Objetivo:** quando a IA (ou o dev) sugere uma feature nova em runtime de conversa, o MCP checa contra o GDD e o milestone atual e responde "isso está fora da fase X — adicionar ao roadmap ou fazer agora mesmo assim?". Não bloqueia; força a decisão consciente. Deve ser **agressivo** no corte, não gentil.

**Por quê:** scope creep é a causa nº1 nomeada de abandono de projeto solo — a IA acelera a velocidade de adicionar feature, não a disciplina de cortar. Um MCP obcecado por rigor pode até piorar isso se não tiver contrapeso. Este é o "hard cutoff" que os guias recomendam, automatizado. Também trava geração de arte final antes do milestone de mecânica fechado (evita refazer arte quando a mecânica muda).

**Arquivos prováveis:** usa `gdd`/`project_brief`/`milestone_ops`; op nova (rollup).

**O que fazer:**
1. Classificar toda ideia nova de feature contra o GDD/milestone: MVP / pós-MVP / fora de escopo.
2. Responder com a classificação + a pergunta (adicionar ao roadmap vs fazer agora).
3. Travar geração de arte final antes de a mecânica estar fechada.

**Critério de aceite específico:**
- C2 (canary): dar uma feature claramente fora de escopo e provar que é classificada como tal; dar uma MVP e provar que passa. Cole.

**Marcação:** [SÊNIOR] — a lógica de classificação precisa de calibração; revisar.

---

### FATIA 1.14 — `project_progress` (termômetro de progresso) **[AUTO]**

**Objetivo:** mostrar "você está em X% do milestone, faltam N itens".

**Por quê:** a pesquisa de anti-abandono mostra que ver o fim se aproximar é o que sustenta motivação na reta final (os "últimos 20% que custam 50%"). Você tem os milestones; falta o termômetro.

**Arquivos prováveis:** `milestone_ops`; op de leitura.

**O que fazer:** calcular e retornar o progresso do milestone atual (itens feitos / total, %).

**Critério de aceite específico:**
- C2 (canary): num milestone com N itens, M feitos, provar que retorna o % certo. Cole.

**Marcação:** [AUTO].

---

### FATIA 1.15 — `get_next_step` evoluído **[SÊNIOR]**

**Objetivo:** evoluir de "próxima ação obrigatória" (binário) para **"próxima ação + por que + o que NÃO fazer agora + a MENOR ação possível que avança"**.

**Por quê:** o papel de arquiteto/guia que você pediu. E o "menor passo possível" ataca a paralisia da baixa energia — o padrão dos devs é "quando bate o cansaço, faça a parte pequena ou só teste". Reduzir o próximo passo a algo trivial quebra a paralisia.

**Arquivos prováveis:** a tool `get_next_step` existente; usa fase/milestone/scope_guard.

**O que fazer:**
1. Além do próximo passo obrigatório: a justificativa (por quê agora), o que NÃO fazer (fora de escopo), e a menor ação que avança.
2. Modo "baixa energia": oferecer a menor ação, não a mais importante.

**Critério de aceite específico:**
- C2 (canary): provar que retorna os quatro elementos (passo, porquê, não-fazer, menor passo). Cole.
- C3 (regressão): não quebra o session gate que usa `get_next_step`.

**Marcação:** [SÊNIOR] — evolui uma tool central (Feature 10); revisar regressão do session gate.

---

### FATIA 1.16 — Buffer de escopo em `create_milestone_plan` **[SÊNIOR]**

**Objetivo:** o planejador de milestone reserva folga e empurra corte de escopo ativamente.

**Por quê:** escopo grande é a causa nº1 de abandono. Prática citada: reservar buffer no fim em vez de preencher até o limite. Se o milestone não modela folga, todo plano tende a estourar prazo por padrão.

**Arquivos prováveis:** `tools/milestone_ops.py::create_milestone_plan`.

**O que fazer:**
1. Ao gerar o plano, reservar folga explícita (buffer day / margem).
2. Sinalizar quando o escopo do milestone parece grande demais e sugerir corte.

**Critério de aceite específico:**
- C2 (canary): gerar um plano e provar que há buffer explícito; dar um escopo inflado e provar que sinaliza corte. Cole.
- C3 (regressão): `create_milestone_plan` continua funcionando (Feature 3 aprovada — reteste obrigatório).

**Marcação:** [SÊNIOR] — mexe em feature aprovada (Feature 3); reteste de regressão obrigatório.

---

## ORDEM SUGERIDA DENTRO DA CAMADA 1

1. **1.1** (engine não fecha) — a dor mais sentida.
2. **1.6** (não-intrusão) — regra transversal, quanto antes melhor (as fatias seguintes herdam).
3. **1.2, 1.3** (screenshot como imagem, capture_ui_snapshot) — base do bloco visual.
4. **1.4, 1.5** (detecção de sobreposição, Set-of-Marks) — resolvem a dor de UI sobreposta.
5. **1.7** (UndoRedo, debounce, status) — convivência.
6. **1.10, 1.11, 1.12** (correção de erro, na ordem) — os vermelhos.
7. **1.8, 1.9** (resume_session, durable execution) — não perder o fio.
8. **1.13, 1.14, 1.15, 1.16** (scope_guard, progresso, next_step, buffer) — guia/anti-abandono.

---

*Fim da Camada 1. Próximo documento: `03-camada-2-testes.md`.*
