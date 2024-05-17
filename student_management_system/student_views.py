from django.shortcuts import render,redirect
from app.models import Student,Student_Notification,Student_Feedback,Attendance,Attendance_Report,StudentResult,Add_Notice,Practice_Exam,PracticeExamQuestion,Practice_Exam_Result,Course,OnlineLiveClass,Live_Exam,LiveExamQuestion,Live_Exam_Result,Live_Exam_Report,LiveExamTimer,PracticeExamTimer
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from calendar import monthrange
from django.utils import timezone
from django.db.models import Subquery



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def HOME(request):
    notice = Add_Notice.objects.all()
    user = request.user
    student = Student.objects.get(admin=user)
    student_class = student.class_id
    live_class= OnlineLiveClass.objects.all().count()
    current_time = timezone.localtime(timezone.now())  # Get the current time in the local timezone
    live_exam = Live_Exam.objects.filter(
            end_time__gt=current_time,
            class_id=student_class,
        ).count()
    practice_exam = Practice_Exam.objects.filter(class_id=student_class).count()

    context={
        'notice':notice,
        'student':student,
        'live_class':live_class,
        'live_exam':live_exam,
        'practice_exam':practice_exam,
    }
    return render(request,'student/home.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def NOTIFICATION(request):
    student = Student.objects.filter(admin=request.user.id)
    for i in student:
        student_id =i.id

        notification = Student_Notification.objects.filter(student_id=student_id)

        context = {
            'notification':notification,
        }
        return render(request,'student/notification.html',context)
    


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_NOTIFICATION_MARK_AS_DONE(request,status):
        notification = Student_Notification.objects.get(id= status)
        notification.status=1
        notification.save()


        return redirect('student-notification')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_FEEDBACK(request):
    student_id = Student.objects.get(admin = request.user.id)

    feedback_history = Student_Feedback.objects.filter(student_id= student_id)

    context= {
        'feedback_history': feedback_history,
    }
    return render(request,'student/feedback.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_FEEDBACK_SAVE(request):
    if request.method=="POST":
        feedback = request.POST.get('feedback')

        student = Student.objects.get(admin=request.user.id)

        feedback= Student_Feedback(
            student_id = student,
            feedback = feedback,
            feedback_reply =""

        )
        feedback.save()
    
        return redirect('student-feedback')
    


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_VIEW_ATTENDANCE(request):
    attendance_month = None
    attendance_records = None
    days_in_month = None
    action = request.GET.get('action')
    student = request.user.student
    #attendance_status= None
    attendance_dates_str = None
    if action is not None:
        if request.method == "POST":
            attendance_month = request.POST.get('attendance_month')
            if attendance_month:
                year, month = map(int, attendance_month.split('-'))

                # Get the number of days in the selected month
                num_days = monthrange(year, month)[1]

                # Generate a list of dates in the selected month
                days_in_month = [datetime(year, month, day) for day in range(1, num_days + 1)]

                # Filter attendance records by the selected month
                attendance_records = Attendance_Report.objects.filter(
                    student_id=student,
                    attendance_id__attendance_date__year=year,
                    attendance_id__attendance_date__month=month
                )

                # Convert attendance_records queryset to a set of dates
                attendance_dates = set(record.attendance_id.attendance_date for record in attendance_records)

                # Create a set of dates in string format
                attendance_dates_str = {date.strftime('%Y-%m-%d') for date in attendance_dates}
                print(attendance_dates_str)

                # Create a dictionary to store whether the student was present on each day
                #attendance_status = {date_string.strftime('%Y-%m-%d'): 'Present' if date_string.strftime('%Y-%m-%d') in attendance_dates_str else 'Absent' for date_string in days_in_month}
                #print(attendance_status)
    context = {
        'attendance_month': attendance_month,
        'attendance_records': attendance_records,
        'student': student,
        'action': action,
        'attendance_dates_str':attendance_dates_str,
        #'attendance_status':attendance_status,
        'days_in_month': days_in_month,  # Pass the preprocessed list to the template
    }

    return render(request, 'student/test.html', context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_VIEW_RESULT(request):
    mark = None
    student = Student.objects.get(admin=request.user.id)
    
    result = StudentResult.objects.filter(student_id=student)

    for i in result:
        assignment_mark = i.assignment_mark
        

        mark = assignment_mark

    context= {
        
        'result':result,
        'mark':mark,
    }
    return render(request,'student/view_result.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_ASK_QUESTION(request):
    return render(request,'student/q&a.html')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_PRACTICE_EXAM(request):
    user = request.user
    student = Student.objects.get(admin=user)
    student_class = student.class_id
    courses = Course.objects.filter(class1=student_class)
    exams = Practice_Exam.objects.filter(class_id=student_class)

    context = {
        'exam':exams,
        'course':courses,
    }
    return render(request,'student/practice_exam.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_TAKE_PRACTICE_EXAM(request,id):
    exam = Practice_Exam.objects.get(id = id)
    total_question = PracticeExamQuestion.objects.all().filter(exam = exam).count()
    questions=PracticeExamQuestion.objects.all().filter(exam=exam)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks

    context = {
        'exam':exam,
        'total_question':total_question,
        'total_marks':total_marks,
    }
    return render(request,'student/take_practice_exam.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_START_PRACTICE_EXAM(request,id):
    exam=Practice_Exam.objects.get(id=id)
    questions=PracticeExamQuestion.objects.all().filter(exam=exam)

    start_time = timezone.localtime(timezone.now())
    user = request.user
    duration_seconds = exam.duration.total_seconds()
    end_time = start_time + timedelta(seconds=duration_seconds)
    timer =PracticeExamTimer.objects.filter(exam=exam,user=user)
    timer = list(timer)

    if len(timer) == 0:
        user_exam_timer = PracticeExamTimer.objects.create(exam=exam,user=user,start_time=start_time,end_time=end_time)
        remaining_time = (end_time - start_time).total_seconds()

    else:
        timer =PracticeExamTimer.objects.get(exam=exam,user=user)
        end_time = timer.end_time
        remaining_time = (end_time - timezone.now()).total_seconds()
    

    context = {
        'questions':questions,
        'exam':exam,
        'remaining_time': remaining_time,
        'no_questions': questions.count() == 0,
    }

    return render(request,'student/start_practice_exam.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_PRACTICE_EXAM_CALCULATE_MARKS(request):
    if request.method == "POST":
        exam_id = request.POST.get('exam_id') 
        exam = Practice_Exam.objects.get(id=exam_id)
        questions = PracticeExamQuestion.objects.filter(exam=exam)
        student = request.user.student

        total_obtained_marks = 0
        correct_answers = 0

        for i in range(len(questions)):
            selected_answer = request.POST.get(str(i+1))  # Assuming the radio button names are the question IDs
            correct_answer = questions[i].answer
            if selected_answer == correct_answer:
                total_obtained_marks += questions[i].marks
                correct_answers += 1
        exam_timer = PracticeExamTimer.objects.get(exam=exam,user = request.user)
        exam_timer.delete()
        exam_result = Practice_Exam_Result.objects.create(student=student, exam=exam, marks=total_obtained_marks)

        print(total_obtained_marks)
        return redirect('student-practice-exam-mark')
        




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_PRACTICE_EXAM_MARK(request):
    user = request.user
    student = Student.objects.get(admin=user)
    student_class = student.class_id
    courses = Course.objects.filter(class1=student_class)
    exams = Practice_Exam.objects.filter(class_id=student_class)

    context = {
        'exam':exams,
        'course':courses,
    }
    return render(request,'student/practice_exam_mark.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_VIEW_PRACTICE_EXAM_MARK(request,id):
    exam=Practice_Exam.objects.get(id=id)
    student =Student.objects.get(admin=request.user.id)
    results=Practice_Exam_Result.objects.all().filter(exam=exam).filter(student=student)

    context = {
        'result':results,
    }
    return render(request,'student/view_practice_exam_mark.html',context)





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_LIVE_EXAM(request):
    user = request.user
    student = Student.objects.get(admin=user)
    student_class = student.class_id
    current_time = timezone.localtime(timezone.now())  # Get the current time in the local timezone
    taken_exams = Live_Exam_Report.objects.filter(user=user, is_taken=True).values('exam')
    exams = Live_Exam.objects.filter(
        end_time__gt=current_time,
        class_id=student_class,
    ).exclude(pk__in=Subquery(taken_exams))

    course= Course.objects.all()
    selected_course = request.GET.get('course_filter', '')
    search_query = request.GET.get('search_query', '')  


    if selected_course:
        exam = exam.filter(course=selected_course)

    context= {
        'exam':exams,
        'search_query':search_query,
        'course':course,
        'selected_course': selected_course,
        'current_time': current_time, 
    }
    return render(request,'student/live_exam.html',context)


def STUDENT_TAKE_LIVE_EXAM(request,id):
    exam = Live_Exam.objects.get(id = id)
    total_question = LiveExamQuestion.objects.all().filter(exam = exam).count()
    questions=LiveExamQuestion.objects.all().filter(exam=exam)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks

    context = {
        'exam':exam,
        'total_question':total_question,
        'total_marks':total_marks,
    }
    return render(request,'student/take_live_exam.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_START_LIVE_EXAM(request,id):
    exam=Live_Exam.objects.get(id=id)
    questions=LiveExamQuestion.objects.all().filter(exam=exam)
    start_time = timezone.localtime(timezone.now())
    user = request.user
    duration_seconds = exam.duration.total_seconds()
    end_time = start_time + timedelta(seconds=duration_seconds)
    timer = LiveExamTimer.objects.filter(exam=exam,user=user)
    timer = list(timer)

    if len(timer) == 0:
        user_exam_timer = LiveExamTimer.objects.create(exam=exam,user=user,start_time=start_time,end_time=end_time)
        remaining_time = (end_time - start_time).total_seconds()

    else:
        timer = LiveExamTimer.objects.get(exam=exam,user=user)
        end_time = timer.end_time
        remaining_time = (end_time - timezone.now()).total_seconds()
        
    context = {
        'questions':questions,
        'exam':exam,
        'remaining_time': remaining_time,
        'no_questions': questions.count() == 0,
    }

    return render(request,'student/start_live_exam.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_LIVE_EXAM_CALCULATE_MARKS(request):
    if request.method == "POST":
        exam_id = request.POST.get('exam_id') 
        exam = Live_Exam.objects.get(id=exam_id)
        questions = LiveExamQuestion.objects.filter(exam=exam)
        student = request.user.student

        total_obtained_marks = 0
        correct_answers = 0

        for i in range(len(questions)):
            selected_answer = request.POST.get(str(i+1))  # Assuming the radio button names are the question IDs
            correct_answer = questions[i].answer
            if selected_answer == correct_answer:
                total_obtained_marks += questions[i].marks
                correct_answers += 1
        exam_timer = LiveExamTimer.objects.get(exam=exam,user = request.user)
        exam_timer.delete()
        exam_result = Live_Exam_Result.objects.create(student=student, exam=exam, marks=total_obtained_marks)
        live_exam_report = Live_Exam_Report.objects.create(exam = exam,user = request.user,is_taken = True)
        return redirect('student-live-exam-mark')
      

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_LIVE_EXAM_MARK(request):
    user = request.user
    student = Student.objects.get(admin=user)
    student_class = student.class_id
    courses = Course.objects.filter(class1=student_class)
    exams = Live_Exam.objects.filter(class_id=student_class)

    context = {
        'exam':exams,
        'course':courses,
    }
    return render(request,'student/live_exam_mark.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_VIEW_LIVE_EXAM_MARK(request,id):
    exam=Live_Exam.objects.get(id=id)
    student =Student.objects.get(admin=request.user.id)
    results=Live_Exam_Result.objects.all().filter(exam=exam).filter(student=student)

    context = {
        'result':results,
    }
    return render(request,'student/view_live_exam_mark.html',context)





def VIEW_ONLINE_LIVE_CLASS(request):
    all_online_live_class= OnlineLiveClass.objects.all().order_by('-start_time')

    context = {
        "class":all_online_live_class,
    }

    return render(request,"student/view_online_live_class.html",context)