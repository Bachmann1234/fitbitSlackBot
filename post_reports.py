import os
import django
from fitbit.slack import post_message

IDS_TO_POST = os.environ['AUTOPOST'].split(',')

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fitbitslackbot.settings")
    django.setup()

    # Cannot import these until django is setup
    from fitbit.models import Token
    from fitbit.views import get_message

    for token in Token.objects.filter(fitbit_id__in=IDS_TO_POST):
        try:
            post_message(get_message(token.fitbit_id))
        except Exception:
            print("Could not send message for {}".format(token.fitbit_id))
