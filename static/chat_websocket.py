from browser import ajax, document, html, timer, websocket, window

message_types = {
    'textMessageEvent': 'message',
    'superChatEvent': 'superchat',
    'superStickerEvent': 'newsponsor',
    'newSponsorEvent': 'newsponsor',
}


def on_message_click(event):
    name, message = event.target.select('p')

    ajax.post(
        f'http://{window.location.host}/highlight',
        data=window.JSON.stringify(
            {'message': message.text, 'name': name.text},
        ),
        headers={'Content-Type': 'application/json'},
    )


def on_message(event):
    data = window.JSON.parse(event.data)

    message = html.DIV('', Class=f'chat-message {message_types[data.type]}')
    message <= html.P(data.name, Class='message__author')
    message <= html.P(data.message, Class='message__content')

    message.bind('click', on_message_click)

    messages = document['messages']
    messages <= message

    window.scrollTo(0, document.body.scrollHeight)

    messages_size = len(messages.childNodes)
    if messages_size > 20:
        messages.removeChild(messages.firstChild)


def check_server_up(event=None):
    def on_complete(request):
        if request.status == 200:
            start_ws()

    try:
        ajax.get(
            f'http://{window.location.host}/health',
            oncomplete=on_complete,
            blocking=True,
        )
    except Exception:
        timer.set_timeout(check_server_up, 5_000)


def start_ws():
    ws = websocket.WebSocket(f'ws://{window.location.host}/ws/chat/messages')

    ws.bind('message', on_message)
    ws.bind('close', check_server_up)


check_server_up()
