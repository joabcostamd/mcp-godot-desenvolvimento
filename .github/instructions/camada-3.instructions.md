---
applyTo: '**'
---

# 04 — CAMADA 3 — CRIAÇÃO COM FOSSO

> Lê-se junto com `00-mestre.md`. Esta é a camada de **maior diferencial de produto**. A auditoria de mercado (8 rodadas de pesquisa) mostrou: nenhum concorrente faz criação de arte/música **com rigor de processo**. Os MCPs de engine (149–175 tools) geram zero arte/áudio; os geradores de arte/música entregam um arquivo cru e param. Você é o único que pode fazer "gerar → validar game-ready → travar se não passar". Isso é o fosso.

Roda depois da Camada 0 (precisa do cliente HTTP compartilhado 0.9 e da gestão de segredo 0.6). Formato de cada fatia: **Objetivo · Por quê · Arquivos prováveis · O que fazer · Critério de aceite específico · Marcação**.

Lembrete permanente: fluxo da seção 7 do mestre. Toda integração externa usa o cliente HTTP compartilhado (0.9), verifica segredo (0.6), e é idempotente (0.13). Toda tool nova é op de rollup (Regra 1 do teto), passa o teste de distinguibilidade (C6).

**Dependência dura de toda esta camada:** confirmar, com o inventário 0.1, o que os rollups `audio_manage`/`asset_manage`/`art_ops` já cobrem antes de construir — para não duplicar op que já existe escondida.

---

## BLOCO A — MÚSICA (o maior buraco de produto, o maior diferencial por esforço)

Contexto de mercado (pesquisa): você tem `generate_audio_sfx` e `generate_voice` (TTS), mas **zero geração de música**. O mercado maduro: Suno v5 (qualidade), Stable Audio 2.5 (loop royalty-clear, o caso de jogo), MiniMax Music 2.5 (API-first, ~$0.035/geração), AIVA (MIDI, game scoring). Existe até `mcp-suno` pronto. A verdade que torna isto seu: **"uma faixa gerada não é música de jogo até: (1) loopar sem emenda, (2) estar no volume certo, (3) tocar no evento certo."** Os geradores param no arquivo cru; fazer loopar + colocar no nó + disparar no evento é processo+engine = seu terreno.

Tudo aqui entra como um rollup novo `music_manage` (ops), não 4 tools de topo.

### FATIA 3.1 — `music_manage` op `generate` **[SÊNIOR]**

**Objetivo:** gerar música a partir de prompt de texto, via API barata (MiniMax ou Stable Audio para loop royalty-clear).

**Por quê:** o buraco central — não existe geração de música hoje. Baixo esforço (a integração é viável, há MCP pronto de referência), alto valor.

**Arquivos prováveis:** rollup novo `tools/music_ops.py`; usa o cliente HTTP compartilhado (0.9).

**O que fazer:**
1. Op `generate`: prompt + estilo → chama a API (via 0.9) → baixa a faixa.
2. Aplicar o style lock do brief (3.6), se já existir, ao estilo musical.
3. Rastrear custo (0.9).

**Critério de aceite específico:**
- C2 (canary): gerar uma faixa curta e provar que o arquivo chega válido. Cole o resultado (caminho + metadados, não o áudio).
- C4 (segurança): sem segredo em código (0.6); idempotente onde a API permitir (não gerar cobrança dupla).
- C1/C6: op nova em `music_manage`, distinguível de `generate_audio_sfx`.

**Marcação:** [SÊNIOR] — primeira integração de música; revisar a escolha de API e o tratamento de custo/erro.

---

### FATIA 3.2 — `music_manage` op `make_seamless_loop` **[SÊNIOR]**

**Objetivo:** pegar a faixa gerada, achar ponto de loop, fazer crossfade, exportar pronta para tocar em loop sem emenda.

**Por quê:** **este é o diferencial que ninguém no mercado de MCP tem.** Transforma "faixa" em "música de jogo". É o passo que os geradores não fazem.

**Arquivos prováveis:** `music_ops`; processamento de áudio (pode precisar de lib local, ex.: análise de onda para achar o ponto de loop).

**O que fazer:**
1. Analisar a faixa, achar o melhor ponto de loop.
2. Crossfade nas bordas para eliminar a emenda.
3. Exportar pronta para `AudioStreamPlayer` com `loop=true`.

**Critério de aceite específico:**
- C2 (canary): loopar uma faixa e provar que a emenda é suave (métrica objetiva: diferença de amplitude/fase no ponto de loop abaixo de um limiar). Cole a métrica.
- C4: determinístico para a mesma faixa.

**Marcação:** [SÊNIOR] — processamento de áudio; revisar a qualidade do loop.

---

### FATIA 3.3 — `music_manage` op `place_and_normalize` **[SÊNIOR]**

**Objetivo:** colocar a música loopável num `AudioStreamPlayer` na cena, roteada para o bus certo, com volume normalizado.

**Por quê:** o diferencial do "colocar no nó" (o que o Summer Engine faz e os geradores não). Volume normalizado = a música senta no nível certo em relação a SFX/voz.

**Arquivos prováveis:** `music_ops`; usa Addon Bridge / Runtime Bridge para criar o nó; `audio_manage` para o bus.

**O que fazer:**
1. Criar/configurar o `AudioStreamPlayer` com a faixa loopável.
2. Rotear para o bus de música.
3. Normalizar o volume (LUFS/pico alvo).

**Critério de aceite específico:**
- C2 (canary): colocar a música na cena e provar que o nó existe, aponta para a faixa, está no bus certo, e o volume está no alvo. Cole o dump do nó.
- C4 (não-intrusão): criar o nó não rouba foco/aba do editor (regra 1.6).

**Marcação:** [SÊNIOR].

---

### FATIA 3.4 — `music_manage` op `bind_to_event` **[SÊNIOR]**

**Objetivo:** conectar a música a um evento de jogo (entrar em combate, abrir menu, mudar de área) — ela toca quando o evento dispara.

**Por quê:** o terceiro pé de "música de jogo" — tocar no evento certo. Casa com o Runtime Bridge e o signal flow que você já tem (`analyze_signal_flow`).

**Arquivos prováveis:** `music_ops`; usa signal flow / Runtime Bridge.

**O que fazer:**
1. Dado um evento (sinal/estado de jogo) e uma faixa, conectar o disparo.
2. Transição básica (fade in/out) na troca.

**Critério de aceite específico:**
- C2 (canary): conectar a música a um evento e provar que ela dispara quando o evento ocorre (teste de runtime). Cole.
- C3 (regressão): não quebra `analyze_signal_flow`.

**Marcação:** [SÊNIOR].

---

## BLOCO B — ARTE GAME-READY (a identidade aplicada a arte)

Contexto (pesquisa): o mercado inteiro admite **"um asset gerado não é um asset de jogo"** — falta escala, colisão, material sob a luz da engine, rig. Os geradores param no `.glb`/PNG cru. Você é o único que pode fazer "gerar → validar game-ready → travar". Regra de timing (pesquisa greybox→vertical slice): arte em três momentos — placeholder desde o dia 1, arte-confirmatória cedo (rápida, não final), arte final só depois da mecânica travada. A fase CONTEUDO é o lugar da arte de verdade; PROTOTIPO deveria empurrar 1 rodada de arte-confirmatória antes de liberar CONTEUDO.

### FATIA 3.5 — `validate_asset_game_ready` **[SÊNIOR]**

**Objetivo:** ao importar um asset (GLB/PNG), checar: escala plausível, colisão presente (se aplicável), material que funciona sob a luz da cena, polycount dentro do orçamento da plataforma, rig (se personagem). Junta o `asset_budget_check` (orçamento de peso) aqui.

**Por quê:** **maior oportunidade de arte do relatório.** É puro Campo C — sua identidade aplicada a arte. Ninguém tem. Transforma asset cru em asset de jogo, com gate.

**Arquivos prováveis:** op em `asset_manage`; usa Runtime Bridge para inspecionar o asset importado.

**O que fazer:**
1. Para um asset importado, rodar as checagens (escala, colisão, material, polycount, rig).
2. Reportar o que passa e o que falta.
3. Opcional: ligar ao gate (asset não game-ready trava avanço de fase).

**Critério de aceite específico:**
- C2 (canary): importar um asset propositalmente sem colisão/escala errada e provar que a validação aponta os problemas; um asset bom e provar que passa. Cole ambos.
- C4 (determinístico).

**Marcação:** [SÊNIOR] — define "game-ready"; a régua precisa de revisão.

---

### FATIA 3.6 — Style lock no `project_brief` **[SÊNIOR]**

**Objetivo:** um "contrato de estilo" persistente no brief (paleta, referência visual, nível de detalhe, estilo — pixel/flat/hand-painted) que é **injetado automaticamente** em toda geração de arte e música.

**Por quê:** a regra de ouro do mercado (múltiplas fontes): **"um pack simples e consistente vale mais que dez assets bonitos de estilos diferentes."** A maior causa de jogo com "cara de colagem" é gerar asset a asset sem plano. Style lock resolve ~80% disso — template de prompt reutilizado, trocando só o assunto. Casa com o brief persistente que você já tem.

**Arquivos prováveis:** `project_brief_ops`; as tools de geração (`generate_game_art`, `music_ops`) leem o style lock.

**O que fazer:**
1. Campo de contrato de estilo no brief: paleta, referência, detalhe, estilo, fonte primária por categoria de asset.
2. Toda geração injeta automaticamente esse contrato no prompt, sem o dev repetir.

**Critério de aceite específico:**
- C2 (canary): setar um style lock e provar que duas gerações diferentes saem no mesmo estilo (o contrato foi injetado). Cole os prompts efetivos.
- C3 (regressão): `set/get/update_project_brief` (Feature 5 aprovada) continuam funcionando — reteste obrigatório.

**Marcação:** [SÊNIOR] — mexe em feature aprovada (Feature 5, brief); reteste de regressão obrigatório.

---

### FATIA 3.7 — Pipeline de arte travado **[SÊNIOR]**

**Objetivo:** orquestrar as peças soltas num fluxo travado: gerar → remover fundo → otimizar → importar → validar game-ready → só então liberar avanço.

**Por quê:** você tem as peças (`remove_background`, `optimize_sprite`, `validate_asset_game_ready`) mas falta a **orquestração travada** entre elas. Isso é feature de processo (seu terreno), não de arte.

**Arquivos prováveis:** `asset_manage`/orquestrador; encadeia as ops existentes.

**O que fazer:**
1. Encadear: geração → `remove_background` → `optimize_sprite` → import (com preset 3.8) → `validate_asset_game_ready` (3.5).
2. Travar: se a validação falha, não libera; reporta o que corrigir.
3. Idempotente e com checkpoint (é cadeia — 0.13, 0.5).

**Critério de aceite específico:**
- C2 (canary): rodar o pipeline ponta a ponta com um asset bom (passa) e um ruim (trava na validação). Cole ambos.
- C3 (regressão): as ops individuais continuam chamáveis fora do pipeline.

**Marcação:** [SÊNIOR] — orquestração de cadeia; revisar.

---

### FATIA 3.8 — Preset de import por categoria de asset **[SÊNIOR]**

**Objetivo:** aplicar automaticamente o preset de import certo por categoria — pixel art (filtro Nearest, sem mipmap), 3D realista (o oposto), UI (o seu).

**Por quê:** o `.import` do Godot é a fonte de verdade de como cada textura é processada, e é **por asset**, não automático por tipo. Sem preset por categoria, cada import novo pode sair com config errada e ninguém percebe até rodar no dispositivo errado — regressão visual silenciosa.

**Arquivos prováveis:** o caminho de import de asset; manipulação do `.import`.

**O que fazer:**
1. Definir presets por categoria (pixel/3D/UI).
2. Detectar/receber a categoria do asset e aplicar o preset no import.
3. Commitar o `.import` (é a fonte de verdade — versionar).

**Critério de aceite específico:**
- C2 (canary): importar um pixel art e provar que saiu com filtro Nearest; um 3D e provar o oposto. Cole os `.import`.
- C4 (determinístico).

**Marcação:** [SÊNIOR].

---

### FATIA 3.9 — Asset placement inteligente **[SÊNIOR]**

**Objetivo:** decidir automaticamente que tipo de nó recebe qual asset — personagem → `AnimatedSprite2D`, ambiente → `TileMapLayer`, UI → `TextureRect` — pelo contexto da entidade, não por escolha manual toda vez.

**Por quê:** sua pergunta direta ("como ele sabe onde colocar cada coisa?"). Hoje `apply_game_art` existe mas não está claro como decide o destino. Placement por contexto tira o trabalho manual repetitivo.

**Arquivos prováveis:** `apply_game_art`/`asset_manage`; usa o contexto da entidade (do brief/GDD/tipo).

**O que fazer:**
1. Mapear categoria de asset → tipo de nó destino.
2. Ao aplicar arte, escolher o nó certo pelo contexto da entidade.
3. Respeitar não-intrusão (1.6) — não mudar a aba/seleção do dev.

**Critério de aceite específico:**
- C2 (canary): aplicar arte de personagem e provar que foi para `AnimatedSprite2D`; de UI, para `TextureRect`. Cole o dump.
- C4 (não-intrusão).

**Marcação:** [SÊNIOR] — a lógica de mapeamento precisa de revisão (casos ambíguos).

---

## BLOCO C — ÁUDIO DE ENGINE E SFX (fechar o gap vs. concorrente)

### FATIA 3.10 — Bus/efeitos/espacial em `audio_manage` **[SÊNIOR]**

**Objetivo:** garantir que `audio_manage` cobre bus routing, efeitos de bus (reverb/EQ/compressão), e áudio espacial 3D (AudioStreamPlayer3D). Se o inventário 0.1 mostrar que já cobre, esta fatia só confirma; se não, adiciona as ops.

**Por quê:** o concorrente (tugcantopaloglu) tem `game_audio_effect`, `game_audio_bus_layout`, `game_audio_spatial` como tools. Você tem `audio_manage` — **[verificar no inventário 0.1]** se cobre. Sem áudio espacial, jogo 3D fica pobre.

**Arquivos prováveis:** `audio_ops`.

**O que fazer:**
1. Confirmar com 0.1 o que `audio_manage` já tem.
2. Adicionar as ops faltantes (bus routing, efeitos, espacial 3D) como ops do rollup.

**Critério de aceite específico:**
- C2 (canary): criar um bus com efeito e um AudioStreamPlayer3D com atenuação, provar que funcionam. Cole.
- C1: só ops novas no diff.

**Marcação:** [SÊNIOR] — depende do inventário; revisar o que já existe antes de duplicar.

---

### FATIA 3.11 — SFX em lote por evento de cena **[SÊNIOR]**

**Objetivo:** varrer a cena, listar eventos que deveriam ter som mas não têm (passos, impactos, cliques de UI), e gerar todos.

**Por quê:** ElevenLabs cobre "a outra metade" do áudio; um jogo precisa de centenas de SFX. Você tem `generate_audio_sfx` (singular). Versão em lote guiada por evento é automação forte.

**Arquivos prováveis:** `audio_ops`; usa signal flow para achar eventos sem som.

**O que fazer:**
1. Varrer a cena/sinais, listar eventos sem SFX.
2. Gerar SFX para cada (via cliente HTTP 0.9, style/consistência).
3. Colocar no nó/evento certo.

**Critério de aceite específico:**
- C2 (canary): numa cena com eventos sem som, provar que lista e gera. Cole a lista + resultado.

**Marcação:** [SÊNIOR].

---

### FATIA 3.12 — Sprite com esqueleto **[SÊNIOR]**

**Objetivo:** geração de animação de sprite com sistema de esqueleto, para consistência multi-frame.

**Por quê:** PixelLab (referência) faz sprite com esqueleto para consistência entre frames. Você tem `create_spritesheet` mas não animação de sprite consistente.

**Arquivos prováveis:** `art_ops`.

**O que fazer:**
1. Gerar/montar animação de sprite com esqueleto (frames consistentes).
2. Exportar como spritesheet + metadados de animação (AtlasTexture/AnimatedSprite2D).

**Critério de aceite específico:**
- C2 (canary): gerar uma animação simples e provar consistência entre frames. Cole.

**Marcação:** [SÊNIOR].

---

### FATIA 3.13 — `license_audit` como gate no import **[SÊNIOR]**

**Objetivo:** auditoria de licença de asset externo como **gate automático no import**, não relatório opcional.

**Por quê:** toda fonte de pesquisa insiste: "o problema não é usar asset grátis, é usar sem plano de licença". Asset misturado de fontes diferentes é onde licença vaza sem ninguém perceber. Gate no import pega antes de entrar no projeto.

**Arquivos prováveis:** `asset_manage`/import; op de auditoria de licença.

**O que fazer:**
1. No import de asset externo, checar licença (CC0/comercial/atribuição/restrito).
2. Registrar a licença por asset (rastreabilidade).
3. Gate: asset de licença incompatível com o projeto trava ou alerta.

**Critério de aceite específico:**
- C2 (canary): importar um asset com licença restrita e provar que o gate alerta; um CC0 e provar que passa. Cole.

**Marcação:** [SÊNIOR].

---

## BLOCO D — PLAYTEST AUTÔNOMO (verificação = seu fosso)

Contexto: playtest autônomo fortalece a verificação (sua identidade), então é Campo C, não Campo A. Entra como rollup `playtest_manage`.

### FATIA 3.14 — `playtest_manage` op `self_play` **[SÊNIOR]**

**Objetivo:** um agente joga o jogo automaticamente para achar bug (self-play).

**Por quê:** encontra bug que teste de código não pega (softlock, exploit, sequence break). Usa a captura visual (1.2) + input (`inject_input_event`/`simulate_input_sequence`) que você já tem.

**Arquivos prováveis:** `playtest_ops`; usa Runtime Bridge + input + captura.

**O que fazer:**
1. Rodar o jogo, injetar inputs, observar (captura + estado).
2. Detectar anomalias (travou, caiu, erro, não avança).
3. Reportar onde e como.

**Critério de aceite específico:**
- C2 (canary): rodar self-play num jogo simples e provar que completa uma sessão + reporta anomalia plantada. Cole.
- C4 (não-intrusão): roda por viewport interno, não rouba foco.

**Marcação:** [SÊNIOR] — comportamento complexo; revisar.

---

### FATIA 3.15 — `playtest_manage` op `regression_from_recording` **[SÊNIOR]**

**Objetivo:** gerar suíte de regressão a partir de uma gravação de gameplay real.

**Por quê:** transforma uma jogada boa em teste repetível — se uma feature nova quebra o fluxo gravado, você sabe.

**Arquivos prováveis:** `playtest_ops`; usa `record_gameplay_gif`/recording + replay.

**O que fazer:**
1. Gravar uma sessão de gameplay (input + estado esperado).
2. Reproduzir como teste; falha se o resultado diverge.

**Critério de aceite específico:**
- C2 (canary): gravar uma jogada, reproduzir e provar que passa; quebrar algo e provar que a regressão detecta. Cole.

**Marcação:** [SÊNIOR].

---

### FATIA 3.16 — `playtest_manage` op `difficulty_curve` **[SÊNIOR]**

**Objetivo:** analisar a curva de dificuldade a partir de playtest simulado (onde o jogador trava, quanto tempo por seção).

**Por quê:** dado de balanceamento sem precisar de playtester humano. Liga ao `balance_analyze` que você já tem.

**Arquivos prováveis:** `playtest_ops` + `balance_ops`.

**O que fazer:**
1. Rodar múltiplas sessões de self-play com perfis diferentes.
2. Medir onde trava, tempo por seção, taxa de falha.
3. Reportar a curva.

**Critério de aceite específico:**
- C2 (canary): rodar e provar que produz uma curva plausível a partir dos dados. Cole.

**Marcação:** [SÊNIOR].

---

## ORDEM SUGERIDA DENTRO DA CAMADA 3

Pré-requisito: 0.1 (inventário), 0.6 (segredo), 0.9 (cliente HTTP) prontos.

1. **3.6** (style lock) — primeiro, porque toda geração seguinte se beneficia dele.
2. **3.1 → 3.2 → 3.3 → 3.4** (música, na ordem) — o maior diferencial por esforço; fluxo completo gerar→loop→colocar→disparar.
3. **3.5** (validate_asset_game_ready) — a identidade aplicada a arte.
4. **3.8** (preset de import) — antes do pipeline, o pipeline usa.
5. **3.7** (pipeline de arte travado) — orquestra 3.5+3.8+ops existentes.
6. **3.9** (asset placement) — responde "onde colocar".
7. **3.10, 3.11** (áudio de engine, SFX em lote) — fechar gap de áudio.
8. **3.13** (license gate) — antes de importar muito asset externo.
9. **3.12** (sprite com esqueleto) — quando precisar de animação de sprite.
10. **3.14 → 3.15 → 3.16** (playtest autônomo) — quando houver jogo jogável para testar.

---

*Fim da Camada 3. Próximo documento: `05-camada-4-extensoes-processo.md`.*
