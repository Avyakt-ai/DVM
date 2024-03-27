from django.contrib import admin

# Register your models here.
from .models import Student, CourseEnrollment, Course, Dept, Professor, CDC, Announcement, Registration, EvalGrade, Evaluative

admin.site.register(Student)
admin.site.register(CourseEnrollment)
admin.site.register(Course)
admin.site.register(Dept)
admin.site.register(Professor)
admin.site.register(CDC)
admin.site.register(Announcement)
admin.site.register(Registration)
admin.site.register(EvalGrade)
admin.site.register(Evaluative)
