#!/bin/sh
# install.sh -- no-Python bootstrap for python-tool on Linux and macOS.
#
# install-python.py is itself a Python script, so it can't be the first
# thing that runs on a machine with no Python at all. This script exists
# to solve exactly that, and only that. It does not reimplement the real
# install: it fetches a small, pinned, checksum-verified, disposable
# CPython build, uses it once to run install-python.py, then deletes it.
# The permanent, governed, checksum-verified install still comes entirely
# from install-python.py's own release lookup, exactly as if you already
# had a working `python3` on the machine.
#
# Requires only `curl` and `tar`. Both ship unconditionally as base OS
# utilities on Linux and macOS; neither is part of the Xcode Command Line
# Tools' gated set on macOS, so this runs on a genuinely fresh Mac with no
# developer tooling installed at all.
#
# Usage:
#   ./install.sh [args passed through to install-python.py]
#   ./install.sh --track 3.11

set -eu

# Pinned bootstrap release. This intentionally does NOT look up "latest"
# from the GitHub API: the bootstrap Python is disposable and only needs
# to be capable of running install-python.py, which does its own, current,
# checksum-verified release lookup for the real, permanent install. Pinning
# avoids a GitHub API dependency (and its rate limits) in the one script
# that most needs to be simple and hard to break.
BOOTSTRAP_TAG="20250828"
BOOTSTRAP_BASE_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${BOOTSTRAP_TAG}"

fail() {
    echo "[install.sh] ERROR: $1" >&2
    exit 1
}

log() {
    echo "[install.sh] $1"
}

# Refuse root, same as install-python.py: this is strictly a user-space tool.
if [ "$(id -u)" = "0" ]; then
    fail "refusing to run as root. python-tool installs entirely in user-space under \$HOME."
fi

command -v curl >/dev/null 2>&1 || fail "curl is required but was not found."
command -v tar >/dev/null 2>&1 || fail "tar is required but was not found."
# Some GNU tar builds (notably on minimal Linux images) don't link zlib and
# shell out to a separate gzip binary for -z decompression instead. macOS's
# tar and Windows' bundled tar.exe are both libarchive-based and don't have
# this issue, but check for it explicitly here rather than letting it fail
# with a cryptic internal tar error later.
if [ "$(uname -s)" = "Linux" ]; then
    command -v gzip >/dev/null 2>&1 || fail "gzip is required but was not found (this GNU tar build shells out to it for .tar.gz extraction)."
fi

# Resolve the directory this script lives in, so install-python.py is found
# next to it regardless of the caller's current working directory.
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
INSTALL_PY="${SCRIPT_DIR}/install-python.py"
[ -f "$INSTALL_PY" ] || fail "install-python.py not found next to this script at ${INSTALL_PY}. Check out the full repository, not just this file."

OS=$(uname -s)
ARCH=$(uname -m)

case "${OS}-${ARCH}" in
    Linux-x86_64)
        TRIPLE="x86_64-unknown-linux-gnu"
        SHA256="248489659e202cc72971181f88eb28e06ad54690369efdfea0f938f0cb14c976"
        ;;
    Linux-aarch64)
        TRIPLE="aarch64-unknown-linux-gnu"
        SHA256="dc7a9afec9592aeb79f672dc3035f2ba401b93ad09c30acd862df54a848872bb"
        ;;
    Darwin-x86_64)
        TRIPLE="x86_64-apple-darwin"
        SHA256="453255250a3777bce345d793f78c9f878b901c355ce2795cc44c9a0e31552c41"
        ;;
    Darwin-arm64)
        TRIPLE="aarch64-apple-darwin"
        SHA256="b3c05a001ceae5214b9d279bd17d3e415275d06a126b62693a27a70d92f9e63c"
        ;;
    *)
        fail "unsupported platform ${OS}/${ARCH}. Supported: Linux x86_64/aarch64, macOS x86_64/arm64."
        ;;
esac

FILENAME="cpython-3.11.13+${BOOTSTRAP_TAG}-${TRIPLE}-install_only_stripped.tar.gz"
URL="${BOOTSTRAP_BASE_URL}/${FILENAME}"

TMP_DIR=$(mktemp -d)
trap 'rm -rf "${TMP_DIR}"' EXIT INT TERM

ARCHIVE="${TMP_DIR}/${FILENAME}"

log "downloading bootstrap Python (${TRIPLE})..."
curl -fsSL -o "${ARCHIVE}" "${URL}" || fail "download failed for ${URL}"

log "verifying checksum..."
if command -v sha256sum >/dev/null 2>&1; then
    ACTUAL=$(sha256sum "${ARCHIVE}" | awk '{print $1}')
elif command -v shasum >/dev/null 2>&1; then
    ACTUAL=$(shasum -a 256 "${ARCHIVE}" | awk '{print $1}')
else
    fail "no sha256 tool found (need sha256sum or shasum)."
fi
[ "${ACTUAL}" = "${SHA256}" ] || fail "checksum mismatch for ${FILENAME}: expected ${SHA256}, got ${ACTUAL}"

log "extracting..."
tar -xzf "${ARCHIVE}" -C "${TMP_DIR}" || fail "extraction failed"

BOOTSTRAP_PYTHON="${TMP_DIR}/python/bin/python3.11"
[ -x "${BOOTSTRAP_PYTHON}" ] || fail "expected interpreter not found after extraction: ${BOOTSTRAP_PYTHON}"

log "bootstrap Python ready. Handing off to install-python.py for the real, verified install..."
"${BOOTSTRAP_PYTHON}" "${INSTALL_PY}" "$@"
STATUS=$?

log "done (bootstrap Python will now be cleaned up; it was never the permanent install)."
exit "${STATUS}"
