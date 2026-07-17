# 03 — CAMADA 2 — TESTES

> Lê-se junto com `00-mestre.md`. **Esta camada começa intercalada com a Camada 0, não depois de tudo.** O erro já cometido neste projeto foi deixar teste para depois — hoje ~88% das tools (186 de 212) nunca foram testadas individualmente. Construir features novas em cima de código não testado é construir na areia.

Não é "testar tudo" (retorno decrescente — 186 testes manuais é inviável e a maioria nunca será usada). É **cobertura por tier de risco**. Formato de cada fatia: **Objetivo · Por quê · Arquivos prováveis · O que fazer · Critério de aceite específico · Marcação**.

Lembrete permanente: fluxo da seção 7 do mestre. Guardrails sempre ativos. Muitas destas fatias constroem o próprio ferramental que a autoauditoria usa — por isso vêm cedo.

---

## FATIA 2.1 — Cobertura Tier-1 (fluxo padrão) **[SÊNIOR]**

**Objetivo:** testar individualmente as tools que aparecem no fluxo padrão de um jogo pequeno e ainda estão marcadas como não testadas (❌ no catálogo).

**Por quê:** o "0% de correção manual" do teste end-to-end só vale para o fluxo que ele tocou. As tools do fluxo padrão que nunca foram testadas direto são o risco mais próximo — é o que o dev vai usar já.

**Candidatas (confirmar contra o catálogo/inventário 0.1):** `godot_run_project`, `godot_stop_project`, `take_screenshot`, ops de `scene_manage` não cobertas, `asset_manage`, `audio_manage`, `anim_manage`, `tilemap_manage`, `create_gun_system`, `dungeon_generate`. ~15–20 tools.

**O que fazer:**
1. Listar as tools do fluxo padrão ainda ❌.
2. Para cada uma: um teste com entrada mínima real e saída esperada.
3. Corrigir o que estiver quebrado (cada correção é uma sub-entrega com prova).

**Critério de aceite específico:**
- C2 (canary): cada tool testada tem 1–2 chamadas conhecidas-boas passando. Cole o stdout de cada.
- C3 (regressão): corrigir uma tool não pode quebrar outra.
- **Prova extra:** a lista de tools que passaram de ❌ para ✅, com o teste de cada.

**Marcação:** [SÊNIOR] — envolve corrigir tools existentes; cada correção que toca código aprovado exige reteste de regressão. Revisar.

---

## FATIA 2.2 — Smoke test automatizado sobre o inventário **[AUTO]**

**Objetivo:** rodar cada tool/rollup uma vez com entrada mínima, só para pegar crash de dispatch/import. Usar o `smoke_test` que já existe, de verdade, sobre todo o inventário.

**Por quê:** os 186 não testados não precisam de teste manual completo — precisam de uma passada barata que pega o óbvio (import quebrado, dispatch errado, crash na chamada). É o Tier-2 da cobertura por risco. E vira a base do critério C3 (regressão) da autoauditoria.

**Arquivos prováveis:** a tool `smoke_test` em `test_ops`; um runner que itera o inventário (usa 0.1).

**O que fazer:**
1. Iterar todas as tools/ops do inventário (0.1).
2. Chamar cada uma com entrada mínima válida.
3. Reportar: quais crasham, quais passam. Não valida comportamento profundo — só "não explode".

**Critério de aceite específico:**
- C2 (canary): rodar o smoke test completo e colar o resumo (N tools, N ok, N crash). Investigar cada crash.
- Este vira o ferramental que C3 usa nas fatias futuras.

**Marcação:** [AUTO].

---

## FATIA 2.3 — `test_coverage_report` **[AUTO]**

**Objetivo:** um relatório de cobertura de teste por tool/handler do próprio MCP — quais têm teste conhecido, quais não.

**Por quê:** você não sabe, hoje, com precisão, o que está e o que não está testado (o catálogo diz ~12%, mas é estimativa). Sem o número real, não dá para saber quando a cobertura Tier-1/Tier-2 é suficiente.

**Arquivos prováveis:** op em `test_ops`; cruza o inventário (0.1) com os testes existentes.

**O que fazer:**
1. Mapear cada tool/op para: tem teste? qual? passa?
2. Gerar o relatório com o número real de cobertura.

**Critério de aceite específico:**
- C2 (canary): rodar e colar o número de cobertura real + a lista do que falta.

**Marcação:** [AUTO].

---

## FATIA 2.4 — `generate_test_cases_from_gdd` **[SÊNIOR]**

**Objetivo:** gerar casos de teste a partir dos requisitos do GDD.

**Por quê:** liga o design ao teste — o que o GDD diz que o jogo deve fazer vira teste verificável. On-brand (rastreabilidade requisito→verificação).

**Arquivos prováveis:** usa `gdd`; op nova (rollup).

**O que fazer:**
1. Ler os requisitos do GDD.
2. Gerar casos de teste (o que verificar, entrada, saída esperada) para os requisitos testáveis.

**Critério de aceite específico:**
- C2 (canary): dar um GDD com requisitos e provar que gera casos de teste plausíveis e verificáveis. Cole.

**Marcação:** [SÊNIOR] — a qualidade dos casos gerados precisa de revisão.

---

## FATIA 2.5 — Regressão visual (screenshot vs baseline) **[SÊNIOR]**

**Objetivo:** comparar um screenshot contra um baseline salvo — pega bug visual que o console não pega (UI sobreposta, sprite invisível, cor errada).

**Por quê:** alguns erros só aparecem visualmente. O laço de correção de erro de console (1.10–1.12) não pega esses. Combinado com a detecção de sobreposição (1.4), você tem duas fontes de erro: console (texto) e tela (visual).

**Arquivos prováveis:** `vision_ops`; usa a captura (1.2) + comparação de imagem.

**O que fazer:**
1. Salvar baseline de uma cena/UI conhecida-boa.
2. Comparar captura atual contra o baseline; reportar diferença acima de um limiar.
3. Ligar à detecção de sobreposição (1.4) para explicar a diferença quando for UI.

**Critério de aceite específico:**
- C2 (canary): mudar algo visível e provar que a comparação detecta; não mudar nada e provar que passa. Cole.
- C4 (determinístico): mesma cena = mesma comparação.

**Marcação:** [SÊNIOR] — o limiar de "diferença relevante" precisa de calibração (evitar falso positivo por ruído de render). Revisar.

---

## FATIA 2.6 — `perf_regression_track` **[AUTO]**

**Objetivo:** rastrear regressão de performance entre commits, usando os dados de `profile_frame`/`profile_memory` que já existem.

**Por quê:** feature nova pode degradar FPS/memória sem quebrar nada funcionalmente. Sem rastreio, isso passa silencioso até o dispositivo errado.

**Arquivos prováveis:** `perf_ops`; op que compara métricas entre pontos no tempo.

**O que fazer:**
1. Capturar métricas de perf (frame, memória) num baseline.
2. Comparar contra medições novas; reportar regressão acima de um limiar.

**Critério de aceite específico:**
- C2 (canary): introduzir uma degradação proposital e provar que é detectada; sem degradação, passa. Cole.

**Marcação:** [AUTO].

---

## FATIA 2.7 — Canary queries por tool crítica **[AUTO]**

**Objetivo:** 2–3 chamadas conhecidas-boas por tool crítica, rodadas periodicamente contra baseline — pega drift silencioso de **comportamento** (não só de schema).

**Por quê:** o contract snapshot (0.11) pega drift de schema; este pega drift de comportamento (a tool ainda tem o mesmo schema, mas passou a retornar coisa diferente). É o outro lado da defesa contra drift. E é o ferramental que o critério C2 da autoauditoria usa.

**Arquivos prováveis:** `test_ops`; um conjunto de canary queries versionado.

**O que fazer:**
1. Para cada tool crítica, definir 2–3 chamadas com saída esperada.
2. Rodar periodicamente (e no CI); comparar contra o esperado.
3. Alertar quando o resultado muda sem mudança de schema.

**Critério de aceite específico:**
- C2 (canary): mudar o comportamento de uma tool de propósito e provar que a canary detecta a mudança. Cole.
- Vira o ferramental que C2 das fatias futuras usa.

**Marcação:** [AUTO].

---

## ORDEM SUGERIDA DENTRO DA CAMADA 2

Como a Camada 2 é intercalada com a 0, priorize primeiro o que vira ferramental de autoauditoria:

1. **2.2** (smoke test) — base do critério C3, e pega crash barato nos 186 não testados.
2. **2.7** (canary queries) — base do critério C2.
3. **2.3** (coverage report) — te dá o número real de cobertura.
4. **2.1** (Tier-1) — testa e corrige o fluxo padrão. Pode ser feito ao longo do tempo, tool a tool.
5. **2.6** (perf regression) — quando houver features que mexem em perf.
6. **2.5** (regressão visual) — junto/depois do bloco visual da Camada 1 (1.2–1.5).
7. **2.4** (test cases do GDD) — quando o fluxo de GDD estiver sendo exercitado.

**Regra de intercalação:** faça 2.2, 2.7 e 2.3 **cedo, junto da Camada 0** — elas constroem o ferramental que a autoauditoria de todas as fatias seguintes usa. As demais podem entrar conforme as features correspondentes forem sendo feitas.

---

*Fim da Camada 2. Próximo documento: `04-camada-3-criacao-com-fosso.md`.*
