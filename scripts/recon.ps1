$ErrorActionPreference='Continue'
$out=Join-Path $PWD 'RECON_MCP.md'
Remove-Item $out -ErrorAction SilentlyContinue
$py = Get-ChildItem -Recurse -Filter *.py -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch '\\(\.venv|__pycache__|node_modules)\\' }
function B([string]$n,[string]$t,[scriptblock]$s){
  "" | Out-File -Append -Encoding utf8 $out
  "== BLOCO $n : $t ==" | Out-File -Append -Encoding utf8 $out
  $r = try { & $s 2>&1 | Out-String } catch { "ERRO: " + $_.Exception.Message }
  if([string]::IsNullOrWhiteSpace($r)){ $r = 'NAO ENCONTRADO / VAZIO' }
  $r.TrimEnd() | Out-File -Append -Encoding utf8 $out
}
B 01 'DATA E LOCAL' { Get-Date; "PWD=$PWD"; "USER=$env:USERNAME" }
B 02 'VSCODE E EXTENSOES' { code --version; code --list-extensions --show-versions | Select-String -Pattern 'copilot|cline|continue|mcp' }
B 03 'SETTINGS.JSON' { Get-Content "$env:APPDATA\Code\User\settings.json" -Raw }
B 04 'MCP.JSON GLOBAL' { Get-Content "$env:APPDATA\Code\User\mcp.json" -Raw }
B 05 'MCP.JSON LOCAL' { Get-Content ".vscode\mcp.json" -Raw }
B 06 'PROMPTS GLOBAIS LISTA' { Get-ChildItem "$env:APPDATA\Code\User\prompts" | Select-Object Name,Length,LastWriteTime | Format-Table -AutoSize }
B 07 'PLAN.PROMPT.MD' { Get-Content "$env:APPDATA\Code\User\prompts\plan.prompt.md" -Raw }
B 08 'ACT.PROMPT.MD' { Get-Content "$env:APPDATA\Code\User\prompts\act.prompt.md" -Raw }
B 09 'SEGUIR-ROADMAP.PROMPT.MD' { Get-Content "$env:APPDATA\Code\User\prompts\seguir-roadmap.prompt.md" -Raw }
B 10 'AUDIT.PROMPT.MD' { Get-Content "$env:APPDATA\Code\User\prompts\audit.prompt.md" -Raw }
B 11 'HANDOFF.PROMPT.MD' { Get-Content "$env:APPDATA\Code\User\prompts\handoff.prompt.md" -Raw }
B 12 'ENCERRAR.PROMPT.MD' { Get-Content "$env:APPDATA\Code\User\prompts\encerrar.prompt.md" -Raw }
B 13 'COPILOT CONFIG ARVORE' { Get-ChildItem "$HOME\.copilot" -Recurse -File | Select-Object FullName,Length | Format-Table -AutoSize }
B 14 'SEGURANCA.JSON' { Get-Content "$HOME\.copilot\hooks\seguranca.json" -Raw }
B 15 'HOOKS SCRIPTS' { Get-ChildItem "$HOME\.copilot\hooks\scripts\*.ps1" | ForEach-Object { "----- " + $_.Name + " -----"; Get-Content $_.FullName -Raw } }
B 16 'SKILL FW-INIT' { Get-Content "$HOME\.copilot\skills\fw-init\SKILL.md" -Raw }
B 17 'GIT ESTADO' { git rev-parse --show-toplevel; git rev-parse --git-common-dir; git branch -a; git status --short; git log --oneline -20 }
B 18 'GIT WORKTREES' { git worktree list }
B 19 'COORDENACAO.JSON' { $d=(git rev-parse --git-common-dir); Get-Content (Join-Path $d 'coordenacao.json') -Raw }
B 20 'ROADMAP PROGRESS' { Get-Content '.roadmap_progress.json' -Raw }
B 21 'TODOS OS PROGRESS JSON DA MAQUINA' { Get-ChildItem (Split-Path $PWD -Parent) -Recurse -Depth 3 -Filter '*roadmap_progress*.json' -ErrorAction SilentlyContinue | ForEach-Object { "----- " + $_.FullName + " -----"; Get-Content $_.FullName -Raw } }
B 22 'AGENTS.MD PROJETO' { Get-Content 'AGENTS.md' -Raw }
B 23 'ARVORE RAIZ' { Get-ChildItem -Force | Select-Object Mode,Length,Name | Format-Table -AutoSize }
B 24 'DIRETORIOS NIVEL 2' { Get-ChildItem -Directory -Recurse -Depth 1 -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch '\\(\.git|\.venv|node_modules|__pycache__)' } | Select-Object -ExpandProperty FullName }
B 25 'MAIORES ARQUIVOS PY' { $py | ForEach-Object { [PSCustomObject]@{ Linhas=(Get-Content $_.FullName).Count; Arquivo=$_.FullName.Replace("$PWD\","") } } | Sort-Object Linhas -Descending | Select-Object -First 30 | Format-Table -AutoSize }
B 26 'PASTAS ALVO EXISTEM' { 'registry','domains','adapters','experimental','meta','core','tools','resources','scripts','tests','.clinerules','.github\prompts','.github\roadmap','.github\hooks' | ForEach-Object { "$_ = " + (Test-Path $_) } }
B 27 'CONTAGEM BRUTA DE TOOLS' { "tool_definitions Tool( linhas = " + (Select-String -Path 'core\tool_definitions.py' -Pattern 'Tool\(' -ErrorAction SilentlyContinue).Count; "server.py Tool( linhas = " + (Select-String -Path 'server.py' -Pattern 'Tool\(' -ErrorAction SilentlyContinue).Count }
B 28 'NOMES DE TOOLS ENCONTRADOS' { Select-String -Path 'core\tool_definitions.py','server.py' -Pattern 'name\s*=\s*"([a-z0-9_]+)"' -AllMatches -ErrorAction SilentlyContinue | ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique }
B 29 'BLOCOS DE CURADORIA' { Select-String -Path 'server.py' -Pattern '^(TOOLSETS|PHASE_TOOLSETS|TOOL_PROFILES|PHASE_TOOLS_CORE|_HINT_RULES)' -Context 0,45 -ErrorAction SilentlyContinue }
B 30 'SIMBOLOS SUSPEITOS DE CODIGO MORTO' { '_READONLY','_DESTRUCTIVE','_IDEMPOTENT','_TITLES','_TAGS','_HINT_RULES','_apply_hints' | ForEach-Object { $k=$_; "----- $k -----"; ($py | Select-String -Pattern $k | Select-Object -First 15 | ForEach-Object { $_.Filename + ":" + $_.LineNumber + ": " + $_.Line.Trim() }) } }
B 31 'ROLLUPS' { "linhas = " + (Get-Content 'tools\rollups.py' -ErrorAction SilentlyContinue).Count; Select-String -Path 'tools\rollups.py' -Pattern '_ROLLUP_BUILDERS' -Context 0,60 -ErrorAction SilentlyContinue; Select-String -Path 'tools\rollups.py' -Pattern '^def ' -ErrorAction SilentlyContinue }
B 32 'META TOOL COMPLETO' { Get-Content '_meta_tool.py' -Raw }
B 33 'MANAGE MANUAIS EM TOOL_DEFINITIONS' { Select-String -Path 'core\tool_definitions.py' -Pattern '"[a-z0-9_]+_manage"' -ErrorAction SilentlyContinue | ForEach-Object { $_.LineNumber.ToString() + ": " + $_.Line.Trim() } }
B 34 'TRIO DE DESCOBERTA' { $py | Select-String -Pattern 'catalog_search|describe_tool|invoke_by_name|tool_catalog|tool_groups' | Select-Object -First 60 | ForEach-Object { $_.Filename + ":" + $_.LineNumber + ": " + $_.Line.Trim() } }
B 35 'RESOURCES' { Get-Content 'resources\__init__.py' -Raw }
B 36 'PYTHON E LIBS' { .venv\Scripts\python --version; .venv\Scripts\python -m pip list }
B 37 'TOOLANNOTATIONS DO SDK' { .venv\Scripts\python -c "from mcp.types import ToolAnnotations; print(sorted(ToolAnnotations.model_fields.keys())); print(ToolAnnotations.model_config)" }
B 38 'PYTEST COLETA' { .venv\Scripts\python -m pytest --collect-only -q 2>&1 | Select-Object -Last 40 }
B 39 'FEATURES 8 9 10' { $py | Select-String -Pattern 'PHASE_TOOLSETS|release_checklist|build_export|get_next_step|advance_phase|set_cache_invalidator' | Select-Object -First 80 | ForEach-Object { $_.Filename + ":" + $_.LineNumber + ": " + $_.Line.Trim() } }
B 40 'BUG NODE PROPERTY' { $py | Select-String -Pattern 'set_node_property|get_node_property' | ForEach-Object { $_.Filename + ":" + $_.LineNumber + ": " + $_.Line.Trim() } }
B 41 'DOCUMENTOS MD' { Get-ChildItem -Recurse -Filter *.md -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch '\\(\.venv|node_modules)' } | Select-Object FullName,Length,LastWriteTime | Format-Table -AutoSize }
B 42 'ARVORE .GITHUB' { Get-ChildItem '.github' -Recurse -File -ErrorAction SilentlyContinue | Select-Object FullName,Length | Format-Table -AutoSize }
B 43 'ESTADO DO PROJETO' { Get-ChildItem -Force -Filter '*.json' | Select-Object Name,Length | Format-Table -AutoSize; Get-Content 'config.local.json' -Raw }
B 44 'REGISTRY DO MONOREPO' { Get-ChildItem (Split-Path $PWD -Parent) -Recurse -Depth 3 -Filter 'registry.json' -ErrorAction SilentlyContinue | ForEach-Object { "----- " + $_.FullName + " -----"; Get-Content $_.FullName -Raw } }
B 45 'REFERENCIAS A CLINERULES' { Get-ChildItem -Recurse -Include *.py,*.md,*.json -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch '\\(\.venv|node_modules)' } | Select-String -Pattern 'clinerules|cline' | ForEach-Object { $_.Filename + ":" + $_.LineNumber + ": " + $_.Line.Trim() } }
B 46 'TAMANHO FINAL' { Get-Item $out | Select-Object Length,FullName }
