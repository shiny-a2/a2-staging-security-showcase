#!/usr/bin/env python3
"""Reject credentials, private topology, or recovery artifacts in the showcase."""

import ipaddress
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


MAX_BYTES = 4 * 1024 * 1024
FORBIDDEN_SUFFIXES = (
    ".bak", ".backup", ".cer", ".crt", ".csv", ".db", ".dump", ".env",
    ".key", ".log", ".p12", ".pem", ".pfx", ".sig", ".sql", ".sqlite",
    ".tar", ".tar.gz", ".tgz", ".zip",
)
FORBIDDEN_NAMES = {".env", ".htpasswd", ".my.cnf", "id_ed25519", "id_rsa"}
FORBIDDEN_DIRECTORIES = {"artifacts", "backups", "dumps", "evidence", "secrets"}
DOMAIN = re.compile(
    rb"(?i)(?<![A-Za-z0-9_-])"
    rb"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    rb"(?:ai|app|biz|cloud|co|com|dev|info|io|ir|live|me|net|online|org|shop|site|store|tech|xyz)"
    rb"(?![A-Za-z0-9_-])"
)
ALLOWED_DOMAINS = {"example.com", "example.net", "example.org"}
IPV4 = re.compile(rb"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
IPV6 = re.compile(
    rb"(?<![0-9A-Fa-f:])(?=[0-9A-Fa-f:.]{2,45}(?![0-9A-Fa-f:.]))"
    rb"[0-9A-Fa-f:.]*:[0-9A-Fa-f:.]+"
)
ALLOWED_NETWORKS = tuple(
    ipaddress.ip_network(value)
    for value in (
        "0.0.0.0/32", "127.0.0.0/8", "192.0.2.0/24", "198.51.100.0/24",
        "203.0.113.0/24", "::/128", "::1/128", "2001:db8::/32",
    )
)
PRIVATE_NETWORKS = tuple(
    ipaddress.ip_network(value)
    for value in (
        "1" + "0.0.0.0/8", "100." + "64.0.0/10", "172." + "16.0.0/12",
        "192." + "168.0.0/16", "fc" + "00::/7",
    )
)
SECRET_PATTERNS = (
    ("private-key", re.compile(rb"-----BEGIN (?:EC |ENCRYPTED |OPENSSH |RSA )?PRIVATE KEY-----")),
    ("certificate", re.compile(rb"-----BEGIN " rb"CERTIFICATE-----")),
    ("aws-token", re.compile(rb"(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])")),
    ("github-token", re.compile(rb"(?<![A-Za-z0-9_])gh[pousr]_[A-Za-z0-9]{30,}")),
    ("google-token", re.compile(rb"(?<![A-Za-z0-9_-])AIza[0-9A-Za-z_-]{35}")),
    ("slack-token", re.compile(rb"(?<![A-Za-z0-9-])xox[baprs]-[A-Za-z0-9-]{20,}")),
    ("bearer-token", re.compile(rb"(?i)\bBearer[ \t]+[A-Za-z0-9._~+/=-]{20,}")),
    ("basic-auth-url", re.compile(rb"(?i)https?://[^/@:\s]{1,128}:[^/@\s]{4,128}@")),
    (
        "database-url-credential",
        re.compile(
            rb"(?i)\b(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|redis(?:s)?|amqp(?:s)?)"
            rb"://[^/@:\s]{1,128}:[^/@\s]{1,256}@"
        ),
    ),
)


def git(root: Path, *arguments: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("Git inspection failed")
    return result.stdout


def inspect(path: str, content: bytes, symbolic_link: bool = False) -> set[str]:
    findings: set[str] = set()
    normalized = PurePosixPath(path)
    parts = tuple(part.lower() for part in normalized.parts)
    basename = parts[-1] if parts else ""
    if symbolic_link:
        findings.add("symbolic-link")
        return findings
    if basename in FORBIDDEN_NAMES or basename.startswith(".env."):
        findings.add("sensitive-filename")
    if any(part in FORBIDDEN_DIRECTORIES for part in parts[:-1]):
        findings.add("sensitive-directory")
    if any(basename.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
        findings.add("sensitive-extension")
    if len(content) > MAX_BYTES:
        findings.add("oversized-file")
        return findings
    if b"\x00" in content[:8192]:
        findings.add("binary-file")
        return findings
    for rule, pattern in SECRET_PATTERNS:
        if pattern.search(content):
            findings.add(rule)
    for pattern in (IPV4, IPV6):
        for match in pattern.finditer(content):
            try:
                address = ipaddress.ip_address(match.group().decode("ascii"))
            except (UnicodeDecodeError, ValueError):
                continue
            if any(address in network for network in ALLOWED_NETWORKS):
                continue
            if address.is_global:
                findings.add("public-address")
            elif any(address in network for network in PRIVATE_NETWORKS):
                findings.add("private-topology")
    for match in DOMAIN.finditer(content):
        domain = match.group().decode("ascii").lower().rstrip(".")
        if domain not in ALLOWED_DOMAINS and not domain.endswith(
            (".example.com", ".example.net", ".example.org", ".example.test")
        ):
            findings.add("unapproved-domain")
    return findings


def entries(root: Path):
    staged = git(root, "ls-files", "--stage", "-z")
    for record in staged.split(b"\x00"):
        if not record:
            continue
        metadata, encoded_path = record.split(b"\t", 1)
        mode, object_id, _stage = metadata.split(b" ", 2)
        yield (
            os.fsdecode(encoded_path),
            git(root, "cat-file", "blob", object_id.decode("ascii")),
            mode == b"120000",
        )

    candidates = git(
        root, "ls-files", "-z", "--cached", "--others", "--exclude-standard"
    )
    for encoded in candidates.split(b"\x00"):
        if not encoded:
            continue
        relative = os.fsdecode(encoded)
        path = root.joinpath(*PurePosixPath(relative).parts)
        if path.is_symlink():
            yield relative, os.fsencode(os.readlink(path)), True
        elif path.is_file():
            yield relative, path.read_bytes(), False

    commits = git(root, "rev-list", "--all").splitlines()
    seen = set()
    for commit in commits:
        commit_name = commit.decode("ascii")
        raw = git(root, "cat-file", "commit", commit_name)
        _headers, boundary, message = raw.partition(b"\n\n")
        if not boundary:
            raise RuntimeError("Malformed commit object")
        yield f"<commit:{commit_name[:12]}>", message, False
        tree = git(root, "ls-tree", "-r", "-z", "--full-tree", commit_name)
        for record in tree.split(b"\x00"):
            if not record:
                continue
            metadata, encoded_path = record.split(b"\t", 1)
            mode, object_type, object_id = metadata.split(b" ", 2)
            identity = (object_id, encoded_path)
            if object_type != b"blob" or identity in seen:
                continue
            seen.add(identity)
            yield (
                os.fsdecode(encoded_path),
                git(root, "cat-file", "blob", object_id.decode("ascii")),
                mode == b"120000",
            )
    tag_records = git(
        root, "for-each-ref", "--format=%(objectname)%00%(refname)", "refs/tags"
    ).splitlines()
    for record in tag_records:
        object_id, boundary, reference = record.partition(b"\x00")
        if not boundary:
            raise RuntimeError("Malformed tag reference")
        object_name = object_id.decode("ascii")
        yield f"<tag-ref:{object_name[:12]}>", reference, False
        if git(root, "cat-file", "-t", object_name).strip() == b"tag":
            raw = git(root, "cat-file", "tag", object_name)
            _headers, message_boundary, message = raw.partition(b"\n\n")
            if not message_boundary:
                raise RuntimeError("Malformed annotated tag")
            yield f"<tag-message:{object_name[:12]}>", message, False


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings = set()
    try:
        for path, content, symbolic_link in entries(root):
            for rule in inspect(path, content, symbolic_link):
                findings.add((path, rule))
    except (OSError, RuntimeError) as error:
        print(f"showcase privacy gate: ERROR: {error}", file=sys.stderr)
        return 2
    if findings:
        print(f"showcase privacy gate: FAILED ({len(findings)} finding(s))", file=sys.stderr)
        for path, rule in sorted(findings):
            print(f"- {path}: {rule}", file=sys.stderr)
        return 1
    print("showcase privacy gate: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
