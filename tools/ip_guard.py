"""
ip_guard.py — Guarda de propriedade intelectual de terceiros

Detecta menção a personagens, franquias ou marcas registradas de
terceiros em prompts de criação de jogos e redireciona para ideias
originais com a mesma sensação.

Princípios:
  - NÃO é bloqueio rígido — é redirecionamento educacional
  - Mecânicas de jogo NÃO são protegidas (ideia vs expressão)
  - Personagens com nome + aparência distinta SÃO protegidos
  - Gêneros (platformer, RPG, FPS) são livres
  - A decisão do usuário é final — o sistema avisa, não proíbe

Fontes:
  - Idea-expression divide (17 U.S.C. § 102(b), TRIPS Art. 9(2))
  - Substantial similarity (Nichols v. Universal, 1930)
  - Scènes à faire doctrine
  - Wikipedia: Video game clone, Fan game suppression
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════
# Franquias conhecidas — mapeia termo → sugestão de alternativa original
# ══════════════════════════════════════════════════════════════════════

_KNOWN_FRANCHISES: dict[str, str] = {
    # Nintendo — a mais agressiva em proteção de PI
    "mario": "encanador que pula em canos e coleta itens",
    "luigi": "irmão mais alto do encanador, com salto diferente",
    "bowser": "grande vilão réptil com castelo e exército",
    "peach": "personagem real que precisa ser resgatada",
    "yoshi": "montaria dinossauro que come inimigos e cospe",
    "donkey kong": "gorila forte que escala e arremessa barris",
    "kirby": "criatura redonda que copia habilidades dos inimigos",
    "zelda": "aventureiro com espada em mundo de fantasia",
    "pokemon": "criaturas elementais colecionáveis que evoluem",
    "pikachu": "criatura elétrica amarela com golpes de raio",
    "metroid": "caçadora espacial em planeta hostil com power-ups",
    "samus": "caçadora de recompensas com armadura tecnológica",
    "star fox": "piloto animal em nave espacial de combate aéreo",
    "animal crossing": "simulador de vida em vila com animais falantes",
    "splatoon": "personagens que atiram tinta para pintar território",
    "fire emblem": "estrategista em batalhas táticas com exército",
    "smash bros": "lutador em arena com personagens variados",
    "earthbound": "garoto com poderes psi em aventura suburbana",
    "f-zero": "piloto de nave anti-gravidade em circuito futurista",

    # Sega
    "sonic": "ourico velocista azul que coleta anéis",
    "tails": "raposa voadora de duas caudas que acompanha o velocista",
    "knuckles": "guardião de esmeralda com punhos poderosos",
    "eggman": "cientista maluco que constrói robôs para dominar o mundo",
    "shadow the hedgehog": "anti-herói sombrio com poderes de caos e velocidade",

    # Capcom
    "mega man": "robô azul que copia armas dos chefes derrotados",
    "ryu": "lutador errante que busca o golpe perfeito",
    "street fighter": "lutador de torneio mundial de artes marciais",
    "resident evil": "sobrevivente de surto biológico em cidade isolada",
    "monster hunter": "caçador de criaturas gigantes com armas forjadas",
    "devil may cry": "caçador de demônios estiloso com combos aéreos",

    # Square Enix
    "final fantasy": "grupo de heróis em jornada épica com cristais mágicos",
    "cloud strife": "mercenário com espada gigante e passado confuso",
    "sephiroth": "vilão com cabelo prateado e tema musical icônico",
    "kingdom hearts": "jovem com chave-espada viajando entre mundos mágicos",
    "dragon quest": "herói lendário enfrentando o lorde das trevas",

    # Sony / PlayStation
    "kratos": "guerreiro marcado pelos deuses em busca de redenção",
    "crash bandicoot": "marsupial giratório que coleta frutas e quebra caixas",
    "spyro": "dragãozinho roxo que plana e cospe fogo elementar",
    "jak and daxter": "herói silencioso com amigo falante em mundo aberto",
    "ratchet and clank": "mecânico felino com robô companheiro e armas malucas",
    "uncharted": "explorador de tesouros em ruínas antigas e tiroteios",
    "the last of us": "sobrevivente protegendo jovem em mundo pós-apocalíptico",

    # Microsoft
    "master chief": "soldado supersoldado com armadura verde em anel espacial",
    "halo": "guerra interestelar entre humanos e aliança alienígena",
    "minecraft": "mundo de blocos onde você constrói e explora livremente",

    # Blizzard
    "warcraft": "facções em guerra em mundo de fantasia com orcs e humanos",
    "starcraft": "três raças em guerra interestelar: humanos, insetos e protoss",
    "overwatch": "time de heróis com habilidades únicas em combate por objetivos",
    "diablo": "herói enfrentando demônios em masmorras escuras por tesouros",

    # Warner Bros / DC
    "batman": "vigilante noturno rico com gadgets e sem superpoderes",
    "superman": "alienígena invencível com capa que protege a humanidade",
    "wonder woman": "guerreira amazona com laço da verdade e braceletes",
    "harry potter": "jovem bruxo em escola de magia com amigos leais",
    "hogwarts": "escola de magia onde jovens aprendem feitiços e poções",

    # Disney / Marvel / Star Wars
    "mickey mouse": "rato antropomórfico otimista com amigos pato e cachorro",
    "spider-man": "jovem herói aracnídeo que balança entre prédios urbanos",
    "iron man": "gênio bilionário em armadura tecnológica que voa e atira",
    "avengers": "equipe de super-heróis enfrentando ameaças globais",
    "thanos": "titã com manopla que busca equilibrar o universo",
    "star wars": "rebeldes com sabres de luz enfrentando império galáctico",
    "darth vader": "vilão mascarado com respiração pesada e sabre vermelho",
    "yoda": "sábio pequeno que fala de trás pra frente e treina guerreiros",

    # Hasbro
    "my little pony": "pôneis coloridos em aventuras mágicas de amizade",
    "dungeons and dragons": "aventureiros de fantasia com dados e mestre do jogo",

    # Outros
    "pac-man": "criatura circular amarela que come pontos em labirinto",
    "tetris": "blocos caindo que você encaixa para completar linhas",
    "angry birds": "pássaros coloridos arremessados contra estruturas de porcos",
    "five nights at freddy": "vigia noturno em pizzaria com animatrônicos assustadores",
    "among us": "tripulantes coloridos com um impostor sabotando a nave",
    "fortnite": "100 jogadores em ilha construindo e atirando até o último",
    "roblox": "jogador em mundos de blocos criados por outros jogadores",
    "genshin impact": "viajante elemental em mundo aberto de fantasia anime",
    "baldur's gate": "aventureiro em reino de fantasia com escolhas morais profundas",

    "half-life": "cientista silencioso sobrevivendo a invasão alienígena",

    "tomb raider": "arqueóloga atlética explorando tumbas antigas com pistolas",

    "elden ring": "maculado em terra devastada com combate preciso e exploração",
    "skyrim": "dragonborn enfrentando dragões em província nórdica gelada",

    "grand theft auto": "criminoso em cidade aberta com missões e caos urbano",
    "the sims": "personagens virtuais vivendo vidas simuladas em casas customizadas",
    "silent hill": "pessoa perdida em cidade fantasma coberta de névoa e monstros",
    "metal gear solid": "espião tático com missões de infiltração e chefes únicos",
}

# ── Termos genéricos (NÃO devem ser flaggados) ──────────────────
_GENERIC_TERMS: set[str] = {
    "platformer", "plataforma", "rpg", "fps", "shooter", "tiro",
    "puzzle", "quebra-cabeça", "roguelike", "roguelite", "metroidvania",
    "survival", "sobrevivência", "horror", "terror", "ação", "action",
    "aventura", "adventure", "estratégia", "strategy", "simulação",
    "simulation", "corrida", "racing", "luta", "fighting", "beat em up",
    "hack and slash", "rts", "moba", "battle royale", "mmo", "mmorpg",
    "arcade", "casual", "idle", "clicker", "visual novel", "dating sim",
    "sandbox", "open world", "mundo aberto", "crafting", "building",
    "tower defense", "card game", "jogo de cartas", "deck builder",
    "dungeon crawler", "bullet hell", "twin stick", "stealth", "furtivo",
    "narration", "walking sim", "rhythm", "ritmo", "party game",
    # Elementos genéricos de fantasia
    "dragão", "dragon", "castelo", "castle", "espada", "sword",
    "mago", "wizard", "feiticeiro", "sorcerer", "elfo", "elf",
    "anão", "dwarf", "orc", "goblin", "troll", "zumbi", "zombie",
    "vampiro", "vampire", "lobisomem", "werewolf", "fantasma", "ghost",
    "robô", "robot", "alien", "alienígena", "nave", "spaceship",
    "pirata", "pirate", "ninja", "samurai", "cavaleiro", "knight",
    "princesa", "princess", "rei", "king", "rainha", "queen",
    # 2D, 3D, pixel art, etc
    "2d", "3d", "pixel art", "low poly", "voxel", "isométrico",
    "top-down", "side-scroller", "plataforma 2d", "first person",
    "third person", "point and click", "text-based",
}


# ── Pré-compila padrões regex para performance ──────────────────
_COMPILED: list[tuple[re.Pattern, str, str]] = [
    (re.compile(rf"\b{re.escape(k)}\b"), k, v) for k, v in _KNOWN_FRANCHISES.items()
]

def check_ip_concern(text: str) -> dict:
    """Verifica se um texto menciona propriedade intelectual de terceiros.

    Usa matching de palavras inteiras (não substrings) para evitar
    falsos positivos. Ex: "Mario" no prompt → flag; "marionete" → não.

    Args:
        text: texto a verificar (prompt de criação, descrição de jogo, etc.)

    Returns:
        dict com:
          - flagged (bool): True se detectou PI de terceiros
          - match (str): termo que disparou (vazio se não flaggou)
          - alternative (str): sugestão de ideia original equivalente
          - message (str): mensagem amigável em pt-BR
    """
    if not text or not text.strip():
        return {"flagged": False, "match": "", "alternative": "", "message": ""}

    text_lower = text.lower()

    # Verifica franquias conhecidas com match de palavra inteira (pré-compilado)
    for pattern, franchise, alternative in _COMPILED:
        if pattern.search(text_lower):
            # Verifica contexto: "meu amigo Mario" vs "jogo do Mario"
            if _is_likely_personal_name(text_lower, franchise):
                continue

            return {
                "flagged": True,
                "match": franchise,
                "alternative": alternative,
                "message": (
                    f"Não posso criar '{franchise}' — é propriedade de outra empresa "
                    f"e você não poderia publicar o jogo depois.\n\n"
                    f"Mas posso fazer algo com a mesma sensação:\n"
                    f"👉 {alternative}.\n\n"
                    f"Quer que eu crie uma versão original com esse conceito?"
                ),
            }

    return {"flagged": False, "match": "", "alternative": "", "message": ""}


def _is_likely_personal_name(text_lower: str, term: str) -> bool:
    """Verifica se o termo parece ser usado como nome próprio comum.

    Padrões que indicam nome pessoal (não franquia):
      - "meu amigo X", "meu primo X", "conheço um X"
      - "o X da padaria", "X me disse"
      - X seguido de sobrenome comum: "Mario Silva", "Luigi Santos"

    Returns True se parece nome pessoal (NÃO deve flaggar).
    """
    personal_patterns = [
        # Posessivo: "meu amigo Mario", "minha prima Peach"
        rf"(meu|minha|nosso|nossa)\s+(amigo|primo|colega|irmao|irma|tio|tia|pai|mae|filho|filha|vizinho|conhecido)\s+{re.escape(term)}",
        # "conheço/conheci/conhecia o/a Mario"
        rf"conhe[çc](o|i|ia|er|emos|eram)\s+(o\s+|a\s+)?(um\s+|uma\s+)?{re.escape(term)}",
        # "Mario me disse/falou/contou"
        rf"{re.escape(term)}\s+(me\s+)?(disse|falou|contou|ligou|chamou|mandou|enviou)",
        # Reverso: "Mario é meu amigo", "Mario era meu primo"
        rf"{re.escape(term)}\s+(é|era|foi|eh)\s+(meu|minha|um|uma)\s+(amigo|primo|colega|irmao|conhecido)",
        # "meu amigo chamado Mario", "um cara chamado Link"
        rf"(meu|minha|um|uma)\s+\w+\s+chamado\s+{re.escape(term)}",
    ]

    for pattern in personal_patterns:
        if re.search(pattern, text_lower):
            return True

    return False


def check_brief_ip(brief_data: dict) -> dict:
    """Verifica PI de terceiros em um project brief completo.

    Verifica title e description do brief.
    """
    title = brief_data.get("title", "")
    description = brief_data.get("description", "")

    for field_name, text in [("title", title), ("description", description)]:
        result = check_ip_concern(text)
        if result["flagged"]:
            result["field"] = field_name
            return result

    return {"flagged": False, "match": "", "alternative": "", "message": ""}


# ══════════════════════════════════════════════════════════════════════
# Estado de decisão do usuário (para não perguntar de novo)
# ══════════════════════════════════════════════════════════════════════

_IP_STATE_FILENAME = ".mcp_ip_state.json"


def _load_ip_state(project_path: str) -> dict:
    """Carrega o estado de decisões IP do projeto."""
    state_file = Path(project_path) / _IP_STATE_FILENAME
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"decisions": {}}


def _save_ip_state(project_path: str, state: dict) -> None:
    """Salva o estado de decisões IP do projeto."""
    state_file = Path(project_path) / _IP_STATE_FILENAME
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def is_ip_previously_accepted(project_path: str, term: str) -> bool:
    """Verifica se o usuário já aceitou este termo antes."""
    state = _load_ip_state(project_path)
    return term.lower() in state.get("decisions", {})


def record_ip_decision(project_path: str, term: str, accepted: bool, reason: str = "") -> None:
    """Registra a decisão do usuário sobre um termo IP."""
    from datetime import datetime
    state = _load_ip_state(project_path)
    state.setdefault("decisions", {})[term.lower()] = {
        "accepted": accepted,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
    }
    _save_ip_state(project_path, state)


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        # Cenário 1: franquia conhecida → deve flaggar
        ("Faz um jogo do Mario", True, "mario"),
        # Cenário 2: gênero → NÃO deve flaggar
        ("Faz um platformer 2D", False, ""),
        # Cenário 3: personagem de arte → deve flaggar
        ("Desenha o Sonic correndo", True, "sonic"),
        # Cenário 4: nome próprio comum → NÃO deve flaggar
        ("Meu amigo Mario me disse", False, ""),
        # Cenário 5: Pokémon → deve flaggar
        ("Cria um jogo estilo Pokemon", True, "pokemon"),
        # Cenário 6: elemento genérico de fantasia → NÃO deve flaggar
        ("Um dragão que cospe fogo no castelo", False, ""),
        # Cenário 7: Minecraft → deve flaggar
        ("Quero um jogo tipo Minecraft", True, "minecraft"),
        # Cenário 8: mecânica, não franquia → NÃO deve flaggar
        ("Jogo de sobrevivência com crafting e exploração", False, ""),
        # Cenário 9: case insensitive
        ("FAZ UM JOGO DO MARIO", True, "mario"),
        # Cenário 10: substring → NÃO deve flaggar ("sonic" em "sonicamente")
        ("Ataque sonicamente rápido", False, ""),
    ]

    all_ok = True
    for text, expected_flagged, expected_match in tests:
        result = check_ip_concern(text)
        flagged_ok = result["flagged"] == expected_flagged
        match_ok = (result["match"] == expected_match) if expected_flagged else True
        ok = flagged_ok and match_ok

        if not ok:
            all_ok = False

        icon = "✅" if ok else "❌"
        print(f"{icon} '{text[:50]}' → flagged={result['flagged']} match='{result['match']}' "
              f"(expected: flagged={expected_flagged} match='{expected_match}')")

    if all_ok:
        print("\n✅ Todos os 10 testes passaram!")
    else:
        print("\n❌ Alguns testes falharam.")
