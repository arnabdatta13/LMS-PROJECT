from django.shortcuts import render,redirect
from app.models import Student,Student_Notification,Student_Feedback,Attendance,Attendance_Report,SchoolExamStudentResult,Add_Notification,Practice_Exam,PracticeExamQuestion,Practice_Exam_Result,Course,OnlineLiveClass,Live_Exam,LiveExamMCQQuestion,Live_Exam_Result,Live_Exam_MCQ_Report,LiveExamTimer,PracticeExamTimer,Class,School_Official_Exam,Subject,LiveExamQuestionOptionSelect,LiveExamWrittenQuestion,LiveExamStudentWrittenAnswer,LiveExamStudentWrittenAnswerImage,Live_Exam_Written_Result,Live_Exam_MCQ_Result,Live_Exam_WRITTEN_Report,StudentQuestion,StudentPhoto,StudentAudio
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from calendar import monthrange
from django.utils import timezone
from django.db.models import Subquery,Q
from django.db.models import F,ExpressionWrapper, DurationField
from django.contrib import messages
from itertools import chain
from django.db.models import Sum, Max
from operator import attrgetter
from django.db.models import Count
from django.http import JsonResponse
from collections import defaultdict
import json



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def HOME(request):
    user = request.user
    student = Student.objects.get(admin=user)
    student_class = student.class_id

    current_time = timezone.localtime(timezone.now())
    live_class = OnlineLiveClass.objects.filter(class1 = student_class)
    taken_mcq_exams = Live_Exam_MCQ_Report.objects.filter(user=user, is_taken=True).values('exam')
    taken_written_exams = Live_Exam_WRITTEN_Report.objects.filter(user=user, is_taken=True).values('exam')

    taken_both_exams = Live_Exam.objects.filter(
        Q(id__in=Subquery(taken_mcq_exams)) & Q(id__in=Subquery(taken_written_exams))
    ).values('id')

    live_exam = Live_Exam.objects.filter(end_time__gt=current_time, class_id=student_class).exclude(pk__in=Subquery(taken_both_exams))

    practice_exam = Practice_Exam.objects.filter(class_id=student_class)

    live_classes = []
    upcoming_classes = []
    live_exams = []
    upcoming_exams = []

    for online_class in live_class:
        class_end_time = online_class.start_time + timedelta(minutes=online_class.duration)
        if online_class.start_time <= current_time < class_end_time:
            online_class.is_live = True
            live_classes.append(online_class)
        elif current_time < online_class.start_time:
            online_class.is_live = False
            upcoming_classes.append(online_class)

    for exam in live_exam:
        if exam.start_time <= current_time < exam.end_time:
            live_exams.append(exam)
        elif current_time < exam.start_time:
            upcoming_exams.append(exam)

    upcoming_classes.sort(key=lambda x: x.start_time)
    upcoming_exams.sort(key=lambda x: x.start_time)


    #total live class and total live exam count
    total_live_exams = Live_Exam.objects.filter(
            end_time__gt=current_time,
            class_id=student_class,
        ).exclude(pk__in=Subquery(taken_both_exams)).count()
    
    valid_online_live_class = [
        online_class for online_class in live_class
        if online_class.start_time + timedelta(minutes=online_class.duration) > current_time
    ]

    valid_online_live_class.sort(key=lambda x: x.start_time, reverse=True)

    total_live_class_count = len(valid_online_live_class)


    #attendance data
    attendance_reports = Attendance_Report.objects.filter(student_id=student)
    attendance_dates = [record.attendance_id.attendance_date.strftime("%Y-%m-%d") for record in attendance_reports]
    


    #attendance chart
    student_user = request.user.student
    attendance_data = Attendance.objects.filter(attendance_report__student_id=student_user)
    #print(attendance_data)
    # Calculate available years and monthly attendance data
    years_with_data = set()
    monthly_attendance = defaultdict(lambda: {'present': 0, 'absent': 0})

     # Calculate overall present and absent days
    total_present_days = 0
    total_absent_days = 0


    for attendance in attendance_data:
        #print(attendance)
        year = attendance.attendance_date.year
        print(year)
        month = attendance.attendance_date.month
        print(month)
        years_with_data.add(year)

        present_days = Attendance_Report.objects.filter(attendance_id=attendance, student_id=student_user).count()
        print(f"present_days: {present_days}")
        # Get total days in the month
        total_days_in_month = monthrange(year, month)[1]
        print(total_days_in_month)

        # Update the total present and absent days for the pie chart
        total_present_days += present_days
        total_absent_days += total_days_in_month - present_days

        # Update the monthly data with present and absent days
        monthly_attendance[(year, month)]['present'] += present_days
        monthly_attendance[(year, month)]['absent'] = total_days_in_month - monthly_attendance[(year, month)]['present']
        print(monthly_attendance)
    # Convert the defaultdict to a normal dict
    monthly_attendance = {f"{year},{month}": data for (year, month), data in monthly_attendance.items()}

    total_days = total_present_days + total_absent_days
    print(total_absent_days)
    print(total_present_days)
    if total_days > 0:
        overall_present_percentage = (total_present_days / total_days) * 100
        overall_absent_percentage = (total_absent_days / total_days) * 100
    else:
        overall_present_percentage = 0
        overall_absent_percentage = 0


    context = {
        'student': student,
        'live_class_count': len(live_classes),
        'upcoming_class_count': len(upcoming_classes),
        'live_classes': live_classes,
        'upcoming_classes': upcoming_classes,
        'live_exam_count': len(live_exams),
        'upcoming_exam_count': len(upcoming_exams),
        'live_exams': live_exams,
        'upcoming_exams': upcoming_exams,
        'practice_exam': practice_exam.count(),
        'total_live_exams':total_live_exams,
        'total_live_classes':total_live_class_count,
        'attendance_dates': attendance_dates,
        'years_with_data': sorted(years_with_data),
        'monthly_attendance_json': json.dumps(monthly_attendance),
        'overall_attendance': json.dumps({
            'present': overall_present_percentage,
            'absent': overall_absent_percentage
        }),
    }

    return render(request, 'student/home.html', context)



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

    return render(request, 'student/view_attendance.html', context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_VIEW_SCHOOL_EXAM_RESULT(request):
    student = Student.objects.get(admin=request.user.id)
    exams = School_Official_Exam.objects.filter(class_id=student.class_id)
    results = None
    selected_exam = None

    if request.method == "POST":
        exam_id = request.POST.get('exam_id')
        selected_exam = School_Official_Exam.objects.get(id=exam_id)
        results = SchoolExamStudentResult.objects.filter(student_id=student, exam_id=selected_exam)
        for result in results:
            result.is_fail = result.assignment_mark <= (result.exam_mark * 0.33)

    context = {
        'exams': exams,
        'results': results,
        'selected_exam': selected_exam,
    }
    return render(request, 'student/view_school_exam_result.html', context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_ASK_QUESTION(request):
    if request.method == 'POST':
        # Extract data from the POST request
        subject_id = request.POST.get('subject')
        chapter = request.POST.get('chapter')
        text_question = request.POST.get('text_question')
        print(subject_id,chapter,text_question)

        audio_file = request.FILES.get('audio')
        print(audio_file)
        if audio_file:
            # Save or process the audio file
            print(f"Audio file: {audio_file.name}")

        # Handle the uploaded files
        uploaded_files = request.FILES.getlist('files')  # Gets the list of uploaded files
        for file in uploaded_files:
            # You can save each file or process it as needed
            print(file.name)  # For now, just printing the file name
        
        messages.success(request, "Question submitted successfully.")
        return redirect('student-question')  # Redirect to the list of questions or another page
    
    user= request.user
    student= Student.objects.get(admin= user)
    student_class = student.class_id

    subjects = Subject.objects.filter(class1 = student_class)
    context = {
        'subjects': subjects
    }
    
    return render(request,'student/q&a.html',context)

'''
        # Save the question
        question = StudentQuestion.objects.create(
            class_id_id=class_id,
            subject_id=subject_id,
            chapter=chapter,
            text_question=text_question
        )

        # Save photos
        for photo in request.FILES.getlist('photos'):
            StudentPhoto.objects.create(question=question, photo=photo)

        # Save audio files
        for audio_file in request.FILES.getlist('audio_files'):
            StudentAudio.objects.create(question=question, audio_file=audio_file)
'''

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_QUESTION(request):
    questions = StudentQuestion.objects.all().order_by('-created_at')
    context = {
        'questions': questions,
    }
    return render(request,'student/student_questions.html',context)


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
        'exam_type': 'practice'
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

        mcq_exam_result = Practice_Exam_Result.objects.create(student=student, exam=exam, marks=total_obtained_marks)

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
        'exam':exam,
    }
    return render(request,'student/view_practice_exam_mark.html',context)






@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_LIVE_EXAM(request):
    user = request.user
    student = Student.objects.get(admin=user)
    student_class = student.class_id
    current_time = timezone.localtime(timezone.now())  # Get the current time in the local timezone
    taken_mcq_exams = Live_Exam_MCQ_Report.objects.filter(user=user, is_taken=True).values('exam')
    taken_written_exams = Live_Exam_WRITTEN_Report.objects.filter(user=user, is_taken=True).values('exam')

    taken_both_exams = Live_Exam.objects.filter(
        Q(id__in=Subquery(taken_mcq_exams)) & Q(id__in=Subquery(taken_written_exams))
    ).values('id')

    exams = Live_Exam.objects.filter(
        end_time__gt=current_time,
        class_id=student_class,
    ).exclude(pk__in=Subquery(taken_both_exams))

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


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_TAKE_LIVE_EXAM(request,id):
    exam = Live_Exam.objects.get(id = id)
    current_time = timezone.localtime(timezone.now()) 

    if current_time < exam.start_time or current_time > exam.end_time:
        messages.error(request, "You cannot take the exam outside the scheduled time.")
        return redirect('student-live-exam')
    
    if Live_Exam_MCQ_Report.objects.filter(exam = exam,user = request.user,is_taken = True).exists() and Live_Exam_WRITTEN_Report.objects.filter(exam = exam,user = request.user,is_taken = True).exists():
        messages.error(request, "You already has taken the exam.")
        return redirect('student-live-exam')


    total_question = LiveExamMCQQuestion.objects.all().filter(exam = exam).count()
    questions=LiveExamMCQQuestion.objects.all().filter(exam=exam)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks


    live_exam_mcq_taken=  Live_Exam_MCQ_Report.objects.filter(exam = exam,user = request.user,is_taken = True).count()
    live_exam_written_taken =  Live_Exam_WRITTEN_Report.objects.filter(exam = exam,user = request.user,is_taken = True).count()

    print(live_exam_mcq_taken)
    print(live_exam_written_taken)


    context = {
        'exam':exam,
        'total_question':total_question,
        'total_marks':total_marks,
        'live_exam_mcq_taken':live_exam_mcq_taken,
        'live_exam_written_taken':live_exam_written_taken,
    }
    return render(request,'student/take_live_exam.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_START_LIVE_EXAM_WRITTEN(request,id):
    exam = Live_Exam.objects.get(id = id)

    question = LiveExamWrittenQuestion.objects.filter(exam=exam)
    context = {
        "exam":exam,
        "questions":question,
    }
    return render(request,"student/start_live_exam_written.html",context)






@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_SUBMIT_LIVE_EXAM_WRITTEN(request):
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        exam = Live_Exam.objects.get(id=exam_id)
        student = request.user.student

        questions = LiveExamWrittenQuestion.objects.filter(exam=exam)

        for index, question in enumerate(questions, start=1):
            answer_text = request.POST.get(f'answer_{index}')
            answer_images = request.FILES.getlist(f'answer_image_{index}')  # Ensure this matches the name in HTML

            # Create the answer record
            answer_record = LiveExamStudentWrittenAnswer.objects.create(
                question=question,
                student=student,
                answer_text=answer_text
            )

            # Save each image in the new model
            for img in answer_images:
                LiveExamStudentWrittenAnswerImage.objects.create(
                    answer=answer_record,
                    image=img
                )

        live_exam_written_report = Live_Exam_WRITTEN_Report.objects.create(exam=exam, user=request.user, is_taken=True)

        return redirect('student-live-exam')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_TAKE_LIVE_EXAM_HOME(request,id):
    exam=Live_Exam.objects.get(id=id)
    current_time = timezone.localtime(timezone.now()) 

    if current_time < exam.start_time or current_time > exam.end_time:
        messages.error(request, "You cannot take the exam outside the scheduled time.")
        return redirect('student-home')
    

    return redirect('student-take-live-exam/{{exam.id}}')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_START_LIVE_EXAM(request,id):
    exam=Live_Exam.objects.get(id=id)

    if Live_Exam_MCQ_Report.objects.filter(exam = exam,user = request.user,is_taken = True).exists() :
        messages.error(request, "You already has taken the exam.")
        return redirect('student-live-exam')
    
    questions= LiveExamMCQQuestion.objects.filter(exam = exam)
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
        'exam_type': "live" 
    }

    return render(request,'student/start_live_exam.html',context)


 

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_LIVE_EXAM_CALCULATE_MARKS(request):
    print("all ok")
    if request.method == "POST":
        print(f"Received POST data: {request.POST}")
        exam_id = request.POST.get('exam_id') 
        exam = Live_Exam.objects.get(id=exam_id)
        student = request.user.student

        # Exam submission logic
        questions = LiveExamMCQQuestion.objects.filter(exam=exam)
        total_obtained_marks = 0
        correct_answers = 0

        for i, question in enumerate(questions):
            selected_answer = request.POST.get(str(i + 1))  # Assuming radio button names are numbers starting from 1
            correct_answer = question.answer

            # Save the selected option
            LiveExamQuestionOptionSelect.objects.create(
                question=question,
                user=request.user,
                selected_option=selected_answer if selected_answer else "No Answer"  # Handle None case
            )

            if selected_answer == correct_answer:
                total_obtained_marks += question.marks
                correct_answers += 1

        # Delete the exam timer for the user
        exam_timer = LiveExamTimer.objects.get(exam=exam, user=request.user)
        exam_timer.delete()

        # Create or update the exam result
        mcq_exam_result = Live_Exam_MCQ_Result.objects.create(student=student, exam=exam, marks=total_obtained_marks)
        exam_result, created = Live_Exam_Result.objects.get_or_create(
            student=student,
            exam=exam,
            defaults={'marks': total_obtained_marks}
        )
        if not created:
            exam_result.marks += total_obtained_marks
            exam_result.save()

        # Mark the exam as taken in the report
        Live_Exam_MCQ_Report.objects.create(exam=exam, user=request.user, is_taken=True)

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
def STUDENT_VIEW_LIVE_EXAM_RESULT(request, id):
    exam = Live_Exam.objects.get(id=id)
    live_exam_mcq_questions = LiveExamMCQQuestion.objects.filter(exam=exam)
    live_exam_written_questions = LiveExamWrittenQuestion.objects.filter(exam=exam)

    student = request.user
    user_answers = LiveExamQuestionOptionSelect.objects.filter(question__in=live_exam_mcq_questions, user=student)
    written_answers = LiveExamStudentWrittenAnswer.objects.filter(student=student.student, question__exam=exam).select_related('question').prefetch_related('images')

    user_answers_dict = {answer.question.id: answer.selected_option for answer in user_answers}

    # Calculate user's total score for MCQ
    user_total_score = 0
    for question in live_exam_mcq_questions:
        selected_option = user_answers_dict.get(question.id)
        question.option1_selected = (selected_option == 'Option1')
        question.option2_selected = (selected_option == 'Option2')
        question.option3_selected = (selected_option == 'Option3')
        question.option4_selected = (selected_option == 'Option4')

        question.is_correct = (selected_option == question.answer)
        if question.is_correct:
            user_total_score += question.marks

        # Calculate statistics for each option
        total_answers = LiveExamQuestionOptionSelect.objects.filter(question=question).count()
        option1_count = LiveExamQuestionOptionSelect.objects.filter(question=question, selected_option='Option1').count()
        option2_count = LiveExamQuestionOptionSelect.objects.filter(question=question, selected_option='Option2').count()
        option3_count = LiveExamQuestionOptionSelect.objects.filter(question=question, selected_option='Option3').count()
        option4_count = LiveExamQuestionOptionSelect.objects.filter(question=question, selected_option='Option4').count()

        question.option1_percentage = (option1_count / total_answers) * 100 if total_answers > 0 else 0
        question.option2_percentage = (option2_count / total_answers) * 100 if total_answers > 0 else 0
        question.option3_percentage = (option3_count / total_answers) * 100 if total_answers > 0 else 0
        question.option4_percentage = (option4_count / total_answers) * 100 if total_answers > 0 else 0

    # Calculate the highest mark and merit position
    user_scores = {}
    for report in Live_Exam_MCQ_Report.objects.filter(exam=exam):
        user = report.user
        user_total = LiveExamQuestionOptionSelect.objects.filter(
            question__exam=exam, 
            user=user,
            question__answer=F('selected_option')
        ).aggregate(total_score=Sum('question__marks'))['total_score'] or 0
        user_scores[user] = user_total

    highest_mark = max(user_scores.values(), default=0)
    
    # Ensure that the user's total score is included in the scores list
    user_scores[request.user] = user_total_score

    # Sort the scores in descending order
    sorted_scores = sorted(user_scores.values(), reverse=True)

    # Calculate the merit position based on the sorted list
    merit_position = sorted_scores.index(user_total_score) + 1

    # Calculate written results
    written_marks = Live_Exam_Written_Result.objects.filter(student=student.student, exam=exam)
    written_results_dict = {result.question.id: {'marks': result.marks} for result in written_marks}

    processed_written_results = []
    for question in live_exam_written_questions:
        result = written_results_dict.get(question.id, {'marks': None})
        obtained_marks = result['marks']
        processed_written_results.append({
            'id': question.id,
            'question': question.question,
            'marks': question.marks,
            'obtained_marks': obtained_marks,
        })

    # Combine written questions and their answers
    combined_written_data = []
    for question in live_exam_written_questions:
        result = next((item for item in processed_written_results if item['id'] == question.id), {'marks': None})
        combined_data = {
            'question': question,
            'results': result,
            'answers': [answer for answer in written_answers if answer.question.id == question.id],
        }
        combined_written_data.append(combined_data)

    context = {
        'mcq_questions': live_exam_mcq_questions,
        'written_questions': combined_written_data,
        'exam': exam,
        'highest_mark': highest_mark,
        'merit_position': merit_position,
        'user_total_score': user_total_score,
    }

    return render(request, 'student/view_online_exam_result.html', context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_MERIT_POSITION(request, id):
    exam = Live_Exam.objects.get(id=id)
    students = Student.objects.all()

    # Create a dictionary to store results for each student who has taken the exam
    student_results = {}
    for student in students:
        result = Live_Exam_Result.objects.filter(exam=exam, student=student).first()
        if result:
            student_results[student] = result

    # Sort the students by their marks in descending order
    sorted_students = sorted(student_results.items(), key=lambda x: x[1].marks, reverse=True)

    # Retrieve the merit position for the logged-in student
    student = Student.objects.get(admin=request.user.id)
    merit_position = next((index + 1 for index, (s, r) in enumerate(sorted_students) if s == student), None)

    # Get the logged-in student's marks
    login_user_mark = student_results.get(student).marks if student in student_results else None

    context = {
        'exam': exam,
        'merit_position': merit_position,
        'student_results': student_results,
        'sorted_students': sorted_students,
        'student': student,
        'login_user_mark': login_user_mark,
    }

    return render(request, 'student/merit_position.html', context)





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def VIEW_ONLINE_LIVE_CLASS(request):
    current_time = timezone.now()
    class_id = Class.objects.get(id=request.user.id)
    all_online_live_class = OnlineLiveClass.objects.filter(class1=class_id)
    
    # Filter out the classes that have already ended
    valid_online_live_class = [
        online_class for online_class in all_online_live_class
        if online_class.start_time + timedelta(minutes=online_class.duration) > current_time
    ]
    
    valid_online_live_class.sort(key=lambda x: x.start_time, reverse=True)
    
    context = {
        "class": valid_online_live_class,
        "current_time": current_time
    }

    return render(request, "student/view_online_live_class.html", context)





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def JOIN_ONLINE_LIVE_CLASS_HOME(request, id):

    online_class = OnlineLiveClass.objects.get(id=id)
    current_time = timezone.localtime(timezone.now())

    if current_time <= online_class.start_time:
        messages.error(request, "Live Class not start.")
        return redirect('student-home')

    return redirect(online_class.join_url)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_PERFORMANCE_COURSE(request):
    user = request.user
    student = Student.objects.get(admin=user)
    student_class = student.class_id
    course = Course.objects.filter(class1=student_class)

    context = {
        'course':course,
    }
    return render(request,'student/performance_course.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_PERFORMANCE(request, id):
    course = Course.objects.get(id=id)
    student = request.user.student
    subject = Subject.objects.filter(class1=student.class_id)

    # Get all exams for the course
    selected_subject_id = request.GET.get('subject_id')

        # Filter exams by selected subject (if any), otherwise get all exams for the course
    if selected_subject_id:
        all_exams = Live_Exam.objects.filter(course=course, subject_id=selected_subject_id)
    else:
        all_exams = Live_Exam.objects.filter(course=course)
        
    # Get the results for live exams (MCQ and written)
    live_mcq_results = Live_Exam_MCQ_Result.objects.filter(exam__course=course, student=student)
    live_written_results = Live_Exam_Written_Result.objects.filter(exam__course=course, student=student)

    # Create dictionaries to map exams to results
    mcq_results_dict = {result.exam.id: result for result in live_mcq_results}
    written_results_dict = {result.exam.id: result for result in live_written_results}

    # Calculate the highest marks in the course for live exams
    highest_live_marks = Live_Exam_Result.objects.filter(exam__course=course).aggregate(max_marks=Max('marks'))['max_marks'] or 0

    # Function to get the sum of obtained marks for a student
    def get_total_obtained_marks(student):
        live_exam_sum = Live_Exam_Result.objects.filter(exam__course=course, student=student).aggregate(total_marks=Sum('marks'))['total_marks'] or 0
        return live_exam_sum

    # Calculate the student's total obtained marks
    student_total_obtained_marks = get_total_obtained_marks(student)

    # Calculate total MCQ and written marks
    total_mcq_obtained_marks = sum(result.marks for result in live_mcq_results)
    total_written_obtained_marks = sum(result.marks for result in live_written_results)

    # Calculate total possible marks for the course
    total_possible_marks = sum(exam.total_marks for exam in all_exams)

    # Calculate merit position based on total obtained marks for all students in the course
    all_students = Student.objects.filter(class_id=student.class_id)
    all_students_results = [
        {'student': student, 'total_marks': get_total_obtained_marks(student)}
        for student in all_students
    ]
    sorted_results = sorted(all_students_results, key=lambda x: x['total_marks'], reverse=True)
    overall_merit_position = next((index + 1 for index, result in enumerate(sorted_results) if result['student'] == student), None)

    # Find the highest mark obtained by any student in the course for merit calculation
    highest_total_marks = max(result['total_marks'] for result in sorted_results) if sorted_results else 0

    # Prepare results with details and merit position for each result
    results_with_details = []
    for exam in all_exams:
        mcq_result = mcq_results_dict.get(exam.id)
        written_result = written_results_dict.get(exam.id)
        model_name = 'live_exam'  # Assuming 'live_exam' as the model name for all exams
        highest_marks = highest_live_marks

        # Calculate merit position for this specific exam
        obtained_marks = 0
        mcq_obtained_marks = mcq_result.marks if mcq_result else 0
        written_obtained_marks = written_result.marks if written_result else 0
        obtained_marks = mcq_obtained_marks + written_obtained_marks

        all_exam_results = Live_Exam_Result.objects.filter(exam=exam).order_by('-marks')
        exam_merit_position = next((index + 1 for index, r in enumerate(all_exam_results) if r.student == student), None)

        results_with_details.append({
            'exam': exam,
            'model_name': model_name,
            'mcq_obtained_marks': mcq_obtained_marks,
            'written_obtained_marks': written_obtained_marks,
            'obtained_marks': obtained_marks,
            'total_marks': exam.total_marks,
            'highest_marks': highest_marks,
            'merit_position': exam_merit_position,
        })

    # Total exam marks for all results
    total_exam_mark = sum(exam.total_marks for exam in all_exams)

    # Determine overall merit position, set to 0 if highest_total_marks is 0
    overall_merit_position = overall_merit_position if highest_total_marks > 0 else 0

    context = {
        'course': course,
        'subject': subject,
        'all_results': results_with_details,
        'total_exam_mark': total_exam_mark,
        'total_obtain_mark': student_total_obtained_marks,
        'total_mcq_obtain_mark': total_mcq_obtained_marks,
        'total_written_obtain_mark': total_written_obtained_marks,
        'total_possible_marks': total_possible_marks,
        'merit_position': overall_merit_position,
        'course_name': course.name,
        'highest_total_marks': highest_total_marks  # This is for merit calculation table
    }
    return render(request, 'student/performance.html', context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_PERFORMANCE_VIEW_QUESTION(request,id):
    exam = Live_Exam.objects.get(id = id)
    questions = LiveExamMCQQuestion.objects.filter(exam=exam)
    context={
        'question':questions,
        'exam':exam
    }
    return render(request,'student/performance_view_question.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 3, login_url='login')
def STUDENT_PAST_EXAM(request):
    student = request.user.student
    live_exams = Live_Exam.objects.all()
    practice_exams = Practice_Exam.objects.all()

    live_exam_reports = {report.exam_id: report for report in Live_Exam_MCQ_Report.objects.filter(user=request.user)}
    practice_exam_results = {result.exam_id: result for result in Practice_Exam_Result.objects.filter(student=student)}
    written_answers = {answer.question.exam_id: answer for answer in LiveExamStudentWrittenAnswer.objects.filter(student=student)}

    # Merge and sort exams by date
    all_exams = sorted(
        chain(
            [(exam, 'live') for exam in live_exams],
            [(exam, 'practice') for exam in practice_exams]
        ),
        key=lambda x: x[0].created_at,
        reverse=True
    )

    context = {
        'all_exams': all_exams,
        'live_exam_reports': live_exam_reports,
        'practice_exam_results': practice_exam_results,
        'written_answers': written_answers,
    }
    return render(request, 'student/past_exam.html', context)




