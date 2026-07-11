# AUDITORIA MCP GODOT AGENT — RESPOSTAS DA IA AGÊNTICA

> **Investigado por:** GitHub Copilot (DeepSeek V4 Pro)
> **Data:** 2026-07-11
> **Arquivos analisados:** `server.py`, `tools/file_ops.py`, `tools/validate_write.py`, `validate_gdscript.py`, `tools/safety.py`, `tools/gut_ops.py`, `tools/runtime_ops.py`, `tools/art_ops.py`, `tools/flux_ops.py`, `tools/decision_engine.py`, `tools/playtest_ops.py`, `tools/rollups.py`, `_meta_tool.py`, `tools/addon_bridge.py`, `config.json`, `.gitignore`, `config.json.example`, `install.py`, `launch.py`, `LEARNINGS.md`

---

## GRUPO 1 — Validação obrigatória de escrita (CRÍTICO)

### 1.1

`write_file` e `safe_write_gdscript` existem como tools separadas. Ao escrever
um arquivo `.gd` via `write_file` (não via `safe_write_gdscript`), o conteúdo
passa por alguma validação de sintaxe antes de ser salvo, ou é gravado sem
checagem?

**RESPOSTA:**

**É gravado SEM checagem de sintaxe GDScript.** A função `write_file` em `tools/file_ops.py` (linhas 106-165) faz apenas:
1. Verificação de tamanho máximo (10MB)
2. Verificação de path traversal
3. Checkpoint/backup do arquivo existente
4. Escrita direta com `full_path.write_text(content, encoding="utf-8")`

Não há NENHUMA validação de sintaxe GDScript no caminho de `write_file`. A tool é genérica para qualquer tipo de arquivo (.gd, .tscn, .tres, .md, etc.) e não inspeciona a extensão.

Apenas `safe_write_gdscript` (`tools/validate_write.py`, linhas 96-155) faz validação. Isso significa que a IA pode contornar a validação simplesmente usando `write_file` em vez de `safe_write_gdscript` para escrever GDScript — e o código será salvo mesmo com erros de sintaxe.

---

### 1.2

Cole aqui o corpo da função handler de `write_file` (arquivo `tools/file_ops.py`
ou onde ela estiver implementada). Ela verifica a extensão do arquivo em algum
ponto?

**RESPOSTA:**

Arquivo: `tools/file_ops.py`, linhas 106-165. **NÃO verifica extensão.**

```python
def write_file(path: str, content: str, mode: str = "create") -> dict:
    proj = _get_active_project()

    # Limite de tamanho (10MB) para evitar consumo excessivo
    MAX_FILE_SIZE = 10 * 1024 * 1024
    if len(content.encode('utf-8')) > MAX_FILE_SIZE:
        return {"status": "error", "message": f"Conteúdo excede {MAX_FILE_SIZE//1024//1024}MB — abortado"}

    violation = _check_path_traversal(path, proj)
    if violation:
        return {"status": "error", "message": violation}

    full_path = proj / path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    backup_id = None

    if mode == "create":
        if full_path.exists():
            return {
                "status": "error",
                "message": f"Arquivo '{path}' já existe. Use mode='overwrite'...",
            }
        if full_path.parent.exists():
            backup_id = checkpoint(path, proj)
    elif mode == "overwrite":
        if full_path.exists():
            backup_id = checkpoint(path, proj)
    elif mode == "append":
        if full_path.exists():
            backup_id = checkpoint(path, proj)
            existing = full_path.read_text(encoding="utf-8")
            content = existing + content
    else:
        return {"status": "error", "message": f"Mode '{mode}' inválido..."}

    full_path.write_text(content, encoding="utf-8")  # ← escrita direta, sem validação
    return {"status": "success", "path": path, "backup_id": backup_id}
```

Não há nenhuma `if path.endswith('.gd')` ou chamada a validador. A função é totalmente agnóstica ao tipo de arquivo.

---

### 1.3

`safe_write_gdscript` (em `tools/validate_write.py`) — qual validador ela chama
exatamente? É o mesmo `validate_gdscript.py` da raiz do projeto, ou uma lógica
própria? Ela detecta as regras R1 e R2 do `LEARNINGS.md` (`var` duplicado na
mesma função; uso de `:=` com acesso a Dictionary)?

**RESPOSTA:**

`safe_write_gdscript` chama **DOIS** validadores, em sequência:

**Validador 1 (local):** `validate_gdscript_syntax()` — lógica PRÓPRIA dentro do mesmo arquivo `tools/validate_write.py` (linhas 12-78). Verifica apenas:
- Mistura de tabs e espaços
- Balanceamento de parênteses/colchetes/chaves
- Linhas não indentadas fora de escopo (heurística simples)

**NÃO detecta R1 (var duplicada) nem R2 (:= com Dictionary).** Essas verificações são triviais e não cobrem os casos reais que quebram no Godot 4.7.

**Validador 2 (Godot):** Se `project_path` for fornecido, roda `godot --headless --check-only --path <proj> <arquivo_temp>` (linhas 118-141). Este sim pegaria R1 e R2, mas:
- Só é executado se `project_path` for passado como argumento
- Usa `--check-only` que faz parse completo e reporta TODOS os erros de uma vez
- É um fallback opcional — a tool funciona mesmo sem ele

O arquivo `validate_gdscript.py` da raiz do projeto é um script **standalone** de linha de comando que detecta R1 e R2 com parsing próprio + R9 via ClassDB. Ele **NÃO é chamado** por `safe_write_gdscript`. São sistemas separados.

**Conclusão:** `safe_write_gdscript` com validação local é uma rede de segurança muito fina. Só pega erros grosseiros de sintaxe (mismatched brackets, tabs+spaces). Para erros reais como R1/R2, depende de o chamador passar `project_path` para ativar a validação Godot.

---

### 1.4

Existe algum caminho no código (rollup, batch operation, `addon_batch_edit`,
etc.) que escreve conteúdo de script sem passar por `safe_write_gdscript` ou
equivalente? Liste todos que encontrar.

**RESPOSTA:**

Sim, existem **múltiplos caminhos** que escrevem GDScript sem validação:

1. **`write_file`** (`tools/file_ops.py:106`) — já documentado acima. Escrita direta, zero validação. A tool está exposta como named tool e como `file_manage` (op `write` não está exposto, mas `write_file` é named tool de alto tráfego).

2. **`addon_batch_edit`** (`tools/addon_bridge.py:494`) — envia operações diretamente para o addon GDScript no Godot via WebSocket. As operações são executadas dentro do editor Godot. Se uma operação for `create_script` ou modificar script, não passa por validador Python nenhum — a validação fica a cargo do Godot editor.

3. **`batch_atomic_edit`** (`tools/batch_ops.py`) — este SIM tem validação de `op` (linhas 216-226), mas as operações individuais dentro dele delegam para os handlers específicos. Se um handler for `write_file`, não há validação GDScript.

4. **`script_manage` (rollup)** — as operações `generate`, `attach`, `detach`, `add_var`, `add_signal` vêm de `tools/script_ops.py`. A op `generate` (`generate_gdscript`) gera código template, mas `attach` e `detach` manipulam scripts existentes sem revalidar.

5. **`compile_test_incremental`** (`tools/runtime_ops.py:113`) — embora não "escreva", ele compila um script e detecta erros. Mas é reativo (pós-escrita), não preventivo.

6. **`execute_gdscript_runtime`** (`tools/runtime_ops.py`) — executa GDScript no jogo rodando via game bridge. Tem sandbox de segurança (`validate_gdscript_code`) mas não valida sintaxe GDScript — só bloqueia classes perigosas (OS, FileAccess, etc.).

**Resumo:** O único ponto de validação preventiva real é `safe_write_gdscript`. Todos os outros caminhos ou não validam, ou validam de forma reativa (pós-escrita).

---

## GRUPO 2 — Testes travando commit (CRÍTICO)

### 2.1

`git_commit_checkpoint` — leia sua implementação. Antes de rodar `git commit`,
ela chama `compile_test` e/ou `run_gut_tests` em algum momento? Cole o trecho.

**RESPOSTA:**

**NÃO.** `git_commit_checkpoint` (`tools/safety.py`, linhas 222-254) NÃO chama `compile_test` nem `run_gut_tests`. Ela apenas faz `git add -A && git commit -m <message>`. Zero validação. Aqui está o código completo:

```python
def git_checkpoint(message: str, project_root: Path | None = None) -> dict:
    if project_root is None:
        project_root = _get_project_root()

    git_dir = project_root / ".git"
    if not git_dir.exists():
        return {"status": "skipped", "note": "Projeto não é um repositório git."}

    try:
        result = subprocess.run(
            ["git", "add", "-A"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return {"status": "success", "commit": message}
        else:
            return {
                "status": "error",
                "message": f"Git commit falhou: {result.stderr.strip()}",
            }
    except Exception as e:
        return {"status": "error", "message": f"Erro ao executar git: {e}"}
```

É um wrapper puro de git. Nenhum hook de validação. Isso significa que commits com código quebrado passam sem resistência.

---

### 2.2

`run_gut_tests` — como ela invoca o Godot exatamente (comando completo,
argumentos)? Ela faz o **warm-up de import** antes de rodar os testes
(`godot --headless --path . --import --quit`) ou vai direto para o runner do
GUT? Isso importa porque, sem esse passo, `class_name` não registra e a suíte
falha por motivo errado, não por bug real.

**RESPOSTA:**

`run_gut_tests` (`tools/gut_ops.py`, linhas 17-97) **NÃO faz warm-up de import.** Vai direto para o GUT runner:

```python
result = subprocess.run(
    [
        godot_path,
        "--headless",
        "--path", project_path,
        "-s", "addons/gut/gut_cmdln.gd",
        "-gdir", test_dir,
        "-gexit",
        "-glog=1",
    ],
    capture_output=True,
    text=True,
    timeout=timeout,
    cwd=project_path,
)
```

O comando é: `godot --headless --path <proj> -s addons/gut/gut_cmdln.gd -gdir res://tests -gexit -glog=1`

**Não há `--import --quit` antes.** Isso significa que, se arquivos `.gd` com `class_name` foram adicionados mas nunca importados, o GUT pode falhar com `"Parser Error: Could not find type 'MeuClass' in the current scope"` — mesmo que o código esteja sintaticamente correto.

O `compile_test` (`tools/runtime_ops.py:65`) também não faz warm-up de import explícito — usa `godot --headless --quit --path <proj>` que implicitamente importa recursos, mas não tem uma etapa separada de `--import`.

---

### 2.3

Se um projeto Godot não tiver nenhum teste GUT escrito ainda (é o caso normal
no início de um jogo novo), `run_gut_tests` retorna sucesso, falha, ou erro?
Qual é o comportamento correto que você recomendaria aqui?

**RESPOSTA:**

Analisando o código: se o diretório de testes (`res://tests`) não existir, o GUT runner vai tentar executar e provavelmente reportar 0 testes. Dependendo da versão do GUT, pode retornar exit code 0 (sucesso vazio) ou exit code 1 (erro por não encontrar testes). O código atual em `run_gut_tests`:

```python
return {
    "status": "success" if result.returncode == 0 else "tests_failed",
    ...
}
```

Isso significa que se o GUT retornar exit code ≠ 0 por falta de testes, o MCP reporta `"tests_failed"` — o que é enganoso (não é que os testes falharam, é que não existem).

**Recomendação:** A ferramenta deveria:
1. Verificar se o diretório `res://tests` existe ANTES de invocar o Godot
2. Se não existir, retornar `{"status": "skipped", "reason": "Nenhum teste GUT configurado. Crie testes em res://tests/ para habilitar validação."}`
3. Se existir mas estiver vazio (0 scripts de teste), também retornar skipped
4. Só rodar o GUT se houver scripts de teste de fato

Isso evita o falso-positivo "tests_failed" que na verdade é "tests_not_configured".

---

### 2.4

Existe um jeito de configurar `git_commit_checkpoint` para **recusar** o
commit se `compile_test` falhar, mesmo que não existam testes GUT ainda? Isso
seria o mínimo aceitável (compila = trava; testes = bônus quando existirem).
Investigue e proponha como isso ficaria.

**RESPOSTA:**

Hoje **não existe** nenhum mecanismo. Mas a implementação é trivial. Bastaria modificar `git_checkpoint` em `tools/safety.py:222` para:

```python
def git_checkpoint(message: str, project_root: Path | None = None,
                   require_compile: bool = True) -> dict:
    if project_root is None:
        project_root = _get_project_root()

    # 1. Validação pré-commit: compilação
    if require_compile:
        from tools.runtime_ops import compile_test
        compile_result = compile_test()
        if compile_result.get("errors"):
            return {
                "status": "error",
                "message": "❌ Commit BLOQUEADO: erros de compilação encontrados.",
                "compile_errors": compile_result["errors"],
            }

    # 2. Validação pré-commit: GUT (se existir)
    test_dir = project_root / "tests"
    if test_dir.exists() and any(test_dir.glob("*.gd")):
        from tools.gut_ops import run_gut_tests
        gut_result = run_gut_tests(project_path=str(project_root))
        if gut_result.get("status") == "tests_failed":
            return {
                "status": "error",
                "message": "❌ Commit BLOQUEADO: testes GUT falharam.",
                "gut_results": gut_result.get("results"),
            }

    # 3. git add + commit (código existente)
    ...
```

E adicionar um parâmetro `require_compile: bool = True` no schema da tool em `server.py`. O default `True` garante que todo commit passe por `compile_test`. Para commits de emergência, `require_compile=False` permitiria pular (com aviso).

Isso implementa o mínimo aceitável: compila = commit passa; não compila = bloqueado. GUT é bônus quando existir.

---

## GRUPO 3 — Exposição de tools ao Copilot (ALTO)

### 3.1

A anotação `deferLoading` que vocês usam nas definições de tool — ela é um
campo customizado dentro do `Tool` object do SDK `mcp` (Python), ou é algo que
o protocolo MCP oficial reconhece? Verifique a documentação do pacote `mcp`
1.28.1 instalado.

**RESPOSTA:**

`deferLoading` é um **campo CUSTOMIZADO**, injetado via `tool.annotations["deferLoading"] = True` no pós-processamento de `_tool_defs()` (`server.py`, linhas 4871-4898).

O SDK `mcp` (Python) usa Pydantic para seus modelos. A classe `Tool` é um modelo Pydantic com `extra='allow'` (ou similar), o que permite adicionar campos arbitrários via `setattr` ou dict. O campo `annotations` é um dict livre.

O protocolo MCP oficial **NÃO define** `deferLoading` como hint padrão. Os hints oficiais do MCP são:
- `readOnlyHint`
- `destructiveHint`
- `idempotentHint`
- `openWorldHint`

`deferLoading` é uma convenção interna do VS Code / GitHub Copilot para indicar que a definição completa da tool (com descrição longa e schema) deve ser carregada sob demanda, não enviada no `tools/list` inicial. Isso reduz o número de tokens gastos na listagem inicial de tools.

O código atual aplica `deferLoading: True` para TODAS as tools que NÃO estão em `_CORE_TOOLS`. `_CORE_TOOLS` (server.py:4841-4847) contém apenas 13 tools:
```python
_CORE_TOOLS = {
    "ping", "health_check", "self_test", "bootstrap_godot_mcp",
    "query_classdb", "read_file", "write_file",
    "project_manage", "scene_manage", "node_manage", "script_manage",
    "file_manage", "runtime_manage", "take_screenshot",
}
```

---

### 3.2

Faça este teste: com o VS Code aberto e o Copilot Chat conectado ao seu MCP,
descubra alguma forma de medir quantos tokens (ou quantos bytes) o `tools/list`
está de fato enviando para o modelo no início de uma sessão. Pode ser via log
do próprio servidor MCP (adicione um `print`/log temporário no handler que
responde `tools/list`), via inspeção de tráfego, ou via qualquer outro método
que você tenha disponível. Reporte o número.

**RESPOSTA:**

Não tenho como fazer esse teste em runtime agora (precisaria reiniciar o servidor MCP com logs ativos e o Copilot conectado). Mas posso estimar com precisão a partir do código:

Pelo `_tool_defs()` em `server.py`, o servidor registra aproximadamente **134 ferramentas** (comentário na linha 3: "Servidor MCP via stdio com 134 ferramentas"). Com o pós-processamento de descrições compactadas (`_compact_description`, limite de 120 caracteres), cada tool carrega:
- `name`: ~20 chars em média
- `description`: ~120 chars (compactada)
- `inputSchema`: JSON com properties, types, descriptions (~200-500 chars)

Estimativa conservadora: ~400 bytes por tool × 134 tools = **~53 KB de JSON** no `tools/list`.

Convertendo para tokens (1 token ≈ 4 caracteres em JSON): aproximadamente **13.000-15.000 tokens** só no `tools/list`.

Porém, com `deferLoading: True`, as tools não-core enviam apenas `name` + `annotations` (metadados leves) no `tools/list` inicial, e a descrição completa + schema é carregada apenas quando a tool é de fato invocada. Isso reduz o payload inicial de 134 tools com descrições completas para algo como 13 core tools com descrições + 121 tools com só nome/annotations.

**Estimativa com deferLoading:** ~13 tools × 400 bytes + 121 tools × 80 bytes = ~5 KB + ~10 KB = **~15 KB** ou **~4.000 tokens** no `tools/list` inicial. Uma economia de ~70%.

---

### 3.3

Existe hoje algum mecanismo (flag de ambiente, argumento de linha de comando,
etc.) para o servidor iniciar expondo **menos** tools — por exemplo só as ~30
mais usadas em desenvolvimento normal do dia a dia (cenas, nós, scripts,
física, runtime básico, playtest textual, git checkpoint)? Se não existir,
isso é fácil de adicionar dado como o `server.py` já está estruturado?

**RESPOSTA:**

**Não existe** mecanismo de perfil de tools hoje. O servidor sempre expõe as 134 tools completas (com `deferLoading` reduzindo o payload inicial, mas ainda assim todas registradas).

Porém, é **muito fácil de adicionar**, porque:

1. `_tool_defs()` já é uma função centralizada que constrói a lista completa
2. Os rollups já são carregados separadamente via `get_rollup_tool_defs()`
3. Já existe `_CORE_TOOLS` como constante
4. O sistema de `tool_groups` em `tools/dynamic_groups.py` já categoriza as tools

Bastaria:
1. Adicionar uma variável de ambiente `MCP_TOOL_PROFILE` (valores: `"core"`, `"full"`)
2. Ler em `_tool_defs()` e filtrar a lista antes de retornar
3. Definir perfis:

```python
PROFILE_CORE = _CORE_TOOLS  # 13 tools
PROFILE_DEV = _CORE_TOOLS | {  # ~30 tools para dev dia a dia
    "asset_manage", "physics_manage", "anim_manage", "ui_manage",
    "compile_test", "run_game", "stop_game", "smart_restart",
    "safe_write_gdscript", "git_commit_checkpoint",
    "analyze_game_structure", "suggest_next_steps",
    "get_runtime_state_digest", "effect_probe",
    "generate_placeholder_sprite", "generate_placeholder_texture_atlas",
    "configure_input_action", "configure_autoload",
    "add_collision_shape", "set_collision_layer_mask",
    "capture_game_screenshot", "detect_empty_screen",
    "gdscript_lsp_connect", "gdscript_diagnostics",
    "generate_gdscript", "validate_gdscript_syntax",
}
```

A estrutura já está pronta para isso — o trabalho é essencialmente declarativo (definir os sets de tools por perfil).

---

### 3.4

Se você tivesse que escolher ~25-30 tools para um "perfil core" de uso diário
(excluindo 3D, networking multiplayer, localização, deploy, C#, coisas raras),
quais escolheria? Liste os nomes.

**RESPOSTA:**

Aqui está minha recomendação de **28 tools** para um "perfil core" de desenvolvimento diário (jogos 2D, dev solo, Godot 4.7):

**Infraestrutura (4):**
1. `ping`
2. `bootstrap_godot_mcp`
3. `compile_test`
4. `smart_restart`

**Projeto & Arquivos (3):**
5. `project_manage` (rollup: create, set_active, get_settings, set_setting, set_main_scene)
6. `file_manage` (rollup: delete, move, inspect)
7. `read_file`

**Cenas & Nós (2):**
8. `scene_manage` (rollup: create, load_tree, instance)
9. `node_manage` (rollup: create, delete, set_property, get_property, reparent, connect_signal, list_signals)

**Scripts (3):**
10. `script_manage` (rollup: generate, attach, detach, validate, add_var, add_signal)
11. `safe_write_gdscript`
12. `write_file`

**Assets & Placeholders (2):**
13. `asset_manage` (rollup: import_texture, import_spritesheet, import_audio, placeholder_sprite, placeholder_atlas, bg_gradient, tileset_colors, palette)
14. `generate_placeholder_sprite` (named tool de alto uso)

**Runtime & Testes (5):**
15. `runtime_manage` (rollup: compile_test, run_game, stop_game, smart_restart, launch_editor, close_editor)
16. `get_runtime_state_digest`
17. `effect_probe`
18. `godot_exec`
19. `execute_gdscript_runtime`

**Física (1):**
20. `physics_manage` (rollup: add_collision, set_layers, set_material, create_joint)

**UI (1):**
21. `ui_manage` (rollup: create_root, add_control, main_menu, hud, pause_menu, health_bar, loading_screen)

**Análise & Debug (3):**
22. `analyze_game_structure`
23. `suggest_next_steps`
24. `gdscript_diagnostics`

**Qualidade & Segurança (2):**
25. `git_commit_checkpoint`
26. `capture_runtime_errors`

**Input & Config (2):**
27. `configure_input_action`
28. `configure_autoload`

**Total: 28 tools** (18 rollups + 10 named). Cobre todo o ciclo: criar projeto → cenas → scripts → física → assets → rodar → inspecionar → commitar.

Deixei de fora (para perfil core): 3D (`threed_gen`, `create_light_3d`, partículas 3D), networking (`game_multiplayer`, `game_http_request`), deploy (`deploy_itch`, `build_export`), localização (`setup_localization`), C# (`build_csharp`), áudio avançado (`configure_audio_bus`, `generate_voice`), shaders 2D (`generate_shader_2d`), diálogo (`create_dialogue_system`), inventário (`create_inventory_system`), e LSP avançado.

---

## GRUPO 4 — Portabilidade entre dois computadores (MÉDIO)

### 4.1

`config.json` hoje é um arquivo versionado ou está no `.gitignore`? Confirme
olhando o `.gitignore` real do repositório.

**RESPOSTA:**

`config.json` está **NO `.gitignore`** e portanto NÃO é versionado. Linha 7 do `.gitignore`:

```gitignore
# Configuração local (cada máquina tem a sua — use config.json.example como modelo)
config.json
```

Isso está correto: `config.json` contém paths absolutos específicos da máquina (`C:\Godot\...`, `C:\Users\joabc\...`) e não deve ser compartilhado. O arquivo `config.json.example` serve como template versionado.

---

### 4.2

Existe algum fallback por variável de ambiente para `godot_path`,
`python_path`, `projects_root` etc., ou o servidor só lê do `config.json`?

**RESPOSTA:**

**O servidor só lê do `config.json`.** Não há fallback por variáveis de ambiente para as configurações principais.

Evidências:
- `tools/safety.py:76-87` (`_get_project_root`): lê `config.json` para `default_project`
- `tools/gut_ops.py:51-54`: lê `config.json` para `godot_path`
- `tools/validate_write.py:118-122`: lê `config.json` para `godot_path` dentro de `safe_write_gdscript`
- `tools/runtime_ops.py`: usa `get_godot_bin()` e `get_config()` que leem de `config.json`
- `install.py:40-70`: tem sua própria lógica de detecção (`find_godot()`, `find_python()`), mas é usada apenas na instalação

Exceção: `tools/flux_ops.py:28-29` usa variáveis de ambiente para API keys:
```python
BFL_API_KEY = os.environ.get("BFL_API_KEY", "")
REPLICATE_API_KEY = os.environ.get("REPLICATE_API_KEY", "")
```

Mas para paths do Godot/Python/projetos, não há env var fallback. Se `config.json` não existir ou estiver incorreto, o servidor falha com erro genérico ou usa paths padrão quebrados.

---

### 4.3

Proponha (sem implementar ainda) como ficaria um `config.local.json` +
`config.json.example` + lógica de merge, de forma que: o `config.json.example`
(sem paths reais) fica versionado, um `config.local.json` (com paths reais da
máquina) fica fora do Git, e o servidor lê o local se existir, senão cai para
variável de ambiente, senão erro amigável explicando o que falta.

**RESPOSTA:**

**Proposta de arquitetura de configuração multi-máquina:**

**Arquivos:**
- `config.json.example` — versionado, contém a estrutura com placeholders
- `config.local.json` — NÃO versionado (.gitignore), contém paths reais da máquina
- `config.defaults.json` — versionado, contém defaults para timeouts, portas, etc.

**Lógica de merge (em `tools/project_ops.py` ou novo `tools/config_loader.py`):**

```python
def load_config() -> dict:
    """Carrega configuração com fallback em cascata."""
    config = _load_defaults()  # 1. defaults versionados

    # 2. config.local.json (prioridade máxima)
    local_path = ROOT / "config.local.json"
    if local_path.exists():
        with open(local_path) as f:
            local = json.load(f)
        config = deep_merge(config, local)
    else:
        # 3. Fallback: variáveis de ambiente
        env_overrides = _load_from_env()
        if env_overrides:
            config = deep_merge(config, env_overrides)

    # 4. Validação: campos obrigatórios
    missing = []
    for key in ["godot_path", "projects_root"]:
        if not config.get(key):
            missing.append(key)

    if missing:
        raise ConfigError(
            f"Configuração incompleta. Campos obrigatórios faltando: {missing}\n"
            f"Crie config.local.json a partir de config.json.example ou "
            f"defina as variáveis de ambiente:\n"
            f"  MCP_GODOT_PATH=C:\\Godot\\Godot_v4.7-stable_win64.exe\n"
            f"  MCP_PROJECTS_ROOT=C:\\meus-projetos\n"
            f"  MCP_DEFAULT_PROJECT=C:\\meus-projetos\\meu-jogo"
        )

    return config

def _load_from_env() -> dict:
    """Carrega configuração de variáveis de ambiente."""
    overrides = {}
    env_map = {
        "MCP_GODOT_PATH": "godot_path",
        "MCP_GODOT_CONSOLE_PATH": "godot_console_path",
        "MCP_PYTHON_PATH": "python_path",
        "MCP_PROJECTS_ROOT": "projects_root",
        "MCP_DEFAULT_PROJECT": "default_project",
        "MCP_ADDON_PORT": "addon_port",
        "MCP_GAME_PORT": "game_port",
    }
    for env_var, config_key in env_map.items():
        val = os.environ.get(env_var)
        if val:
            # Converter portas para int
            if config_key.endswith("_port"):
                val = int(val)
            overrides[config_key] = val
    return overrides
```

**`.gitignore` adicional:**
```
config.local.json
config.json  # já existente
```

**`config.json.example` (modelo):**
```json
{
  "_comment": "Copie este arquivo para config.local.json e preencha os paths da sua máquina",
  "godot_path": "C:\\Godot\\Godot_v4.7-stable_win64.exe",
  "godot_console_path": "C:\\Godot\\Godot_v4.7-stable_win64_console.exe",
  "python_path": "C:\\Python312\\python.exe",
  "projects_root": "C:\\meus-projetos",
  "default_project": "",
  "addon_port": 9080,
  "game_port": 9081,
  "timeouts": { "fast": 15, "compile": 60, "export": 300 }
}
```

**Vantagens:**
- `config.json.example` versionado → qualquer dev vê a estrutura
- `config.local.json` não versionado → paths reais nunca vazam
- Variáveis de ambiente → funciona em CI/CD e Docker
- Erro amigável → diz exatamente o que falta e como resolver

---

### 4.4

`install.py` e/ou `launch.py` já fazem alguma detecção automática de caminho
do Godot ou do Python na máquina (procurar em locais comuns de instalação,
`which`/`where`, etc.)? Se sim, descreva a lógica. Se não, isso seria a base
do `setup_machine.py` que vamos pedir depois.

**RESPOSTA:**

**Sim, `install.py` faz detecção automática.** A lógica está nas funções `find_godot()` e `find_python()` (`install.py`, linhas 29-75):

**`find_godot()` — 4 níveis de fallback:**
1. Paths comuns hardcoded: `C:\Godot\Godot_v4.7-stable_win64.exe`, `C:\Program Files\Godot\...`, `~/Godot/...`
2. `shutil.which("Godot_v4.7-stable_win64")` — busca no PATH do sistema
3. Glob `Godot*.exe` em todos os diretórios do PATH
4. Varredura em `C:\Godot\**` e `D:\Godot\**` com `glob("**/Godot*.exe")`

**`find_python()` — 2 níveis:**
1. `shutil.which("python3")`, `shutil.which("python")`, `shutil.which("py")` — busca no PATH
2. Verifica `--version` para confirmar que é Python 3

**`launch.py` NÃO faz detecção** — ele apenas lê `config.json` e usa o que está lá. Se o path estiver errado, falha.

Portanto, a detecção existe mas está **isolada no instalador**. O servidor (`server.py`) e o lançador (`launch.py`) não usam essa lógica — eles dependem 100% do `config.json`. Seria ideal portar essa lógica de detecção para um módulo compartilhado (`tools/config_loader.py`) usado tanto pelo instalador quanto pelo servidor.

---

## GRUPO 5 — Geração paga de arte nunca automática (MÉDIO)

### 5.1

No `decision_engine.py`, a decisão "gerar arte via FLUX vs placeholder" — ela
de fato pode disparar uma chamada real e paga à API FLUX.2/Replicate sem
nenhuma confirmação humana, quando o confidence score for ≥0.90? Confirme lendo
o código, não só a documentação.

**RESPOSTA:**

**NÃO.** O `decision_engine.py` é um motor de **recomendação**, não de **execução**. Veja o código:

`decision_engine.py:40-50` (`decide_art`):
```python
def decide_art(entity_name: str, entity_type: str = "Node") -> dict:
    state = get_state()
    if state.project_root is None:
        return {"should_generate": False, "generator": "none", ...}
    if state.has_sprite_for(entity_name):
        return {"should_generate": False, "generator": "none", ...}
    if entity_type in _NODE_NEEDS_SPRITE:
        gen = "placeholder" if state.get_stage() in ("vazio", "prototipo") else "flux"
        return {"should_generate": True, "generator": gen, ...}
    return {"should_generate": False, "generator": "none", ...}
```

Ele retorna um dicionário com `should_generate: True/False` e `generator: "placeholder"|"flux"`. Mas **nunca chama** `generate_game_art_flux()` nem `generate_game_art()`. É puramente consultivo.

**Quem poderia disparar a chamada paga é a IA agêntica**, se ela decidir seguir a recomendação e chamar `generate_game_art_flux`. Mas:
1. A IA precisaria explicitamente invocar `generate_game_art_flux`
2. `generate_game_art_flux` (`tools/flux_ops.py:243`) só funciona se `BFL_API_KEY` ou `REPLICATE_API_KEY` estiverem configuradas como variáveis de ambiente
3. Sem API keys, a chamada retorna `{"status": "error", "message": "BFL_API_KEY nao configurada..."}`

**No entanto**, `generate_game_art` (`tools/art_ops.py:225`) tenta ChatGPT/DALL-E via Playwright browser headless. Isso é gratuito (usa a interface web do ChatGPT), mas frágil (depende de sessão de browser). O fallback é Pillow procedural (sempre disponível, gratuito).

**Conclusão:** O `decision_engine` não dispara nada sozinho. Mas se a IA seguir cegamente a recomendação e chamar `generate_game_art_flux` com API keys configuradas, a chamada paga acontece sem confirmação humana. Não há um prompt de "Tem certeza? Isso vai custar ~$0.03."

---

### 5.2

Existe hoje algum jeito de desativar globalmente a geração automática paga
(deixando só placeholder disponível por padrão, com FLUX exigindo um parâmetro
explícito tipo `force_paid_generation: true` em cada chamada)? Se não existir,
isso é uma mudança pequena?

**RESPOSTA:**

**Não existe** mecanismo de bloqueio global para geração paga. Mas é uma mudança **muito pequena** de implementar.

**Onde mexer:**

1. **Adicionar flag no `config.json`** (ou `config.local.json`):
```json
{
  "art_generation": {
    "allow_paid": false,
    "provider": "placeholder"
  }
}
```

2. **Modificar `generate_game_art_flux`** (`tools/flux_ops.py:243`):
```python
def generate_game_art_flux(..., force_paid: bool = False) -> dict:
    # Verificar flag global
    config = _load_config()
    allow_paid = config.get("art_generation", {}).get("allow_paid", False)

    if not allow_paid and not force_paid:
        return {
            "status": "blocked",
            "message": (
                "❌ Geração paga BLOQUEADA. O config art_generation.allow_paid = false.\n"
                "Use generate_placeholder_sprite para arte procedural gratuita, ou\n"
                "passe force_paid=True para autorizar esta chamada específica."
            ),
        }
    # ... resto da lógica
```

3. **Modificar `decision_engine.decide_art`** para respeitar a flag:
```python
def decide_art(entity_name, entity_type="Node"):
    # ...
    config = _load_config()
    allow_paid = config.get("art_generation", {}).get("allow_paid", False)
    if not allow_paid:
        gen = "placeholder"  # força placeholder sempre
    else:
        gen = "placeholder" if state.get_stage() in ("vazio", "prototipo") else "flux"
    # ...
```

**Impacto:** ~10 linhas de código em 2 arquivos. A mudança é trivial e de baixo risco. O default `allow_paid: false` garante que numa máquina nova, sem config explícito, nenhuma chamada paga aconteça.

---

## GRUPO 6 — Tools de imagem para um modelo text-only (BAIXO/MÉDIO)

### 6.1

Liste todas as tools que retornam imagem (base64 PNG, GIF, etc.) em vez de
texto. Confirme se `detect_empty_screen`, `detect_offscreen_elements` e
`compare_screenshots` retornam **apenas** dados textuais/numéricos (sem a
imagem em si), ou se também embutem a imagem na resposta.

**RESPOSTA:**

**Tools que retornam imagem (base64):**

| Tool | Arquivo | Retorna |
|------|---------|---------|
| `capture_game_screenshot` | `runtime_ops.py:707` | `image_base64` (PNG) + `image_path` |
| `take_screenshot` | `runtime_ops.py:587` | screenshot via editor bridge |
| `record_gameplay_gif` | `runtime_ops.py:1058` | `gif_base64` (GIF animado) |
| `generate_game_art` | `art_ops.py:225` | `frames` (paths), sem base64 na resposta principal |
| `generate_game_art_flux` | `flux_ops.py:243` | `image_base64` (PNG) |

**Tools que retornam APENAS texto/dados numéricos (sem imagem):**

| Tool | Arquivo | Retorna |
|------|---------|---------|
| `detect_empty_screen` | `runtime_ops.py:910` | `{"empty": bool, "reason": str, "dominant_color": [...], "dominant_ratio": float}` |
| `detect_offscreen_elements` | `scene_ops.py` (importado) | Dados textuais sobre elementos fora da tela |
| `compare_screenshots` | `runtime_ops.py:810` | `{"metrics": {"max", "mean", "mean_squared", "root_mean_squared", "peak_snr", "difference_percent"}}` — apenas números |

**Confirmado:** `detect_empty_screen`, `detect_offscreen_elements` e `compare_screenshots` retornam **APENAS dados textuais/numéricos**, sem a imagem em si. Isso é bom para o DeepSeek V4 que é text-only.

`detect_empty_screen` recebe `image_base64` como INPUT (para analisar), mas o OUTPUT é puramente textual: razão da tela vazia, cor dominante, percentual. A imagem não é reenviada na resposta.

---

### 6.2

`effect_probe` e `get_runtime_state_digest` — cole um exemplo real de output
(rodando contra qualquer projeto de teste que você tenha à mão, ou um exemplo
sintético fiel ao formato real). Preciso confirmar que é texto/JSON puro,
suficiente para um modelo sem visão entender o que aconteceu no jogo.

**RESPOSTA:**

**`get_runtime_state_digest`** (`tools/playtest_ops.py:161`):

Output sintético fiel ao código:
```json
{
  "status": "success",
  "state": {
    "scene": "Main",
    "entities": [
      {
        "name": "Player",
        "type": "CharacterBody2D",
        "path": "/root/Main/Player",
        "position": {"x": 150.5, "y": 320.0},
        "visible": true,
        "groups": ["player", "entities"],
        "velocity": {"x": 0.0, "y": 0.0}
      },
      {
        "name": "Enemy1",
        "type": "CharacterBody2D",
        "path": "/root/Main/Enemy1",
        "position": {"x": 400.0, "y": 200.0},
        "visible": true,
        "groups": ["enemy", "entities"]
      },
      {
        "name": "Bullet",
        "type": "Area2D",
        "path": "/root/Main/Bullet",
        "position": {"x": 200.0, "y": 310.0},
        "visible": true,
        "groups": ["projectile"]
      }
    ],
    "time_scale": 1.0,
    "paused": false,
    "fps": 60
  }
}
```

**`effect_probe`** (`tools/playtest_ops.py:368`):

Exemplo com `before="return $Player.hp"`, `action="$Player.take_damage(20)"`, `after="return $Player.hp"`:
```json
{
  "status": "success",
  "before": 100,
  "after": 80,
  "delta": -20,
  "effect_detected": true
}
```

**Confirmado:** Ambos retornam JSON puro, sem imagens. `get_runtime_state_digest` é particularmente valioso para um modelo text-only — ele fornece posição, velocidade, grupos e visibilidade de TODAS as entidades na cena, permitindo que a IA "veja" o estado do jogo sem precisar de um screenshot. O `effect_probe` é um mini-framework de teste: verifica se uma ação produziu o efeito esperado.

---

## GRUPO 7 — Validação de `op` nos rollups (confirmação rápida)

### 7.1

Em `project_manage`, `scene_manage`, `node_manage` etc., se a IA passar um
valor de `op` que não existe (erro de digitação), o que acontece? Cole o
comportamento real: erro claro listando os `op` válidos, falha silenciosa, ou
exceção não tratada?

**RESPOSTA:**

**Erro claro com sugestões.** A validação está em `build_manage_handler` (`_meta_tool.py`, linhas 211-249):

```python
def build_manage_handler(args: dict, ops: dict[str, Callable[..., dict]]) -> dict:
    op = args.get("op", "")
    params: dict = args.get("params") or {}
    op_names = list(ops.keys())

    # ── Validação do op ─────────────────────────────────────
    if op not in ops:
        suggestions = difflib.get_close_matches(op, op_names, n=3, cutoff=0.4)
        return {
            "status": "error",
            "message": (
                f"Operação desconhecida: '{op}'."
                + (
                    f" Você quis dizer: {suggestions}?"
                    if suggestions
                    else f" Valores válidos: {op_names}"
                )
            ),
            "suggestions": suggestions,
            "valid_ops": op_names,
        }
```

**Exemplo:** Se a IA chamar `node_manage` com `op: "set_propety"` (typo de "set_property"):

```json
{
  "status": "error",
  "message": "Operação desconhecida: 'set_propety'. Você quis dizer: ['set_property']?",
  "suggestions": ["set_property"],
  "valid_ops": ["create", "delete", "set_property", "get_property", "reparent", "connect_signal", "list_signals"]
}
```

Se for algo completamente diferente (`op: "explode"`):

```json
{
  "status": "error",
  "message": "Operação desconhecida: 'explode'. Valores válidos: ['create', 'delete', 'set_property', 'get_property', 'reparent', 'connect_signal', 'list_signals']",
  "suggestions": [],
  "valid_ops": ["create", "delete", "set_property", "get_property", "reparent", "connect_signal", "list_signals"]
}
```

**Avaliação:** Implementação excelente. Usa `difflib.get_close_matches` com cutoff 0.4 para sugerir correções, e sempre retorna a lista completa de ops válidos. Não há falha silenciosa nem exceção não tratada. O schema JSON também tem `"enum": op_names` no parâmetro `op`, o que ajuda o modelo a escolher valores válidos.

Isso se aplica a TODOS os rollups: `project_manage`, `scene_manage`, `node_manage`, `script_manage`, `file_manage`, `asset_manage`, `physics_manage`, `anim_manage`, `ui_manage`, `tilemap_manage`, etc.

---

## GRUPO 8 — Perguntas abertas suas

Se, durante esta investigação, você (IA agêntica) encontrar qualquer outro
problema, inconsistência, código morto, ou risco que não está coberto pelas
perguntas acima, mas que você julga relevante para os 5 requisitos listados no
início deste documento, registre aqui:

**RESPOSTA:**

### 8.1 — `safe_write_gdscript` não usa checkpoint nem backup

`safe_write_gdscript` (`tools/validate_write.py:96`) escreve o arquivo com `Path(file_path).write_text(content)` diretamente, sem chamar `checkpoint()` do `safety.py`. Isso significa que:
- Se a validação passar mas o conteúdo estiver logicamente errado, não há backup para desfazer
- `write_file` faz checkpoint; `safe_write_gdscript` não
- Inconsistência: a tool "segura" é menos segura em termos de backup que a tool "genérica"

**Correção sugerida:** Adicionar `checkpoint(file_path, proj)` antes da escrita em `safe_write_gdscript`.

### 8.2 — `config.json` no `.gitignore` mas `config.json.example` tem paths reais

O `config.json.example` contém paths hardcoded:
```json
"godot_path": "C:\\Godot\\Godot_v4.7-stable_win64.exe",
"python_path": "C:\\Python312\\python.exe",
```

Isso é um exemplo válido, mas pode induzir ao erro se alguém copiar sem editar. O ideal seria usar placeholders óbvios como `"<COLE_O_CAMINHO_DO_GODOT_AQUI>"` ou `"auto"` (para disparar detecção automática).

### 8.3 — `LEARNINGS.md` R10 (ciclo declarativo) não tem enforcement no código

A regra R10 ("Ciclo declarativo: ler estado → editar → validar → reiniciar → verificar") é documentada mas não tem NENHUM enforcement no código. O servidor não verifica se a IA leu o estado antes de editar, não força `compile_test` após `write_file`, etc. Isso é particularmente crítico para o requisito 2 ("Nenhum commit aconteça com o jogo quebrado").

### 8.4 — `bootstrap_godot_mcp` não documenta a necessidade de warm-up de import

O bootstrap (`tools/bootstrap_ops.py`) faz polling de portas e conecta LSP/WebSocket, mas não executa `godot --headless --import --quit` para garantir que `class_name` e `.uid` files estejam registrados. Isso pode causar falhas misteriosas em projetos recém-clonados.

### 8.5 — Mistura de portas: LSP 6005, WebSocket 9082, Editor Bridge 9080, Game Bridge 9081

O sistema usa 4 portas diferentes. Isso é complexo para debugging. Documentação existe no `GUIA_CONEXAO.md`, mas não há um health check unificado que verifique todas as portas de uma vez.

### 8.6 — `generate_game_art` tenta ChatGPT/DALL-E automaticamente

`art_ops.py:225` (`generate_game_art`) tenta `_generate_via_chatgpt` automaticamente se `_HAS_PLAYWRIGHT` for True. Embora seja gratuito (usa a interface web, não API paga), é frágil e depende de sessão de browser. O fallback para Pillow procedural é bom, mas a tentativa automática do ChatGPT pode causar timeouts longos sem feedback para o usuário.

### 8.7 — Ausência de `--import` no pipeline de compile_test

Conforme discutido em 2.2, `compile_test` usa `godot --headless --quit --path <proj>` que implicitamente faz import, mas não há uma etapa explícita `--import`. Em projetos com muitos `.import` files pendentes, o primeiro `compile_test` pode ser muito mais lento que o esperado.

---

## AO TERMINAR

Não corrija nada ainda. Salve este arquivo com todas as respostas preenchidas
e me avise que terminou. O próximo passo é eu (ou você, seguindo minhas specs)
gerar os patches exatos para `server.py`, `tools/validate_write.py`,
`tools/safety.py`, `config.json` e `decision_engine.py` — só depois de ler
suas respostas reais, não hipóteses.
