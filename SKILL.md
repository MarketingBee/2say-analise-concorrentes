---
name: analise-concorrentes-discovery
description: >
  Faz a Análise de Concorrentes do Discovery da 2SAY de ponta a ponta: briefing do cliente
  e dos concorrentes, mapa de canais, coleta de métricas públicas (Instagram, Facebook,
  LinkedIn, YouTube, TikTok e Biblioteca de Anúncios da Meta via ScrapeCreators; avaliações
  do Google Maps; site com PageSpeed/Lighthouse e tecnologias instaladas), comparação na
  mesma régua, classificação dos temas do conteúdo, diagnóstico de posicionamento e mapa de
  gaps e oportunidades para o cliente. Use sempre que alguém da 2SAY pedir análise de
  concorrentes, benchmark de redes ou site, "comparar o cliente com os concorrentes", "como
  o cliente está frente ao mercado", a etapa 4 do Discovery, ou quiser montar/atualizar os
  slides de concorrentes do deck — mesmo sem citar Discovery nem ScrapeCreators. Não
  confundir com `competitor-social-research` (genérica, só redes sociais, sem briefing nem
  formato 2SAY).
---

# Análise de Concorrentes — Discovery 2SAY

## Para que serve

A Análise de Concorrentes é a etapa 4 do Discovery e aparece em todos os Discoverys
(template fixo, documentado na metodologia interna da 2SAY: principais concorrentes,
posicionamento, proposta de valor, mote, canais, o que comunicam, diagnóstico e brechas).
Até set/2026 ela era só qualitativa — o único dado "numérico" do deck era ✓/✗ de presença
por canal. O Andrey pediu a camada de métricas: comparar cliente e concorrentes com o
máximo de dado público, para que a brecha apontada no diagnóstico venha com evidência, não
só com leitura.

Esta skill junta as duas camadas. O primeiro caso completo foi uma associação empresarial
regional (site institucional + Instagram/Facebook/LinkedIn/YouTube/TikTok ativos, 3
concorrentes de porte parecido) — deu o formato de relatório e os padrões de leitura que
estão em `references/metricas-e-leitura.md`. Se você trabalha no vault interno da 2SAY,
peça pra alguém do time o caminho do relatório real; ele não está neste repositório porque
é entrega de cliente.

**Referências ao vault interno:** algumas partes desta skill citam docs que só existem no
vault "Segundo Cérebro Coonecta" da 2SAY (a metodologia do Discovery, o guia de escrita
anti-IA). Se você estiver usando esta skill fora desse vault, ela funciona normalmente sem
eles — são só enriquecimento de tom e contexto, não dependência técnica.

## Antes de começar

1. Rode `python3 "<pasta-da-skill>/scripts/checar.py"`. Ele detecta a raiz do projeto
   *desta instalação* (a pasta que contém o `.claude/` daqui — não presume "2SAY" nem
   nenhum outro nome) e diz se a chave está no `.env` dessa raiz, se tem Python/Node e se
   dá para medir o site. No Windows, troque `python3` por `python` (ou `py`).
   Cada cópia da skill, em cada pasta de projeto diferente, tem seu próprio `.env` — quem
   copiar esta skill para o próprio vault não herda a chave de ninguém, precisa da sua.
   Se faltar a chave da ScrapeCreators, **peça o valor à pessoa ali no chat** e grave com
   `python3 scripts/configurar.py --set SCRAPECREATORS_API_KEY=<chave>` — não peça para
   ela editar arquivo oculto na mão; veja `INSTALACAO.md` para o passo a passo completo.
2. A pasta de trabalho é `2SAY/Clientes/<Cliente>/Análise de Concorrentes/`. Tudo fica ali:
   `briefing.md`, `config.json`, `temas.json`, `google.json`, `dados/` e o relatório.
   Guardar os dados crus junto é o que permite refazer a conta ou atualizar daqui a meses
   sem gastar crédito de novo.
3. Leia o que o vault já tem do cliente antes de perguntar: `2SAY/Clientes/<Cliente>.md`,
   notas do Discovery, transcrições de reunião. O briefing só pergunta o que faltar.

## Fluxo

### 1. Briefing

Use o modelo de `references/briefing.md` e salve preenchido como `briefing.md` na pasta de
trabalho. O essencial: quem é o cliente e o que ele quer do Discovery, 3 a 5 concorrentes
(com o motivo de cada um estar na lista — direto, indireto ou referência de outra praça),
posicionamento declarado do cliente, público e perguntas específicas dos sócios. Se a
pessoa não souber os concorrentes, proponha uma lista (busca no Google/Maps da região +
concorrentes citados em reunião) e confirme antes de coletar.

### 2. Mapa de canais → `config.json`

Monte o `config.json` com uma entrada por entidade. Para achar os canais:
`python3 scripts/sites.py <pasta> --descobrir` lê o site de cada entidade e lista as redes
linkadas; complete com os links da bio do Instagram (saem na coleta) e busca na web.
Canal que não existe fica `null` — ausência também é achado.

```json
{
  "cliente": "ACIC Chapecó",
  "janela_dias": 30,
  "pais": "BR",
  "entidades": [
    {
      "slug": "acic", "nome": "ACIC Chapecó", "papel": "cliente",
      "site": "https://acichapeco.com.br",
      "instagram": "acichapeco",
      "facebook": "https://www.facebook.com/acic.chapeco",
      "linkedin": "https://www.linkedin.com/company/acic-associacao-comercial-e-industrial-de-chapeco",
      "youtube": "UCdQaLsfZQPZsQQB-D_vemKQ",
      "tiktok": null,
      "meta_page_id": null,
      "google_maps": "ACIC Associação Comercial Industrial Chapecó"
    }
  ]
}
```

`papel` é `cliente`, `concorrente` ou `referencia` (alguém de outra praça que serve de
modelo, como a ACIF de Florianópolis no caso ACIC). `youtube` aceita ID do canal (`UC...`),
@handle ou URL. `meta_page_id` é opcional — o script descobre pela página do Facebook.

`janela_dias`: 30 funciona para quem posta quase todo dia. Se o segmento posta pouco
(2–3 vezes por semana), use 60 ou 90, senão cada conta fica com poucos posts para comparar.

Mostre à pessoa a lista de entidades e canais e rode `python3 scripts/coletar.py <pasta>
--estimar` para mostrar quantos créditos a coleta vai gastar. Confirme antes de coletar —
créditos são da conta da empresa.

### 3. Coleta

- **Redes e anúncios:** `python3 scripts/coletar.py <pasta>` (opções: `--canais`,
  `--so slug1,slug2`, `--paginas-ig N`). Grava cru em `dados/raw-AAAA-MM-DD/` e
  consolidado em `dados/coleta.json`. Leia os avisos que ele imprime (conta inexistente,
  página de anúncios não identificada).
- **Site:** `python3 scripts/sites.py <pasta>`. Tecnologias (Analytics, Pixel, RD, chat),
  chamadas para ação, data do conteúdo mais recente e desempenho no celular. Grava
  `dados/sites.json`. Site que bloqueia leitura automática aparece como 403 — abra no
  navegador (extensão Claude in Chrome) e anote à mão o que faltar.
- **Google Maps:** a ScrapeCreators não cobre avaliações. Com a extensão do Chrome, abra
  `https://www.google.com/maps/search/<termo>` para cada entidade e use `get_page_text`:
  saem nota, total, os temas que o Google agrupa ("estrutura 11", "cursos 8") e as
  avaliações em destaque (veja se o dono responde). Sem a extensão, peça à pessoa nota e
  total. Salve em `google.json`:

```json
{
  "acic": {"nota": 4.7, "avaliacoes": 275, "perfil": "sede",
           "temas": {"estrutura": 11, "cursos": 8, "estacionamento": 8},
           "responde": "não, nas avaliações em destaque",
           "observacao": "elogios à estrutura; crítica a equipamento antigo"}
}
```

  Se a entidade tiver mais de um perfil (sede, regional, prédio), registre qual foi usado.
  Ordenar por "Mais recentes" não funcionou pela automação — não insista; recência e taxa
  de resposta ficam como amostra.

### 4. Temas do conteúdo

É a parte que transforma "o que comunicam" em número. Rode
`python3 scripts/metricas.py <pasta> --legendas` para exportar as legendas da janela em
`dados/legendas_para_classificar.tsv`.

Defina de 5 a 8 categorias que façam sentido para o segmento — mutuamente exclusivas,
nomeadas pelo assunto do post, não pelo formato. Para associações empresariais, as que
funcionaram: promoção de evento/curso, cobertura de evento, pauta da cidade/região,
educativo, institucional/data comemorativa, comercial (patrocinador, produto, varejo),
associativismo. Para outro segmento, adapte (ex.: produto, bastidor, cliente/case,
educativo, oferta, institucional). Leia as legendas e classifique cada post pelo `code`:

```json
{
  "categorias": {"P": "Promoção de evento/curso", "A": "Pauta da cidade/região"},
  "posts": {"DcRNafVx4og": "A", "Db6_iWiSD74": "P"}
}
```

Classifique por `code`, nunca por posição na lista: na primeira vez isso foi feito por
ordem e quatro posts desalinharam sem ninguém perceber. O `metricas.py` avisa se sobrar
post sem tema. Diga no relatório que a classificação é sua e precisa de revisão humana.

### 5. Métricas

`python3 scripts/metricas.py <pasta>` gera `dados/metricas.md` com painel multicanal,
retrato do Instagram na janela comum, desempenho por formato e por tema, posts fora da
curva, anúncios, Google e site. A janela é a mesma para todas as contas — o script encurta
e avisa se alguma conta não tiver posts suficientes coletados.

Antes de interpretar, leia `references/metricas-e-leitura.md`: lá estão as definições e as
armadilhas que já apareceram (conta pequena com engajamento inflado, views de anúncio
parecendo alcance orgânico, collab somando público do parceiro).

### 6. Posicionamento — os 7 itens do Discovery

Preencha para cada entidade, a partir de bio, título e manchete do site, legendas e texto
dos anúncios:

1. Principais concorrentes (quem, de onde, por que está na lista)
2. Posicionamento — que lugar tenta ocupar
3. Proposta de valor — o principal benefício prometido
4. Mote/conceito — slogan ou frase-chave (se não existe, diga "não fica claro")
5. Canais — agora com número (ativo, parado, inexistente)
6. O que comunicam — agora com a % por tema
7. Diagnóstico geral do mercado

Separe o **declarado** (o que a marca diz de si) do **percebido** (avaliações do Google,
comentários) e do **entregue** (o que o feed de fato publica). A distância entre os três é
onde mora a maior parte dos achados.

### 7. Gaps e oportunidades

O cruzamento que mais rendeu no caso ACIC:

- **Território:** que tema rende acima da mediana para o cliente e quanto do feed dele ocupa?
  Que tema nenhum concorrente da praça ocupa? Tema que rende, que o cliente pouco publica e
  que ninguém ocupa é a oportunidade mais forte — ainda mais se casar com o posicionamento
  declarado.
- **Canal:** canal inativo, inexistente ou com produção sem audiência (YouTube com 3 views
  por episódio → cortar em Reels).
- **Medição e mídia:** anuncia sem Pixel/automação no site? Concorrente usa mídia paga para
  captar (cliente, associado) e o cliente não?
- **Reputação:** nota, volume e se responde avaliação; o que as avaliações dizem que o
  cliente é, comparado ao que ele diz ser.
- **Funil:** o site tem chamada clara para a conversão que importa, e o que vem depois dela?

Cada oportunidade precisa de evidência numérica e de uma sugestão testável. Priorize por
impacto × esforço e marque o que é fato e o que é inferência ("parece", "sugere").

### 8. Relatório

Siga `references/relatorio-modelo.md`. Salve na pasta de trabalho como
`AAAA-MM-DD - Análise de Concorrentes <Cliente>.md`. Revele o arquivo no explorador de
arquivos do sistema — no Mac, `open -R <arquivo>`; no Windows, `explorer /select,<arquivo>`.
Ofereça em seguida transformar em slides no formato do deck do Discovery.

Escreva como pessoa, não como relatório de IA — as regras de escrita do vault
(`CLAUDE.md` e `2SAY/Estratégia/2SAY - Escrita Humana (Anti-IA).md`) valem aqui também.

## Custos

Uma análise típica (cliente + 3 concorrentes, 6 canais) gasta perto de 60 créditos da
ScrapeCreators — centavos de dólar no pacote de US$ 47 / 25 mil créditos. Google, site e
cálculo não gastam nada. O saldo aparece ao fim de cada coleta; registre no relatório.

## Arquivos da skill

- `INSTALACAO.md` — chaves de API e pré-requisitos, passo a passo para quem vai usar.
- `references/briefing.md` — modelo de briefing.
- `references/metricas-e-leitura.md` — definições, armadilhas e padrões de leitura.
- `references/relatorio-modelo.md` — estrutura do relatório.
- `references/fontes-e-custos.md` — endpoints, custo por chamada, limites conhecidos.
- `scripts/checar.py` · `coletar.py` · `sites.py` · `metricas.py` — Python puro, sem
  instalar pacote. `sc.py` é o cliente compartilhado da API e a lógica de onde fica o
  `.env` de cada instalação. `configurar.py` cria ou atualiza esse `.env`.
