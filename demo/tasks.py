import asyncio
import random

import httpx
from channels.layers import get_channel_layer

from channelsDemo import celery_app as app
from demo.constants import WSNotificationType

QUOTE_ENDPOINT: str = "https://api.quotable.io/random"
JOKE_ENDPOINTS: list[str] = ["https://official-joke-api.appspot.com/random_joke", "https://v2.jokeapi.dev/joke/Any"]


def _get_response(endpoint: str) -> dict:
    with httpx.Client() as client:
        res: httpx.Response = client.get(endpoint)
    res.raise_for_status()
    return res.json()


def _get_random_quote() -> dict:
    res_json: dict = _get_response(QUOTE_ENDPOINT)
    print(50 * "*")
    print(res_json)
    print(50 * "*")
    return {
        "quote": res_json["content"],
        "author": res_json["author"],
    }


def _get_random_joke() -> dict:
    endpoint: str = random.choice(JOKE_ENDPOINTS)
    res_json: dict = _get_response(endpoint)
    print(50 * "*")
    print(res_json)
    print(50 * "*")
    data = {
        "joke_type": res_json["type"],
        "joke": res_json.get("joke", res_json["setup"]),
    }

    if "delivery" in res_json:
        data["delivery"] = res_json["delivery"]

    if "punchline" in res_json:
        data["delivery"] = res_json["punchline"]

    return data


@app.task
def send_random_quote_to_user_via_ws(user_id):
    content = _get_random_quote()
    loop = asyncio.get_event_loop()

    layer = get_channel_layer()
    coroutine = layer.group_send(
        group=str(user_id),
        message={"type": WSNotificationType.SEND_QUOTE, "message": content},
    )
    loop.run_until_complete(coroutine)


@app.task
def send_random_joke_to_user_via_ws(user_id):
    content = _get_random_joke()
    loop = asyncio.get_event_loop()

    layer = get_channel_layer()
    coroutine = layer.group_send(
        group=str(user_id),
        message={"type": WSNotificationType.SEND_JOKE, "message": content},
    )
    loop.run_until_complete(coroutine)
