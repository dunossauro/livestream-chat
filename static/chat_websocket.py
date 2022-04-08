from browser import websocket, window, document, html


def on_open(event):
    ws.send(f'Teste!')


def on_message(event):
    messages = document['messages']
    messages <= html.P(event.data)
    messages.scrollTop = (
        messages.scrollHeight - messages.clientHeight
    )

ws = websocket.WebSocket(
    f'ws://{window.location.host}/ws/chat'
)

ws.bind('message', on_message)
ws.bind('open', on_open)
