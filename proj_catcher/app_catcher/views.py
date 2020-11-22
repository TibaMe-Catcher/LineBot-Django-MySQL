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
#from azure.cognitiveservices.vision.face import FaceClient
#from msrest.authentication import CognitiveServicesCredentials

from .models import users
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
    if not (users.objects.filter(uid=userId).exists()):
        unit = users.objects.create(uid=userId)
        unit.save()



@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if isinstance(event.message, TextMessage):
        text = event.message.text
        if text == '@Hey, Catcher@':   # 點擊圖文選單，出現@Hey, Catcher@ → 回傳關心用語01 → 要自拍照  (儲存方式要再想)
            # line_bot_api.reply_message(event.reply_token, TextSendMessage(text='今天過得好嗎? \n拍張自拍照讓我瞧瞧你現在的狀態吧~'))
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
"""
@handler.add(MessageEvent, message=TextMessage)    # 這一段是抄老師的保存客戶文字，但部署的需求不太一樣，要再研究
def process_text_message(event):
    '''
    handler處理文字消息，收到用戶回應的文字消息後
    將文字消息內容往素材資料夾中儲存，找尋以該內容命名的資料夾，讀取reply.json
    轉譯為json後，將消息回傳給用戶
    '''
    try:
        result_message_array = []         # 讀取本地的檔案，並轉譯成消息
        replyJsonPath = 'material/' + event.message.text + 'reply.json'
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
        line_bot_api.reply_message(event.reply_token, result_message_array)
    except FileNotFoundError as e:
        print('File not found!!!!!')
    with db:
        TextMessageTable.create(
            replyToken.reply_token,
            timestamp = event.timestamp,
            userId = event.source.user_id,
            messageId = event.message.id,
            messageType = event.message.type,
            messageText = event.message.text
        )
"""
'''
# Create an authenticated FaceClient.
KEY = secretFileContentJson.get("azure_key_1")
ENDPOINT = secretFileContentJson.get("azure_face_detect_endpoint")
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
'''

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):

    if isinstance(event.message, ImageMessage):      # 若訊息是圖片，則執行以下的操作
        message_content = line_bot_api.get_message_content(event.message.id)

        i = Image.open(BytesIO(message_content.content))
        filename = './images/' + userId + event.message.id +'.jpg'
        i.save(filename)

        """
        # 偵測臉部，這段式抄寫老師的code，老師導入的是azure的模型
        detected_faces = face_client.face.detect_with_stream(BytesIO(message_content.content))
        if not detected_faces:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到臉...."))
            raise Exception('No face detected from image...')


        """
        message = TextSendMessage(text='成功儲存')    # 成功儲存圖片回傳訊息給使用者
        line_bot_api.reply_message(event.reply_token, message)

        