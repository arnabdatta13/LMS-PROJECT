from django.shortcuts import render,redirect
from app.models import Course,Session_Year,CustomUser,Student,Teacher,Subject,Star_student,Student_activity,Teacher_Feedback,Student_Notification,Attendance_Report,Attendance,Class,Add_Notification,PracticeExamQuestion,Practice_Exam,OnlineLiveClass,Live_Exam,LiveExamMCQQuestion,Live_Exam_Result,LiveExamWrittenQuestion,LiveExamStudentWrittenAnswer,Live_Exam_Written_Result,Student_Feedback,SchoolExamStudentResult,School_Official_Exam,Notice,StudentQuestion,TeacherTextAnswer,TeacherAudioAnswer,TeacherPhotoAnswer,ImageGallery
from django.contrib import messages
from operator import attrgetter
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db.models import Sum,Max
import requests
import json
from django.http import JsonResponse
import base64
import hmac
import hashlib
import time
from datetime import timedelta,datetime
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
from collections import defaultdict
from student_management_system.ai_generated_mcq_question import RESPONSE_JSON,generate_evaluate_chain
from langchain.callbacks import get_openai_callback


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

    # Calculate attendance percentages
    attendance_data = Attendance.objects.all()
    attendance_report = defaultdict(lambda: {'present': 0, 'absent': 0})

    for attendance in attendance_data:
        year = attendance.attendance_date.year
        total_students = Student.objects.filter(class_id=attendance.class_id).count()
        present_students = Attendance_Report.objects.filter(attendance_id=attendance).count()
        absent_students = total_students - present_students

        attendance_report[year]['present'] += present_students
        attendance_report[year]['absent'] += absent_students

    # Calculate percentages
    attendance_percentages = {}
    for year, data in attendance_report.items():
        total = data['present'] + data['absent']
        if total > 0:
            attendance_percentages[year] = {
                'present': (data['present'] / total) * 100,
                'absent': (data['absent'] / total) * 100,
            }

    years = SchoolExamStudentResult.objects.dates('created_at', 'year')
    classes = Class.objects.all()
    if request.method == "POST":
        data = json.loads(request.body)
        class_id = data.get("class_id")
        year = int(data.get("year"))  # Parse the year as an integer
        
        exam_results_data = []
        
        # Filter by class and year
        exam_results = SchoolExamStudentResult.objects.filter(
            student_id__class_id=class_id,
            created_at__year=year
        )

        exam_summary = {}
        for result in exam_results:
            exam_name = result.exam_id.exam_name
            
            if exam_name not in exam_summary:
                exam_summary[exam_name] = {'total_students': 0, 'pass_count': 0}

            exam_summary[exam_name]['total_students'] += 1
            
            # Calculate 33% of exam mark
            passing_threshold = 0.33 * result.exam_mark
            
            # Determine pass/fail based on assignment mark
            if result.assignment_mark >= passing_threshold:
                exam_summary[exam_name]['pass_count'] += 1

        # Calculate pass and fail percentages
        for exam_name, summary in exam_summary.items():
            total_students = summary['total_students']
            pass_percentage = (summary['pass_count'] / total_students) * 100
            fail_percentage = 100 - pass_percentage
            exam_results_data.append({
                'exam_name': exam_name,
                'pass_percentage': pass_percentage,
                'fail_percentage': fail_percentage
            })

        return JsonResponse({'results': exam_results_data})


    #overall_exam_results
    overall_exam_results_data = []
    
    # Calculate overall pass/fail percentages for all exams
    exam_results = SchoolExamStudentResult.objects.all()
    exam_summary = {'total_students': 0, 'pass_count': 0}

    for result in exam_results:
        exam_summary['total_students'] += 1
        
        # Calculate 33% of exam mark for pass threshold
        passing_threshold = 0.33 * result.exam_mark
        
        # Determine pass/fail based on assignment mark
        if result.assignment_mark >= passing_threshold:
            exam_summary['pass_count'] += 1

    # Calculate pass and fail percentages
    total_students = exam_summary['total_students']
    if total_students > 0:
        pass_percentage = (exam_summary['pass_count'] / total_students) * 100
        fail_percentage = 100 - pass_percentage
    else:
        pass_percentage = 0
        fail_percentage = 0

    overall_exam_results_data = {
        'pass_percentage': pass_percentage,
        'fail_percentage': fail_percentage
    }
    print(overall_exam_results_data)

    context = {
        'student_count':student_count,
        'teacher_count':teacher_count,
        'course_count':course_count,
        'exam_count':exam_count,
        'student_gender_male':student_gender_male,
        'student_gender_female': student_gender_female,
        'star_student':star_student,
        'student_activity':student_activity,
        'attendance_percentages': attendance_percentages,  # Pass attendance data to template
        "years": [date.year for date in years],
        "classes":classes,
        "exam_results_json": json.dumps([]),  # Send the exam results to the front-end
        'overall_exam_results_json': json.dumps(overall_exam_results_data)  # Convert to JSON for JavaScript
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
    
    return render(request, 'teacher/student/add_student.html',context)


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
    return render(request,'teacher/student/view_student.html',context)



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


    return render(request,'teacher/attendance/take_attendance.html',context)



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
    return render(request, 'teacher/attendance/view_attendance.html', context)







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
    return render(request,'teacher/school_result/add_result.html',context)




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
    return render(request, 'teacher/school_result/view_result.html', context)

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
    return render(request, 'teacher/school_result/show_result.html', context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_EDIT_RESULT(request,id):
    result = SchoolExamStudentResult.objects.get(id=id)

    context = {
        'result':result,
    }
    return render(request,'teacher/school_result/edit_result.html',context)



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
def LIVE_EXAM_ADD(request):
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
    return render(request,'teacher/live_exam/add_live_exam.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def LIVE_EXAM_SAVE(request):
    if request.method == "POST":

        class_id= request.POST.get('class_id')
        exam_name= request.POST.get('exam_name')
        total_questions= request.POST.get('total_question')
        total_marks= request.POST.get('total_number')
        
        course_id= request.POST.get('course_id')
        subject_id= request.POST.get('subject_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        duration = int(request.POST.get('duration'))

        class1= Class.objects.get(id=class_id)
        course = Course.objects.get(id=course_id)
        subject = Subject.objects.get(id=subject_id)

        start_time = timezone.make_aware(datetime.strptime(start_time, '%Y-%m-%dT%H:%M'))
        end_time = timezone.make_aware(datetime.strptime(end_time, '%Y-%m-%dT%H:%M'))
        print(start_time)
        print(end_time)

        duration = timedelta(minutes=duration)
        exam = Live_Exam(
            exam_name= exam_name,
            total_questions=total_questions,
            total_marks=total_marks,
            class_id=class1,
            course = course,
            subject= subject,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
        )
        exam.save()
        messages.success(request,'Exam Are Successfully Added')
        return redirect('teacher-live-exam-add')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def LIVE_EXAM_VIEW(request):
    current_time = timezone.localtime(timezone.now())  # Get the current time in the local timezone
    #print(current_time)
    exam = Live_Exam.objects.all()
    course= Course.objects.all()
    classes = Class.objects.all()
    selected_course = request.GET.get('course_filter', '')
    search_query = request.GET.get('search_query', '')  
    class_filter = request.GET.get('class_filter', '')

    if class_filter:
        exam = exam.filter(class_id=class_filter)

    if selected_course:
        exam = exam.filter(course=selected_course)


    # Sort exams: ongoing/future exams first, then expired ones
    exam = exam.annotate(
        exam_status=Case(
            When(start_time__lte=current_time, end_time__gte=current_time, then=Value(0)),  # Ongoing
            When(start_time__gt=current_time, then=Value(1)),  # Upcoming
            When(end_time__lt=current_time, then=Value(2)),  # Expired
            output_field=IntegerField(),
        )
    ).order_by('exam_status', 'start_time')


    context= {
        'exam':exam,
        'classes':classes,
        'search_query':search_query,
        'selected_class':class_filter,
        'course':course,
        'selected_course': selected_course,
        'current_time': current_time, 
    }
    return render(request,'teacher/live_exam/view_live_exam.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def LIVE_EXAM_EDIT(request, id):
    exam = Live_Exam.objects.get(id=id)
    class_id = exam.class_id
    course = Course.objects.filter(class1=class_id)
    subject = Subject.objects.filter(class1=class_id)
    
    # Format the start and end times
    start_time_formatted = exam.start_time.strftime('%m-%d-%y,%I:%M %p')
    end_time_formatted = exam.end_time.strftime('%m-%d-%y,%I:%M %p')

    context = {
        'exam': exam,
        'class': class_id,
        'course': course,
        'subject': subject,
        'start_time_formatted': start_time_formatted,
        'end_time_formatted': end_time_formatted,
    }
    
    return render(request, 'teacher/live_exam/edit_live_exam.html', context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def LIVE_EXAM_UPDATE(request):
    if request.method == 'POST':
        # Retrieve POST data
        exam_id = request.POST.get('exam_id')
        exam_name = request.POST.get('exam_name').strip()
        total_questions = int(request.POST.get('total_question'))
        total_marks = int(request.POST.get('total_number'))
        class_id = request.POST.get('class_id')
        course_id = request.POST.get('course_id')
        subject_id = request.POST.get('subject_id')
        start_time_str = request.POST.get('start_time').strip()
        end_time_str = request.POST.get('end_time').strip()
        duration = request.POST.get('duration').strip()

        # Parse the start and end times with the correct format
        start_time = datetime.strptime(start_time_str, '%m-%d-%y,%I:%M %p').strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time_str, '%m-%d-%y,%I:%M %p').strftime('%Y-%m-%d %H:%M:%S')

        # Convert duration string to timedelta
        hours, minutes, seconds = map(int, duration.split(':'))
        duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        
        # Fetch the exam instance
        exam = Live_Exam.objects.get(id=exam_id)
        class1 = Class.objects.get(id=class_id)
        course = Course.objects.get(id=course_id)
        subject = Subject.objects.get(id=subject_id)
        # Update the exam instance with new data
        exam.exam_name = exam_name
        exam.total_questions = total_questions
        exam.total_marks = total_marks
        exam.class_id = class1
        exam.course = course
        exam.subject = subject
        exam.start_time = start_time
        exam.end_time = end_time
        exam.duration = duration

        # Save the updated exam
        exam.save()

        messages.success(request, "Live Exam updated successfully.")
        return redirect('teacher-live-exam-view')    
        



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def LIVE_EXAM_DELETE(request,id):
    exam = Live_Exam.objects.get(id = id)
    exam.delete()

    messages.success(request,'Exam Are Successfully Deleted')

    return redirect('teacher-live-exam-view')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def ADD_LIVE_EXAM_MCQ_QUESTION(request):
    current_time = timezone.now()
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
            exam = Live_Exam.objects.filter(class_id=class_id,end_time__gt=current_time)
            

    context = {
        
        'class':class1,
        'action':action,
        'get_class':get_class,
        
        'subject': subject,
        
        'course':course,
        'exam':exam,

    }
    return render(request,'teacher/live_exam/add_live_exam_mcq_question.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def SAVE_LIVE_EXAM_MCQ_QUESTION(request):
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        exam = Live_Exam.objects.get(id=exam_id)
        existing_questions_count = LiveExamMCQQuestion.objects.filter(exam=exam).count()
        total_questions_allowed = exam.total_questions

        # Calculate the sum of marks for existing questions
        existing_total_marks = LiveExamMCQQuestion.objects.filter(exam=exam).aggregate(total_marks=Sum('marks'))['total_marks'] or 0
        total_marks_allowed = exam.total_marks

        question_counter = 1
        added_questions_count = 0
        added_marks = 0

        while True:
            question_key = f'question{question_counter}' if question_counter > 1 else 'question'
            mark_key = f'mark{question_counter}' if question_counter > 1 else 'mark'
            option1_key = f'option1{question_counter}' if question_counter > 1 else 'option1'
            option2_key = f'option2{question_counter}' if question_counter > 1 else 'option2'
            option3_key = f'option3{question_counter}' if question_counter > 1 else 'option3'
            option4_key = f'option4{question_counter}' if question_counter > 1 else 'option4'
            answer_key = f'answer{question_counter}' if question_counter > 1 else 'answer'
            solution_key = f'solution{question_counter}' if question_counter > 1 else 'solution'

            question_text = request.POST.get(question_key)
            marks_str = request.POST.get(mark_key)
            option1 = request.POST.get(option1_key)
            option2 = request.POST.get(option2_key)
            option3 = request.POST.get(option3_key)
            option4 = request.POST.get(option4_key)
            answer = request.POST.get(answer_key)
            solution = request.POST.get(solution_key)

            if not question_text:
                break

            try:
                marks = int(marks_str)
            except (ValueError, TypeError):
                messages.error(request, f'Invalid marks value: {marks_str}')
                return redirect('teacher-add-live-exam-mcq-question')

            if existing_questions_count + added_questions_count >= total_questions_allowed:
                messages.error(request, 'You cannot add more questions than the total number allowed for this exam.')
                return redirect('teacher-add-live-exam-mcq-question')

            new_total_marks = existing_total_marks + added_marks + marks
            if new_total_marks > total_marks_allowed:
                messages.error(request, 'You cannot add more marks than the total marks allowed for this exam.')
                return redirect('teacher-add-live-exam-mcq-question')

            # Create and save the question object
            LiveExamMCQQuestion.objects.create(
                exam=exam,
                marks=marks,
                question=question_text,
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4,
                answer=answer,
                solution_details=solution
            )
            
            added_questions_count += 1
            added_marks += marks
            question_counter += 1

        messages.success(request, 'Questions are added successfully')
        return redirect('teacher-add-live-exam-mcq-question')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_LIVE_EXAM_MCQ_QUESTION_FILTER(request):
    exam = Live_Exam.objects.all()
    current_time = timezone.now()
    context = {
        'exam':exam,   
        "current_time":current_time,
    }

    return render(request,'teacher/live_exam/view_live_exam_mcq_question_filter.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_LIVE_EXAM_MCQ_QUESTION(request,id):
    exam = Live_Exam.objects.get(id = id)

    question = LiveExamMCQQuestion.objects.filter(exam=exam)

    context = {
        'exam':exam,
        'question':question,
    }
    return render(request,'teacher/live_exam/view_live_exam_mcq_question.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def EDIT_LIVE_EXAM_MCQ_QUESTION(request,id):
    exam = Live_Exam.objects.all()
    question = LiveExamMCQQuestion.objects.filter(id = id)

    context = {
        'exam':exam,
        'question':question,
    }
    return render(request,'teacher/live_exam/edit_live_exam_mcq_question.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def UPDATE_LIVE_EXAM_MCQ_QUESTION(request):
    if request.method == "POST":
        exam_id = request.POST.get('exam_id')
        question_text = request.POST.get('question')
        question_id = request.POST.get('question_id')
        marks = request.POST.get('mark')
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        option4 = request.POST.get('option4')
        answer = request.POST.get('answer')
        solution = request.POST.get('solution')
        exam= Live_Exam.objects.get(id = exam_id)
        question = LiveExamMCQQuestion.objects.get(id = question_id)

        question.exam=exam
        question.marks=marks
        question.question=question_text
        question.option1=option1
        question.option2=option2
        question.option3=option3
        question.option4=option4
        question.answer=answer
        question.solution_details=solution

        question.save()

        messages.success(request,'Queation Are Successfully Updated')
        return redirect('teacher-view-live-exam-mcq-question')





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def DELETE_LIVE_EXAM_MCQ_QUESTION(request,id):

    question = LiveExamMCQQuestion.objects.get(id = id)
    question.delete()

    messages.success(request,'Question are successfully deleted.')

    return redirect('teacher-view-live-exam-mcq-question')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def ADD_LIVE_EXAM_WRITTEN_QUESTION(request):
    current_time = timezone.now()
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
            exam = Live_Exam.objects.filter(class_id=class_id,end_time__gt=current_time)
            
    context = {
        'class':class1,
        'action':action,
        'get_class':get_class,
        'subject': subject,
        'course':course,
        'exam':exam,

    }
    return render(request,"teacher/live_exam/add_live_exam_written_question.html",context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def SAVE_LIVE_EXAM_WRITTEN_QUESTION(request):
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        exam = Live_Exam.objects.get(id=exam_id)
        existing_questions_count = LiveExamWrittenQuestion.objects.filter(exam=exam).count()
        total_questions_allowed = exam.total_questions

        # Calculate the sum of marks for existing questions
        existing_total_marks = LiveExamWrittenQuestion.objects.filter(exam=exam).aggregate(total_marks=Sum('marks'))['total_marks'] or 0
        total_marks_allowed = exam.total_marks

        question_counter = 1
        added_questions_count = 0
        added_marks = 0

        while True:
            question_key = f'question{question_counter}' if question_counter > 1 else 'question'
            mark_key = f'mark{question_counter}' if question_counter > 1 else 'mark'
            solution_key = f'solution{question_counter}' if question_counter > 1 else 'solution'

            question_text = request.POST.get(question_key)
            marks_str = request.POST.get(mark_key)
            solution = request.POST.get(solution_key)

            if not question_text:
                break

            try:
                marks = int(marks_str)
            except (ValueError, TypeError):
                messages.error(request, f'Invalid marks value: {marks_str}')
                return redirect('teacher-add-live-exam-written-question')

            if existing_questions_count + added_questions_count >= total_questions_allowed:
                messages.error(request, 'You cannot add more questions than the total number allowed for this exam.')
                return redirect('teacher-add-live-exam-written-question')

            new_total_marks = existing_total_marks + added_marks + marks
            if new_total_marks > total_marks_allowed:
                messages.error(request, 'You cannot add more marks than the total marks allowed for this exam.')
                return redirect('teacher-add-live-exam-written-question')

            # Create and save the question object
            LiveExamWrittenQuestion.objects.create(
                exam=exam,
                marks=marks,
                question=question_text,
                solution_details=solution
            )
            
            added_questions_count += 1
            added_marks += marks
            question_counter += 1

        messages.success(request, 'Questions are added successfully')
        return redirect('teacher-add-live-exam-written-question')


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_LIVE_EXAM_WRITTEN_QUESTION_FILTER(request):
    exam = Live_Exam.objects.all()

    context = {
        'exam':exam,   
    }

    return render(request,'teacher/live_exam/view_live_exam_written_question_filter.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_LIVE_EXAM_WRITTEN_QUESTION(request,id):
    exam = Live_Exam.objects.get(id = id)

    question = LiveExamWrittenQuestion.objects.filter(exam=exam)

    context = {
        'exam':exam,
        'question':question,
    }
    return render(request,'teacher/live_exam/view_live_exam_written_question.html',context)





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def EDIT_LIVE_EXAM_WRITTEN_QUESTION(request,id):
    exam = Live_Exam.objects.all()
    question = LiveExamWrittenQuestion.objects.filter(id = id)

    context = {
        'exam':exam,
        'question':question,
    }
    return render(request,'teacher/live_exam/edit_live_exam_written_question.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def UPDATE_LIVE_EXAM_WRITTEN_QUESTION(request):
    if request.method == "POST":
        exam_id = request.POST.get('exam_id')
        question_text = request.POST.get('question')
        question_id = request.POST.get('question_id')
        marks = request.POST.get('mark')
        solution = request.POST.get('solution')
        exam= Live_Exam.objects.get(id = exam_id)
        question = LiveExamWrittenQuestion.objects.get(id = question_id)

        question.exam=exam
        question.marks=marks
        question.question=question_text
        question.solution_details=solution

        question.save()

        messages.success(request,'Queation Are Successfully Updated')
        return redirect('teacher-view-live-exam-written-question')





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 1, login_url='login')
def DELETE_LIVE_EXAM_WRITTEN_QUESTION(request,id):

    question = LiveExamWrittenQuestion.objects.get(id = id)
    question.delete()

    messages.success(request,'Question are successfully deleted.')

    return redirect('admin-view-live-exam-written-question')





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
    return render(request,'teacher/practice_exam/add_practice_exam.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def PRACTICE_EXAM_SAVE(request):
    if request.method == "POST":

        class_id= request.POST.get('class_id')
        exam_name= request.POST.get('exam_name')
        total_questions= request.POST.get('total_question')
        total_marks= request.POST.get('total_number')
        
        course_id= request.POST.get('course_id')
        subject_id= request.POST.get('subject_id')
        duration = int(request.POST.get('duration'))

        print(class_id)
        class1= Class.objects.get(id=class_id)
        course = Course.objects.get(id=course_id)
        subject = Subject.objects.get(id=subject_id)


        duration = timedelta(minutes=duration)
        exam = Practice_Exam(
            exam_name= exam_name,
            total_questions=total_questions,
            total_marks=total_marks,
            class_id=class1,
            course = course,
            subject= subject,
            duration=duration,
        )
        exam.save()
        messages.success(request,'Exam Are Successfully Added')
        return redirect('teacher-practice-exam-add')


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def PRACTICE_EXAM_VIEW(request):
    exam = Practice_Exam.objects.all()
    course= Course.objects.all()
    classes = Class.objects.all()
    selected_course = request.GET.get('course_filter', '')
    search_query = request.GET.get('search_query', '')  
    class_filter = request.GET.get('class_filter', '')

    if class_filter:
        exam = exam.filter(class_id=class_filter)

    if selected_course:
        exam = exam.filter(course=selected_course)

    context= {
        'exam':exam,
        'classes':classes,
        'search_query':search_query,
        'selected_class':class_filter,
        'course':course,
        'selected_course': selected_course,
    }
    return render(request,'teacher/practice_exam/view_practice_exam.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
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
    
    return render(request,'teacher/practice_exam/edit_practice_exam.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def PRACTICE_EXAM_UPDATE(request):
    if request.method == "POST":
        exam_id = request.POST.get('exam_id')
        class_id= request.POST.get('class_id')
        exam_name= request.POST.get('exam_name')
        total_questions= request.POST.get('total_question')
        total_marks= request.POST.get('total_number')
        
        course_id= request.POST.get('course_id')
        subject_id= request.POST.get('subject_id')

        duration_str = request.POST.get('duration') 

        hours, minutes, seconds = map(int, duration_str.strip().split(':'))
        duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        
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
        exam.duration=duration
        exam.save()
        messages.success(request,'Practice Exam Are Successfully Updated')
        return redirect('teacher-practice-exam-view')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def PRACTICE_EXAM_DELETE(request,id):
    exam = Practice_Exam.objects.get(id = id)
    exam.delete()

    messages.success(request,'Exam Are Successfully Deleted')

    return redirect('teacher-practice-exam-view')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def ADD_PRACTICE_EXAM_QUESTION(request):
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
    return render(request,'teacher/practice_exam/add_practice_exam_question.html',context)





@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def SAVE_PRACTICE_EXAM_QUESTION(request):
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        exam = Practice_Exam.objects.get(id=exam_id)
        existing_questions_count = PracticeExamQuestion.objects.filter(exam=exam).count()
        total_questions_allowed = exam.total_questions

        # Calculate the sum of marks for existing questions
        existing_total_marks = PracticeExamQuestion.objects.filter(exam=exam).aggregate(total_marks=Sum('marks'))['total_marks'] or 0
        total_marks_allowed = exam.total_marks

        question_counter = 1
        added_questions_count = 0
        added_marks = 0

        while True:
            question_key = f'question{question_counter}' if question_counter > 1 else 'question'
            mark_key = f'mark{question_counter}' if question_counter > 1 else 'mark'
            option1_key = f'option1{question_counter}' if question_counter > 1 else 'option1'
            option2_key = f'option2{question_counter}' if question_counter > 1 else 'option2'
            option3_key = f'option3{question_counter}' if question_counter > 1 else 'option3'
            option4_key = f'option4{question_counter}' if question_counter > 1 else 'option4'
            answer_key = f'answer{question_counter}' if question_counter > 1 else 'answer'
            solution_key = f'solution{question_counter}' if question_counter > 1 else 'solution'

            
            question_text = request.POST.get(question_key)
            marks = request.POST.get(mark_key)
            option1 = request.POST.get(option1_key)
            option2 = request.POST.get(option2_key)
            option3 = request.POST.get(option3_key)
            option4 = request.POST.get(option4_key)
            answer = request.POST.get(answer_key)
            solution = request.POST.get(solution_key)

            if not question_text:
                break

            if existing_questions_count + added_questions_count > total_questions_allowed:
                messages.error(request, 'You cannot add more questions than the total number allowed for this exam.')
                return redirect('teacher-add-practice-exam-question')

            if existing_total_marks + added_marks + int(marks) > total_marks_allowed:
                messages.error(request, 'You cannot add more marks than the total marks allowed for this exam.')
                return redirect('teacher-add-practice-exam-question')

            # Create and save the question object
            PracticeExamQuestion.objects.create(
                exam=exam,
                marks=marks,
                question=question_text,
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4,
                answer=answer,
                solution_details = solution
            )
            
            added_questions_count += 1
            added_marks += int(marks)
            question_counter += 1
        
        messages.success(request, 'Questions are added successfully')
        return redirect('teacher-add-practice-exam-question')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_PRACTICE_EXAM_QUESTION_FILTER(request):
    exam = Practice_Exam.objects.all()

    context = {
        'question':exam,
       
    }
    return render(request,'teacher/practice_exam/view_practice_exam_question_filter.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_PRACTICE_EXAM_QUESTION(request,id):
    exam = Practice_Exam.objects.get(id = id)

    question = PracticeExamQuestion.objects.filter(exam=exam)

    context = {
        'exam':exam,
        'question':question,
    }
    return render(request,'teacher/practice_exam/view_practice_exam_question.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def EDIT_PRACTICE_EXAM_QUESTION(request,id):
    exam = Practice_Exam.objects.all()
    question = PracticeExamQuestion.objects.filter(id = id)

    context = {
        'exam':exam,
        'question':question,
    }
    return render(request,'teacher/practice_exam/edit_practice_exam_question.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def UPDATE_PRACTICE_EXAM_QUESTION(request):
    if request.method == "POST":
        exam_id = request.POST.get('exam_id')
        question_text = request.POST.get('question')
        question_id = request.POST.get('question_id')
        marks = request.POST.get('mark')
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        option4 = request.POST.get('option4')
        answer = request.POST.get('answer')
        solution = request.POST.get('solution')

        exam= Practice_Exam.objects.get(id = exam_id)
        question = PracticeExamQuestion.objects.get(id = question_id)

        question.exam=exam
        question.marks=marks
        question.question=question_text
        question.option1=option1
        question.option2=option2
        question.option3=option3
        question.option4=option4
        question.answer=answer
        question.solution_details=solution

        question.save()

        messages.success(request,'Queation Are Successfully Updated')
        return redirect('teacher-view-practice-exam-question')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def DELETE_PRACTICE_EXAM_QUESTION(request,id):

    question = PracticeExamQuestion.objects.get(id = id)
    question.delete()

    messages.success(request,'Question are successfully deleted.')

    return redirect('teacher-view-practice-exam-question')






@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_STUDENT_PERFORMANCE_COURSE(request):
    course = Course.objects.all()

    context = {
        'course':course,
    }
    return render(request,'teacher/performance/view_student_performance_course.html',context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_STUDENT_PERFORMANCE_STUDENT(request,id):
    course = Course.objects.get(id = id)
    class1 = course.class1

    student = Student.objects.filter(class_id=class1)


    context = {
        "course":course,
        'student':student,
    }
    return render(request,'teacher/performance/view_student_performance_student.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_STUDENT_PERFORMANCE(request,course_id, student_id):
    course = Course.objects.get(id=course_id)
    student_id= Student.objects.get(id = student_id)
    subject = Subject.objects.filter(class1=student_id.class_id)

    # Get all exams for the course
    all_exams = Live_Exam.objects.filter(course=course)

    # Get the results for live exams
    live_exam_results = Live_Exam_Result.objects.filter(exam__course=course, student=student_id)

    # Create a dictionary to map exams to results
    exam_results_dict = {result.exam.id: result for result in live_exam_results}

    # Calculate the highest marks in the course for live exams
    highest_live_marks = Live_Exam_Result.objects.filter(exam__course=course).aggregate(max_marks=Max('marks'))['max_marks'] or 0

    # Function to get the sum of obtained marks for a student
    def get_total_obtained_marks(student):
        live_exam_sum = Live_Exam_Result.objects.filter(exam__course=course, student=student).aggregate(total_marks=Sum('marks'))['total_marks'] or 0
        return live_exam_sum

    # Calculate the student's total obtained marks
    student_total_obtained_marks = get_total_obtained_marks(student_id)

    # Calculate merit position based on total obtained marks for all students in the course
    all_students = Student.objects.filter(class_id=student_id.class_id)
    all_students_results = [
        {'student': student, 'total_marks': get_total_obtained_marks(student)}
        for student in all_students
    ]
    sorted_results = sorted(all_students_results, key=lambda x: x['total_marks'], reverse=True)
    overall_merit_position = next((index + 1 for index, result in enumerate(sorted_results) if result['student'] == student_id), None)

    # Find the highest mark obtained by any student in the course for merit calculation
    highest_total_marks = max(result['total_marks'] for result in sorted_results) if sorted_results else 0

    # Prepare results with details and merit position for each result
    results_with_details = []
    for exam in all_exams:
        result = exam_results_dict.get(exam.id)
        model_name = result.exam._meta.model_name if result else 'N/A'
        highest_marks = highest_live_marks

        # Calculate merit position for this specific exam
        if result:
            all_exam_results = Live_Exam_Result.objects.filter(exam=exam).order_by('-marks')
            exam_merit_position = next((index + 1 for index, r in enumerate(all_exam_results) if r.student == student_id), None)
            obtained_marks = result.marks
        else:
            exam_merit_position = 0
            obtained_marks = 0

        results_with_details.append({
            'exam': exam,
            'result': result,
            'model_name': model_name,
            'highest_marks': highest_marks,
            'merit_position': exam_merit_position,
            'obtained_marks': obtained_marks,
            'total_marks': exam.total_marks,
        })

    # Total exam marks for all results
    total_exam_mark = sum(exam.total_marks for exam in all_exams)

    # Determine overall merit position, set to 0 if highest_total_marks is 0
    overall_merit_position = overall_merit_position if highest_total_marks > 0 else 0

    context = {
        "student":student_id,
        'course': course,
        'subject': subject,
        'all_results': results_with_details,
        'total_exam_mark': total_exam_mark,
        'total_obtain_mark': student_total_obtained_marks,
        'merit_position': overall_merit_position,
        'course_name': course.name,
        'highest_total_marks': highest_total_marks  # This is for merit calculation table
    }
    return render(request, 'teacher/performance/view_student_performance.html', context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STUDENT_PERFORMANCE_VIEW_QUESTION(request,id):
    exam = Live_Exam.objects.get(id = id)
    questions = LiveExamMCQQuestion.objects.filter(exam=exam)
    context={
        'question':questions,
        'exam':exam
    }
    return render(request,'teacher/performance/performance_view_question.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_ADD_NOTIFICATION(request):

    if request.method== "POST":
        notification= request.POST.get('notification')
        notice1 = Add_Notification(
            notification = notification,
        )
        notice1.save()
        messages.success(request,'Notification Are Successfully Created')
        return redirect('teacher-add-notification')

    return render(request,'teacher/add_notification.html')



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_VIEW_NOTIFICATION(request):
    notification  = Add_Notification.objects.all()
    context = {
        "notification":notification,
    }
    return render(request,"teacher/view_notification.html",context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_DELETE_NOTIFICATION(request,id):
    notification = Add_Notification.objects.get(id = id)

    notification.delete()
    messages.success(request, "Notification is deleted successfully")
    return redirect('teacher-view-notification')




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
    
    return render(request,'teacher/star_student/add_star_student.html',context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STAR_STUDENT_EDIT(request,id):
    star_student = Star_student.objects.filter(id = id)
    class1 = Class.objects.all()
    context= {
        'star_student':star_student,
        'class':class1,
    }
    
    return render(request,'teacher/star_student/edit_star_student.html',context)




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

    
    return render(request,'teacher/student_activity/add_student_activity.html')




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STUDENT_ACTIVITY_VIEW(request):
    student_activity= Student_activity.objects.all()

    context = {
        'student_activity':student_activity,
    }

    return render(request,'teacher/student_activity/view_student_activity.html',context)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def STUDENT_ACTIVITY_EDIT(request,id):
    student_activity= Student_activity.objects.get(id = id)

    context = {
        'student_activity':student_activity,
    }
    return render(request,'student/student_activity/edit_student_activity.html',context)



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
            return render(request, "teacher/live_exam_student_written_answer/student_written_answer_filter.html", {"action": "Show-Courses", "courses": courses, "selected_class_id": selected_class_id})
        
        elif action == 'Show-Exams':
            selected_class_id = request.POST.get('class_id')
            selected_course_id = request.POST.get('course_id')
            exams = Live_Exam.objects.filter(course_id=selected_course_id)
            return render(request, "teacher/live_exam_student_written_answer/student_written_answer_filter.html", {"action": "Show-Exams", "exams": exams, "selected_course_id": selected_course_id, "selected_class_id": selected_class_id})
        
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
            return render(request, "teacher/live_exam_student_written_answer/student_written_answer_filter.html", context)
    else:
        classes = Class.objects.all()
        return render(request, "teacher/live_exam_student_written_answer/student_written_answer_filter.html", {"classes": classes})
   


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
    
    return render(request, 'teacher/live_exam_student_written_answer/student_written_answer.html', context)




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
  







#online class implement

def get_zoom_access_token():
    url = "https://zoom.us/oauth/token"
    payload = {
        'account_id': 'lU13tpFVSwO_zEhMMXAO_w',
        'client_id': '6ptiKZuYSjyb2pHzJyHTA',
        'client_secret': '4acUTxYAd94H1krPFhtlmVkaKQNVKo4m',
        'grant_type': 'account_credentials'
    }
    response = requests.post(url, data=payload)
    access_token = json.loads(response.text).get('access_token')
    return access_token


def get_zak_token(access_token):
    zak_url = "https://api.zoom.us/v2/users/me/token?type=zak"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(zak_url, headers=headers)
    response_data = response.json()
    
    # Check if response contains the token
    if 'token' in response_data:
        return response_data['token']
    else:
        # If token is not present, raise an error or return None
        raise ValueError("ZAK token not found in response")



def schedule_zoom_meeting(access_token,topic,start_time,duration):
    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    meeting_details = {
        "topic": topic,
        "type": 2,
        "start_time": start_time,
        "duration": duration,  # Duration in minutes
        "schedule_for": "arnabdatta83@gmail.com",
        "timezone": "Asia/Dhaka",
        "agenda": "Discussion on the project.",
        "settings": {
            "join_before_host": False,  # Prevent participants from joining before the host
            "jbh_time": 0,  # Disable the option to join before host by any minutes
            "waiting_room": False,  # Enable waiting room, optional but recommended for better control
            "auto_admit_participants": True
        }
    }

    response = requests.post(url, headers=headers, json=meeting_details)
    return json.loads(response.text)

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def ADD_ONLINE_LIVE_CLASS(request):
    class1 = Class.objects.all()
    course = Course.objects.all()
    if request.method == "POST":

        access_token = get_zoom_access_token()

        topic = request.POST.get('topic')
        start_time = request.POST.get('start_time')
        duration = request.POST.get('duration')
        class_id = request.POST.get('class_id')
        course = request.POST.get("course")
        start_time = timezone.make_aware(datetime.strptime(start_time, '%Y-%m-%dT%H:%M'))
        start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        class1 = Class.objects.get(id = class_id)
        course = Course.objects.get(id = course)
        meeting_data = schedule_zoom_meeting(access_token,topic,start_time,duration)
        print(meeting_data)
        OnlineLiveClass.objects.create(
            topic=meeting_data['topic'],
            start_time=meeting_data['start_time'],
            duration=meeting_data['duration'],
            class1=class1,
            course = course,
            zoom_meeting_id=meeting_data['id'],
            #host_email=meeting_data['host_email'],
            start_url=meeting_data['start_url'],
            join_url=meeting_data['join_url'],
            password=meeting_data['password'],
            agenda=meeting_data['agenda'] if 'agenda' in meeting_data else ''
        )
        
        messages.success(request, 'Online Live Class has been Ccreated')
        return redirect("teacher-view-online-live-class")
    context = {
        'class':class1,
        'course':course
    }
    return render(request,"teacher/online_live_class/add_online_live_class.html",context)

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_ONLINE_LIVE_CLASS(request):
    all_online_live_class= OnlineLiveClass.objects.all().order_by('-start_time')
    class1 = Class.objects.all()
    course = Course.objects.all()
    subject = Subject.objects.all()

    search_query = request.GET.get('search_query', '')  
    class_filter = request.GET.get('class_filter', '')
    course_filter = request.GET.get('course_filter', '')
    subject_filter = request.GET.get('subject_filter', '')

    if class_filter:
        all_online_live_class = all_online_live_class.filter(class1=class_filter)
    elif class_filter:
        all_online_live_class = all_online_live_class.filter(course=course_filter)

    context = {
        "classes":class1,
        "course":course,
        "subject":subject,
        "class":all_online_live_class,
    }

    return render(request,"teacher/online_live_class/view_online_live_class.html",context)

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def START_ONLINE_LIVE_CLASS(request, id):
    online_class = OnlineLiveClass.objects.get(id=id)

    # Generate the signature and other necessary data
    sdk_key = "QSLLcCXOTLmVDToDsr4itA"  # Replace with your SDK Key
    sdk_secret = "1fWY3gcWHJ7L4LRCqkQEMb5EmbXdhqWc"  # Replace with your SDK Secret
    # Step 1: Get OAuth access token
    access_token = get_zoom_access_token()
    print(access_token)
    # Step 2: Get ZAK token
    zak_token = get_zak_token(access_token)

    signature = generate_signature(sdk_key, sdk_secret, online_class.zoom_meeting_id, 1)

    context = {
        'class_id': id,
        'username': "Arnab",
        "password": online_class.password,
        "meeting_id": online_class.zoom_meeting_id,
        'signature': signature,
        'sdk_key': sdk_key,
        'zak_token': zak_token,
    }

    # Debug print to check context values
    print(context)

    return render(request, "teacher/online_live_class/start_online_live_class.html", context)



def generate_signature(api_key, api_secret, meeting_number, role):
    timestamp = int(round(time.time() * 1000)) - 30000
    msg = f"{api_key}{meeting_number}{timestamp}{role}"
    message = base64.b64encode(bytes(msg, 'utf-8'))
    secret = bytes(api_secret, 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    hash = base64.b64encode(hash.digest())
    return f"{api_key}.{meeting_number}.{timestamp}.{role}.{hash.decode('utf-8')}"


def DELETE_ONLINE_CLASS(request,id):
    online_class = OnlineLiveClass.objects.get(id = id)
    online_class.delete()
    messages.success(request,"Online Class Delete Successfully")
    return redirect("teacher-view-online-live-class")



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def ADD_NOTICE(request):
    if request.method == 'POST':
        title = request.POST.get("title")
        pdf = request.FILES.get("pdf")  # Use request.FILES to get the uploaded file
        print(pdf)
        notice = Notice(
            title = title,
            pdf = pdf
        )
        notice.save()
        messages.success(request,"Notices Are Added Successfully")
        return redirect("teacher-add-notice")

    return render(request,"teacher/notice/add_notice.html")



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def VIEW_NOTICE(request):
    notice = Notice.objects.all()

    context = {
        "notice":notice,
    }
    return render(request,"teacher/notice/view_notice.html",context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def EDIT_NOTICE(request,id):
    notice = Notice.objects.get(id = id)

    context = {
        "notice":notice,
    }

    return render(request,"teacher/notice/edit_notice.html",context)


login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def UPDATE_NOTICE(request):
    if request.method == "POST":
        notice_id = request.POST.get('notice_id')
        title = request.POST.get('title')
        pdf = request.POST.get('pdf')

        try:
            notice = Notice.objects.get(id=notice_id)
        except Session_Year.DoesNotExist:
            raise Http404("Session not found")
        
        if pdf is None or pdf == "":
            pdf = notice.pdf
        print(pdf)
        notice.title = title
        notice.pdf = pdf
        notice.save()

        messages.success(request, 'Notice was successfully updated')
        return redirect('teacher-view-notice')


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def DELETE_NOTICE(request,id):

    notice = Notice.objects.get(id = id)
    notice.delete()
    messages.success(request,"Notices Are Deleted Successfully")

    return redirect("teacher-view-notice")


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def QA(request):
    classes = Class.objects.all()  # Fetch all classes from the database

    class_filter = request.GET.get('class_filter', '')

    # Fetch questions without any related answers (text, photo, or audio)
    unanswered_questions = StudentQuestion.objects.filter(
        Q(text_answers__isnull=True) &
        Q(photo_answers__isnull=True) &
        Q(audio_answers__isnull=True)
    ).distinct()

    if class_filter:
        unanswered_questions = unanswered_questions.filter(class_id=class_filter)

    context = {
        "classes":classes,
        "unanswered_questions": unanswered_questions,
    }

    return render(request, "teacher/qa.html", context)

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_ANSWER(request,id):
    question =  StudentQuestion.objects.get(id = id)
    context = {
        "question" : question,
    }

    return render(request, "teacher/answer.html", context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def TEACHER_ANSWER_STUDENT_QUESTION(request):
    if request.method == "POST":
        user = request.user
        teacher = Teacher.objects.get(admin=user)
        
    
        answer_text = request.POST.get('text_question')
        question_id = request.POST.get("question_id")
        audio_files = request.FILES.getlist('audio')
        uploaded_files = request.FILES.getlist('files')  # Gets the list of uploaded files

        question = StudentQuestion.objects.get(id = question_id)

        TeacherTextAnswer.objects.create(
            teacher= teacher,
            question = question,
            answer_text=answer_text
        )

        for photo in uploaded_files:
            TeacherPhotoAnswer.objects.create(
                question=question, 
                photo=photo
            )
        
         # Save audio files
        for audio_file in audio_files:
            TeacherAudioAnswer.objects.create(
                question=question, 
                audio_file=audio_file
            )

        messages.success(request,"Answer has been submited successfully.")
        return redirect("teacher-qa")
    


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')  
def TEACHER_VIEW_STUDENT_QUESTION_ANSWER(request):
    classes = Class.objects.all()  # Fetch all classes from the database

    class_filter = request.GET.get('class_filter', '')


    
    # Filter questions with any type of answer from the teacher
    answered_questions = StudentQuestion.objects.filter(
        Q(text_answers__isnull=False) | 
        Q(audio_answers__isnull=False) | 
        Q(photo_answers__isnull=False)
    ).distinct()

    if class_filter:
        answered_questions = answered_questions.filter(class_id=class_filter)

    context = {
        "classes":classes,
        'answered_questions': answered_questions,
        'selected_class': class_filter,
    }
    
    return render(request, "teacher/view_answer.html", context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')  
def TEACHER_EDIT_STUDENT_QUESTION_ANSWER(request,id):
    question = StudentQuestion.objects.get(id = id)

    context = {
        "question":question,
    }
    return render(request,"teacher/edit_answer.html",context)



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')  
def TEACHER_DELETE_STUDENT_QUESTION_ANSWER(request,id):
    # Filter questions with any type of answer from the teacher
    TeacherTextAnswer.objects.filter(question_id=id).delete()

    # Filter and delete audio answers related to the question
    TeacherAudioAnswer.objects.filter(question_id=id).delete()

    # Filter and delete photo answers related to the question
    TeacherPhotoAnswer.objects.filter(question_id=id).delete()
    messages.success(request,"Answer has been deleted successfully.")
    return redirect("teacher-view-student-question-answer")


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')  
def TEACHER_EDIT_STUDENT_QUESTION_ANSWER_POST(request):
    # Filter questions with any type of answer from the teacher
    if request.method == "POST":

        user = request.user
        teacher = Teacher.objects.get(admin=user)
        

        answer_text = request.POST.get('text_question')
        question_id = request.POST.get("question_id")

        
        audio_files = request.FILES.getlist('audio')
        uploaded_files = request.FILES.getlist('files')  # Gets the list of uploaded files
        print(uploaded_files)
        print(audio_files)
        question = StudentQuestion.objects.get(id = question_id)

        TeacherTextAnswer.objects.filter(question_id=question_id).delete()

        # Filter and delete audio answers related to the question
        TeacherAudioAnswer.objects.filter(question_id=question_id).delete()

        # Filter and delete photo answers related to the question
        TeacherPhotoAnswer.objects.filter(question_id=question_id).delete()
        

        TeacherTextAnswer.objects.create(
            teacher= teacher,
            question = question,
            answer_text=answer_text
        )

        for photo in uploaded_files:
            TeacherPhotoAnswer.objects.create(
                question=question, 
                photo=photo
        )
        
         # Save audio files
        for audio_file in audio_files:
            TeacherAudioAnswer.objects.create(
                question=question, 
                audio_file=audio_file
        )
        messages.success(request,"Answer has been edited successfully.")
        return redirect("teacher-view-student-question-answer")



@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def CREATE_AI_GENERATED_QUESTION(request,id):
    current_time = timezone.now()
    class_id = Class.objects.get(id = id)
    exam = Live_Exam.objects.filter(class_id=class_id,end_time__gt=current_time)
    context = {
        "exam":exam,
        "class":class_id
    }
    return render(request,"teacher/create_ai_generated_question.html",context)


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def CREATE_AI_GENERATED_QUESTION_POST(request):
    if request.method == "POST":
        exam_id = request.POST.get('exam_id')
        number_of_question = request.POST.get('number_of_question')
        each_question_mark = request.POST.get('each_question_mark')
        content = request.POST.get('content')
        
        exam = Live_Exam.objects.get(id = exam_id)
        TONE = "simple"

        with get_openai_callback() as cb:
            response = generate_evaluate_chain(
                {
                    "text": content,
                    "number": number_of_question,
                    "subject": exam.subject.name,
                    "tone": TONE,
                    "response_json": json.dumps(RESPONSE_JSON)
                }
            )

        quiz=response.get("quiz")
        quiz = json.loads(quiz)

        for key, value in quiz.items():
            mcq = value["mcq"]
            options = value["options"]
            correct_answer = value["correct"]
            if correct_answer == "a":
                correct_answer = "Option1"
            elif correct_answer == "b":
                correct_answer = "Option2"
            elif correct_answer == "c":
                correct_answer = "Option3"
            elif correct_answer == "d":
                correct_answer = "Option4"

            print(quiz)
            solution = value["solution"]
            LiveExamMCQQuestion.objects.create(
                exam=exam,
                marks=each_question_mark,
                question=mcq,
                option1=options.get("a", ""),
                option2=options.get("b", ""),
                option3=options.get("c", ""),
                option4=options.get("d", ""),
                answer=correct_answer,
                solution_details=solution
            )
        messages.success(request,"Ai Generated MCQ Question has benn created successfully.")
        return redirect("teacher-view-live-exam-mcq-question")
 

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def ADD_PHOTO(request):

    
    return render(request,"teacher/add_photo.html")


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 2, login_url='login')
def ADD_PHOTO_POST(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        image = request.POST.get("image")

        ImageGallery.objects.create(
           title = title,
           description = description,
           image = image
        )
        
        messages.success(request, 'Image has been added successfully.')
        return redirect("teacher-add-gallary-photo-post")