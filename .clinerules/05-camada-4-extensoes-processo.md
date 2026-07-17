# 05 — CAMADA 4 — EXTENSÕES DE PROCESSO

> Lê-se junto com `00-mestre.md`. Camada on-brand (reforça o processo/verificação, sua identidade), esforço médio. Aqui entram: teste de i18n, CI de verificação, **organização de código Godot** (a resposta à sua pergunta sobre gdtoolkit), segurança/supply-chain, orquestração de agentes, save schema, dead-end de quest, e documentação automática.

Roda depois das Camadas 0–3. Formato de cada fatia: **Objetivo · Por quê · Arquivos prováveis · O que fazer · Critério de aceite específico · Marcação**.

Lembrete permanente: fluxo da seção 7 do mestre. Toda tool nova = op de rollup, passa distinguibilidade (C6).

---

## FATIA 4.1 — Teste de i18n (traduções faltantes, overflow, contraste) **[SÊNIOR]**

**Objetivo:** detectar traduções faltantes/incompletas, texto cortado em UI com idioma longo (alemão, russo), e contraste ruim.

**Por quê:** você tem `setup_localization`/`add_translation_string` (criar tradução) mas **zero teste** de i18n. **Nenhum MCP de mercado tem isso** — diferencial de nicho, baixo esforço, casa com verificação. Overflow de texto usa a detecção geométrica de UI (1.4). Contraste usa a captura (1.2).

**Arquivos prováveis:** `localization_ops`; usa `capture_ui_snapshot` (1.3), detecção de sobreposição (1.4).

**O que fazer:**
1. `find_missing_translations`: cruzar strings do jogo com as traduções; listar faltantes.
2. Overflow: trocar o locale, capturar UI, detectar texto que estoura o Rect2 do container.
3. Contraste: checar contraste texto/fundo a partir da captura.

**Critério de aceite específico:**
- C2 (canary): faltar uma tradução e provar que detecta; forçar um texto longo que estoura e provar que detecta o overflow. Cole.

**Marcação:** [SÊNIOR].

---

## FATIA 4.2 — Gatilho de CI da verificação **[AUTO]**

**Objetivo:** rodar `run_verification_pipeline` (+ os gates de 0.8/0.11) a cada commit/push, via GitHub Actions.

**Por quê:** o gate é local hoje; falta o gate no repositório. Casa com sua obsessão por prova. Roadmap Fase 2 original, item 12.

**Arquivos prováveis:** `.github/workflows/`; usa `generate_ci_snippet` (existe, untested).

**O que fazer:**
1. Workflow de CI que roda a verificação + contract snapshot (0.11) + gate de orçamento (0.8) a cada push/PR.
2. Falha o build em regressão/breaking não intencional.

**Critério de aceite específico:**
- C2 (canary): um push com quebra proposital falha o CI; um push limpo passa. Cole o resultado do CI.
- C3 (regressão): `generate_ci_snippet` — se for usado/tocado, reteste.

**Marcação:** [AUTO].

---

## FATIA 4.3 — `code_quality_manage`: gdtoolkit como gate **[SÊNIOR]**

**Objetivo:** integrar o **gdtoolkit** (`gdlint` + `gdformat` + `gdradon`) como **gate dentro do `run_verification_pipeline`**, não relatório avulso.

**Por quê:** esta é a resposta direta à sua pergunta "o MCP tem ferramenta de organização de código dentro do Godot?" — não tinha, e gdtoolkit é o padrão de facto para GDScript. Detecta: função longa, complexidade ciclomática, **god_class** (o padrão nº1 de degradação em projeto Godot que cresce rápido com IA gerando código), nomeação inconsistente, parâmetro em excesso, aninhamento profundo, variável não usada. Roda sem o editor aberto, tem CLI para CI. **O ponto crítico:** integrar como **gate**, não relatório — se roda dentro da verificação, toda feature nova impede que o código do jogo degrade. É o "não deixar a casa nova quebrar a antiga" aplicado ao próprio jogo.

**Arquivos prováveis:** rollup novo `code_quality_ops` (ou op em `analysis_manage`); ligar ao `verification_ops`. gdtoolkit é Python (`pip install gdtoolkit`), roda standalone.

**O que fazer:**
1. Integrar gdlint (análise) + gdformat (formatação) + gdradon (complexidade).
2. Configurar limiares (`.gdlintrc`): função, complexidade, god_class, nomenclatura.
3. Ligar ao `run_verification_pipeline` como gate: código que viola os limiares críticos não fecha a feature.
4. A versão do gdtoolkit deve casar com o major do Godot (4.x → `gdtoolkit==4.*`).

**Critério de aceite específico:**
- C2 (canary): um script com god_class/função longa proposital falha o gate; um limpo passa. Cole o output do gdlint.
- C3 (regressão): `run_verification_pipeline` (usado pela Feature 2) continua funcionando — reteste obrigatório.

**Marcação:** [SÊNIOR] — mexe no pipeline de verificação central (Feature 2 aprovada); reteste de regressão obrigatório.

---

## FATIA 4.4 — `code_quality_manage`: análises específicas **[SÊNIOR]**

**Objetivo:** análises que o gdtoolkit não cobre: função não usada, bloco duplicado, antipadrão Godot (`get_node` em loop, uso pesado de `_process`, polling desnecessário), sinal órfão/nó órfão, ciclo de referência entre cenas, consistência de import settings, nomenclatura de nós, busca semântica no código.

**Por quê:** complementa o gdtoolkit com verificações específicas de Godot que evitam degradação. Ciclo de cena (A instancia B que instancia A) e sinal órfão são bugs silenciosos comuns.

**Arquivos prováveis:** `code_quality_ops` (ops adicionais).

**O que fazer:** cada uma como op do rollup: `find_unused_functions`, `find_duplicate_code_blocks`, `detect_gdscript_antipatterns`, `find_orphan_signals_nodes`, `detect_scene_reference_cycles`, `check_import_settings_consistency`, `check_naming_convention`, `semantic_code_search`, `suggest_refactor`.

**Critério de aceite específico:**
- C2 (canary): para cada op adicionada, plantar o problema que ela detecta e provar que detecta; caso limpo passa. Cole (pode ser incremental, uma op por sub-entrega).
- C5/C6: são ops de um rollup, distinguíveis entre si.

**Marcação:** [SÊNIOR] — muitas ops; fazer incremental, uma ou poucas por sub-entrega, cada uma com prova.

---

## FATIA 4.5 — Segurança / supply-chain **[SÊNIOR]**

**Objetivo:** `scan_addon_vulnerabilities`, `check_addon_license` (distinto de licença de asset), consistência de import settings entre assets do mesmo tipo.

**Por quê:** addon de terceiro é vetor de risco (a pesquisa de 2026 mostrou exploits reais em MCP/addons). Complementa a gestão de segredo (0.6).

**Arquivos prováveis:** rollup de segurança existente (`security_ops`); ops novas.

**O que fazer:**
1. Scan de vulnerabilidade conhecida em addons/plugins.
2. Checagem de licença de addon.
3. Consistência de import entre assets do mesmo tipo.

**Critério de aceite específico:**
- C2 (canary): plantar um addon com problema conhecido e provar que detecta. Cole.

**Marcação:** [SÊNIOR].

---

## FATIA 4.6 — `agent_manage` (orquestração de agentes) **[SÊNIOR]**

**Objetivo:** rollup para coordenar a própria IA agêntica: file lock entre agentes, fila de tarefa com dependência, pedido de revisão cruzada, comparar outputs de modelos, gerar context pack para handoff, gerar onboarding brief para agente novo.

**Por quê:** dá suporte ao próprio processo autônomo. O `compare_agent_outputs` liga direto à verificação cross-model Pro↔Flash (mestre 6). O context pack liga à recuperação de sessão (1.8) e ao pacote de escalação (mestre 4.7).

**Arquivos prováveis:** rollup novo `agent_ops`; usa `config_lock` (existe), o estado por projeto.

**O que fazer:** ops: `acquire/release_file_lock`, `create_task_queue`/`get_next_task`, `request_peer_review`, `compare_agent_outputs`, `generate_agent_context_pack`, `generate_agent_onboarding_brief`.

**Critério de aceite específico:**
- C2 (canary): provar file lock (dois "agentes" não editam o mesmo arquivo ao mesmo tempo); provar que `compare_agent_outputs` roda os critérios objetivos contra dois resultados. Cole.
- C4 (segurança): file lock via `config_lock` (escrita concorrente protegida).

**Marcação:** [SÊNIOR].

---

## FATIA 4.7 — Save schema + migração **[SÊNIOR]**

**Objetivo:** `generate_save_schema` (gerar schema de save a partir da estrutura de dados do jogo) + migração de save antigo.

**Por quê:** save é onde dado de jogador vive; sem schema + migração, atualização do jogo quebra saves antigos. Análogo à migração de estado do MCP (0.10), mas para o save do jogo.

**Arquivos prováveis:** `gamestate_ops`; ops novas.

**O que fazer:**
1. Gerar schema de save a partir da estrutura de dados.
2. Migração de save de versão antiga para nova.

**Critério de aceite específico:**
- C2 (canary): migrar um save antigo (fixture) e provar que preserva dados. Cole antes/depois.

**Marcação:** [SÊNIOR].

---

## FATIA 4.8 — Dead-end de quest/diálogo **[SÊNIOR]**

**Objetivo:** validação de beco sem saída — quest impossível de completar, ramo de diálogo sem saída.

**Por quê:** `dialogue_manage` existe; falta a validação de que o jogador não fica preso. Bug de design comum e difícil de pegar manualmente.

**Arquivos prováveis:** `dialogue_ops`; análise de grafo de quest/diálogo.

**O que fazer:**
1. Modelar quest/diálogo como grafo.
2. Detectar nós sem saída, quests sem condição de conclusão alcançável.

**Critério de aceite específico:**
- C2 (canary): montar um diálogo com beco sem saída proposital e provar que detecta; um bem formado passa. Cole.

**Marcação:** [SÊNIOR].

---

## FATIA 4.9 — Documentação automática **[AUTO]**

**Objetivo:** `generate_changelog` (do git log), `generate_project_readme` (do estado real), `generate_project_wiki`.

**Por quê:** doc que se gera sozinha do estado real não envelhece. Baixo risco (só lê e escreve doc).

**Arquivos prováveis:** rollup de doc (ou ops em rollup existente); lê git log + estado.

**O que fazer:**
1. Changelog a partir do git log.
2. README/wiki a partir do estado real do projeto.

**Critério de aceite específico:**
- C2 (canary): gerar o changelog e provar que reflete os commits reais. Cole.

**Marcação:** [AUTO].

---

## ORDEM SUGERIDA DENTRO DA CAMADA 4

1. **4.3** (gdtoolkit como gate) — a resposta à sua dor de organização de código; alto valor, on-brand.
2. **4.4** (análises específicas) — complementa 4.3, incremental.
3. **4.2** (CI da verificação) — leva os gates para o repositório.
4. **4.1** (i18n) — diferencial de nicho, usa o bloco visual da Camada 1.
5. **4.5** (supply-chain) — segurança de addon.
6. **4.6** (agent_manage) — suporte ao próprio processo autônomo.
7. **4.7, 4.8** (save schema, dead-end) — quando o jogo tiver save/quest.
8. **4.9** (doc automática) — a qualquer momento; baixo risco.

---

*Fim da Camada 4. Próximos documentos: `06`, `07`, `08` (camadas marginais).*
