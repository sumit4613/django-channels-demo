import logging
from typing import Optional

import jwt
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.conf import settings

from demo.constants import WSCommands, WSMessages, WSMessageType, WSNotificationType, COMMAND_TO_MESSAGE_MAP
from demo.decorators import handle_ws_disconnects
from demo.models import User
from demo.tasks import send_random_quote_to_user_via_ws, send_random_joke_to_user_via_ws

logger = logging.getLogger(__name__)


class MyConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user: Optional[User] = None
        self.group = ""

    @handle_ws_disconnects
    def receive_json(self, content, **kwargs):
        command = content.get("command", "")
        message = content.get("message", "")

        if command == WSCommands.PING:
            self.send_pong()
        elif command == WSCommands.AUTHORIZE:
            if user_id := self.authorize(message):
                self.greet_user(user_id)
        elif command in [WSCommands.QUOTE, WSCommands.JOKE]:
            self.notify_user(command)

    @handle_ws_disconnects
    def send_json(self, content, close=False):
        return super().send_json(content, close)

    @handle_ws_disconnects
    def authorize(self, auth_token) -> Optional[str]:
        try:
            decoded_data: dict = self.validate_jwt_token(auth_token)

            self.scope["user"] = self.get_user(user_id=decoded_data["user_id"])
            self.user = self.scope["user"]
            self.group = str(decoded_data["user_id"])

            # Add user to his own group
            self.add_user_to_group(self.group)

        except Exception as e:  # noqa
            self.send_json(
                {
                    "message_type": WSMessageType.AUTHENTICATION,
                    "message": WSMessages.AUTHORIZATION_FAILED,
                    "data": str(e),
                }
            )
            logger.error("WS Authorization Failed", exc_info=e)

        if self.group:
            self.send_message_to_group(
                self.group, {"type": WSNotificationType.AUTHENTICATION, "message": WSMessages.AUTHORIZATION_SUCCESSFUL}
            )
            return self.group

    # command handlers
    @handle_ws_disconnects
    def send_pong(self):
        if self.group:
            self.send_message_to_group(self.group, {"type": WSNotificationType.SEND_PONG, "message": ""})

    def task_map(self):
        # Simple task map to map commands to tasks
        return {
            WSCommands.QUOTE: send_random_quote_to_user_via_ws,
            WSCommands.JOKE: send_random_joke_to_user_via_ws,
        }

    @handle_ws_disconnects
    def notify_user(self, notification_type: str):
        """Notify user about the task that is going to be executed"""
        if self.group:
            self.send_json({"message_type": WSMessageType.NOTIFY, "message": COMMAND_TO_MESSAGE_MAP[notification_type]})
            self.task_map()[notification_type].delay(self.group)

    @handle_ws_disconnects
    def greet_user(self, user_id: str):
        """Greet user with a welcome message"""
        self.send_message_to_group(
            user_id,
            {
                "type": WSNotificationType.GREET_USER,
                "message": WSMessages.USER_CONNECTED.format(username=self.user.username),
            },
        )

    # group handlers
    @handle_ws_disconnects
    def add_user_to_group(self, group_name: str):
        """Add user to his own group"""
        self.groups.append(group_name)
        async_to_sync(self.channel_layer.group_add)(group_name, self.channel_name)

    @handle_ws_disconnects
    def send_message_to_group(self, group_name: str, message: dict):
        """Send message to a group"""
        async_to_sync(self.channel_layer.group_send)(group_name, message)

    # utils
    def validate_jwt_token(self, auth_token: str) -> dict:
        return jwt.decode(auth_token, settings.SECRET_KEY, algorithms=["HS256"])

    def get_user(self, user_id: str) -> User:
        return User.objects.get(id=user_id)

    # notification type handlers
    @handle_ws_disconnects
    def pong_message(self, event):
        self.send_json({"message_type": WSMessageType.PONG, "message": event["message"]})

    @handle_ws_disconnects
    def greet_message(self, event):
        self.send_json({"message_type": WSMessageType.GREET, "message": event["message"]})

    @handle_ws_disconnects
    def authentication_message(self, event):
        self.send_json({"message_type": WSMessageType.AUTHENTICATION, "message": event["message"]})

    @handle_ws_disconnects
    def quote_message(self, event):
        self.send_json({"message_type": WSMessageType.QUOTE, "message": event["message"]})

    @handle_ws_disconnects
    def joke_message(self, event):
        self.send_json({"message_type": WSMessageType.JOKE, "message": event["message"]})
