from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage    # 含入LINE Bot所使用的事件模組

from .models import users
from module import func

##### 讀取 <setting.py> 中設定的 channel secret 與 channel access token #####
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

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
                    
                ##### 若接收到文字訊息，就會回傳相同的文字訊息 #####
                #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
                
 
                mtext = event.message.text
                if mtext == '@Hey, Catcher@':   # 點擊圖文選單，出現@Hey, Catcher@ → 回傳關心用語01 → 要自拍照  (儲存方式要再想)
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



                #elif mtext == '@傳送圖片':
                #    func.sendImage(event)
                   
                
        return HttpResponse()
    else:
        return HttpResponseBadRequest()