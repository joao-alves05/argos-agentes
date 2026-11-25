"""Gera tests/proibidos.sha256 a partir de uma lista LOCAL de termos.

Uso:
    PRIVADO_TERMOS=/caminho/fora/do/repo/termos.txt python tests/gerar_proibidos.py

O arquivo de termos tem um termo por linha e NUNCA entra no repositório.
Só os hashes SHA-256 dos termos normalizados são escritos.
"""
import hashlib
import os
import re
import sys
import unicodedata
from pathlib import Path

SAIDA = Path(__file__).with_name("proibidos.sha256")
MAX_PALAVRAS = 3


def palavras(texto):
    """Minúsculas, sem acento, só letras e dígitos."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", sem_acento.lower())


def hash_termo(lista_palavras):
    return hashlib.sha256(" ".join(lista_palavras).encode("utf-8")).hexdigest()


def main():
    caminho = os.environ.get("PRIVADO_TERMOS")
    if not caminho:
        print(
            "Defina a variável PRIVADO_TERMOS com o caminho de um arquivo LOCAL,\n"
            "fora do repositório, com um termo proibido por linha.\n"
            "O script escreve apenas os hashes SHA-256 em tests/proibidos.sha256."
        )
        return 1
    hashes = set()
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            p = palavras(linha)
            if not p:
                continue
            if len(p) > MAX_PALAVRAS:
                print(f"aviso: termo com mais de {MAX_PALAVRAS} palavras ignorado", file=sys.stderr)
                continue
            hashes.add(hash_termo(p))
    SAIDA.write_text("\n".join(sorted(hashes)) + "\n", encoding="utf-8")
    print(f"{len(hashes)} hashes escritos em {SAIDA.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
