"""
tools/tradutor.py — Tradutor de intenção v0 (sota_1.4).

Pipeline de 4 estágios:
  A — Normalização (LLM)
  B — Recuperação (busca semântica, sota_1.2)
  C — Desambiguação (threshold 0.08)
  D — Validação (conflitos, sota_1.6)

Fonte: SOTA_01_FUNDACAO_CEREBRO.md, seção sota_1.4.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional

# Dependências internas (sota_1.2 e sota_1.6)
from tools.semantic_search import search_behaviors, ids_disponiveis
from tools.gamespec_ops import check_conflicts

# Caminhos
_PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prompts_internos")
_NORMALIZAR_PROMPT = os.path.join(_PROMPTS_DIR, "normalizar.txt")

# Threshold de desambiguação
AMBIGUITY_THRESHOLD = 0.08


def _carregar_prompt() -> str:
    """Carrega o prompt de normalização do arquivo."""
    if not os.path.exists(_NORMALIZAR_PROMPT):
        return ""
    with open(_NORMALIZAR_PROMPT, encoding="utf-8") as f:
        return f.read()


# ═══════════════════════════════════════════════════════════════
# Estágio A — Normalização
# ═══════════════════════════════════════════════════════════════

def _estagio_a_normalizar(texto: str, modelo_fn=None) -> dict:
    """
    Normaliza o pedido do usuário via LLM.

    Se modelo_fn for None (sem LLM disponível), usa fallback heurístico:
    extrai palavras-chave e monta interpretações básicas.

    Returns:
        {"canonico": str, "interpretacoes": [{"termo": str, "verbos": [str]}]}
    """
    if modelo_fn is not None:
        # Modo LLM: envia prompt + texto para o modelo
        prompt = _carregar_prompt()
        full_prompt = prompt + "\n" + texto
        try:
            raw = modelo_fn(full_prompt)
            resultado = _parse_llm_output(raw)
            if resultado:
                return resultado
        except Exception:
            pass  # Fallback para heurística

    # Fallback heurístico (sem LLM)
    return _normalizar_heuristica(texto)


def _parse_llm_output(raw: str) -> Optional[dict]:
    """Extrai JSON da saída do LLM (pode vir com markdown ou texto extra)."""
    # Tenta parse direto
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Tenta extrair de bloco ```json ... ```
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Tenta encontrar primeiro { ... } válido
    for m in re.finditer(r'\{[^{}]*\}', raw):
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            continue

    return None


def _normalizar_heuristica(texto: str) -> dict:
    """
    Fallback heurístico: extrai verbos de ação do texto.
    Não depende de LLM — funciona offline.
    """
    texto_lower = texto.lower()

    # Dicionário de mapeamento: palavra → verbos de jogo
    ACAO_MAP = {
        "pulo": ["pular", "saltar", "flutuar"],
        "pular": ["pular", "saltar", "flutuar"],
        "pule": ["pular", "saltar", "flutuar"],
        "jump": ["pular", "saltar", "flutuar"],
        "vida": ["curar", "regenerar", "proteger"],
        "health": ["curar", "regenerar", "proteger"],
        "hp": ["curar", "regenerar", "proteger"],
        "dano": ["atacar", "atingir", "colidir"],
        "damage": ["atacar", "atingir", "colidir"],
        "tiro": ["atirar", "disparar", "lançar"],
        "shoot": ["atirar", "disparar", "lançar"],
        "atirar": ["atirar", "disparar", "lançar"],
        "movimento": ["mover", "andar", "correr"],
        "move": ["mover", "andar", "correr"],
        "mover": ["mover", "andar", "correr"],
        "coletar": ["coletar", "pegar", "adquirir"],
        "collect": ["coletar", "pegar", "adquirir"],
        "inimigo": ["perseguir", "atacar", "patrulhar"],
        "enemy": ["perseguir", "atacar", "patrulhar"],
        "salvar": ["salvar", "gravar", "persistir"],
        "save": ["salvar", "gravar", "persistir"],
        "camera": ["enquadrar", "seguir", "tremer"],
        "som": ["tocar", "reproduzir", "emitir"],
        "sound": ["tocar", "reproduzir", "emitir"],
        "particula": ["emitir", "explodir", "espalhar"],
        "particle": ["emitir", "explodir", "espalhar"],
        "dialogo": ["mostrar", "exibir", "escrever"],
        "dialog": ["mostrar", "exibir", "escrever"],
    }

    interpretacoes = []
    for palavra, verbos in ACAO_MAP.items():
        if palavra in texto_lower:
            interpretacoes.append({"termo": palavra, "verbos": verbos})

    # Se não encontrou nada, retorna interpretação genérica
    if not interpretacoes:
        palavras = [p for p in texto_lower.split() if len(p) > 2]
        interpretacoes.append({
            "termo": texto[:40],
            "verbos": palavras[:5] if palavras else ["usar", "aplicar", "criar"]
        })

    return {
        "canonico": texto.strip(),
        "interpretacoes": interpretacoes,
    }


# ═══════════════════════════════════════════════════════════════
# Estágio B — Recuperação (usa sota_1.2)
# ═══════════════════════════════════════════════════════════════

def _estagio_b_recuperar(interpretacoes: List[dict], texto_original: str) -> List[dict]:
    """
    Para cada interpretação, busca behaviors semanticamente.
    Retorna lista de {termo, verbos, behaviors: [{nome, score}]}.
    """
    resultados = []

    # Busca principal com o texto original
    behaviors_principal = search_behaviors(texto_original)

    # Busca para cada verbo de cada interpretação
    for interp in interpretacoes:
        verbos = interp.get("verbos", [])
        behaviors_da_interp = []
        for verbo in verbos:
            query = f"{verbo} {interp.get('termo', '')}"
            results = search_behaviors(query)
            behaviors_da_interp.extend(results[:5])

        # Deduplica por nome e ordena por score
        seen = set()
        unicos = []
        for b in sorted(behaviors_da_interp, key=lambda x: x["score"], reverse=True):
            if b["nome"] not in seen:
                seen.add(b["nome"])
                unicos.append(b)
                if len(unicos) >= 5:
                    break

        resultados.append({
            "termo": interp.get("termo", ""),
            "verbos": verbos,
            "behaviors": [
                {"nome": b["nome"], "score": b["score"]}
                for b in unicos
            ],
        })

    # Adiciona a busca principal como fallback
    if not resultados and behaviors_principal:
        resultados.append({
            "termo": texto_original[:40],
            "verbos": [],
            "behaviors": [
                {"nome": b["nome"], "score": b["score"]}
                for b in behaviors_principal[:5]
            ],
        })

    return resultados


# ═══════════════════════════════════════════════════════════════
# Estágio C — Desambiguação
# ═══════════════════════════════════════════════════════════════

def _estagio_c_desambiguar(recuperados: List[dict]) -> dict:
    """
    Decide entre as opções recuperadas.
    Se diferença < AMBIGUITY_THRESHOLD entre top-2 → retorna múltiplas opções.
    Senão → retorna a top-1.

    Returns:
        {"escolhida": {...}, "alternativas": [...]}
    """
    # Coleta todos os behaviors únicos com maior score
    all_behaviors: Dict[str, dict] = {}
    for r in recuperados:
        for b in r.get("behaviors", []):
            nome = b["nome"]
            if nome not in all_behaviors or b["score"] > all_behaviors[nome]["score"]:
                all_behaviors[nome] = dict(b)

    ordenados = sorted(all_behaviors.values(), key=lambda x: x["score"], reverse=True)

    if not ordenados:
        return {"escolhida": None, "alternativas": []}

    top1 = ordenados[0]
    top2 = ordenados[1] if len(ordenados) > 1 else None

    # Verifica ambiguidade
    if top2 and (top1["score"] - top2["score"]) < AMBIGUITY_THRESHOLD:
        # Ambíguo: retorna top-3 opções
        alternativas = ordenados[:3]
        return {
            "escolhida": top1,
            "alternativas": alternativas,
            "ambiguo": True,
            "preview_gifs": [
                f"behaviors/{b['nome']}/preview.gif"
                for b in alternativas
            ],
        }
    else:
        # Claro: retorna só a top-1
        return {
            "escolhida": top1,
            "alternativas": [top1],
            "ambiguo": False,
        }


# ═══════════════════════════════════════════════════════════════
# Estágio D — Validação (usa sota_1.6)
# ═══════════════════════════════════════════════════════════════

def _estagio_d_validar(escolhida: Optional[dict], behaviors_no_projeto: List[str]) -> List[dict]:
    """
    Verifica conflitos da behavior escolhida contra as já presentes no projeto.

    Returns:
        Lista de conflitos: [{behavior, conflito_com, mensagem}].
    """
    if not escolhida:
        return []

    nome = escolhida.get("nome", "")
    if not nome:
        return []

    conflitos = []
    for existente in behaviors_no_projeto:
        ok, msg = check_conflicts(nome, [existente])
        if not ok:
            conflitos.append({
                "behavior": nome,
                "conflito_com": existente,
                "mensagem": msg,
            })

    return conflitos


# ═══════════════════════════════════════════════════════════════
# Pipeline principal
# ═══════════════════════════════════════════════════════════════

def traduzir_intencao(
    texto: str,
    behaviors_no_projeto: Optional[List[str]] = None,
    modelo_fn=None,
) -> dict:
    """
    Traduz pedido em linguagem natural para ações concretas sobre a biblioteca.

    Args:
        texto: Pedido em PT ou EN (ex: "quero um personagem que pule").
        behaviors_no_projeto: Lista de behaviors já no projeto (para validação).
        modelo_fn: Função que recebe prompt e retorna resposta do LLM.
                   Se None, usa fallback heurístico (offline).

    Returns:
        {
            "texto_original": str,
            "canonico": str,
            "interpretacoes": [...],
            "recuperados": [...],
            "escolhida": {...} | None,
            "alternativas": [...],
            "ambiguo": bool,
            "conflitos": [...],
            "modo": "llm" | "heuristico",
        }
    """
    if behaviors_no_projeto is None:
        behaviors_no_projeto = []

    # Validação de entrada
    if not texto or not texto.strip():
        return {
            "texto_original": texto,
            "erro": "Texto vazio. Forneça um pedido em linguagem natural.",
        }

    # ═══ Estágio A: Normalização ═══
    normalizado = _estagio_a_normalizar(texto.strip(), modelo_fn)
    interpretacoes = normalizado.get("interpretacoes", [])
    canonico = normalizado.get("canonico", texto)
    modo = "llm" if modelo_fn is not None else "heuristico"

    # ═══ Estágio B: Recuperação ═══
    recuperados = _estagio_b_recuperar(interpretacoes, texto)

    # ═══ Estágio C: Desambiguação ═══
    decisao = _estagio_c_desambiguar(recuperados)
    escolhida = decisao.get("escolhida")
    alternativas = decisao.get("alternativas", [])
    ambiguo = decisao.get("ambiguo", False)

    # ═══ Estágio D: Validação ═══
    conflitos = _estagio_d_validar(escolhida, behaviors_no_projeto)

    # ═══ Validação anti-alucinação ═══
    ids_validos = set(ids_disponiveis())
    if escolhida and escolhida.get("nome", "") not in ids_validos:
        escolhida = None  # Behavior inexistente → descartado

    alternativas = [a for a in alternativas if a.get("nome", "") in ids_validos]

    # ═══ Monta ações sugeridas ═══
    acoes = []
    if escolhida:
        acoes.append({
            "op": "add_behavior",
            "behavior": escolhida["nome"],
            "params_sugeridos": {},
        })

    return {
        "texto_original": texto,
        "canonico": canonico,
        "interpretacoes": interpretacoes,
        "recuperados": [
            {
                "termo": r["termo"],
                "verbos": r["verbos"],
                "behaviors": r["behaviors"][:3],
            }
            for r in recuperados
        ],
        "escolhida": escolhida,
        "alternativas": alternativas[:3],
        "ambiguo": ambiguo,
        "acoes": acoes,
        "conflitos": conflitos,
        "modo": modo,
    }
