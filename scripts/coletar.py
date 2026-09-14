#!/usr/bin/env python3
"""Coleta dados públicos das entidades do config.json via ScrapeCreators.

Uso:
  python3 coletar.py <pasta> --estimar
  python3 coletar.py <pasta> [--canais instagram,facebook,anuncios,linkedin,youtube,tiktok]
                             [--so slug1,slug2] [--paginas-ig 5]
  python3 coletar.py <pasta> --so-normalizar

Grava as respostas cruas em <pasta>/dados/raw-AAAA-MM-DD/ e o consolidado em
<pasta>/dados/coleta.json. --so-normalizar refaz o coleta.json a partir da pasta raw mais
recente, sem gastar crédito.
"""
import argparse
import json
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sc import ScrapeCreators, carregar_chaves, ler_json  # noqa: E402

CANAIS = ["instagram", "facebook", "anuncios", "linkedin", "youtube", "tiktok"]


def custo_estimado(e, canais, paginas_ig):
    c = 0
    if "instagram" in canais and e.get("instagram"):
        c += 1 + paginas_ig
    if "facebook" in canais and e.get("facebook"):
        c += 1
    if "anuncios" in canais:
        c += 1 if (e.get("meta_page_id") or e.get("facebook")) else 2
    if "linkedin" in canais and e.get("linkedin"):
        c += 2
    if "youtube" in canais and e.get("youtube"):
        c += 2
    if "tiktok" in canais and e.get("tiktok"):
        c += 1
    return c


# ---------- coleta ----------

def coletar_instagram(sc, e, dias, max_paginas):
    h = e["instagram"].lstrip("@")
    perfil = sc.get("/v1/instagram/profile", {"handle": h}, f"{e['slug']}__ig_perfil")
    if perfil.get("erro") or perfil.get("success") is False:
        print(f"   ! Instagram @{h}: {perfil.get('erro') or perfil.get('message')}")
        return
    limite = time.time() - (dias + 2) * 86400
    cursor = None
    for p in range(1, max_paginas + 1):
        d = sc.get("/v2/instagram/user/posts", {"handle": h, "next_max_id": cursor},
                   f"{e['slug']}__ig_posts_p{p}")
        itens = d.get("items") or []
        # post fixado tem data antiga e não indica que a página chegou ao fim da janela
        datas = [i.get("taken_at") or 0 for i in itens if not i.get("timeline_pinned_user_ids")]
        cursor = d.get("next_max_id")
        if not itens or not cursor or d.get("more_available") is False:
            break
        if datas and min(datas) < limite:
            break


def coletar_anuncios(sc, e, fb, desde, pais):
    page_id = e.get("meta_page_id") or ((fb or {}).get("adLibrary") or {}).get("pageId")
    if not page_id:
        busca = sc.get("/v1/facebook/adLibrary/search/companies", {"query": e["nome"]},
                       f"{e['slug']}__ads_busca")
        ig = (e.get("instagram") or "").lstrip("@").lower()
        for r in busca.get("searchResults") or []:
            if ig and (r.get("ig_username") or "").lower() == ig:
                page_id = r.get("page_id")
                break
        if not page_id:
            nomes = [f"{r.get('name')} (@{r.get('ig_username')}, id {r.get('page_id')})"
                     for r in (busca.get("searchResults") or [])[:5]]
            print(f"   ! Anúncios: página não identificada. Candidatos: {nomes or 'nenhum'}."
                  " Se achar a certa, ponha o id em meta_page_id no config.")
            return
    sc.get("/v1/facebook/adLibrary/company/ads",
           {"pageId": page_id, "country": pais, "status": "ALL", "start_date": desde},
           f"{e['slug']}__ads")


def _param_youtube(valor):
    v = valor.strip()
    if v.startswith("UC") and "/" not in v:
        return {"channelId": v}
    if v.startswith("http"):
        return {"url": v}
    return {"handle": v.lstrip("@")}


def coletar_youtube(sc, e):
    canal = sc.get("/v1/youtube/channel", _param_youtube(e["youtube"]), f"{e['slug']}__yt_canal")
    channel_id = canal.get("channelId")
    if not channel_id:
        print(f"   ! YouTube: canal não encontrado ({canal.get('erro') or canal.get('message')})")
        return
    sc.get("/v1/youtube/channel-videos", {"channelId": channel_id, "sort": "latest"},
           f"{e['slug']}__yt_videos")


# ---------- normalização ----------

def _int(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip().replace(",", "")
    m = re.match(r"([\d.]+)\s*([KkMm])", s)
    if m:
        return int(float(m.group(1)) * (1000 if m.group(2).lower() == "k" else 1_000_000))
    dig = re.sub(r"\D", "", s)
    return int(dig) if dig else None


def _data(ts):
    if isinstance(ts, (int, float)) and ts > 0:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    return str(ts)[:10] if ts else None


def _dias_relativos(texto):
    if not texto:
        return None
    m = re.search(r"(\d+|an?|one)\s+(second|minute|hour|day|week|month|year)", texto.lower())
    if not m:
        return None
    n = 1 if m.group(1) in ("a", "an", "one") else int(m.group(1))
    return n * {"second": 0, "minute": 0, "hour": 0, "day": 1, "week": 7,
                "month": 30, "year": 365}[m.group(2)]


def _falhou(d):
    return d is None or d.get("erro") or d.get("success") is False


def _post_ig(i):
    cap = i.get("caption")
    formato = "reels" if i.get("product_type") == "clips" else \
        {1: "foto", 2: "video", 8: "carrossel"}.get(i.get("media_type"), "outro")
    return {
        "code": i.get("code"),
        "url": f"https://www.instagram.com/p/{i.get('code')}/",
        "data": _data(i.get("taken_at")),
        "formato": formato,
        "curtidas": i.get("like_count") or 0,
        "comentarios": i.get("comment_count") or 0,
        "views": i.get("play_count") or i.get("ig_play_count"),
        "curtidas_ocultas": bool(i.get("like_and_view_counts_disabled")),
        "collab": [c.get("username") for c in (i.get("coauthor_producers") or []) if c.get("username")],
        "parceria_paga": bool(i.get("is_paid_partnership")),
        "fixado": bool(i.get("timeline_pinned_user_ids")),
        "legenda": cap.get("text", "") if isinstance(cap, dict) else "",
    }


def normalizar(raw, cfg, pasta):
    saida = {"data_coleta": raw.name.replace("raw-", ""), "cliente": cfg.get("cliente"),
             "janela_dias": cfg.get("janela_dias", 30), "entidades": {}}
    for e in cfg["entidades"]:
        s = e["slug"]
        ent = {"nome": e["nome"], "papel": e.get("papel", "concorrente"), "site": e.get("site")}

        def ler(nome):
            return ler_json(raw / f"{s}__{nome}.json")

        perfil = ler("ig_perfil")
        if e.get("instagram"):
            if _falhou(perfil):
                ent["instagram"] = {"handle": e["instagram"], "erro": "não coletado" if perfil is None
                                    else (perfil.get("erro") or perfil.get("message"))}
            else:
                u = (perfil.get("data") or {}).get("user") or {}
                posts = {}
                for f in sorted(raw.glob(f"{s}__ig_posts_p*.json")):
                    for i in (ler_json(f) or {}).get("items") or []:
                        posts[i.get("code")] = _post_ig(i)
                ent["instagram"] = {
                    "handle": e["instagram"],
                    "seguidores": (u.get("edge_followed_by") or {}).get("count"),
                    "seguindo": (u.get("edge_follow") or {}).get("count"),
                    "bio": u.get("biography"),
                    "links": [b.get("url") for b in (u.get("bio_links") or [])] or
                             ([u["external_url"]] if u.get("external_url") else []),
                    "verificado": u.get("is_verified"),
                    "posts": sorted(posts.values(), key=lambda p: p["data"] or "", reverse=True),
                }

        fb = ler("fb_perfil")
        if e.get("facebook"):
            if _falhou(fb):
                ent["facebook"] = {"erro": "não coletado" if fb is None else (fb.get("erro") or fb.get("message"))}
            else:
                status = ((fb.get("adLibrary") or {}).get("adStatus") or "").lower()
                ent["facebook"] = {
                    "seguidores": _int(fb.get("followerCount")),
                    "curtidas_pagina": _int(fb.get("likeCount")),
                    "falando_sobre": _int(fb.get("talkingAboutCount")),
                    "recomendacao": fb.get("rating"),
                    "categoria": fb.get("category"),
                    "anunciando_agora": ("currently running ads" in status and "isn't" not in status) if status else None,
                }

        ads, busca = ler("ads"), ler("ads_busca")
        if ads is not None and not _falhou(ads):
            res = ads.get("results") or []
            itens = []
            for a in res[:40]:
                snap = a.get("snapshot") or {}
                corpo = snap.get("body")
                texto = corpo.get("text", "") if isinstance(corpo, dict) else str(corpo or "")
                itens.append({"inicio": _data(a.get("start_date")), "fim": _data(a.get("end_date")),
                              "ativo": a.get("is_active"), "plataformas": a.get("publisher_platform"),
                              "formato": snap.get("display_format"), "texto": texto[:220]})
            ent["anuncios_meta"] = {"total": len(res), "total_informado": ads.get("searchResultsCount"),
                                    "ativos": sum(1 for a in res if a.get("is_active")), "itens": itens}
        elif busca is not None:
            ent["anuncios_meta"] = {"erro": "página não identificada na Biblioteca de Anúncios"}

        li, lp = ler("li_empresa"), ler("li_posts")
        if e.get("linkedin"):
            if _falhou(li):
                ent["linkedin"] = {"erro": "não coletado" if li is None else (li.get("erro") or li.get("message"))}
            else:
                datas = sorted([p.get("datePublished", "")[:10] for p in (lp or {}).get("posts") or []
                                if p.get("datePublished")], reverse=True)
                ent["linkedin"] = {"seguidores": _int(li.get("followers")),
                                   "funcionarios": _int(li.get("employeeCount")),
                                   "slogan": li.get("slogan"), "posts_datas": datas}

        yc, yv = ler("yt_canal"), ler("yt_videos")
        if e.get("youtube"):
            if _falhou(yc) or not yc.get("channelId"):
                ent["youtube"] = {"erro": "não coletado" if yc is None else (yc.get("erro") or yc.get("message") or "canal não encontrado")}
            else:
                recentes = [{"titulo": v.get("title"), "quando": v.get("publishedTimeText"),
                             "dias_aprox": _dias_relativos(v.get("publishedTimeText")),
                             "views": _int(v.get("viewCountInt") if v.get("viewCountInt") is not None else v.get("viewCountText"))}
                            for v in ((yv or {}).get("videos") or [])[:15]]
                ent["youtube"] = {"nome": yc.get("name"), "inscritos": _int(yc.get("subscriberCount")),
                                  "videos": _int(yc.get("videoCount")), "views_totais": _int(yc.get("viewCount")),
                                  "recentes": recentes}

        tt = ler("tt_perfil")
        if e.get("tiktok"):
            if tt and tt.get("user"):
                st = tt.get("stats") or tt.get("statsV2") or {}
                ent["tiktok"] = {"existe": True, "seguidores": _int(st.get("followerCount")),
                                 "videos": _int(st.get("videoCount")), "curtidas": _int(st.get("heartCount"))}
            elif tt and "exist" in str(tt.get("message", "")).lower():
                ent["tiktok"] = {"existe": False}
            else:
                ent["tiktok"] = {"erro": "não coletado" if tt is None else (tt.get("erro") or tt.get("message"))}

        saida["entidades"][s] = ent

    destino = pasta / "dados" / "coleta.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Consolidado: {destino}")
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta")
    ap.add_argument("--estimar", action="store_true", help="só mostra os créditos que a coleta vai gastar")
    ap.add_argument("--so-normalizar", action="store_true", help="refaz coleta.json a partir da pasta raw mais recente")
    ap.add_argument("--canais", default=",".join(CANAIS))
    ap.add_argument("--so", default="", help="slugs separados por vírgula")
    ap.add_argument("--paginas-ig", type=int, default=5, help="páginas de 12 posts por conta (padrão 5)")
    args = ap.parse_args()

    pasta = Path(args.pasta).expanduser().resolve()
    cfg = json.loads((pasta / "config.json").read_text(encoding="utf-8"))
    canais = [c.strip() for c in args.canais.split(",") if c.strip()]
    so = {s.strip() for s in args.so.split(",") if s.strip()}
    entidades = [e for e in cfg["entidades"] if not so or e["slug"] in so]
    dias = cfg.get("janela_dias", 30)

    if args.so_normalizar:
        raws = sorted((pasta / "dados").glob("raw-*"))
        if not raws:
            sys.exit("Nenhuma pasta dados/raw-* encontrada.")
        normalizar(raws[-1], cfg, pasta)
        return

    if args.estimar:
        total = 0
        for e in entidades:
            c = custo_estimado(e, canais, args.paginas_ig)
            total += c
            print(f"{e['nome']:<40} ~{c} créditos")
        print(f"{'TOTAL':<40} ~{total} créditos (canais: {', '.join(canais)})")
        return

    chave = carregar_chaves().get("SCRAPECREATORS_API_KEY")
    if not chave:
        sys.exit("SCRAPECREATORS_API_KEY não encontrada. Veja INSTALACAO.md na pasta da skill.")

    raw = pasta / "dados" / f"raw-{date.today().isoformat()}"
    sc = ScrapeCreators(chave, raw)
    desde = (date.today() - timedelta(days=max(dias, 90))).isoformat()

    for e in entidades:
        print(f"→ {e['nome']}")
        s = e["slug"]
        fb = None
        if "instagram" in canais and e.get("instagram"):
            coletar_instagram(sc, e, dias, args.paginas_ig)
        if "facebook" in canais and e.get("facebook"):
            fb = sc.get("/v1/facebook/profile", {"url": e["facebook"]}, f"{s}__fb_perfil")
        if "anuncios" in canais:
            coletar_anuncios(sc, e, fb or ler_json(raw / f"{s}__fb_perfil.json"), desde, cfg.get("pais", "BR"))
        if "linkedin" in canais and e.get("linkedin"):
            sc.get("/v1/linkedin/company", {"url": e["linkedin"]}, f"{s}__li_empresa")
            sc.get("/v1/linkedin/company/posts", {"url": e["linkedin"]}, f"{s}__li_posts")
        if "youtube" in canais and e.get("youtube"):
            coletar_youtube(sc, e)
        if "tiktok" in canais and e.get("tiktok"):
            tt = sc.get("/v1/tiktok/profile", {"handle": e["tiktok"].lstrip("@")}, f"{s}__tt_perfil")
            if not tt.get("user"):
                print(f"   ! TikTok @{e['tiktok']}: {tt.get('message') or tt.get('erro')}")

    print(f"\nChamadas: {sc.chamadas} | créditos restantes: {sc.creditos}")
    normalizar(raw, cfg, pasta)


if __name__ == "__main__":
    main()
