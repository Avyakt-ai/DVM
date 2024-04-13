from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.student_login, name='student_login'),
    path('dash/', views.student_dash, name='student_dashboard'),
    path('register/', views.student_register, name='student_register'),
    path('register_course/<int:course_id>/', views.register_course, name='register_course'),
    path('unregister_course/<int:course_id>/', views.unregister_course, name='unregister_course'),
    path('course-registration/', views.course_registration, name='course_registration'),
    path('add_cdc/', views.add_all_cdc, name='add_all_cdc'),
    path('select_department/', views.select_department, name='select_department'),
    path('course-detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('grades/', views.grades, name='grades'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),

    # path('accounts/google/login/', views.custom_login, name='google_login'),
]
