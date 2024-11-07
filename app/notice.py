# your_app/context_processors.py
from .models import Add_Notification

def notice_processor(request):
    # Fetch all notices
    notifications = Add_Notification.objects.all()
    return {'notification': notifications}


# your_app/context_processors.py
from .models import Points,Student

def notice_processor(request):
    # Fetch all notices
    student = Student.objects.get(id = request.user.id)
    points = Points.objects.filter(student_id = student)
    return {'points': points}


