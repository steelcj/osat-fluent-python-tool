# python-tool

Version: 0.1.0
Status: Draft

## What this is

python-tool installs a self-contained CPython runtime into user-space, side by side with any system Python, with no elevated privilege, no package manager, and no compiler required. It follows the same governed pattern as every other OSAT Fluent tool: fetch a verified release artifact, extract it to a versioned directory, render a wrapper.

It does not replace, modify, or shadow whatever Python your system already has. The two coexist deliberately.

## Why python-build-standalone

We evaluated python.org's own distributions directly and found the fit differs sharply by platform:

- On Linux, python.org publishes no binaries at all. Their own documentation states that "for most Unix systems, you must download and compile the source code," which reintroduces a compiler toolchain dependency Fluent tools exist specifically to avoid.
- On macOS, the `.pkg` installer requires Administrator privilege and writes system-wide, to `/Applications` and `/Library/Frameworks`. No user-space, no-elevation variant exists.
- On Windows, the "embeddable package" is genuinely user-space and needs no elevation, but the standard library's own documentation says plainly that using pip to manage dependencies "is not supported with this distribution." The stdlib `venv` module does not work against it without unsupported workarounds. That fails the one requirement that matters most here: other Fluent tools need a real interpreter they can build a working `.venv` from.

`python-build-standalone` builds a full, working CPython on all three platforms, no compiler needed anywhere, no elevation needed anywhere, and `venv`/`pip` work natively out of the box. It is the same source `uv` and modern `pyenv` builds use. We verified this in practice, not just on paper: the installed interpreter creates a working `venv`, and `pip` runs inside it with no patching.

We deliberately did not build a hybrid that uses python.org's embeddable package on Windows and python-build-standalone elsewhere. A single governed source across all platforms keeps the provenance story the same everywhere, which matters more here than leaning on the "official" source where it happens to work.

## Do I need this?

The answer differs meaningfully by platform, so we are not going to pretend it does not.

**Linux.** Most mainstream distributions (Ubuntu, Debian, Fedora, Arch) already ship a real, working `python3`. You may not need python-tool at all. Reach for it when you want a specific pinned version without touching system packages, a build with `venv` and `pip` guaranteed to work regardless of what your distro's minimal or container images include, or the same governed, checksum-verified provenance every other Fluent tool gives you.

**macOS.** The common belief that "Macs come with Python" is out of date. Typing `python3` on a fresh Mac prompts an install of Xcode Command Line Tools, a large separate download, and Apple's own documentation describes the resulting system Python as intended "for Apple utilities, not for you," recommending against using it for your own work. The two conventional alternatives both carry real costs: python.org's installer needs Administrator privilege, and Homebrew requires installing an entire second package manager first. python-tool is the strongest option on this platform, not a fallback.

**Windows.** There is no system Python by default, aside from a Microsoft Store stub behind the `python` alias. python-tool is the intended path here too. Status note: the extraction and versioned-layout logic is written and platform-detected, but has not yet been tested on a real Windows machine. Treat this platform as unverified until that testing happens; see ROADMAP.md.

## Installing

### Test for Python

#### Linux and MacOS

```bash
which python
```

#### Windows

Same alias trap as `curl`, worth flagging for exactly the same reason. In PowerShell, `where` is aliased to `Where-Object`, a completely different cmdlet, so bare `where python` won't do what you'd expect. The real locator tool needs to be called explicitly:

```
where.exe python
```

Calling it with the `.exe` extension forces PowerShell to resolve it as the actual external command rather than the alias, and this same form works identically in `cmd.exe` too, so it's the one to put in the doc rather than picking a PowerShell-specific alternative like `Get-Command python -ErrorAction SilentlyContinue`.

One more Windows-specific wrinkle worth a line in the doc right next to this, otherwise it'll confuse someone: `where.exe python` can report success on a completely fresh machine even though there's no real Python installed. Windows ships an "app execution alias" stub at `python.exe` (and `python3.exe`) that, when run, just opens the Microsoft Store to a Python listing instead of being an interpreter. So "found" isn't sufficient confirmation the way it is on Linux/macOS, it's worth telling the reader to actually run `python --version` (not just locate it) to be sure they've got a real interpreter and not the Store stub.

So the Windows block, parallel to the nix one, would read something like:

```
where.exe python
python --version
```

### On System with Python 3.8 or greater

#### Linux or MacOS

Common case with Linux, or a Mac/Windows machine that happens to have Python from somewhere else.

One command. `install-python.py` does everything: looks up the latest `python-build-standalone` release, downloads it, verifies the checksum, extracts it, renders the wrapper. Done.

```
python3 install-python.py
```

#### Windows

**python.org's official Windows installer creates `python.exe` and `py.exe`. It does not create a `python3.exe`.** So on a Windows system that has Python you would run:

```powershell
python install-python.py
```

or, using the launcher that ships alongside a python.org install (installed directly in `C:\Windows`, so it's reliably on `PATH`, and picks the right version if multiple are installed):

```
py install-python.py
```

Here's the genuinely annoying part, though, there isn't one universal answer across *all* Windows install methods, because Microsoft's Store version of Python does the opposite of python.org's installer:

- **python.org installer** → `python` and `py` work. `python3` does not exist.
- **Microsoft Store install** → `python` and `python3` both work (it's this version specifically that registers both). `py` does not exist, the launcher is a python.org-only feature.





This installs the default track (currently 3.12) for your platform. To install a specific track:

```
python3 install-python.py --track 3.11
```

Running the installer again for a track you already have is a no-op unless something changed; pass `--force` to reinstall anyway.

### System with no Python

#### Linux/MacOS

```bash
./install.sh
```

1. `install.sh` downloads a small, pinned, disposable CPython build to a temp directory and verifies its checksum.
2. It extracts that disposable build.
3. It then runs `install-python.py` **itself**, using that disposable interpreter, i.e. `install.sh` internally executes the equivalent of `python3 install-python.py`, the user never types that command themselves.
4. `install-python.py` does its normal job (real release lookup, real download, real checksum, real extract, real wrapper), landing the *permanent* install in the usual place.
5. `install.sh` then deletes the temp directory the disposable bootstrap Python lived in.

#### Windows

Same shape as Linux/macOS, one command, `install.ps1` does the whole bootstrap-then-real-install sequence internally, the person never types two separate commands.

```
.\install.ps1
```

What happens inside that single invocation:

1. `install.ps1` downloads a small, pinned, disposable CPython build via `curl.exe` (called explicitly, not the bare `curl` alias, which in Windows PowerShell 5.1 actually points to `Invoke-WebRequest`, a different tool) and verifies its checksum with `Get-FileHash`.
2. It extracts that disposable build with `tar.exe`, both of these come built into Windows 10 (1803+) and Windows 11, nothing extra to install first.
3. It runs `install-python.py` itself, using that disposable interpreter, same as `install.sh` does on nix.
4. `install-python.py` does the real, permanent, checksum-verified install and renders the wrapper.
5. `install.ps1` deletes the temp directory afterward.

One wrinkle specific to Windows, worth documenting alongside the command itself rather than burying it: PowerShell's default execution policy can block running a downloaded `.ps1` file outright. If that happens, the person needs:

```
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

That's a real, common first-run obstacle on Windows (unlike `chmod +x` on nix, which is a one-time, unsurprising step), so it deserves a line in the "Installing" section itself, not a footnote someone only finds after already hitting the error.

One honesty flag to carry into the doc: unlike `install.sh`, which was actually run end-to-end multiple times in this session, `install.ps1` has only been syntax-validated (PowerShell 7's own parser) and had its checksum logic verified in isolation, it has not been run as a whole on real Windows hardware. Worth keeping that distinction visible in whatever we write, the same way `ROADMAP.md` already does, rather than presenting both platforms with equal confidence.

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

## Requirements to run the installer itself

Python 3.8 or later, standard library only. Nothing else. The installer does not require network access to any host beyond `api.github.com` and `github.com`'s release-asset hosts.

## Status

Linux: tested end to end against a real release, including confirming `venv` and `pip` work in the installed interpreter.
macOS: platform detection and paths are written; not yet tested on real hardware.
Windows: platform detection and paths are written; not yet tested on real hardware. See ROADMAP.md.

## License

This document, *python-tool*, by **Christopher Steel**, with AI assistance from **Claude Sonnet 4.6 (Anthropic)**, is licensed under the [GNU General Public License v3.0 or later](https://www.gnu.org/licenses/gpl-3.0.html).
