import os

import requests

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
DISCORD_CHANNEL = os.environ['DISCORD_CHANNEL']
POST_URL = "https://discordapp.com/api/channels/{}/messages".format(DISCORD_CHANNEL)


def post_message(message):
    headers = {
        "Authorization": "Bot {}".format(DISCORD_TOKEN),
        "Content-Type": "application/json"
    }
    response = requests.post(
        POST_URL,
        json={
            "content": message
        },
        headers=headers
    )
    response.raise_for_status()
