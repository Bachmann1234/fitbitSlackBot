import base64
import os

import requests

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
    return do_fitbit_auth(auth_url, fitbit_info)


def do_fitbit_auth(url, fitbit_info):
    r = requests.post(
        url,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {}'.format(TOKEN),
        }
    )
    r.raise_for_status()
    response = r.json()
    fitbit_info.refresh_token = response['refresh_token']
    fitbit_info.fitbit_id = response['user_id']
    fitbit_info.save()
    return response


def get_weight(fitbit_auth_dict):
    url = "https://api.fitbit.com/1/user/{}/profile.json".format(
        fitbit_auth_dict['user_id']
    )
    response = requests.get(
        url,
        headers=_make_headers(fitbit_auth_dict)
    ).json()
    return response['user']['weight']


def _make_headers(fitbit_auth_dict):
    return {
        'Authorization': 'Bearer {}'.format(fitbit_auth_dict['access_token']),
        'Accept-Language': 'en_US'
    }
