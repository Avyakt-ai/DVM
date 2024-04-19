from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Registration(models.Model):
    register = models.BooleanField(default=False)


# Well the below is more like branch it is just named Dept
class Dept(models.Model):
    class TypeChoices(models.TextChoices):
        BE_CHEMICAL = 'A1' 'B.E. Chemical'
        BE_CIVIL = 'A2' 'B.E. Civil'
        BE_ELECTRICAL = 'A3' 'B.E. Electrical & Electronics'
        BE_MECHANICAL = 'A4' 'B.E. Mechanical'
        B_PHARMA = 'A5' 'B. Pharma'
        BE_CS = 'A7' 'B.E. Computer Science'
        BE_ELECTRONICS = 'A8' 'B.E. Electronics and Instrumentation'
        BE_BIOTECH = 'A9' 'B.E. Biotechnology'
        BE_ELECTRONICS_COMM = 'AA' 'B.E. Electronics & Communication'
        BE_MANUFACTURING = 'AB' 'B.E. Manufacturing Engineering'
        M_SC_BIO = 'B1' 'M.Sc. Biological Sciences'
        M_SC_CHEM = 'B2' 'M.Sc. Chemistry'
        M_SC_ECON = 'B3' 'M.Sc. Economics'
        M_SC_MATH = 'B4' 'M.Sc. Mathematics'
        M_SC_PHYSICS = 'B5' 'M.Sc. Physics'
        M_SC_GENERAL = 'C2' 'M.Sc. General Studies'
        M_SC_TECH = 'C5' 'M.Sc. Engineering Technology'
        M_SC_INFO_SYS = 'C6' 'M.Sc. Information Systems'
        M_SC_FINANCE = 'C7' 'M.Sc. Finance'
    dept = models.CharField(max_length=50, choices=TypeChoices.choices)

    def __str__(self):
        return f"{self.dept}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey('Dept', on_delete=models.CASCADE, null=True)
    cdc_added = models.BooleanField(default=False)  # At the end of each sem it should be changed back to False.
    sem = models.IntegerField(default=1)
    email = models.EmailField(max_length=254, default='')

    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs):
        if not self.email:  # If email field is empty
            self.email = self.user.email  # Set email field to user's email address
        super().save(*args, **kwargs)


class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user.username}"


# $$$$$$$$ REMEMBER TO REMOVE NULL=TRUE FOR IC HERE $$$$$$$$$$$
class Course(models.Model):
    student = models.ManyToManyField(Student, through='CourseEnrollment')
    name = models.CharField(max_length=100)
    uid = models.CharField(max_length=10, null=True)
    ic = models.OneToOneField(User, on_delete=models.CASCADE, null=True, limit_choices_to={'groups__name': 'prof'})
    dept = models.ManyToManyField(Dept, through='CDC')
    units = models.IntegerField(default=3)
    image = models.ImageField(default='default_image.png', upload_to='course_image')

    def __str__(self):
        return f"{self.uid}"


# Through table for student course and student
class CourseEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    grade = models.FloatField(null=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    sem = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.course.uid} for {self.student}"


# Through table for compulsory courses for departments
class CDC(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    sem = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.course.uid} CDC of {self.dept} for sem {self.sem}"


class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    prof = models.ForeignKey(Professor, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True)
    content = models.TextField(null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='announcement_image', null=True, blank=True)
    file = models.FileField(upload_to='pdf_files', blank=True, null=True)

    def __str__(self):
        return self.title


class Evaluative(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    info = models.CharField(max_length=400, null=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.course} eval on {self.date}"


class EvalGrade(models.Model):
    eval = models.ForeignKey(Evaluative, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    grade = models.FloatField(null=True, validators=[MinValueValidator(0), MaxValueValidator(10)])

    def __str__(self):
        return f"{self.student} in {self.eval.course.uid}"
