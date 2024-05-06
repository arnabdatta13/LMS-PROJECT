from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class UserModel(UserAdmin):
    list_display= ['username','user_type','first_name','last_name','mobile_number']
admin.site.register(CustomUser)
admin.site.register(Course)
admin.site.register(Class)
admin.site.register(Session_Year)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Practice_Exam)
admin.site.register(Question)
admin.site.register(Online_Exam_Result)
admin.site.register(Star_student)
admin.site.register(Teacher_Notification)
admin.site.register(Teacher_Feedback)
admin.site.register(Student_Notification)
admin.site.register(Student_Feedback)
admin.site.register(Attendance)
admin.site.register(Attendance_Report)
admin.site.register(StudentResult)
admin.site.register(Add_Notice)
admin.site.register(OnlineLiveClass)