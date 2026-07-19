# 🎮 MCP Godot Agent

Servidor MCP (Model Context Protocol) para Godot Engine 4.x.
Pipeline autonomo multi-agente de desenvolvimento de jogos.

## 📊 Progresso: 57/67 fatias (85%)

![Progress](https://progress-bar.xyz/85?title=completo)

## 🚀 Features

### Pipeline de Verificacao
- Compile check, headless run, screenshot, GUT tests
- Code quality gate com gdtoolkit (gdlint + gdformat + gdradon)
- Auditoria de cenas orfas e ciclos de referencia
- 9 analises especificas de qualidade de codigo

### Seguranca
- Scan de vulnerabilidades em addons
- Verificacao de licencas (GPL/AGPL/CC incompativel)
- Scan de segredos vazados (API keys, tokens)

### Orquestracao de Agentes
- File lock entre agentes
- Fila de tarefas com dependencia
- Revisao cruzada e comparacao de outputs

### CI/CD
- GitHub Actions com verificacao completa
- Budget gate (teto de tools)
- Contract snapshot (drift de schema)

## 📦 Instalacao

```bash
pip install -r requirements.txt
```

### Dependencias principais
- `mcp>=1.0.0`
- `godot_parser>=0.1.7`
- `Pillow>=10.0.0`
- `jinja2>=3.1.0`
- `pyinstaller>=6.0.0`
- `pygltflib>=1.16.0`

## 📁 Estrutura

```
mcp-godot-desenvolvimento/
├── tools/
├── tests/
├── .github/
├── addons/
├── templates/
├── docs/
├── server.py
├── requirements.txt
├── pyproject.toml
└── ROADMAP_UNIFICADO.md
```