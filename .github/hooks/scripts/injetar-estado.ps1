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
    # === DETECTOR DE DERIVA: compara hash do HANDOFF com HEAD ===
    $driftWarning = ""
    $handoffHash = $null
    # Extrai hash do ULTIMO commit mencionado no HANDOFF.md
    # O formato pode ser: "- **Commit:** `hash`" ou "- **Commit:** hash"
    $commitMatches = [regex]::Matches($stateContent, "(?:Ultimo commit|Commit|commit):.*?([a-f0-9]{7,40})")
    if ($commitMatches.Count -gt 0) {
        $handoffHash = $commitMatches[$commitMatches.Count - 1].Groups[1].Value
    }
    if ($handoffHash) {
        $currentHead = git -C $projectRoot rev-parse --short=7 HEAD 2>$null
        if ($currentHead -and $handoffHash -ne $currentHead) {
            # Conta commits entre o hash do HANDOFF e HEAD
            $commitsEntre = git -C $projectRoot log --oneline "$handoffHash..HEAD" 2>$null
            $countEntre = 0
            if ($commitsEntre) {
                $countEntre = ($commitsEntre | Where-Object { $_ -match '\S' } | Measure-Object).Count
            }
            $driftWarning = "`n`n⚠️ DERIVA DETECTADA: o HANDOFF.md registra o commit $handoffHash, mas o HEAD atual e $currentHead — ha $countEntre commit(s) nao registrados no HANDOFF.md. Antes de responder 'onde paramos', rode git log para ver o que mudou.`n"
        }
    }
    # === FIM DO DETECTOR DE DERIVA ===

    # === VERIFICACAO DIARIA DA TRAVA DE SEGURANCA ===
    $travaWarning = ""
    $hoje = (Get-Date).ToString("yyyy-MM-dd")
    $ultimoAutotesteFile = "$env:USERPROFILE\.copilot\hooks\.ultimo-autoteste"
    $rodarAutoteste = $true
    if (Test-Path $ultimoAutotesteFile) {
        $ultimaData = (Get-Content $ultimoAutotesteFile -Raw).Trim()
        if ($ultimaData -eq $hoje) { $rodarAutoteste = $false }
    }
    if ($rodarAutoteste) {
        $autotesteResult = powershell -NoProfile -File "$env:USERPROFILE\.copilot\hooks\scripts\autoteste.ps1" 2>&1
        if ($LASTEXITCODE -ne 0 -or $autotesteResult -notmatch "TRAVA OK") {
            $travaWarning = "`n`n⚠️ A TRAVA DE SEGURANCA FALHOU NO AUTOTESTE — verifique antes de continuar.`n"
        }
        # Atualiza a data (mesmo se falhou — ja avisamos)
        $hoje | Out-File $ultimoAutotesteFile -Encoding UTF8 -Force
    }
    # === FIM DA VERIFICACAO DIARIA ===

    # Verifica se o arquivo tem mais de 6 meses sem atualizar
    $lastWrite = (Get-Item "$projectRoot\$stateFile").LastWriteTime
    $sixMonthsAgo = (Get-Date).AddMonths(-6)
    $ageWarning = ""

    if ($lastWrite -lt $sixMonthsAgo) {
        $daysOld = [math]::Floor(((Get-Date) - $lastWrite).TotalDays)
        $ageWarning = "`n`n[AVISO: $stateFile nao e atualizado ha $daysOld dias (desde $($lastWrite.ToString('yyyy-MM-dd'))). O estado pode estar desatualizado.]"
    }

    $additionalContext = "$travaWarning$driftWarning=== ESTADO DO PROJETO ($stateFile) ===`n$stateContent$ageWarning"
    # Informa sobre historico arquivado
    $additionalContext += "`n`n(Historico de sessoes mais antigas esta em docs/archive/handoffs/ — consulte la se precisar de contexto anterior a 5 sessoes.)"
}

# Bloco de prevencao de erros
$regrasCriticas = "`n`n=== REGRAS QUE JA CAUSARAM ERRO ANTES (NAO REPITA) ===`nR1: Nunca declare var com mesmo nome na mesma funcao GDScript.`nR2: Nunca use := com acesso a Dictionary; declare tipo explicito.`nR10: Ciclo declarativo.`nR11: Todo handler referenciado no _HANDLERS_CACHE precisa ser definido antes do import.`nR12: godot --headless --script/--check-only NAO funciona no Windows 4.7.`nR17: Alias 'no'->'node' causa falso positivo.`nR18: PhaseState.load() SEMPRE seguido de self.save().`nR19: NUNCA use := em @tool scripts Godot.`nR20: Agent hooks do VS Code NAO disparam com extensoes third-party."

$additionalContext += $regrasCriticas

# Le coordenacao.json da pasta .git comum
Push-Location $projectRoot
$commonDir = git rev-parse --git-common-dir 2>$null
Pop-Location
if ($commonDir) {
    if (-not [System.IO.Path]::IsPathRooted($commonDir)) {
        $commonDir = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($projectRoot, $commonDir))
    }
    $coordFile = Join-Path $commonDir "coordenacao.json"
    if (Test-Path $coordFile) {
        $coordContent = Get-Content $coordFile -Raw -Encoding UTF8
        $additionalContext += "`n`n=== COORDENACAO ENTRE WORKTREES ===`nClaims ativos no coordenacao.json: $coordContent`n(Nao escolha etapa ja reivindicada por outro worktree.)"
    }
}

# Escapa para JSON seguro
$escapedContext = $additionalContext -replace '\\', '\\' -replace '"', '\"' -replace "`n", '\n' -replace "`r", ''

Write-Output "{`"hookSpecificOutput`":{`"hookEventName`":`"SessionStart`",`"additionalContext`":`"$escapedContext`"}}"
exit 0