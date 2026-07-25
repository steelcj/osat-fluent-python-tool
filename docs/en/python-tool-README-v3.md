# python-tool

Version: 0.1.0
Status: Draft

## What this is

python-tool installs a self-contained CPython runtime into user-space, side by side with any system Python, with no elevated privilege, no package manager, and no compiler required. It follows the same governed pattern as every other OSAT Fluent tool: fetch a verified release artifact, extract it to a versioned directory, render a wrapper.

It does not replace, modify, or shadow whatever Python your system already has. The two coexist deliberately.

## Do I need this?

The answer differs meaningfully by platform, so we are not going to pretend it does not.

### Linux

Most mainstream distributions (Ubuntu, Debian, Fedora, Arch) already ship a real, working `python3`. You may not need python-tool at all. Reach for it when you want a specific pinned version without touching system packages, a build with `venv` and `pip` guaranteed to work regardless of what your distro's minimal or container images include, or the same governed, checksum-verified provenance every other Fluent tool gives you.

### macOS

The common belief that "Macs come with Python" is out of date. Typing `python3` on a fresh Mac prompts an install of Xcode Command Line Tools, a large separate download, and Apple's own documentation describes the resulting system Python as intended "for Apple utilities, not for you," recommending against using it for your own work. The two conventional alternatives both carry real costs: python.org's installer needs Administrator privilege, and Homebrew requires installing an entire second package manager first. python-tool is the strongest option on this platform, not a fallback.

### Windows

There is no system Python by default, aside from a Microsoft Store stub behind the `python` alias. python-tool is the intended path here too. Status note: the extraction and versioned-layout logic is written and platform-detected, but has not yet been tested on a real Windows machine. Treat this platform as unverified until that testing happens; see ROADMAP.md.

## Why python-build-standalone

We evaluated python.org's own distributions directly and found the fit differs sharply by platform:

- On Linux, python.org publishes no binaries at all. Their own documentation states that "for most Unix systems, you must download and compile the source code," which reintroduces a compiler toolchain dependency Fluent tools exist specifically to avoid.
- On macOS, the `.pkg` installer requires Administrator privilege and writes system-wide, to `/Applications` and `/Library/Frameworks`. No user-space, no-elevation variant exists.
- On Windows, the "embeddable package" is genuinely user-space and needs no elevation, but the standard library's own documentation says plainly that using pip to manage dependencies "is not supported with this distribution." The stdlib `venv` module does not work against it without unsupported workarounds. That fails the one requirement that matters most here: other Fluent tools need a real interpreter they can build a working `.venv` from.

`python-build-standalone` builds a full, working CPython on all three platforms, no compiler needed anywhere, no elevation needed anywhere, and `venv`/`pip` work natively out of the box. It is the same source `uv` and modern `pyenv` builds use. We verified this in practice, not just on paper: the installed interpreter creates a working `venv`, and `pip` runs inside it with no patching.

We deliberately did not build a hybrid that uses python.org's embeddable package on Windows and python-build-standalone elsewhere. A single governed source across all platforms keeps the provenance story the same everywhere, which matters more here than leaning on the "official" source where it happens to work.

## Installing

### Test for Python

#### Linux and macOS

```bash
which python3
```

#### Windows

In PowerShell, `where` is aliased to `Where-Object`, a completely different cmdlet, so bare `where python` will not do what you would expect. Call the real locator tool explicitly instead, the `.exe` extension forces PowerShell to resolve it as the actual external command rather than the alias, and this same form also works identically in `cmd.exe`.

A "found" result alone is not sufficient confirmation on Windows the way it is on Linux and macOS. Windows ships an "app execution alias" stub at `python.exe` (and `python3.exe`) that, when run, just opens the Microsoft Store to a Python listing instead of being a real interpreter. Always follow the locator with a version check:

```powershell
where.exe python
python --version
```

### On a system that already has Python 3.8 or greater

#### Linux and macOS

One command. `install-python.py` does everything: looks up the latest `python-build-standalone` release, downloads it, verifies the checksum, extracts it, renders the wrapper.

```bash
python3 install-python.py
```

#### Windows

python.org's official Windows installer creates `python.exe` and `py.exe`. It does not create a `python3.exe`. On a Windows system that already has Python, run:

```powershell
python install-python.py
```

or, using the launcher that ships alongside a python.org install (installed directly in `C:\Windows`, so it is reliably on `PATH`, and picks the right version if multiple are installed):

```powershell
py install-python.py
```

There is no single command that works across every Windows install method, because the Microsoft Store version of Python does the opposite of python.org's installer:

- **python.org installer**: `python` and `py` work. `python3` does not exist.
- **Microsoft Store install**: `python` and `python3` both work, this is the one install method that registers `python3`. `py` does not exist; the launcher is a python.org-only feature.

If `python install-python.py` fails with "not recognized," try `python3 install-python.py`.

### On a system with no Python at all

#### Linux and macOS

```bash
./install.sh
```

One command. Internally, this:

1. Downloads a small, pinned, disposable CPython build to a temp directory and verifies its checksum.
2. Extracts that disposable build.
3. Runs `install-python.py` itself, using that disposable interpreter, the same as if you had typed `python3 install-python.py` yourself. You never type that command; `install.sh` does it for you.
4. `install-python.py` does its normal job (real release lookup, real download, real checksum, real extract, real wrapper), landing the permanent install in the usual place.
5. Deletes the temporary bootstrap Python.

#### Windows

```powershell
.\install.ps1
```

Same shape as Linux and macOS, one command, `install.ps1` handles the whole bootstrap-then-real-install sequence internally:

1. Downloads a small, pinned, disposable CPython build via `curl.exe`, called explicitly rather than the bare `curl` alias, which in Windows PowerShell 5.1 actually points to `Invoke-WebRequest`, a different tool, and verifies its checksum with `Get-FileHash`.
2. Extracts that disposable build with `tar.exe`. Both `curl.exe` and `tar.exe` are built into Windows 10 (1803+) and Windows 11; nothing extra to install first.
3. Runs `install-python.py` itself, using that disposable interpreter, same as `install.sh` does on Linux and macOS.
4. `install-python.py` does the real, permanent, checksum-verified install and renders the wrapper.
5. Deletes the temporary bootstrap Python.

PowerShell's default execution policy can block running a downloaded `.ps1` file outright. If that happens:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

## python-tool options

### Help

```bash
python3 install-python.py -h
```

Output Example:

```bash
usage: install-python.py [-h] [--track TRACK] [--force]

Install a self-contained CPython runtime, Fluent-style.

options:
  -h, --help     show this help message and exit
  --track TRACK  Python minor version track to install, e.g. 3.12 (default: 3.12)
  --force        Reinstall even if this version's wrapper already matches.
```

### Installing the default version

```bash
python3 install-python.py
```

Output example:

```bash
[python-tool] looking up latest astral-sh/python-build-standalone release...
[python-tool] release 20260718
[python-tool] selected CPython 3.12.13 (x86_64-unknown-linux-gnu, install_only_stripped)
[python-tool] CPython 3.12.13 is already installed and the wrapper is current: /home/initial/.local/bin/python3.12
[python-tool] pass --force to reinstall anyway.
```

### Installing a specific version (or track)

Both the direct command and the bootstrap scripts accept the same options, `install.sh` and `install.ps1` pass everything through to `install-python.py` unchanged.

Install a specific track:

```bash
python3 install-python.py --track 3.11
```

Running the installer again for a track you already have is a no-op unless something changed; pass `--force` to reinstall anyway.

#### Version checks

##### 3.11

```bash
python3.11 --version
```

Output example:

```bash
Python 3.11.15
```

##### 3.12

```bash
python3.12 --version
```

Otuput example:

```bash
Python 3.12.13
```

#### Path checks

##### 3.11

```bash
which python3.11
```

Output example:

```bash
/home/initial/.local/bin/python3.11
```

##### 3.12

```bash
which python3.12
```

Output example:

```bash
/home/initial/.local/bin/python3.12
```

### Network access

The installer does not require network access to any host beyond `api.github.com` and `github.com`'s release-asset hosts. `install.sh` and `install.ps1` reach the same hosts for their own bootstrap download.

## What gets installed, and where

### Linux and macOS

```
~/.local/share/python-tool/<version>/python/bin/python3.<minor>
~/.local/bin/python3.<minor>          (wrapper)
```

### Windows

```
%LOCALAPPDATA%\python-tool\<version>\python\python.exe
%LOCALAPPDATA%\Programs\python3.<minor>.cmd   (wrapper, untested)
```

Everything under the version directory is owner-only (`700`/`600` throughout), matching every other Fluent tool.

## Why the wrapper is not just `python3`

The rendered command is `python3.<minor>`, e.g. `python3.12`, never a bare `python3` or `python`. A bare `python3` wrapper would silently shadow whatever the system already provides the moment `~/.local/bin` is on PATH, which is exactly the kind of quiet, undocumented behavior change Fluent tools are built to avoid. This mirrors the same collision-avoidance reasoning behind the `-tool` suffix elsewhere in OSAT Fluent, most directly `rclone-tool` avoiding collision with `rclone`'s own config conventions.

If you want `python3.12` to be the first thing found on PATH, that is a choice you make explicitly in your own shell configuration, not a default this tool imposes on you.

## Status

**Linux.** `install-python.py` tested end to end against a real release, including confirming `venv` and `pip` work in the installed interpreter. `install.sh` tested end to end multiple times, including in an environment with no Python and no bash present anywhere on `PATH`.

**macOS.** `install-python.py` platform detection and paths are written; not yet tested on real hardware. `install.sh` uses the same code paths already proven on Linux, but the macOS-specific download targets have not themselves been exercised on real hardware.

**Windows.** `install-python.py` platform detection and paths are written; not yet tested on real hardware. `install.ps1` parses cleanly under PowerShell 7's own AST parser and its checksum logic (`Get-FileHash`) has been verified to produce output identical to `sha256sum`, but neither script has been run end to end on an actual Windows machine.

See ROADMAP.md for the full list of open items.

## License

This document, *python-tool*, by **Christopher Steel**, with AI assistance from **Claude Sonnet 4.6 (Anthropic)**, is licensed under the [GNU General Public License v3.0 or later](https://www.gnu.org/licenses/gpl-3.0.html).
