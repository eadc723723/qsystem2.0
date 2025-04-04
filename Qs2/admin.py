from django.contrib import admin
from .models import QueueNumber

class QueueNumberAdmin(admin.ModelAdmin):
    list_display = ('number', 'is_called', 'is_canceled', 'called_at', 'created_at')  # Columns in the admin list
    list_filter = ('is_called', 'is_canceled', 'created_at')  # Filters on the right panel
    search_fields = ('number',)  # Allows searching by queue number
    ordering = ('-created_at', 'number')  # Orders by latest created_at first

admin.site.register(QueueNumber, QueueNumberAdmin)  # Register the model with custom settings

