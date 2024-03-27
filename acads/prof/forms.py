from django import forms
from student.models import Course, Student, Announcement, Evaluative, EvalGrade
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from student.models import Dept


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'uid', 'ic', 'units', 'image']


class StudentEnrollmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StudentEnrollmentForm, self).__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(department__isnull=False)

    student = forms.ModelChoiceField(queryset=Student.objects.none())


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'image', 'file']


class EvalForm(forms.ModelForm):
    class Meta:
        model = Evaluative
        fields = ['course', 'info', 'date']


class UserRegisterForm(UserCreationForm):
    dept = forms.ModelChoiceField(queryset=Dept.objects.all(), empty_label=None)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'dept']


class GradeForm(forms.ModelForm):
    class Meta:
        model = EvalGrade
        fields = ['student', 'grade']