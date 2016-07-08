import os

from slackclient import SlackClient

SLACK_TOKEN = os.environ['SLACK_TOKEN']
sc = SlackClient(SLACK_TOKEN)


def post_message(msg):
    sc.api_call(
        "chat.postMessage", channel="#weightloss", text=msg,
        username='pybot', icon_emoji=':robot_face:'
    )
