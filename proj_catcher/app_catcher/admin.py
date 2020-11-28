from django.contrib import admin
from app_catcher.models import *    # 把 user 資料表加入顯示的表單

class UsersAdmin(admin.ModelAdmin):     # 將 uid 和 question 列為顯示的欄位
    list_display = ('uid',)
admin.site.register(Users, UsersAdmin)


class DiaryAdmin(admin.ModelAdmin):
    list_display = ('diary_id', 'text', 'created_at', )
admin.site.register(Diary, DiaryAdmin)


class PictureAdmin(admin.ModelAdmin):
    list_display = ('picture_id', 'created_at',)
admin.site.register(Picture, PictureAdmin)


# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('question_id', 'self_mood', 'self_sleep', 'self_sleep_status', 'self_eat', 'self_energy', 'created_at', 'uid',)
# admin.site.register(Question, QuestionAdmin)