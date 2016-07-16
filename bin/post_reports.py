#!/usr/bin/env python3

import os
import django
from fitbit.slack import post_message
from fitbit.discord import post_message as discord_post_message


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fitbitslackbot.settings")
    DISCORD_USERS = os.environ['DISCORD_USERS'].split(",")
    django.setup()

    # Cannot import these until django is setup
    from fitbit.models import Token
    from fitbit.views import get_message

    for token in Token.objects.all():
        try:
            message = get_message(token.fitbit_id)
            post_message(message)
            if token.fitbit_id in DISCORD_USERS:
                discord_post_message(message)
        except Exception:
            print("Could not send message for {}".format(token.fitbit_id))
