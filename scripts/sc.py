"""Chaves do .env e cliente mínimo da ScrapeCreators, compartilhados pelos outros scripts.

Onde fica o .env: a raiz do projeto onde ESTA cópia da skill está instalada — ou seja, a
pasta que contém o `.claude/` mais próximo, subindo a partir deste arquivo. Não presume
"2SAY" nem nenhum outro nome de pasta: cada pessoa que instalar esta skill num projeto
diferente (vault próprio, outra pasta local) tem sua própria raiz e seu próprio `.env`,
sem interferir no dos outros. Ver `raiz_projeto()` e `gravar_chave()`.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.scrapecreators.com"
CHAVES = ("SCRAPECREATORS_API_KEY", "PAGESPEED_API_KEY")


def raiz_projeto():
    """Pasta-raiz do projeto desta instalação: a que contém o `.claude/` mais próximo,
    subindo a partir deste arquivo. É assim que a mesma skill, copiada em vários projetos
    diferentes, acha o `.env` de cada um sem depender do nome da pasta."""
    aqui = Path(__file__).resolve().parent
    for pasta in (aqui, *aqui.parents):
        # pula um `.claude` que seja config global do usuário (ex.: ~/.claude/plugins/...),
        # não uma instalação de projeto — nesse caso cai no cwd abaixo
        if pasta.name == ".claude" and pasta.parent != Path.home():
            return pasta.parent
    return Path.cwd().resolve()


def _candidatos_env():
    raiz = raiz_projeto()
    vistos, candidatos = [], set()
    for c in (raiz / ".env", raiz / "2SAY" / ".env", Path.cwd().resolve() / ".env"):
        if c not in candidatos:
            candidatos.add(c)
            vistos.append(c)
    return vistos


def _achar_env():
    for candidato in _candidatos_env():
        if candidato.is_file():
            return candidato
    return None


def carregar_chaves():
    chaves = {}
    arquivo = _achar_env()
    if arquivo:
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                k, v = linha.split("=", 1)
                chaves[k.strip()] = v.strip().strip("'\"")
    for k in CHAVES:
        if os.environ.get(k):
            chaves[k] = os.environ[k]
    chaves["_arquivo"] = str(arquivo) if arquivo else None
    chaves["_raiz_projeto"] = str(raiz_projeto())
    chaves["_onde_criar"] = str(raiz_projeto() / ".env")
    return chaves


def gravar_chave(nome, valor, arquivo=None):
    """Cria o .env na raiz do projeto se não existir, ou atualiza a linha da chave se ela já
    existir (nunca duplica a linha). Devolve o Path do arquivo gravado."""
    if nome not in CHAVES:
        raise ValueError(f"chave desconhecida: {nome!r} (esperado uma de {', '.join(CHAVES)})")
    destino = Path(arquivo) if arquivo else (_achar_env() or (raiz_projeto() / ".env"))
    linhas = destino.read_text(encoding="utf-8").splitlines() if destino.is_file() else []
    prefixo = f"{nome}="
    for i, linha in enumerate(linhas):
        if linha.strip().startswith(prefixo):
            linhas[i] = f"{nome}={valor}"
            break
    else:
        linhas.append(f"{nome}={valor}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    try:
        destino.chmod(0o600)  # só o dono lê/escreve; Windows ignora isso sem erro
    except OSError:
        pass
    return destino


def ler_json(caminho):
    caminho = Path(caminho)
    if not caminho.is_file():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


class ScrapeCreators:
    def __init__(self, chave, pasta_raw=None):
        self.chave = chave
        self.pasta_raw = Path(pasta_raw) if pasta_raw else None
        if self.pasta_raw:
            self.pasta_raw.mkdir(parents=True, exist_ok=True)
        self.creditos = None
        self.chamadas = 0

    def get(self, caminho, params, nome_arquivo=None):
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        req = urllib.request.Request(f"{BASE}{caminho}?{query}", headers={"x-api-key": self.chave})
        dados = None
        for tentativa in range(3):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    corpo = r.read().decode("utf-8", "ignore")
                try:
                    dados = json.loads(corpo)
                except json.JSONDecodeError:
                    dados = {"erro": "resposta não-JSON", "detalhe": corpo[:200]}
                break
            except urllib.error.HTTPError as e:
                if e.code >= 500 and tentativa < 2:
                    time.sleep(3 * (tentativa + 1))
                    continue
                dados = {"erro": f"HTTP {e.code}", "detalhe": e.read().decode("utf-8", "ignore")[:300]}
                break
            except (urllib.error.URLError, TimeoutError) as e:
                if tentativa < 2:
                    time.sleep(3 * (tentativa + 1))
                    continue
                dados = {"erro": str(e)}
        self.chamadas += 1
        if isinstance(dados, dict) and dados.get("credits_remaining") is not None:
            self.creditos = dados["credits_remaining"]
        if self.pasta_raw and nome_arquivo:
            destino = self.pasta_raw / f"{nome_arquivo}.json"
            destino.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
        return dados
