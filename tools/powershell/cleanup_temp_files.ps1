param(
  [Parameter(Mandatory = $true)]
  [string]$TargetPath,

  [int]$MaxFiles = 2000
)

$ErrorActionPreference = "Stop"

$allowedPrefixes = @(
  "C:\Windows\Temp",
  "$env:TEMP",
  "$env:TMP"
)

function Is-AllowedPath([string]$path) {
  foreach ($prefix in $allowedPrefixes) {
    if ($path.ToLower().StartsWith($prefix.ToLower())) { return $true }
  }
  return $false
}

try {
  if (-not (Is-AllowedPath -path $TargetPath)) {
    Write-Output ("ERROR: Path '{0}' is blocked by allowlist." -f $TargetPath)
    exit 2
  }

  if (-not (Test-Path -LiteralPath $TargetPath)) {
    Write-Output ("ERROR: Path '{0}' does not exist." -f $TargetPath)
    exit 3
  }

  $items = Get-ChildItem -LiteralPath $TargetPath -Recurse -File -Force -ErrorAction Stop | Select-Object -First $MaxFiles
  foreach ($item in $items) {
    Remove-Item -LiteralPath $item.FullName -Force -ErrorAction SilentlyContinue
  }

  Write-Output ("SUCCESS: cleanup_temp_files completed on {0}." -f $TargetPath)
  exit 0
} catch {
  Write-Output ("ERROR: {0}" -f $_.Exception.Message)
  exit 1
}

