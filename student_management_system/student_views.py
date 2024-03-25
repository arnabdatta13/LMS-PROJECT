from django.shortcuts import render,redirect
from app.models import Student,Student_Notification,Student_Feedback,Attendance,Attendance_Report,StudentResult,Add_Notice,Practice_Exam,Question,Online_Exam_Result,Course

def HOME(request):
    notice = Add_Notice.objects.all()

    context={
        'notice':notice,
    }
    return render(request,'student/home.html',context)


def NOTIFICATION(request):
    student = Student.objects.filter(admin=request.user.id)
    for i in student:
        student_id =i.id

        notification = Student_Notification.objects.filter(student_id=student_id)

        context = {
            'notification':notification,
        }
        return render(request,'student/notification.html',context)
    

def STUDENT_NOTIFICATION_MARK_AS_DONE(request,status):
        notification = Student_Notification.objects.get(id= status)
        notification.status=1
        notification.save()


        return redirect('student-notification')


def STUDENT_FEEDBACK(request):
    student_id = Student.objects.get(admin = request.user.id)

    feedback_history = Student_Feedback.objects.filter(student_id= student_id)

    context= {
        'feedback_history': feedback_history,
    }
    return render(request,'student/feedback.html',context)


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
    

def STUDENT_VIEW_ATTENDANCE(request):
    student = request.user.student  # Assuming request.user is the logged-in user

    # Retrieve the attendance reports for the student
    attendance_reports = Attendance_Report.objects.filter(student_id=student)

    context = {
        'attendance_reports': attendance_reports
    }

    return render(request,'student/view_attendance.html',context)




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


def STUDENT_ASK_QUESTION(request):
    return render(request,'student/q&a.html')




def STUDENT_EXAM(request):
    user = request.user
    student = Student.objects.get(admin=user)
    student_class = student.class_id
    courses = Course.objects.filter(class1=student_class)
    exams = Practice_Exam.objects.filter(class_id=student_class)

    context = {
        'exam':exams,
        'course':courses,
    }
    return render(request,'student/exam.html',context)



def STUDENT_TAKE_EXAM(request,id):
    exam = Practice_Exam.objects.get(id = id)
    total_question = Question.objects.all().filter(exam = exam).count()
    questions=Question.objects.all().filter(exam=exam)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks



    context = {
        'exam':exam,
        'total_question':total_question,
        'total_marks':total_marks,
    }
    return render(request,'student/take_exam.html',context)



def STUDENT_START_EXAM(request,id):
    exam=Practice_Exam.objects.get(id=id)
    questions=Question.objects.all().filter(exam=exam)

    context = {
        'questions':questions,
        'exam':exam,
    }

    return render(request,'student/start_exam.html',context)


def STUDENT_CALCULATE_MARKS(request):
    if request.method == "POST":
        exam_id = request.POST.get('exam_id') 
        exam = Practice_Exam.objects.get(id=exam_id)
        questions = Question.objects.filter(exam=exam)
        student = request.user.student

        total_obtained_marks = 0
        correct_answers = 0

        for i in range(len(questions)):
            selected_answer = request.POST.get(str(i+1))  # Assuming the radio button names are the question IDs
            correct_answer = questions[i].answer
            if selected_answer == correct_answer:
                total_obtained_marks += questions[i].marks
                correct_answers += 1

        exam_result = Online_Exam_Result.objects.create(student=student, exam=exam, marks=total_obtained_marks)

        print(total_obtained_marks)
        return redirect('student-mark')
        





def STUDENT_MARK(request):
    user = request.user
    student = Student.objects.get(admin=user)
    student_class = student.class_id
    courses = Course.objects.filter(class1=student_class)
    exams = Practice_Exam.objects.filter(class_id=student_class)

    context = {
        'exam':exams,
        'course':courses,
    }
    return render(request,'student/mark.html',context)



def STUDENT_VIEW_MARK(request,id):
    exam=Practice_Exam.objects.get(id=id)
    student =Student.objects.get(admin=request.user.id)
    results=Online_Exam_Result.objects.all().filter(exam=exam).filter(student=student)

    context = {
        'result':results,
    }
    return render(request,'student/view_mark.html',context)