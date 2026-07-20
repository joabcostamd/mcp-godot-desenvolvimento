"""
name_utils.py — Normalizacao de nomes para identificadores seguros

Separa ROTULO (exibicao) de IDENTIFICADOR (uso interno: pasta, arquivo, classe).
Garante compatibilidade cross-platform e com Godot/GDScript.

Uso:
    from tools.name_utils import normalize_identifier, resolve_collision

    slug = normalize_identifier("Meu Jogo Legal")  # -> "meu_jogo_legal"
    final = resolve_collision(slug, {"meu_jogo_legal"})  # -> "meu_jogo_legal_2"
"""

from __future__ import annotations

import re
import unicodedata


def normalize_identifier(raw: str) -> str:
    """Converte qualquer string em um identificador seguro [a-z0-9_].

    Processo:
      1. NFKD — decompoe caracteres acentuados (c + ¸, a + ~)
      2. ASCII — remove diacriticos, mantem so a base
      3. Lowercase + substitui especiais por _
      4. Limpa bordas de _

    Args:
        raw: string de entrada (ex: "Meu Jogo Legal", "Coração 2")

    Returns:
        identificador normalizado (ex: "meu_jogo_legal", "coracao_2")
        Se a string ficar vazia apos normalizacao, retorna "projeto".

    Exemplos:
        "Meu Jogo Legal" → "meu_jogo_legal"
        "Coração 2"      → "coracao_2"
        "Jogador™"        → "jogadortm"
        "游戏"            → "" → fallback "projeto"
        "  Espaços!  "    → "espacos"
    """
    if not raw or not raw.strip():
        return "projeto"

    # 1. NFKD: decompoe caracteres Unicode em base + diacriticos
    nfkd = unicodedata.normalize("NFKD", raw)

    # 2. Remove diacriticos: codifica como ASCII, ignora o que nao couber
    ascii_bytes = nfkd.encode("ascii", "ignore")
    ascii_str = ascii_bytes.decode("ascii")

    # 3. Lowercase + substitui qualquer sequencia de nao-[a-z0-9] por um unico _
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_str.lower()).strip("_")

    # 4. Fallback: se a string ficar vazia (ex: nome puramente nao-latino)
    if not slug:
        slug = "projeto"

    return slug


def resolve_collision(desired: str, existing: set[str]) -> str:
    """Resolve colisao de nomes adicionando sufixo numerico.

    Args:
        desired: nome desejado (ex: "cafe")
        existing: conjunto de nomes que ja existem (ex: {"cafe"})

    Returns:
        nome unico (ex: "cafe_2", "cafe_3", ...)

    Exemplos:
        resolve_collision("cafe", {"cafe"})      → "cafe_2"
        resolve_collision("cafe", {"cafe_2"})    → "cafe"   (desejado nao colide)
        resolve_collision("cafe", set())          → "cafe"
    """
    if desired not in existing:
        return desired

    n = 2
    while f"{desired}_{n}" in existing:
        n += 1
    return f"{desired}_{n}"


def is_safe_identifier(value: str) -> bool:
    """Verifica se uma string ja e um identificador seguro.

    Retorna True se a string contem apenas [a-z0-9_] e nao comeca com digito.
    """
    if not value:
        return False
    return bool(re.fullmatch(r"[a-z_][a-z0-9_]*", value))


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        ("Meu Jogo Legal", "meu_jogo_legal"),
        ("Coração 2", "coracao_2"),
        ("Jogadór", "jogador"),
        ("  Espaços!  ", "espacos"),
        ("游戏", "projeto"),
        ("", "projeto"),
        ("   ", "projeto"),
        ("Olá, Mundo!", "ola_mundo"),
        ("Teste_123", "teste_123"),
        ("Jogador™", "jogadortm"),
    ]

    all_ok = True
    for raw, expected in tests:
        result = normalize_identifier(raw)
        ok = result == expected
        if not ok:
            all_ok = False
        print(f"{'✅' if ok else '❌'} normalize({raw!r}) = {result!r} (esperado: {expected!r})")

    # Teste de colisão
    print()
    r1 = resolve_collision("cafe", {"cafe"})
    r2 = resolve_collision("cafe", set())
    r3 = resolve_collision("cafe", {"cafe", "cafe_2"})
    print(f"resolve_collision('cafe', {{'cafe'}})           = {r1!r} (esperado: 'cafe_2')")
    print(f"resolve_collision('cafe', set())                 = {r2!r} (esperado: 'cafe')")
    print(f"resolve_collision('cafe', {{'cafe', 'cafe_2'}})  = {r3!r} (esperado: 'cafe_3')")

    if all_ok:
        print("\n✅ Todos os testes passaram!")
    else:
        print("\n❌ Alguns testes falharam.")
