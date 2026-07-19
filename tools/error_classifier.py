"""error_classifier.py — Classificador + diagnostico de causa raiz (Fatia 1.11).

Dado um UnifiedError (da fatia 1.10), diagnostica a causa provavel,
propoe um patch, e rotula como "corrige_causa" ou "silencia_sintoma".

Totalmente automatico e sem risco: so proposicao, nunca aplica correcoes.

Uso:
    from tools.error_classifier import ErrorClassifier, classify_errors
    ec = ErrorClassifier()
    diags = ec.classify_all(erros)
"""

import re
from dataclasses import dataclass, asdict


@dataclass
class Diagnosis:
    """Diagnostico de um erro — causa provavel + patch proposto."""

    erro_original: dict  # UnifiedError como dict (referencia)
    causa_provavel: str
    patch_proposto: str
    rotulo: str  # "corrige_causa" | "silencia_sintoma"
    confianca: float = 1.0  # 0.0 (chute) a 1.0 (certeza)

    def to_dict(self) -> dict:
        return asdict(self)


# ══════════════════════════════════════════════════════════════════
# Padrões de erro — organizados por tipo
# ══════════════════════════════════════════════════════════════════

# Parse errors (LSP / compilador)
PARSE_PATTERNS: list[tuple] = [
    # ── Variaveis e membros ──
    (
        r"(?i)identifier\s+['\"]?(\w+)['\"]?\s+not\s+declared",
        "Variavel '{0}' usada mas nao declarada no escopo atual.",
        "Declare 'var {0}' antes de usar ou verifique se o nome esta correto.",
        "corrige_causa", 0.9,
    ),
    (
        r"(?i)cannot\s+find\s+member\s+['\"]?(\w+)['\"]?",
        "Metodo/propriedade '{0}' nao existe na classe base.",
        "Use gdscript_hover() para ver os metodos validos da classe.",
        "corrige_causa", 0.85,
    ),
    (
        r"(?i)member\s+['\"]?(\w+)['\"]?\s+not\s+found",
        "Membro '{0}' nao encontrado na classe ou no node.",
        "Verifique se '{0}' e metodo/propriedade valido. Use has_method() em runtime.",
        "corrige_causa", 0.85,
    ),
    # ── Sintaxe ──
    (
        r"(?i)unexpected\s+token|parse\s+error|syntax\s+error",
        "Erro de sintaxe no codigo GDScript.",
        "Verifique parenteses, virgulas, indentacao e keywords na linha indicada.",
        "corrige_causa", 0.8,
    ),
    (
        r"(?i)expected\s+(\w+)\s+but\s+found\s+['\"]?(\w+)['\"]?",
        "Tipo '{1}' encontrado onde se esperava '{0}'.",
        "Corrija o tipo do valor ou use cast explicito com 'as'.",
        "corrige_causa", 0.85,
    ),
    (
        r"(?i)too\s+many\s+arguments|wrong\s+number\s+of\s+arguments",
        "Numero incorreto de argumentos na chamada de funcao.",
        "Confira a assinatura da funcao e ajuste os argumentos.",
        "corrige_causa", 0.9,
    ),
    # ── Warnings (silencia_sintoma) ──
    (
        r"(?i)unused\s+variable\s+['\"]?(\w+)['\"]?|unused\s+parameter",
        "Variavel '{0}' declarada mas nunca usada.",
        "Remova a declaracao ou prefixe parametros nao usados com '_'.",
        "silencia_sintoma", 0.7,
    ),
    (
        r"(?i)unused\s+signal\s+['\"]?(\w+)['\"]?",
        "Sinal '{0}' declarado mas nunca emitido.",
        "Remova a declaracao do sinal se nao for mais necessario.",
        "silencia_sintoma", 0.65,
    ),
    (
        r"(?i)shadow|shadows\s+variable",
        "Variavel local sombreia variavel de escopo externo.",
        "Renomeie uma das variaveis para evitar confusao de escopo.",
        "silencia_sintoma", 0.7,
    ),
    (
        r"(?i)return\s+value\s+discarded|return\s+value\s+not\s+used",
        "Valor de retorno da funcao esta sendo descartado.",
        "Atribua o retorno a uma variavel ou use 'await' se for corrotina.",
        "silencia_sintoma", 0.6,
    ),
]

# Runtime errors (console / push_error)
RUNTIME_PATTERNS: list[tuple] = [
    # ── Null ──
    (
        r"(?i)null\s+instance|null\s+object|on\s+a\s+null|cannot\s+call.*null",
        "Referencia nula — acesso em objeto null/nao inicializado.",
        "Adicione 'if obj != null:' antes de acessar. Verifique @onready e _ready().",
        "corrige_causa", 0.9,
    ),
    # ── Indices ──
    (
        r"(?i)out\s+of\s+bounds|index\s+\d+\s+out\s+of|invalid\s+index",
        "Indice fora dos limites do array/string.",
        "Verifique bounds: 'if idx < array.size():'. Prefira 'for item in array'.",
        "corrige_causa", 0.9,
    ),
    # ── Aritmetica ──
    (
        r"(?i)division\s+by\s+zero",
        "Divisao por zero.",
        "Verifique se o divisor != 0 antes da operacao.",
        "corrige_causa", 1.0,
    ),
    # ── Tipos ──
    (
        r"(?i)cannot\s+convert|invalid\s+conversion|type\s+mismatch|invalid\s+operand",
        "Erro de tipo em runtime — conversao ou operacao invalida.",
        "Use str(), int(), float() explicitamente. Verifique tipos com 'is'.",
        "corrige_causa", 0.8,
    ),
    # ── Recursos ──
    (
        r"(?i)not\s+found|does\s+not\s+exist|missing\s+file|cannot\s+open",
        "Recurso nao encontrado (node, arquivo, cena).",
        "Verifique o path. Use $NodeName para caminhos absolutos. Confirme .import.",
        "corrige_causa", 0.8,
    ),
    # ── Recursao ──
    (
        r"(?i)stack\s+overflow|infinite\s+loop|recursion|too\s+deep",
        "Stack overflow — recursao ou loop infinito.",
        "Adicione condicao de parada na recursao/loop. Verifique chamadas ciclicas.",
        "corrige_causa", 0.9,
    ),
    # ── Sinais ──
    (
        r"(?i)signal.*connect|failed\s+to\s+connect|signal.*not\s+found",
        "Falha ao conectar sinal — metodo alvo ou sinal inexistente.",
        "Confirme que o metodo existe no node alvo com os parametros corretos.",
        "corrige_causa", 0.85,
    ),
    # ── Memoria (silencia_sintoma) ──
    (
        r"(?i)memory\s+leak|leaked\s+\d+|orphan\s+node",
        "Possivel vazamento de memoria — nodes orfaos ou recursos nao liberados.",
        "Use queue_free() em vez de remove_child(). Verifique referencias circulares.",
        "silencia_sintoma", 0.55,
    ),
]

# Editor errors (auditorias)
EDITOR_PATTERNS: list[tuple] = [
    (
        r"(?i)not\s+in\s+input\s*map|not\s+found.*input|input.*not\s+found|acao.*nao.*declarada",
        "Acao de input usada mas nao declarada no Input Map.",
        "Adicione a acao em Project Settings > Input Map.",
        "corrige_causa", 0.95,
    ),
    (
        r"(?i)unreachable|inalcancavel|not\s+reachable|never\s+instantiated",
        "Cena existe no projeto mas nunca e alcancada/instanciada.",
        "Adicione ao fluxo de jogo ou remova se for obsoleta.",
        "silencia_sintoma", 0.7,
    ),
    (
        r"(?i)autoload.*missing|autoload.*not\s+found|singleton.*not",
        "Autoload/Singleton referenciado mas nao configurado.",
        "Configure em Project Settings > Autoload.",
        "corrige_causa", 0.95,
    ),
    (
        r"(?i)uid.*inconsist|uid.*mismatch|uid.*corrupt",
        "UID inconsistente — recurso renomeado/corrompido.",
        "Reimporte o recurso ou corrija a referencia no .tscn/.gd.",
        "corrige_causa", 0.8,
    ),
    (
        r"(?i)save.*incompat|save.*version|save.*corrupt",
        "Arquivo de save incompativel com a versao atual.",
        "Atualize o formato de save ou implemente migracao de versao.",
        "corrige_causa", 0.85,
    ),
    (
        r"(?i)duplicate|duplicado|ja\s+existe|already\s+exists",
        "Recurso ou nome duplicado no projeto.",
        "Renomeie um dos recursos para evitar conflito.",
        "corrige_causa", 0.9,
    ),
    (
        r"(?i)deprecated|obsoleto|removed\s+in",
        "Recurso ou API depreciada/removida nesta versao do Godot.",
        "Substitua pela API recomendada na documentacao de migracao do Godot.",
        "silencia_sintoma", 0.6,
    ),
]


class ErrorClassifier:
    """Classifica erros e produz diagnosticos com causa raiz."""

    def classify(self, error: dict) -> Diagnosis:
        """Classifica um unico UnifiedError."""
        tipo = error.get("tipo", "parse")
        mensagem = error.get("mensagem", "")

        patterns = {
            "parse": PARSE_PATTERNS,
            "runtime": RUNTIME_PATTERNS,
            "editor": EDITOR_PATTERNS,
        }.get(tipo)

        if patterns:
            return self._match(mensagem, error, patterns)

        return Diagnosis(
            erro_original=error,
            causa_provavel=f"Tipo de erro desconhecido: '{tipo}'.",
            patch_proposto="Analise manualmente a mensagem e o contexto.",
            rotulo="corrige_causa",
            confianca=0.3,
        )

    def classify_all(self, errors: list[dict]) -> list[dict]:
        """Classifica uma lista de UnifiedError."""
        return [self.classify(e).to_dict() for e in errors]

    def _match(self, mensagem: str, error: dict, patterns: list) -> Diagnosis:
        """Tenta casar a mensagem contra uma lista de padroes.

        Args:
            mensagem: Texto da mensagem de erro
            error: UnifiedError original (para referencia)
            patterns: Lista de tuplas (regex, causa, patch, rotulo, confianca)

        Returns:
            Diagnosis — o primeiro match ou fallback generico
        """
        for regex, causa_tpl, patch_tpl, rotulo, confianca in patterns:
            m = re.search(regex, mensagem)
            if m:
                # Substitui {0}, {1}, ... pelos grupos capturados
                grupos = m.groups()
                causa = causa_tpl
                patch = patch_tpl
                for i, g in enumerate(grupos):
                    causa = causa.replace(f"{{{i}}}", g)
                    patch = patch.replace(f"{{{i}}}", g)
                return Diagnosis(
                    erro_original=error,
                    causa_provavel=causa,
                    patch_proposto=patch,
                    rotulo=rotulo,
                    confianca=confianca,
                )

        # Fallback — nenhum padrao conhecido
        return Diagnosis(
            erro_original=error,
            causa_provavel=f"Nao foi possivel classificar automaticamente: '{mensagem[:120]}'.",
            patch_proposto="Analise manual necessaria. Consulte a documentacao do Godot ou o stack trace.",
            rotulo="corrige_causa",
            confianca=0.2,
        )


# ── Singleton ──────────────────────────────────────────────────────

_classifier: ErrorClassifier | None = None


def get_error_classifier() -> ErrorClassifier:
    global _classifier
    if _classifier is None:
        _classifier = ErrorClassifier()
    return _classifier


def classify_errors(errors: list[dict]) -> list[dict]:
    """Interface publica — classifica uma lista de UnifiedError.

    Args:
        errors: Lista de dicts UnifiedError (de collect_errors)

    Returns:
        Lista de dicts Diagnosis
    """
    return get_error_classifier().classify_all(errors)
