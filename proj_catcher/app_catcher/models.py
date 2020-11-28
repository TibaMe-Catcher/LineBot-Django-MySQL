from django.db import models

#Line ID 資料收集
class Users(models.Model):
    uid = models.CharField(max_length=50, null=False)      # uid 欄位儲存使用者的 Line ID
    #datatest = models.CharField(max_length=50, null=False)
    
    def __str__(self):
        return self.uid


#使用者 Diary 紀錄
class Diary(models.Model):
    diary_id = models.CharField(blank=False, max_length=15, default=None)
    text = models.TextField(blank=True, default=None)
    #text_score = models.FloatField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    #diary_uid = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.diary_id


# 使用者 Pirture 紀錄
class Picture(models.Model):
    picture_id = models.CharField(max_length=50, null=False, default=None)
    #picture_score = models.FloatField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    #picture_uid = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.pirture_id


# # 使用者每日主觀評估
# class Question(models.Model):
#     question_id = models.CharField(max_length=50, null=False, default=None)
#     self_mood = models.IntegerField(default='0', null=False)          # 給自己昨天的心情幾分?
#     self_sleep = models.IntegerField(default='0', null=False)         # 昨晚睡了幾個小時?
#     self_sleep_status = models.IntegerField(default='0', null=False)  # 睡眠狀態如何?
#     self_eat = models.IntegerField(default='0', null=False)           # 昨天吃了幾餐?
#     self_energy = models.IntegerField(default='0', null=False)        # 昨天體力狀況?
#     created_at = models.DateTimeField(auto_now_add=True)              # 填寫問卷時間
#     uid = models.CharField(max_length=50, null=False)                 # 使用者是誰?

#     def __str__(self):
#         return self.question_id


# # 使用者 PHQ9 紀錄
# class phq9(models.Model):
#     uid = models.CharField(max_length=50, default=None, null=False)
#     num01 = models.IntegerField(default='0', null=False)
#     num02 = models.IntegerField(default='0', null=False)
#     num03 = models.IntegerField(default='0', null=False)
#     num04 = models.IntegerField(default='0', null=False)
#     num05 = models.IntegerField(default='0', null=False)
#     num06 = models.IntegerField(default='0', null=False)
#     num07 = models.IntegerField(default='0', null=False)
#     num08 = models.IntegerField(default='0', null=False)
#     num09 = models.IntegerField(default='0', null=False)
#     phqall = models.IntegerField(default='0', null=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.uid
