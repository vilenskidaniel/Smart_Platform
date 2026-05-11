[CmdletBinding()]
param(
    [ValidateSet("Loopback", "Lan")]
    [string]$EntryMode = "Lan",
    [string]$BindHost,
    [int]$Port = 8091,
    [string]$PublicBaseUrl,
    [string]$PythonExe,
    [ValidateSet("App", "Default")]
    [string]$BrowserMode = "App",
    [switch]$OpenBrowser = $true,
    [switch]$NewWindow = $true,
    [switch]$StopExisting = $true,
    [switch]$DisableSync = $true,
    [switch]$ShowServerWindow,
    [switch]$PrintOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    return Split-Path -Parent $PSScriptRoot
}

function Get-RuntimeDir {
    $runtimeDir = Join-Path $PSScriptRoot "runtime"
    if (-not (Test-Path $runtimeDir)) {
        New-Item -ItemType Directory -Path $runtimeDir | Out-Null
    }
    return $runtimeDir
}

function Write-HostRuntimeScript {
    param(
        [string]$RuntimeDir,
        [string]$RepoRoot,
        [string]$ResolvedBindHost,
        [int]$ResolvedPort,
        [string]$ResolvedPublicBaseUrl,
        [string]$ResolvedPythonExe,
        [string]$ResolvedAppPath,
        [string]$ResolvedSyncEnabledValue,
        [string]$ResolvedServerLogPath
    )

    $runtimeScriptPath = Join-Path $RuntimeDir "run-rpi-shell-host.ps1"
    $runtimeScript = @(
        "`$ErrorActionPreference = 'Stop'",
        "Set-Location '$RepoRoot'",
        "`$env:SMART_PLATFORM_RPI_HOST = '$ResolvedBindHost'",
        "`$env:SMART_PLATFORM_RPI_PORT = '$ResolvedPort'",
        "`$env:SMART_PLATFORM_RPI_PUBLIC_BASE_URL = '$ResolvedPublicBaseUrl'",
        "`$env:SMART_PLATFORM_SYNC_ENABLED = '$ResolvedSyncEnabledValue'",
        "& '$ResolvedPythonExe' '$ResolvedAppPath' *>> '$ResolvedServerLogPath'"
    ) -join [Environment]::NewLine

    Set-Content -Path $runtimeScriptPath -Value $runtimeScript -Encoding ASCII
    return $runtimeScriptPath
}

function Resolve-PythonExe {
    param([string]$Requested)

    if ($Requested) {
        if (Test-Path $Requested) {
            return (Resolve-Path $Requested).Path
        }
        throw "Python executable was not found: $Requested"
    }

    $candidates = @(
        "C:/Users/vilen/AppData/Local/Programs/Python/Python313/python.exe",
        (Get-Command python.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1),
        (Get-Command py.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1)
    ) | Where-Object { $_ }

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }

    throw "Python 3 was not found. Pass -PythonExe <path> explicitly."
}

function Get-LanAddress {
    $netAddresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -and
            $_.IPAddress -ne "127.0.0.1" -and
            $_.IPAddress -notlike "169.254*" -and
            $_.AddressState -eq "Preferred"
        } |
        Select-Object -ExpandProperty IPAddress -Unique

    if ($netAddresses) {
        return @($netAddresses)[0]
    }

    $addresses = [System.Net.Dns]::GetHostAddresses([System.Net.Dns]::GetHostName()) |
        Where-Object {
            $_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork -and
            -not $_.IPAddressToString.StartsWith("127.") -and
            -not $_.IPAddressToString.StartsWith("169.254.")
        } |
        Select-Object -ExpandProperty IPAddressToString -Unique

    if ($addresses) {
        return @($addresses)[0]
    }

    throw "Unable to determine a LAN IPv4 address. Pass -PublicBaseUrl explicitly."
}

function Resolve-BindHost {
    param(
        [string]$Mode,
        [string]$Requested
    )

    if ($Requested) {
        return $Requested
    }

    if ($Mode -eq "Loopback") {
        return "127.0.0.1"
    }

    return "0.0.0.0"
}

function Resolve-PublicBaseUrl {
    param(
        [string]$Mode,
        [string]$Requested,
        [int]$ResolvedPort
    )

    if ($Requested) {
        return $Requested.TrimEnd("/")
    }

    if ($Mode -eq "Loopback") {
        return "http://127.0.0.1:$ResolvedPort"
    }

    $lanAddress = Get-LanAddress
    return "http://$($lanAddress):$ResolvedPort"
}

function Resolve-AppBrowserExe {
    $candidates = @(
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
        "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        (Get-Command chrome.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1),
        (Get-Command msedge.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1)
    ) | Where-Object { $_ }

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }

    return $null
}

function Ensure-WindowApi {
    if ("SmartPlatformWindowApi" -as [type]) {
        return
    }

    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class SmartPlatformWindowApi {
    [DllImport("user32.dll")]
    public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
}
"@
}

function Find-BrowserWindowHandle {
    param(
        [object]$Process,
        [datetime]$EarliestStartTime,
        [string]$TitleHint = "Smart Platform",
        [int]$TimeoutMs = 10000
    )

    $deadline = (Get-Date).AddMilliseconds($TimeoutMs)
    $processName = ""
    $launchFloor = if ($EarliestStartTime) { $EarliestStartTime } else { (Get-Date).AddSeconds(-15) }

    try {
        $processName = [string]$Process.ProcessName
    } catch {
        $processName = ""
    }

    while ((Get-Date) -lt $deadline) {
        $seenProcessIds = @{}
        $candidates = @()

        if ($Process -is [System.Diagnostics.Process]) {
            try {
                if (-not $Process.HasExited) {
                    $Process.Refresh()
                    $seenProcessIds[$Process.Id] = $true
                    $candidates += $Process
                }
            } catch {
            }
        }

        if ($processName) {
            try {
                $related = Get-Process -Name $processName -ErrorAction SilentlyContinue |
                    Sort-Object `
                        @{ Expression = {
                            try {
                                if ($TitleHint -and $_.MainWindowTitle -like "*$TitleHint*") { 1 } else { 0 }
                            } catch {
                                0
                            }
                        }; Descending = $true }, `
                        @{ Expression = {
                            try {
                                if ($_.StartTime -ge $launchFloor) { 1 } else { 0 }
                            } catch {
                                0
                            }
                        }; Descending = $true }, `
                        @{ Expression = {
                            try {
                                $_.StartTime
                            } catch {
                                Get-Date 0
                            }
                        }; Descending = $true }
                foreach ($candidate in $related) {
                    if (-not $seenProcessIds.ContainsKey($candidate.Id)) {
                        $seenProcessIds[$candidate.Id] = $true
                        $candidates += $candidate
                    }
                }
            } catch {
            }
        }

        foreach ($candidate in $candidates) {
            try {
                $candidate.Refresh()
                if ($candidate.MainWindowHandle -and $candidate.MainWindowHandle -ne [IntPtr]::Zero) {
                    return $candidate.MainWindowHandle
                }
            } catch {
            }
        }

        Start-Sleep -Milliseconds 200
    }

    return [IntPtr]::Zero
}

function Maximize-BrowserWindow {
    param(
        [object]$Process,
        [datetime]$EarliestStartTime,
        [string]$TitleHint = "Smart Platform",
        [int]$TimeoutMs = 10000
    )

    Ensure-WindowApi
    $windowHandle = Find-BrowserWindowHandle -Process $Process -EarliestStartTime $EarliestStartTime -TitleHint $TitleHint -TimeoutMs $TimeoutMs
    if ($windowHandle -eq [IntPtr]::Zero) {
        return $false
    }

    [SmartPlatformWindowApi]::ShowWindowAsync($windowHandle, 3) | Out-Null

    $followUpDeadline = (Get-Date).AddMilliseconds(1800)
    while ((Get-Date) -lt $followUpDeadline) {
        Start-Sleep -Milliseconds 200
        $nextHandle = Find-BrowserWindowHandle -Process $Process -EarliestStartTime $EarliestStartTime -TitleHint $TitleHint -TimeoutMs 200
        if ($nextHandle -ne [IntPtr]::Zero -and $nextHandle -ne $windowHandle) {
            [SmartPlatformWindowApi]::ShowWindowAsync($nextHandle, 3) | Out-Null
            $windowHandle = $nextHandle
        }
    }

    return $true
}

function Open-ShellBrowser {
    param(
        [string]$Url,
        [string]$Mode
    )

    if ($Mode -eq "App") {
        $browserExe = Resolve-AppBrowserExe
        if ($browserExe) {
            $launchStartedAt = Get-Date
            $browserProcess = Start-Process -FilePath $browserExe -WindowStyle Hidden -PassThru -ArgumentList @(
                "--app=$Url",
                "--start-maximized",
                "--new-window",
                "--disable-session-crashed-bubble"
            )
            Maximize-BrowserWindow -Process $browserProcess -EarliestStartTime $launchStartedAt | Out-Null
            return
        }
    }

    Start-Process $Url | Out-Null
}

function Stop-ExistingListener {
    param([int]$ResolvedPort)

    $connection = Get-NetTCPConnection -LocalPort $ResolvedPort -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($connection) {
        Stop-Process -Id $connection.OwningProcess -Force
    }
}

function Wait-ForHttp {
    param(
        [string]$Url,
        [int]$TimeoutSec = 12
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -UseBasicParsing $Url -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        } catch {
        }

        Start-Sleep -Milliseconds 250
    }

    return $false
}

$repoRoot = Get-RepoRoot
$pythonExe = Resolve-PythonExe -Requested $PythonExe
$bindHost = Resolve-BindHost -Mode $EntryMode -Requested $BindHost
$publicBaseUrl = Resolve-PublicBaseUrl -Mode $EntryMode -Requested $PublicBaseUrl -ResolvedPort $Port
$syncEnabledValue = if ($DisableSync.IsPresent) { "0" } else { "1" }
$appPath = Join-Path $repoRoot "host_runtime/app.py"
$runtimeDir = Get-RuntimeDir
$serverLogPath = Join-Path $runtimeDir "rpi-shell-host.log"
$runtimeScriptPath = Write-HostRuntimeScript -RuntimeDir $runtimeDir -RepoRoot $repoRoot -ResolvedBindHost $bindHost -ResolvedPort $Port -ResolvedPublicBaseUrl $publicBaseUrl -ResolvedPythonExe $pythonExe -ResolvedAppPath $appPath -ResolvedSyncEnabledValue $syncEnabledValue -ResolvedServerLogPath $serverLogPath

if (-not (Test-Path $appPath)) {
    throw "Raspberry Pi app entrypoint was not found: $appPath"
}

$launchPlan = [pscustomobject]@{
    entry_mode = $EntryMode.ToLowerInvariant()
    bind_host = $bindHost
    port = $Port
    public_base_url = $publicBaseUrl
    python = $pythonExe
    app_path = $appPath
    browser_mode = $BrowserMode.ToLowerInvariant()
    open_browser = [bool]$OpenBrowser
    new_window = [bool]$NewWindow
    stop_existing = [bool]$StopExisting
    sync_enabled = ($syncEnabledValue -eq "1")
    server_window = if ($ShowServerWindow) { "visible" } else { "hidden" }
    server_log = $serverLogPath
    runtime_script = $runtimeScriptPath
}

$launchPlan | ConvertTo-Json -Compress

if ($PrintOnly) {
    return
}

if ($StopExisting) {
    Stop-ExistingListener -ResolvedPort $Port
}

if ($NewWindow) {
    $powerShellArgs = @(
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $runtimeScriptPath
    )

    if ($ShowServerWindow) {
        $powerShellArgs = @(
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            $runtimeScriptPath
        )
        Start-Process -FilePath "powershell.exe" -ArgumentList $powerShellArgs | Out-Null
    } else {
        Start-Process -FilePath "powershell.exe" -WindowStyle Hidden -ArgumentList $powerShellArgs | Out-Null
    }

    Wait-ForHttp -Url $publicBaseUrl | Out-Null

    if ($OpenBrowser) {
        Open-ShellBrowser -Url $publicBaseUrl -Mode $BrowserMode
    }
    return
}

if ($OpenBrowser) {
    Write-Warning "Automatic browser opening is only reliable with -NewWindow. Run with the default window mode, or open $publicBaseUrl manually."
}

Set-Location $repoRoot
$env:SMART_PLATFORM_RPI_HOST = $bindHost
$env:SMART_PLATFORM_RPI_PORT = "$Port"
$env:SMART_PLATFORM_RPI_PUBLIC_BASE_URL = $publicBaseUrl
$env:SMART_PLATFORM_SYNC_ENABLED = $syncEnabledValue
& $pythonExe $appPath