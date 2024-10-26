# your_app/context_processors.py
from .models import Add_Notification

def notice_processor(request):
    # Fetch all notices
    notifications = Add_Notification.objects.all()
    return {'notification': notifications}
