def handle_response(message):
    msg = message.lower()
    if msg == 'hello':
        return 'Hey there!'

    if msg == 'help':
        return "`I help!`"
