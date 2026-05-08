param(
  [Parameter(Mandatory = $true)]
  [string]$ServiceName
)

$ErrorActionPreference = "Stop"

$allowlist = @(
  "Spooler"
)

try {
  if (-not ($allowlist -contains $ServiceName)) {
    Write-Output ("ERROR: Service '{0}' is blocked by allowlist." -f $ServiceName)
    exit 2
  }

  $svc = Get-Service -Name $ServiceName -ErrorAction Stop
  if ($svc.Status -ne "Running") {
    Start-Service -Name $ServiceName -ErrorAction Stop
  } else {
    Restart-Service -Name $ServiceName -Force -ErrorAction Stop
  }

  Write-Output ("SUCCESS: restart_service completed on {0}." -f $ServiceName)
  exit 0
} catch {
  Write-Output ("ERROR: {0}" -f $_.Exception.Message)
  exit 1
}

