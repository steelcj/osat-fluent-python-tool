# ROADMAP

## Open items

### osat-fluent variances

#### install-<target>.py

Fluent "install" scripts are actually manage scripts. Options should be similar/unified so expectations are the same. 

###### example of install-restic.py

```bash
Usage:
    install-restic.py --install [VERSION]  Install a version (default: latest)
    install-restic.py --switch VERSION     Point the env file at an installed version
    install-restic.py --status             Show installed, archived, and active versions
    install-restic.py --remove VERSION     Remove an installed version (archive is kept)
    install-restic.py --version            Show this manager's version

```

yet for `install-python.py` `--version` is replaced with `--track`

In addition Fluent some tools use the "tool" postfix to differentiate  (<tool_name>-tool) from system apps with the same name. Yet the python-tool uses the "track" (version) postfix. This might be good or bad, the point is that it is different and we should have a good reason that is explained as to why this is the case.

### Windows: install-python.py and install.ps1 both untested on real hardware.

The platform detection (`x86_64-pc-windows-msvc`), versioned-layout paths, and both wrapper templates are written. `install.ps1` additionally parses cleanly under PowerShell 7's own AST parser and its checksum logic (`Get-FileHash`) has been verified to produce output identical to `sha256sum`, but neither script has been run end-to-end on an actual Windows machine. Do not treat Windows support as verified until that happens.

### macOS: install-python.py untested on real hardware.

Same caveat as Windows, minus the wrapper format question (macOS uses the nix wrapper template and `install.sh`, both already proven end-to-end on Linux with zero Python or bash present). The `x86_64-apple-darwin` and `aarch64-apple-darwin` target triples themselves have not been exercised against a real download on real macOS hardware.

**musl libc not wired up.** `TARGET_TRIPLES` only maps to glibc targets on Linux (`x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`). Alpine and other musl-based systems will fail with the "unsupported platform" error even though python-build-standalone does publish musl builds. Add musl detection (e.g. via `platform.libc_ver()` or checking for the presence of `/etc/alpine-release`) and the corresponding target triples if this becomes a real need.

**`GITHUB_TOKEN` support exists but is undocumented.** The installer already sends a bearer-adjacent higher-limit path via the GitHub API when rate-limited advice is given in the error message, but there is no documentation anywhere telling a person how or why they'd set it. Add a section to docs/en/README.md once this is confirmed worth documenting (it may not come up often enough to be worth the complexity).

**No `--list` or `--uninstall` command yet.** Every other Fluent tool in this fleet eventually needs a way to see what's installed and remove a version cleanly. python-tool doesn't have either yet; for now, removal is manual (`rm -rf` the version directory and the wrapper).

**Bootstrap scripts are pinned to a fixed release (tag `20250828`, CPython 3.11.13).** This is deliberate, the bootstrap Python is disposable and only needs to run `install-python.py`, which does its own current release lookup for the real, permanent install, but the pin will eventually be old enough to be worth a policy decision: update it periodically, or leave it alone indefinitely since its only job never changes. Not urgent.

## Deliberately out of scope

**Package installation beyond the interpreter itself.** python-tool installs CPython, `pip`, and `venv`. It does not manage project dependencies, virtual environments, or package installation beyond what ships in the base python-build-standalone artifact. That's a different tool's job.

**Non-glibc, non-musl Linux C libraries.** Anything outside the two libc families python-build-standalone itself supports is out of scope here; we inherit upstream's platform support surface rather than extending it.
