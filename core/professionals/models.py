from django.db import models
from django.contrib.auth.models import User
import uuid

class Professional(models.Model):
    # Using UUIDs instead of standard 1,2,3 integers is much safer for mobile APIs
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255) # e.g., Therapist, Social Worker
    bio = models.TextField()

    # Link to the User account for authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional')
    
    # Defaults align exactly with our Flutter app logic
    is_vetted = models.BooleanField(default=False)
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    
    # Always good practice to track when a record was created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # This makes it readable when we look at the database later
        return f"{self.name} - {self.title}"
    

# Appointment model

class Appointment(models.Model):
    # Link the appointment to a specific professional
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='appointments')
    
    # Client details (We'll keep it simple for now so they don't have to create an account yet)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    
    # The actual calendar data
    date = models.DateField()
    time = models.TimeField()
    
    # Is it Pending, Confirmed, or Declined?
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} with {self.professional.name} on {self.date}"
    