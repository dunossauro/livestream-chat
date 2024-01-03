from browser import ajax, document, html, timer, websocket, window


def on_message(event):
    messages = document['message']
    selected = document.select_one('.message')
    data = window.JSON.parse(event.data)

    if selected and (
        selected.select_one('.message__content').text == data.message
        and selected.select_one('.message__author').text == data.name
    ):
        messages.clear()
        return

    messages.clear()

    message = html.DIV('', Class='chat-message message')
    message <= html.P(data.name, Class='message__author')
    message <= html.P(data.message, Class='message__content')

    messages <= message


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
    ws = websocket.WebSocket(f'ws://{window.location.host}/ws/chat/event')

    ws.bind('message', on_message)
    ws.bind('close', check_server_up)


check_server_up()
