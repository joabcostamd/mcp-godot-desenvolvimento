# Copilot Instructions — MCP Godot Agent

Este arquivo contém instruções permanentes para a IA agêntica (VS Code Copilot / DeepSeek V4 Pro)
que opera neste repositório e nos projetos Godot conectados via MCP.

---

## ⚡ ATIVAÇÃO DE GRUPOS VIRTUAIS (INÍCIO DE SESSÃO)

> **Regra fixa:** No início de **toda sessão de trabalho**, antes de qualquer outra ação,
> verifique se existem tools com prefixo `activate_` visíveis no chat (ex: `activate_scene`,
> `activate_script`, `activate_art`, etc.). Essas tools são stubs de grupos virtuais criados
> pelo VS Code Copilot quando o número total de tools do servidor MCP `godot-agent` excede o
> threshold de 128 — as tools reais do grupo ficam **inacessíveis** até que o stub seja chamado.
>
> **Procedimento:**
> 1. Liste as tools disponíveis e identifique TODAS as que começam com `activate_`.
> 2. Chame **todas** elas, uma por uma, sem exceção.
> 3. Só então prossiga com o bootstrap normal da sessão (leitura de docs, auditoria, etc.).
>
> **Exemplo:**
> ```
> # Se existirem activate_scene, activate_script, activate_art:
> 1. Chamar activate_scene → grupo scene expandido
> 2. Chamar activate_script → grupo script expandido
> 3. Chamar activate_art → grupo art expandido
> # Agora as tools reais (scene_manage, safe_write_gdscript, generate_game_art, etc.)
> # estão acessíveis e a sessão pode prosseguir normalmente.
> ```
>
> **Se NÃO existirem tools `activate_*`:** O threshold de virtualização não foi atingido
> (total de tools ≤ 128 ou o mecanismo não está ativo nesta versão do Copilot).
> Prossiga com o bootstrap normal — **não invente tools que não existem.**
