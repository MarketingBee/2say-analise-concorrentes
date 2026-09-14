# Modelo do relatório

Arquivo: `2SAY/Clientes/<Cliente>/Análise de Concorrentes/AAAA-MM-DD - Análise de Concorrentes <Cliente>.md`.
É documento interno da 2SAY — a base do que depois vira slide para o cliente. Números
vêm do `dados/metricas.md`; copie as tabelas e escreva a leitura em volta delas.

```markdown
---
tags: [2say, discovery, analise-concorrentes, <cliente>]
created: AAAA-MM-DD
fonte: ScrapeCreators, Google Maps, PageSpeed/Lighthouse, leitura dos sites
---

# Análise de Concorrentes — <Cliente>

Uma frase de contexto: para que é (etapa do Discovery), quem entrou, janela, data da coleta.
Link para o briefing.

## Resumo
3 a 5 achados, cada um com o número que o sustenta. Depois, as 3 oportunidades mais fortes
em uma linha cada. Quem só ler esta seção precisa sair sabendo o que fazer.

## Painel multicanal
(tabela do metricas.md)

## Instagram
### Retrato na janela comum
### Formato
### Temas — o que cada um comunica e o que rende
### Posts fora da curva

## Mídia paga
Quem anuncia, quantos anúncios, com qual mensagem. Cruze com outliers de views.

## Google — reputação
Nota, volume, temas das avaliações, se responde. O que as avaliações dizem que a empresa é.

## Site
Desempenho, medição/automação instalada, chamada para ação, o que a home destaca.

## Posicionamento (os 7 itens do Discovery)
Tabela ou blocos por entidade: posicionamento, proposta de valor, mote, canais, o que
comunicam, e o diagnóstico geral do mercado. Separe declarado × percebido × entregue.

## Gaps e oportunidades
| Oportunidade | Evidência (número) | O que testar | Impacto | Esforço |
|---|---|---|---|---|

## Correções ao que já existia
Se havia versão qualitativa anterior (deck), o que os números confirmam e o que corrigem.

## Pro deck
Que número entra em que slide: Canais (trocar ✓ por seguidores + último post), Desempenho
por canal, O que comunicam (% por tema), Mídia paga, Reputação, Site, Brechas.

## Limitações
Janela, período atípico, classificação de temas feita por IA (revisar), dados que a API não
trouxe, perfis do Google usados.

## Custo e fontes
Créditos gastos e saldo; onde estão os dados crus (`dados/raw-AAAA-MM-DD/`).
```

## Tom

- Número antes de adjetivo: "rende 2,4 vezes o post típico", não "rende muito bem".
- Fato × inferência: estratégia de concorrente vista de fora é inferência — "parece",
  "sugere". Métrica é fato.
- Nada de "a lição é", "o que isso significa é", fechamento moralizante ou lista de três
  adjetivos. As regras de escrita do vault valem aqui.
- Conta de tamanhos diferentes: nunca compare engajamento % cru sem dizer o tamanho.
