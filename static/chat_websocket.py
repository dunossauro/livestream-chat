from browser import websocket, window, document, html

message_types = {
    # message_type: css_class
    'textMessageEvent': 'message',
    'superChatEvent': 'superchat',
    'superStickerEvent': 'newsponsor',
    'newSponsorEvent': 'newsponsor'
}

def on_open(event):
    ws.send(f'Teste!')


def on_message(event):
    data = window.JSON.parse(event.data)

    message = html.DIV("", Class=message_types[data.type])
    message <= html.P(data.name, Class="message__author")
    message <= html.P(data.message, Class="message__content")

    messages = document['messages']
    messages <= message

    window.scrollTo(0, document.body.scrollHeight)

    messages_size = len(messages.childNodes)
    if messages_size > 20:
        messages.removeChild(messages.firstChild)


ws = websocket.WebSocket(
    f'ws://{window.location.host}/ws/chat'
)

ws.bind('message', on_message)
ws.bind('open', on_open)
