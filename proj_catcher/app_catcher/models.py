from django.db import models

# Line ID 資料收集
# class Users(models.Model):
#     uid = models.CharField(max_length=50, null=False)      # uid 欄位儲存使用者的 Line ID
#     created_at = models.DateTimeField(auto_now_add=True)
#     phq_score = models.CharField(max_length=50, null=False)
    
#     def __str__(self):
#         return self.uid


# 使用者 Diary 紀錄
class Diary(models.Model):
    diary_id = models.CharField(blank=False, max_length=15, default=None)
    text = models.TextField(blank=True, default=None)
    text_score = models.FloatField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    diary_uid = models.CharField(max_length=50, null=False, default=None)

    def __str__(self):
        return self.diary_id


# 使用者 Pirture 紀錄
class Picture(models.Model):
    picture_id = models.CharField(max_length=50, null=False, default=None)
    picture_score = models.FloatField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    picture_uid = models.CharField(max_length=50, null=False, default=None)

    def __str__(self):
        return self.pirture_id



# 使用者 Surprise 推薦
class Surprise(models.Model):
    sur_id = models.CharField(blank=False, max_length=15, default=None)
    category = models.TextField(blank=True, default=None)
    mood = models.TextField(blank=True, default=None)
    title = models.TextField(blank=True, default=None)
    content = models.TextField(blank=True, max_length=300, default=None)

    def __str__(self):
        return self.sur_id



