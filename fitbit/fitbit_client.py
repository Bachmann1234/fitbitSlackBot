import base64
import os

import requests
from fitbit.models import Token

FITBIT_AUTH_URL = 'https://api.fitbit.com/oauth2/token?code={code}&client_id={client_id}&grant_type=authorization_code'
FITBIT_AUTH_REFRESH_URL = ('https://api.fitbit.com/oauth2/token?'
                           'refresh_token={refresh_token}&grant_type=refresh_token')
CLIENT_ID = os.environ["FITBIT_CLIENT_ID"]
CLIENT_SECRET = os.environ["FITBIT_CLIENT_SECRET"]

FITBIT_PERMISSION_SCREEN = 'https://fitbit.com/oauth2/authorize?response_type=code&client_id={client_id}&scope={scope}'.format(
    client_id=CLIENT_ID,
    scope='nutrition%20activity%20weight%20profile'
)

TOKEN = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET).encode('utf-8')).decode('utf-8')


def refresh(fitbit_info):
    auth_url = FITBIT_AUTH_REFRESH_URL.format(
        refresh_token=fitbit_info.refresh_token
    )
    return do_fitbit_auth(auth_url)


def do_fitbit_auth(url):
    r = requests.post(
        url,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {}'.format(TOKEN),
        }
    )
    r.raise_for_status()
    response = r.json()
    fitbit_info = Token.objects.get_or_create(fitbit_id=response['user_id'])[0]
    fitbit_info.refresh_token = response['refresh_token']
    fitbit_info.save()
    return response


def get_profile(fitbit_auth_dict):
    return _get_fitbit_response(
        "https://api.fitbit.com/1/user/{}/profile.json".format(
            fitbit_auth_dict['user_id']
        ),
        fitbit_auth_dict
    )['user']


def get_food_for_day(fitbit_auth_dict, date_to_get):
    return _get_fitbit_response(
        "https://api.fitbit.com/1/user/{}/foods/log/date/{:%Y-%m-%d}.json".format(
            fitbit_auth_dict['user_id'],
            date_to_get
        ),
        fitbit_auth_dict
    )


def get_activity_for_day(fitbit_auth_dict, date_to_get):
    return _get_fitbit_response(
        "https://api.fitbit.com/1/user/{}/activities/date/{:%Y-%m-%d}.json".format(
            fitbit_auth_dict['user_id'],
            date_to_get
        ),
        fitbit_auth_dict
    )


def get_weight_for_day(fitbit_auth_dict, date_to_get):
    return _get_fitbit_response(
        "https://api.fitbit.com/1/user/{}/body/log/weight/date/{:%Y-%m-%d}.json".format(
            fitbit_auth_dict['user_id'],
            date_to_get
        ),
        fitbit_auth_dict
    )['weight']


def _make_headers(fitbit_auth_dict):
    return {
        'Authorization': 'Bearer {}'.format(fitbit_auth_dict['access_token']),
        'Accept-Language': 'en_US'
    }


def _get_fitbit_response(url, auth):
    return requests.get(
        url,
        headers=_make_headers(auth)
    ).json()
