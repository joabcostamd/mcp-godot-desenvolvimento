@echo off
chcp 65001 >nul
echo ============================================================
echo  SETUP AUTOMATICO — MCP Godot Agent v3.5.0
echo  Repo: joabcostamd/mcp-godot-desenvolvimento (branch: main)
echo  Estado: 268 tools | 83/96 fatias | 19-jul-2026
echo ============================================================
echo.

REM ── 1. Criar estrutura de pastas ──────────────────────────────
echo [1/6] Criando estrutura de pastas...
if not exist "%USERPROFILE%\OneDrive\Documentos\VSCODE" mkdir "%USERPROFILE%\OneDrive\Documentos\VSCODE"
if not exist "%USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO" mkdir "%USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO"
if not exist "%USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO\projetos" mkdir "%USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO\projetos"
echo    OK
echo.

REM ── 2. Clonar/atualizar repositorio ───────────────────────────
echo [2/6] Clonando repositorio do GitHub...
cd /d "%USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO\projetos"
if exist "mcp-godot-desenvolvimento" (
    echo    Pasta ja existe — atualizando com git pull...
    cd mcp-godot-desenvolvimento
    git pull origin main
) else (
    git clone -b main https://github.com/joabcostamd/mcp-godot-desenvolvimento
    cd mcp-godot-desenvolvimento
)
if %ERRORLEVEL% neq 0 (
    echo    [ERRO] Falha ao clonar/atualizar. Verifique git e internet.
    pause
    exit /b 1
)
echo    OK — branch main, commit mais recente
echo.

REM ── 3. Criar ambiente virtual ─────────────────────────────────
echo [3/6] Criando ambiente virtual Python (.venv)...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo    [ERRO] Python nao encontrado. Instale Python 3.12+ e adicione ao PATH.
    pause
    exit /b 1
)
if exist ".venv" (
    echo    .venv ja existe — pulando criacao
) else (
    python -m venv .venv
)
echo    OK
echo.

REM ── 4. Instalar dependencias ──────────────────────────────────
echo [4/6] Instalando dependencias Python...
call .venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo    [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)
echo    OK
echo.

REM ── 5. Configurar config.json ─────────────────────────────────
echo [5/6] Configurando config.json...
if not exist "config.json" (
    copy config.json.example config.json >nul
    echo    config.json CRIADO do config.json.example.
    echo.
    echo    ╔══════════════════════════════════════════════════════╗
    echo    ║  !! IMPORTANTE — Abra config.json e ajuste:         ║
    echo    ║                                                    ║
    echo    ║  "godot_path": "C:\\Godot\\Godot_v4.7-stable..."   ║
    echo    ║  "default_project": "C:\\...\\breakout_test"       ║
    echo    ╚══════════════════════════════════════════════════════╝
    echo.
) else (
    echo    config.json ja existe — mantido
)
echo    OK
echo.

REM ── 6. Verificacao final ──────────────────────────────────────
echo [6/6] Verificando instalacao...
.venv\Scripts\python.exe -c "import server; print('  ✅ MCP Godot Agent OK'); print(f'  Tools: {len(server._raw_tool_defs())} (raw)'); print(f'  Handlers: {len(server._build_handlers())}')"
if %ERRORLEVEL% neq 0 (
    echo    [ERRO] Verificacao falhou. Verifique Python e dependencias.
    pause
    exit /b 1
)
echo    OK
echo.

REM ── Mensagem final ────────────────────────────────────────────
echo ============================================================
echo  ✅ SETUP CONCLUIDO — TUDO PRONTO!
echo ============================================================
echo.
echo  Proximo passo: Cole isso no Copilot do VS Code:
echo.
echo    Leia .session\SESSION_NEXT.md e execute /seguir-roadmap
echo.
pause