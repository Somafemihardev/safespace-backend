from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( ProfessionalViewSet, 
      book_appointment, 
      get_my_profile, 
      get_vetted_professionals, 
      register_professional,
        get_my_schedule,
          update_appointment_status ) # <-- Import your new views
 

router = DefaultRouter()
router.register(r'professionals', ProfessionalViewSet)

urlpatterns = [
    # The new route for getting the logged-in user's specific data
    path('profile/', get_my_profile), 
    
    path('register/', register_professional),
    # The standard routes

    path('directory/', get_vetted_professionals), # <-- Add this line for the vetted professionals endpoint

    path('book/', book_appointment), #  
    path('schedule/', get_my_schedule),
    path('appointments/<int:pk>/status/', update_appointment_status), # <-- Add this line for updating appointment status
]