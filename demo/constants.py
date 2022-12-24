class WSCommands:
    PING: str = "ping"
    AUTHORIZE: str = "authorize"
    QUOTE: str = "quote"
    JOKE: str = "joke"


class WSMessages:
    AUTHORIZATION_SUCCESSFUL: str = "Authorization successful"
    AUTHORIZATION_FAILED: str = "Authorization failed"
    USER_CONNECTED: str = "Welcome, {username}! You are now connected. Cheers!"
    SENDING_QUOTE: str = "Sending a quote to you..."
    SENDING_JOKE: str = "Sending a joke to you..."


COMMAND_TO_MESSAGE_MAP: dict = {
    WSCommands.QUOTE: WSMessages.SENDING_QUOTE,
    WSCommands.JOKE: WSMessages.SENDING_JOKE,
}


class WSMessageType:
    PONG: str = "pong"
    GREET: str = "greet"
    AUTHENTICATION: str = "authentication"
    QUOTE: str = "quote"
    JOKE: str = "joke"
    NOTIFY: str = "notify"


class WSNotificationType:
    SEND_PONG: str = "pong.message"
    GREET_USER: str = "greet.message"
    AUTHENTICATION: str = "authentication.message"
    SEND_QUOTE: str = "quote.message"
    SEND_JOKE: str = "joke.message"
