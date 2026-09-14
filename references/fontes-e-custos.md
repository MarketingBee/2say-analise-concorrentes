# Fontes, custos e limites conhecidos

Checado em set/2026 numa rodada real de 4 entidades em 6 canais. Header de autenticação: `x-api-key`. Base:
`https://api.scrapecreators.com`. Toda resposta traz `credits_remaining` (o endpoint
`/v1/credit/balance` da documentação dá 404).

## Endpoints usados pelo `coletar.py`

| Canal | Endpoint | Parâmetro | Crédito | Observação |
|---|---|---|---|---|
| Instagram perfil | `/v1/instagram/profile` | handle | 1 | Seguidores, bio, links da bio. O "count" de mídia não é o total de posts. |
| Instagram posts | `/v2/instagram/user/posts` | handle, next_max_id | 1 por página | 12 posts por página. Traz curtidas, comentários, views, formato, collab, legenda. |
| Facebook página | `/v1/facebook/profile` | url | 1 | Seguidores, "falando sobre", recomendação, e o `adLibrary.pageId` (usado para anúncios). |
| Anúncios Meta | `/v1/facebook/adLibrary/company/ads` | pageId, country, status, start_date | 1 | Funciona para anúncio comercial no Brasil (a API oficial da Meta não). Não mostra gasto. |
| Busca de página | `/v1/facebook/adLibrary/search/companies` | query | 1 | Só se não houver Facebook no config. Casa pelo `ig_username`. |
| LinkedIn empresa | `/v1/linkedin/company` | url | 1 | Seguidores, funcionários. |
| LinkedIn posts | `/v1/linkedin/company/posts` | url | 1 | Só data e texto, sem engajamento. |
| YouTube canal | `/v1/youtube/channel` | channelId, handle ou url | 1 | Inscritos, vídeos, views totais. |
| YouTube vídeos | `/v1/youtube/channel-videos` | channelId, sort=latest | 1 | Atenção: `/channel/videos` (com barra) dá 404. |
| TikTok perfil | `/v1/tiktok/profile` | handle | 1 | Conta inexistente responde "Account doesn't exist" e cobra 1 crédito. |

Não usados, mas disponíveis: comentários (`/v2/instagram/post/comments`), transcrição de
Reels (`/v2/instagram/media/transcript`), anúncios do Google (`/v1/google/company/ads`,
25 créditos com detalhes), anúncios do LinkedIn (`/v1/linkedin/ads/search`). A skill
`scrapecreators-api` tem a tabela completa.

## Estimativa por entidade

Instagram 1 + páginas (padrão 5) · Facebook 1 · anúncios 1 (2 sem Facebook) · LinkedIn 2 ·
YouTube 2 · TikTok 1. Com todos os canais: ~12 por entidade. Quatro entidades: ~50–60.

## Fora da ScrapeCreators

- **Google Maps:** nenhuma API grátis simples para avaliações. Caminho atual: navegador
  (extensão Claude in Chrome) ou a pessoa informa. Se um dia precisar de recência e taxa de
  resposta em escala, um coletor de avaliações do Google Maps (ex.: Apify) resolve.
- **PageSpeed Insights API:** grátis com chave própria (25 mil consultas/dia). Sem chave, a
  cota anônima estoura fácil (erro 429).
- **Lighthouse local:** `npx lighthouse` com Chrome instalado. O log de rede dele revela
  Pixel, RD Station e Analytics mesmo quando o site bloqueia leitura simples.
- **MCP do Chrome DevTools** (alternativa ao Lighthouse local, não configurada por padrão):
  se a pessoa já tiver esse MCP instalado, ele grava um trace de performance real do site
  (em vez do teste sintético do Lighthouse) e o Claude lê Core Web Vitals direto dali, sem
  passar pelo `sites.py`. Não resolve a dependência de Node/Chrome — só desloca ela do
  script para a configuração do MCP — então não é pré-requisito da skill, é só um caminho
  melhor para quem já tiver o MCP pronto.
- **API oficial da Meta (Business Discovery):** alternativa grátis para números de perfil e
  posts do Instagram de contas profissionais. Exige app na Meta; não foi necessária.

## Monitoramento contínuo

Para acompanhar cliente e concorrentes depois do Discovery (Conselho Estratégico), uma
ferramenta de monitoramento com histórico (Socialinsider, Rival IQ, Metricool) faz mais
sentido que coletas pontuais — nenhuma reconstrói histórico de seguidores, então cadastrar
cedo importa.
