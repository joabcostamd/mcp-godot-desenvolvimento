"""fuzzy_suggest — Utilitário de sugestão por proximidade de texto.

Generaliza o padrão já usado em godot_class_ref (difflib.get_close_matches)
para qualquer handler que recebe um nome como parâmetro.

Feature: Grupo C — Sugestão fuzzy generalizada.
"""

import difflib


def suggest_similar(name: str, valid_names: list[str], n: int = 3, cutoff: float = 0.6) -> list[str]:
    """Retorna até n sugestões de nomes parecidos com `name`."""
    if not valid_names:
        return []
    return difflib.get_close_matches(name, valid_names, n=n, cutoff=cutoff)


def not_found_error(kind: str, name: str, valid_names: list[str]) -> dict:
    """Monta um dict de erro padronizado com sugestão embutida.

    Exemplo de uso dentro de um handler existente:
        node = _find_node(scene, node_path)
        if node is None:
            return not_found_error("nó", node_path, _list_all_node_paths(scene))
    """
    suggestions = suggest_similar(name, valid_names)
    msg = f"{kind.capitalize()} '{name}' não encontrado."
    if suggestions:
        msg += f" Você quis dizer: {', '.join(suggestions)}?"
    return {"status": "error", "message": msg, "suggestions": suggestions}
