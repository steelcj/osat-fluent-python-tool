#!/usr/bin/env python3
"""install-python.py -- fetch a versioned, self-contained CPython runtime from
python-build-standalone, install it for the current user with SHA-256
verification against the release's published SHA256SUMS file, and render a
versioned wrapper so the installed interpreter runs from anywhere without
shadowing the system Python.

Why python-build-standalone and not python.org directly:
  - macOS: python.org's .pkg installer requires Administrator privilege and
    writes system-wide (/Applications, /Library/Frameworks). No user-space,
    no-elevation variant is published.
  - Linux: python.org publishes source only for Unix; there are no prebuilt
    binaries at all. Building from source reintroduces exactly the compiler
    toolchain dependency Fluent tools exist to avoid.
  - Windows: python.org's "embeddable package" IS user-space and needs no
    elevation, but the standard library's own docs say plainly that using
    pip to manage dependencies "is not supported with this distribution",
    and the stdlib venv module does not work against it out of the box.
    That fails the one requirement that matters most here: other Fluent
    tools (sat-tool and future Python-based tools) need a real interpreter
    they can build a working .venv from.
  python-build-standalone is a full, working CPython build on all three
  platforms, no compiler needed, no elevation needed, working venv and pip
  out of the box. It is what `uv` and modern `pyenv` builds use under the
  hood.

Layout:
  binary   ~/.local/share/python-tool/<version>/python/bin/python3(.<minor>)
  wrapper  ~/.local/bin/python3.<minor>  (rendered from scripts/nix/python-wrapper
           or scripts/windows/python-wrapper.cmd)

The wrapper is deliberately named python3.<minor>, never a bare python3 or
python, so it never silently shadows the system interpreter. This mirrors
the same collision-avoidance reasoning behind the -tool suffix elsewhere in
OSAT Fluent (see rclone-tool vs rclone).

Supported:
  Linux   x86_64, aarch64  (gnu libc; musl not yet wired up, see ROADMAP.md)
  macOS   x86_64 (Intel), arm64 (Apple Silicon)
  Windows x86_64  -- extraction and versioned layout only; wrapper pending
                     (see ROADMAP.md)

Other platforms fail with an explicit message; see ROADMAP.md for planned
bringup. Requires only the Python standard library (Python 3.8+) to run
this installer itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import stat
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
TOOL_NAME = "python-tool"
GITHUB_REPO = "astral-sh/python-build-standalone"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"
DEFAULT_TRACK = "3.12"
FLAVOR = "install_only_stripped"
USER_AGENT = "osat-fluent-python-tool/0.1.0 (+https://github.com/steelcj/osat-fluent-python-tool)"

# (platform.system(), platform.machine()) -> python-build-standalone target triple
TARGET_TRIPLES = {
    ("Linux", "x86_64"): "x86_64-unknown-linux-gnu",
    ("Linux", "aarch64"): "aarch64-unknown-linux-gnu",
    ("Darwin", "x86_64"): "x86_64-apple-darwin",
    ("Darwin", "arm64"): "aarch64-apple-darwin",
    ("Windows", "AMD64"): "x86_64-pc-windows-msvc",
}


class InstallError(RuntimeError):
    """Raised for any condition that should stop the install with a clear message."""


def log(message: str) -> None:
    print(f"[python-tool] {message}")


def fail(message: str) -> None:
    raise InstallError(message)


def refuse_root() -> None:
    """OSAT Fluent tools are strictly user-space. Refuse to run as root or
    Administrator so nothing ends up owned outside the invoking user's account."""
    if os.name == "posix" and hasattr(os, "geteuid") and os.geteuid() == 0:
        fail(
            "refusing to run as root. python-tool installs entirely in "
            "user-space under $HOME; there is nothing here that needs, or "
            "should have, elevated privilege."
        )
    if os.name == "nt":
        try:
            import ctypes

            if ctypes.windll.shell32.IsUserAnAdmin():
                fail(
                    "refusing to run as Administrator. python-tool installs "
                    "entirely in user-space under %LOCALAPPDATA%; there is "
                    "nothing here that needs, or should have, elevated "
                    "privilege."
                )
        except Exception:
            # If we can't determine admin status, proceed rather than block
            # a legitimate non-admin install on a detection failure.
            pass


def target_triple() -> str:
    key = (platform.system(), platform.machine())
    try:
        return TARGET_TRIPLES[key]
    except KeyError:
        fail(
            f"unsupported platform {key[0]}/{key[1]}. Supported: "
            f"{', '.join(f'{s}/{m}' for s, m in TARGET_TRIPLES)}. "
            "See ROADMAP.md for planned bringup."
        )


class Paths:
    def __init__(self) -> None:
        self.is_windows = os.name == "nt"
        if self.is_windows:
            local = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            self.bin_dir = local / "Programs"
            self.tool_root = local / TOOL_NAME
        else:
            xdg_bin = Path(os.environ.get("XDG_BIN_HOME", Path.home() / ".local" / "bin"))
            xdg_data = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
            self.bin_dir = xdg_bin
            self.tool_root = xdg_data / TOOL_NAME

    def version_dir(self, version: str) -> Path:
        return self.tool_root / version

    def python_root(self, version: str) -> Path:
        # python-build-standalone tarballs extract to a top-level "python/" dir
        return self.version_dir(version) / "python"

    def interpreter(self, version: str) -> Path:
        minor_track = ".".join(version.split(".")[:2])
        if self.is_windows:
            return self.python_root(version) / "python.exe"
        return self.python_root(version) / "bin" / f"python{minor_track}"

    def wrapper_name(self, version: str) -> str:
        minor_track = ".".join(version.split(".")[:2])
        return f"python{minor_track}.cmd" if self.is_windows else f"python{minor_track}"

    def wrapper(self, version: str) -> Path:
        return self.bin_dir / self.wrapper_name(version)


def http_get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            fail(
                "GitHub API rate limit hit while looking up the latest "
                "python-build-standalone release. Wait a while and retry, "
                "or set GITHUB_TOKEN in the environment for a higher limit."
            )
        fail(f"GitHub API request failed ({exc.code}) for {url}")
    except urllib.error.URLError as exc:
        fail(f"network error contacting GitHub API: {exc.reason}")


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, open(destination, "wb") as out_file:
            shutil.copyfileobj(response, out_file)
    except urllib.error.HTTPError as exc:
        fail(f"download failed ({exc.code}) for {url}")
    except urllib.error.URLError as exc:
        fail(f"network error downloading {url}: {exc.reason}")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_sha256sums(text: str) -> dict:
    checksums = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        digest, filename = parts
        filename = filename.lstrip("*")
        checksums[filename] = digest
    return checksums


def find_asset(release: dict, triple: str, track: str) -> tuple:
    """Return (asset_dict, full_version) for the newest patch of `track` on
    `triple` with the install_only_stripped flavor, or fail with a clear
    message listing what was actually available."""
    prefix = f"cpython-{track}."
    suffix = f"-{triple}-{FLAVOR}.tar.gz"
    candidates = []
    for asset in release.get("assets", []):
        name = asset["name"]
        if name.startswith(prefix) and name.endswith(suffix):
            # name looks like cpython-3.12.7+20250828-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz
            version_part = name[len("cpython-"):].split("+", 1)[0]
            candidates.append((tuple(int(p) for p in version_part.split(".")), asset, version_part))
    if not candidates:
        available = sorted({a["name"] for a in release.get("assets", []) if triple in a["name"]})
        fail(
            f"no asset found for track {track} on {triple} in release "
            f"{release.get('tag_name')}. Assets seen for this platform: "
            f"{', '.join(available) if available else '(none)'}"
        )
    candidates.sort(key=lambda item: item[0], reverse=True)
    _, asset, full_version = candidates[0]
    return asset, full_version


def extract(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as tar:
        # Guard against path traversal in the archive before extracting anything.
        for member in tar.getmembers():
            member_path = (destination / member.name).resolve()
            if not str(member_path).startswith(str(destination.resolve())):
                fail(f"refusing to extract unsafe path in archive: {member.name}")
        tar.extractall(destination)


def make_owner_only(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_symlink():
            continue
        try:
            if path.is_dir():
                path.chmod(stat.S_IRWXU)
            else:
                mode = stat.S_IRUSR | stat.S_IWUSR
                if os.access(path, os.X_OK):
                    mode |= stat.S_IXUSR
                path.chmod(mode)
        except OSError:
            continue
    try:
        root.chmod(stat.S_IRWXU)
    except OSError:
        pass


def wrapper_template_path(is_windows: bool) -> Path:
    if is_windows:
        return REPO_DIR / "scripts" / "windows" / "python-wrapper.cmd"
    return REPO_DIR / "scripts" / "nix" / "python-wrapper"


def render_wrapper(paths: Paths, version: str) -> Path:
    paths.bin_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = paths.wrapper(version)
    interpreter = paths.interpreter(version)
    template_path = wrapper_template_path(paths.is_windows)
    if not template_path.exists():
        fail(f"wrapper template missing: {template_path} (repo checkout is incomplete)")
    template = template_path.read_text()
    wrapper_path.write_text(template.format(interpreter=interpreter))
    if not paths.is_windows:
        # Set an explicit owner-only mode rather than OR-ing onto whatever
        # the umask produced -- ORing onto a permissive default (e.g. 644)
        # can leak group/other access instead of enforcing 700 throughout.
        wrapper_path.chmod(stat.S_IRWXU)
    return wrapper_path


def wrapper_matches(paths: Paths, version: str) -> bool:
    """True if the wrapper already exists and already points at this version's
    interpreter. Catches UnicodeDecodeError/OSError gracefully so a stray
    binary at the wrapper path doesn't crash the installer."""
    wrapper_path = paths.wrapper(version)
    if not wrapper_path.exists():
        return False
    try:
        content = wrapper_path.read_text()
    except (UnicodeDecodeError, OSError):
        log(
            f"warning: {wrapper_path} exists but isn't a text file this "
            f"installer recognises. If it's left over from a different "
            f"install method, move it aside first: mv {wrapper_path} "
            f"{wrapper_path}.bak"
        )
        return False
    return str(paths.interpreter(version)) in content


def path_contains(directory: Path) -> bool:
    path_var = os.environ.get("PATH", "")
    separator = ";" if os.name == "nt" else ":"
    parts = {Path(p) for p in path_var.split(separator) if p}
    return directory in parts


def main() -> int:
    parser = argparse.ArgumentParser(description="Install a self-contained CPython runtime, Fluent-style.")
    parser.add_argument(
        "--track",
        default=DEFAULT_TRACK,
        help=f"Python minor version track to install, e.g. 3.12 (default: {DEFAULT_TRACK})",
    )
    parser.add_argument("--force", action="store_true", help="Reinstall even if this version's wrapper already matches.")
    args = parser.parse_args()

    try:
        refuse_root()
        triple = target_triple()
        paths = Paths()

        log(f"looking up latest {GITHUB_REPO} release...")
        release = http_get_json(f"{GITHUB_API}/releases/latest")
        tag = release.get("tag_name", "unknown")
        log(f"release {tag}")

        asset, version = find_asset(release, triple, args.track)
        log(f"selected CPython {version} ({triple}, {FLAVOR})")

        if not args.force and wrapper_matches(paths, version):
            log(f"CPython {version} is already installed and the wrapper is current: {paths.wrapper(version)}")
            log("pass --force to reinstall anyway.")
            return 0

        checksums_asset = next((a for a in release.get("assets", []) if a["name"] == "SHA256SUMS"), None)
        if checksums_asset is None:
            fail(f"release {tag} has no SHA256SUMS asset; refusing to install unverified.")

        with tempfile.TemporaryDirectory(prefix="python-tool-") as tmp:
            tmp_path = Path(tmp)
            sums_path = tmp_path / "SHA256SUMS"
            log("downloading SHA256SUMS...")
            download(checksums_asset["browser_download_url"], sums_path)
            checksums = parse_sha256sums(sums_path.read_text())

            asset_name = asset["name"]
            expected_digest = checksums.get(asset_name)
            if not expected_digest:
                fail(f"{asset_name} is not listed in SHA256SUMS for release {tag}; refusing to install unverified.")

            archive_path = tmp_path / asset_name
            log(f"downloading {asset_name} ({asset.get('size', 0) // (1024 * 1024)} MiB)...")
            download(asset["browser_download_url"], archive_path)

            log("verifying SHA-256...")
            actual_digest = sha256_of(archive_path)
            if actual_digest != expected_digest:
                fail(
                    f"checksum mismatch for {asset_name}: expected {expected_digest}, "
                    f"got {actual_digest}. Not installing a runtime that failed verification."
                )

            version_dir = paths.version_dir(version)
            if version_dir.exists():
                log(f"removing existing install at {version_dir} before re-extracting...")
                shutil.rmtree(version_dir)

            log(f"extracting to {version_dir}...")
            extract(archive_path, version_dir)

        make_owner_only(paths.version_dir(version))

        interpreter = paths.interpreter(version)
        if not interpreter.exists():
            fail(f"expected interpreter not found after extraction: {interpreter}")
        # make_owner_only() above already set owner-only, execute-preserving
        # permissions on everything under version_dir, interpreter included.

        wrapper_path = render_wrapper(paths, version)
        log(f"wrapper installed: {wrapper_path} -> {interpreter}")

        if not path_contains(paths.bin_dir):
            log(
                f"warning: {paths.bin_dir} is not on PATH. Add it in your "
                f"shell profile (or the equivalent env file convention) to "
                f"run '{paths.wrapper_name(version)}' from anywhere."
            )

        log(f"done. CPython {version} installed. Try: {paths.wrapper_name(version)} --version")
        return 0

    except InstallError as exc:
        print(f"[python-tool] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
