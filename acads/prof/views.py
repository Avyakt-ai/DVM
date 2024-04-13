from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from .forms import CourseForm, StudentEnrollmentForm, AnnouncementForm, EvalForm, UserRegisterForm, CdcForm, BulkCdcForm
from student.models import Course, Student, CourseEnrollment, Announcement, Professor, Evaluative, EvalGrade, Dept, CDC
from mailjet_rest import Client
import base64
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404


def is_prof(user):
    return user.groups.filter(name='prof').exists()


def not_authorized(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'prof/not_authorized.html')


def prof_login(request):
    if request.user.is_authenticated:
        messages.success(request, "You have been logged out of your account. Login In Again!")
        logout(request)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        # Create something that if the login email is like of a prof then it will automatically send that user to the prof group.
        # CHECK BELOW LINES!!!!!!!!!!!!!!
        if user is not None and user.is_active and user.groups.filter(name='prof').exists():
            login(request, user)
            return redirect('prof_dash')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'prof/prof_login.html')


def prof_register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='prof')
            user.groups.add(group)

            dept = form.cleaned_data['dept']
            Professor.objects.create(user=user, dept=dept)
            messages.success(request, 'Your account has been created! You can now login')
            return redirect('prof_login')
    else:
        form = UserRegisterForm()
    return render(request, 'prof/register.html', {'form': form})


@user_passes_test(is_prof, login_url='not_authorized')
def prof_dash(request):
    return render(request, 'prof/prof_dash.html')


@user_passes_test(is_prof, login_url='not_authorized')
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New course added!!')
            return redirect('prof_dash')  # Redirect to the dashboard or any other desired page
    else:
        form = CourseForm()
    return render(request, 'prof/add_course.html', {'form': form})


@user_passes_test(is_prof, login_url='not_authorized')
def add_cdc(request):
    bulk_form = BulkCdcForm()
    if request.method == 'POST':
        form = CdcForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New CDC added!!')
            return redirect('add_cdc')
    else:
        form = CdcForm()
    return render(request, 'prof/add_cdc.html', {'form': form, 'bulk_form': bulk_form})


@user_passes_test(is_prof, login_url='not_authorized')
def your_courses(request):
    try:
        course = Course.objects.get(ic=request.user)
        students = CourseEnrollment.objects.filter(course=course)
    except Course.DoesNotExist:
        course = None
        students = None
    if request.method == 'POST':
        form = StudentEnrollmentForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student']
            student = Student.objects.get(id=student_id.id)
            if not CourseEnrollment.objects.filter(course=course, student=student):
                enrollment = CourseEnrollment.objects.create(
                    student=student,
                    course=course,
                )
                enrollment.save()
                messages.success(request, f'Successfully registered {student.user} for the Course')
            else:
                messages.success(request, 'Student is already registered for the Course')
            return redirect('your_courses')
    else:
        form = StudentEnrollmentForm()

    # all_student = Student.objects.
    return render(request, 'prof/your_courses.html', {
        'course': course,
        'students': students,
        'form': form,
    })


@user_passes_test(is_prof, login_url='not_authorized')
def create_announcement(request):
    try:
        course = Course.objects.get(ic=request.user)
        students = Student.objects.filter(course=course)
    except Course.DoesNotExist:
        course = None
        students = None
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.course_id = course.id
            announcement.prof_id = request.user.professor.id
            announcement.save()
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            image = request.FILES.get('image')
            pdf_files = request.FILES.get('file')
            encoded_image = None
            encoded_file = None
            if image:
                try:
                    # Read the image file and encode it as base64
                    with image.open() as f:
                        encoded_image = base64.b64encode(f.read()).decode('utf-8')
                except Exception as e:
                    print(f"Error encoding image: {e}")
            if pdf_files:
                try:
                    # Read the image file and encode it as base64
                    with pdf_files.open() as f:
                        encoded_file = base64.b64encode(f.read()).decode('utf-8')
                except Exception as e:
                    print(f"Error encoding image: {e}")
            mailjet_api_key = '7a162f536c5ec2bb964c0f390cf83703'
            mailjet_api_secret = '1a641f1b17487cb31b5124644b05918d'
            mailjet = Client(auth=(mailjet_api_key, mailjet_api_secret), version='v3.1')
            for student in students:
                if student.email:
                    student_email = student.email
                    subject = f'{course} Announcement'
                    message = f'{title}'
                    html_content = (
                        f'<h2>Dear {student},</h2><p>{content}</p>'
                        f'<br><br><p> Sent by Prof. <strong>{request.user.username}</strong></p><p> Contact <strong>DVM</strong> in case of any problems.</p><p>Phone no.: +91 8817928004</p>')
                    from_email = 'avyakt.seven@gmail.com'
                    to_email = student_email

                    data = {
                        'Messages': [
                            {
                                'From': {'Email': from_email, 'Name': 'DVM-Acads'},
                                'To': [{'Email': to_email, 'Name': student_email}],
                                'Subject': subject,
                                'TextPart': message,
                                'HTMLPart': html_content,
                                'Attachments': []
                            }
                        ]
                    }
                    if image and encoded_image:
                        attachment = {
                            'ContentType': image.content_type,  # Content type of the attachment
                            'Filename': image.name,  # Name of the attachment
                            'Base64Content': encoded_image
                        }
                        data['Messages'][0]['Attachments'].append(attachment)
                    if pdf_files:
                        attachment = {
                            'ContentType': pdf_files.content_type,  # Content type of the attachment
                            'Filename': pdf_files.name,  # Name of the attachment
                            'Base64Content': encoded_file
                        }
                        data['Messages'][0]['Attachments'].append(attachment)

                    result = mailjet.send.create(data=data)
                    print(result.status_code)
                    # print(result.json())
                else:
                    print(student, "has no email")
            messages.success(request, 'Announcement was sent successfully')
            return redirect('prof_dash')  # Redirect to the dashboard or any other desired page
    else:
        form = AnnouncementForm()
    return render(request, 'prof/create_announcement.html', {'form': form, 'course': course, })


@user_passes_test(is_prof, login_url='not_authorized')
def create_eval(request):
    try:
        course = Course.objects.get(ic=request.user)
        students = Student.objects.filter(course=course)
        existing_evals = Evaluative.objects.filter(course=course)
    except Course.DoesNotExist:
        course = None
        students = None
        existing_evals = None
    if request.method == 'POST':
        form = EvalForm(request.POST)
        if form.is_valid():
            evaluative = form.save(commit=False)
            evaluative.course_id = course.id
            evaluative.save()
            eval_announcement = Announcement.objects.create(
                course=course,
                prof=request.user.professor,
                title=f"{course.uid} Evaluative",
                content=form.cleaned_data['info'],

            )
            eval_announcement.save()
            info = form.cleaned_data['info']
            date = form.cleaned_data['date']
            mailjet_api_key = '7a162f536c5ec2bb964c0f390cf83703'
            mailjet_api_secret = '1a641f1b17487cb31b5124644b05918d'
            mailjet = Client(auth=(mailjet_api_key, mailjet_api_secret), version='v3.1')
            for student in students:
                eval_grade = EvalGrade.objects.create(
                    eval=evaluative,
                    student=student,
                )
                eval_grade.save()
                if student.email:
                    student_email = student.email
                    subject = f'{course} Evaluative'
                    message = f'{info}'
                    html_content = (
                        f'<h2>Dear {student},</h2>'
                        f'<p>{info}</p>'
                        f'<p><strong>Date and Time of Evaluative: {date}</strong></p>'
                        f'<br><br><p> Sent by Prof. <strong>{request.user.username}</strong></p><p> Contact <strong>DVM</strong> in case of any problems.</p><p>Phone no.: +91 8817928004</p>')
                    from_email = 'avyakt.seven@gmail.com'
                    to_email = student_email

                    data = {
                        'Messages': [
                            {
                                'From': {'Email': from_email, 'Name': 'DVM-Acads'},
                                'To': [{'Email': to_email, 'Name': student_email}],
                                'Subject': subject,
                                'TextPart': message,
                                'HTMLPart': html_content,
                                'Attachments': []
                            }
                        ]
                    }

                    result = mailjet.send.create(data=data)
                    print(result.status_code)
                else:
                    print(student, "has no email")

            messages.success(request, 'Evaluative was created successfully')
            return redirect('prof_dash')  # Redirect to the dashboard or any other desired page
    else:
        form = EvalForm()
    return render(request, 'prof/create_eval.html', {
        'form': form,
        'course': course,
        'students': students,
        'existing_evals': existing_evals,
    })


@user_passes_test(is_prof, login_url='not_authorized')
def create_grade(request, eval_id):
    evaluative = get_object_or_404(Evaluative, pk=eval_id)
    students = evaluative.evalgrade_set.all()

    if request.method == 'POST':
        for student in students:
            grade_field_name = f'grade_{student.id}'
            if grade_field_name in request.POST:
                student.grade = request.POST[grade_field_name]
                student.save()
                messages.success(request, f'{student} has been graded')
        return redirect('create_evaluative')

    return render(request, 'prof/create_grade.html', {'evaluative': evaluative, 'students': students})


@user_passes_test(is_prof, login_url='not_authorized')
def course_grade(request, student_id):
    student = Student.objects.get(pk=student_id)
    courses = student.courseenrollment_set.all()

    if request.method == 'POST':
        for course in courses:
            grade_field_name = f'grade_{course.id}'
            if grade_field_name in request.POST:
                if request.POST[grade_field_name]:
                    course.grade = request.POST[grade_field_name]
                    course.save()
        return redirect('grading')
    return render(request, 'prof/course_grade.html', {'student': student, 'courses': courses})


@user_passes_test(is_prof, login_url='not_authorized')
def course_stu(request):
    try:
        course = Course.objects.get(ic=request.user)
        students = Student.objects.filter(course=course)
    except Course.DoesNotExist:
        course = None
        students = None
    return render(request, 'prof/grading.html', {
        'students': students,
        'courses': course,
    })


def add_bulk_cdc(request):
    if request.method == 'POST':
        form = BulkCdcForm(request.POST)
        if form.is_valid():
            dept_group = form.cleaned_data['dept_group']
            course = form.cleaned_data['course']
            sem = form.cleaned_data['sem']
            departments_a = Dept.objects.filter(dept__startswith=dept_group)
            # Add CDC for each department and semester 1
            for department in departments_a:
                cdc_entry = CDC.objects.create(dept=department, course=course, sem=sem)
                cdc_entry.save()
            messages.success(request, f'CDC for group {dept_group} for course {course.uid} has been added successfully!')
    return redirect('add_cdc')
