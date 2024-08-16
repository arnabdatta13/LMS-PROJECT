# your_app/context_processors.py
from .models import Add_Notice

def notice_processor(request):
    # Fetch all notices
    notices = Add_Notice.objects.all()
    return {'notice': notices}
