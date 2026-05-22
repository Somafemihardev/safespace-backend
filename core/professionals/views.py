from rest_framework import viewsets, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User

from .models import Professional, Appointment
from .serializers import ProfessionalSerializer, AppointmentSerializer


class ProfessionalViewSet(viewsets.ModelViewSet):
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer

# --- SECURED ENDPOINT ---
@api_view(['GET', 'PUT']) 
@authentication_classes([TokenAuthentication]) # The ID Scanner!
@permission_classes([IsAuthenticated])         # The Bouncer!
def get_my_profile(request):
    try:
        # We follow the chain from the User account to their linked Professional profile
        profile = request.user.professional 
    except Exception:
        return Response({'error': 'No professional profile found for this user.'}, status=404)

    # 1. If Flutter is asking for the data to display the Dashboard
    if request.method == 'GET':
        serializer = ProfessionalSerializer(profile)
        return Response(serializer.data)

    # 2. If Flutter is sending updated data from an "Edit Profile" screen
    elif request.method == 'PUT':
        # partial=True allows them to update just one field (like bio) without breaking
        serializer = ProfessionalSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save() # Saves the new data to the SQLite database
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- PUBLIC ENDPOINT ---
@api_view(['POST'])
@permission_classes([AllowAny]) # Anyone can create a profile
def register_professional(request):
    data = request.data
    
    try:
        # 1. Check if the username is already taken
        if User.objects.filter(username=data.get('username')).exists():
            return Response({'error': 'Username is already taken.'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Create the secure User account (this automatically hashes the password!)
        user = User.objects.create_user(
            username=data['username'],
            password=data['password']
        )

        # 3. Create the Professional profile and chain it to the new User
        professional = Professional.objects.create(
            user=user,
            name=data['name'],
            title=data['title'],
            bio=data['bio'],
            is_vetted=False # Force this to False so they must be approved!
        )

        return Response({'message': 'Registration successful!'}, status=status.HTTP_201_CREATED)
        
    except KeyError as e:
        return Response({'error': f'Missing required field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Something went wrong during registration.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# --- PUBLIC ENDPOINT ---
@api_view(['GET'])
@permission_classes([AllowAny]) # Anyone downloading the client app can browse
def get_vetted_professionals(request):
    try:
        # Filter the database to ONLY grab professionals where is_vetted is True
        vetted_pros = Professional.objects.filter(is_vetted=True)
        
        # Translate the Python list into JSON (many=True because it's a list!)
        serializer = ProfessionalSerializer(vetted_pros, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': 'Could not fetch the directory.'}, status=500)


# --- PUBLIC ENDPOINT ---
@api_view(['POST'])
@permission_classes([AllowAny]) # Anyone on the client app can request a session
def book_appointment(request):
    data = request.data
    client_email = data.get('client_email')
    
    # --- 🛡️ THE SPAM SHIELD 🛡️ ---
    # Check if this email already has an appointment sitting in 'Pending' status
    has_pending = Appointment.objects.filter(client_email=client_email, status='Pending').exists()
    
    if has_pending:
        return Response(
            {'error': 'You already have a pending request. Please wait for the professional to respond.'}, 
            status=status.HTTP_429_TOO_MANY_REQUESTS # 429 means "Too Many Requests"
        )
    # -----------------------------
    
    try:
        # Find the professional they are trying to book
        professional = Professional.objects.get(id=data['professional_id'])
        
        # Create the calendar appointment!
        Appointment.objects.create(
            professional=professional,
            client_name=data.get('client_name'),
            client_email=client_email,
            date=data.get('date'),
            time=data.get('time')
        )
        
        return Response({'message': 'Session requested successfully!'}, status=status.HTTP_201_CREATED)
        
    except Professional.DoesNotExist:
        return Response({'error': 'Professional not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

# --- SECURED ENDPOINT ---
@api_view(['GET'])
@authentication_classes([TokenAuthentication]) # The ID Scanner
@permission_classes([IsAuthenticated])         # The Bouncer
def get_my_schedule(request):
    try:
        # Find the profile of the person making the request
        profile = request.user.professional 
        
        # Grab all their appointments and put them in chronological order
        appointments = Appointment.objects.filter(professional=profile).order_by('date', 'time')
        
        # Translate to JSON
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': 'Could not fetch schedule.'}, status=status.HTTP_400_BAD_REQUEST)


# --- SECURED ENDPOINT ---
@api_view(['PUT'])
@authentication_classes([TokenAuthentication]) # The ID Scanner
@permission_classes([IsAuthenticated])         # The Bouncer
def update_appointment_status(request, pk):
    try:
        # Find the specific appointment. 
        # We also ensure it belongs to the logged-in professional for security!
        appointment = Appointment.objects.get(id=pk, professional=request.user.professional)
        
        # Grab the new status from Flutter
        new_status = request.data.get('status')
        
        if new_status in ['Confirmed', 'Declined']:
            appointment.status = new_status
            appointment.save()
            return Response({'message': f'Status updated to {new_status}'}, status=status.HTTP_200_OK)
            
        return Response({'error': 'Invalid status provided.'}, status=status.HTTP_400_BAD_REQUEST)

    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)