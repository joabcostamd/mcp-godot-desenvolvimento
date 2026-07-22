# injetar-estado.ps1 — Hook SessionStart
# Le HANDOFF.md (fonte unica de estado) e injeta como additionalContext.

param()

$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$stateContent = ""
$stateFile = ""

# HANDOFF.md e a fonte unica de estado do projeto
if (Test-Path "$projectRoot\HANDOFF.md") {
    $stateFile = "HANDOFF.md"
    $stateContent = Get-Content "$projectRoot\HANDOFF.md" -Raw -Encoding UTF8
}

if (-not $stateContent -or $stateContent.Trim().Length -eq 0) {
    $additionalContext = "AVISO: Nenhum arquivo de estado encontrado ou arquivo vazio. Rode /plan para iniciar."
} else {
    # Verifica se o arquivo tem mais de 6 meses sem atualizar
    $lastWrite = (Get-Item "$projectRoot\$stateFile").LastWriteTime
    $sixMonthsAgo = (Get-Date).AddMonths(-6)
    $ageWarning = ""

    if ($lastWrite -lt $sixMonthsAgo) {
        $daysOld = [math]::Floor(((Get-Date) - $lastWrite).TotalDays)
        $ageWarning = "`n`n[AVISO: $stateFile nao e atualizado ha $daysOld dias (desde $($lastWrite.ToString('yyyy-MM-dd'))). O estado pode estar desatualizado.]"
    }

    $additionalContext = "=== ESTADO DO PROJETO ($stateFile) ===`n$stateContent$ageWarning"
    # Informa sobre historico arquivado
    $additionalContext += "`n`n(Historico de sessoes mais antigas esta em docs/archive/handoffs/ — consulte la se precisar de contexto anterior a 5 sessoes.)"
}

# Bloco de prevencao de erros — regras que ja causaram retrabalho real
$regrasCriticas = @"
`n`n=== REGRAS QUE JA CAUSARAM ERRO ANTES (NAO REPITA) ===
R1: Nunca declare var com mesmo nome na mesma funcao GDScript.
R2: Nunca use := com acesso a Dictionary; declare tipo explicito.
R10: Ciclo declarativo — ler estado, editar, validar, reiniciar, verificar. Nao pule passos.
R11: Todo handler referenciado no _HANDLERS_CACHE precisa ser definido antes do import.
R12: godot --headless --script/--check-only NAO funciona no Windows 4.7.
R17: Alias "no"->"node" causa falso positivo — palavras de 2 letras sem acento nao viram alias.
R18: PhaseState.load() SEMPRE seguido de self.save() — senao estado some da proxima sessao.
R19: NUNCA use := em @tool scripts Godot; declare tipo explicito.
R20: Agent hooks do VS Code NAO disparam com extensoes third-party — nao dependa deles para gates.
"@

$additionalContext += $regrasCriticas

# Le coordenacao.json da pasta .git comum (coordenacao entre worktrees)
Push-Location $projectRoot
$commonDir = git rev-parse --git-common-dir 2>$null
Pop-Location
if ($commonDir) {
    # Resolve caminho absoluto se for relativo
    if (-not [System.IO.Path]::IsPathRooted($commonDir)) {
        $commonDir = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($projectRoot, $commonDir))
    }
    $coordFile = Join-Path $commonDir "coordenacao.json"
    if (Test-Path $coordFile) {
        $coordContent = Get-Content $coordFile -Raw -Encoding UTF8
        $additionalContext += "`n`n=== COORDENACAO ENTRE WORKTREES ==="
        $additionalContext += "`nClaims ativos no coordenacao.json: $coordContent"
        $additionalContext += "`n(Nao escolha etapa ja reivindicada por outro worktree.)"
    }
}

# Escapa para JSON seguro
$escapedContext = $additionalContext -replace '\\', '\\' -replace '"', '\"' -replace "`n", '\n' -replace "`r", ''

Write-Output "{`"hookSpecificOutput`":{`"hookEventName`":`"SessionStart`",`"additionalContext`":`"$escapedContext`"}}"
exit 0
