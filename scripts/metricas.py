#!/usr/bin/env python3
"""Calcula as métricas comparativas a partir de dados/coleta.json.

Uso:
  python3 metricas.py <pasta> --legendas   # exporta as legendas da janela para classificar temas
  python3 metricas.py <pasta> [--inicio AAAA-MM-DD] [--fim AAAA-MM-DD]

Lê também, se existirem: <pasta>/temas.json, <pasta>/google.json, <pasta>/dados/sites.json.
Grava <pasta>/dados/metricas.md.
"""
import argparse
import json
import statistics as st
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sc import ler_json  # noqa: E402

ORDEM_PAPEL = {"cliente": 0, "concorrente": 1, "referencia": 2}
FORMATOS = ["reels", "carrossel", "foto", "video"]


def num(x, casas=0):
    if x is None:
        return "—"
    s = f"{x:,.{casas}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x, casas=2):
    return "—" if x is None else f"{num(x, casas)}%"


def tabela(cab, linhas):
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join(["---"] + ["---:"] * (len(cab) - 1)) + "|"]
    out += ["| " + " | ".join(str(c) for c in linha) + " |" for linha in linhas]
    return "\n".join(out)


def interacoes(p):
    return (p["curtidas"] or 0) + (p["comentarios"] or 0)


def janela_comum(ents, data_coleta, dias, inicio=None, fim=None):
    fim = date.fromisoformat(fim) if fim else data_coleta - timedelta(days=1)
    alvo = fim - timedelta(days=dias - 1)
    if inicio:
        return date.fromisoformat(inicio), fim, alvo, []
    limites = []
    for slug, ent in ents:
        posts = [p for p in (ent.get("instagram") or {}).get("posts", []) if not p["fixado"] and p["data"]]
        if posts:
            limites.append((date.fromisoformat(min(p["data"] for p in posts)), ent["nome"]))
    ini = max([alvo] + [d for d, _ in limites])
    avisos = [f"Janela encurtada: {nome} só tem posts coletados desde {d.isoformat()}. "
              f"Rode o coletar.py com --paginas-ig maior para cobrir {dias} dias."
              for d, nome in limites if d > alvo]
    return ini, fim, alvo, avisos


def stats_instagram(ent, ini, fim):
    ig = ent.get("instagram") or {}
    if not ig.get("posts") and not ig.get("seguidores"):
        return None
    seg = ig.get("seguidores") or 0
    ps = [p for p in ig.get("posts", []) if p["data"] and ini <= date.fromisoformat(p["data"]) <= fim]
    dias = (fim - ini).days + 1
    if not ps:
        return {"seguidores": seg, "n": 0, "posts": [], "dias": dias}
    eng = [interacoes(p) for p in ps]
    med = st.median(eng)
    reels = [p for p in ps if p["formato"] == "reels" and p["views"]]
    views = [p["views"] for p in reels]
    por_formato = {}
    for p, e in zip(ps, eng):
        por_formato.setdefault(p["formato"], []).append(e)
    curt = sum(p["curtidas"] for p in ps)
    return {
        "seguidores": seg, "n": len(ps), "posts": ps, "dias": dias,
        "por_semana": len(ps) / dias * 7,
        "dias_com_post": len({p["data"] for p in ps}),
        "mix": {f: sum(1 for p in ps if p["formato"] == f) / len(ps) * 100 for f in FORMATOS},
        "int_mediana": med,
        "eng_mediano": st.median([e / seg * 100 for e in eng]) if seg else None,
        "coment_mediano": st.median([p["comentarios"] for p in ps]),
        "coment_por_curtida": sum(p["comentarios"] for p in ps) / curt if curt else None,
        "views_mediana": st.median(views) if views else None,
        "views_pct": st.median(views) / seg * 100 if views and seg else None,
        "reels_acima_seguidores": sum(1 for v in views if seg and v > seg),
        "collabs": sum(1 for p in ps if p["collab"]),
        "parceria_paga": sum(1 for p in ps if p["parceria_paga"]),
        "ocultos": sum(1 for p in ps if p["curtidas_ocultas"]),
        "total_int": sum(eng),
        "formato_mediana": {f: (st.median(v), len(v)) for f, v in por_formato.items()},
        "fora_da_curva": sorted([(e, p) for p, e in zip(ps, eng) if med and e >= 3 * med],
                                key=lambda x: -x[0]),
    }


def exportar_legendas(pasta, ents, ini, fim):
    destino = pasta / "dados" / "legendas_para_classificar.tsv"
    linhas = ["code\tentidade\tdata\tformato\tinteracoes\tlegenda"]
    for slug, ent in ents:
        for p in (ent.get("instagram") or {}).get("posts", []):
            if p["data"] and ini <= date.fromisoformat(p["data"]) <= fim:
                leg = " ".join(p["legenda"].split())[:300]
                linhas.append(f"{p['code']}\t{slug}\t{p['data']}\t{p['formato']}\t{interacoes(p)}\t{leg}")
    destino.write_text("\n".join(linhas), encoding="utf-8")
    print(f"{len(linhas) - 1} posts na janela {ini} a {fim} → {destino}")
    print("Classifique cada code em temas.json: {\"categorias\": {...}, \"posts\": {\"<code>\": \"<sigla>\"}}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta")
    ap.add_argument("--legendas", action="store_true")
    ap.add_argument("--inicio")
    ap.add_argument("--fim")
    args = ap.parse_args()

    pasta = Path(args.pasta).expanduser().resolve()
    coleta = ler_json(pasta / "dados" / "coleta.json")
    if not coleta:
        sys.exit("dados/coleta.json não encontrado — rode o coletar.py antes.")
    ents = sorted(coleta["entidades"].items(), key=lambda kv: ORDEM_PAPEL.get(kv[1]["papel"], 9))
    data_coleta = date.fromisoformat(coleta["data_coleta"])
    ini, fim, alvo, avisos = janela_comum(ents, data_coleta, coleta.get("janela_dias", 30), args.inicio, args.fim)

    if args.legendas:
        for a in avisos:
            print("! " + a)
        exportar_legendas(pasta, ents, ini, fim)
        return

    temas = ler_json(pasta / "temas.json")
    google = ler_json(pasta / "google.json") or {}
    sites = ler_json(pasta / "dados" / "sites.json") or {}
    S = {slug: stats_instagram(ent, ini, fim) for slug, ent in ents}
    nomes = [ent["nome"] + (" (cliente)" if ent["papel"] == "cliente" else "") for _, ent in ents]
    md = [f"# Métricas comparativas — coleta de {coleta['data_coleta']}", "",
          f"Janela comum do Instagram: **{ini.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}** "
          f"({(fim - ini).days + 1} dias).", ""]

    # ---------- painel multicanal ----------
    def linha_painel(rotulo, func):
        return [rotulo] + [func(slug, ent) for slug, ent in ents]

    def ig_cel(slug, ent):
        s = S[slug]
        if not s:
            return "sem conta" if not ent.get("instagram") else f"erro: {ent['instagram'].get('erro')}"
        return f"{num(s['seguidores'])} · {num(s.get('por_semana'), 1)}/sem · {pct(s.get('eng_mediano'))}"

    def fb_cel(slug, ent):
        f = ent.get("facebook")
        if not f:
            return "sem página"
        if f.get("erro"):
            return f"erro: {f['erro']}"
        return f"{num(f['seguidores'])} · {f.get('recomendacao') or 'sem recomendação'}"

    def li_cel(slug, ent):
        li = ent.get("linkedin")
        if not li:
            return "sem página"
        if li.get("erro"):
            return f"erro: {li['erro']}"
        na_janela = sum(1 for d in li["posts_datas"] if d and ini.isoformat() <= d <= fim.isoformat())
        ultimo = li["posts_datas"][0] if li["posts_datas"] else "nenhum visível"
        return f"{num(li['seguidores'])} · {na_janela} posts na janela · último {ultimo}"

    def yt_cel(slug, ent):
        y = ent.get("youtube")
        if not y:
            return "sem canal"
        if y.get("erro"):
            return f"erro: {y['erro']}"
        rec = y["recentes"]
        vs = [v["views"] for v in rec[:5] if v["views"] is not None]
        faixa = f"{num(min(vs))}–{num(max(vs))} views (5 últimos)" if vs else ""
        return f"{num(y['inscritos'])} inscritos · último {rec[0]['quando'] if rec else '—'} · {faixa}"

    def tt_cel(slug, ent):
        t = ent.get("tiktok")
        if not t or t.get("existe") is False:
            return "sem conta"
        if t.get("erro"):
            return f"erro: {t['erro']}"
        return f"{num(t['seguidores'])} seguidores · {num(t['videos'])} vídeos"

    def ads_cel(slug, ent):
        a = ent.get("anuncios_meta")
        if not a:
            return "não coletado"
        if a.get("erro"):
            return a["erro"]
        return f"{a['total']} ({a['ativos']} ativos)"

    def g_cel(slug, ent):
        g = google.get(slug)
        return f"{num(g.get('nota'), 1)} · {num(g.get('avaliacoes'))}" if g else "—"

    def site_cel(slug, ent):
        s = sites.get(slug)
        if not s:
            return "—"
        d = (s.get("desempenho") or {}).get("desempenho")
        return f"desempenho {d if d is not None else '—'} · {len(s.get('tecnologias', []))} ferramentas"

    md += ["## Painel multicanal", "", tabela(["Canal"] + nomes, [
        linha_painel("Instagram (seguidores · posts/semana · engajamento mediano)", ig_cel),
        linha_painel("Facebook (seguidores · recomendação)", fb_cel),
        linha_painel("LinkedIn", li_cel),
        linha_painel("YouTube", yt_cel),
        linha_painel("TikTok", tt_cel),
        linha_painel("Anúncios Meta (últimos 90 dias)", ads_cel),
        linha_painel("Google (nota · avaliações)", g_cel),
        linha_painel("Site", site_cel),
    ]), ""]

    # ---------- instagram ----------
    validos = [(slug, ent) for slug, ent in ents if S[slug] and S[slug]["n"]]
    total_grupo = sum(S[s]["total_int"] for s, _ in validos) or 1
    if validos:
        col = [ent["nome"] for _, ent in validos]

        def lin(rotulo, f):
            return [rotulo] + [f(S[s]) for s, _ in validos]

        md += ["## Instagram — retrato na janela", "", tabela([""] + col, [
            lin("Seguidores", lambda s: num(s["seguidores"])),
            lin("Posts na janela", lambda s: num(s["n"])),
            lin("Posts por semana", lambda s: num(s["por_semana"], 1)),
            lin("Dias com post", lambda s: f"{s['dias_com_post']} de {s['dias']}"),
            lin("Mix (Reels / carrossel / foto / vídeo)", lambda s: " / ".join(f"{s['mix'][f]:.0f}%" for f in FORMATOS)),
            lin("Interações medianas por post", lambda s: num(s["int_mediana"])),
            lin("Engajamento mediano (% seguidores)", lambda s: pct(s["eng_mediano"])),
            lin("Comentário mediano por post", lambda s: num(s["coment_mediano"])),
            lin("Comentários por curtida", lambda s: num(s["coment_por_curtida"], 3)),
            lin("Views medianas de Reels (% seguidores)", lambda s: f"{num(s['views_mediana'])} ({pct(s['views_pct'], 0)})" if s["views_mediana"] else "—"),
            lin("Reels com views acima dos seguidores", lambda s: num(s["reels_acima_seguidores"])),
            lin("Posts em collab", lambda s: f"{s['collabs']} de {s['n']}"),
            lin("Posts com curtidas ocultas", lambda s: num(s["ocultos"])),
            lin("Fatia do engajamento do grupo", lambda s: pct(s["total_int"] / total_grupo * 100, 0)),
        ]), ""]

        formatos_usados = [f for f in FORMATOS if any(f in S[s]["formato_mediana"] for s, _ in validos)]
        md += ["## Instagram — interações medianas por formato", "", tabela(["Formato"] + col, [
            [f] + [f"{num(S[s]['formato_mediana'][f][0])} (n={S[s]['formato_mediana'][f][1]})"
                   if f in S[s]["formato_mediana"] else "—" for s, _ in validos] for f in formatos_usados
        ]), ""]

        if temas:
            cats, tags = temas.get("categorias", {}), temas.get("posts", {})
            na_janela = [p["code"] for s, _ in validos for p in S[s]["posts"]]
            sem_tema = [c for c in na_janela if c not in tags]
            desconhecidas = sorted({t for t in tags.values() if t not in cats})
            if sem_tema:
                avisos.append(f"{len(sem_tema)} posts da janela sem tema em temas.json (ex.: {', '.join(sem_tema[:5])}).")
            if desconhecidas:
                avisos.append(f"Siglas de tema sem categoria definida: {', '.join(desconhecidas)}.")
            linhas = []
            for sigla, nome in cats.items():
                linha = [nome]
                for s, _ in validos:
                    ps = S[s]["posts"]
                    grupo = [interacoes(p) for p in ps if tags.get(p["code"]) == sigla]
                    if not grupo:
                        linha.append("—")
                        continue
                    share = len(grupo) / len(ps) * 100
                    rend = st.median(grupo) / S[s]["int_mediana"] if S[s]["int_mediana"] and len(grupo) >= 2 else None
                    linha.append(f"{share:.0f}% · {num(rend, 1) + 'x' if rend is not None else 'n<2'}")
                linhas.append(linha)
            md += ["## Instagram — temas (% do feed · rendimento vs. mediana da conta)", "",
                   tabela(["Tema"] + col, linhas), "",
                   "Rendimento = mediana de interações do tema ÷ mediana da conta. Só calculado com 2 posts ou mais.", ""]

        md += ["## Instagram — posts fora da curva (3x ou mais a mediana da conta)", ""]
        for s, ent in validos:
            fc = S[s]["fora_da_curva"]
            md.append(f"**{ent['nome']}** — {len(fc)} posts")
            for e, p in fc[:5]:
                extra = []
                if p["views"]:
                    extra.append(f"{num(p['views'])} views")
                if p["collab"]:
                    extra.append("collab com @" + ", @".join(p["collab"]))
                leg = " ".join(p["legenda"].split())[:110]
                md.append(f"- {num(e)} interações · {p['data']} · {p['formato']}"
                          f"{' · ' + ' · '.join(extra) if extra else ''} · [{p['code']}]({p['url']}) — {leg}")
            md.append("")

    # ---------- anúncios ----------
    md += ["## Anúncios na Meta (últimos 90 dias)", ""]
    for s, ent in ents:
        a = ent.get("anuncios_meta")
        if not a or a.get("erro"):
            md.append(f"- **{ent['nome']}**: {a['erro'] if a else 'não coletado'}")
            continue
        md.append(f"- **{ent['nome']}**: {a['total']} anúncios ({a['ativos']} ativos)")
        for it in a["itens"][:8]:
            md.append(f"  - {it['inicio']} → {it['fim']} · {'ativo' if it['ativo'] else 'encerrado'} · "
                      f"{it['formato']} · {', '.join(it['plataformas'] or [])} · {' '.join(it['texto'].split())[:120]}")
    md.append("")

    # ---------- site ----------
    if sites:
        col = [ent["nome"] for s, ent in ents if s in sites]
        so = [s for s, _ in ents if s in sites]

        def d(s, k):
            return (sites[s].get("desempenho") or {}).get(k)

        md += ["## Site", "", tabela([""] + col, [
            ["Desempenho no celular (0–100)"] + [d(s, "desempenho") if d(s, "desempenho") is not None else "—" for s in so],
            ["SEO"] + [d(s, "seo") if d(s, "seo") is not None else "—" for s in so],
            ["Acessibilidade"] + [d(s, "acessibilidade") if d(s, "acessibilidade") is not None else "—" for s in so],
            ["Conteúdo principal aparece em (LCP)"] + [d(s, "lcp") or "—" for s in so],
            ["Estabilidade do layout (CLS)"] + [d(s, "cls") or "—" for s in so],
            ["Peso da página (MB)"] + [num(d(s, "peso_mb"), 1) for s in so],
            ["Fonte da medição"] + [d(s, "fonte") or (sites[s].get("desempenho") or {}).get("erro") or "—" for s in so],
            ["Ferramentas"] + [", ".join(sites[s].get("tecnologias", [])) or "nenhuma detectada" for s in so],
            ["Chamadas para ação"] + [", ".join(sites[s].get("ctas", [])[:5]) or "—" for s in so],
            ["Manchete (h1)"] + [" / ".join(sites[s].get("h1", [])) or "—" for s in so],
            ["Conteúdo datado mais recente na home"] + [sites[s].get("data_mais_recente") or "—" for s in so],
            ["Leitura automática"] + ["ok" if sites[s].get("status") == 200 else f"HTTP {sites[s].get('status')}" for s in so],
        ]), ""]

    # ---------- google ----------
    if google:
        md += ["## Google Maps", ""]
        for s, ent in ents:
            g = google.get(s)
            if not g:
                continue
            temas_g = ", ".join(f"{k} ({v})" for k, v in (g.get("temas") or {}).items())
            md.append(f"- **{ent['nome']}**: {num(g.get('nota'), 1)} · {num(g.get('avaliacoes'))} avaliações"
                      f"{' · perfil: ' + g['perfil'] if g.get('perfil') else ''}"
                      f"{' · temas: ' + temas_g if temas_g else ''}"
                      f"{' · responde: ' + g['responde'] if g.get('responde') else ''}"
                      f"{' · ' + g['observacao'] if g.get('observacao') else ''}")
        md.append("")

    # ---------- avisos ----------
    for s, _ in validos if S else []:
        if S[s]["n"] < 10:
            avisos.append(f"{coleta['entidades'][s]['nome']} tem só {S[s]['n']} posts na janela — medianas frágeis.")
    if avisos:
        md += ["## Avisos", ""] + [f"- {a}" for a in avisos] + [""]

    destino = pasta / "dados" / "metricas.md"
    destino.write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md[:4]))
    for a in avisos:
        print("! " + a)
    print(f"\nGravado: {destino}")


if __name__ == "__main__":
    main()
