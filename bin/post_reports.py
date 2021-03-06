#!/usr/bin/env python3

import os
import django
from fitbit.slack import post_message as post_slack_message
from fitbit.discord import post_message as post_discored_message


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fitbitslackbot.settings")
    DISCORD_USERS = os.environ['DISCORD_USERS'].split(",")
    SLACK_USERS = os.environ['SLACK_USERS'].split(",")
    django.setup()

    # Cannot import these until django is setup
    from fitbit.models import Token
    from fitbit.views import get_message

    for token in Token.objects.all():
        try:
            message = get_message(token.fitbit_id)
            if token.fitbit_id in DISCORD_USERS:
                post_discored_message(message)
            if token.fitbit_id in SLACK_USERS:
                post_slack_message(message)
        except Exception:
            print("Could not send message for {}".format(token.fitbit_id))
