# Instalação — Análise de Concorrentes (Discovery)

Passo a passo para quem vai usar a skill pela primeira vez. Leva uns 15 minutos.

## 1. O que você precisa ter

- **Claude Code** instalado e logado.
- Esta skill copiada para dentro de `.claude/skills/` de **algum projeto ou vault seu**.
  Não precisa ser o vault compartilhado "2SAY + Andrey" — pode ser qualquer pasta local
  onde você organiza o trabalho da 2SAY. Abra o Claude Code nessa pasta e a skill aparece
  sozinha, sem instalar nada pelo terminal.
- **Python 3.**
  - Mac: já vem instalado. Confira no Terminal com `python3 --version`.
  - Windows: instale em python.org/downloads e marque **"Add Python to PATH"** na
    primeira tela do instalador. Confira com `python --version`.

**Importante:** cada pasta onde você instalar esta skill tem sua própria chave, guardada
num `.env` só dela. Se você copiou a skill para o seu vault pessoal, **não herda** a chave
que está no vault do Gabriel — precisa da sua própria (passo 2). A skill detecta sozinha a
raiz do projeto onde está instalada; não precisa apontar caminho nenhum.

## 2. Chave da ScrapeCreators (obrigatória)

É a API que puxa os dados públicos de Instagram, Facebook, LinkedIn, YouTube, TikTok e da
Biblioteca de Anúncios da Meta.

1. Entre em https://scrapecreators.com e crie a conta. Ela vem com 100 créditos grátis.
2. No painel, copie a sua **API key**.
3. No Claude Code, dentro da conversa, cole a chave e peça para gravar — ou rode direto no
   terminal, a partir da pasta onde a skill está instalada:
   ```
   python3 .claude/skills/analise-concorrentes-discovery/scripts/configurar.py --set SCRAPECREATORS_API_KEY=cole_sua_chave_aqui
   ```
   Isso cria o `.env` na raiz do seu projeto (ou atualiza, se já existir) — não precisa
   procurar arquivo oculto nem editar nada na mão. Para conferir onde ele gravou:
   `python3 .claude/skills/analise-concorrentes-discovery/scripts/configurar.py --onde`

Créditos: quase toda chamada custa 1. Uma análise completa (cliente + 3 concorrentes)
gasta perto de 60. O pacote de US$ 47 traz 25 mil créditos, que não expiram.

**Se for usar a conta da 2SAY** em vez de criar a sua: peça a chave ao Gabriel e combine
antes de rodar análises grandes, porque o saldo é compartilhado entre quem usa essa chave.
Não cole a chave em documento, e-mail ou grupo de WhatsApp — ela fica só no `.env`.

## 3. Chave do PageSpeed (recomendada, grátis)

Serve para medir o desempenho dos sites no celular. Sem ela a skill tenta outro caminho
(passo 4), mas a chave é o jeito mais simples e funciona igual em Mac e Windows.

1. Entre em https://console.cloud.google.com com uma conta Google.
2. Crie um projeto (ex.: "2SAY Análises"). Não precisa cadastrar cartão.
3. Menu → **APIs e serviços → Biblioteca** → busque **PageSpeed Insights API** → **Ativar**.
4. **APIs e serviços → Credenciais → Criar credenciais → Chave de API**. Copie.
5. (Recomendado) Clique na chave → **Restrições de API** → marque só a PageSpeed Insights API.
6. Grave do mesmo jeito do passo 2:
   ```
   python3 .claude/skills/analise-concorrentes-discovery/scripts/configurar.py --set PAGESPEED_API_KEY=cole_sua_chave_aqui
   ```

## 4. Plano B para o desempenho do site (opcional)

Sem chave do PageSpeed, a skill roda o Lighthouse no seu computador. Para isso precisa:
- **Node.js** (versão LTS em nodejs.org) e
- **Google Chrome** instalado.

Sem nenhum dos dois caminhos, a análise sai sem a nota de desempenho do site — o resto
funciona normalmente.

## 5. Extensão Claude in Chrome (opcional)

Com ela, o Claude abre o Google Maps e lê nota, total e temas das avaliações sozinho. Sem
ela, ele vai pedir que você abra o Maps e informe nota e número de avaliações de cada
empresa — leva dois minutos.

## 6. Teste

No Claude Code, peça: *"roda a checagem da skill de análise de concorrentes"*. Ou rode
direto no terminal, a partir da pasta `2SAY + Andrey`:

```
python3 .claude/skills/analise-concorrentes-discovery/scripts/checar.py --testar-api
```

(no Windows, `python` no lugar de `python3`). O `--testar-api` gasta 1 crédito e mostra o
saldo. Tudo verde: é só pedir *"faz a análise de concorrentes do Discovery do cliente X"*.

## Problemas comuns

- **"SCRAPECREATORS_API_KEY não encontrada"** — ainda não existe `.env` nesta instalação.
  Rode `configurar.py --onde` para ver onde ele ficaria e `configurar.py --set` para criar
  (passo 2). Se você tem certeza que já configurou, confira se está rodando o Claude Code
  na mesma pasta onde instalou esta skill — cada instalação tem o próprio `.env`.
- **Erro 401 da ScrapeCreators** — chave errada ou com espaço sobrando. Cole de novo.
- **PageSpeed com erro 429** — cota esgotada. Acontece sem chave; com chave própria a cota
  é de 25 mil consultas por dia.
- **Site aparece com 403** — o site bloqueia leitura automática. O Claude completa pelo
  navegador ou pede para você olhar.
