# Briefing — Análise de Concorrentes

Copie o bloco abaixo para `2SAY/Clientes/<Cliente>/Análise de Concorrentes/briefing.md` e
preencha. Antes de perguntar à pessoa, veja o que o vault já responde (nota do cliente,
reuniões, deck do Discovery) — pergunte só o que faltar, e no máximo 3–4 perguntas por vez.

Os campos marcados com * são os que bloqueiam a coleta. O resto melhora a leitura, mas dá
para seguir sem e completar depois.

---

```markdown
---
tags: [2say, discovery, analise-concorrentes]
cliente: <nome>
created: AAAA-MM-DD
---

# Briefing — Análise de Concorrentes · <Cliente>

## Cliente
- Nome*:
- Segmento e o que vende*:
- Cidade / região de atuação*:
- Site*:
- Instagram* (e outros canais que você já sabe):
- Quem compra e quem decide a compra (pode ser gente diferente):
- Posicionamento declarado — como o cliente se descreve (bio, site, fala dos sócios):
- O que o cliente disse querer do Discovery (expectativas da abertura do workshop):

## Concorrentes (3 a 5)
| Nome* | Cidade | Tipo (direto / indireto / referência de outra praça) | Por que está na lista | Instagram ou site (se souber) |
|---|---|---|---|---|
|  |  |  |  |  |

Referência de outra praça é quem não disputa o mesmo cliente, mas mostra o que é possível
no segmento (ex.: um caso maduro do mesmo tipo de negócio numa cidade maior).

## Contexto
- Algum período atípico nos últimos meses? (evento grande, eleição, campanha sazonal, crise)
- O cliente vai liberar acesso aos Insights dele (alcance, salvamentos, público)? sim / não
- Perguntas específicas dos sócios ou do cliente que a análise precisa responder:
- Onde a saída vai entrar (páginas do deck, reunião, entrega separada) e prazo:

## Parâmetros da coleta
- Janela de comparação: 30 dias (padrão) / 60 / 90 — use mais para quem posta pouco
- Canais a incluir: Instagram, Facebook, LinkedIn, YouTube, TikTok, anúncios Meta, Google, site
- Créditos estimados (preencher após `coletar.py --estimar`):
```

---

## Como conduzir

- **Concorrentes que o cliente cita × concorrentes reais.** O cliente costuma citar quem
  ele vê, não quem o comprador compara. Se der, cruze com uma busca no Google/Maps pelo
  serviço na região e pergunte ao usuário se inclui algum que apareceu.
- **Grupos com várias marcas ou unidades.** Decida junto com a pessoa se entra a marca-mãe,
  a unidade local ou as duas — e registre, porque muda a comparação.
- **Mesma régua.** Todo concorrente passa pelos mesmos canais e pela mesma janela. Canal
  que não existe é registrado como ausente, não pulado.
- **Sem acesso aos Insights.** Tudo bem — a comparação usa só dado público de todos. Se
  vier acesso, o dado privado entra no diagnóstico do cliente, nunca na tabela comparativa.
