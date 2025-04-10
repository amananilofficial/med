from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid  # Import uuid to generate unique order IDs

# Create your models here.

class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="medapp_user_set",
        related_query_name="medapp_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="medapp_user_set",
        related_query_name="medapp_user",
    )
    def __str__(self):
        return self.username

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True)
    message = models.TextField()
    whatsapp = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class NewsletterSubscriber(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    whatsapp = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class NavbarCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='media/navbar_categories/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    navbar_category = models.ForeignKey(NavbarCategory, related_name='categories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='navbar_categories/categories/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class SubCategory(models.Model):
    navbar_category = models.ForeignKey(NavbarCategory, related_name='subcategories', on_delete=models.CASCADE, default=1)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='navbar_categories/categories/subcategories/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    navbar_categories = models.ManyToManyField(NavbarCategory, related_name='products', blank=True)
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    sub_categories = models.ManyToManyField(SubCategory, related_name='products', blank=True)

    MEDICINE_TYPE_CHOICES = [
        ('tablet', 'Tablet'),
        ('syrup', 'Syrup'),
        ('capsule', 'Capsule'),
        ('injection', 'Injection'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in Indian Rupees (INR)")
    stock = models.PositiveIntegerField()

    main_image = models.ImageField(upload_to='navbar_categories/categories/subcategories/prdoucts/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='navbar_categories/categories/subcategories/prdoucts/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='navbar_categories/categories/subcategories/prdoucts/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='navbar_categories/categories/subcategories/prdoucts/', null=True, blank=True)
    image_5 = models.ImageField(upload_to='navbar_categories/categories/subcategories/prdoucts/', null=True, blank=True)

    requires_prescription = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Extended fields
    medicine_type = models.CharField(max_length=20, choices=MEDICINE_TYPE_CHOICES, default='tablet')
    brand = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile', null=True, blank=True)
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True, help_text="Patient's email address")
    street_address = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=100, default='')
    postal_code = models.CharField(max_length=20, default='')
    country = models.CharField(max_length=100, default='India')
    blood_group = models.CharField(
        max_length=3,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-')
        ],
        null=True,
        blank=True
    )
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)
    medical_history = models.TextField(blank=True, help_text="Past conditions, allergies, surgeries, etc.")
    profile_image = models.ImageField(upload_to='patients/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    last_visit = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_full_address(self):
        address_parts = [
            self.street_address,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, address_parts)) or 'Not provided'

    def __str__(self):
        return self.full_name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    specialization = models.CharField(max_length=255)
    qualifications = models.CharField(max_length=255, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    street_address = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=100, default='')
    postal_code = models.CharField(max_length=20, default='')
    country = models.CharField(max_length=100, default='India')
    available_days = models.CharField(max_length=100, help_text="e.g. Mon-Wed-Fri")
    available_time = models.CharField(max_length=100, help_text="e.g. 10:00 AM - 1:00 PM")
    profile_image = models.ImageField(upload_to='doctors/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    clinic_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.full_name} ({self.specialization})"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    symptoms = models.TextField(blank=True, help_text="Describe symptoms or reason for visit")
    consultation_type = models.CharField(
        max_length=20,
        choices=[('in_person', 'In Person'), ('online', 'Online')],
        default='in_person'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.full_name} with Dr. {self.doctor.full_name} on {self.appointment_date}"

class Cart(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.patient.full_name}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"

    def total_price(self):
        return self.quantity * self.product.price

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    upi_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expected_delivery_time = models.DateTimeField(null=True, blank=True)
    order_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Make it nullable

    def __str__(self):
        return f"Order {self.order_id} - {self.patient.full_name}"

    def cancel_order(self):
        self.status = 'cancelled'
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Order {self.order.id}"

    def total_price(self):
        return self.quantity * self.price

class VideoChatRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('waiting_for_response', 'Waiting for Response'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='video_chat_requests')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='video_chat_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    chat_started_at = models.DateTimeField(null=True, blank=True)
    chat_ended_at = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    video_file_path = models.CharField(max_length=255, null=True, blank=True)
    chat_log = models.TextField(null=True, blank=True)  # To store chat messages
    room_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Video Chat Request from {self.patient.full_name} to {self.doctor.full_name} - Status: {self.status}"

    def update_status(self, new_status):
        self.status = new_status
        self.save()