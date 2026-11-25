"""Liga um hook de pre-commit local que roda o teste de privacidade (uso opcional)."""
import subprocess
import sys
from pathlib import Path

SCRIPT = """#!/bin/sh
# gerado por tests/instalar_gancho.py
cd "$(git rev-parse --show-toplevel)" || exit 1
PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
exec "$PY" -m unittest discover -s tests -p "test_privacidade.py"
"""


def main():
    caminho = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-path", "hooks/pre-commit"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.strip()
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(SCRIPT, encoding="utf-8", newline="\n")
    destino.chmod(0o755)
    print("Hook de pre-commit instalado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
