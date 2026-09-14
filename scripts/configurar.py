#!/usr/bin/env python3
"""Cria ou atualiza o .env do projeto onde ESTA cópia da skill está instalada.

Uso:
  python3 configurar.py --onde
      Mostra a raiz do projeto detectada e onde o .env está (ou ficaria).

  python3 configurar.py --set SCRAPECREATORS_API_KEY=abc123
  python3 configurar.py --set SCRAPECREATORS_API_KEY=abc123 --set PAGESPEED_API_KEY=xyz789
      Cria o .env se não existir, ou atualiza a linha da chave se já existir (nunca
      duplica). Cada instalação desta skill (cada pasta de projeto diferente) grava no
      próprio .env — não existe chave "global" compartilhada por padrão.

Pensado para ser chamado a partir da conversa no Claude Code: peça a chave à pessoa no chat
e rode este comando com o valor recebido, em vez de pedir para ela editar um arquivo oculto
na mão.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sc import CHAVES, carregar_chaves, gravar_chave  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", metavar="NOME=valor", action="append", default=[],
                     help="pode repetir para gravar mais de uma chave de uma vez")
    ap.add_argument("--onde", action="store_true")
    args = ap.parse_args()

    if args.onde or not args.set:
        c = carregar_chaves()
        print(f"Raiz do projeto desta instalação: {c['_raiz_projeto']}")
        print(f".env: {c['_arquivo'] or 'não existe ainda — seria criado em ' + c['_onde_criar']}")
        if not args.set:
            if not args.onde:
                ap.error("use --set NOME=valor ou --onde")
            return

    for par in args.set:
        if "=" not in par:
            sys.exit(f"formato inválido: {par!r} — use NOME=valor")
        nome, valor = par.split("=", 1)
        nome, valor = nome.strip(), valor.strip()
        if nome not in CHAVES:
            sys.exit(f"chave desconhecida: {nome!r} (esperado uma de {', '.join(CHAVES)})")
        if not valor:
            sys.exit(f"valor vazio para {nome}")
        destino = gravar_chave(nome, valor)
        print(f"{nome} gravada em {destino}")


if __name__ == "__main__":
    main()
