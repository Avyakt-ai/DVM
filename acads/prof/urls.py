from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.prof_login, name='prof_login'),
    path('dash/', views.prof_dash, name='prof_dash'),
    path('register/', views.prof_register, name='prof_register'),
    path('not_authorized/', views.not_authorized, name='not_authorized'),
    path('add_course/', views.add_course, name='add_course'),
    path('your_courses', views.your_courses, name='your_courses'),
    path('create-announcement/', views.create_announcement, name='create_announcement'),
    path('create-evaluative', views.create_eval, name='create_evaluative'),
    path('eval-grade/<int:eval_id>/', views.create_grade, name='create_grade'),
    path('course-grade/<int:student_id>/', views.course_grade, name='course_grade'),
    path('grading/', views.course_stu, name='grading'),
]
