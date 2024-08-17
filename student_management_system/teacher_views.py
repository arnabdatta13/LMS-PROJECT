from django.shortcuts import render,redirect
from app.models import Course,Session_Year,CustomUser,Student,Teacher,Subject,Star_student,Student_activity,Teacher_Notification,Teacher_Feedback,Student_Notification,Attendance_Report,Attendance,Class,Add_Notice,PracticeExamQuestion,Practice_Exam,OnlineLiveClass,Live_Exam,LiveExamMCQQuestion,Live_Exam_Result,LiveExamWrittenQuestion,LiveExamStudentWrittenAnswer,Live_Exam_Written_Result,Student_Feedback,SchoolExamStudentResult,School_Official_Exam
from django.contrib import messages
from operator import attrgetter
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.http import Http404




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def HOME(request):
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
    return render(request, 'teacher/home.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
            return redirect('teacher-student-add')
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
            return redirect('teacher-student-add')
            
            
    
    context = {
        'class': class1,
        'session_year':session_year,
    }
    
    return render(request, 'admin/add_student.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
            return redirect('teacher-student-edit', id=student_id)  # Redirect back to the edit page
        if session_year_id == 'Select Session Year':
            messages.error(request, 'Please select a valid Session Year.')
            return redirect('teacher-student-edit', id=student_id)  # Redirect back to the edit page

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
        return redirect('teacher-student-view')

        
        

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STUDENT_DELETE(request,admin):
    student = CustomUser.objects.get(id= admin)
    student.delete()
    messages.success(request,'Record Are Successfully Deleted')
    return redirect('teacher-student-view')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def NOTIFICATION(request):
    teacher = Teacher.objects.filter(admin=request.user.id)
    for i in teacher:
        teacher_id =i.id

        notification = Teacher_Notification.objects.filter(teacher_id=teacher_id)

        context = {
            'notification':notification,
        }
        return render(request,'teacher/notification.html',context)
    


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_NOTIFICATION_MARK_AS_DONE(request,status):
    notification = Teacher_Notification.objects.get(id= status)
    notification.status=1
    notification.save()


    return redirect('teacher-notification')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_FEEDBACK(request):
    teacher_id = Teacher.objects.get(admin = request.user.id)

    feedback_history = Teacher_Feedback.objects.filter(teacher_id= teacher_id)

    context= {
        'feedback_history': feedback_history,
    }
    return render(request,'teacher/feedback.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_FEEDBACK_SAVE(request):
    if request.method=="POST":
        feedback = request.POST.get('feedback')

        teacher = Teacher.objects.get(admin=request.user.id)

        feedback= Teacher_Feedback(
            teacher_id = teacher,
            feedback = feedback,
            feedback_reply =""

        )
        feedback.save()
    
        return redirect('teacher-feedback')
    



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STUDENT_FEEDBACK(request):
    student_feedback = Student_Feedback.objects.all()

    context = {
        'student_feedback':student_feedback,
    }
    return render(request,"teacher/student_feedback.html",context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STUDENT_FEEDBACK_SAVE(request):
    if request.method== "POST":
        feedback_id= request.POST.get('feedback_id')
        feedback_reply = request.POST.get('feedback_reply')

      

        feedback = Student_Feedback.objects.get(id=feedback_id)

        feedback.feedback_reply=feedback_reply
        feedback.save()

        return redirect('teacher-student-feedback')
    


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_TAKE_ATTENDANCE(request):

    session_year = Session_Year.objects.all()
    class1 = Class.objects.all()

    action = request.GET.get('action')
    get_class = None
    get_session_year= None
    student=None
    if action is not None:
        if request.method == "POST":
            
            class_id = request.POST.get('class_id')
            session_year_id = request.POST.get('session_year_id')

            get_class = Class.objects.get(id =class_id)
            get_session_year = Session_Year.objects.get(id=session_year_id)

            course = Class.objects.filter(id= class_id)
            for i in course:
                student_id = i.id
                student= Student.objects.filter(class_id=student_id)

    context = {
        'class':class1,
        'session_year':session_year,
        'get_class':get_class,
        'get_session_year':get_session_year,
        'action':action,
        'student':student,
    }


    return render(request,'teacher/take_attendance.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_SAVE_ATTENDANCE(request):
    if request.method == "POST":
        class_id = request.POST.get('class_id')
        session_year_id = request.POST.get('session_year_id')
        attendance_date = request.POST.get('attendance_date')
        student_ids = request.POST.getlist('student_id')  # Get a list of selected student IDs

        get_class = Class.objects.get(id=class_id)
        get_session_year = Session_Year.objects.get(id=session_year_id)

        attendance = Attendance(
            class_id=get_class,
            attendance_date=attendance_date,
            session_year_id=get_session_year,
        )
        attendance.save()

        for student_id in student_ids:
            int_stud_id = int(student_id)
            p_student = Student.objects.get(id=int_stud_id)

            # Create the Attendance_Report object
            attendance_report = Attendance_Report(
                student_id=p_student,
                attendance_id=attendance,
            )
            attendance_report.save()

    return redirect('teacher-take-attendance')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_VIEW_ATTENDANCE(request):
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
    return render(request, 'teacher/view_attendance.html', context)







@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_ADD_RESULT(request):

    class1 = Class.objects.all()

    result = SchoolExamStudentResult.objects.all()

    action = request.GET.get('action')

    get_class = None
    student=None
    subject = None
    exam = None
    if action is not None:
        if request.method=="POST":
            class_id = request.POST.get('class_id')

            get_class = Class.objects.get(id=class_id)

            class1 = Class.objects.filter(id= class_id)
            subject = Subject.objects.filter(class1=get_class)
            exam = School_Official_Exam.objects.filter(class_id=get_class)
            for i in class1:
                student_id = i.id
                student = Student.objects.filter(
                    class_id=student_id,
                    studentresult__assignment_mark__isnull=True,
                    studentresult__exam_mark__isnull=True,
                ).order_by('roll_number')
                subject = Subject.objects.filter(class1=student_id)


    context = {
        'exam':exam,
        'class':class1,
        'action':action,
        'get_class':get_class,
        'student':student,
        'subject': subject,
        'result':result,

    }
    return render(request,'teacher/add_result.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_SAVE_RESULT(request):
    if request.method == "POST":
      
        subject_id = request.POST.get('subject_id')
        student_id= request.POST.get('student_id')
        exam_id = request.POST.get('exam_id')
        assignment_mark=request.POST.get('assignment_mark')
        exam_mark= request.POST.get('Exam_mark')

        get_student= Student.objects.get(admin=student_id)
        get_subject= Subject.objects.get(id=subject_id)
        get_exam = School_Official_Exam.objects.get(id=exam_id)

        check_exits= SchoolExamStudentResult.objects.filter(subject_id=get_subject,student_id=get_student,exam_id=get_exam).exists()
        if check_exits:
            result = SchoolExamStudentResult.objects.get(subject_id=get_subject,student_id=get_student,exam_id=get_exam)
            result.assignment_mark= assignment_mark
            result.exam_mark=exam_mark
            result.save()
            messages.success(request,'Result Are Successfully Updated')
            return redirect('teacher-add-result')
        else:
            result =SchoolExamStudentResult(
                student_id=get_student,
                subject_id=get_subject,
                exam_id=get_exam,
                exam_mark=exam_mark,
                assignment_mark=assignment_mark
            )
            result.save()
            messages.success(request,'Result Are Successfully added')
            return redirect('teacher-add-result')





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_VIEW_RESULT(request):
    classes = Class.objects.all()
    exams = None

    action = request.GET.get('action')
    selected_class = None
    selected_exam = None
    students = None

    if action == 'get_exams':
        if request.method == "POST":
            class_id = request.POST.get('class_id')
            selected_class = Class.objects.get(id=class_id)
            exams = School_Official_Exam.objects.filter(class_id=class_id)
    elif action == 'get_students':
        if request.method == "POST":
            class_id = request.POST.get('class_id')
            exam_id = request.POST.get('exam_id')
            selected_class = Class.objects.get(id=class_id)
            selected_exam = School_Official_Exam.objects.get(id=exam_id)
            students = Student.objects.filter(class_id=class_id)

    context = {
        'classes': classes,
        'exams': exams,
        'selected_class': selected_class,
        'selected_exam': selected_exam,
        'students': students,
        'action': action,
    }
    return render(request, 'teacher/view_result.html', context)

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_SHOW_RESULT(request, id, exam_id):
    student = Student.objects.get(id=id)
    exam = School_Official_Exam.objects.get(id=exam_id)
    
    results = SchoolExamStudentResult.objects.filter(student_id=student, exam_id=exam)
    for result in results:
        result.is_fail = result.assignment_mark <= (result.exam_mark * 0.33)

    context = {
        'result': results,
    }
    return render(request, 'teacher/show_result.html', context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_EDIT_RESULT(request,id):
    result = SchoolExamStudentResult.objects.get(id=id)

    context = {
        'result':result,
    }
    return render(request,'teacher/edit_result.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_UPDATE_RESULT(request):
    if request.method == "POST":
        result_id = request.POST.get('result_id')
        exam_mark = request.POST.get('exam_mark')
        assignment_mark = request.POST.get('assignment_mark')

        # Retrieve the student result object
        result = get_object_or_404(SchoolExamStudentResult, id=result_id)

        # Update the result fields
        result.exam_mark = exam_mark
        result.assignment_mark = assignment_mark

        # Save the updated result
        result.save()

        # Optionally, you can add a success message
        messages.success(request, 'Result successfully updated.')

        # Redirect to the appropriate page
    return redirect('teacher-view-result')
    


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_DELETE_RESULT(request,id):
    
    result = SchoolExamStudentResult.objects.get(id=id)
    result.delete()
    messages.success(request, 'Student Result has been successfully deleted.')

    return redirect('teacher-view-result')





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_ADD_NOTICE(request):

    if request.method== "POST":
        notice= request.POST.get('notice')
        notice1 = Add_Notice(
            notice = notice,
        )
        notice1.save()
        messages.success(request,'Notice Are Successfully Created')
        return redirect('teacher-add-notice')

    return render(request,'teacher/add_notice.html')











@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
    return render(request,'teacher/student_notification.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
        return redirect('teacher-star-student-add')
    
    context = {
        'class':class1,
    }
    
    return render(request,'admin/add_star_student.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STAR_STUDENT_EDIT(request,id):
    star_student = Star_student.objects.filter(id = id)
    class1 = Class.objects.all()
    context= {
        'star_student':star_student,
        'class':class1,
    }
    
    return render(request,'admin/edit_star_student.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
        return redirect('teacher-home')    




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STAR_STUDENT_DELETE(request,id):
    star_student = Star_student.objects.get(id= id)
    star_student.delete()

    messages.success(request,'Star Student Are Successfully Deleted')

    return redirect('teacher-home')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STUDENT_ACTIVITY_ADD(request):
    if request.method == "POST":
        date = request.POST.get('date')
        description = request.POST.get('description')

        if not description:
            # Handle the case where description is empty
            messages.error(request, 'Description is required.')
            return redirect('teacher-student-activity-add')

        student_activity = Student_activity(
            date=date,
            description=description,
        )
        student_activity.save()
        messages.success(request, 'Student Activity Are Successfully Created')
        return redirect('teacher-student-activity-add')

    
    return render(request,'admin/add_student_activity.html')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STUDENT_ACTIVITY_VIEW(request):
    student_activity= Student_activity.objects.all()

    context = {
        'student_activity':student_activity,
    }

    return render(request,'admin/view_student_activity.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STUDENT_ACTIVITY_EDIT(request,id):
    student_activity= Student_activity.objects.get(id = id)

    context = {
        'student_activity':student_activity,
    }
    return render(request,'admin/edit_student_activity.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
        return redirect('teacher-home')


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STUDENT_ACTIVITY_DELETE(request,id):
    student_activity = Student_activity.objects.get(id= id)
    student_activity.delete()

    messages.success(request,'Student Activity Are Successfully Deleted')

    return redirect('teacher-student-activity-view')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_STUDENT_WRITTEN_ANSWER_FILTER(request):
    if request.method == 'POST':
        action = request.GET.get('action')
        if action == 'Show-Courses':
            selected_class_id = request.POST.get('class_id')
            courses = Course.objects.filter(class1=selected_class_id)
            return render(request, "teacher/student_written_answer_filter.html", {"action": "Show-Courses", "courses": courses, "selected_class_id": selected_class_id})
        
        elif action == 'Show-Exams':
            selected_class_id = request.POST.get('class_id')
            selected_course_id = request.POST.get('course_id')
            exams = Live_Exam.objects.filter(course_id=selected_course_id)
            return render(request, "teacher/student_written_answer_filter.html", {"action": "Show-Exams", "exams": exams, "selected_course_id": selected_course_id, "selected_class_id": selected_class_id})
        
        elif action == 'Show-Students':
            selected_class_id = request.POST.get('class_id')
            selected_course_id = request.POST.get('course_id')
            selected_exam_id = request.POST.get('exam_id')
           
            get_class = Class.objects.get(id=selected_class_id)
            # Fetch students who do not have results for the selected exam
            students = Student.objects.filter(class_id=get_class).exclude(
                id__in=Live_Exam_Written_Result.objects.filter(exam_id=selected_exam_id).values_list('student_id', flat=True)
            )

            context = {
                "action": "Show-Students", 
                "students": students, 
                "class":selected_class_id, 
                "selected_course_id": selected_course_id,
                "exam":selected_exam_id
            }
            return render(request, "teacher/student_written_answer_filter.html", context)
    else:
        classes = Class.objects.all()
        return render(request, "teacher/student_written_answer_filter.html", {"classes": classes})
   


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_STUDENT_WRITTEN_ANSWER(request, student_id, exam_id):
    exam = Live_Exam.objects.get(id = exam_id)
    # Get the questions for the exam
    questions = LiveExamWrittenQuestion.objects.filter(exam=exam_id)
    
    # Get the student's written answers for the exam
    student =Student.objects.get( id=student_id)
    written_answers = LiveExamStudentWrittenAnswer.objects.filter(student=student, question__exam=exam_id).select_related('question').prefetch_related('images')
    
    context = {
        "questions": questions,
        "written_answers": written_answers,
        "student": student,
        "exam":exam,
    }
    
    return render(request, 'admin/student_written_answer.html', context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def GIVE_STUDENT_WRITTEN_EXAM_MARK(request):
    if request.method == "POST":
        student = request.POST.get("student_id")
        exam = request.POST.get("exam_id")

        student = Student.objects.get(id = student)
        exam = Live_Exam.objects.get(id = exam)

        for question in LiveExamWrittenQuestion.objects.filter(exam=exam):
            marks = request.POST.get(f'marks_{question.id}')
            if marks is not None:
                Live_Exam_Written_Result.objects.create(
                    student=student,
                    exam=exam,
                    question=question,
                    marks=int(marks)
                )
        
        live_written_exam_mark = Live_Exam_Written_Result.objects.filter(exam=exam)
        total_mark = 0
        for i in live_written_exam_mark:
            total_mark= total_mark + i.marks
        
        exam_result, created = Live_Exam_Result.objects.get_or_create(
            student=student,
            exam=exam,
            defaults={'marks': total_mark}
        )
        if not created:
            exam_result.marks += total_mark
            exam_result.save()

        return redirect('teacher-home')
  