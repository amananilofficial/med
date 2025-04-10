from django import forms
from .models import Patient, Doctor, Appointment, User
from django.contrib.auth.forms import UserCreationForm

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'full_name',
            'gender',
            'date_of_birth',
            'phone',
            'email',
            'street_address',
            'city',
            'state',
            'postal_code',
            'country',
            'blood_group',
            'emergency_contact',
            'medical_history',
            'profile_image',
        ]

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'full_name',
            'gender',
            'date_of_birth',
            'specialization',
            'qualifications',
            'experience_years',
            'phone',
            'email',
            'street_address',
            'city',
            'state',
            'postal_code',
            'country',
            'available_days',
            'available_time',
            'profile_image',
            'clinic_address',
        ]

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'patient',
            'doctor',
            'appointment_date',
            'appointment_time',
            'symptoms',
            'consultation_type',
        ]

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password1', 'password2') 