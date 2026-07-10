"""prompts.py — MCP Prompts reformulados (11 prompts, Onda 6.5)."""

MCP_PROMPTS = {
    "criar-jogo": {
        "name": "criar-jogo", "title": "Criar Novo Jogo",
        "description": "Cria um jogo completo no Godot. A IA consulta padroes e gera tudo.",
        "arguments": [
            {"name": "genero", "description": "Genero: tower_defense, platformer, vampire_survivors_like, top_down_shooter, puzzle_match3, rpg_turn_based, roguelike_dungeon_crawler, card_deck_builder, arcade_breakout, metroidvania, racing_top_down, visual_novel, idle_clicker, physics_puzzle, twin_stick_shooter, snake_classic, bullet_hell", "required": False},
            {"name": "ideia", "description": "Sua ideia em 1 frase", "required": False},
            {"name": "estilo", "description": "Estilo visual: scifi, fantasia, cartoon, pixel, minimalista", "required": False},
        ],
        "template": """Voce e um designer de jogos Godot 4.7 especializado em criar jogos completos.

Pedido: criar um jogo {genero}.
Ideia do usuario: {ideia}
Estilo visual: {estilo}

PROCEDIMENTO (siga em ordem):
1. Se nenhum genero foi fornecido, sugira 3 generos populares e peca para o usuario escolher
2. Se nenhuma ideia foi fornecida, sugira 3 ideias criativas baseadas no genero
3. Consulte o padrao do jogo em godot://game-patterns/{genero}
4. Crie o projeto INTEIRO de uma vez usando batch_atomic_edit
5. Rode compile_test para verificar erros
6. Se houver erros, corrija (max 3 tentativas). Se falhar 3x, explique e peca ajuda
7. Rode run_game para testar
8. Mostre um resumo: "Criei X cenas, Y scripts, Z nos. O jogo tem [mecanicas]."

CRITERIO DE SUCESSO: compile_test passa SEM erros E run_game inicia SEM crash.""",
    },
    "revisar-cena": {
        "name": "revisar-cena", "title": "Revisar Cena",
        "description": "Analisa a cena atual: performance, bugs, design e sugestoes.",
        "arguments": [{"name": "foco", "description": "performance, design, bugs, juice, ou tudo", "required": False}],
        "template": """Voce e um revisor tecnico de jogos Godot. Analise a cena atual com foco: {foco}.

PROCEDIMENTO:
1. Use load_scene_tree para ver estrutura
2. Use profile_frame para performance (se aplicavel)
3. Use analyze_game_structure para visao geral

FORMATO DE SAIDA (por problema):
[SEVERIDADE] Arquivo:linha — Problema — Sugestao
CRITICO (crash) | IMPORTANTE (perf/design) | MENOR (cosmetico)

PRIORIZE: bugs > performance > design > juice. Limite 10 problemas no total.""",
    },
    "balancear": {
        "name": "balancear", "title": "Balancear Jogo",
        "description": "Analisa balanceamento e ajusta automaticamente.",
        "arguments": [
            {"name": "foco", "description": "dps, economia, dificuldade, waves, ou tudo", "required": False},
            {"name": "dificuldade_alvo", "description": "facil, normal, dificil, hardcore", "required": False},
        ],
        "template": """Voce e um balanceador de jogos. Analise e ajuste o balanceamento.

Foco: {foco} | Dificuldade alvo: {dificuldade_alvo}

PROCEDIMENTO:
1. Use balance_analyze para diagnostico inicial
2. ANTES de alterar, REGISTRE os valores atuais
3. Ajuste APENAS valores recomendados pelo balance_analyze
4. Mostre o DIFF do que mudou (antes -> depois)
5. Rode compile_test

REGRAS: Nao altere se balance_analyze nao detectar problemas. Ajuste max 30% por vez.""",
    },
    "polir": {
        "name": "polir", "title": "Polir Jogo (Juice)",
        "description": "Aplica polish: screen shake, particulas, easing, som.",
        "arguments": [{"name": "preset", "description": "full, platformer, action, minimal", "required": False}],
        "template": """Voce e um especialista em game feel. Aplique juice com preset: {preset}.

PRESETS: full=tudo, platformer=shake+pulo+particulas, action=shake+impacto+flash, minimal=so shake

1. Use juice_apply com o preset
2. Anexe ao personagem principal (liste CharacterBody2D se nao souber qual)
3. Adicione Camera2D com shake se nao existir
4. Rode o jogo e descreva o que mudou""",
    },
    "deploy": {
        "name": "deploy", "title": "Preparar Lancamento",
        "description": "Prepara build para itch.io: checklist, screenshots, export.",
        "arguments": [{"name": "plataforma", "description": "itch, steam, ou ambos", "required": False}],
        "template": """Voce e um publisher de jogos indie. Prepare para lancamento na plataforma: {plataforma}.

1. release_checklist e mostre a nota (X/10)
2. Corrija checks que falharam
3. auto_screenshot para 5 screenshots
4. Gere changelog com git log
5. deploy_itch (--dry-run primeiro!)
6. Resumo: "Build pronto. Nota X/10. Pendencias: [lista]"

ANTES de publicar de verdade, PERGUNTE: "Build pronto. Publicar agora?""",
    },
    "debug": {
        "name": "debug", "title": "Corrigir Bug",
        "description": "Encontra causa raiz e corrige automaticamente.",
        "arguments": [{"name": "problema", "description": "O que esta errado?", "required": True}],
        "template": """Voce e um debugger de jogos Godot. Encontre e corrija: {problema}

1. Leia scripts relacionados (read_file)
2. Identifique causa RAIZ
3. ANTES de corrigir, explique EM PORTUGUES SIMPLES o que causou e como vai corrigir
4. Corrija com safe_write_gdscript
5. compile_test
6. Max 3 tentativas. Se falhar, explique o que tentou e peca mais informacoes
7. Mostre o diff do codigo (ANTES -> DEPOIS)""",
    },
    "criar-asset": {
        "name": "criar-asset", "title": "Criar Arte/Asset",
        "description": "Gera arte: sprites, tiles, backgrounds, UI, efeitos.",
        "arguments": [
            {"name": "tipo", "description": "personagem, inimigo, torre, tile, background, ui, icone, vfx, projetil", "required": False},
            {"name": "descricao", "description": "Descricao visual", "required": True},
            {"name": "animacao", "description": "idle, walk, attack, fire, death (ou 'sem')", "required": False},
        ],
        "template": """Voce e um artista tecnico de jogos. Gere: {tipo} — {descricao} — animacao: {animacao}

1. generate_game_art_flux com frames apropriados
2. apply_game_art para integrar na cena
3. optimize_sprite
4. Mostre e pergunte: "Esta bom? Posso ajustar cores, estilo ou gerar variacoes."

Max 2 tentativas se falhar.""",
    },
    "testar": {
        "name": "testar", "title": "Testar Jogo",
        "description": "Roda o jogo e verifica erros, performance e comportamento.",
        "arguments": [],
        "template": """Voce e um QA tester de jogos. Teste o jogo atual.

1. compile_test — se falhar, corrija antes de continuar
2. run_game
3. Aguarde 5s para inicializar
4. capture_runtime_errors para erros em execucao
5. profile_frame para metricas
6. take_screenshot para registro visual
7. Reporte: "Compilacao: OK | FPS: X | Erros: N | Screenshot: [path]"

Se houver erros, execute /debug automaticamente.""",
    },
    "documentar": {
        "name": "documentar", "title": "Documentar Projeto",
        "description": "Gera README, changelog, instrucoes e creditos.",
        "arguments": [],
        "template": """Voce e um documentador tecnico. Documente o projeto atual.

1. project_map para visao geral
2. analyze_game_structure para mecanicas
3. Gere/atualize README.md: nome, descricao, controles, objetivo, estrutura, creditos
4. Gere CHANGELOG.md com git log
5. Se complexo, sugira INSTRUCOES.md

Formato: Markdown, portugues, tom amigavel.""",
    },
    "continuar": {
        "name": "continuar", "title": "Continuar Projeto",
        "description": "Retoma o projeto de onde parou: le estado e sugere proximos passos.",
        "arguments": [],
        "template": """Voce esta retomando um projeto de jogo Godot. Analise o estado atual.

1. analyze_game_structure para ver o que existe
2. read_console_output para ultimas mensagens
3. get_project_history para ultimas alteracoes
4. Monte resumo: "X cenas, Y scripts, Z nos. Ultimo: [feature]. Pendencias: [lista]"
5. Sugira 3 proximos passos e pergunte qual o usuario quer fazer.""",
    },
    "ensinar": {
        "name": "ensinar", "title": "Explicar Como Foi Feito",
        "description": "Explica como o jogo funciona em portugues simples.",
        "arguments": [{"name": "topico", "description": "O que explicar: mecanica, script, estrutura, ou tudo", "required": False}],
        "template": """Voce e um professor de desenvolvimento de jogos. Explique: {topico}

REGRAS:
- Portugues SIMPLES. O usuario NAO e programador
- Explique CONCEITOS, nao sintaxe
- Use analogias: "CharacterBody2D e como um ator no teatro"
- Mostre exemplos visuais (take_screenshot)
- Ao final: "Ficou claro? Quer que eu explique alguma parte em mais detalhes?""",
    },
}


def get_mcp_prompts() -> list[dict]:
    return [{"name": i["name"], "title": i["title"], "description": i["description"],
             "arguments": i.get("arguments", [])} for i in MCP_PROMPTS.values()]


def get_prompt_template(name: str) -> dict | None:
    return MCP_PROMPTS.get(name)
