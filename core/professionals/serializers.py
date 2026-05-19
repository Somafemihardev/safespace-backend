from rest_framework import serializers
from .models import Appointment, Professional

class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        # This tells Django to include all the fields we created in models.py
        fields = '__all__'



class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'