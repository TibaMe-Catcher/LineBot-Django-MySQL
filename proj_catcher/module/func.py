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
import pandas as pd

# 分析文字需要的套件
import jieba
import joblib
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
            text = "Hola ~~\n" +
                   "下方菜單欄中有需多小功能，\n有時間都可以嘗試看看喔~\n\n" +
                   " 每日一照：拍張照片，讓我瞧瞧現在的你\n" +
                   " 心情日記：跟我分享今天發生哪些事情?\n" +
                   " 心情問卷：做個心理健康評估\n" +
                   " 心情回顧：回顧一周的心情天氣\n" + 
                   " 小小驚喜：點擊看看就知道了 >v<\n")
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

def sendText5(event):
    '''@小小驚喜@'''
    # 記得要先從models.py import 小驚喜的class

    try:
        # 資料庫設定
        db_settings = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'abc123',
            'db': 'line_catcher',
            'charset': 'utf8'
        }

        connection = pymysql.connect(**db_settings)    # 建立 connection 物件
        
        with connection.cursor() as cursor:
            surp =("SELECT * FROM line_catcher.app_catcher_surprise ORDER BY RAND() LIMIT 1")
            cursor.execute(surp)
        connection.commit()

        result = cursor.fetchall()[0]                  # result的類型是tuple

        if result[2] == "music":
            text = "想跟你分享一首好聽的歌！ \n[{}]\n{}".format(result[4], result[5])
        elif result[2] == "joke":
            text = "我來跟你說一個笑話！\n\n[{}]\n\n{}".format(result[4], result[5])
        
        # 關閉數據庫的連結
        cursor.close()
        connection.close()

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))
    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！\n聯絡我感恩!'))

#=======================================================================================================

def sendText6(event):
    '''
    @心情回顧@
    當使用者點擊@心情回顧@後，
    會跳出選單讓使用者選擇要回顧的天數，
    有兩個選擇：今天、一周
    '''
    text = event.message.text
    try:
        line_bot_api.reply_message(event.reply_token,
                        TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='回顧天數',
                                text='請選擇要回顧的天數',
                                actions=[
                                    MessageTemplateAction(label='_今天_', text='_今天_'),
                                    MessageTemplateAction(label='_一周_', text='_一周_')
                                ])))
    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='發生錯誤！\n請聯絡我感恩!'))

#=======================================================================================================

def sendText7(event):
    '''
    @心情回顧@
    當使用者點擊@心情回顧@，可以返回當天的心情天氣
    連結MYSQL，索要userid、phq9_score、picture_score、diary_score分數加總
    '''
    line_userid = event.source.user_id
    # 資料庫設定
    db_settings = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'abc123',
        'db': 'line_catcher',
        'charset': 'utf8'
    }
    
        # 建立 connection 物件
    connection = pymysql.connect(**db_settings)
        # 製作一個指標，只要執行成功，就會回傳訊息
    with connection.cursor() as cursor:
        all_score = (
                "SELECT phq9.userID,(phq9.Q1+phq9.Q2+phq9.Q3+phq9.Q4+phq9.Q5+phq9.Q6+phq9.Q7+phq9.Q8+phq9.Q9) as phq9_score,\
                SUM(app_catcher_diary.text_score) / COUNT(current_date()-1) AS text_score,\
                CAST(app_catcher_diary.created_at AS DATE) AS diary_date,\
                app_catcher_picture.picture_score AS pictre_score,\
                CAST(app_catcher_picture.created_at AS DATE) AS picture_date\
                FROM phq9\
                LEFT OUTER JOIN app_catcher_diary ON phq9.UserID=app_catcher_diary.diary_uid\
                LEFT OUTER JOIN app_catcher_picture ON phq9.UserID=app_catcher_picture.picture_uid\
                where current_date()-1 = CAST(app_catcher_diary.created_at AS DATE)\
                AND current_date()-1 = CAST(app_catcher_picture.created_at AS DATE)\
                group by CAST(app_catcher_diary.created_at AS DATE), UserID"                
            )
        cursor.execute(all_score)
    connection.commit()
        
    result = cursor.fetchall()
 
    cursor.close()
    connection.close()
    print('MySQL connection is closed.')
    
    # 將數據tuple轉換為DataFrame
    col = ["userid", "phq9_score", "text_score", "text_date", "picture_score", "picture_date"]
    df = pd.DataFrame(list(map(list, result)), columns = col)
    # 核對使用者ID，將正確的數據抽取
    index = df[df.userid == line_userid]
    phq9_oneday = df.phq9_score.loc[0]
    text_oneday = df.text_score.loc[0]
    picture_oneday = df.picture_score.loc[0]
    
    try:
        if phq9_oneday < 5:          # 極輕度焦慮
            if text_oneday > 1.33 and picture_oneday == 1:     # 健康文本，開心臉
                text = "今天的心情天氣是晴朗艷陽天"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday > 1.33 and picture_oneday == 2:   # 健康文本，中性臉
                text = "今天的心情天氣是晴朗艷陽天"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday > 1.33 and picture_oneday == 3:   # 健康文本，傷心臉
                text = "今天的心情天氣是烏雲密布"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday <= 1.33 and picture_oneday == 3:  # 憂鬱文本，傷心臉
                text = "今天的心情天氣是烏雲密佈"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            else:
                text = "今天的心情天氣是多雲小日子"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
        
        elif 5 <= phq9_oneday < 10:  # 輕度焦慮
            if text_oneday > 1.33 and picture_oneday == 1:     # 健康文本，開心臉
                text = "今天的心情天氣是晴朗艷陽天"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday > 1.33 and picture_oneday == 2:   # 健康文本，中性臉
                text = "今天的心情天氣是晴朗艷陽天"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday > 1.33 and picture_oneday == 3:   # 健康文本，傷心臉
                text = "今天的心情天氣是烏雲密布"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday <= 1.33 and picture_oneday == 1:  # 憂鬱文本，生氣臉
                text = "今天的心情天氣是烏雲密佈"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday <= 1.33 and picture_oneday == 3:  # 憂鬱文本，傷心臉
                text = "今天的心情天氣是陰雨綿綿"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            else:
                text = "今天的心情天氣是多雲小日子"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))

        else:                        # 中重度焦慮
            if text_oneday > 1.33 and picture_oneday == 1:     # 健康文本，生氣臉
                text = "今天的心情天氣是狂風暴雨"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday > 1.33 and picture_oneday == 2:   # 健康文本，中性臉
                text = "今天的心情天氣是烏雲密佈"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday > 1.33 and picture_oneday == 3:   # 健康文本，傷心臉
                text = "今天的心情天氣是傾盆大雨"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday <= 1.33 and picture_oneday == 1:  # 憂鬱文本，生氣臉
                text = "今天的心情天氣是狂風暴雨"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday <= 1.33 and picture_oneday == 2:  # 憂鬱文本，中性臉
                text = "今天的心情天氣是烏雲密佈"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            elif text_oneday <= 1.33 and picture_oneday == 3:  # 憂鬱文本，傷心臉
                text = "今天的心情天氣是傾盆大雨"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
            else:
                text = "今天的心情天氣是多雲小日子"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！\n聯絡我感恩!'))    

#=======================================================================================================

def sendText8(event):
    '''
    _一周_
    時間不太夠，若之後要修改，請改動SQL的呼叫
    詳細的可以參考sendText7的部分
    '''
    try:
        text = '你的日記累積不到七天喔~~\n請再多寫幾天的日記再查詢優~~'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = text))
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！\n聯絡我感恩!'))

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

def svm_test(text):
    #建立function，將列表進行斷詞並用空格連接
    def segmentWord(cont):
        c = []
        for i in cont:
            a = list(jieba.cut(i))
            b = " ".join(a)
            c.append(b)
        return c
    # 呼叫模型
    clf = joblib.load('C:/Users/coco/Desktop/tibame_project/proj_catcher/module/nlp_clf.pkl')
    return clf.predict(segmentWord(text))

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
    
    
    # 建立 connection 物件
    connection = pymysql.connect(**db_settings)
    # 製作一個指標，只要執行成功，就會回傳訊息
    with connection.cursor() as cursor:
        # 添加數據到 MySQL，若PRIMARY KEY存在則忽略該行，若不存在，則添加新使用者的資料
        sql_insert_statement = "INSERT IGNORE INTO {}(TIMESTAMP, Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, UserID) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(tableName)
        for i in sql_data:
            cursor.execute(sql_insert_statement, i)              # 將資料的每一個 row 存進 MySQL
    connection.commit()
    #print("Table {} successfully updated.".format(tableName))    # 儲存變更成功回傳訊息
    # except pymysql.Error as error:
    #     connection.rollback()
    #     print("Error: {}. Table {} not updated!".format(error, tableName))
        
    #finally: 
    cursor.close()
    connection.close()
    print('MySQL connection is closed.')

data = GetSpreadsheetData('PHQ9', 0)
UpdateMySQLTable(data, 'PHQ9')

