from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage, ImageMessage    # 含入LINE Bot所使用的事件模組

from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

import os, tempfile

from .models import users
from module import func

##### 讀取 <setting.py> 中設定的 channel secret 與 channel access token #####
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

##### 建立 callback 函式，使用者呼叫 "首頁網址/callback" 就會執行此函式
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        
        try:
            events = parser.parse(body, signature)    # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        
        for event in events:
            if isinstance(event, MessageEvent):       # 如果有訊息事件，就發生以下的....
                
                ##### 若使用者第一次使用，會記錄他的 Line ID #####
                user_id = event.source.user_id
                if not (users.objects.filter(uid=user_id).exists()):
                    unit = users.objects.create(uid=user_id)
                    unit.save()
                
                # 收到指定訊息後，回傳特定的訊息
                mtext = event.message.text
                if mtext == '@Hey, Catcher@':   # 點擊圖文選單，出現@Hey, Catcher@ → 回傳關心用語01 → 要自拍照  (儲存方式要再想)
                    #line_bot_api.reply_message(event.reply_token, TextSendMessage(text='今天過得好嗎? \n拍張自拍照讓我瞧瞧你現在的狀態吧~'))
                    func.sendText1(event)
                elif mtext == '@使用說明@':      # 點擊圖文選單，出現@使用說明@     → 回傳使用說明的對話框
                    func.sendText2(event)
                elif mtext == '@心情日記@':      # 點擊圖文選單，出現@心情日記@     → 回傳關心用語02 → 紀錄日記  (儲存方式要再想)
                    func.sendText3(event)
                elif mtext == '@健康檢測@':      # 點擊圖文選單，出現@健康檢測@     → 回傳google問卷(想下要怎麼顯示，不想URL)
                    pass
                elif mtext == '@心情回顧@':      # 點擊圖文選單，出現@心情回顧@     → 顯示一周心情波動圖表       (可能出現心情天氣icon)
                    pass
                elif mtext == '@小小驚喜@':      # 點擊圖文選單，出現@小小驚喜@     → 回傳好聽的音樂或是美食資訊
                    pass
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    ''' 當收到圖片時，儲存圖片，並上載到Imgur中 '''
    ''' 參考 https://github.com/twtrubiks/line-bot-imgur-tutorial/blob/master/app.py '''
    if isinstance(event.message, ImageMessage):  # 若訊息是圖片，則執行以下的操作
        ext = 'jpg'

        message_content = line_bot_api.get_message_content(event.message.id)
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
        
        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)

        # 上傳照片到Imgur
        try:
            client = ImgurClient(settings.client_id, settings.client_secret, settings.access_token, settings.refresh_token)
            config = {
                'album': settings.album_id,
                'name': 'catcher',
                'title': 'catcher',
                'description': '????line bot'
            }
            path = os.path.join('static', 'tmp', dist_name)
            client.upload_from_path(path, config=config, anon=False)
            os.remove(path)
            print(path)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='收到照片囉~'))
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='我沒收到(〒︿〒)，\n請再傳一次，謝謝'))
        return 0

        
        