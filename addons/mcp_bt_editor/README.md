# MCP BT Editor — Editor Visual de Behavior Trees

Editor visual de Behavior Trees integrado ao Godot 4.7.
Montagem de comportamentos por drag-and-drop, depuração ao vivo e exportação GDScript.

## Funcionalidades

- 🎨 **16 features** — 100% GDScript nativo, zero C++
- 🧩 **249 behaviors** na paleta (via `behavior.json`)
- 🔗 **4 tipos de portas** coloridas: FLOW (azul), CONDITION (amarelo), DATA (verde), EVENT (vermelho)
- ✅ **Validação de conexões** por tipo + detecção de ciclos (DAG)
- ⟐ **Reroute nodes** — organização pura de conexões
- 📐 **Expression nodes** — GDScript de uma linha
- 🔀 **Auto-Arrange** — layout hierárquico automático
- 📋 **Export GDScript** — código compatível com `behavior_tree.gd`
- 💾 **Salvar/Carregar** `.tres` Resource
- 🔍 **Inspetor** — edição de parâmetros por behavior
- 🐛 **Debugger ao vivo** — breakpoints visuais, watch window, destaque de nós ativos
- ↩️ **Undo/Redo** via `EditorUndoRedoManager`
- 📁 **GraphFrame** — agrupamento de nós relacionados
- 🗺️ **Minimap** — ativado para árvores com >10 nós

## Instalação

1. Copie a pasta `addons/mcp_bt_editor/` para o diretório `addons/` do seu projeto Godot
2. Ative o plugin em `Project > Project Settings > Plugins > MCP BT Editor`
3. Acesse pelo dock inferior direito ou menu `Project > MCP BT Editor`

## Requisitos

- Godot 4.7+
- Projeto com behaviors no formato `behavior.json` em `behaviors/`

## Estrutura

```
addons/mcp_bt_editor/
  plugin.cfg                 — Metadados
  bt_editor_plugin.gd        — EditorPlugin principal
  bt_editor_node.gd          — GraphNode customizado
  bt_editor_palette.gd       — Paleta com busca e categorias
  bt_editor_graph.gd         — GraphEdit com validação
  bt_editor_inspector.gd     — Inspetor de parâmetros
  bt_editor_serializer.gd    — Salvar/Carregar .tres + Export GDScript
  bt_editor_debugger.gd      — Debug ao vivo (WebSocket 9082)
  bt_tree_resource.gd        — Resource para persistência
  icons/                     — Ícones por categoria
```

## Uso

1. Abra o dock **MCP BT Editor**
2. Arraste behaviors da **paleta** (esquerda) para o **grafo** (centro)
3. Conecte as **portas coloridas** entre os nós
4. Edite **parâmetros** no inspetor (direita)
5. Use a **toolbar** para salvar, carregar, exportar
6. Ative o **debugger** (abaixo do inspetor) para depuração ao vivo

## Licença

MIT — veja `LICENSE` na raiz do projeto.
