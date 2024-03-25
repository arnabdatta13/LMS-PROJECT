from django.shortcuts import render,redirect
from app.models import Teacher, Teacher_Notification,Teacher_Feedback,Student_Feedback,Session_Year,Course,Student,Attendance,Attendance_Report,Subject,StudentResult,Class,Add_Notice
from django.contrib import messages
from operator import attrgetter
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse





def HOME(request):
    notice = Add_Notice.objects.all()

    context={
        'notice':notice,
    }
    return render(request,'teacher/home.html',context)


def NOTIFICATION(request):
    teacher = Teacher.objects.filter(admin=request.user.id)
    for i in teacher:
        teacher_id =i.id

        notification = Teacher_Notification.objects.filter(teacher_id=teacher_id)

        context = {
            'notification':notification,
        }
        return render(request,'teacher/notification.html',context)
    

def TEACHER_NOTIFICATION_MARK_AS_DONE(request,status):
    notification = Teacher_Notification.objects.get(id= status)
    notification.status=1
    notification.save()


    return redirect('teacher-notification')


def TEACHER_FEEDBACK(request):
    teacher_id = Teacher.objects.get(admin = request.user.id)

    feedback_history = Teacher_Feedback.objects.filter(teacher_id= teacher_id)

    context= {
        'feedback_history': feedback_history,
    }
    return render(request,'teacher/feedback.html',context)

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
    


def STUDENT_FEEDBACK(request):
    student_feedback = Student_Feedback.objects.all()

    context = {
        'student_feedback':student_feedback,
    }
    return render(request,"teacher/student_feedback.html",context)

def STUDENT_FEEDBACK_SAVE(request):
    if request.method== "POST":
        feedback_id= request.POST.get('feedback_id')
        feedback_reply = request.POST.get('feedback_reply')

      

        feedback = Student_Feedback.objects.get(id=feedback_id)

        feedback.feedback_reply=feedback_reply
        feedback.save()

        return redirect('teacher-student-feedback')
    

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








def TEACHER_ADD_RESULT(request):

    class1 = Class.objects.all()

    result = StudentResult.objects.all()

    action = request.GET.get('action')

    get_class = None
    student=None
    subject = None

    if action is not None:
        if request.method=="POST":
            class_id = request.POST.get('class_id')

            get_class = Class.objects.get(id=class_id)

            class1 = Class.objects.filter(id= class_id)
            subject = Subject.objects.filter(class1=get_class)

            for i in class1:
                student_id = i.id
                student = Student.objects.filter(
                    class_id=student_id
                ).order_by('roll_number')
                subject = Subject.objects.filter(class1=student_id)


    context = {
        
        'class':class1,
        'action':action,
        'get_class':get_class,
        'student':student,
        'subject': subject,
        'result':result,

    }
    return render(request,'teacher/add_result.html',context)



def TEACHER_SAVE_RESULT(request):
    if request.method == "POST":
      
        subject_id = request.POST.get('subject_id')
        student_id= request.POST.get('student_id')
        assignment_mark=request.POST.get('assignment_mark')
        exam_mark= request.POST.get('Exam_mark')

        get_student= Student.objects.get(admin=student_id)
        get_subject= Subject.objects.get(id=subject_id)

        check_exits= StudentResult.objects.filter(subject_id=get_subject,student_id=get_student).exists()
        if check_exits:
            result = StudentResult.objects.get(subject_id=get_subject,student_id=get_student)
            result.assignment_mark= assignment_mark
            result.exam_mark=exam_mark
            result.save()
            messages.success(request,'Result Are Successfully Updated')
            return redirect('teacher-add-result')
        else:
            result =StudentResult(
                student_id=get_student,
                subject_id=get_subject,
                exam_mark=exam_mark,
                assignment_mark=assignment_mark
            )
            result.save()
            messages.success(request,'Result Are Successfully added')
            return redirect('teacher-add-result')





def TEACHER_VIEW_RESULT(request):

  
    class1 = Class.objects.all()

    action = request.GET.get('action')


    get_class = None
    
    student=None
    if action is not None:
        if request.method == "POST":
            
            class_id = request.POST.get('class_id')
            
            get_class = Class.objects.get(id =class_id)
            

            course = Class.objects.filter(id= class_id)
            for i in course:
                student_id = i.id
                student= Student.objects.filter(class_id=student_id)


    context = {
        'class':class1,
     
        'get_class':get_class,
       
        'action':action,
        'student':student,
    }



    return render(request,'teacher/view_result.html',context)


def TEACHER_SHOW_RESULT(request,id):

    mark = None
    
    student = Student.objects.get(id=id)
    
    result = StudentResult.objects.filter(student_id=student)

    for i in result:
        assignment_mark = i.assignment_mark
        

        mark = assignment_mark

    context= {
        
        'result':result,
        'mark':mark,
    }



   
    return render(request,'teacher/show_result.html',context)



def TEACHER_EDIT_RESULT(request,id):
    result = StudentResult.objects.get(id=id)

    context = {
        'result':result,
    }
    return render(request,'teacher/edit_result.html',context)

def TEACHER_UPDATE_RESULT(request):
    if request.method == "POST":
        result_id = request.POST.get('result_id')
        exam_mark = request.POST.get('exam_mark')
        assignment_mark = request.POST.get('assignment_mark')

        # Retrieve the student result object
        result = get_object_or_404(StudentResult, id=result_id)

        # Update the result fields
        result.exam_mark = exam_mark
        result.assignment_mark = assignment_mark

        # Save the updated result
        result.save()

        # Optionally, you can add a success message
        messages.success(request, 'Result successfully updated.')

        # Redirect to the appropriate page
    return redirect('teacher-view-result')
    



def TEACHER_DELETE_RESULT(request,id):
    
    result = StudentResult.objects.get(id=id)
    result.delete()
    messages.success(request, 'Student Result has been successfully deleted.')

    return redirect('teacher-view-result')






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