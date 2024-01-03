# livestream-chat

Overlay para chats de livestreams. Inicialmente para rodar dentro do browser do obs-studio.

![livestream-chat](https://user-images.githubusercontent.com/1103672/162596499-ab338e0c-6301-47de-a720-08eff5c36582.gif)

## TODO:

- [x] [Issues iniciais](https://github.com/dunossauro/livestream-chat/issues)
- [ ] Suportar [emotes da twitch](https://www.npmjs.com/package/@mkody/twitch-emoticons)
- [x] Refresh no socket (front)
- [x] Capturar e exibir de forma diferente as mensagens da twitch


## Colocar as duas variáveis de ambiente


- LIVESTREAM_ID - ID de uma live rolando (código do final da URL)

- SERVICES - "youtube,twitch"
- YOUTUBE_LIVESTREAM_ID - ID de uma live rolando (código do final da URL)
- GOOGLE_API_KEY - Sua api do google
- TWITCH_TOKEN="oauth:..."
- SENTRY_DSN="https://...@....ingest.sentry.io/..." **OPCIONAL**

Você também pode criar um arquivo `.env` e passar as suas variáveis de ambiente para ele. Existe um exemplo [aqui](dotenv.txt)

## Como rodar o projeto?

```shell
docker-compose up
```

## Como editar os estilos?

Primeiro, instale as dependências de front:

```shell
npm install
```

Depois, edite o que quiser no arquivo `static/styles.scss` (não mexa manualmente no `static/styles.css`)

E finalmente rode o compilador do [sass](https://sass-lang.com/) para regerar o arquivo `static/styles.css`. Esse comando deve ser rodado toda vez que um estilo for alterado no `static/styles.scss`.

```shell
npm run compile-sass
```

Caso queira editar as bordas e cores da mensagem, veja a documentação das variáveis usadas no SCSS [desse projeto aqui](https://nigelotoole.github.io/pixel-borders/) e mude o que quiser no `@include` feito na classe `.message`.
