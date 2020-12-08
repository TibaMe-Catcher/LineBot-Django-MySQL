from django.conf import settings

from linebot import LineBotApi
from linebot.models import *

import http.client, json
from app_catcher.models import *

# 影像識別需要的套件
import dlib
import math,  cv2, glob, joblib
import numpy as np
from sklearn.svm import SVC

# google表單存進MySQL的function，之後要整併成一個大的function，等view那邊寫好後這邊整合
import pymysql
import gspread
from oauth2client.service_account import ServiceAccountCredentials

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

def sendText1(event):
    ''' @Hey, Catcher@ 收集自拍照，之後要呼叫情緒臉辨識的演算法進行分析 '''
    try:
        text01 = '今天過得好嗎? \n請拍一張照片來告訴我你現在的心情~'
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
                   " '我的頭像'：拍個自拍照，讓我瞧瞧現在的你\n" +
                   " '心情日記'：寫下今天的日記或是趣事雜記吧\n" +
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
        text02 = '跟我說說~~\n今天發生了哪些事情，和你當時的心情~~'
        message = TextSendMessage(text = text02)
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！\n聯絡我感恩!'))

#=======================================================================================================

def sendText4(event):
    ''' @心情問卷@ '''
    try:
        text = '請先複製你的ID：' + event.source.user_id + '\n\n並點擊連結填寫健康檢測問卷：\n' + 'https://forms.gle/mBGwnuuqMtZ3mmgBA'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！\n聯絡我感恩!'))

#=======================================================================================================






#=======================================================================================================

def cv_test(img):    
    # 使用 Dlib 偵測人臉 & 特徵點萃取
    detector = dlib.get_frontal_face_detector()               # 呼叫人臉偵測器
    predictor = dlib.shape_predictor(
        "C:/Users/coco/Desktop/tibame_project/proj_catcher/module/shape_predictor_68_face_landmarks.dat"
        )                                                     # 呼叫特徵點萃取器


    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    data = {}
    img_data = []


    # 定義偵測人臉和特徵點的function
    def get_landmarks(img):
        face_rects = detector(img, 0)                   # face_rects 回傳結果為人臉方框的座標
        for k, d in enumerate(face_rects):
            shape = predictor(img, d)                   # 使用predictor類別萃取人臉特徵點

            xlist = []
            ylist = []
            for i in range(1, 68):                      # 將特徵點(共68點) X和Y座標各別存入兩個list
                xlist.append(float(shape.part(i).x))
                ylist.append(float(shape.part(i).y))

            xmean = np.mean(xlist)                   # 取得 xlist 矩陣的平均值
            ymean = np.mean(ylist)                   # 取得 ylist 矩陣的平均值

            # 每個特徵點的x座標與xmean相減以得到離均差(deviation from the mean)
            xcentral = [(x-xmean) for x in xlist]
            # 每個特徵點的y座標與ymean相減以得到離均差(deviation from the mean)
            ycentral = [(y-ymean) for y in ylist]

            landmarks_vectorised = []
            # zip() 函數可以將對應的元素打包成一個個tuple以節約內存
            for x, y, w, z in zip(xcentral, ycentral, xlist, ylist):
                landmarks_vectorised.append(w)
                # landmarks_vectorised = [xlist[0], ylist[0], xlist[1], ylsit[1]...]
                landmarks_vectorised.append(z)
                # np.asarry() 將input轉為矩陣
                meannp = np.asarray((ymean, xmean))
                coornp = np.asarray((z, w))
                # linalg=linear algebra，norm則表示範數。範數是對向量（或者矩陣）的度量，是一個標量（scalar）。
                dist = np.linalg.norm(coornp-meannp)        # 計算每個特徵點座標到臉中心點的距離
                landmarks_vectorised.append(dist)
                # math.atan2()回傳從原點到(x, y)點的線段與x軸正方向之間的平面角度(弧度值)
                # 用鼻樑的角度修正臉傾斜所造成的誤差
                landmarks_vectorised.append((math.atan2(y, x)*360)/2*math.pi)

                # 我們得到 a. 每個特徵點到臉中心點的距離  b. 角度  -> 矩陣
                data['landmarks_vectorised'] = landmarks_vectorised

        # 若人臉偵測失敗，value為error
        if len(face_rects) < 1:
            data['landmarks_vectorised'] = "error"


    def test(img):
        img = cv2.imread(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe_image = clahe.apply(gray)
        get_landmarks(clahe_image)
        img_data.append(data['landmarks_vectorised'])
        np_img_data = np.array(img_data)
        return img_data

    # 呼叫模型
    clf_1 = joblib.load('C:/Users/coco/Desktop/tibame_project/proj_catcher/module/clf_4.pkl')

    # 套用模型
    return clf_1.predict(test(img))

#=======================================================================================================

# 將 gspread 的變量初始化
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('linebotphq9-184c1a155eaa.json', scope)
client = gspread.authorize(creds)

# 從表單提取數據
def GetSpreadsheetData(PHQ9, worksheetIndex):
    """
    表單名字：PHQ9
    要獲取的工作表分頁是worksheetIndex==0
    """
    sheet = client.open(PHQ9).get_worksheet(worksheetIndex)
    return sheet.get_all_values()[1:]


# 若資料有更新，就執行下面的function
def UpdateMySQLTable(sql_data, tableName):
    # 資料庫設定
    db_settings = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'abc123',
        'db': 'line_catcher',
        'charset': 'utf8'
    }
    
    try:
        # 建立 connection 物件
        connection = pymysql.connect(**db_settings)
        # 製作一個指標，只要執行成功，就會回傳訊息
        with connection.cursor() as cursor:
            # 添加數據到 MySQL，若PRIMARY KEY存在則忽略該行，若不存在，則添加新使用者的資料
            sql_insert_statement = "INSERT IGNORE INTO {}(TIMESTAMP, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, UserID) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(tableName)
            for i in sql_data:
                cursor.execute(sql_insert_statement, i)              # 將資料的每一個 row 存進 MySQL
        connection.commit()
        print("Table {} successfully updated.".format(tableName))    # 儲存變更成功回傳訊息
    except pymysql.Error as error:
        connection.rollback()
        print("Error: {}. Table {} not updated!".format(error, tableName))
        
    finally: 
        cursor.close()
        connection.close()
        print('MySQL connection is closed.')

data = GetSpreadsheetData('PHQ9', 0)
UpdateMySQLTable(data, 'PHQ9')
#=======================================================================================================
