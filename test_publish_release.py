#!/usr/bin/env python3
#
# source
#   project: sat-doc-automa
#   path: test_publish_release.py
#
"""
test_publish_release.py, offline test suite for publish-release.py.

Builds scratch git repositories with a local bare `origin` (so the
transport-layer preflight, ls-remote, works with no network), publishes
through the dir backend (the narrowest backend doubling as the test
fixture, as intended), and exercises every refusal.

Usage:
    python3 test_publish_release.py

Exit 0 with a PASS line per test, or exit 1 at the first failure.
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "publish-release.py"

PASSED = 0


def sh(cwd, *args, check=True):
    r = subprocess.run(list(args), cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"fixture command failed: {' '.join(args)}\n"
                           f"{r.stderr}")
    return r


def ok(name):
    global PASSED
    PASSED += 1
    print(f"  PASS  {name}")


def check(cond, name, detail=""):
    if not cond:
        print(f"  FAIL  {name}\n{detail}", file=sys.stderr)
        sys.exit(1)
    ok(name)


def make_repo(root: Path) -> Path:
    """A release-managed scratch repo at v0.1.0, tag cut and pushed to
    a local bare origin."""
    repo = root / "scratch"
    repo.mkdir()
    sh(repo, "git", "init", "-q", "-b", "main")
    sh(repo, "git", "config", "user.name", "Test")
    sh(repo, "git", "config", "user.email", "test@example.invalid")
    (repo / "VERSION").write_text("0.1.0\n")
    (repo / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-08-02\n\n"
        "### Added\n\n- First release.\n")
    (repo / "README.md").write_text("# scratch\n")
    shutil.copyfile(SCRIPT, repo / "publish-release.py")
    sh(repo, "git", "add", "-A")
    sh(repo, "git", "commit", "-q", "-m", "initial")
    sh(repo, "git", "tag", "-a", "v0.1.0", "-m", "version 0.1.0")
    origin = root / "scratch.git"
    sh(root, "git", "init", "-q", "--bare", str(origin))
    sh(repo, "git", "remote", "add", "origin", str(origin))
    sh(repo, "git", "push", "-q", "origin", "main", "v0.1.0")
    return repo


def publish(repo, *extra):
    return subprocess.run(
        [sys.executable, str(repo / "publish-release.py"), *extra],
        cwd=repo, capture_output=True, text=True)


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        repo = make_repo(root)
        target = root / "published"

        # ── Happy path: dry run builds artifacts, publishes nothing ──
        r = publish(repo, "--backend", "dir", "--target", str(target),
                    "--dry-run", "--no-sign")
        check(r.returncode == 0, "dry run exits 0", r.stderr)
        tarball = repo / "dist" / "scratch-0.1.0.tar.gz"
        sums = repo / "dist" / "SHA256SUMS"
        check(tarball.is_file() and sums.is_file(),
              "dry run leaves tarball and SHA256SUMS in dist/")
        check(not target.exists(), "dry run publishes nothing")
        digest = hashlib.sha256(tarball.read_bytes()).hexdigest()
        check(sums.read_text() == f"{digest}  {tarball.name}\n",
              "SHA256SUMS matches the tarball, coreutils format")

        # ── The tarball is a valid archive with the right prefix ──
        import tarfile
        with tarfile.open(tarball) as tf:
            names = tf.getnames()
        check(names and all(n == "scratch-0.1.0"
                            or n.startswith("scratch-0.1.0/")
                            for n in names)
              and "scratch-0.1.0/VERSION" in names,
              "tarball extracts with the <repo>-<version>/ prefix")

        # ── Determinism across separate invocations ──
        first = digest
        r = publish(repo, "--backend", "dir", "--target", str(target),
                    "--dry-run", "--no-sign")
        check(r.returncode == 0, "second dry run exits 0", r.stderr)
        second = hashlib.sha256(tarball.read_bytes()).hexdigest()
        check(first == second,
              "tarball bytes identical across separate invocations")

        # ── Publish through the dir backend ──
        r = publish(repo, "--backend", "dir", "--target", str(target),
                    "--no-sign")
        check(r.returncode == 0, "publish via dir backend exits 0",
              r.stderr)
        rel = target / "v0.1.0"
        check((rel / "scratch-0.1.0.tar.gz").is_file()
              and (rel / "SHA256SUMS").is_file(),
              "artifacts land in target/v0.1.0/")
        if shutil.which("sha256sum"):
            v = subprocess.run(["sha256sum", "-c", "SHA256SUMS"],
                               cwd=rel, capture_output=True, text=True)
            check(v.returncode == 0,
                  "sha256sum -c verifies as a consumer would",
                  v.stdout + v.stderr)

        # ── Refusal: releases are never reused ──
        r = publish(repo, "--backend", "dir", "--target", str(target),
                    "--no-sign")
        check(r.returncode != 0 and "already exists" in r.stderr,
              "re-publish of the same tag refuses", r.stderr)

        # ── Refusal: auto-sign absence never blocks ──
        r = publish(repo, "--backend", "dir",
                    "--target", str(root / "p2"), "--dry-run")
        check(r.returncode == 0,
              "auto sign mode proceeds unsigned when no key exists",
              r.stderr)

        # ── Refusal: no backend for an unrecognized remote ──
        r = publish(repo, "--dry-run")
        check(r.returncode != 0 and "No backend for remote" in r.stderr,
              "unrecognized remote with no --backend refuses", r.stderr)

        # ── Refusal: VERSION with no tag ──
        (repo / "VERSION").write_text("0.2.0\n")
        sh(repo, "git", "commit", "-aqm", "bump without cut")
        r = publish(repo, "--backend", "dir", "--target", str(target),
                    "--dry-run", "--no-sign")
        check(r.returncode != 0 and "does not exist" in r.stderr
              and "cut-release.py" in r.stderr,
              "missing tag refuses and points at cut-release.py",
              r.stderr)

        # ── Refusal: tag exists locally but was never pushed ──
        sh(repo, "git", "tag", "-a", "v0.2.0", "-m", "version 0.2.0")
        r = publish(repo, "--backend", "dir", "--target", str(target),
                    "--dry-run", "--no-sign")
        check(r.returncode != 0 and "is not on origin" in r.stderr
              and "git push" in r.stderr,
              "unpushed tag refuses and shows the push commands",
              r.stderr)

        # ── Refusal: tag content disagrees with VERSION ──
        old = sh(repo, "git", "rev-list", "--max-count=1",
                 "v0.1.0").stdout.strip()
        (repo / "VERSION").write_text("0.3.0\n")
        sh(repo, "git", "commit", "-aqm", "bump to 0.3.0")
        sh(repo, "git", "tag", "-a", "v0.3.0", "-m", "wrong", old)
        sh(repo, "git", "push", "-q", "origin", "v0.3.0")
        r = publish(repo, "--backend", "dir", "--target", str(target),
                    "--dry-run", "--no-sign")
        check(r.returncode != 0 and "VERSION is" in r.stderr,
              "tag pointing at the wrong VERSION refuses", r.stderr)

        # ── Refusal: --sign with no usable key ──
        env_repo = make_repo(Path(tempfile.mkdtemp(dir=root)))
        r = subprocess.run(
            [sys.executable, str(env_repo / "publish-release.py"),
             "--backend", "dir", "--target", str(root / "p3"),
             "--dry-run", "--sign"],
            cwd=env_repo, capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(root / "nohome")})
        check(r.returncode != 0 and "no usable gpg" in r.stderr,
              "--sign with no key refuses", r.stderr)

        # ── Real signing with a throwaway key, when gpg is present ──
        if shutil.which("gpg"):
            gnupg = root / "gnupg"
            gnupg.mkdir(mode=0o700)
            env = {"PATH": "/usr/bin:/bin",
                   "GNUPGHOME": str(gnupg), "HOME": str(root)}
            gen = subprocess.run(
                ["gpg", "--batch", "--pinentry-mode", "loopback",
                 "--passphrase", "", "--quick-generate-key",
                 "test@example.invalid", "ed25519", "sign", "0"],
                capture_output=True, text=True, env=env)
            if gen.returncode == 0:
                srepo = make_repo(Path(tempfile.mkdtemp(dir=root)))
                r = subprocess.run(
                    [sys.executable,
                     str(srepo / "publish-release.py"),
                     "--backend", "dir",
                     "--target", str(root / "psign"), "--sign"],
                    cwd=srepo, capture_output=True, text=True, env=env)
                check(r.returncode == 0, "signed publish exits 0",
                      r.stderr)
                asc = root / "psign" / "v0.1.0" / "SHA256SUMS.asc"
                check(asc.is_file(),
                      "SHA256SUMS.asc travels with the release")
                v = subprocess.run(
                    ["gpg", "--verify", str(asc),
                     str(root / "psign" / "v0.1.0" / "SHA256SUMS")],
                    capture_output=True, text=True, env=env)
                check(v.returncode == 0,
                      "the signature verifies against SHA256SUMS",
                      v.stderr)
            else:
                print("  skip  gpg key generation unavailable here")
        else:
            print("  skip  gpg not installed here")

    print(f"\n[test-publish-release] {PASSED} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
