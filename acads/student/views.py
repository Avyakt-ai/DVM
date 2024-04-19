from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from .models import Course, CourseEnrollment, CDC, Announcement, Evaluative, EvalGrade, Student
from .forms import DepartmentSelectionForm, UserRegisterForm
from reportlab.pdfgen import canvas
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse


def is_stud(user):
    return not user.groups.filter(name='prof').exists()


def not_authorized(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'prof/not_authorized.html')


def type_of_user(request):
    if request.user.is_authenticated:
        messages.success(request, 'You have been logged out of your account. Login In Again!')
        logout(request)
    return render(request, 'student/type_of_user.html')


def student_register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Your account has been created! You can now login')
            form.save()
            return redirect('student_login')
    else:
        form = UserRegisterForm()
    return render(request, 'student/register.html', {'form': form})


def student_login(request):
    if request.user.is_authenticated:
        messages.success(request, 'You have been logged out of your account. Login In Again!')
        logout(request)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'student/student_login.html')


@user_passes_test(is_stud, login_url='not_authorized')
def student_dash(request):
    # If user belongs to a department then only continue.
    if request.user.student.department:
        enrolled_courses = CourseEnrollment.objects.filter(student=request.user.student)
        return render(request, 'student/student_dash.html', {
            'enrolled_courses': enrolled_courses,
        })
    else:
        return redirect('select_department')


def course_registration(request):
    # Get all courses
    all_courses = Course.objects.all()
    cdc_list = CDC.objects.filter(dept=request.user.student.department, sem=request.user.student.sem)
    # Get enrolled courses for the current semester
    enrolled_courses = CourseEnrollment.objects.filter(student=request.user.student, sem=request.user.student.sem).values_list('course', flat=True)
    # Filter available courses by excluding enrolled courses
    available_courses = all_courses.exclude(id__in=enrolled_courses)
    current_units = 0
    dept = request.user.student.department
    required_units = 0
    if dept.dept.startswith('A'):
        if request.user.student.sem == 1:
            required_units = 20
        elif request.user.student.sem == 2:
            required_units = 17
        elif request.user.student.sem == 3:
            required_units = 20
        elif request.user.student.sem == 4:
            required_units = 20
        elif request.user.student.sem == 5:
            required_units = 17
        elif request.user.student.sem == 6:
            required_units = 21
        elif request.user.student.sem == 7:
            required_units = 18
        elif request.user.student.sem == 8:
            required_units = 25
    elif dept.dept.startswith('B'):
        if request.user.student.sem == 1:
            required_units = 19
        elif request.user.student.sem == 2:
            required_units = 18
        elif request.user.student.sem == 3:
            required_units = 17
        elif request.user.student.sem == 4:
            required_units = 20
        elif request.user.student.sem == 5:
            required_units = 21
        elif request.user.student.sem == 6:
            required_units = 21
        elif request.user.student.sem == 7:
            required_units = 30
        elif request.user.student.sem == 8:
            required_units = 5
        elif request.user.student.sem == 9:
            required_units = 5
        elif request.user.student.sem == 10:
            required_units = 5
    else:
        required_units = 37
    enrolled_courses = CourseEnrollment.objects.filter(student=request.user.student, sem=request.user.student.sem, grade=None)
    for c in enrolled_courses:
        current_units += c.course.units
    disable_registration = 0
    if current_units > required_units:
        disable_registration = 1
    elif current_units == required_units:
        disable_registration = 2
    return render(request, 'student/student_registration.html', {
        'available_courses': available_courses,
        'enrolled_courses': enrolled_courses,
        'cdc_list': cdc_list,
        'current_units': current_units,
        'required_units': required_units,
        'disable_registration': disable_registration,
    })


def register_course(request, course_id):
    if request.method == 'POST':
        # Get the selected course
        course = Course.objects.get(pk=course_id)
        # Get the current student
        student = request.user.student
        # Enroll the student in the course
        CourseEnrollment.objects.create(student=student, course=course, sem=request.user.student.sem)
        return redirect('course_registration')
    else:
        return redirect('course_registration')


def unregister_course(request, course_id):
    if request.method == 'POST':
        # Get the selected course
        course = Course.objects.get(pk=course_id)
        # Get the current student
        student = request.user.student
        # Enroll the student in the course
        enrollment = CourseEnrollment.objects.get(student=student, course=course, sem=request.user.student.sem)
        enrollment.delete()
        return redirect('course_registration')
    else:
        return redirect('course_registration')


def add_all_cdc(request):
    cdc_courses = CDC.objects.filter(dept=request.user.student.department, sem=request.user.student.sem)
    already_enrolled = CourseEnrollment.objects.filter(student=request.user.student, sem=request.user.student.sem)
    already_enrolled_course_ids = already_enrolled.values_list('course__id', flat=True)
    for c in cdc_courses:
        if c.course.id not in already_enrolled_course_ids:
            CourseEnrollment.objects.create(student=request.user.student, course=c.course)
    request.user.student.cdc_added = True
    request.user.student.save()
    messages.success(request, f'You Have been enrolled for all the cdc for department {request.user.student.department} for semester {request.user.student.sem}')
    return redirect('course_registration')


def select_department(request):
    if request.method == 'POST':
        form = DepartmentSelectionForm(request.POST)
        if form.is_valid():
            department = form.cleaned_data['department']
            sem = form.cleaned_data['sem']  # Retrieve semester from form
            student = request.user.student
            student.department = department
            student.sem = sem  # Save semester
            student.save()
            return redirect('student_dashboard')
    else:
        form = DepartmentSelectionForm()
    print(form)
    return render(request, 'student/select_dept.html', {'form': form})


def course_detail(request, course_id):
    # Retrieve the course object from the database based on the provided course_id
    course = get_object_or_404(Course, id=course_id)
    course_enrollments = CourseEnrollment.objects.get(student=request.user.student, course=course)

    announcements = Announcement.objects.filter(course=course)
    return render(request, 'student/course_detail.html', {
        'course': course,
        'course_enrollments': course_enrollments,
        'announcements': announcements,
    })


def grades(request):
    evals = EvalGrade.objects.filter(student=request.user.student)
    return render(request, 'student/grades.html', {
        'evals': evals,
    })


def generate_pdf(request):
    # Assuming you have a way to identify the current student, let's say through request.user
    student = request.user.student  # Assuming Student model has a OneToOneField with User

    # Fetch the courses and grades for the current student
    course_enrollments = CourseEnrollment.objects.filter(student=student)
    student_units = 0
    total_units = 0
    for i in course_enrollments:
        if i.grade:
            student_units += i.grade * i.course.units
        if i.course.units:
            total_units += i.course.units
    if total_units == 0:
        cgpa = 0
    else:
        cgpa = student_units / total_units

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="grades.pdf"'

    pdf = canvas.Canvas(response)
    pdf.setTitle('Grades Report')

    pdf.drawString(200, 800, 'Grades Report')
    y_position = 760
    for enrollment in course_enrollments:
        pdf.drawString(100, y_position, f"Course: {enrollment.course.name}, Grade: {enrollment.grade}")
        y_position -= 20
    pdf.drawString(100, 400, f"CGPA: {cgpa}")
    pdf.save()
    return response
