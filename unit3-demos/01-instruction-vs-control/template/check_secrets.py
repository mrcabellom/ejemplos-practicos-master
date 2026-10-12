"""Pre-commit control: blocks the commit if a staged file contains a secret.

A tiny stand-in for a real scanner such as gitleaks, with no downloads needed.
"""
import re
import subprocess
import sys

PATTERNS = {
    "token de GitHub": re.compile(r"ghp_[A-Za-z0-9]{36}"),
    "clave de acceso de AWS": re.compile(r"AKIA[0-9A-Z]{16}"),
    "clave privada": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def main():
    findings = []
    for path in git("diff", "--cached", "--name-only", "--diff-filter=ACM").splitlines():
        content = git("show", f":{path}")
        for number, line in enumerate(content.splitlines(), start=1):
            for kind, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(f"  {path}:{number}  {kind}")
    if findings:
        print("COMMIT BLOQUEADO: se han detectado secretos en los cambios preparados:")
        print("\n".join(findings))
        sys.exit(1)


if __name__ == "__main__":
    main()
