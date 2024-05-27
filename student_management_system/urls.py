"""student_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views,admin_views,teacher_views,student_views
urlpatterns = [
    path('admin/', admin.site.urls),
    #all user interface
    path('', views.HOME,name=''),
    path('contract', views.CONTRACT,name='contract'),
    path('about', views.ABOUT,name='about'),

    path('clear-notifications', views.clear_notifications, name='clear_notifications'),
    
    path('base/', views.BASE,name='base'),
    path('join_now', views.JOIN_NOW,name='join_now'),

    #login path
    path('login', views.LOGIN,name='login'),
    path('faceID-login', views.FACE_ID_LOGIN,name='faceID-login'),
    path('face-id-dologin', views.FACE_ID_DOLOGIN,name='face-id-dologin'),
    path('dologin', views.dologin,name='dologin'), 
    path('dologout', views.dologout,name='logout'),

    #profile update 
    path('profile', views.PROFILE,name='profile'),
    path('profile/update', views.PROFILE_UPDATE,name='profile_update'),
    
    #this is admin panel url
    path('admin-home', admin_views.Home,name='admin_home'),


    path('admin-student-add', admin_views.STUDENT_ADD,name='admin-student-add'),
    path('admin-student-view', admin_views.STUDENT_VIEW,name='admin-student-view'),
    path('admin-student-edit/<str:id>', admin_views.STUDENT_EDIT,name='admin-student-edit'),
    path('admin-student-update', admin_views.STUDENT_UPDATE,name='admin-student-update'),
    path('admin-student-delete/<str:admin>', admin_views.STUDENT_DELETE,name='admin-student-delete'),

    path('admin-teacher-add', admin_views.TEACHER_ADD,name='admin-teacher-add'),
    path('admin-teacher-view', admin_views.TEACHER_VIEW,name='admin-teacher-view'),
    path('admin-teacher-edit/<str:id>', admin_views.TEACHER_EDIT,name='admin-teacher-edit'),
    path('admin-teacher-update', admin_views.TEACHER_UPDATE,name='admin-teacher-update'),
    path('admin-teacher-delete/<str:admin>', admin_views.TEACHER_DELETE,name='admin-teacher-delete'),


    path('admin-class-add', admin_views.CLASS_ADD,name='admin-class-add'),
    path('admin-class-view', admin_views.CLASS_VIEW,name='admin-class-view'),
    path('admin-class-edit/<str:id>', admin_views.CLASS_EDIT,name='admin-class-edit'),
    path('admin-class-update', admin_views.CLASS_UPDATE,name='admin-class-update'),
    path('admin-class-delete/<str:id>', admin_views.CLASS_DELETE,name='admin-class-delete'),



    path('admin-course-add', admin_views.COURSE_ADD,name='admin-course-add'),
    path('admin-course-view', admin_views.COURSE_VIEW,name='admin-course-view'),
    path('admin-course-edit/<str:id>', admin_views.COURSE_EDIT,name='admin-course-edit'),
    path('admin-course-update', admin_views.COURSE_UPDATE,name='admin-course-update'),
    path('admin-course-delete/<str:id>', admin_views.COURSE_DELETE,name='admin-course-delete'),


    path('admin-subject-add', admin_views.SUBJECT_ADD,name='admin-subject-add'),
    path('admin-subject-view', admin_views.SUBJECT_VIEW,name='admin-subject-view'),
    path('admin-subject-edit/<str:id>', admin_views.SUBJECT_EDIT,name='admin-subject-edit'),
    path('admin-subject-update', admin_views.SUBJECT_UPDATE,name='admin-subject-update'),
    path('admin-subject-delete/<str:id>', admin_views.SUBJECT_DELETE,name='admin-subject-delete'),


    path('admin-session-add', admin_views.SESSION_ADD,name='admin-session-add'),
    path('admin-session-view', admin_views.SESSION_VIEW,name='admin-session-view'),
    path('admin-session-edit/<str:id>', admin_views.SESSION_EDIT,name='admin-session-edit'),
    path('admin-session-update', admin_views.SESSION_UPDATE,name='admin-session-update'),
    path('admin-session-delete/<str:id>', admin_views.SESSION_DELETE,name='admin-session-delete'),


    path('admin-practice-exam-add', admin_views.PRACTICE_EXAM_ADD,name='admin-practice-exam-add'),
    path('admin-practice-exam-view', admin_views.PRACTICE_EXAM_VIEW,name='admin-practice-exam-view'),
    path('admin-practice-exam-save', admin_views.PRACTICE_EXAM_SAVE,name='admin-practice-exam-save'),
    path('admin-practice-exam-delete/<str:id>', admin_views.PRACTICE_EXAM_DELETE,name='admin-practice-exam-delete'),
    path('admin-practice-exam-edit/<str:id>', admin_views.PRACTICE_EXAM_EDIT,name='admin-practice-exam-edit'),
    path('admin-practice-exam-update', admin_views.PRACTICE_EXAM_UPDATE,name='admin-practice-exam-update'),


    path('admin-add-practice-exam-question', admin_views.ADD_PRACTICE_EXAM_QUESTION,name='admin-add-practice-exam-question'),
    path('admin-save-practice-exam-question', admin_views.SAVE_PRACTICE_EXAM_QUESTION,name='admin-save-practice-exam-question'),
    path('admin-view-practice-exam-question', admin_views.VIEW_PRACTICE_EXAM_QUESTION_FILTER,name='admin-view-practice-exam-question'),
    path('admin-view-practice-exam-question/<str:id>', admin_views.VIEW_PRACTICE_EXAM_QUESTION,name='admin-view-practice-exam-question'),
    path('admin-edit-practice-exam-question/<str:id>', admin_views.EDIT_PRACTICE_EXAM_QUESTION,name='admin-edit-practice-exam-question'),
    path('admin-update-practice-exam-question', admin_views.UPDATE_PRACTICE_EXAM_QUESTION,name='admin-update-practice-exam-question'),
    path('admin-delete-peactice-exam-question/<str:id>', admin_views.DELETE_PRACTICE_EXAM_QUESTION,name='admin-delete-practice-exam-question'),


    path('admin-live-exam-add', admin_views.LIVE_EXAM_ADD,name='admin-live-exam-add'),
    path('admin-live-exam-save', admin_views.LIVE_EXAM_SAVE,name='admin-live-exam-save'),
    path('admin-live-exam-view', admin_views.LIVE_EXAM_VIEW,name='admin-live-exam-view'),
    path('admin-live-exam-edit/<str:id>', admin_views.LIVE_EXAM_EDIT,name='admin-live-exam-edit'),
    path('admin-live-exam-update', admin_views.LIVE_EXAM_UPDATE,name='admin-live-exam-update'),
    path('admin-live-exam-delete/<str:id>', admin_views.LIVE_EXAM_DELETE,name='admin-live-exam-delete'),


    path('admin-add-live-exam-question', admin_views.ADD_LIVE_EXAM_QUESTION,name='admin-add-live-exam-question'),
    path('admin-save-live-exam-question', admin_views.SAVE_LIVE_EXAM_QUESTION,name='admin-save-live-exam-question'),
    path('admin-view-live-exam-question', admin_views.VIEW_LIVE_EXAM_QUESTION_FILTER,name='admin-view-live-exam-question'),
    path('admin-view-live-exam-question/<str:id>', admin_views.VIEW_LIVE_EXAM_QUESTION,name='admin-view-live-exam-question'),
    path('admin-edit-live-exam-question/<str:id>', admin_views.EDIT_LIVE_EXAM_QUESTION,name='admin-edit-live-exam-question'),
    path('admin-update-live-exam-question', admin_views.UPDATE_LIVE_EXAM_QUESTION,name='admin-update-live-exam-question'),
    path('admin-delete-live-exam-question/<str:id>', admin_views.DELETE_LIVE_EXAM_QUESTION,name='admin-delete-live-exam-question'),


    path('admin-star-student-add', admin_views.STAR_STUDENT_ADD,name='admin-star-student-add'),
    path('admin-star-student-edit/<str:id>', admin_views.STAR_STUDENT_EDIT,name='admin-star-student-edit'),
    path('admin-star-student-update', admin_views.STAR_STUDENT_UPDATE,name='admin-star-student-update'),
    path('admin-star-student-delete/<str:id>', admin_views.STAR_STUDENT_DELETE,name='admin-star-student-delete'),



    path('admin-student-activity-add', admin_views.STUDENT_ACTIVITY_ADD,name='admin-student-activity-add'),
    path('admin-student-activity-view', admin_views.STUDENT_ACTIVITY_VIEW,name='admin-student-activity-view'),
    path('admin-student-activity-edit/<str:id>', admin_views.STUDENT_ACTIVITY_EDIT,name='admin-student-activity-edit'),
    path('admin-student-activity-update', admin_views.STUDENT_ACTIVITY_UPDATE,name='admin-student-activity-update'),
    path('admin-student-activity-delete/<str:id>', admin_views.STUDENT_ACTIVITY_DELETE,name='admin-student-activity-delete'),


    path('admin-teacher-send-notification', admin_views.TEACHER_SEND_NOTIFICATION,name='admin-teacher-send-notification'),
    path('admin-teacher-save-notification', admin_views.TEACHER_SAVE_NOTIFICATION,name='admin-teacher-save-notification'),


    path('admin-teacher-feedback', admin_views.TEACHER_Feedback,name='admin-teacher-feedback'),
    path('admin-teacher-save', admin_views.TEACHER_Feedback_SAVE,name='admin-teacher-feedback-save'),
    

    path('admin-student-send-notification', admin_views.STUDENT_SEND_NOTIFICATION,name='admin-student-send-notification'),
    path('admin-student-save-notification', admin_views.STUDENT_SAVE_NOTIFICATION,name='admin-student-save-notification'),


    path('admin-view-attendance', admin_views.ADMIN_VIEW_ATTENDANCE,name='admin-view-attendance'),
    

    path('admin-delete-all-expire-student', admin_views.ADMIN_DELETE_ALL_EXPIRE_STUDENT,name='admin-delete-all-expire-student'),
    
    path('admin-upgrade-student-class', admin_views.UPGRADE_CLASS,name='admin-upgrade-student-class'),


    
    path('admin-add-online-live-class', admin_views.ADD_ONLINE_LIVE_CLASS, name='admin-add-online-live-class'),
    path('admin-view-online-live-class', admin_views.VIEW_ONLINE_LIVE_CLASS, name='admin-view-online-live-class'),
    path('admin-start-online-live-class/<int:id>', admin_views.START_ONLINE_LIVE_CLASS, name='admin-start-online-live-class'),

    #this is teacher panel url
    path('teacher-home', teacher_views.HOME,name='teacher-home'),
    path('teacher-notification', teacher_views.NOTIFICATION,name='teacher-notification'),
    path('teacher/mark_as_done/<str:status>', teacher_views.TEACHER_NOTIFICATION_MARK_AS_DONE,name='teacher-mark-as-done'),

    path('teacher-feedback', teacher_views.TEACHER_FEEDBACK,name='teacher-feedback'),
    path('teacher-feedback-save', teacher_views.TEACHER_FEEDBACK_SAVE,name='teacher-feedback-save'),

    path('teacher-student-feedback', teacher_views.STUDENT_FEEDBACK,name='teacher-student-feedback'),
    path('teacher-student-save', teacher_views.STUDENT_FEEDBACK_SAVE,name='teacher-student-feedback-save'),


    path('teacher-take-attendance', teacher_views.TEACHER_TAKE_ATTENDANCE,name='teacher-take-attendance'),
    path('teacher-save-attendance', teacher_views.TEACHER_SAVE_ATTENDANCE,name='teacher-save-attendance'),
    path('teacher-view-attendance', teacher_views.TEACHER_VIEW_ATTENDANCE,name='teacher-view-attendance'),
    
    path('teacher-add-notice', teacher_views.TEACHER_ADD_NOTICE,name='teacher-add-notice'),
  


    path('teacher-add-result', teacher_views.TEACHER_ADD_RESULT,name='teacher-add-result'),
    path('teacher-save-result', teacher_views.TEACHER_SAVE_RESULT,name='teacher-save-result'),
    path('teacher-view-result', teacher_views.TEACHER_VIEW_RESULT,name='teacher-view-result'),
    path('teacher-show-result/<str:id>/<int:exam_id>', teacher_views.TEACHER_SHOW_RESULT,name='teacher-show-result'),
    path('teacher-edit-result/<str:id>', teacher_views.TEACHER_EDIT_RESULT,name='teacher-edit-result'),
    path('admin-update-result', teacher_views.TEACHER_UPDATE_RESULT,name='teacher-update-result'),
    path('teacher-delete-result/<str:id>', teacher_views.TEACHER_DELETE_RESULT,name='teacher-delete-result'),



    path('teacher-student-send-notification', teacher_views.STUDENT_SEND_NOTIFICATION,name='teacher-student-send-notification'),
    path('teacher-student-save-notification', teacher_views.STUDENT_SAVE_NOTIFICATION,name='teacher-student-save-notification'),




    #this is student panel url
    path('student-home', student_views.HOME,name='student-home'),
    path('student-notification', student_views.NOTIFICATION,name='student-notification'),
    path('student/mark_as_done/<str:status>', student_views.STUDENT_NOTIFICATION_MARK_AS_DONE,name='student-mark-as-done'),


    path('student-feedback',student_views.STUDENT_FEEDBACK,name='student-feedback'),
    path('student-feedback-save', student_views.STUDENT_FEEDBACK_SAVE,name='student-feedback-save'),

    path('student-view-attendance',student_views.STUDENT_VIEW_ATTENDANCE,name='student-view-attendance'),

    path('student-view-school-exam-result',student_views.STUDENT_VIEW_SCHOOL_EXAM_RESULT,name='student-view-school-exam-result'),

    path('student-practice-exam',student_views.STUDENT_PRACTICE_EXAM,name='student-practice-exam'),
    path('student-take-practice-exam/<str:id>',student_views.STUDENT_TAKE_PRACTICE_EXAM,name='student-take-practice-exam'),
    path('student-start-practice-exam/<str:id>',student_views.STUDENT_START_PRACTICE_EXAM,name='student-start-practice-exam'),
    path('student-practice-exam-calculate-marks',student_views.STUDENT_PRACTICE_EXAM_CALCULATE_MARKS,name='student-practice-exam-calculate-marks'),
    path('student-practice-exam-mark',student_views.STUDENT_PRACTICE_EXAM_MARK,name='student-practice-exam-mark'),
    path('student-view-practice-exam-mark/<str:id>',student_views.STUDENT_VIEW_PRACTICE_EXAM_MARK,name='student-view-practice-exam-mark'),
    path('student-merit-position/<int:id>', student_views.STUDENT_MERIT_POSITION, name='student-merit-position'),


    path('student-live-exam',student_views.STUDENT_LIVE_EXAM,name='student-live-exam'),
    path('student-take-live-exam/<str:id>',student_views.STUDENT_TAKE_LIVE_EXAM,name='student-take-live-exam'),
    path('student-take-live-exam-home/<str:id>',student_views.STUDENT_TAKE_LIVE_EXAM_HOME,name='student-take-live-exam-home'),
    path('student-start-live-exam/<str:id>',student_views.STUDENT_START_LIVE_EXAM,name='student-start-live-exam'),
    path('student-live-exam-calculate-marks',student_views.STUDENT_LIVE_EXAM_CALCULATE_MARKS,name='student-live-exam-calculate-marks'),
    path('student-live-exam-mark',student_views.STUDENT_LIVE_EXAM_MARK,name='student-live-exam-mark'),
    path('student-view-live-exam-mark/<str:id>',student_views.STUDENT_VIEW_LIVE_EXAM_MARK,name='student-view-live-exam-mark'),



    path('student-view-online-live-class', student_views.VIEW_ONLINE_LIVE_CLASS, name='student-view-online-live-class'),
    path('student-join-online-live-class/<int:id>/', student_views.JOIN_ONLINE_LIVE_CLASS, name='student-join-online-live-class'),
    path('student-join-online-live-class-home/<int:id>/', student_views.JOIN_ONLINE_LIVE_CLASS_HOME, name='student-join-online-live-class-home'),


    path('student-performance',student_views.STUDENT_PERFORMANCE_COURSE,name='student-performance'),
    path('student-performance/<int:id>',student_views.STUDENT_PERFORMANCE,name='student-performance'),
    path('student-performance-view-question/<int:id>',student_views.STUDENT_PERFORMANCE_VIEW_QUESTION,name='student-performance-view-question'),

    path('student-past-exam',student_views.STUDENT_PAST_EXAM,name='student-past-exam'),

    path('student-view-online-exam-result/<int:id>',student_views.STUDENT_VIEW_ONLINE_EXAM_RESULT,name='student-view-online-exam-result'),

    path('student-ask-question',student_views.STUDENT_ASK_QUESTION,name='student-ask-question'),


    
] + static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
