# Métricas e leitura

## Definições (o que o `metricas.py` calcula)

| Métrica | Conta | Por que assim |
|---|---|---|
| Interações por post | curtidas + comentários | O que é público para qualquer conta. Salvamento e compartilhamento só o dono vê. |
| Engajamento mediano | mediana de (interações ÷ seguidores) | Mediana e não média: um post viral puxa a média para cima e esconde o post típico. |
| Posts por semana / dias com post | posts na janela ÷ dias × 7 | Volume e regularidade são coisas diferentes. |
| Mix de formato | % de Reels, carrossel, foto, vídeo | — |
| Rendimento (por formato ou tema) | mediana do grupo ÷ mediana da própria conta | Compara a conta com ela mesma. É a forma justa de comparar contas de tamanhos diferentes. 2,4x = o tema rende 2,4 vezes o post típico daquela conta. |
| Fatia do engajamento | interações da conta ÷ soma de todas na janela | Quem "ocupa" a conversa do grupo, em volume absoluto. |
| Views de Reels ÷ seguidores | mediana de views dos Reels ÷ seguidores | Se o conteúdo sai da base. Acima de 100% = chegou em quem não segue. |
| Comentários por curtida | soma de comentários ÷ soma de curtidas | Conteúdo que gera conversa × conteúdo que só recebe like. |
| Fora da curva | post com 3 vezes ou mais a mediana da conta | Onde a conta acertou. É o material mais útil para o diagnóstico. |

## Armadilhas que já apareceram

- **Conta pequena tem engajamento % maior por natureza.** No caso ACIC, a DEATEC (4,7 mil
  seguidores) tinha 0,67% contra 0,14% da ACIC (14,8 mil). Não quer dizer que se comunica
  melhor. Use fatia do engajamento e rendimento por tema para comparar.
- **Views altas com interação baixa = anúncio.** O Reel da CDL teve 124 mil views e 13
  interações — o mesmo criativo estava rodando como anúncio. Sempre cruze outliers de views
  com a Biblioteca de Anúncios antes de chamar de "sucesso orgânico".
- **Collab soma o público do parceiro.** O maior post da ACIC era uma collab. Registre
  quantos posts de cada conta são collab e diga isso ao citar um outlier.
- **Período atípico distorce tema.** Eleição, evento grande, campanha sazonal. Na ACIF,
  a campanha eleitoral inflava "pauta da cidade". Pergunte no briefing e cite no relatório.
- **Curtidas ocultas.** Conta que esconde curtidas entra com comentários e views; o script
  conta quantos posts vieram assim.
- **Janela curta para quem posta pouco.** Com menos de ~10 posts na janela, mediana e
  rendimento ficam frágeis. Aumente `janela_dias` ou diga que o número é indicativo.
- **Facebook:** reações de post recente vêm zeradas pela API — não use como engajamento.
  Seguidores, "falando sobre" e recomendação são confiáveis.
- **LinkedIn:** a API não traz engajamento dos posts; use só frequência e data do último.
- **Google:** o perfil do Maps pode ser do prédio, de uma regional ou de um espaço de
  eventos com nome próprio. Diga qual foi usado; some perfis só se fizer sentido.
- **Site:** Lighthouse/PageSpeed é teste de laboratório e varia alguns pontos por rodada.
  Compare ordens de grandeza (32 × 56), não diferenças de 3 pontos.
- **Dado privado do cliente não entra na comparação.** Os concorrentes não teriam o
  equivalente — vira comparação desigual.

## Padrões de leitura que renderam achados

1. **Declarado × percebido × entregue.** A ACIC dizia ser "a voz dos empreendedores"; o
   Google dizia "estrutura, cursos, estacionamento"; o feed tinha 29% de promoção de curso.
   A distância entre os três virou o achado central.
2. **Tema que rende, que o cliente publica pouco e que ninguém ocupa.** Pauta da cidade
   rendia 2,4x na ACIC, ocupava 12% do feed, e nenhum concorrente de Chapecó publicava.
3. **Produção sem distribuição.** Podcast no YouTube com 3–56 views por episódio enquanto
   Reels da mesma conta rendiam mais — sugestão: cortar episódios em Reels.
4. **Mídia sem medição.** Cliente anunciando na Meta com site sem Pixel nem automação.
5. **Botão sem funil.** Todo mundo tem "associe-se" no site; só quem junta anúncio +
   formulário de automação + chat está de fato captando.
6. **Canal marcado como ativo que está parado.** Confira a data do último post antes de
   dar ✓ no slide de canais.
7. **Reputação sem resposta.** Maior volume de avaliações da praça e nenhuma resposta às
   avaliações em destaque — ajuste barato e visível.
8. **Correção do diagnóstico anterior.** Se já existe uma versão qualitativa (deck), os
   números podem confirmar ou desmentir. No caso ACIC, desmentiram "nenhum concorrente
   busca novos associados" (a ACIF fazia por anúncio). Registre as correções.
