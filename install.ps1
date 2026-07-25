# install.ps1 -- no-Python bootstrap for python-tool on Windows.
#
# install-python.py is itself a Python script, so it can't be the first
# thing that runs on a machine with no Python at all. This script exists
# to solve exactly that, and only that. It does not reimplement the real
# install: it fetches a small, pinned, checksum-verified, disposable
# CPython build, uses it once to run install-python.py, then deletes it.
# The permanent, governed, checksum-verified install still comes entirely
# from install-python.py's own release lookup.
#
# Requires only curl.exe and tar.exe, both bundled unconditionally in
# Windows 10 (1803+) and Windows 11. Note: in Windows PowerShell 5.1,
# `curl` is aliased to Invoke-WebRequest, a different tool with different
# flags, so this script calls `curl.exe` explicitly throughout, never the
# bare `curl` alias.
#
# NOTE: this script has not yet been run on real Windows hardware. See
# ROADMAP.md. It has been written carefully against documented Windows
# and PowerShell behavior, but treat it as unverified until tested.
#
# Usage:
#   .\install.ps1
#   .\install.ps1 --track 3.11
#   (If PowerShell blocks the script: powershell -ExecutionPolicy Bypass -File .\install.ps1)

$ErrorActionPreference = "Stop"

# Pinned bootstrap release. This intentionally does NOT look up "latest"
# from the GitHub API: the bootstrap Python is disposable and only needs
# to be capable of running install-python.py, which does its own, current,
# checksum-verified release lookup for the real, permanent install.
$BootstrapTag = "20250828"
$BootstrapBaseUrl = "https://github.com/astral-sh/python-build-standalone/releases/download/$BootstrapTag"
$BootstrapFilename = "cpython-3.11.13+$BootstrapTag-x86_64-pc-windows-msvc-install_only_stripped.tar.gz"
$BootstrapSha256 = "0c31ec9bfa1a820db62e61c47fcda3b1ca25328a4f1e3795383015a1dad74059"

function Fail($message) {
    Write-Error "[install.ps1] ERROR: $message"
    exit 1
}

function Log($message) {
    Write-Host "[install.ps1] $message"
}

# Refuse Administrator, same as install-python.py: this is strictly a
# user-space tool.
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Fail "refusing to run as Administrator. python-tool installs entirely in user-space under `$env:LOCALAPPDATA."
}

if (-not $env:PROCESSOR_ARCHITECTURE -or $env:PROCESSOR_ARCHITECTURE -ne "AMD64") {
    Fail "unsupported architecture '$env:PROCESSOR_ARCHITECTURE'. Only x86_64 (AMD64) is supported currently."
}

if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
    Fail "curl.exe is required but was not found. This ships with Windows 10 1803+ and Windows 11; if it's missing, this is an unusually old or stripped-down Windows install."
}
if (-not (Get-Command tar.exe -ErrorAction SilentlyContinue)) {
    Fail "tar.exe is required but was not found. This ships with Windows 10 1803+ and Windows 11; if it's missing, this is an unusually old or stripped-down Windows install."
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallPy = Join-Path $ScriptDir "install-python.py"
if (-not (Test-Path $InstallPy)) {
    Fail "install-python.py not found next to this script at $InstallPy. Check out the full repository, not just this file."
}

$TmpDir = Join-Path $env:TEMP "python-tool-bootstrap-$(Get-Random)"
New-Item -ItemType Directory -Path $TmpDir | Out-Null

try {
    $ArchivePath = Join-Path $TmpDir $BootstrapFilename
    $Url = "$BootstrapBaseUrl/$BootstrapFilename"

    Log "downloading bootstrap Python (x86_64-pc-windows-msvc)..."
    & curl.exe -fsSL -o $ArchivePath $Url
    if ($LASTEXITCODE -ne 0) {
        Fail "download failed for $Url"
    }

    Log "verifying checksum..."
    $actualHash = (Get-FileHash -Path $ArchivePath -Algorithm SHA256).Hash.ToLower()
    if ($actualHash -ne $BootstrapSha256) {
        Fail "checksum mismatch for $BootstrapFilename`: expected $BootstrapSha256, got $actualHash"
    }

    Log "extracting..."
    & tar.exe -xzf $ArchivePath -C $TmpDir
    if ($LASTEXITCODE -ne 0) {
        Fail "extraction failed"
    }

    $BootstrapPython = Join-Path $TmpDir "python\python.exe"
    if (-not (Test-Path $BootstrapPython)) {
        Fail "expected interpreter not found after extraction: $BootstrapPython"
    }

    Log "bootstrap Python ready. Handing off to install-python.py for the real, verified install..."
    & $BootstrapPython $InstallPy @args
    $Status = $LASTEXITCODE

    Log "done (bootstrap Python will now be cleaned up; it was never the permanent install)."
    exit $Status
}
finally {
    if (Test-Path $TmpDir) {
        Remove-Item -Recurse -Force $TmpDir -ErrorAction SilentlyContinue
    }
}
