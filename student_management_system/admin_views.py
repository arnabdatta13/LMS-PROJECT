from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from app.models import Course,Session_Year,CustomUser,Student,Teacher,Subject,Star_student,Student_activity,Teacher_Notification,Teacher_Feedback,Student_Notification,Student_Feedback,Attendance_Report,Attendance,Class,Add_Notice,Question,Practice_Exam,StudentResult
from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SESSION_UPDATE(request):
    if request.method == "POST":
        session_id = request.POST.get('session_id')
        session_year_start = request.POST.get('session_year_start')
        session_year_end = request.POST.get('session_year_end')

        try:
            session = Session_Year.objects.get(id=session_id)
        except Session_Year.DoesNotExist:
            raise Http404("Session not found")

        session.session_start = session_year_start
        session.session_end = session_year_end
        session.save()

        messages.success(request, 'Session was successfully updated')
        return redirect('admin-session-view')


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def Home(request):
    student_count = Student.objects.all().count()
    teacher_count= Teacher.objects.all().count()
    course_count = Course.objects.all().count()
    exam_count = Practice_Exam.objects.all().count()


    student_gender_male = Student.objects.filter(gender= 'Male').count()
    student_gender_female = Student.objects.filter(gender= 'Female').count()

    star_student = Star_student.objects.all()
    student_activity= Student_activity.objects.all()
    notice = Add_Notice.objects.all()

    
    context = {
        'student_count':student_count,
        'teacher_count':teacher_count,
        'course_count':course_count,
        'exam_count':exam_count,
        'student_gender_male':student_gender_male,
        'student_gender_female': student_gender_female,
        'star_student':star_student,
        'student_activity':student_activity,
        'notice':notice,
    }
    return render(request, 'admin/home.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_ADD (request):
    class1= Class.objects.all()
    session_year =Session_Year.objects.all()

    if request.method == "POST":
        profile_pic=request.FILES.get('profile_pic')
        first_name =request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        username =request.POST.get('username')
        password =request.POST.get('password')
        fathers_name =request.POST.get('fathers_name')
        mathers_name =request.POST.get('mathers_name')
        
        roll_number =request.POST.get('roll')
        class_id =request.POST.get('class_id')
        session_year_id =request.POST.get('session_year_id')
        gender =request.POST.get('gender')
        phone_number =request.POST.get('phone_number')
        address =request.POST.get('address')

        
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request,'Username Is Already Taken')
            return redirect('admin-student-add')
        else:
            user= CustomUser(
                first_name= first_name,
                last_name =last_name,
                username=username,
                profile_pic=profile_pic,
                user_type = 3,
                


            )
            user.set_password(password)
            user.save()

            class1=Class.objects.get(id=class_id)
            session_year = Session_Year.objects.get(id=session_year_id)

            student = Student(
                admin= user,
                address =address,
                fathers_name=fathers_name,
                mothers_name=mathers_name,
                session_year_id= session_year,
                class_id=class1,
                gender=gender,
                
                roll_number=roll_number,
                phone_number=phone_number,
            )
            student.save()
            messages.success(request, user.first_name + " " + user.last_name + " Are Successfully Added")
            return redirect('admin-student-add')
            
            
    
    context = {
        'class': class1,
        'session_year':session_year,
    }
    
    return render(request, 'admin/add_student.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_VIEW(request):
    student = Student.objects.all()
    classes = Class.objects.all()  # Fetch all classes from the database

    search_query = request.GET.get('search_query', '')  
    class_filter = request.GET.get('class_filter', '')
    roll_number_query = request.GET.get('roll_number_filter', '') 

    if search_query:
        student = student.filter(
            Q(admin__first_name__icontains=search_query) | 
            Q(admin__last_name__icontains=search_query)
        )
    if class_filter:
        student = student.filter(class_id=class_filter)
    if roll_number_query:
        student = student.filter(roll_number=roll_number_query)


    context = {
        'student':student,
        'search_query': search_query,
        'classes': classes,
        'selected_class': class_filter,  # Pass selected class filter to template
        'roll_number_query': roll_number_query,
    }
    return render(request,'admin/view_student.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_EDIT(request,id):
    student = Student.objects.filter(id=id)
    class1= Class.objects.all()
    session_year = Session_Year.objects.all()
    

    context={
        'student':student,
        'class':class1,
        'session_year':session_year,
    }
    return render(request, 'admin/edit_student.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_UPDATE(request):
    if request.method == 'POST':
        student_id =request.POST.get('student_id')
        
        profile_pic= request.FILES.get('profile_pic')
        first_name =request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        username =request.POST.get('username')
        password =request.POST.get('password')
        fathers_name =request.POST.get('fathers_name')
        mathers_name =request.POST.get('mathers_name')
        
        roll_number =request.POST.get('roll')
        class_id =request.POST.get('class_id')
        session_year_id =request.POST.get('session_year_id')
        gender =request.POST.get('gender')
        phone_number =request.POST.get('phone_number')
        address =request.POST.get('address')

        if class_id == 'Select Course':
            messages.error(request, 'Please select a valid course.')
            return redirect('admin-student-edit', id=student_id)  # Redirect back to the edit page
        if session_year_id == 'Select Session Year':
            messages.error(request, 'Please select a valid Session Year.')
            return redirect('admin-student-edit', id=student_id)  # Redirect back to the edit page

        user= CustomUser.objects.get(id=student_id)
        
        if first_name != None and first_name != "":
            user.first_name=first_name
            
        if last_name != None and last_name != "":
            user.last_name=last_name

        if username != None and username != "":
            user.username=username

            
        if profile_pic != None and profile_pic != "":
            user.profile_pic=profile_pic

            #customuser.username= username
        if password != None and password != "":
            user.set_password(password)
        user.save()

        student = Student.objects.get(admin= student_id)

        if fathers_name != None and fathers_name != "":
            student.fathers_name=fathers_name
        
        if mathers_name != None and mathers_name != "":
            student.mothers_name=mathers_name

        

        if roll_number != None and roll_number != "":
            student.roll_number=roll_number
        
        if gender != None and gender != "":
            student.gender=gender

        if phone_number != None and phone_number != "":
            student.phone_number=phone_number

        if address != None and address != "":
            student.address=address
        
        class1 = Class.objects.get(id=class_id)

        student.class_id=class1

        session_year = Session_Year.objects.get(id=session_year_id)

        student.session_year_id = session_year

        student.save()
        messages.success(request,'Record Are Successfully Updated')
        return redirect('admin-student-view')

        
        

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_DELETE(request,admin):
    student = CustomUser.objects.get(id= admin)
    student.delete()
    messages.success(request,'Record Are Successfully Deleted')
    return redirect('admin-student-view')


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def CLASS_ADD(request):
    if request.method== "POST":
        class_name= request.POST.get('class_name')
        class1 = Class(
            name = class_name,
        )
        class1.save()
        messages.success(request,'Class Are Successfully Created')
        return redirect('admin-class-add')
    
    return render(request,'admin/add_class.html')


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def CLASS_VIEW(request):
    class1 = Class.objects.all()


    context = {
        'class': class1,

    }
    return render(request,'admin/view_class.html',context)

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def CLASS_EDIT(request,id):
    class1 = Class.objects.get(id = id)

    context = {
        'class':class1,
    }
    return render(request,'admin/edit_class.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def CLASS_UPDATE(request):
    if request.method == "POST":
        name= request.POST.get('class_name')
        class_id = request.POST.get('class_id')

        class1 = Class.objects.get(id = class_id)
        class1.name= name
        class1.save()
        messages.success(request,'Class Are Successfully Updated')
        return redirect('admin-class-view')

        
    return render(request,'admin/edit_class.html')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def CLASS_DELETE(request,id):
    class1 = Class.objects.get(id = id)
    class1.delete()

    messages.success(request,'Class Are Successfully Deleted')

    return redirect('admin-class-view')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def COURSE_ADD(request):
    class1= Class.objects.all()
    if request.method== "POST":
        course_name= request.POST.get('course_name')
        class1 =request.POST.get('class_id')

        user_class = Class.objects.get(id=class1)
        course = Course(
            name = course_name,
            class1=user_class,
        )
        course.save()
        messages.success(request,'Course Are Successfully Created')
        return redirect('admin-course-add')
    
    context = {
        'class':class1,
    }
    return render(request,'admin/add_course.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def COURSE_VIEW(request):
    course = Course.objects.all()


    context = {
        'course': course,

    }
    return render(request,'admin/view_course.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def COURSE_EDIT(request,id):
    course = Course.objects.get(id = id)
    class1= Class.objects.all()
    context = {
        'course':course,
        'class':class1,
    }
    return render(request,'admin/edit_course.html',context)

def COURSE_UPDATE(request):
    if request.method == "POST":
        name= request.POST.get('course_name')
        class_id= request.POST.get('class_id')
        course_id = request.POST.get('course_id')

        course = Course.objects.get(id = course_id)
        class1=Class.objects.get(id=class_id)
        course.name= name
        course.class1=class1
        course.save()
        messages.success(request,'Course Are Successfully Updated')
        return redirect('admin-course-view')

        
    return render(request,'admin/edit_course.html')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def COURSE_DELETE(request,id):
    course = Course.objects.get(id= id)
    course.delete()

    messages.success(request,'Course Are Successfully Deleted')

    return redirect('admin-course-view')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def TEACHER_ADD(request):
    if request.method=="POST":
        profile_pic= request.FILES.get('profile_pic')
        first_name =request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        username =request.POST.get('username')
        password =request.POST.get('password')
        gender =request.POST.get('gender')
        phone_number =request.POST.get('phone_number')
        address =request.POST.get('address')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request,"Username Is Already Taken")
            return redirect('admin-teacher-add')
        else:
            user = CustomUser(first_name=first_name,last_name=last_name,profile_pic=profile_pic,user_type=2,username=username)
            user.set_password(password)
            user.save()

            teacher =Teacher(
                admin = user,
                phone_number=phone_number,
                gender=gender,
                address=address
            )
            teacher.save()
            messages.success(request,"Teacher Are Successfully Added")
            return redirect('admin-teacher-add')
    return render(request,'admin/add_teacher.html')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def TEACHER_VIEW(request):
    teacher = Teacher.objects.all()
    context ={
        'teacher':teacher,
    }
    return render(request,'admin/view_teacher.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def TEACHER_EDIT(request,id):
    teacher = Teacher.objects.get(id=id)

    context = {
        'teacher':teacher,
    }
    return render(request,'admin/edit_teacher.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def TEACHER_UPDATE(request):
    if request.method == "POST":
        teacher_id = request.POST.get('teacher_id')
        profile_pic= request.FILES.get('profile_pic')
        first_name =request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        username =request.POST.get('username')
        password =request.POST.get('password')
        gender =request.POST.get('gender')
        phone_number =request.POST.get('phone_number')
        address =request.POST.get('address')

        user = CustomUser.objects.get(id= teacher_id)
        user.username=username
        user.first_name=first_name
        user.last_name=last_name
        if profile_pic != None and profile_pic != "":
            user.profile_pic=profile_pic

            
        if password != None and password != "":
            user.set_password(password)


        user.save()

        teacher = Teacher.objects.get(admin= teacher_id)
        teacher.gender=gender
        teacher.phone_number=phone_number
        teacher.address=address

        teacher.save()
        messages.success(request,'Teacher Is Successfully Updated')
        return redirect('admin-teacher-view')
        
        
    return render(request,'admin/edit_teacher.html')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def TEACHER_DELETE(request,admin):
    teacher = CustomUser.objects.get(id= admin)
    teacher.delete()
    messages.success(request,'Racord Are Successfully Deleted')
    return redirect('admin-teacher-view')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SUBJECT_ADD(request):
    class1 = Class.objects.all()
    teacher = Teacher.objects.all()

    if request.method == "POST":
        subject_name= request.POST.get('subject_name')
        class_id= request.POST.get('class_id')
        teacher_id= request.POST.get('teacher_id')

        class1 = Class.objects.get(id=class_id)
        teacher = Teacher.objects.get(id = teacher_id)

        subject = Subject(
            name= subject_name,
            class1 = class1,
            teacher= teacher,
        )
        subject.save()
        messages.success(request,'Subjects Are Successfully Added')
        return redirect('admin-subject-add')
    
    context = {
        'class':class1,
        'teacher':teacher,
    }
    return render(request,'admin/add_subject.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SUBJECT_VIEW(request):
    subject = Subject.objects.all()
    
   
    context = {
        'subject':subject,
        
    }
    return render(request,'admin/view_subject.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SUBJECT_EDIT(request,id):
    subject = Subject.objects.get(id= id)
    class1 = Class.objects.all()
    teacher = Teacher.objects.all()


    context = {
        'subject':subject,
        'class':class1,
        "teacher":teacher,
    }
    return render(request,'admin/edit_subject.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SUBJECT_UPDATE(request):
    if request.method == "POST":
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject_name')
        class_id = request.POST.get('class_id')
        teacher_id = request.POST.get('teacher_id')

        # Check if 'Select Course' was chosen
        if class_id == 'Select Class':
            messages.error(request, 'Please select a valid class.')
            return redirect('admin-subject-edit', id=subject_id)  # Redirect back to the edit page
        if teacher_id == 'Select Teacher':
            messages.error(request, 'Please select a valid Teacher.')
            return redirect('admin-subject-edit', id=subject_id)  # Redirect back to the edit page

        try:
            # Attempt to fetch the Course and Teacher objects
            class1 = Class.objects.get(id=class_id)
            teacher = Teacher.objects.get(id=teacher_id)

            # Update the Subject object
            subject = Subject.objects.get(id=subject_id)
            subject.name = subject_name
            subject.class1 = class1
            subject.teacher = teacher
            subject.save()

            messages.success(request, 'Subject was successfully updated.')
            return redirect('admin-subject-view')
        except (ValueError, Course.DoesNotExist, Teacher.DoesNotExist, Subject.DoesNotExist):
            messages.error(request, 'Invalid data or subject not found.')
            return redirect('admin-subject-edit', id=subject_id)
    


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SUBJECT_DELETE(request,id):
    subject = Subject.objects.filter(id = id)
    subject.delete()
    messages.success(request,'Subject Are Successfully Deleted')
    return redirect('admin-subject-view')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SESSION_ADD(request):
    if request.method == "POST":
        session_year_start=request.POST.get('session_year_start')
         
        session_year_end=request.POST.get('session_year_end')

        session = Session_Year(
            session_start= session_year_start,
            session_end = session_year_end,
        )
        session.save()
        messages.success(request,'Session Are Successfully Created')
        return redirect('admin-session-add')

    return render(request,'admin/add_session.html')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SESSION_VIEW(request):
    session = Session_Year.objects.all()

    context= {
        'session':session,
    }
    return render(request,'admin/view_session.html',context)


def SESSION_EDIT(request,id):
    session = Session_Year.objects.filter(id = id)

    context= {
        'session':session,
    }
    
    return render(request,'admin/edit_session.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SESSION_UPDATE(request):
    if request.method == "POST":
        session_id = request.POST.get('session_id')
        session_year_start = request.POST.get('session_year_start')
        session_year_end = request.POST.get('session_year_end')

        try:
            session = Session_Year.objects.get(id=session_id)
        except Session_Year.DoesNotExist:
            raise Http404("Session not found")

        session.session_start = session_year_start
        session.session_end = session_year_end
        session.save()

        messages.success(request, 'Session was successfully updated')
        return redirect('admin-session-view')    



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SESSION_DELETE(request,id):
    session = Session_Year.objects.filter(id = id)
    session.delete()
    messages.success(request,'Session Are Successfully Deleted')
    return redirect('admin-session-view')





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def PRACTICE_EXAM_ADD(request):
    class1 = Class.objects.all()
    action = request.GET.get('action')

    get_class = None
  
    subject = None
    course = None

    if action is not None:
        if request.method=="POST":
            class_id = request.POST.get('class_id')

            get_class = Class.objects.get(id=class_id)

            class1 = Class.objects.filter(id= class_id)
            subject = Subject.objects.filter(class1=get_class)

            course = Course.objects.filter(class1=get_class)

    context = {
        
        'class':class1,
        'action':action,
        'get_class':get_class,
      
        'subject': subject,
        
        'course':course,

    }
    return render(request,'admin/add_practice_exam.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def PRACTICE_EXAM_SAVE(request):
    if request.method == "POST":

        class_id= request.POST.get('class_id')
        exam_name= request.POST.get('exam_name')
        total_questions= request.POST.get('total_question')
        total_marks= request.POST.get('total_number')
        
        course_id= request.POST.get('course_id')
        subject_id= request.POST.get('subject_id')

        class1= Class.objects.get(id=class_id)
        course = Course.objects.get(id=course_id)
        subject = Subject.objects.get(id=subject_id)

        exam = Practice_Exam(
            exam_name= exam_name,
            total_questions=total_questions,
            total_marks=total_marks,
            class_id=class1,
            course = course,
            subject= subject,
        )
        exam.save()
        messages.success(request,'Exam Are Successfully Added')
        return redirect('admin-practice-exam-add')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def PRACTICE_EXAM_EDIT(request,id):
    exam = Practice_Exam.objects.filter(id = id)

    exam_id = Practice_Exam.objects.get(id=id)


    class_id = exam_id.class_id

    course = Course.objects.filter(class1=class_id)

    subject = Subject.objects.filter(class1=class_id)

    context= {
        'exam':exam,
        'class':class_id,
        'course':course,
        'subject':subject,

    }
    
    return render(request,'admin/edit_practice_exam.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def PRACTICE_EXAM_UPDATE(request):
    if request.method == "POST":
        exam_id = request.POST.get('exam_id')
        class_id= request.POST.get('class_id')
        exam_name= request.POST.get('exam_name')
        total_questions= request.POST.get('total_question')
        total_marks= request.POST.get('total_number')
        
        course_id= request.POST.get('course_id')
        subject_id= request.POST.get('subject_id')

        exam = Practice_Exam.objects.get(id = exam_id)
        class1= Class.objects.get(id=class_id)
        course = Course.objects.get(id=course_id)
        subject = Subject.objects.get(id=subject_id)

        exam.exam_name=exam_name
        exam.total_questions=total_questions
        exam.total_marks=total_marks
        exam.class_id=class1
        exam.course=course
        exam.subject=subject
        exam.save()
        messages.success(request,'Practice Exam Are Successfully Updated')
        return redirect('admin-peactice-exam-view')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def PRACTICE_EXAM_DELETE(request,id):
    exam = Practice_Exam.objects.get(id = id)
    exam.delete()

    messages.success(request,'Exam Are Successfully Deleted')

    return redirect('admin-practice-exam-view')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def PRACTICE_EXAM_VIEW(request):
    exam = Practice_Exam.objects.all()
    course= Course.objects.all()
    selected_course = request.GET.get('course_filter', '') 
    if selected_course:
        exam = exam.filter(course=selected_course)
 

    context= {
        'exam':exam,
        'course':course,
        'selected_course': selected_course,
    }
    return render(request,'admin/view_practice_exam.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def ADD_QUESTION(request):
    class1 = Class.objects.all()

    action = request.GET.get('action')

    get_class = None
 
    subject = None
    course = None
    exam = None

    if action is not None:
        if request.method=="POST":
            class_id = request.POST.get('class_id')

            get_class = Class.objects.get(id=class_id)

            class1 = Class.objects.filter(id= class_id)
            exam = Practice_Exam.objects.filter(class_id=class_id)
            


    context = {
        
        'class':class1,
        'action':action,
        'get_class':get_class,
        
        'subject': subject,
        
        'course':course,
        'exam':exam,

    }
    return render(request,'admin/add_question.html',context)





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def SAVE_QUESTION(request):
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        marks = request.POST.get('mark')
        question_text = request.POST.get('question')
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        option4 = request.POST.get('option4')
        answer = request.POST.get('answer')

        # Assuming exam_id exists in Exam model, validate other fields as per your requirements
        
        # Create and save the question object
        question = Question.objects.create(
            exam_id=exam_id,
            marks=marks,
            question=question_text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            answer=answer
        )
        # Optionally, you can redirect the user to a success page or perform any other action

        messages.success(request,'Question are added successfully')
        return redirect('admin-add-question')
    


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def VIEW_QUESTION(request):
    question = Question.objects.all()
    
    context = {
        'question':question,
    }

    return render(request,'admin/view_question.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def EDIT_QUESTION(request,id):

    exam = Practice_Exam.objects.all()
    question = Question.objects.filter(id = id)


    context = {
        'exam':exam,
        'question':question,
    }
    return render(request,'admin/edit_question.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def DELETE_QUESTION(request,id):

    question = Question.objects.get(id = id)
    question.delete()

    messages.success(request,'Question are successfully deleted.')

    return redirect('admin-view-question')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STAR_STUDENT_ADD(request):
    class1=Class.objects.all()
    if request.method == "POST":
        student_name=request.POST.get('name')
         
        user_class=request.POST.get('class')
        roll=request.POST.get('roll')
        mark=request.POST.get('marks')
        persentage=request.POST.get('percentage')
        year=request.POST.get('year')

        star_student = Star_student(
            student_name=student_name,
            user_class=user_class,
            roll=roll,
            mark=mark,
            persentage=persentage,
            year=year,
        )
        star_student.save()
        messages.success(request,'Star Student Are Successfully Created')
        return redirect('admin-star-student-add')
    
    context = {
        'class':class1,
    }
    
    return render(request,'admin/add_star_student.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STAR_STUDENT_EDIT(request,id):
    star_student = Star_student.objects.filter(id = id)
    class1 = Class.objects.all()
    context= {
        'star_student':star_student,
        'class':class1,
    }
    
    return render(request,'admin/edit_star_student.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STAR_STUDENT_UPDATE(request):
    if request.method == "POST":
        star_student_id = request.POST.get('star_student_id')
        student_name=request.POST.get('name')
         
        user_class=request.POST.get('class')
        roll=request.POST.get('roll')
        mark=request.POST.get('marks')
        persentage=request.POST.get('percentage')
        year=request.POST.get('year')

        try:
            star_student = Star_student.objects.get(id=star_student_id)
        except Star_student.DoesNotExist:
            raise Http404("Star Student not found")

        star_student.student_name = student_name
        star_student.user_class = user_class
        star_student.roll = roll
        star_student.mark = mark
        star_student.persentage = persentage
        star_student.year = year
        star_student.save()

        messages.success(request, 'Star Student was successfully updated')
        return redirect('admin_home')    




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STAR_STUDENT_DELETE(request,id):
    star_student = Star_student.objects.get(id= id)
    star_student.delete()

    messages.success(request,'Star Student Are Successfully Deleted')

    return redirect('admin_home')


def STUDENT_ACTIVITY_ADD(request):
    if request.method == "POST":
        date = request.POST.get('date')
        description = request.POST.get('description')

        if not description:
            # Handle the case where description is empty
            messages.error(request, 'Description is required.')
            return redirect('admin-student-activity-add')

        student_activity = Student_activity(
            date=date,
            description=description,
        )
        student_activity.save()
        messages.success(request, 'Student Activity Are Successfully Created')
        return redirect('admin-student-activity-add')

    
    return render(request,'admin/add_student_activity.html')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_ACTIVITY_VIEW(request):
    student_activity= Student_activity.objects.all()

    context = {
        'student_activity':student_activity,
    }



    return render(request,'admin/view_student_activity.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_ACTIVITY_EDIT(request,id):
    student_activity= Student_activity.objects.get(id = id)

    context = {
        'student_activity':student_activity,
    }
    return render(request,'admin/edit_student_activity.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_ACTIVITY_UPDATE(request):
        if request.method == "POST":
            date = request.POST.get('date')
            description = request.POST.get('description')
            student_activity_id = request.POST.get('student_activity_id')

            student_activity = Student_activity.objects.get(id = student_activity_id)

            student_activity.date = date
            student_activity.description = description
            student_activity.save()
            messages.success(request,'Student Activity Are Successfully Updated')
            return redirect('admin_home')


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_ACTIVITY_DELETE(request,id):
    student_activity = Student_activity.objects.get(id= id)
    student_activity.delete()

    messages.success(request,'Student Activity Are Successfully Deleted')

    return redirect('admin-student-activity-view')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def TEACHER_SEND_NOTIFICATION(request):
    teacher = Teacher.objects.all()

    see_notification =  Teacher_Notification.objects.all().order_by('-id')[0:8]

    context= {
        'teacher': teacher,
        'see_notification': see_notification,
    }
    return render(request,'admin/teacher_notification.html',context)





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def TEACHER_SAVE_NOTIFICATION(request):
    if request.method=="POST":

        teacher_id= request.POST.get('teacher_id')
        message= request.POST.get('message')

        #print(teacher_id,message)


        teacher = Teacher.objects.get(admin=teacher_id)

        notification = Teacher_Notification(
            teacher_id=teacher,
            message=message,
        )
        notification.save()
        messages.success(request,'Notification Are Successfully Send')

    
    return redirect('admin-teacher-send-notification')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def TEACHER_Feedback(request):
    teacher_feedback = Teacher_Feedback.objects.all()

    context = {
        'teacher_feedback':teacher_feedback,
    }
    return render(request,"admin/teacher_feedback.html",context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def TEACHER_Feedback_SAVE(request):
    if request.method== "POST":
        feedback_id= request.POST.get('feedback_id')
        feedback_reply = request.POST.get('feedback_reply')

      

        feedback = Teacher_Feedback.objects.get(id=feedback_id)

        feedback.feedback_reply=feedback_reply
        feedback.save()

        return redirect('admin-teacher-feedback')
    



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_SEND_NOTIFICATION(request):
    student = Student.objects.all()

    notification = Student_Notification.objects.all()
    
    
    selected_class = request.GET.get('class_filter', '')  # Get the selected class from the request
    roll_number_query = request.GET.get('roll_number_filter', '') 

    
    # Filter students by class if a class is selected
    if selected_class:
        student = student.filter(user_class=selected_class)

    # Filter students by roll number if a roll number query is provided
    if roll_number_query:
        student = student.filter(roll_number=roll_number_query)


    
    context = {
        'student':student,
        'notification':notification,
        'selected_class': selected_class,
    }
    return render(request,'admin/student_notification.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def STUDENT_SAVE_NOTIFICATION(request):
    if request.method == "POST":

        student_id = request.POST.get('student_id')
        message = request.POST.get('message')

        student = Student.objects.get( admin= student_id)

        student_notification = Student_Notification(
            student_id= student,
            message=message,
        )
        student_notification.save()

        messages.success(request,'Student Notification Are Successfully Sent')
        return redirect('admin-student-send-notification')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def ADMIN_VIEW_ATTENDANCE(request):
    session_year = Session_Year.objects.all()
    class1 = Class.objects.all()

    action = request.GET.get('action')

    get_class = None
    get_session_year= None

    attendance_date=None
    attendance_report=None
   
    students = None
    student_attendance_report = set()
    if action is not None:
        if request.method == "POST":
            class_id = request.POST.get('class_id')
            session_year_id = request.POST.get('session_year_id')
            attendance_date= request.POST.get('attendance_date')

            get_class = Class.objects.get(id=class_id)
            get_session_year = Session_Year.objects.get(id=session_year_id)

            attendance = Attendance.objects.filter(class_id=get_class, attendance_date=attendance_date)
            for i in attendance:
                attendance_id = i.id
                attendance_report = Attendance_Report.objects.filter(attendance_id=attendance_id)

            # Fetch students belonging to the selected class
            students = Student.objects.filter(class_id=get_class)
            if attendance_report:
                student_attendance_report = set(report.student_id for report in attendance_report)
            else:
                student_attendance_report = set()

    context = {
        'class': class1,
        'session_year': session_year,
        'action': action,
        'get_class': get_class,
        'get_session_year': get_session_year,
        'attendance_date': attendance_date,
        'attendance_report': attendance_report,
        'students': students,  # Pass students to the template
        'student_attendance_report':student_attendance_report
    }
    return render(request, 'admin/view_attendance.html', context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def ADMIN_DELETE_ALL_EXPIRE_STUDENT(request):
    if request.method == "POST":
        current_date = timezone.now().date()

        # Get all session years whose end date is less than the current date
        expired_session_years = Session_Year.objects.filter(session_end__lt=current_date)

        # Iterate over each expired session year
        for session_year in expired_session_years:
            # Get all students associated with this expired session year
            expired_students = Student.objects.filter(session_year_id=session_year)
            # Delete each expired student
            expired_students.delete()

        messages.success(request,'All Expire Student Are Successfully Deleted')
        return redirect('admin-student-view')



