from django.db import models
from django.utils import timezone

class QueueNumber(models.Model):
    number = models.IntegerField()
    is_called = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    called_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('number', 'created_at')  # Ensures unique numbers per day

    @staticmethod
    def reset_daily_queue():
        """Deletes queue numbers from previous days to reset the queue daily."""
        today = timezone.now().date()
        QueueNumber.objects.filter(created_at__lt=today).delete()  # ✅ Fixed!

    def __str__(self):
        return f"Queue {self.number} ({'Called' if self.is_called else 'Waiting'})"