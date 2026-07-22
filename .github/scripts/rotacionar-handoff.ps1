# rotacionar-handoff.ps1 — Mantem HANDOFF.md com no maximo 5 secoes.
# Move secoes antigas para docs/archive/handoffs/HANDOFF-<ano>.md.
# Rode como parte do /encerrar (FASE 11).

param(
    [string]$HandoffPath = "HANDOFF.md",
    [int]$MaxSecoes = 5
)

if (-not (Test-Path $HandoffPath)) {
    Write-Host "HANDOFF.md nao encontrado em $HandoffPath"
    exit 0
}

$content = Get-Content $HandoffPath -Raw -Encoding UTF8
if (-not $content -or $content.Trim().Length -eq 0) { exit 0 }

$secoes = [regex]::Split($content, '(?=## (?:Handoff|Encerramento)\b)') | Where-Object { $_.Trim().Length -gt 0 }

$firstSectionIndex = $content.IndexOf('## Handoff')
if ($firstSectionIndex -lt 0) { $firstSectionIndex = $content.IndexOf('## Encerramento') }
$header = ''
if ($firstSectionIndex -gt 0) { $header = $content.Substring(0, $firstSectionIndex).TrimEnd() }

$total = $secoes.Count
Write-Host "Secoes encontradas: $total"

if ($total -le $MaxSecoes) {
    Write-Host "Nada a rotacionar ($total <= $MaxSecoes)"
    exit 0
}

$recentes = $secoes | Select-Object -Last $MaxSecoes
$antigas = $secoes | Select-Object -First ($total - $MaxSecoes)

$archiveDir = 'docs/archive/handoffs'
if (-not (Test-Path $archiveDir)) { New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null }

foreach ($s in $antigas) {
    $ano = 'desconhecido'
    if ($s -match '(\d{4})-\d{2}-\d{2}') { $ano = $Matches[1] }
    $archiveFile = Join-Path $archiveDir "HANDOFF-$ano.md"
    $s.Trim() + "`n`n" | Add-Content $archiveFile -Encoding UTF8
    Write-Host "Arquivado em: $archiveFile"
}

$novoConteudo = @()
if ($header) { $novoConteudo += $header.TrimEnd() }
foreach ($r in $recentes) { $novoConteudo += ''; $novoConteudo += $r.TrimEnd() }
$novoConteudo += ''

[System.IO.File]::WriteAllText((Resolve-Path $HandoffPath), ($novoConteudo -join "`n"), [System.Text.UTF8Encoding]::new($true))
Write-Host "HANDOFF.md atualizado: $($recentes.Count) secoes mantidas, $(($total - $MaxSecoes)) arquivadas"
exit 0