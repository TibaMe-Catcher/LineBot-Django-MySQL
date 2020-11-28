from django.shortcuts import render               # Django 模組
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *                       # LINE Bot 模組
from linebot.models.template import *

#from imgurpython import ImgurClient               # 好像不需要用到Imgur，若之後有需要回傳圖片給User，再導入此段
#from imgurpython.helpers.error import ImgurClientError

import os, tempfile, datetime, errno, json, sys    # 常用的模組
from PIL import Image, ImageDraw                   # 圖片及臉部辨識模組
from io import BytesIO

from .models import *
from module import func

##### 讀取 <setting.py> 中設定的 channel secret 與 channel access token #####
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

##### 建立 callback 函式，使用者呼叫 "首頁網址/callback" 就會執行此函式 #####
@csrf_exempt
def callback(request):
    '''監聽所有來自/callback的POST request'''
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']    # 解析request的header是否包含Line的簽名
        body = request.body.decode('utf-8')                  # 以 utf-8 編碼解析request body
        
        try:
            handler.handle(body,signature)                   # 從Line傳過來訊息
        except InvalidSignatureError:
            return HttpResponseBadRequest
        return HttpResponse('OK')

##### 取得User ID，若尚未存入資料庫就儲存 #####        
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userId = line_bot_api.get_profile(event.source.user_id)
    if not (Users.objects.filter(uid=userId).exists()):
        unit = Users.objects.create(uid=userId)
        unit.save()


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if isinstance(event.message, TextMessage):
        text = event.message.text
        if text == '@Hey, Catcher@':   # 點擊圖文選單，出現@Hey, Catcher@ → 回傳關心用語01 → 要自拍照  (儲存方式要再想)
            func.sendText1(event)
        elif text == '@使用說明@':      # 點擊圖文選單，出現@使用說明@     → 回傳使用說明的對話框
            func.sendText2(event)
        elif text == '@心情日記@':      # 點擊圖文選單，出現@心情日記@     → 回傳關心用語02 → 紀錄日記  (儲存方式要再想)
            func.sendText3(event)
        elif text == '@每日檢測@':      # 點擊圖文選單，出現@每日檢測@     → 回傳google問卷(想下要怎麼顯示，不想URL)
            pass
        elif text == '@心情回顧@':      # 點擊圖文選單，出現@心情回顧@     → 顯示一周心情波動圖表       (可能出現心情天氣icon)
            pass
        elif text == '@小小驚喜@':      # 點擊圖文選單，出現@小小驚喜@     → 回傳好聽的音樂或是美食資訊
            pass
        else:                           # 假若不是預設功能的文字，就將文字訊息存入SQL
            message_id = event.message.id
            text = event.message.text
            diary_uid = event.source.user_id    # 作為ForeignKey，但寫的過程沒有成功

            # message = [TextSendMessage(text = "text：" + text + "\n" + 
            #                                   "message_id：" + event.message.id + "\n" + 
            #                                   "diary_uid：" + event.source.user_id)]
            # line_bot_api.reply_message(event.reply_token, message)    # 回傳同樣文字、message_id、user_id給使用者

            # with open("./tmp/test.txt", "a") as myfile:               # 將文字內容存到本地端
            #     myfile.write(json.dumps(text,sort_keys=True))
            #     myfile.write('\r\n')
        
            unit = Diary.objects.create(diary_id = message_id, text = text)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    if isinstance(event.message, ImageMessage):      # 若訊息是圖片，則執行以下的操作
        picture_id = event.message.id
        picture_uid = event.source.user_id           # 作為ForeignKey，但寫的過程沒有成功
        
        unit = Picture.objects.create(picture_id = picture_id)
        
        # 將圖片儲存到./images/的資料夾下面
        message_content = line_bot_api.get_message_content(event.message.id)
        i = Image.open(BytesIO(message_content.content))
        filename = './images/' + event.message.id +'.jpg'
        i.save(filename)
        

        message = TextSendMessage(text='成功儲存')    # 成功儲存圖片回傳訊息給使用者
        line_bot_api.reply_message(event.reply_token, message)

        

        