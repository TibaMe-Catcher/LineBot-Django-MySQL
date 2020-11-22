from django.contrib import admin
from app_catcher.models import *    # 把 user 資料表加入顯示的表單

class usersAdmin(admin.ModelAdmin):     # 將 uid 和 question 列為顯示的欄位
    list_display = ('uid', 'datatest')
admin.site.register(users, usersAdmin)

'''
class diaryAdmin(admin.ModelAdmin):
    list_display = ('uid', 'diaryid', 'content', 'created_at')
admin.site.register(diary, diaryAdmin)
'''