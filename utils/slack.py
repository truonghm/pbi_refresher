import os, json, sys
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .config import slack_token

def slack_noti(message, user):
    try:
        client = WebClient(token=slack_token)
        response = client.chat_postMessage(
            channel=user,text=message
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]    # str like 'invalid_auth', 'channel_not_found'
        print(e.response["error"])


def slack_table(message, channel):
    
    try:
        client = WebClient(token=slack_token)
        response = client.chat_postMessage(channel = channel, blocks = message)
    except SlackApiError as e:
        assert e.response["error"]
        print(e.response["error"])