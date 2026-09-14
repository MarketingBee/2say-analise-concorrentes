#!/usr/bin/env python3
"""Confere se a skill está pronta para rodar nesta máquina.

Uso: python3 checar.py [--testar-api]   (o teste da API gasta 1 crédito e mostra o saldo)
"""
import argparse
import platform
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sc import ScrapeCreators, carregar_chaves  # noqa: E402


def linha(ok, texto):
    print(f"  [{'ok' if ok else '--'}] {texto}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--testar-api", action="store_true")
    args = ap.parse_args()

    chaves = carregar_chaves()
    print(f"Sistema: {platform.system()} · Python {platform.python_version()}")
    print(f"Raiz do projeto desta instalação: {chaves['_raiz_projeto']}")
    linha(sys.version_info >= (3, 8), "Python 3.8 ou mais novo")
    linha(bool(chaves.get("_arquivo")),
          f"arquivo .env: {chaves.get('_arquivo') or 'não existe ainda — seria criado em ' + chaves['_onde_criar']}")
    sc_ok = bool(chaves.get("SCRAPECREATORS_API_KEY"))
    linha(sc_ok, "SCRAPECREATORS_API_KEY (obrigatória)")
    if not sc_ok:
        print("     → sem chave própria nesta instalação. Peça a chave da ScrapeCreators à"
              " pessoa (veja INSTALACAO.md) e grave com:")
        print(f"       python3 configurar.py --set SCRAPECREATORS_API_KEY=<chave colada aqui>")
    psi = bool(chaves.get("PAGESPEED_API_KEY"))
    npx = bool(shutil.which("npx"))
    linha(psi, "PAGESPEED_API_KEY (recomendada)")
    linha(npx, "Node/npx para Lighthouse local (plano B do desempenho)")
    if not psi and not npx:
        print("     → sem as duas, a análise sai sem a nota de desempenho do site.")

    if args.testar_api and sc_ok:
        d = ScrapeCreators(chaves["SCRAPECREATORS_API_KEY"]).get("/v1/instagram/profile",
                                                                  {"handle": "instagram", "trim": "true"})
        ok = d.get("credits_remaining") is not None
        linha(ok, f"API respondeu · créditos restantes: {d.get('credits_remaining')}" if ok
              else f"API falhou: {d.get('erro') or d.get('message')} {d.get('detalhe', '')}")

    if not sc_ok:
        print("\nFalta a chave da ScrapeCreators. Veja INSTALACAO.md na pasta da skill.")
        sys.exit(1)
    print("\nPronto para rodar." if sc_ok else "")


if __name__ == "__main__":
    main()
