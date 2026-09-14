<#
.SYNOPSIS
  Install the project-delivery-loop skill and per-tool adapter files (Windows).
.EXAMPLE
  .\install.ps1 -Repo C:\code\my-app -InitLedgers -Name "My App" -Offset "+05:30"
#>
param(
  [Parameter(Mandatory = $true)][string]$Repo,
  [switch]$User,
  [switch]$InitLedgers,
  [string]$Name = "",
  [string]$Offset = "+00:00",
  [switch]$DryRun,
  [switch]$AllTools
)

$ErrorActionPreference = "Stop"
$Src = Split-Path -Parent $MyInvocation.MyCommand.Path
$Skill = "project-delivery-loop"
if (-not (Test-Path -LiteralPath $Repo -PathType Container)) {
  throw "Repo must name an existing directory."
}
$Python = $null
foreach ($candidate in @("python", "python3")) {
  if (Get-Command $candidate -ErrorAction SilentlyContinue) {
    & $candidate -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>$null
    if ($LASTEXITCODE -eq 0) { $Python = $candidate; break }
  }
}
if (-not $Python) { throw "Python 3.10+ is required." }
$InstallArgs = [System.Collections.Generic.List[string]]::new()
foreach ($value in @("-B", (Join-Path $Src "scripts/install_skill.py"), "--repo", $Repo, "--source", $Src, "--offset=$Offset")) {
  $InstallArgs.Add($value)
}

function Copy-Skill($SkillsDir) {
  $InstallArgs.Add("--skills-dir")
  $InstallArgs.Add($SkillsDir)
}

function Write-Block($Target, $SrcFile) {
  $InstallArgs.Add("--adapter")
  $InstallArgs.Add($Target)
  $InstallArgs.Add($SrcFile)
}

Copy-Skill (Join-Path $Repo ".devin/skills")
if ($AllTools) {
  foreach ($dir in @(".agents/skills", ".claude/skills", ".codex/skills", ".github/skills")) {
    Copy-Skill (Join-Path $Repo $dir)
  }
  $A = Join-Path $Src "adapters"
  foreach ($target in @("AGENTS.md", "CLAUDE.md", "GEMINI.md", "CONVENTIONS.md", ".github/copilot-instructions.md", ".windsurf/rules/delivery-loop.md", ".clinerules/delivery-loop.md", ".roo/rules/delivery-loop.md", ".amazonq/rules/delivery-loop.md", ".junie/guidelines.md", ".zed/rules.md")) {
    Write-Block (Join-Path $Repo $target) (Join-Path $A "AGENTS.md")
  }
  Write-Block (Join-Path $Repo ".cursor/rules/delivery-loop.mdc") (Join-Path $A "cursor-project-delivery-loop.mdc")
}
if ($User) { Copy-Skill (Join-Path $HOME ".config/devin/skills") }
if ($InitLedgers) { $InstallArgs.Add("--init-ledgers") }
if ($DryRun) { $InstallArgs.Add("--dry-run") }
if ($Name) { $InstallArgs.Add("--name"); $InstallArgs.Add($Name) }
$OldEncoding = $env:PYTHONIOENCODING
$OldBytecode = $env:PYTHONDONTWRITEBYTECODE
try {
  $env:PYTHONIOENCODING = "utf-8"
  $env:PYTHONDONTWRITEBYTECODE = "1"
  & $Python @InstallArgs
  $Result = $LASTEXITCODE
} finally {
  $env:PYTHONIOENCODING = $OldEncoding
  $env:PYTHONDONTWRITEBYTECODE = $OldBytecode
}
exit $Result
