from datetime import datetime
import os
import sys
import logging
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.models import (
    MessageEvent, TextMessage, FollowEvent, TextSendMessage,
)
from linebot.exceptions import (
    InvalidSignatureError
)

from databaseConnections.firestoreConnection import FirestoreConnection

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

def callback(request):
    try:
        # get linebot event
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return 'ERROR'
        
        # handle events
        for event in events:
            handleEvent(event)

    except Exception as ex:
        # Display error message in console
        logging.error(str(ex))
        return 'ERROR'
    return 'OK'

def handleEvent(event):
    try:
        if isinstance(event, FollowEvent):
            handleFollowEvent(event)
            
        if not isinstance(event, MessageEvent):
            return
        if not isinstance(event.message, TextMessage):
            return

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = event.message.text))

    except Exception as ex:
        # Display error message in chatroom
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = str(ex)))

def handleFollowEvent(event: FollowEvent):
    try:
        db = FirestoreConnection()
        user_info = db.getUserInfo(event.source.user_id)
        userProfile = line_bot_api.get_profile(event.source.user_id)

        if user_info == None:
            db.setUserInfo(event.source.user_id, {
                "UserId": event.source.user_id,
                "UserName": userProfile.display_name,
                "FollowedDate": datetime.now(),
                "Following": True,
            })
            line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text = f"Hi {userProfile.display_name}, it's good to see you!"))
        else:
            db.setUserInfo(event.source.user_id, {
                "UserName": userProfile.display_name,
                "Following": True,
            })
            line_bot_api.reply_message(event.reply_token,
                TextSendMessage(text = f"Hi {userProfile.display_name}, it's good to see you again!"))
    except Exception as ex:
        raise ex
    finally:
        db.close()
