# Guia de Publicação — ONDA 4

> ⚠️ NADA PUBLICADO AINDA. Este guia é preparação para quando a ONDA 4 começar.

## 1. AssetLib (Godot)

### Pré-requisitos
- [x] `addons/mcp_addon/plugin.cfg` completo
- [x] `addons/mcp_addon/README.md` bilíngue
- [x] `addons/mcp_addon/LICENSE` (MIT)
- [x] `addons/mcp_addon/CHANGELOG.md`
- [ ] Screenshots reais (5) em `addons/mcp_addon/screenshots/`
- [ ] Ícone 128x128 (rodar `generate_icon.gd` no Godot)

### Passos
1. Tirar screenshots no Godot (dock MCP, BT editor, jogo rodando)
2. Gerar ícone: abrir `generate_icon.gd` no Godot, F6
3. Compactar: `git archive --format=zip HEAD addons/mcp_addon/ > mcp_addon.zip`
4. Subir em: https://godotengine.org/asset-library/

## 2. itch.io

### Estrutura do pacote
```
mcp-godot-agent-3.2.1/
  addons/
    mcp_addon/
    mcp_dock/
    mcp_bt_editor/
    mcp_runtime_bridge/
  example_project/
    platformer/
    rpg/
    puzzle/
    shooter/
  docs/
    getting-started.md
    tools.md
    arquitetura.md
  README.md
  LICENSE
```

### Passos
1. Criar release tag: `git tag v3.2.1`
2. Gerar ZIP: `git archive --format=zip -o mcp-godot-agent-3.2.1.zip HEAD`
3. Subir em: https://joabcostamd.itch.io/ (criar página do produto)
4. Preço: "Pay what you want" (mínimo grátis)

## 3. GitHub Releases

### Passos
1. Criar release: GitHub → Releases → Draft new release
2. Tag: `v3.2.1`
3. Título: "MCP Godot Agent v3.2.1 — Editor Visual + 4 Jogos-Exemplo"
4. Anexar ZIP do projeto

## 4. Comunidade

### Discord (template)
- Canais: `#bem-vindo`, `#projetos`, `#behaviors`, `#ajuda`, `#showcase`
- Cargos: @dev, @artista, @moderador
- Bot: notificações de GitHub → Discord

### GitHub Discussions
- Categorias: 📣 Anúncios, 💡 Ideias, ❓ Perguntas, 🎮 Showcase
- Template em `.github/DISCUSSION_TEMPLATES/`

> 📅 Alvo: ONDA 4 — quando 3 jogos de terceiros forem publicados.
