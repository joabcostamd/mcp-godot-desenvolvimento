@echo off
echo ============================================================
echo  SETUP AUTOMATICO — MCP Godot Desenvolvimento
echo  Destino: %USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO\projetos\mcp-godot-desenvolvimento
echo ============================================================
echo.

REM ── 1. Criar estrutura de pastas ──────────────────────────────
echo [1/6] Criando estrutura de pastas...
if not exist "%USERPROFILE%\OneDrive\Documentos\VSCODE" (
    mkdir "%USERPROFILE%\OneDrive\Documentos\VSCODE"
)
if not exist "%USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO" (
    mkdir "%USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO"
)
if not exist "%USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO\projetos" (
    mkdir "%USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO\projetos"
)
echo    OK
echo.

REM ── 2. Clonar o repositorio ──────────────────────────────────
echo [2/6] Clonando repositorio do GitHub...
cd /d "%USERPROFILE%\OneDrive\Documentos\VSCODE\NUCLEO\projetos"
if exist "mcp-godot-desenvolvimento" (
    echo    !!! PASTA JA EXISTE — Pulando clone...
    cd mcp-godot-desenvolvimento
    git pull origin master
) else (
    git clone https://github.com/joabcostamd/mcp-godot-desenvolvimento
    cd mcp-godot-desenvolvimento
)
if %ERRORLEVEL% neq 0 (
    echo    [ERRO] Falha ao clonar. Verifique git e internet.
    pause
    exit /b 1
)
echo    OK
echo.

REM ── 3. Criar ambiente virtual ─────────────────────────────────
echo [3/6] Criando ambiente virtual Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo    [ERRO] Python nao encontrado no PATH. Instale Python 3.11+ primeiro.
    pause
    exit /b 1
)
if not exist ".venv" (
    python -m venv .venv
) else (
    echo    .venv ja existe — pulando
)
echo    OK
echo.

REM ── 4. Ativar venv e instalar dependencias ───────────────────
echo [4/6] Instalando dependencias...
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo    [ERRO] Falha ao instalar dependencias.
    pause
    exit /b 1
)
echo    OK
echo.

REM ── 5. Criar config.json a partir do example ──────────────────
echo [5/6] Criando config.json...
if not exist "config.json" (
    if exist "config.json.example" (
        copy config.json.example config.json
        echo    config.json criado do example.
        echo    !!! IMPORTANTE: Edite config.json e ajuste godot_path para o caminho do Godot neste PC.
    ) else (
        echo    config.json.example nao encontrado — criando config.json padrao...
        (
            echo {
            echo     "default_project": "",
            echo     "godot_path": "C:/Program Files/Godot/Godot_v4.3-stable_win64.exe",
            echo     "api_keys": {}
            echo }
        ) > config.json
        echo    !!! IMPORTANTE: Edite config.json e ajuste godot_path.
    )
) else (
    echo    config.json ja existe — mantido
)
echo    OK
echo.

REM ── 6. Verificacao final ──────────────────────────────────────
echo [6/6] Verificando instalacao...
python -c "import sys; sys.path.insert(0, '.'); print('  server.py importavel: OK'); from server import _tool_defs; print(f'  Tools carregadas: {len(_tool_defs())}')"
if %ERRORLEVEL% neq 0 (
    echo    [ERRO] Verificacao falhou — algo nao esta certo.
    pause
    exit /b 1
)
echo    OK
echo.

REM ── Mensagem final ────────────────────────────────────────────
echo ============================================================
echo  ✅ SETUP CONCLUIDO COM SUCESSO!
echo ============================================================
echo.
echo  AGORA FALTA COPIAR MANUALMENTE DO OUTRO PC:
echo.
echo   1. .roadmap_progress.json   ^<- PROGRESSO DAS 21 FATIAS (OBRIGATORIO)
echo   2. config.json              ^<- SUAS CONFIGURACOES LOCAIS (caminho Godot, chaves API)
echo.
echo  Cole ambos na pasta:
echo    %CD%
echo.
echo  DEPOIS DISSO, ABRA O VS CODE NESTA PASTA E RODE /plan
echo.
pause