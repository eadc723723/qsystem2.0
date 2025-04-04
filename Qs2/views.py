from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
from django.http import JsonResponse
from django.utils.timezone import now
from django.db.models import Max
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
import datetime
import time
import json
from .models import QueueNumber

def reset_queue_daily():
    """Deletes previous day's queue numbers once per day."""
    today = datetime.date.today()
    
    # Check if reset has already been done today
    last_reset = cache.get("last_reset")
    
    if last_reset != str(today):  # Ensures it runs only once per day
        QueueNumber.objects.filter(created_at__lt=today).delete()  # ✅ Fixed
        cache.set("last_reset", str(today), timeout=86400)  # Cache reset time for 24 hours # Store reset timestamp for 1 day

# **Customer View** - Show generated queue number on mobile
def customer_view(request):
    reset_queue_daily()  # Ensure queue resets once per day
    queue_number = request.session.get('queue_number', None)  # Get only their queue number
    return render(request, 'queueapp/customer.html', {'queue_number': queue_number})

# **Generate Queue Number** - Assigns a queue number to a customer
def generate_queue_number(request):
    reset_queue_daily()

    last_queue = QueueNumber.objects.aggregate(Max('number'))
    next_number = (last_queue['number__max'] or 999) + 1  # Start from 1000 if no records exist

    queue = QueueNumber.objects.create(number=next_number)
    request.session['queue_number'] = next_number  # Store only in this customer's session
    request.session.set_expiry(7200)

    return redirect('customer_view')  # Redirect back to view their assigned number

def check_queue_status(request):
    """Check if the customer has an active queue number using session data."""
    has_queue = 'queue_number' in request.session  # Check if a queue number exists in the session
    return JsonResponse({"has_queue": has_queue})

# **Staff View** - Display queue list for staff to manage
def staff_view(request):
    reset_queue_daily()
    queues = QueueNumber.objects.all().order_by('number')
    return render(request, 'queueapp/staff.html', {'queues': queues})

# **Call Queue Number** - Marks the number as called
def call_queue_number(request, queue_id):
    queue = QueueNumber.objects.get(id=queue_id)
    queue.is_called = True
    queue.called_at = now()
    queue.save()
    return redirect('staff_view')

# **Cancel Queue Number** - Deletes a queue number
def cancel_queue_number(request, queue_id):
    queue = QueueNumber.objects.get(id=queue_id)
    queue.delete()
    return redirect('staff_view')

@csrf_exempt
def recall_queue(request, queue_id):
    """Marks a queue number as recalled and updates its timestamp."""
    if request.method == "POST":
        queue = QueueNumber.objects.get(id=queue_id)
        queue.is_called = True  # Keep it marked as called
        queue.called_at = now()  # Update called_at to refresh display order
        queue.save()
        return JsonResponse({"message": f"Queue number {queue.number} recalled successfully!"})
    
# **Display Called Queue Number** - Shown on another monitor
def display_screen(request):
    return render(request, 'queueapp/display.html')

# **SSE for real-time updates of called numbers**
def sse_queue_updates(request):
    """Server-Sent Events (SSE) stream for queue updates."""
    def event_stream():
        last_sent = None  # Track last sent data to prevent duplicates

        while True:
            queues = QueueNumber.objects.all().order_by("number").values("id", "number", "is_called")
            queue_list = list(queues)

            # Send only if data has changed
            if last_sent != queue_list:
                yield f"data: {json.dumps(queue_list)}\n\n"
                last_sent = queue_list

            time.sleep(2)  # Update every 2 seconds

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    return response

def sse_last_called(request):
    """SSE stream for the last called or recalled queue number."""
    def event_stream():
        last_sent = None  # Track last sent number
        while True:
            last_called = QueueNumber.objects.filter(is_called=True).order_by("-called_at").first()
            last_number = last_called.number if last_called else "Waiting..."

            if last_sent != last_number:
                yield f"data: {json.dumps({'number': last_number})}\n\n"
                last_sent = last_number

            time.sleep(2)  # Update every 2 seconds

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    return response