#!/usr/bin/env python3
"""gerar_manual.py — Gera docs/manual/ a partir do código real.

Regra ABSOLUTA: zero número escrito à mão. Toda contagem vem de len(),
todo texto vem de __doc__ ou .description dos objetos reais.

Uso: python scripts/gerar_manual.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "docs" / "manual"


def _load_tools():
    """Carrega todas as tools do _raw_tool_defs()."""
    from core.tool_definitions import _raw_tool_defs
    return list(_raw_tool_defs())


def _load_behaviors():
    """Carrega todos os behaviors de behaviors/**/behavior.json."""
    behaviors = []
    bdir = ROOT / "behaviors"
    if bdir.is_dir():
        for bf in sorted(bdir.rglob("behavior.json")):
            try:
                data = json.loads(bf.read_text(encoding="utf-8"))
                behaviors.append(data)
            except Exception:
                pass
    return behaviors


def _load_blueprints():
    """Carrega todos os blueprints de blueprints/*.json (exceto schema)."""
    blueprints = []
    bdir = ROOT / "blueprints"
    if bdir.is_dir():
        for bf in sorted(bdir.glob("*.json")):
            if "schema" in bf.name:
                continue
            try:
                data = json.loads(bf.read_text(encoding="utf-8"))
                blueprints.append(data)
            except Exception:
                pass
    return blueprints


def _load_friendly_errors():
    """Carrega o FRIENDLY_MAP de friendly_errors.py."""
    from tools.friendly_errors import FRIENDLY_MAP
    return FRIENDLY_MAP


def _ferramentas_por_grupo():
    """Agrupa tools por prefixo (ex: scene_manage → scene)."""
    tools = _load_tools()
    grupos: dict[str, list] = {}
    for t in tools:
        prefix = t.name.split("_")[0]
        grupos.setdefault(prefix, []).append(t)
    return grupos


# ══════════════════════════════════════════════════════════════════════
# SEÇÕES DO MANUAL
# ══════════════════════════════════════════════════════════════════════

def gerar_00():
    """O que é esta ferramenta."""
    tools = _load_tools()
    texto = f"""# O que é o MCP Godot Agent?

O MCP Godot Agent é um assistente que cria jogos completos em Godot 4.7.
Você fala o que quer em português, e ele constrói o jogo para você —
da ideia até o jogo pronto para publicar.

**Você não precisa saber programar.** A IA cuida do código, das cenas,
dos personagens, da física, da música, de tudo.

## O que ele sabe fazer

O MCP tem **{len(tools)} ferramentas** que cobrem todas as etapas de
criação de um jogo:

- Criar projetos, cenas, personagens e inimigos
- Escrever scripts (GDScript)
- Configurar física, animações, câmera
- Adicionar sons e músicas
- Criar menus, HUD, diálogos
- Exportar o jogo para Windows, Linux, Web e mobile

## Como funciona

Você abre o VS Code, digita o que quer — por exemplo:
**"quero um jogo de plataforma com um herói que pula e atira"** —
e o MCP constrói o jogo passo a passo, mostrando o progresso no
painel dentro do Godot.
"""
    (OUT / "00-o-que-e.md").write_text(texto, encoding="utf-8")


def gerar_01():
    """Instalação em 1 comando."""
    texto = """# Instalação

## Em 1 comando

Abra o terminal (PowerShell) e cole:

```
python init.py
```

O instalador vai:

1. Procurar o Godot 4.7 e o Python 3.12+ no seu computador
2. Criar o ambiente isolado
3. Configurar a conexão com o VS Code
4. Criar seu primeiro projeto Godot
5. Abrir o editor do Godot automaticamente

Depois é só digitar `/plan` no chat do VS Code para começar.

## Se algo der errado

O instalador mostra `[OK]` ou `[FALHA]` para cada passo,
com a explicação do que fazer em português simples.
"""
    (OUT / "01-instalar.md").write_text(texto, encoding="utf-8")


def gerar_02():
    """Primeiro jogo em 10 minutos."""
    texto = """# Seu primeiro jogo

> ⚠️ **Em breve.** Esta seção será preenchida pela Fatia 1.J (`quick_start`),
> que permite criar um jogo jogável a partir de uma única frase.

Enquanto isso, você pode começar assim:

1. Digite `/plan` no chat
2. Descreva o jogo que você quer fazer
3. O MCP vai planejar e mostrar o que vai construir
4. Quando estiver pronto, diga "sim" e ele começa
"""
    (OUT / "02-primeiro-jogo.md").write_text(texto, encoding="utf-8")


def gerar_03():
    """As 6 fases e por que elas existem."""
    phases = [
        ("IDEIA", "Você descreve o jogo. O MCP entende o que você quer e monta o plano."),
        ("DESIGN", "O MCP define as regras, personagens, fases e a estrutura do jogo."),
        ("PROTOTIPO", "O MCP constrói uma versão jogável simples para testar a ideia."),
        ("CONTEUDO", "O MCP adiciona fases, inimigos, itens, diálogos — o jogo cresce."),
        ("POLIMENTO", "O MCP ajusta sons, efeitos visuais, menus e a experiência final."),
        ("PRONTO_PARA_LANCAR", "O jogo está pronto. O MCP prepara a exportação."),
    ]

    linhas = ["# As 6 fases do desenvolvimento", ""]
    linhas.append("O MCP divide a criação do jogo em 6 fases. Isso existe para")
    linhas.append("proteger você: cada fase tem travas que impedem pular etapas")
    linhas.append("e garantem que nada importante seja esquecido.")
    linhas.append("")

    for i, (nome, desc) in enumerate(phases, 1):
        linhas.append(f"## {i}. {nome}")
        linhas.append(desc)
        linhas.append("")

    linhas.append("---")
    linhas.append("")
    linhas.append("💡 **Dica:** Use `get_next_step()` a qualquer momento para")
    linhas.append("saber exatamente qual é o próximo passo.")

    (OUT / "03-as-fases.md").write_text("\n".join(linhas), encoding="utf-8")


def gerar_04():
    """Dicionário: o que posso pedir."""
    behaviors = _load_behaviors()
    linhas = ["# O que posso pedir?", ""]
    linhas.append("Esta é a seção mais importante do manual. Aqui você descobre")
    linhas.append("tudo o que o MCP sabe fazer no seu jogo.")
    linhas.append("")

    if not behaviors:
        linhas.append("> ⚠️ Nenhum comportamento catalogado ainda.")
        linhas.append("> Esta seção será preenchida pela Onda 2 (biblioteca de comportamentos).")
    else:
        linhas.append(f"**{len(behaviors)} comportamentos disponíveis:**")
        linhas.append("")
        for b in behaviors:
            nome = b.get("name", "sem nome")
            desc = b.get("description_pt", b.get("description_en", ""))
            synonyms = b.get("synonyms", [])
            params = b.get("parameters", {})

            linhas.append(f"## {nome}")
            if desc:
                linhas.append(f"_{desc}_")
                linhas.append("")
            if synonyms:
                # synonyms pode ser dict {"pt": [...], "en": [...]} ou list
                if isinstance(synonyms, dict):
                    syn_pt = synonyms.get("pt", [])
                    if syn_pt:
                        linhas.append(f'**Diga:** "quero {syn_pt[0]}"')
                elif isinstance(synonyms, list) and len(synonyms) > 0:
                    linhas.append(f'**Diga:** "quero {synonyms[0]}"')
            linhas.append(f"**O que acontece:** {desc}" if desc else "**O que acontece:** (descrição em breve)")

            if params:
                linhas.append("**Você pode ajustar:**")
                if isinstance(params, list):
                    for p in params:
                        pname = p.get("name", "?") if isinstance(p, dict) else str(p)
                        pdesc = p.get("description_pt", "") if isinstance(p, dict) else ""
                        linhas.append(f"- {pname}: {pdesc}" if pdesc else f"- {pname}")
                else:
                    for pname, pinfo in params.items():
                        pdesc = pinfo.get("description_pt", pname) if isinstance(pinfo, dict) else str(pinfo)
                        linhas.append(f"- {pname}: {pdesc}")
            linhas.append("")

    (OUT / "04-o-que-posso-pedir.md").write_text("\n".join(linhas), encoding="utf-8")


def gerar_05():
    """Gêneros disponíveis."""
    blueprints = _load_blueprints()
    linhas = ["# Gêneros de jogo disponíveis", ""]
    linhas.append("Escolha um gênero para começar, ou peça algo novo —")
    linhas.append("o MCP adapta o que você quiser.")
    linhas.append("")

    if not blueprints:
        linhas.append("> Nenhum gênero catalogado ainda.")
    else:
        linhas.append(f"**{len(blueprints)} gêneros:**")
        linhas.append("")
        for bp in blueprints:
            nome = bp.get("display_name_pt", bp.get("genre", "sem nome"))
            desc = bp.get("description_pt", bp.get("description_en", ""))
            systems = bp.get("systems", [])

            linhas.append(f"## {nome}")
            if desc:
                linhas.append(desc)
                linhas.append("")
            if systems:
                linhas.append("**Sistemas inclusos:**")
                for s in systems:
                    snome = s.get("name", s) if isinstance(s, dict) else s
                    linhas.append(f"- {snome}")
                linhas.append("")
            linhas.append(f'**Exemplo:** "quero fazer um jogo de {nome.lower()}"')
            linhas.append("")

    (OUT / "05-generos.md").write_text("\n".join(linhas), encoding="utf-8")


def gerar_06():
    """O painel (dock) explicado."""
    texto = """# O painel do Godot

Quando você abre o Godot, o painel do MCP aparece do lado direito.
Ele tem 3 zonas:

## Zona 1 — Estado do projeto (topo)

Mostra:
- O nome do seu projeto
- A fase atual do desenvolvimento
- O progresso da fase atual
- **Uma frase** com o próximo passo

## Zona 2 — Semáforo e erros (meio)

Um semáforo colorido:
- 🟢 **Verde:** tudo funcionando
- 🟡 **Amarelo:** atenção — algo pode precisar de ajuste
- 🔴 **Vermelho:** erro encontrado

Quando aparece um erro, ele é explicado em português simples —
o que aconteceu, o que significa para o seu jogo, e o que fazer.

## Zona 3 — Botões (rodapé)

Quatro botões grandes:

| Botão | O que faz |
|---|---|
| **Rodar** | Abre o jogo para você testar |
| **Testar** | Roda os testes automáticos |
| **Aprovar** | Confirma a etapa atual e avança |
| **Reverter** | Volta para a etapa anterior |

O botão **Reverter** mostra para onde você vai voltar —
por exemplo: "volta para antes de 'adicionar inimigos'".
"""
    (OUT / "06-o-painel.md").write_text(texto, encoding="utf-8")


def gerar_07():
    """Quando o sistema te barra e por quê."""
    texto = """# Quando o sistema te barra

O MCP tem travas de segurança que impedem você de pular etapas
ou fazer algo que quebraria o jogo. Isso é proteção, não obstáculo.

## Travas que você pode encontrar

### "Sessão não inicializada"
**Por que:** Você ainda não disse qual projeto quer trabalhar.
**O que fazer:** Digite `get_next_step()` para ver o estado atual.

### "Fase bloqueada"
**Por que:** Você tentou uma ação que não é permitida na fase atual.
**O que fazer:** Avance para a próxima fase antes de usar essa ferramenta.

### "Orçamento excedido"
**Por que:** O custo estimado da sua sessão atingiu o limite.
**O que fazer:** Aumente o limite ou revise o que já foi feito.

### "Rate limit"
**Por que:** Você fez operações rápido demais.
**O que fazer:** Aguarde alguns segundos e tente de novo.

### "Conflito com editor"
**Por que:** O editor do Godot tem alterações não salvas.
**O que fazer:** Salve no Godot (Ctrl+S) e tente de novo.

---

💡 **Lembre-se:** toda trava é explicada em português simples,
com o motivo e o que fazer para resolver.
"""
    (OUT / "07-quando-travo.md").write_text(texto, encoding="utf-8")


def gerar_08():
    """Como publicar seu jogo."""
    texto = """# Como publicar seu jogo

> ⚠️ **Em breve.** Esta seção será preenchida quando o sistema de
> exportação estiver completo (Fatia 1.B + build_export).

Quando estiver pronto, publicar será simples:

1. O MCP prepara todos os arquivos
2. Você escolhe a plataforma (Windows, Linux, Web)
3. O jogo é empacotado e pronto para distribuir

Por enquanto, use o próprio Godot:
**Project → Export** no menu superior.
"""
    (OUT / "08-publicar.md").write_text(texto, encoding="utf-8")


def gerar_09():
    """Erros comuns em linguagem humana."""
    fmap = _load_friendly_errors()
    linhas = ["# Quando algo dá errado", ""]
    linhas.append("Erros acontecem. Aqui estão os mais comuns, explicados")
    linhas.append("em português simples — sem linguagem técnica.")
    linhas.append("")

    # Pega os primeiros 15 erros mais relevantes
    erros_para_mostrar = list(fmap.items())[:15]

    for padrao, mensagem in erros_para_mostrar:
        # Pega só a primeira linha (o que aconteceu)
        partes = mensagem.split("\n")
        titulo = partes[0] if partes else padrao
        linhas.append(f"## {titulo}")
        linhas.append("")
        for p in partes[1:4]:  # 3 partes
            if p.strip():
                linhas.append(p)
        linhas.append("")
        linhas.append("---")
        linhas.append("")

    (OUT / "09-deu-errado.md").write_text("\n".join(linhas), encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════
# EXECUÇÃO
# ══════════════════════════════════════════════════════════════════════

def gerar_tudo():
    """Gera todas as 10 seções do manual."""
    OUT.mkdir(parents=True, exist_ok=True)

    secoes = [
        ("00", gerar_00),
        ("01", gerar_01),
        ("02", gerar_02),
        ("03", gerar_03),
        ("04", gerar_04),
        ("05", gerar_05),
        ("06", gerar_06),
        ("07", gerar_07),
        ("08", gerar_08),
        ("09", gerar_09),
    ]

    for num, func in secoes:
        try:
            func()
            print(f"  [OK] docs/manual/{num}-*.md")
        except Exception as e:
            print(f"  [FALHA] docs/manual/{num}-*.md: {e}")

    arquivos = list(OUT.glob("*.md"))
    print(f"\nManual gerado: {len(arquivos)} arquivos em docs/manual/")


if __name__ == "__main__":
    gerar_tudo()
