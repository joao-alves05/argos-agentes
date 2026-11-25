"""Falha se qualquer arquivo versionado tiver dado pessoal ou segredo."""
import re
import subprocess
import unittest
from pathlib import Path

from gerar_proibidos import MAX_PALAVRAS, hash_termo, palavras

RAIZ = Path(__file__).resolve().parent.parent
HASHES = Path(__file__).with_name("proibidos.sha256")

PADROES = {
    "e-mail": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "telefone": re.compile(
        r"(?<!\d)(?:\+55[\s-]?)?\(?[1-9]\d\)?[\s.-]?9\d{4}[\s.-]?\d{4}(?!\d)"
        r"|(?<!\d)(?:\+55[\s-]?)?\([1-9]\d\)\s?\d{4}-?\d{4}(?!\d)"
    ),
    "caminho de usuário do Windows": re.compile(r"[A-Za-z]:\\+Users\\+[^\\\s]|/[a-z]/Users/", re.I),
    "IPv4": re.compile(r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\d.])"),
    "chave/token": re.compile(
        r"sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}"
        r"|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    ),
}


def ip_publico(texto):
    a, b = (int(x) for x in texto.split(".")[:2])
    return not (
        a in (0, 10, 127) or a >= 224
        or (a == 172 and 16 <= b <= 31)
        or (a == 192 and b == 168)
        or (a == 169 and b == 254)
    )


def arquivos():
    saida = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=RAIZ, capture_output=True, text=True, check=True,
    ).stdout
    for nome in saida.splitlines():
        caminho = RAIZ / nome
        if caminho.is_file() and caminho != HASHES:
            yield nome, caminho


def carregar_hashes():
    if not HASHES.exists():
        return set()
    return {l.strip() for l in HASHES.read_text(encoding="utf-8").splitlines() if l.strip()}


def achados_do_texto(texto, proibidos):
    achados = []
    for rotulo, rx in PADROES.items():
        for m in rx.finditer(texto):
            if rotulo == "IPv4" and not ip_publico(m.group()):
                continue
            achados.append(rotulo)
    p = palavras(texto)
    vistos = set()
    for n in range(1, MAX_PALAVRAS + 1):
        for i in range(len(p) - n + 1):
            if hash_termo(p[i:i + n]) in proibidos:
                vistos.add(1)
    if vistos:
        achados.append("termo proibido")
    return achados


class TestPrivacidade(unittest.TestCase):
    def test_hashes_existem(self):
        self.assertTrue(carregar_hashes(), "tests/proibidos.sha256 vazio ou ausente")

    def test_nenhum_dado_pessoal(self):
        proibidos = carregar_hashes()
        problemas = []
        for nome, caminho in arquivos():
            try:
                texto = caminho.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            # o nome do arquivo também conta
            for rotulo in achados_do_texto(nome + "\n" + texto, proibidos):
                problemas.append(f"{nome}: {rotulo}")
        # nunca imprime o trecho achado, só o arquivo e o tipo
        self.assertEqual(problemas, [], "\n".join(problemas))

    def test_detectores_funcionam(self):
        ex = {
            "e-mail": "fulano" + "@" + "exemplo.org",
            "telefone": "(51) 9" + "8765-4321",
            "caminho de usuário do Windows": "C:" + chr(92) + "Users" + chr(92) + "alguem",
            "IPv4": "8.8" + ".4.4",
            "chave/token": "gh" + "p_" + "a" * 30,
        }
        for rotulo, texto in ex.items():
            self.assertIn(rotulo, achados_do_texto(texto, set()), rotulo)
        self.assertEqual(achados_do_texto("192.168.0.1 e 3.12", set()), [])
        self.assertIn("termo proibido", achados_do_texto("Olá Ação", {hash_termo(["ola", "acao"])}))


if __name__ == "__main__":
    unittest.main()
