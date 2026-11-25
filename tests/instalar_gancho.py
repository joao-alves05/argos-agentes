"""Liga um hook de pre-commit local que roda o teste de privacidade (uso opcional)."""
import subprocess
import sys
from pathlib import Path

SCRIPT = """#!/bin/sh
# gerado por tests/instalar_gancho.py
cd "$(git rev-parse --show-toplevel)" || exit 1
PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python
exec "$PY" -m unittest discover -s tests -p "test_privacidade.py"
"""


def main():
    raiz = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
    ).stdout.strip()
    caminho = subprocess.run(
        ["git", "rev-parse", "--git-path", "hooks/pre-commit"],
        cwd=raiz, capture_output=True, text=True, check=True,
    ).stdout.strip()
    destino = Path(raiz) / caminho
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(SCRIPT, encoding="utf-8", newline="\n")
    destino.chmod(0o755)
    print("Hook de pre-commit instalado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
