"""friendly_errors — Traduz erros técnicos para PT-BR simples.

Usado pelo MCP server para transformar mensagens de erro técnicas
em explicações que um non-coder entende.

Formato canônico (3 partes):
  1. O que aconteceu (em português)
  2. O que isso significa para o jogo dele
  3. O que fazer agora
"""

# ══════════════════════════════════════════════════════════════════════
# Mapeamento de padrões de erro → mensagem amigável (formato 3 partes)
# ══════════════════════════════════════════════════════════════════════

FRIENDLY_MAP: dict[str, str] = {
    # ── Godot / Projeto ──────────────────────────────────────────
    "project.godot não encontrado": (
        "O projeto Godot não foi encontrado na pasta atual.\n"
        "Sem o projeto, o MCP não sabe onde criar cenas e scripts.\n"
        "Use 'create_project' para criar um novo ou 'set_active_project' para abrir um existente."
    ),
    "main scene não definida": (
        "O jogo não tem uma cena principal definida.\n"
        "Isso significa que o Godot não sabe qual cena abrir quando o jogo inicia — o jogo não roda.\n"
        "Use 'set_main_scene' para definir a cena que abre primeiro."
    ),
    "no main scene": (
        "O jogo não tem uma cena principal definida.\n"
        "Isso significa que o Godot não sabe qual cena abrir quando o jogo inicia — o jogo não roda.\n"
        "Use 'set_main_scene' para definir a cena que abre primeiro."
    ),

    # ── Arquivos ─────────────────────────────────────────────────
    "File not found": (
        "O arquivo que você tentou acessar não existe.\n"
        "O jogo depende desse arquivo para funcionar — sem ele, algo vai quebrar.\n"
        "Verifique se o caminho está correto ou crie o arquivo primeiro."
    ),
    "não encontrado": (
        "O que você está procurando não foi encontrado no projeto.\n"
        "Pode ser que esse elemento ainda não tenha sido criado.\n"
        "Crie o elemento primeiro e depois tente acessá-lo."
    ),
    "já existe": (
        "Já existe algo com esse nome no projeto.\n"
        "Godot não permite dois recursos com o mesmo nome na mesma pasta — isso causaria conflitos.\n"
        "Escolha outro nome ou remova o existente primeiro."
    ),

    # ── Cena / Nós ───────────────────────────────────────────────
    "Node not found": (
        "O elemento que você está tentando acessar não existe na cena atual.\n"
        "Isso significa que o script ou cena tenta usar algo que não está mais lá.\n"
        "Use 'load_scene_tree' para ver todos os elementos disponíveis na cena."
    ),
    "nó não encontrado": (
        "O elemento que você está tentando acessar não existe na cena atual.\n"
        "Isso significa que o script ou cena tenta usar algo que não está mais lá.\n"
        "Use 'add_node' para criar o elemento primeiro."
    ),
    "Invalid node type": (
        "O tipo de elemento que você pediu não existe no Godot 4.7.\n"
        "Isso geralmente é um erro de digitação no nome da classe.\n"
        "Use 'list_valid_node_types' para ver os tipos disponíveis."
    ),

    # ── GDScript ─────────────────────────────────────────────────
    "Parse Error": (
        "O código GDScript do jogo tem um erro de escrita (sintaxe).\n"
        "Isso impede o jogo de rodar — o Godot não consegue entender o script.\n"
        "Isso geralmente é um bug do MCP ao gerar código. Peça para a IA revisar e corrigir o script."
    ),
    "SCRIPT ERROR": (
        "O jogo encontrou um erro durante a execução.\n"
        "Isso acontece quando uma cena tenta acessar algo que foi removido ou nunca existiu.\n"
        "Use 'compile_test' para ver os erros exatos e corrija a referência quebrada."
    ),

    # ── Performance / Timeout ────────────────────────────────────
    "Timeout": (
        "A operação demorou muito e foi cancelada por segurança.\n"
        "Isso pode acontecer se o projeto estiver muito grande ou o Godot estiver sobrecarregado.\n"
        "Tente de novo. Se persistir, reinicie o Godot ou reduza o tamanho do projeto."
    ),
    "timeout": (
        "A operação demorou muito e foi cancelada por segurança.\n"
        "Isso pode acontecer se o projeto estiver muito grande ou o Godot estiver sobrecarregado.\n"
        "Tente de novo com um projeto menor ou reinicie o Godot."
    ),

    # ── Conexão ──────────────────────────────────────────────────
    "Connection refused": (
        "Não foi possível conectar ao editor do Godot.\n"
        "Sem essa conexão, o MCP não consegue comunicar com o editor para executar operações.\n"
        "Verifique se o Godot está aberto com o plugin MCP Addon ativo (Project → Project Settings → Plugins)."
    ),
    "Bridge offline": (
        "A ponte de comunicação com o Godot não está ativa.\n"
        "Sem a bridge, o MCP fica isolado — não consegue ler nem modificar o projeto.\n"
        "Abra o Godot e ative o plugin MCP Addon em Project → Project Settings → Plugins."
    ),

    # ── Export ───────────────────────────────────────────────────
    "Templates de exportação não instalados": (
        "Os templates de exportação do Godot não estão instalados.\n"
        "Sem eles, você não consegue exportar o jogo para Windows, Linux, Web ou mobile.\n"
        "No Godot, vá em Editor → Manage Export Templates → Download and Install."
    ),

    # ── Segurança ────────────────────────────────────────────────
    "Path traversal": (
        "Você tentou acessar uma pasta fora do projeto.\n"
        "Isso não é permitido por segurança — todas as operações devem ficar dentro da pasta do projeto.\n"
        "Mova o arquivo para dentro da pasta do projeto ou use um caminho relativo a ela."
    ),

    # ── Godot CLI / Runtime ─────────────────────────────────────
    "Can't run project": (
        "O Godot não conseguiu rodar o projeto.\n"
        "Isso geralmente acontece porque não há uma cena principal definida.\n"
        "Use 'set_main_scene' para definir a cena principal primeiro."
    ),
    "Invalid assignment of property": (
        "O jogo tentou atribuir um valor a uma propriedade que não existe mais.\n"
        "Isso acontece quando um nó foi removido da cena mas o script ainda tenta acessá-lo.\n"
        "Revise o script e remova as referências aos nós que não existem mais."
    ),
    "Failed loading resource": (
        "O Godot não conseguiu carregar um arquivo de recurso.\n"
        "Isso pode significar que o arquivo está corrompido ou em um formato incompatível.\n"
        "Tente recriar o arquivo com a IA ou restaure de um checkpoint anterior."
    ),
    "No such file": (
        "O arquivo que você tentou acessar não existe no projeto.\n"
        "O jogo depende desse arquivo — sem ele, vai quebrar em execução.\n"
        "Verifique o caminho ou crie o arquivo primeiro."
    ),

    # ── Rate limit / Geral ───────────────────────────────────────
    "Rate limit": (
        "Você está fazendo operações rápido demais e o sistema pediu uma pausa.\n"
        "Isso é uma proteção normal — sem ela, o MCP ou o Godot poderiam sobrecarregar.\n"
        "Aguarde alguns segundos e tente novamente."
    ),
    "Permission denied": (
        "Sem permissão para acessar este arquivo.\n"
        "Isso geralmente acontece quando outro programa (como o editor do Godot) está usando o arquivo.\n"
        "Feche outros programas que possam estar usando o arquivo e tente de novo."
    ),
    "already exists": (
        "Já existe algo com este nome no projeto.\n"
        "Godot não permite duplicatas — dois recursos com o mesmo nome causariam conflitos.\n"
        "Escolha um nome diferente para o novo recurso."
    ),
    "not a valid": (
        "O valor fornecido não é válido para esta operação.\n"
        "Isso significa que o formato ou tipo do valor não corresponde ao esperado.\n"
        "Verifique o formato e o tipo do valor e tente novamente."
    ),

    # ── Erros de sistema (governador, rate-limit, budget, etc.) ──
    "governor_blocked": (
        "O sistema de segurança do MCP bloqueou esta operação.\n"
        "Isso significa que o governador detectou um risco — loop, operação repetida, ou padrão suspeito.\n"
        "Aguarde um momento e tente novamente. Se o bloqueio persistir, peça ajuda ao humano."
    ),
    "editor_conflict": (
        "O editor do Godot tem alterações não salvas que conflitam com esta operação.\n"
        "Escrever por fora enquanto o editor tem mudanças pendentes pode corromper arquivos.\n"
        "Salve as alterações no editor do Godot (Ctrl+S) e tente novamente."
    ),
    "rate limit excedido": (
        "Você atingiu o limite de operações por minuto.\n"
        "Isso é uma proteção para evitar sobrecarga do sistema e custos excessivos.\n"
        "Aguarde o tempo indicado e tente novamente."
    ),
    "session gate": (
        "A sessão ainda não foi inicializada.\n"
        "Sem inicializar, o MCP não sabe em qual fase do projeto você está nem qual é o próximo passo.\n"
        "Chame 'get_next_step()' primeiro para ver a fase atual e o próximo passo obrigatório."
    ),
    "budget_exceeded": (
        "O orçamento de tokens desta sessão foi atingido.\n"
        "Isso significa que o custo estimado da sessão chegou ao limite configurado.\n"
        "Aumente o limite com 'budget_manage' ou revise o que já foi feito antes de continuar."
    ),
    "tool nao implementada": (
        "A ferramenta solicitada não está disponível.\n"
        "Isso pode significar que ela não existe ou não está liberada para a fase atual do projeto.\n"
        "Use 'tool_catalog' para ver as ferramentas disponíveis na fase atual."
    ),
    "erro interno": (
        "Ocorreu um erro inesperado no servidor MCP.\n"
        "Isso é um bug — não é culpa do seu projeto nem da sua ação.\n"
        "Reporte este erro para análise. Enquanto isso, tente a operação novamente."
    ),
}


def translate_error(message: str, tool_name: str = "") -> str:
    """Traduz uma mensagem de erro técnica para PT-BR amigável (formato 3 partes).

    Args:
        message: Mensagem de erro original.
        tool_name: Nome da ferramenta onde o erro ocorreu (para contexto).

    Returns:
        Mensagem traduzida com formato de 3 partes + detalhe técnico acessível.
    """
    if not message:
        return (
            "Ocorreu um erro inesperado.\n"
            "Isso não deveria acontecer e não é culpa da sua ação.\n"
            "Tente de novo. Se persistir, peça ajuda ao humano."
        )

    msg_lower = message.lower()

    # 1. Tenta match exato no mapa
    for pattern, friendly in FRIENDLY_MAP.items():
        if pattern.lower() in msg_lower:
            detail = message[:300] if len(message) > 300 else message
            return f"{friendly}\n\n[Detalhe técnico: {detail}]"

    # 2. Fallback: formato 3 partes genérico, nunca stack trace puro
    ctx = f" em '{tool_name}'" if tool_name else ""
    detail = message[:500] if len(message) > 500 else message
    return (
        f"Algo deu errado ao executar a operação{ctx}.\n"
        f"Isso significa que uma ação recente não foi concluída como esperado.\n"
        f"Tente desfazer a última ação com 'undo_last_action' ou peça para a IA revisar.\n\n"
        f"[Detalhe técnico: {detail}]"
    )


def make_error_response(message: str, tool_name: str = "",
                        error_code: int = 5000, extra: dict | None = None) -> dict:
    """Gera um dicionário de erro completo com friendly garantido.

    Esta é a ÚNICA função que deve ser usada para gerar respostas de erro
    que chegam ao usuário. Todo erro passa por aqui.

    Args:
        message: Mensagem de erro original (técnica).
        tool_name: Nome da ferramenta onde o erro ocorreu.
        error_code: Código de erro numérico (padrão 5000 = erro interno).
        extra: Campos extras a incluir na resposta (ex: retry_after, budget_exceeded).

    Returns:
        Dicionário com status, message, friendly, error_code e campos extras.
    """
    friendly = translate_error(message, tool_name)
    body: dict = {
        "status": "error",
        "message": message,
        "friendly": friendly,
        "error_code": error_code,
    }
    if extra:
        body.update(extra)
    return body


def wrap_result_with_friendly(result: dict) -> dict:
    """Adiciona campo 'friendly' a um resultado se houver erro.

    Preferível usar make_error_response() diretamente nos handlers.
    Esta função é mantida para compatibilidade retroativa.

    Args:
        result: Dicionário de resultado de uma tool.

    Returns:
        Mesmo dicionário com campo 'friendly' adicionado se status for error.
    """
    if result.get("status") == "error":
        result["friendly"] = translate_error(result.get("message", ""))
    return result
