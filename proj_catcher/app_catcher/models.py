from django.db import models

# Line ID 資料收集
class users(models.Model):
    uid = models.CharField(max_length=50, null=False)      # uid 欄位儲存使用者的 Line ID
    datatest = models.CharField(max_length=50, null=False)
    
    def __str__(self):
        return self.uid


# 使用者 PHQ9紀錄
class phq9(models.Model):
    phq_id = models.CharField(max_length=50, default='0', null=False)
    num01 = models.CharField(max_length=1, default='0', null=False)
    num02 = models.CharField(max_length=1, default='0', null=False)
    num03 = models.CharField(max_length=1, default='0', null=False)
    num04 = models.CharField(max_length=1, default='0', null=False)
    num05 = models.CharField(max_length=1, default='0', null=False)
    num06 = models.CharField(max_length=1, default='0', null=False)
    num07 = models.CharField(max_length=1, default='0', null=False)
    num08 = models.CharField(max_length=1, default='0', null=False)
    num09 = models.CharField(max_length=1, default='0', null=False)

    def __str__(self):
        return self.phq_id