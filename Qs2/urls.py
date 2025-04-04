from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    customer_view,
    staff_view,
    display_screen,
    generate_queue_number,
    call_queue_number,
    cancel_queue_number,
    sse_queue_updates,
    sse_last_called,
    check_queue_status,
    recall_queue
)

urlpatterns = [
    path("", customer_view, name="customer_view"),
    path("staff/", staff_view, name="staff_view"),
    path("display/", display_screen, name="display_screen"),
    path("generate/", generate_queue_number, name="generate_queue_number"),
    path("queue/check-status/", check_queue_status, name="check_queue_status"),
    path("queue/recall-queue/<int:queue_id>/", recall_queue, name="recall-queue"),
    path("queue/call-queue/<int:queue_id>/", call_queue_number, name="call_queue_number"),
    path("queue/cancel-queue/<int:queue_id>/", cancel_queue_number, name="cancel_queue_number"),
    path("sse/queue-updates/", sse_queue_updates, name="sse_queue_updates"),  # SSE route
    path("sse/last-called/", sse_last_called, name="sse_last_called"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
