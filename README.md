# Channels Demo

This is just a demo project which I created while learning about channels and channels_redis.

In this project, I created a simple websocket endpoint which sends quotes and jokes to authenticated users. For more
details check [consumers.py](demo/consumers.py).

- [Channels](https://github.com/django/channels/)
- [Channels Redis](https://github.com/django/channels_redis/)

## Note

- **We're using `channels_redis` as our channel layer. Please make sure you have redis installed and running on your
  system.**

## Installation

- Clone the repository.
- Create a virtual environment and activate it.
- Install the requirements using `pip install -r requirements.txt`.
- Run the migrations using `python manage.py migrate`.
- Run `python manage.py create_dummy_user` to create a dummy user.
- Run `python manage.py runserver` to start the server.
- Make a POST call with username and password of your dummy user to `http://127.0.0.1:8000/token/` to get access token.
- Run uvicorn using `uvicorn --port 8001 channelsDemo.asgi:application` to start the websocket server.
- Run celery worker using `celery -A channelsDemo.celery_app worker -l INFO` to start the celery worker.
- Everything is set up now. Open any websocket client and connect to `ws://127.0.0.1:8001/ws/user/notifications/`

## Usage

#### From client side, send a message with the following format to the websocket server:

```json
{
  "command": "authorize",
  "message": "your_access_token"
}
```

#### You will receive a message with the following format:

```json
{
  "message_type": "authentication",
  "message": "Authorization successful"
}
```

```json
{
  "message_type": "greet",
  "message": "Welcome, <your_username>! You are now connected. Cheers!"
}
```

## Quote

#### To get a quote, send a message with the following format:

```json
{
  "command": "quote"
}
```

#### In response, you will receive a message with the following format:

```json
{
  "message_type": "quote",
  "message": {
    "quote": "Do not overrate what you have received, nor envy others. He who envies others does not obtain peace of mind.",
    "author": "Buddha"
  }
}
  ```

## Joke

#### To get a joke, send a message with the following format:

```json
{
  "command": "joke"
}
```

#### In response, you will receive a message with the following format:

```json
{
  "message_type": "joke",
  "message": {
    "joke_type": "twopart",
    "setup": "What does the mermaid wear to math class?",
    "delivery": "Algae-bra."
  }
}
```

## Checking if connection is alive

```json
{
  "command": "ping"
}
```

#### In response, you will receive a message with the following format:

```json
{
  "message_type": "pong",
  "message": ""
}
```

What's missing?

- [ ] Tests (Maybe I'll add them later if I get time)