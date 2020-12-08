from django.shortcuts import render               # Django 模組
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *                       # LINE Bot 模組
from linebot.models.template import *

#from imgurpython import ImgurClient               # 不需要用到Imgur，若之後有需要回傳圖片給User，再導入此段
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
def handle_get_userid(event):
    userId = line_bot_api.get_profile(event.source.user_id)

    if not (Users.objects.filter(uid=userId).exists()):
        unit = Users.objects.create(uid=userId)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text

    if text == '@Hey, Catcher@':   # 點擊圖文選單，出現@Hey, Catcher@ → 回傳關心用語01 → 要自拍照
        func.sendText1(event)
    elif text == '@使用說明@':      # 點擊圖文選單，出現@使用說明@     → 回傳使用說明的對話框
        func.sendText2(event)
    elif text == '@心情日記@':      # 點擊圖文選單，出現@心情日記@     → 回傳關心用語02 → 紀錄日記
        func.sendText3(event)
    elif text == '@心情問卷@':      # 點擊圖文選單，出現@心情問卷@     → 回傳google問卷(想下要怎麼顯示，不想URL)
        func.sendText4(event)
    elif text == '@心情回顧@':      # 點擊圖文選單，出現@心情回顧@     → 顯示一周心情波動圖表   (可能出現心情天氣icon)
        pass
    elif text == '@小小驚喜@':      # 點擊圖文選單，出現@小小驚喜@     → 回傳好聽的音樂或是美食資訊
        pass
    else:                           # 假若不是預設功能的文字，就將文字訊息存入SQL
        message_id = event.message.id
        text = event.message.text
        diary_uid = event.source.user_id

        # message = [TextSendMessage(text = "text：" + text + "\n" + 
        #                                   "message_id：" + event.message.id + "\n" + 
        #                                   "diary_uid：" + event.source.user_id)]
        # line_bot_api.reply_message(event.reply_token, message)    # 回傳同樣文字、message_id、user_id給使用者

        # with open("./tmp/test.txt", "a") as myfile:               # 將文字內容存到本地端
        #     myfile.write(json.dumps(text,sort_keys=True))
        #     myfile.write('\r\n')
        
        unit = Diary.objects.create(diary_id = message_id, text = text, diary_uid=diary_uid)


@handler.add(MessageEvent, message=ImageMessage)    # 若訊息是圖片，則執行以下的操作
def handle_image_message(event):    
    picture_id = event.message.id
    picture_uid = event.source.user_id
        
    # 將圖片儲存到./images/的資料夾下面
    message_content = line_bot_api.get_message_content(event.message.id)
    i = Image.open(BytesIO(message_content.content))
    filename = 'C:/Users/coco/Desktop/tibame_project/proj_catcher/images/' + event.message.id +'.jpg'
    i.save(filename)
    
    # # 成功儲存圖片回傳訊息給使用者
    # message = TextSendMessage(text='成功儲存')
    # line_bot_api.reply_message(event.reply_token, message)
    
    # 呼叫模型比對照片的情緒
    picture_score = int(func.cv_test(filename))

    if picture_score == 0:    # 假如判斷是 "angry"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='什麼事情惹你不高興?來跟我說說吧'))
    elif picture_score == 1:  # 假如判斷是 "happy"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='看起來你今天挺開心的，有什麼好事可以跟我分享?'))    
    elif picture_score == 2:  # 假如判斷是 "neutral"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='看起來你今天沒有太大情緒起伏?!'))
    elif picture_score == 3:  # 假如判斷是 "sad"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生了什麼事，你看起來不太好Q_Q'))            
    elif picture_score == 4:  # 假如判斷是 "surprise"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='什麼事情讓你這麼吃驚?!'))


    unit = Picture.objects.create(picture_id=picture_id, picture_score=picture_score, picture_uid=picture_uid)
    

        

        