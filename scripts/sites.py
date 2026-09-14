#!/usr/bin/env python3
"""Lê o site de cada entidade: tecnologia instalada, chamadas para ação, frescor e desempenho.

Uso:
  python3 sites.py <pasta>                    # tudo, com desempenho no celular
  python3 sites.py <pasta> --sem-desempenho
  python3 sites.py <pasta> --descobrir        # só lista as redes sociais linkadas em cada site
  python3 sites.py <pasta> --so slug1,slug2

Desempenho: API do PageSpeed se houver PAGESPEED_API_KEY; senão Lighthouse local (npx,
precisa de Node e Chrome); senão fica de fora. Grava <pasta>/dados/sites.json.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sc import carregar_chaves  # noqa: E402

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")

TECNOLOGIAS = {
    "Google Analytics 4": r"googletagmanager\.com/gtag|google-analytics\.com/g/|gtag\(['\"]config['\"],\s*['\"]G-",
    "Google Tag Manager": r"googletagmanager\.com/gtm|GTM-[A-Z0-9]{4,}",
    "Pixel da Meta": r"connect\.facebook\.net/[^\"']*fbevents|fbq\(|facebook\.com/tr\?",
    "Google Ads (conversão/remarketing)": r"googleadservices|doubleclick\.net/pagead|googleads\.g\.doubleclick|AW-\d{6,}",
    "LinkedIn Insight": r"snap\.licdn|_linkedin_partner|px\.ads\.linkedin",
    "Pixel do TikTok": r"analytics\.tiktok",
    "RD Station": r"rdstation|d335luupugsy2",
    "HubSpot": r"hs-scripts|js\.hs-|hubspot",
    "ActiveCampaign": r"activehosted|trackcmp",
    "Hotjar": r"hotjar",
    "Microsoft Clarity": r"clarity\.ms",
    "Chat no site": r"tawk\.to|jivosite|jivochat|zendesk|intercom|crisp\.chat|movidesk|blip\.ai|octadesk|zenvia|joinchat|chaty|manychat",
    "Link de WhatsApp": r"wa\.me/|api\.whatsapp\.com",
    "Aviso de cookies/LGPD": r"cookiebot|onetrust|cookieyes|complianz|adopt\.app|cookie-notice|lgpd",
    "WordPress": r"wp-content|wp-includes",
    "Elementor": r"elementor",
    "Wix": r"wixstatic|static\.wix",
    "Webflow": r"webflow",
    "Shopify": r"cdn\.shopify",
    "VTEX": r"vtex(commerce|assets)|\.vtex\.",
    "Nuvemshop": r"nuvemshop|tiendanube",
}

REDES = r"https?://(?:www\.|br\.|m\.)?(?:facebook|instagram|linkedin|youtube|tiktok|twitter|x)\.com/[A-Za-z0-9_.@/%-]+"
IGNORAR_REDE = re.compile(r"/(p|reel|reels|watch|sharer|share|intent|tr|plugins|embed|hashtag|explore)\b|sharer\.php", re.I)
VERBOS_CTA = re.compile(
    r"associ|seja|fa[çc]a parte|quero|fale|contato|or[çc]amento|agend|compr|inscrev|cadastr|"
    r"solicit|pe[çc]a|baix|assine|teste gr|experimente|whatsapp|come[çc]ar|conhe[çc]a", re.I)
CATEGORIAS_LH = ["performance", "seo", "accessibility", "best-practices"]


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.geturl(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:  # noqa: BLE001 — site fora do ar, SSL etc.
        return None, url, str(e)


def _texto(fragmento):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragmento)).strip()


def ler_home(html):
    titulo = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    meta = re.search(r"<meta[^>]+name=[\"']description[\"'][^>]*content=[\"']([^\"']*)", html, re.I) or \
        re.search(r"<meta[^>]+content=[\"']([^\"']*)[\"'][^>]*name=[\"']description[\"']", html, re.I)
    h1 = [_texto(x)[:120] for x in re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)]
    textos_link = [_texto(x) for x in re.findall(r"<(?:a|button)[^>]*>(.*?)</(?:a|button)>", html, re.S | re.I)]
    ctas = []
    for t in textos_link:
        if t and len(t) <= 45 and VERBOS_CTA.search(t) and t not in ctas:
            ctas.append(t)
    redes = sorted({u.rstrip("/") for u in re.findall(REDES, html) if not IGNORAR_REDE.search(u)})
    hoje = date.today()
    datas = []
    for d, m, a in re.findall(r"\b(\d{2})[/.](\d{2})[/.](20\d{2})\b", html):
        try:
            datas.append(date(int(a), int(m), int(d)))
        except ValueError:
            pass
    for a, m, d in re.findall(r"\b(20\d{2})-(\d{2})-(\d{2})\b", html):
        try:
            datas.append(date(int(a), int(m), int(d)))
        except ValueError:
            pass
    passadas = [d for d in datas if d <= hoje]  # datas futuras costumam ser agenda de evento
    return {
        "titulo": _texto(titulo.group(1))[:150] if titulo else None,
        "meta_descricao": meta.group(1)[:220] if meta else None,
        "h1": h1[:3],
        "ctas": ctas[:12],
        "redes": redes,
        "data_mais_recente": max(passadas).isoformat() if passadas else None,
    }


def detectar(blob):
    return [nome for nome, padrao in TECNOLOGIAS.items() if re.search(padrao, blob, re.I)]


def resumo_lighthouse(lh, crux=None):
    c, a = lh.get("categories", {}), lh.get("audits", {})

    def nota(k):
        s = (c.get(k) or {}).get("score")
        return round(s * 100) if s is not None else None

    peso = (a.get("total-byte-weight") or {}).get("numericValue")
    urls = [i.get("url", "") for i in ((a.get("network-requests") or {}).get("details") or {}).get("items", [])]
    return {
        "desempenho": nota("performance"), "seo": nota("seo"),
        "acessibilidade": nota("accessibility"), "boas_praticas": nota("best-practices"),
        "lcp": (a.get("largest-contentful-paint") or {}).get("displayValue"),
        "cls": (a.get("cumulative-layout-shift") or {}).get("displayValue"),
        "tbt": (a.get("total-blocking-time") or {}).get("displayValue"),
        "peso_mb": round(peso / 1_048_576, 1) if peso else None,
        "experiencia_real_crux": crux,
        "_urls_rede": urls,
    }


def pagespeed(url, chave):
    params = [("url", url), ("strategy", "mobile"), ("key", chave)] + \
             [("category", c.upper().replace("-", "_")) for c in CATEGORIAS_LH]
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(endpoint, timeout=180) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        return {"erro": f"PageSpeed HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"erro": f"PageSpeed: {e}"}
    res = resumo_lighthouse(d.get("lighthouseResult", {}),
                            (d.get("loadingExperience") or {}).get("overall_category"))
    res["fonte"] = "PageSpeed Insights"
    return res


def lighthouse_local(url):
    npx = shutil.which("npx")
    if not npx:
        return {"erro": "sem chave do PageSpeed e sem Node/npx para o Lighthouse local"}
    with tempfile.TemporaryDirectory() as tmp:
        saida = Path(tmp) / "lh.json"
        cmd = [npx, "-y", "lighthouse", url, "--quiet", "--chrome-flags=--headless=new",
               f"--only-categories={','.join(CATEGORIAS_LH)}", "--output=json", f"--output-path={saida}"]
        try:
            subprocess.run(cmd, capture_output=True, timeout=240, check=False)
            lh = json.loads(saida.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            return {"erro": f"Lighthouse local falhou: {e}"}
    if lh.get("runtimeError"):
        return {"erro": f"Lighthouse: {lh['runtimeError'].get('code')}"}
    res = resumo_lighthouse(lh)
    res["fonte"] = "Lighthouse local"
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta")
    ap.add_argument("--sem-desempenho", action="store_true")
    ap.add_argument("--descobrir", action="store_true")
    ap.add_argument("--so", default="")
    args = ap.parse_args()

    pasta = Path(args.pasta).expanduser().resolve()
    cfg = json.loads((pasta / "config.json").read_text(encoding="utf-8"))
    so = {s.strip() for s in args.so.split(",") if s.strip()}
    chave_psi = carregar_chaves().get("PAGESPEED_API_KEY")
    destino = pasta / "dados" / "sites.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    resultado = {}
    if destino.is_file() and not args.descobrir:
        resultado = json.loads(destino.read_text(encoding="utf-8"))
    raw_sites = pasta / "dados" / f"raw-{date.today().isoformat()}" / "sites"

    for e in cfg["entidades"]:
        if so and e["slug"] not in so:
            continue
        url = e.get("site")
        if not url:
            print(f"{e['nome']}: sem site no config")
            continue
        status, final, html = baixar(url)
        home = ler_home(html) if html and status == 200 else {}
        if args.descobrir:
            print(f"{e['nome']} ({final}) → HTTP {status}")
            for r in home.get("redes", []):
                print(f"   {r}")
            continue

        print(f"→ {e['nome']}: HTTP {status}")
        raw_sites.mkdir(parents=True, exist_ok=True)
        if html:
            (raw_sites / f"{e['slug']}.html").write_text(html, encoding="utf-8")
        item = {"url": url, "url_final": final, "status": status, "coletado_em": datetime.now().isoformat(timespec="minutes"),
                **home}
        if status != 200:
            item["aviso"] = "o site não entregou a página para leitura automática — conferir no navegador"
        tecnologias = set(detectar(html)) if html else set()

        if not args.sem_desempenho:
            desempenho = pagespeed(url, chave_psi) if chave_psi else lighthouse_local(url)
            if chave_psi and desempenho.get("erro"):
                print(f"   ! {desempenho['erro']} — tentando Lighthouse local")
                desempenho = lighthouse_local(url)
            tecnologias |= set(detectar("\n".join(desempenho.pop("_urls_rede", []))))
            item["desempenho"] = desempenho
            if desempenho.get("erro"):
                print(f"   ! {desempenho['erro']}")
            else:
                print(f"   desempenho {desempenho['desempenho']} · SEO {desempenho['seo']} · LCP {desempenho['lcp']} ({desempenho['fonte']})")
        elif (resultado.get(e["slug"]) or {}).get("desempenho"):
            item["desempenho"] = resultado[e["slug"]]["desempenho"]

        item["tecnologias"] = sorted(tecnologias)
        print(f"   tecnologias: {', '.join(item['tecnologias']) or 'nenhuma detectada'}")
        print(f"   CTAs: {', '.join(home.get('ctas', [])[:6]) or '—'}")
        resultado[e["slug"]] = item

    if not args.descobrir:
        destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nGravado: {destino}")


if __name__ == "__main__":
    main()
