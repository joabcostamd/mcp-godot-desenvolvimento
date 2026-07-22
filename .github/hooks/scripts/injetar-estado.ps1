# injetar-estado.ps1 — Hook SessionStart
# Le HANDOFF.md (fonte unica de estado) e injeta como additionalContext.

param()

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
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
}

# Escapa para JSON seguro
$escapedContext = $additionalContext -replace '\\', '\\' -replace '"', '\"' -replace "`n", '\n' -replace "`r", ''

Write-Output "{`"hookSpecificOutput`":{`"hookEventName`":`"SessionStart`",`"additionalContext`":`"$escapedContext`"}}"
exit 0
