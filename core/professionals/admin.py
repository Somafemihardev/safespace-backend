from django.contrib import admin
from .models import Appointment, Professional

# Register your models here.
admin.site.register(Professional)
admin.site.register(Appointment)