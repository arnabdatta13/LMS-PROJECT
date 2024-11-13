# your_app/context_processors.py
from .models import Add_Notification,CustomUser
from django.contrib.auth.decorators import login_required

def notice_processor(request):
    # Fetch all notices
    notifications = Add_Notification.objects.all()
    return {'notification': notifications}


# your_app/context_processors.py
from .models import Points,Student

def notice_processor(request):
    if request.user.is_authenticated and request.user.user_type == 3:
        user = CustomUser.objects.get(id=request.user.id)
        student = Student.objects.get(admin=user)
        points = Points.objects.filter(student_id=student)
        return {'points': points}
    else:
        return {'points': None}


