from django.conf import settings

from linebot import LineBotApi
from linebot.models import (TextSendMessage, ImageSendMessage, LocationSendMessage, TemplateSendMessage, ImagemapSendMessage)

from app_catcher.models import users

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

def sendText1(event):
    ''' @Hey, Catcher@ 收集自拍照，之後要呼叫情緒臉辨識的演算法進行分析 '''
    try:
        text01 = '今天過得好嗎? \n拍張自拍照讓我瞧瞧你現在的狀態吧~'
        message = TextSendMessage(text = text01)
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！\n聯絡我感恩!'))
    
    # 尚未撰寫儲存圖片的方式
    # 參考https://github.com/twtrubiks/line-bot-imgur-tutorial/blob/master/README.md
    # 或是參考 http://studyhost.blogspot.com/2019/01/line-botimgur.html

#=======================================================================================================

def sendText2(event):
    ''' @使用說明@ '''
    try:
        message = [
            TextSendMessage(  
            text = "Hola ~~\n我是Catcher，很高興認識你~\n\n" +
                   "下方菜單欄中有需多小功能，有時間都可以嘗試看看喔~\n\n" +
                   " '我的頭像'：拍個自拍照\n" +
                   " '心心日記'：寫下今天的心情日記或是趣事雜記\n" +
                   " '健康檢測'：做個心理健康評估\n" +
                   " '心情回顧'：回顧一周的心情天氣\n" + 
                   " '小小驚喜'：點擊看看就知道了 >u<\n")
            ]
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！\n聯絡我感恩!'))    

#=======================================================================================================

def sendText3(event):
    ''' @心情日記@ '''
    try:
        text02 = '紀錄一下今天發生的事，\n以及你的心情吧~~'
        message = TextSendMessage(text = text02)
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！\n聯絡我感恩!'))

#=======================================================================================================

'''
def googlelist(event):
    formId = "1ffPC2aqVcetPDFIzsz-6MJPuLtYHpUyJQkGYnSkqE3g"         #表單 ID
    spreadSheetId = "1a_iw1N8dXS_FmKvw4xpAYnryoLyQgNqHShlu1uUpn3I"  #試算表 ID
    sheetName = "PHQ紀錄"                                           #工作表名稱
    destinationFolderID = "1TRYx5qAq5B14N1tElaOMb_WylsAXkjMm"       #存放檔案的資料夾ID

    form_Id = FormApp.openById(formId)
    spreadSheet = SpreadsheetApp.openById(spreadSheetId)
    sheet = spreadSheet.getSheetByName(sheetName)
    lastRow = sheet.getLastRow()
    lastColumn = sheet.getLastColumn()
    sheetData = sheet.getSheetValues(1, 1, lastRow, lastColumn)
    confirmationMessageDefault = "我們已經收到您回覆的表單。"
    confirmationMessage = form_Id.getConfirmationMessage()
'''