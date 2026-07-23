# CATALOGO COMPLETO DE TOOLS — MCP Godot Agent

> Total: 287 tools | Data: 2026-07-21 (⚠️ snapshot histórico. Auditoria 2026-07-23: 236 tools visíveis, 272 definições brutas, 189 depreciadas)
> TOOLSETS: 5 namespaces | Fases: 6

## 1. ARQUITETURA DE CURADORIA

4 camadas controlam quais tools o modelo ve:

| Camada | Mecanismo | Funcao |
|---|---|---|
| 1 | _raw_tool_defs() | 287 tools registradas (lista plana) |
| 2 | --profile (lean/dev/full) | Filtro grosso por perfil de uso |
| 3 | --toolsets (5 namespaces) | Filtro por dominio |
| 4 | PHASE_TOOLSETS + CORE | Filtro por fase do jogo (IDEIA→PRONTO) |

### 1.1 Profiles

| Profile | Tools | Uso |
|---|---|---|
| lean | 14 | Modo minimalista, so essenciais |
| dev | 46 | Desenvolvimento ativo |
| full | 287 | Sem filtro |

## 2. TOOLSETS — 5 NAMESPACES (zero sobreposicao)

### 2.1 project (96 tools)

[ ] `accessibility_add_subtitles` | fase=ORFA | Adiciona sistema de legendas/closed captions ao projeto. Gera script de UI que exibe legendas sincronizadas com audio. Use para dialogos, cutscenes e 
[ ] `accessibility_apply_colorblind_filter` | fase=ORFA | Aplica filtro de daltonismo ao projeto (shader fullscreen). Suporta 4 tipos: protanopia, deuteranopia, tritanopia, achromatopsia. Modos: simulate (com
[ ] `accessibility_remap_controls` | fase=ORFA | Configura sistema de remapeamento de controles. Permite jogador redefinir teclas e botoes do joystick. Gera UI de configuracao e script de persistenci
[ ] `add_nodes_batch` | fase=PROTOTIPO | Adiciona múltiplos nós a uma cena em UMA OPERAÇÃO. Muito mais rápido que chamar add_node repetidamente. Use para criar vários filhos de uma vez (ex: 5
[ ] `add_parallax_layer` | fase=CONTEUDO | Adiciona uma camada a um ParallaxBackground existente. Use para adicionar mais camadas de profundidade a um cenario parallax. Quando NAO usar: se aind
[ ] `add_raycast_2d` | fase=ORFA | Adiciona um RayCast2D a um no para deteccao de linha de visao. Use para: verificar se ha chao a frente, detectar obstaculos, mirar armas. Configura po
[ ] `add_shapecast_2d` | fase=ORFA | Adiciona um ShapeCast2D para deteccao de area em linha. Use para deteccao mais robusta que RayCast: ataques melee, sensores de chao largos. Suporta fo
[ ] `add_translation_string` | fase=CONTEUDO | Adiciona uma string traduzida ao sistema de localizacao. Use para cada texto que aparece na UI: botoes, labels, dialogos. Forneca as traducoes como di
[R] `anim_manage` | fase=PROTOTIPO | 
[ ] `batch_atomic_edit` | fase=PROTOTIPO | ⚛️ Edição ATÔMICA em lote com ROLLBACK automático. Executa múltiplas operações (criar nó, definir propriedade, deletar, reparentar, duplicar, conectar
[ ] `behavior_tree_generate` | fase=DESIGN | Gera Behavior Tree completa em GDScript a partir de descricao em portugues. Analisa texto como 'patrulha, detecta, persegue, ataca, foge' e gera codig
[ ] `behavior_tree_list_templates` | fase=DESIGN | Lista templates de Behavior Tree disponiveis: patrol_chase_attack, patrol_chase_attack_flee, guard_alert_chase, idle_wander_flee, boss_phases.
[ ] `camera_configure_attributes` | fase=PROTOTIPO | Configura atributos de câmera 3D: DOF, exposição, near/far, FOV. Quando usar: para ajustar profundidade de campo, exposição ou clipping da câmera. Pré
[R] `camera_manage` | fase=PROTOTIPO | 
[ ] `cloud_save_configure` | fase=ORFA | Configura sistema de Cloud Save (Steam Auto-Cloud ou local). Gera CloudSaveManager GDScript com save/load automático em user://. Use para persistir pr
[R] `config_manage` | fase=DESIGN | 
[ ] `create_achievement_system` | fase=ORFA | Cria sistema de conquistas e Cloud Save para o projeto. Gera script GDScript com AchievementManager (Steamworks + offline) e CloudSaveManager com supo
[ ] `create_animation_tree` | fase=PROTOTIPO | Adiciona um nó AnimationTree a uma cena. Use para animações avançadas com blend trees e state machines. Superior ao AnimationPlayer para transições co
[ ] `create_bullet_template` | fase=CONTEUDO | Cria uma cena de projetil (bullet) reutilizavel para sistemas de tiro. Use em shooters, tower defense, ou qualquer jogo com armas de projetil. Define 
[ ] `create_entities` | fase=CORE+DESIGN | Cria MULTIPLAS entidades em lote sequencial. Cada entidade passa pelo mesmo pipeline de create_entity (cena + collider + script + arte + audio + compi
[ ] `create_entity` | fase=CORE+DESIGN | Cria uma entidade COMPLETA: cena + collider + script + sprite + audio. Decide automaticamente o que gerar. Use para inimigos, players, NPCs, itens. Ex
[ ] `create_gun_system` | fase=CONTEUDO | Cria um script de sistema de arma com fire rate, municao, reload e spread. Use para armas do player ou inimigos: pistola, metralhadora, shotgun. Inclu
[ ] `create_joint_2d` | fase=ORFA | Cria uma junta 2D (PinJoint2D) conectando dois nós. Use para portas giratórias, pontes basculantes, cordas, alavancas. Suporta PinJoint2D (ponto fixo)
[ ] `create_light_2d` | fase=PROTOTIPO | Adiciona PointLight2D ou DirectionalLight2D a uma cena. Use para iluminação 2D: tochas, lanternas, luz ambiente. Configura cor, energia (intensidade) 
[ ] `create_light_3d` | fase=ORFA | Adiciona uma luz 3D (OmniLight3D, SpotLight3D ou DirectionalLight3D) a uma cena. Use para iluminar cenas 3D: tochas, lanternas, luz solar. Configura c
[ ] `create_navigation_agent_2d` | fase=ORFA | Adiciona NavigationAgent2D com script de perseguição. O nó pai DEVE ser CharacterBody2D. Gera script que persegue o alvo usando pathfinding da Navigat
[ ] `create_navigation_region_2d` | fase=ORFA | Cria região de navegação 2D com polígono. Define área onde personagens podem andar. Use ao criar mapa com pathfinding. Depois use create_navigation_ag
[ ] `create_parallax_background` | fase=CONTEUDO | Cria um fundo com efeito parallax (ParallaxBackground + multiplas camadas). Use para dar profundidade a jogos 2D: ceu, montanhas, nuvens em velocidade
[ ] `create_path_2d` | fase=CONTEUDO | Cria um Path2D com PathFollow2D para movimentacao controlada por curva. Use para plataformas moveis, rotas de camera, ou animacoes de trajetoria. Pre-
[ ] `create_patrol_route` | fase=CONTEUDO | Cria uma rota de patrulha com waypoints e script de movimento automatico. Use para inimigos que patrulham, NPCs andando, ou objetos moveis em rotas. S
[ ] `create_spritesheet` | fase=CONTEUDO | Cria sprite sheet a partir de frames individuais. Use para juntar frames de animacao em uma unica imagem.
[ ] `csg_create_node` | fase=PROTOTIPO | Cria nó CSG (Constructive Solid Geometry) para prototipagem 3D: box, sphere, cylinder, torus. Quando usar: para blockout/prototipagem rápida de níveis
[ ] `csharp_build_project` | fase=PRONTO_PARA_LANCAR | Compila o projeto C# do Godot via dotnet build. Quando usar: para verificar erros de compilação em scripts C#. Pré-condições: projeto C# scaffoldado, 
[ ] `csharp_generate_script` | fase=DESIGN | Gera script C# a partir de templates: basic, player, enemy, pickup, ui. Quando usar: para criar rapidamente scripts C# com boilerplate. Pré-condições:
[ ] `csharp_scaffold_project` | fase=DESIGN | Cria/scaffolda um projeto C# Godot: .csproj, .sln, script exemplo. Quando usar: para iniciar desenvolvimento C# no Godot. Pré-condições: projeto Godot
[ ] `cutscene_add_camera_shot` | fase=ORFA | Adiciona um shot de camera a uma cutscene. Define alvo, transicao (cut, fade, dissolve, zoom, pan) e duracao. Use dentro de cutscene_create_timeline o
[ ] `cutscene_add_dialogue_event` | fase=ORFA | Adiciona evento de dialogo a uma cutscene. Define falante, texto e duracao da exibicao. Use para inserir falas de NPCs ou narrador na timeline. Exempl
[ ] `cutscene_create_timeline` | fase=ORFA | Cria linha do tempo de cutscene com eventos sequenciais. Suporta shots de camera, dialogo, audio, animacao e esperas. Gera script GDScript com orquest
[R] `d3_manage` | fase=CONTEUDO | 
[ ] `dialogue_generate_npc_lines` | fase=ORFA | Gera linhas de dialogo para NPCs baseado em tipo e contexto. Suporta 8 personalidades (guarda, mercador, sabio, vilao, etc.) e 7 cenarios (greeting, q
[ ] `dialogue_generate_personality` | fase=ORFA | Gera perfil completo de personalidade para NPC. Define tracos, tom de fala, motivacoes e estilo de dialogo. Use para criar NPCs profundos e consistent
[R] `dialogue_manage` | fase=CONTEUDO | 
[R] `file_manage` | fase=CORE+DESIGN | 
[R] `gamestate_manage` | fase=CONTEUDO | 
[ ] `generate_project_structure` | fase=DESIGN | Gera a estrutura completa de pastas e arquivos base para um projeto Godot. Cria pastas padronizadas (scenes, scripts, assets), scene principal com nod
[ ] `gi_create_node` | fase=PROTOTIPO | Cria nó de Global Illumination (VoxelGI ou LightmapGI) para iluminação indireta 3D. Quando usar: para melhorar qualidade de iluminação em cenas 3D. Pr
[R] `inventory_manage` | fase=CONTEUDO | 
[ ] `load_scene_async` | fase=PROTOTIPO | Carrega uma cena de forma assincrona com tela de loading. Use para transicoes suaves entre fases ou areas grandes. Mostra progresso real de carregamen
[ ] `loot_table_generate` | fase=CONTEUDO | Gera tabela de loot balanceada com chances de drop por raridade. Suporta temas: scifi, fantasy, modern, post_apocalyptic.
[ ] `mod_manifest_generate` | fase=ORFA | Gera manifesto de mod (mod.json) para projetos Godot. Define nome, versao, dependencias e arquivos do mod. Use para criar sistema de modding no jogo. 
[ ] `multimesh_create_instance` | fase=PROTOTIPO | Cria um MultiMeshInstance3D para renderizar muitos objetos idênticos com performance. Quando usar: para árvores, pedras, grama — centenas de instância
[R] `navigation_manage` | fase=CONTEUDO | 
[ ] `network_configure_dedicated_server` | fase=CONTEUDO | Configura parâmetros de servidor dedicado para exportação. Quando usar: para preparar build headless de servidor. Pré-condições: projeto Godot. Exempl
[ ] `network_create_lobby` | fase=CONTEUDO | Cria sistema de lobby básico para multiplayer: salas, join/ready, transição. Quando usar: para implementar tela de espera antes de partida multiplayer
[ ] `network_create_rpc` | fase=CONTEUDO | Adiciona um método RPC (@rpc) a um script GDScript. Quando usar: para criar funções que rodam remotamente em multiplayer. Pré-condições: script .gd ex
[ ] `network_create_websocket` | fase=CONTEUDO | Adiciona código de WebSocket client a um script GDScript. Quando usar: para comunicação com servidores externos (APIs, chat, matchmaking). Pré-condiçõ
[ ] `network_setup_multiplayer` | fase=CONTEUDO | Configura multiplayer peer (ENet ou WebSocket) gerando script de setup. Quando usar: para adicionar multiplayer ao jogo. Pré-condições: projeto Godot 
[R] `node_manage` | fase=CORE+DESIGN | 
[ ] `onboarding_create_guided_tour` | fase=ORFA | Cria tour guiado pela UI do jogo. Sequencia de destaques que mostram cada elemento da interface. Use para primeira experiencia do jogador (FTUE). Exem
[ ] `onboarding_create_tutorial_step` | fase=ORFA | Cria passo de tutorial interativo com highlight e instrucao. Gera script GDScript que destaca no da UI, mostra texto e aguarda acao. Use para ensinar 
[ ] `physics_configure_body` | fase=PROTOTIPO | Configura propriedades físicas de um corpo: massa, atrito, bounce, damping, freeze. Quando usar: para ajustar comportamento físico de RigidBody ou Cha
[ ] `physics_create_joint` | fase=PROTOTIPO | Cria um joint físico entre dois corpos: PinJoint2D, Spring, Hinge, Cone, Slider. Quando usar: para conectar corpos rígidos (ex: portas, pontes, cordas
[R] `physics_manage` | fase=PROTOTIPO | 
[R] `project_manage` | fase=CORE+IDEIA | 
[ ] `project_map` | fase=DESIGN | Gera mapa do projeto: cenas, scripts, funcoes, assets. Formatos: json ou html.
[ ] `project_status` | fase=CORE+IDEIA | Status completo do projeto: cenas, scripts, sprites, audio, assets faltantes, sugestoes do que criar a seguir. Use para diagnosticar o estado do jogo.
[ ] `quest_generate` | fase=ORFA | Gera quest procedural baseada em templates. Tipos: fetch, kill, boss, explore. Inclui titulo, objetivos, recompensas e dialogo de NPC. Use para criar 
[R] `raycast_manage` | fase=PROTOTIPO | 
[ ] `read_file` | fase=CORE+IDEIA | Lê o conteúdo de um arquivo do projeto (.gd, .tscn, .tres, etc.). Use para examinar scripts, cenas ou qualquer arquivo de texto do projeto. Quando NÃO
[ ] `render_get_settings` | fase=DESIGN | Obtém configurações atuais de rendering do project.godot. Quando usar: para auditar qualidade gráfica antes de modificar. Pré-condições: project.godot
[ ] `render_set_antialiasing` | fase=CONTEUDO | Configura antialiasing: MSAA (2x/4x/8x), FXAA, TAA. Quando usar: para melhorar qualidade de bordas ou performance. Pré-condições: project.godot acessí
[ ] `render_set_quality` | fase=CONTEUDO | Configura qualidade de rendering por preset (low/balanced/high/ultra) ou manual. Quando usar: para otimizar performance ou maximizar qualidade. Pré-co
[ ] `render_set_scaling` | fase=CONTEUDO | Configura modo de scaling/resolução: modo, escala, stretch. Quando usar: para configurar como o jogo se adapta a diferentes resoluções. Pré-condições:
[ ] `safe_write_gdscript` | fase=CORE+DESIGN | Escreve .gd COM validacao. Recusa codigo invalido! Ex: {'file_path':'res://x.gd','content':'...'}.
[ ] `scene_fx_create_node` | fase=PROTOTIPO | Cria nó de efeito de cena: ReflectionProbe, Decal, FogVolume. Quando usar: para adicionar reflexos, decalques ou neblina volumétrica. Pré-condições: c
[R] `scene_manage` | fase=CORE+DESIGN | 
[R] `script_manage` | fase=CORE+DESIGN | 
[ ] `set_properties_batch` | fase=PROTOTIPO | Define múltiplas propriedades em UMA OPERAÇÃO. Muito mais rápido que chamar set_node_property repetidamente. Use para configurar vários nós de uma vez
[ ] `setup_camera_2d` | fase=ORFA | Adiciona e configura uma Camera2D com limites, zoom, drag e suavização. Use ao criar qualquer cena 2D que precise de câmera. Quando NÃO usar: se a cen
[ ] `setup_localization` | fase=CONTEUDO | Configura o sistema de traducao (i18n) do projeto. Use para jogos com suporte a multiplos idiomas (ex: PT-BR, EN, ES). Cria arquivos de traducao CSV e
[ ] `skeleton_create_bone` | fase=PROTOTIPO | Cria um novo osso num Skeleton3D existente. Quando usar: para adicionar ossos extras a um rig (ex: osso de arma, acessório). Pré-condições: cena com S
[ ] `skeleton_create_ik_chain` | fase=PROTOTIPO | Cria/configura uma chain SkeletonIK3D vinculada a um osso. Quando usar: para adicionar IK procedural (ex: pés no chão, mão alcançando objeto). Pré-con
[ ] `skeleton_get_bone_pose` | fase=DESIGN | Obtém a pose (transform) de um osso específico num Skeleton3D. Quando usar: para inspecionar posição/rotação de um osso antes de animar. Pré-condições
[ ] `skeleton_get_info` | fase=DESIGN | Obtém informações completas de um Skeleton3D: bones, IK chains, estrutura. Quando usar: visão geral do rig antes de modificações. Pré-condições: cena 
[ ] `skeleton_list_bones` | fase=DESIGN | Lista todos os ossos de um Skeleton3D com índices, nomes e hierarquia. Quando usar: para conhecer a estrutura do esqueleto antes de criar animações ou
[ ] `skeleton_set_bone_pose` | fase=PROTOTIPO | Define a pose (transform) de um osso num Skeleton3D. Quando usar: para posicionar ossos para animação ou correção de rig. Pré-condições: cena com Skel
[ ] `sky_create_procedural` | fase=PROTOTIPO | Cria um céu procedural ou físico (Sky/PhysicalSky) numa cena 3D. Quando usar: para configurar o céu e iluminação ambiente. Pré-condições: cena 3D com 
[R] `tilemap_manage` | fase=CONTEUDO | 
[ ] `ui_configure_focus_nav` | fase=DESIGN | Configura navegação por foco entre widgets (gamepad/teclado). Quando usar: para navegação fluida em menus com controle ou teclado. Pré-condições: nós 
[ ] `ui_create_tab_with_content` | fase=DESIGN | Adiciona uma tab com conteúdo a um TabContainer existente. Quando usar: para criar interfaces com abas (configurações, inventário). Pré-condições: Tab
[ ] `ui_create_widget` | fase=DESIGN | Cria widget de UI granular: Tree, ItemList, OptionButton, TabContainer, PopupMenu, ProgressBar, Slider, SpinBox, ColorPicker, LineEdit, TextEdit, Rich
[R] `ui_manage` | fase=DESIGN | 
[ ] `ui_set_anchor_preset` | fase=DESIGN | Define anchor preset de um nó Control para layout responsivo. Quando usar: para posicionar elementos UI que se adaptam a diferentes resoluções. Pré-co
[ ] `ui_set_tooltip` | fase=DESIGN | Define o texto de tooltip de um nó Control. Quando usar: para adicionar dicas de interface. Pré-condições: nó Control na cena. Exemplo: veja documenta
[ ] `world_describe` | fase=DESIGN | Analisa um mundo gerado e sugere melhorias e pontos de interesse. Detecta biomas e recomenda elementos de gameplay.
[ ] `write_file` | fase=CORE+IDEIA | Cria ou modifica um arquivo no projeto. Use para criar scripts GDScript, editar cenas manualmente, ou qualquer escrita de arquivo. Quando NÃO usar: pa

### 2.2 assets (40 tools)

[ ] `apply_game_art` | fase=PROTOTIPO | Aplica arte gerada (frames recortados) num AnimatedSprite2D do Godot. Importa frames, cria SpriteFrames .tres, configura animacao com FPS e loop. Use 
[R] `asset_manage` | fase=PROTOTIPO | 
[R] `audio_manage` | fase=PROTOTIPO | 
[ ] `capsule_generate_store_image` | fase=ORFA | Gera imagem de capsula para loja (Steam). Suporta 6 tamanhos: header (920x430), small (231x87), main (616x353), vertical (374x448), hero (3840x1240), 
[ ] `configure_particles_2d` | fase=ORFA | Configura particulas 2D (GPUParticles2D) com parametros de emissao. Use para efeitos visuais: explosao, fumaca, sparkles, chuva, neve. Suporta presets
[ ] `configure_standard_material_3d` | fase=ORFA | Aplica e configura um StandardMaterial3D a um MeshInstance3D. Use para definir aparencia de objetos 3D: cor, metallic, roughness. Suporta presets: met
[ ] `create_asset_manifest` | fase=CONTEUDO | Gera um template de asset_manifest.json no projeto com exemplos. Use para iniciar a configuracao de assets em lote. Pre-condicoes: projeto ativo confi
[ ] `create_particles_2d` | fase=ORFA | Adiciona GPUParticles2D com ParticleProcessMaterial a uma cena. Use para efeitos visuais: explosão, fumaça, sparkles, chuva, neve. Configura amount, l
[ ] `create_particles_3d` | fase=ORFA | Adiciona GPUParticles3D a uma cena 3D com presets visuais. Use para fogo, fumaca, ou outros efeitos de particula em jogos 3D. Suporta presets: fire, s
[ ] `download_asset` | fase=CONTEUDO | Baixa assets GRATUITOS (CC0) de APIs publicas. Fontes: Poly Haven (texturas PBR, HDRIs, modelos 3D), Kenney (sprites, tilesets, UI, audio), AmbientCG 
[ ] `dungeon_generate` | fase=CONTEUDO | Gera dungeon procedural com salas e corredores (algoritmo BSP). Salas classificadas como combat, treasure, boss, start, empty. GRATIS.
[ ] `edit_shader` | fase=ORFA | Edita .gdshader com validacao antes de escrever.
[ ] `generate_3d_asset` | fase=PROTOTIPO | Gera asset 3D via API Hyper3D Rodin (⚠️💰 ~$0.05/modelo) ou placeholder GRATIS. SEM custo se HYPER3D_API_KEY nao configurada. Categorias: prop, charact
[ ] `generate_3d_placeholder` | fase=PROTOTIPO | Gera placeholder 3D procedural (box, sphere, cylinder, cone, pyramid). Preview PNG + codigo de cena Godot .tscn. GRATIS — Pillow.
[ ] `generate_audio_sfx` | fase=PROTOTIPO | Gera um efeito sonoro WAV por sintese procedural com 23 tipos. Suporta: beep, jump, laser, explosion, collect, hit, coin, ui_click, ui_hover, ui_error
[ ] `generate_dungeon_rooms` | fase=CONTEUDO | Gera um layout procedural de dungeon com salas e corredores. Use para roguelikes, RPGs, ou qualquer jogo com masmorras aleatorias. Retorna dados das s
[ ] `generate_game_art` | fase=PROTOTIPO | Gera arte de jogo a partir de descricao em linguagem natural usando IA (ChatGPT/DALL-E via navegador headless). Gera QUALQUER artefato: torres, inimig
[ ] `generate_game_art_flux` | fase=PROTOTIPO | Gera arte de jogo via FLUX.2 API (Black Forest Labs). Substitui o DALL-E/Playwright. Suporta: torre, inimigo, personagem, bioma, tile, icone, hud, vfx
[ ] `generate_shader_2d` | fase=ORFA | Gera um shader 2D a partir de templates pre-definidos. Use para efeitos visuais avancados: glow, dissolve, outline, water, wind. O shader e salvo como
[ ] `generate_voice` | fase=CONTEUDO | Gera narracao/fala a partir de texto (TTS). Usa Kokoro TTS local (82M params, Apache 2.0, offline) ou Edge TTS gratuito como fallback. Ideal para dial
[ ] `get_shader_params` | fase=ORFA | Extrai as declaracoes uniform de um shader.
[ ] `import_3d_model` | fase=CONTEUDO | Importa um modelo 3D (.glb/.gltf) e opcionalmente cria cena com MeshInstance3D. Use para trazer modelos 3D para o projeto. Quando usar: se o usuário f
[ ] `import_asset_manifest` | fase=CONTEUDO | Importa TODOS os assets listados no asset_manifest.json do projeto. Suporta 5 fontes: generate (IA), placeholder (procedural), sfx (audio), import (ar
[ ] `import_downloaded_asset` | fase=CONTEUDO | Importa um asset baixado para o projeto Godot ativo. Use APOS download_asset. Exemplo: {'asset_path': 'C:/.../gdm_assets/...', 'target_dir': 'assets/t
[ ] `juice_apply` | fase=CONTEUDO | Aplica tecnicas de game feel/polish profissional: coyote time, input buffer, hit-stop, screen shake, squash & stretch, easing. Presets: full, platform
[ ] `juice_list_presets` | fase=CONTEUDO | Lista presets de juice disponiveis com tecnicas incluidas.
[ ] `marketplace_download` | fase=CONTEUDO | Baixa asset gratuito do marketplace. Kenney.nl (ZIP direto, CC0). GRATIS.
[ ] `marketplace_search` | fase=CONTEUDO | Busca assets em marketplaces gratuitos: Kenney.nl (CC0, 300+ packs), Godot Asset Library, OpenGameArt, Poly Haven. GRATIS.
[R] `music_manage` | fase=ORFA | 
[ ] `optimize_sprite` | fase=CONTEUDO | Otimiza/compacta sprite PNG usando oxipng (lossless, 10-30% reducao). Use antes de exportar o jogo para reduzir tamanho final.
[ ] `read_shader` | fase=ORFA | Le o conteudo de um arquivo .gdshader existente.
[ ] `remove_background` | fase=CONTEUDO | Remove o fundo de uma imagem usando IA (rembg/birefnet). Use para sprites gerados por IA que vieram com fundo. Suporta PNG, JPG, WebP. Retorna PNG com
[ ] `shader_generate` | fase=PROTOTIPO | Gera arquivo .gdshader a partir de descricao em portugues. 15 templates 2D: glow, dissolve, water, wind, hologram, forcefield, outline, pixelate, chro
[ ] `shader_list_templates` | fase=PROTOTIPO | Lista 15 templates de shader 2D disponiveis com palavras-chave.
[R] `shader_manage` | fase=PROTOTIPO | 
[ ] `terrain_generate` | fase=CONTEUDO | Gera terreno procedural com biomas por altura/umidade. Usa FastNoiseLite (built-in Godot). Retorna JSON com seed, distribuicao de biomas e parametros 
[ ] `trailer_capture_clip` | fase=ORFA | Captura clipe de gameplay para trailer. Suporta specs por plataforma: Steam (1080p60), itch.io (720p30), YouTube. Inclui instrucoes de montagem com FF
[ ] `trailer_render_sequence` | fase=ORFA | Define sequencia de cenas para renderizacao de trailer. Planeja storyboard: quais cenas, ordem, duracao, acoes. Valida duracao total contra limite da 
[R] `vfx_manage` | fase=PROTOTIPO | 
[ ] `wave_generate` | fase=CONTEUDO | Gera composicao de ondas para tower defense. Curva de dificuldade (linear, exponential, staircase). Chefoes a cada N waves. Use para planejar as waves

### 2.3 runtime (81 tools)

[ ] `addon_batch_edit` | fase=PRONTO_PARA_LANCAR | Executa MÚLTIPLAS operações no editor em UMA ação UndoRedo. 1 Ctrl+Z desfaz TUDO. Ideal para criar estruturas complexas. Exemplo: [{"method": "create_
[ ] `addon_connect` | fase=PRONTO_PARA_LANCAR | Conecta ao addon GDScript via WebSocket na porta 9082. Use após abrir o Godot com o addon MCP instalado. Pré-condições: Godot editor ABERTO com addon 
[ ] `addon_create_node` | fase=PRONTO_PARA_LANCAR | Cria um nó na cena atual do editor Godot com UndoRedo NATIVO (Ctrl+Z funciona). Use para adicionar nós visualmente no editor — é a versão ao vivo de n
[ ] `addon_delete_node` | fase=PRONTO_PARA_LANCAR | Remove um nó da cena do editor com UndoRedo nativo. Pré-condições: addon conectado.
[ ] `addon_disconnect` | fase=PRONTO_PARA_LANCAR | Desconecta do addon GDScript.
[ ] `addon_duplicate_node` | fase=PRONTO_PARA_LANCAR | Duplica um nó no editor com UndoRedo nativo. Pré-condições: addon conectado.
[ ] `addon_get_scene_tree` | fase=PRONTO_PARA_LANCAR | Obtém a árvore da cena atual do editor via addon. Retorna estrutura hierárquica completa com tipos e paths. Pré-condições: addon conectado.
[ ] `addon_is_available` | fase=PRONTO_PARA_LANCAR | Verifica se o addon GDScript está conectado e respondendo. Use para decidir entre modo editor (addon) ou file-based.
[ ] `addon_ping` | fase=PRONTO_PARA_LANCAR | Verifica se o addon GDScript está respondendo (ping/pong).
[ ] `addon_reparent_node` | fase=PRONTO_PARA_LANCAR | Move um nó para outro pai no editor com UndoRedo nativo. Pré-condições: addon conectado.
[ ] `addon_set_property` | fase=PRONTO_PARA_LANCAR | Define uma propriedade de nó no editor com UndoRedo nativo. Use para ajustar posição, escala, cor, etc. com feedback visual imediato. Pré-condições: a
[ ] `addon_take_screenshot` | fase=PRONTO_PARA_LANCAR | Captura screenshot do viewport do editor Godot via addon. Alternativa ao take_screenshot (TCP bridge) — funciona via WebSocket. Pré-condições: addon c
[ ] `assert_node_exists` | fase=ORFA | Verifica se no existe na cena. Ex: {'scene_path':'...','node_path':'./Player'}.
[ ] `auto_screenshot` | fase=POLIMENTO | Gera screenshots automaticas do jogo rodando para loja (itch.io/Steam). GRATIS.
[ ] `build_csharp` | fase=PRONTO_PARA_LANCAR | Compila projeto C# e retorna erros estruturados.
[ ] `capture_game_screenshot` | fase=PROTOTIPO | Captura uma screenshot do jogo em execução usando janela off-screen. Use para VER o estado atual do jogo sem abrir o Godot — a IA pode analisar a imag
[ ] `capture_runtime_errors` | fase=PROTOTIPO | Captura informacoes de runtime: FPS, contagem de objetos, estado da arvore.
[R] `debug_manage` | fase=POLIMENTO | 
[ ] `debugger_get_stack` | fase=POLIMENTO | Obtem stack trace atual do debugger.
[ ] `debugger_get_variables` | fase=POLIMENTO | Inspeciona variaveis no escopo do debugger. Ex: {'variable_name':'health'}.
[ ] `debugger_set_breakpoint` | fase=POLIMENTO | Define breakpoint. Ex: {'script_path':'res://player.gd','line':42}.
[ ] `debugger_status` | fase=POLIMENTO | Verifica estado do debugger do Godot (porta 6006).
[ ] `debugger_step` | fase=POLIMENTO | Avança uma linha no debugger. Ex: {'step_type':'over'}.
[ ] `effect_probe` | fase=PROTOTIPO | Verifica se uma acao no jogo produziu o efeito esperado. Avalia expressao antes, executa acao, avalia depois, compara. Ideal para testar: 'o dano redu
[ ] `execute_gdscript_runtime` | fase=PROTOTIPO | Executa código GDScript arbitrário no jogo em execução e retorna o valor. Use para consultar estado do jogo, modificar nós, ou testar lógica em tempo 
[R] `export_manage` | fase=PRONTO_PARA_LANCAR | 
[ ] `freeze_game_clock` | fase=PROTOTIPO | Congela o relogio do jogo. Use antes de step_game_time para playtesting deterministico.
[ ] `game_await_signal` | fase=ORFA | Espera sinal com timeout.
[R] `game_bridge_manage` | fase=PROTOTIPO | 
[ ] `game_call_method` | fase=ORFA | Chama metodo em no no jogo rodando.
[ ] `game_find_nodes_by_class` | fase=ORFA | Encontra nos por classe no jogo.
[ ] `game_get_camera` | fase=ORFA | Obtem posicao da camera ativa.
[ ] `game_http_request` | fase=ORFA | HTTP request no jogo. Ex: {'url':'https://api.ex.com','method':'GET'}.
[ ] `game_input_state` | fase=ORFA | Estado de input: teclas, mouse, gamepad.
[ ] `game_multiplayer` | fase=ORFA | Multiplayer ENet. Ex: {'action':'create_server','port':9090}.
[ ] `game_pause` | fase=ORFA | Pausa/despausa o jogo.
[ ] `game_performance` | fase=ORFA | Metricas: FPS, memoria, objetos, draw calls.
[ ] `game_play_animation` | fase=ORFA | Controla AnimationPlayer no jogo.
[ ] `game_raycast` | fase=ORFA | Ray cast 2D/3D no jogo.
[ ] `game_serialize_state` | fase=ORFA | Salva/restaura estado completo do jogo como JSON.
[ ] `game_spawn_node` | fase=ORFA | Cria no dinamicamente no jogo.
[ ] `game_window` | fase=ORFA | Controle de janela: size, fullscreen, title.
[ ] `get_runtime_state_digest` | fase=PROTOTIPO | Retorna estado do jogo como JSON: posicao, velocidade, grupos de todas as entidades.
[ ] `godot_custom_command` | fase=PROTOTIPO | Chama comando customizado registrado no jogo (ex: get_puzzle_state).
[ ] `godot_exec` | fase=PROTOTIPO | Executa codigo GDScript DENTRO do jogo rodando. Use para setup de cenarios de teste: spawnar inimigos, modificar estado. Use 'return' para obter valor
[ ] `godot_keep_alive` | fase=PROTOTIPO | Garante que o Godot Editor esta aberto. Se nao estiver, abre. NAO fecha o Godot em hipotese alguma. Chame no inicio de toda sessao. Use quando suspeit
[ ] `godot_list_custom_commands` | fase=PROTOTIPO | Lista comandos customizados registrados no bridge do jogo.
[ ] `godot_run_project` | fase=PROTOTIPO | Lanca o jogo direto via CLI (godot --path <projeto>), sem abrir o editor. Retorna pid.
[ ] `godot_runtime_info` | fase=PROTOTIPO | FPS, draw calls, memoria estatica e tempo de fisica do jogo rodando agora.
[ ] `godot_screenshot` | fase=PROTOTIPO | Captura screenshot do jogo rodando via MCPRuntimeBridge. Jogo precisa estar em execucao (debug).
[ ] `godot_stop_project` | fase=PROTOTIPO | Encerra um processo de jogo iniciado por godot_run_project.
[ ] `godot_wait_for_bridge` | fase=PROTOTIPO | Espera ate o MCPRuntimeBridge responder (polling de runtime_info).
[ ] `inject_input_event` | fase=PROTOTIPO | Injeta um evento de input (mouse/teclado) no jogo EM EXECUÇÃO. Use para simular cliques, teclas, ou movimento de mouse durante o jogo. Quando NÃO usar
[ ] `physics_query_area_overlap` | fase=PROTOTIPO | Prepara código para verificar corpos/áreas sobrepostos a uma Area2D/Area3D em runtime. Quando usar: para detectar se algo entrou numa área de trigger.
[ ] `physics_raycast_query` | fase=PROTOTIPO | Prepara código para executar raycast em runtime via nó RayCast2D/3D. Quando usar: para detectar colisões em linha reta (tiro, visão, ground check). Pr
[R] `playtest_manage` | fase=ORFA | 🎮 Playtest automatizado do jogo (ONDA 3). Operacoes: smoke (teste de sanidade: FPS, crash, viewport) e persona_run (persona scriptada joga o jogo: apr
[ ] `profile_frame` | fase=POLIMENTO | Analisa performance do jogo rodando: FPS medio/min/max, draw calls, uso de memoria e nos na cena. Sugere otimizacoes especificas. Nota A (otimo) ate D
[ ] `profile_memory` | fase=POLIMENTO | Analisa uso de memoria do jogo (estatica + video) e detecta objetos. GRATIS — sem API externa.
[ ] `read_console_output` | fase=PRONTO_PARA_LANCAR | Lê as últimas linhas do console do editor Godot. Use para diagnosticar erros de runtime, warnings, ou ver prints de debug. Quando NÃO usar: se o edito
[ ] `record_gameplay_gif` | fase=PROTOTIPO | Grava a tela do jogo por N segundos e retorna um GIF animado em base64. Usa Godot --write-movie para capturar frames e PIL para compor GIF. Quando usa
[ ] `regression_test` | fase=POLIMENTO | Teste de regressao: valida correcoes dos GRUPOS 1 e 2 (write_file .gd, R2, GUT skipped). NAO requer Godot rodando. Retorna status de cada validacao e 
[ ] `run_gut_tests` | fase=POLIMENTO | Executa testes GUT via Godot headless. Ex: {'test_dir': 'res://tests'}.
[ ] `run_scripted_tests` | fase=POLIMENTO | Executa cenarios de teste roteirizados com input sintetico. NAO requer Godot rodando — testa as tools do MCP diretamente. Use para validar correcoes, 
[ ] `run_stress_test` | fase=ORFA | Teste de stress com carga e input aleatorio REPRODUTIVEL. Spawna N instancias de uma cena, injeta input aleatorio com seed explicita, e coleta FPS/mem
[ ] `run_verification_pipeline` | fase=POLIMENTO | Executa pipeline de verificacao completo em um projeto Godot: compilacao, execucao headless, screenshot e testes GUT. Retorna relatorio consolidado JS
[ ] `runtime_connect_signal` | fase=PROTOTIPO | Gera código GDScript para conectar sinais em runtime. Quando usar: para wiring dinâmico de callbacks (ex: botão criado em código). Pré-condições: nós 
[ ] `runtime_disconnect_signal` | fase=PROTOTIPO | Gera código GDScript para desconectar sinais em runtime. Quando usar: para limpar conexões que não são mais necessárias. Pré-condições: sinal previame
[ ] `runtime_emit_signal` | fase=PROTOTIPO | Gera código GDScript para emitir sinal em runtime. Quando usar: para disparar eventos customizados programaticamente. Pré-condições: script com signal
[R] `runtime_manage` | fase=PROTOTIPO | 
[ ] `simulate_input_sequence` | fase=PROTOTIPO | Simula sequencia de inputs. Ex: {'actions':[{'type':'key','key':32}]}.
[ ] `smoke_test` | fase=POLIMENTO | Smoke test rapido: valida pipeline core do MCP (ping, ClassDB, validacao, config). NAO requer Godot rodando. Ideal para inicio de sessao. Retorna stat
[ ] `start_recording` | fase=PROTOTIPO | Inicia gravacao de sessao (inputs/estados).
[ ] `step_game_time` | fase=PROTOTIPO | Avanca o jogo em N ms e congela novamente. Ex: 500ms = meio segundo de jogo processado.
[ ] `step_until` | fase=PROTOTIPO | Avanca o jogo ate que uma condicao GDScript seja verdadeira. Com timeout.
[ ] `stop_recording` | fase=PROTOTIPO | Para gravacao e retorna resumo.
[ ] `take_screenshot` | fase=PROTOTIPO | Captura uma screenshot do viewport 2D do editor Godot. Use para VER o estado atual do jogo sem precisar abri-lo manualmente. A imagem é retornada em b
[R] `test_manage` | fase=POLIMENTO | 
[ ] `unfreeze_game_clock` | fase=PROTOTIPO | Descongela o relogio do jogo (retoma execucao normal).
[ ] `watch_signal` | fase=PROTOTIPO | Observa um sinal de um nó por N segundos e retorna se disparou. Use para verificar se um evento ocorreu (ex: inimigo morreu, animação terminou). Verif
[ ] `watch_state_collect` | fase=PROTOTIPO | Coleta o historico de estados observados desde watch_state_start(). Retorna array de snapshots com timestamp e valores das propriedades.
[ ] `watch_state_start` | fase=PROTOTIPO | Comeca a observar propriedades de nos do jogo a cada step. Use para monitorar HP, posicao, velocidade durante playtesting. Depois colete com watch_sta

### 2.4 analysis (41 tools)

[ ] `accessibility_audit_scene` | fase=ORFA | Audita cena para problemas de acessibilidade. Verifica contraste de cores, tamanho de texto, navegacao sem mouse, informacao apenas por cor, legendas 
[ ] `accessibility_certification_checklist` | fase=ORFA | Checklist de certificacao de acessibilidade. Cobre requisitos Steam, console (TRC/TCR) e boas praticas. Retorna nota e itens pendentes por categoria. 
[ ] `adaptive_difficulty_adjust` | fase=ORFA | Analisa desempenho do jogador e sugere ajustes de dificuldade. Usa metricas (mortes, kills, tempo, dano, precisao) para recomendar mudancas em HP, dan
[R] `analysis_manage` | fase=IDEIA | 
[ ] `analyze_signal_flow` | fase=DESIGN,PROTOTIPO | Analisa conexoes de sinal no projeto: detecta sinais conectados a metodos que nao existem mais (orfaos pos-refatoracao) e sinais declarados mas nunca 
[ ] `audit_autoloads` | fase=IDEIA | Audita os Autoloads do projeto: lista autoloads registrados e detecta autoloads possivelmente nao usados. NAO requer Godot rodando — analise estatica.
[ ] `audit_input_map` | fase=IDEIA | Audita o Input Map do projeto: lista acoes declaradas, acoes nao usadas e acoes referenciadas mas nao declaradas. NAO requer Godot rodando — analise e
[ ] `audit_save_compatibility` | fase=IDEIA | Audita a compatibilidade de save: verifica se o SaveManager tem campo de versao e logica de migracao. Detecta chaves write/read inconsistentes e chave
[ ] `audit_scene_reachability` | fase=IDEIA | Audita a alcançabilidade de cenas: partindo da cena principal, detecta cenas que nao sao referenciadas por nenhuma outra (orfas). NAO requer Godot rod
[ ] `audit_uid_consistency` | fase=IDEIA | Audita a consistencia de UIDs no projeto: detecta UIDs duplicados, UIDs com mismatch entre .uid e .import, e UIDs nao resolvidos. NAO requer Godot rod
[ ] `balance_analyze` | fase=CONTEUDO | Analisa o balanceamento do jogo e sugere ajustes. Calcula DPS necessario, verifica se o jogo eh 'vencivel', detecta torres com custo-beneficio ruim, i
[ ] `dps_calculator` | fase=CONTEUDO | Calcula DPS efetivo de uma torre/arma considerando criticos, dano em area e dano continuo (DoT). Retorna Time-To-Kill para HPs de referencia.
[ ] `estimate_tool_tokens` | fase=POLIMENTO | Estima o consumo de tokens do tools/list para cada perfil de ferramentas. Mede o tamanho do JSON que seria enviado no tools/list inicial e converte pa
[ ] `find_unused_resources` | fase=CONTEUDO,POLIMENTO | Encontra assets que existem no projeto mas nao sao referenciados por nenhum .tscn, .gd ou .tres (orfaos). Varre imagens, audio, modelos 3D, .tres e fo
[ ] `find_usages` | fase=CORE+DESIGN | Encontra TODOS os usos de um recurso/alvo no projeto (estatico, sem LSP). Busca em .tscn (ExtResource, scene instances) e .gd (preload/load). NAO requ
[ ] `gdscript_definition` | fase=DESIGN | Navega para a definição de um símbolo GDScript. Use para encontrar onde uma variável, função ou classe foi declarada. Pré-condições: LSP conectado.
[ ] `gdscript_diagnostics` | fase=DESIGN | Retorna erros e warnings do compilador GDScript via LSP. Mais preciso que validate_gdscript_syntax (tempo real, contextual). Pré-condições: LSP conect
[ ] `gdscript_hover` | fase=DESIGN | Exibe tipo e documentação de um símbolo GDScript sob o cursor. Use para inspecionar tipo de variável ou assinatura de função. Pré-condições: LSP conec
[ ] `gdscript_lsp_connect` | fase=DESIGN | Conecta ao Language Server do Godot na porta 6005. Use no início da sessão, após abrir o editor Godot com o projeto. Quando NÃO usar: se o editor não 
[ ] `gdscript_lsp_disconnect` | fase=DESIGN | Desconecta do Language Server do Godot. Use ao finalizar a sessão ou antes de fechar o editor.
[ ] `gdscript_references` | fase=DESIGN | Encontra todas as referências a um símbolo GDScript (variável, função, classe). Use para rastrear usos antes de renomear ou refatorar. Pré-condições: 
[ ] `gdscript_rename` | fase=DESIGN | Renomeia um símbolo GDScript em TODO o projeto com segurança semântica. Diferente de grep/replace, o LSP entende escopo e não quebra referências. Quan
[ ] `gdscript_symbols` | fase=DESIGN | Lista símbolos (funções, classes, variáveis) de um arquivo GDScript. Use para obter índice estrutural do código. Pré-condições: LSP conectado.
[ ] `gdscript_sync_file` | fase=DESIGN | Notifica o LSP sobre alterações em um arquivo GDScript. Use após write_file para manter o LSP sincronizado. Pré-condições: LSP conectado.
[ ] `godot_class_ref` | fase=CORE+IDEIA | Consulta metodos, propriedades, sinais, enums e constantes nativos do Godot via ClassDB (extension_api.json). Cobre APENAS classes nativas do engine; 
[ ] `list_valid_node_types` | fase=DESIGN | Lista todos os tipos de nó que podem ser usados em cenas (classes que herdam de Node). Use para descobrir quais tipos de nó existem no Godot 4.7. Quan
[R] `localization_manage` | fase=ORFA | 
[ ] `onboarding_check_first_experience` | fase=ORFA | Verifica qualidade da primeira experiencia do jogador (FTUE). Avalia clareza do tutorial, tempo ate primeira acao, complexidade inicial, frustracao po
[ ] `query_classdb` | fase=DESIGN | Consulta informações COMPLETAS de uma classe na ClassDB do Godot com PAGINAÇÃO, FILTROS e DETALHES. Retorna propriedades (com tipo, descrição, default
[ ] `resource_dependency_graph` | fase=DESIGN | Grafo de dependencias de recursos.
[ ] `runtime_list_signals` | fase=POLIMENTO | Lista todos os sinais definidos e emitidos num script GDScript. Quando usar: para inspecionar a API de sinais de um script. Pré-condições: script .gd 
[ ] `runtime_watch_signal` | fase=PROTOTIPO | Gera código para monitorar (watch) um sinal durante runtime com contagem e duração. Quando usar: para debugar frequência de sinais (ex: quantas vezes 
[ ] `search_classdb` | fase=DESIGN | 🔍 Busca classes na ClassDB do Godot por nome PARCIAL. Diferente de query_classdb (que exige nome exato), esta tool faz busca fuzzy: 'Body' encontra Ch
[ ] `telemetry_get_funnel` | fase=ORFA | Gera analise de funil (funnel analysis) dos eventos de telemetria. Mostra taxas de conversao entre etapas do jogo. Use para identificar onde jogadores
[ ] `telemetry_heatmap` | fase=ORFA | Gera mapa de calor (heatmap) de eventos de jogo. Mostra onde jogadores morrem, coletam itens ou encontram bosses. Use para balanceamento de nivel e po
[ ] `telemetry_session_summary` | fase=ORFA | Resumo da sessao de jogo: tempo total, eventos, mortes, kills, itens. Use para analise pos-jogo ou debug de balanceamento. Exemplo: {'session_id': 'se
[ ] `telemetry_track_event` | fase=ORFA | Registra evento de telemetria COM opt-in explicito do jogador. Suporta 19 tipos de eventos: session, level, enemy, item, boss, menu, etc. Dados armaze
[ ] `validate_achievement_config` | fase=ORFA | Valida configuracao de conquistas: IDs duplicados, nomes vazios, icones de conquista faltantes, requisitos nao atingiveis. Use antes de publicar para 
[ ] `validate_mod_compatibility` | fase=ORFA | Valida compatibilidade entre mods e jogo base. Verifica versao, dependencias, conflitos de arquivos e scripts de entrada. Use antes de carregar mods n
[ ] `validate_project_refs` | fase=CORE+DESIGN | Valida TODAS as referencias cruzadas no projeto Godot: ext_resource, sub_resource, nodes (script/textura/mesh), preload/load/ResourceLoader.load. NAO 
[R] `vision_manage` | fase=POLIMENTO | 

### 2.5 orchestration (48 tools)

[ ] `advance_milestone` | fase=IDEIA | Conclui um milestone. Sem ID, avanca o proximo pendente automaticamente. GRATIS.
[ ] `advance_phase` | fase=CORE+IDEIA | Avanca o projeto para a proxima fase, SE o criterio da fase atual foi cumprido. Use force=true so com motivo explicito. GRATIS.
[ ] `bootstrap_godot_mcp` | fase=CORE+IDEIA | 🚀 BOOTSTRAP AUTOMÁTICO: conecta VS Code → MCP → Godot em UMA chamada. Substitui 12+ passos manuais (validar, configurar, abrir Godot, esperar LSP, esp
[ ] `capture_proof` | fase=CORE+IDEIA | Coleta MECANICAMENTE a evidência de uma tarefa concluída e grava num arquivo assinado por hash SHA-256. NENHUM texto vem da IA — tudo é output literal
[ ] `catalog_search` | fase=ORFA | Busca ferramentas por linguagem natural (português ou inglês). Use para DESCOBRIR qual tool resolve seu problema. Ex: {'query': 'criar cena'} → retorn
[ ] `circuit_breaker_status` | fase=POLIMENTO | Status dos circuit breakers das APIs externas (FLUX, Replicate, Edge TTS). Use para verificar se alguma API está temporariamente bloqueada.
[ ] `configure_export_preset` | fase=PRONTO_PARA_LANCAR | Configura um preset de exportacao (Windows, Linux, macOS, Web, Android). Use antes de build_export para definir nome do app, versao, icone e empresa. 
[ ] `configure_security` | fase=POLIMENTO | Configura token de seguranca para o addon MCP.
[ ] `create_milestone_plan` | fase=IDEIA | Cria um plano de milestones (roteiro) baseado no genero e ideia do jogo. Usa gdd_generate() + estimate_game_scope() para gerar milestones distribuidos
[ ] `deploy_itch` | fase=PRONTO_PARA_LANCAR | Exporta e envia o jogo para itch.io via butler CLI. Suporta Windows, Linux, Web, macOS, Android. GRATIS.
[ ] `describe_tool` | fase=ORFA | Retorna o schema COMPLETO de uma ferramenta específica: descrição, parâmetros, hints (readOnly, destructive, idempotent, openWorld) e categoria de ope
[ ] `dump_mcp_state` | fase=CORE+IDEIA | Captura snapshot completo do estado do MCP: config, tool counts, caches, imports, git. Util para debugging e comparacao entre maquinas. NAO requer God
[ ] `gdd_generate` | fase=IDEIA | Gera Game Design Document (GDD) completo a partir de uma ideia. Suporta: tower_defense, platformer, rpg, shooter, puzzle, roguelike. Niveis de detalhe
[ ] `generate_ci_snippet` | fase=POLIMENTO | Gera GitHub Actions / GitLab CI para export.
[ ] `get_audit_log` | fase=POLIMENTO | Historico de auditoria das acoes da IA.
[ ] `get_audit_replay` | fase=POLIMENTO | Replay do historico de auditoria.
[ ] `get_current_phase` | fase=CORE+IDEIA | Mostra em que fase do projeto o time esta (IDEIA/DESIGN/PROTOTIPO/CONTEUDO/POLIMENTO/PRONTO_PARA_LANCAR) e o que falta para avancar. GRATIS.
[ ] `get_milestone_plan` | fase=IDEIA | Mostra o plano completo de milestones + progresso (total, concluidos, pendentes, %). GRATIS.
[ ] `get_next_step` | fase=CORE | Retorna o PROXIMO PASSO OBRIGATORIO da sessao: fase atual, blockers, criterio para avancar, e acao sugerida. Inclui why_now (justificativa), do_not_do
[ ] `get_phase_history` | fase=CORE+IDEIA | Mostra o historico de mudancas de fase do projeto. GRATIS.
[ ] `get_project_brief` | fase=IDEIA | Retorna o project brief atual. Se nunca foi configurado, retorna brief=null e configured=False. Use para consultar as caracteristicas do projeto antes
[ ] `get_vibe_context` | fase=POLIMENTO | Retorna contexto atual do Vibe Coding Mode.
[ ] `godot` | fase=CORE | 🎯 INTENT ROUTER — A MELHOR FERRAMENTA DO MCP. Descreva o que você quer fazer em linguagem natural (PT-BR ou EN) e o sistema automaticamente encontra e
[ ] `health_check` | fase=CORE+IDEIA | Verifica a saude de todos os componentes do MCP: config.json, Godot, ClassDB, templates, projeto ativo. Use no inicio de sessoes para diagnosticar pro
[ ] `install_mcp_addon` | fase=IDEIA | Instala o addon MCP no projeto Godot ativo e ativa o plugin do editor. O QUE FAZ: copia os arquivos do addon (mcp_addon.gd, plugin.cfg) para addons/mc
[ ] `invoke_by_name` | fase=ORFA | Invoca uma ferramenta pelo nome, passando os argumentos como dict. RESPEITA todos os gates (fase, session, kill switch, governador). Use como alternat
[ ] `ping` | fase=CORE+IDEIA | Verifica se o servidor godot-mcp-agent está funcional e conectado. Use esta tool no início de cada sessão para confirmar que o MCP está vivo. Quando u
[ ] `project_progress` | fase=CORE | Termometro visual do milestone atual: barra de progresso ASCII, percentual, mensagem motivacional e proximo milestone pendente. Use para ver 'quanto f
[ ] `release_checklist` | fase=PRONTO_PARA_LANCAR | Verifica se o projeto esta pronto para lancamento (nota 0-10): project.godot, main scene, scripts, assets, audio, export presets, gitignore, readme, l
[ ] `remote_balance_config` | fase=ORFA | Gerencia configuracao de balance remoto para ajustes pos-lancamento. Permite exportar, validar ou gerar template de balance JSON. Atualizavel sem patc
[ ] `resume_session` | fase=CORE | Recuperacao de sessao: le o estado persistente do projeto (fase, milestone, roadmap de fatias) e devolve um resumo unificado de onde voce parou + qual
[R] `safety_manage` | fase=CORE+IDEIA | 
[ ] `security_status` | fase=POLIMENTO | Verifica configuracao de seguranca atual.
[ ] `self_test` | fase=CORE+IDEIA | Executa uma suite de testes internos do MCP: ping, ClassDB, godot_parser, jinja2, Pillow. Use para verificar se todas as dependencias estao funcionais
[ ] `set_auto_dismiss` | fase=POLIMENTO | Liga/desliga o fechamento automatico de dialogos modais durante testes automatizados. Use antes de run_stress_test. Pre-condicoes: jogo rodando via go
[ ] `set_project_brief` | fase=IDEIA | Define ou sobrescreve o project brief (genero, estilo de arte, tom, plataforma). Use no inicio do projeto para configurar caracteristicas fundamentais
[ ] `set_safety_policy` | fase=POLIMENTO | Configura politica de seguranca (allowlist/blocklist).
[ ] `setup_mcp_config` | fase=IDEIA | Gera arquivo de configuracao MCP para VS Code Copilot, Claude ou Cursor.
[ ] `tool_catalog` | fase=CORE+IDEIA | Catalogo de tools por grupo. Ex: {'query':'scene','group':'core'}.
[ ] `tool_groups` | fase=CORE+IDEIA | Gerencia grupos dinamicos de tools. Ex: {'action':'activate','group':'art'}.
[ ] `update_project_brief` | fase=IDEIA | Atualiza campos especificos do project brief sem sobrescrever os demais. Use para ajustar uma caracteristica sem redefinir o brief inteiro. Nunca exig
[ ] `validate_godot_version` | fase=IDEIA | Verifica se a versão do Godot instalada é 4.7.x. Use no início da primeira sessão com um novo projeto, ou quando suspeitar que o Godot foi atualizado.
[ ] `validate_mcp_environment` | fase=IDEIA | Verifica se o ambiente MCP esta pronto: Python, dependencias, server.py.
[ ] `validate_mcp_registry` | fase=IDEIA | Ferramenta de diagnóstico: valida a consistência entre as 3 fontes de verdade do registro de tools (definições Tool(), handlers, e TOOLSETS/PHASE_TOOL
[ ] `verify_proof` | fase=CORE+IDEIA | Verifica se uma prova é válida E se corresponde ao estado ATUAL do código (ou seja: se o código não mudou depois que a prova foi coletada). Use para v
[ ] `vibe_coding_mode` | fase=POLIMENTO | Ativa/desativa Vibe Coding Mode. Foco automatico na cena configurada.
[ ] `workflow_handoff` | fase=POLIMENTO | Prepara resumo para proxima sessao. Use no FINAL de cada sessao.
[ ] `workflow_snapshot` | fase=POLIMENTO | Salva snapshot do estado atual do projeto no workflow log. Use ANTES de operações grandes para ter ponto de restauração.

## 3. PHASE_TOOLSETS — CURADORIA POR FASE

### 3.0 CORE (31 tools — sempre visiveis)

- `advance_phase`
- `bootstrap_godot_mcp`
- `capture_proof`
- `create_entities`
- `create_entity`
- `dump_mcp_state`
- `file_manage`
- `find_usages`
- `get_current_phase`
- `get_next_step`
- `get_phase_history`
- `godot`
- `godot_class_ref`
- `health_check`
- `node_manage`
- `ping`
- `project_manage`
- `project_progress`
- `project_status`
- `read_file`
- `resume_session`
- `safe_write_gdscript`
- `safety_manage`
- `scene_manage`
- `script_manage`
- `self_test`
- `tool_catalog`
- `tool_groups`
- `validate_project_refs`
- `verify_proof`
- `write_file`

### 3.1 IDEIA (36 + 31 CORE = 67 visiveis)

- `advance_milestone`
- `advance_phase`
- `analysis_manage`
- `audit_autoloads`
- `audit_input_map`
- `audit_save_compatibility`
- `audit_scene_reachability`
- `audit_uid_consistency`
- `bootstrap_godot_mcp`
- `capture_proof`
- `create_milestone_plan`
- `dump_mcp_state`
- `gdd_generate`
- `get_current_phase`
- `get_milestone_plan`
- `get_phase_history`
- `get_project_brief`
- `godot_class_ref`
- `health_check`
- `install_mcp_addon`
- `ping`
- `project_manage`
- `project_status`
- `read_file`
- `safety_manage`
- `self_test`
- `set_project_brief`
- `setup_mcp_config`
- `tool_catalog`
- `tool_groups`
- `update_project_brief`
- `validate_godot_version`
- `validate_mcp_environment`
- `validate_mcp_registry`
- `verify_proof`
- `write_file`

### 3.2 DESIGN (41 + 31 CORE = 72 visiveis)

- `analyze_signal_flow`
- `behavior_tree_generate`
- `behavior_tree_list_templates`
- `config_manage`
- `create_entities`
- `create_entity`
- `csharp_generate_script`
- `csharp_scaffold_project`
- `file_manage`
- `find_usages`
- `gdscript_definition`
- `gdscript_diagnostics`
- `gdscript_hover`
- `gdscript_lsp_connect`
- `gdscript_lsp_disconnect`
- `gdscript_references`
- `gdscript_rename`
- `gdscript_symbols`
- `gdscript_sync_file`
- `generate_project_structure`
- `list_valid_node_types`
- `node_manage`
- `project_map`
- `query_classdb`
- `render_get_settings`
- `resource_dependency_graph`
- `safe_write_gdscript`
- `scene_manage`
- `script_manage`
- `search_classdb`
- `skeleton_get_bone_pose`
- `skeleton_get_info`
- `skeleton_list_bones`
- `ui_configure_focus_nav`
- `ui_create_tab_with_content`
- `ui_create_widget`
- `ui_manage`
- `ui_set_anchor_preset`
- `ui_set_tooltip`
- `validate_project_refs`
- `world_describe`

### 3.3 PROTOTIPO (69 + 31 CORE = 100 visiveis)

- `add_nodes_batch`
- `analyze_signal_flow`
- `anim_manage`
- `apply_game_art`
- `asset_manage`
- `audio_manage`
- `batch_atomic_edit`
- `camera_configure_attributes`
- `camera_manage`
- `capture_game_screenshot`
- `capture_runtime_errors`
- `create_animation_tree`
- `create_light_2d`
- `csg_create_node`
- `effect_probe`
- `execute_gdscript_runtime`
- `freeze_game_clock`
- `game_bridge_manage`
- `generate_3d_asset`
- `generate_3d_placeholder`
- `generate_audio_sfx`
- `generate_game_art`
- `generate_game_art_flux`
- `get_runtime_state_digest`
- `gi_create_node`
- `godot_custom_command`
- `godot_exec`
- `godot_keep_alive`
- `godot_list_custom_commands`
- `godot_run_project`
- `godot_runtime_info`
- `godot_screenshot`
- `godot_stop_project`
- `godot_wait_for_bridge`
- `inject_input_event`
- `load_scene_async`
- `multimesh_create_instance`
- `physics_configure_body`
- `physics_create_joint`
- `physics_manage`
- `physics_query_area_overlap`
- `physics_raycast_query`
- `raycast_manage`
- `record_gameplay_gif`
- `runtime_connect_signal`
- `runtime_disconnect_signal`
- `runtime_emit_signal`
- `runtime_manage`
- `runtime_watch_signal`
- `scene_fx_create_node`
- `set_properties_batch`
- `shader_generate`
- `shader_list_templates`
- `shader_manage`
- `simulate_input_sequence`
- `skeleton_create_bone`
- `skeleton_create_ik_chain`
- `skeleton_set_bone_pose`
- `sky_create_procedural`
- `start_recording`
- `step_game_time`
- `step_until`
- `stop_recording`
- `take_screenshot`
- `unfreeze_game_clock`
- `vfx_manage`
- `watch_signal`
- `watch_state_collect`
- `watch_state_start`

### 3.4 CONTEUDO (43 + 31 CORE = 74 visiveis)

- `add_parallax_layer`
- `add_translation_string`
- `balance_analyze`
- `create_asset_manifest`
- `create_bullet_template`
- `create_gun_system`
- `create_parallax_background`
- `create_path_2d`
- `create_patrol_route`
- `create_spritesheet`
- `d3_manage`
- `dialogue_manage`
- `download_asset`
- `dps_calculator`
- `dungeon_generate`
- `find_unused_resources`
- `gamestate_manage`
- `generate_dungeon_rooms`
- `generate_voice`
- `import_3d_model`
- `import_asset_manifest`
- `import_downloaded_asset`
- `inventory_manage`
- `juice_apply`
- `juice_list_presets`
- `loot_table_generate`
- `marketplace_download`
- `marketplace_search`
- `navigation_manage`
- `network_configure_dedicated_server`
- `network_create_lobby`
- `network_create_rpc`
- `network_create_websocket`
- `network_setup_multiplayer`
- `optimize_sprite`
- `remove_background`
- `render_set_antialiasing`
- `render_set_quality`
- `render_set_scaling`
- `setup_localization`
- `terrain_generate`
- `tilemap_manage`
- `wave_generate`

### 3.5 POLIMENTO (31 + 31 CORE = 62 visiveis)

- `auto_screenshot`
- `circuit_breaker_status`
- `configure_security`
- `debug_manage`
- `debugger_get_stack`
- `debugger_get_variables`
- `debugger_set_breakpoint`
- `debugger_status`
- `debugger_step`
- `estimate_tool_tokens`
- `find_unused_resources`
- `generate_ci_snippet`
- `get_audit_log`
- `get_audit_replay`
- `get_vibe_context`
- `profile_frame`
- `profile_memory`
- `regression_test`
- `run_gut_tests`
- `run_scripted_tests`
- `run_verification_pipeline`
- `runtime_list_signals`
- `security_status`
- `set_auto_dismiss`
- `set_safety_policy`
- `smoke_test`
- `test_manage`
- `vibe_coding_mode`
- `vision_manage`
- `workflow_handoff`
- `workflow_snapshot`

### 3.6 PRONTO_PARA_LANCAR (19 + 31 CORE = 50 visiveis)

- `addon_batch_edit`
- `addon_connect`
- `addon_create_node`
- `addon_delete_node`
- `addon_disconnect`
- `addon_duplicate_node`
- `addon_get_scene_tree`
- `addon_is_available`
- `addon_ping`
- `addon_reparent_node`
- `addon_set_property`
- `addon_take_screenshot`
- `build_csharp`
- `configure_export_preset`
- `csharp_build_project`
- `deploy_itch`
- `export_manage`
- `read_console_output`
- `release_checklist`

## 4. TOOLS ORFAS DE FASE

**75 tools (26% do total)** sem fase.
NUNCA visiveis por curadoria de fase (mas ainda chamaveis).

[ ] `accessibility_add_subtitles` | ns=project
[ ] `accessibility_apply_colorblind_filter` | ns=project
[ ] `accessibility_audit_scene` | ns=analysis
[ ] `accessibility_certification_checklist` | ns=analysis
[ ] `accessibility_remap_controls` | ns=project
[ ] `adaptive_difficulty_adjust` | ns=analysis
[ ] `add_raycast_2d` | ns=project
[ ] `add_shapecast_2d` | ns=project
[ ] `assert_node_exists` | ns=runtime
[R] `budget_manage` | ns=???
[ ] `capsule_generate_store_image` | ns=assets
[ ] `catalog_search` | ns=orchestration
[ ] `cloud_save_configure` | ns=project
[R] `community_manage` | ns=???
[R] `complexity_gate_manage` | ns=???
[ ] `configure_particles_2d` | ns=assets
[ ] `configure_standard_material_3d` | ns=assets
[ ] `create_achievement_system` | ns=project
[ ] `create_joint_2d` | ns=project
[ ] `create_light_3d` | ns=project
[ ] `create_navigation_agent_2d` | ns=project
[ ] `create_navigation_region_2d` | ns=project
[ ] `create_particles_2d` | ns=assets
[ ] `create_particles_3d` | ns=assets
[ ] `cutscene_add_camera_shot` | ns=project
[ ] `cutscene_add_dialogue_event` | ns=project
[ ] `cutscene_create_timeline` | ns=project
[ ] `describe_tool` | ns=orchestration
[ ] `dialogue_generate_npc_lines` | ns=project
[ ] `dialogue_generate_personality` | ns=project
[ ] `edit_shader` | ns=assets
[R] `fun_report_manage` | ns=???
[ ] `game_await_signal` | ns=runtime
[ ] `game_call_method` | ns=runtime
[ ] `game_find_nodes_by_class` | ns=runtime
[ ] `game_get_camera` | ns=runtime
[ ] `game_http_request` | ns=runtime
[ ] `game_input_state` | ns=runtime
[ ] `game_multiplayer` | ns=runtime
[ ] `game_pause` | ns=runtime
[ ] `game_performance` | ns=runtime
[ ] `game_play_animation` | ns=runtime
[ ] `game_raycast` | ns=runtime
[ ] `game_serialize_state` | ns=runtime
[ ] `game_spawn_node` | ns=runtime
[ ] `game_window` | ns=runtime
[ ] `generate_shader_2d` | ns=assets
[ ] `get_shader_params` | ns=assets
[ ] `invoke_by_name` | ns=orchestration
[R] `mcp_telemetry_manage` | ns=???
[ ] `mod_manifest_generate` | ns=project
[ ] `onboarding_check_first_experience` | ns=analysis
[ ] `onboarding_create_guided_tour` | ns=project
[ ] `onboarding_create_tutorial_step` | ns=project
[R] `playtest_manage` | ns=runtime
[R] `polish_manage` | ns=???
[R] `publish_manage` | ns=???
[ ] `quest_generate` | ns=project
[R] `quickstart_manage` | ns=???
[ ] `read_shader` | ns=assets
[ ] `remote_balance_config` | ns=orchestration
[R] `reviewer_manage` | ns=???
[ ] `run_stress_test` | ns=runtime
[R] `scope_manage` | ns=???
[ ] `setup_camera_2d` | ns=project
[R] `teacher_manage` | ns=???
[ ] `telemetry_get_funnel` | ns=analysis
[ ] `telemetry_heatmap` | ns=analysis
[ ] `telemetry_session_summary` | ns=analysis
[ ] `telemetry_track_event` | ns=analysis
[ ] `trailer_capture_clip` | ns=assets
[ ] `trailer_render_sequence` | ns=assets
[ ] `validate_achievement_config` | ns=analysis
[ ] `validate_mod_compatibility` | ns=analysis
[R] `version_history_manage` | ns=???

## 5. FAMILIAS POR PREFIXO — CANDIDATAS A ROLLUP

Tools agrupadas por prefixo comum. [R]=ja tem rollup, [ ]=oportunidade.

### 🔴 OPORTUNIDADE: `gdscript_*` (6 tools)

    `gdscript_definition`
    `gdscript_diagnostics`
    `gdscript_hover`
    `gdscript_references`
    `gdscript_rename`
    `gdscript_symbols`

### 🔴 OPORTUNIDADE: `game_*` (5 tools)

    `game_multiplayer`
    `game_pause`
    `game_performance`
    `game_raycast`
    `game_window`

### 🔴 OPORTUNIDADE: `godot_*` (3 tools)

    `godot`
    `godot_exec`
    `godot_screenshot`

### 🔴 OPORTUNIDADE: `project_*` (3 tools)

    `project_map`
    `project_progress`
    `project_status`

### 🔴 OPORTUNIDADE: `create_*` (3 tools)

    `create_entities`
    `create_entity`
    `create_spritesheet`

### 🔴 OPORTUNIDADE: `addon_*` (3 tools)

    `addon_connect`
    `addon_disconnect`
    `addon_ping`

### 🔴 OPORTUNIDADE: `network_create_*` (3 tools)

    `network_create_lobby`
    `network_create_rpc`
    `network_create_websocket`

### 🔴 OPORTUNIDADE: `render_set_*` (3 tools)

    `render_set_antialiasing`
    `render_set_quality`
    `render_set_scaling`

### 🔴 OPORTUNIDADE: `validate_mcp_*` (2 tools)

    `validate_mcp_environment`
    `validate_mcp_registry`

### 🔴 OPORTUNIDADE: `read_*` (2 tools)

    `read_file`
    `read_shader`

### 🔴 OPORTUNIDADE: `workflow_*` (2 tools)

    `workflow_handoff`
    `workflow_snapshot`

### 🔴 OPORTUNIDADE: `get_audit_*` (2 tools)

    `get_audit_log`
    `get_audit_replay`

### 🔴 OPORTUNIDADE: `tool_*` (2 tools)

    `tool_catalog`
    `tool_groups`

### 🔴 OPORTUNIDADE: `debugger_*` (2 tools)

    `debugger_status`
    `debugger_step`

### 🔴 OPORTUNIDADE: `debugger_get_*` (2 tools)

    `debugger_get_stack`
    `debugger_get_variables`

### 🔴 OPORTUNIDADE: `generate_game_*` (2 tools)

    `generate_game_art`
    `generate_game_art_flux`

### 🔴 OPORTUNIDADE: `create_particles_*` (2 tools)

    `create_particles_2d`
    `create_particles_3d`

### 🔴 OPORTUNIDADE: `create_light_*` (2 tools)

    `create_light_2d`
    `create_light_3d`

### 🔴 OPORTUNIDADE: `create_navigation_*` (2 tools)

    `create_navigation_agent_2d`
    `create_navigation_region_2d`

### 🔴 OPORTUNIDADE: `gdscript_lsp_*` (2 tools)

    `gdscript_lsp_connect`
    `gdscript_lsp_disconnect`

### 🔴 OPORTUNIDADE: `watch_state_*` (2 tools)

    `watch_state_collect`
    `watch_state_start`

### 🔴 OPORTUNIDADE: `behavior_tree_*` (2 tools)

    `behavior_tree_generate`
    `behavior_tree_list_templates`

### 🔴 OPORTUNIDADE: `profile_*` (2 tools)

    `profile_frame`
    `profile_memory`

### 🔴 OPORTUNIDADE: `generate_3d_*` (2 tools)

    `generate_3d_asset`
    `generate_3d_placeholder`

### 🔴 OPORTUNIDADE: `advance_*` (2 tools)

    `advance_milestone`
    `advance_phase`

### 🔴 OPORTUNIDADE: `marketplace_*` (2 tools)

    `marketplace_download`
    `marketplace_search`

### 🔴 OPORTUNIDADE: `cutscene_add_*` (2 tools)

    `cutscene_add_camera_shot`
    `cutscene_add_dialogue_event`

### 🔴 OPORTUNIDADE: `dialogue_generate_*` (2 tools)

    `dialogue_generate_npc_lines`
    `dialogue_generate_personality`

### 🔴 OPORTUNIDADE: `onboarding_create_*` (2 tools)

    `onboarding_create_guided_tour`
    `onboarding_create_tutorial_step`

### 🔴 OPORTUNIDADE: `skeleton_get_*` (2 tools)

    `skeleton_get_bone_pose`
    `skeleton_get_info`

### 🔴 OPORTUNIDADE: `skeleton_create_*` (2 tools)

    `skeleton_create_bone`
    `skeleton_create_ik_chain`

### 🔴 OPORTUNIDADE: `ui_create_*` (2 tools)

    `ui_create_tab_with_content`
    `ui_create_widget`

### 🔴 OPORTUNIDADE: `ui_set_*` (2 tools)

    `ui_set_anchor_preset`
    `ui_set_tooltip`

## 6. METRICAS FINAIS

| Metrica | Valor |
|---|---|
| Total tools registradas | 287 |
| Em TOOLSETS | 287 (100%) |
| Em PHASE_TOOLSETS | 212 (74%) |
| Orfas de fase | 75 (26%) |
| Rollups (_manage) | 13 (5%) |
| CORE sempre visivel | 31 |
| Maior fase | PROTOTIPO: 100 tools |
| Menor fase | PRONTO_PARA_LANCAR: 50 tools |
| Familias com 2+ tools | 33 |
| Familias COM rollup | 0 |
| Familias SEM rollup (oportunidade) | 33 |

## 7. PERGUNTAS PARA O CLAUDE (AUDITOR)

1. Quais familias devem ser consolidadas em rollups PRIMEIRO? Priorize.
2. As 75 orfas devem ser atribuidas a fases ou sao auxiliares legitimas?
3. PROTOTIPO com 97 tools visiveis e aceitavel? (DeepSeek V4 Pro: 200K tokens)
4. Deveriamos implementar paginacao no tools/list (previsto na spec MCP)?
5. game_* + addon_* + godot_* deveriam ser unificados?
6. O sistema de 4 camadas de curadoria e excessivo?
7. Qual o numero ideal de tools? 39 (IvanMurzak) ou 287 (nos)?
8. Quais tools podem ser REMOVIDAS sem perda real de funcionalidade?
9. A estrutura atual (5 namespaces × 6 fases × 28 CORE) esta correta ou deveria ser:
   a) namespaces DENTRO de fases?
   b) fases DENTRO de namespaces?
   c) independentes como hoje?
10. Toda tool atomica (create_*, get_*, set_*) deveria ser op de rollup ou existem excecoes validas?