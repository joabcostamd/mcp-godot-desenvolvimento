"""friendly_errors — Traduz erros técnicos para PT-BR simples.

Usado pelo MCP server para transformar mensagens de erro técnicas
em explicações que um non-coder entende.
"""

# ══════════════════════════════════════════════════════════════════════
# Mapeamento de padrões de erro → mensagem amigável
# ══════════════════════════════════════════════════════════════════════

FRIENDLY_MAP: dict[str, str] = {
    # Godot / Projeto
    "project.godot não encontrado": (
        "O projeto Godot não foi encontrado. "
        "Use 'create_project' para criar um novo ou 'set_active_project' para abrir um existente."
    ),
    "main scene não definida": (
        "O jogo não tem uma cena principal. "
        "Use 'set_main_scene' para definir qual cena abre quando o jogo inicia."
    ),
    "no main scene": (
        "O jogo não tem uma cena principal. "
        "Use 'set_main_scene' para definir qual cena abre quando o jogo inicia."
    ),

    # Arquivos
    "File not found": (
        "O arquivo que você tentou acessar não existe. "
        "Verifique se o caminho está correto ou se o arquivo já foi criado."
    ),
    "não encontrado": (
        "O que você está procurando não foi encontrado. "
        "Pode ser que ainda não tenha sido criado. Crie primeiro, depois acesse."
    ),
    "já existe": (
        "Já existe algo com esse nome. Escolha outro nome ou delete o existente primeiro."
    ),

    # Cena / Nós
    "Node not found": (
        "O elemento que você está tentando acessar não existe na cena. "
        "Use 'load_scene_tree' para ver todos os elementos disponíveis."
    ),
    "nó não encontrado": (
        "O elemento que você está tentando acessar não existe na cena. "
        "Use 'add_node' para criar ele primeiro."
    ),
    "Invalid node type": (
        "O tipo de elemento que você pediu não existe no Godot. "
        "Use 'list_valid_node_types' para ver os tipos disponíveis."
    ),

    # GDScript
    "Parse Error": (
        "O código do jogo tem um erro de escrita. "
        "Isso geralmente é um bug do MCP — peça para a IA revisar o script."
    ),
    "SCRIPT ERROR": (
        "O jogo encontrou um erro durante a execução. "
        "Isso acontece quando uma cena tenta acessar algo que não existe mais. "
        "Use 'compile_test' para ver os erros exatos."
    ),

    # Performance / Timeout
    "Timeout": (
        "A operação demorou muito e foi cancelada. "
        "Tente de novo. Se persistir, o projeto pode estar muito grande ou o Godot travou."
    ),
    "timeout": (
        "A operação demorou muito e foi cancelada. "
        "Tente de novo com um projeto menor ou reinicie o Godot."
    ),

    # Conexão
    "Connection refused": (
        "Não foi possível conectar ao Godot. "
        "Verifique se o Godot está aberto com o plugin MCP IA DEV ativo."
    ),
    "Bridge offline": (
        "A ponte de comunicação com o Godot não está ativa. "
        "Abra o Godot e ative o plugin MCP IA DEV em Project → Project Settings → Plugins."
    ),

    # Export
    "Templates de exportação não instalados": (
        "Para exportar o jogo, você precisa instalar os templates. "
        "No Godot, vá em Editor → Manage Export Templates → Download and Install."
    ),

    # Path traversal
    "Path traversal": (
        "Você tentou acessar uma pasta fora do projeto. Isso não é permitido por segurança. "
        "Todos os arquivos devem ficar dentro da pasta do projeto."
    ),

    # Godot CLI / Runtime
    "Can't run project": (
        "O Godot não conseguiu rodar o projeto. "
        "Use 'set_main_scene' para definir a cena principal primeiro."
    ),
    "Invalid assignment of property": (
        "O jogo tentou usar um valor em algo que não existe mais. "
        "Isso acontece quando um nó foi removido mas o script ainda o referencia."
    ),
    "Failed loading resource": (
        "O Godot não conseguiu carregar um arquivo. "
        "O arquivo pode estar corrompido. Tente recriá-lo com a IA."
    ),
    "No such file": (
        "O arquivo que você tentou acessar não existe. "
        "Verifique o caminho ou crie o arquivo primeiro."
    ),

    # Rate limit / Geral
    "Rate limit": (
        "Você está fazendo muitas operações muito rápido. Aguarde alguns segundos."
    ),
    "Permission denied": (
        "Sem permissão para acessar este arquivo. "
        "Feche outros programas que possam estar usando ele."
    ),
    "already exists": (
        "Já existe algo com este nome. Use um nome diferente."
    ),
    "not a valid": (
        "O valor fornecido não é válido. Verifique o formato e o tipo do valor."
    ),
}


def translate_error(message: str) -> str:
    """Traduz uma mensagem de erro técnica para PT-BR amigável.

    Args:
        message: Mensagem de erro original.

    Returns:
        Mensagem traduzida, ou a original se nenhum padrão for encontrado.
    """
    if not message:
        return "Erro desconhecido. Tente de novo ou peça ajuda."

    msg_lower = message.lower()

    for pattern, friendly in FRIENDLY_MAP.items():
        if pattern.lower() in msg_lower:
            return f"{friendly}\n\n[Detalhe técnico: {message[:200]}]"

    # Fallback: retorna mensagem original com prefixo amigável
    return (
        f"Algo deu errado, mas não se preocupe — isso geralmente tem solução. "
        f"Use 'undo_last_action' para desfazer se algo quebrou.\n\n"
        f"[Detalhe: {message[:300]}]"
    )


def wrap_result_with_friendly(result: dict) -> dict:
    """Adiciona campo 'friendly' a um resultado se houver erro.

    Args:
        result: Dicionário de resultado de uma tool.

    Returns:
        Mesmo dicionário com campo 'friendly' adicionado se status for error.
    """
    if result.get("status") == "error":
        result["friendly"] = translate_error(result.get("message", ""))
    return result
