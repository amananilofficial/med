from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from .models import (
    ContactMessage,
    NewsletterSubscriber,
    NavbarCategory,
    Category,
    SubCategory,
    Product,
    Patient,
    Doctor,
    Appointment,  # Import the Appointment model
    Cart,
    CartItem,
    Order,
    OrderItem
)
from .forms import PatientForm, DoctorForm, AppointmentForm, CustomUserCreationForm  # Ensure this import is correct
from django.contrib.auth.decorators import login_required
from django.conf import settings
import logging
from django.core.exceptions import ImproperlyConfigured
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
import os

logger = logging.getLogger(__name__)

def home(request):
    navbar_categories = NavbarCategory.objects.all()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    products = Product.objects.all()  # Adjust this as needed to filter products

    context = {
        'navbar_categories': navbar_categories,
        'categories': categories,
        'subcategories': subcategories,
        'products': products,
    }
    return render(request, 'medapp/home.html', context)


def consultation(request):
    return render(request, 'medapp/consultation.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        message = request.POST.get('message')
        whatsapp = request.POST.get('whatsapp') == 'on'

        ContactMessage.objects.create(
            name=name,
            email=email,
            phone_number=phone_number,
            message=message,
            whatsapp=whatsapp
        )
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')

    return render(request, 'medapp/contact.html')


def newsletter_subscribe(request):
    if request.method == 'POST':
        name = request.POST.get('newsletter_name')
        email = request.POST.get('newsletter_email')
        phone_number = request.POST.get('newsletter_phone')
        whatsapp = request.POST.get('newsletter_whatsapp') == 'on'

        if NewsletterSubscriber.objects.filter(email=email).exists():
            messages.warning(request, 'You are already subscribed!')
        else:
            NewsletterSubscriber.objects.create(
                name=name,
                email=email,
                phone_number=phone_number,
                whatsapp=whatsapp
            )
            messages.success(request, 'Thank you for subscribing to our newsletter!')

        return redirect('home')

    return JsonResponse({'error': 'Invalid request'}, status=400)


def check_contact_exists(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        exists = ContactMessage.objects.filter(email=email).exists() or \
                 ContactMessage.objects.filter(phone_number=phone_number).exists()

        return JsonResponse({'exists': exists})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def navbar_category_detail(request, navbar_slug):
    navbar_category = get_object_or_404(NavbarCategory, slug=navbar_slug)
    categories = navbar_category.categories.all()
    subcategories = SubCategory.objects.filter(category__navbar_category=navbar_category)

    context = {
        'navbar_category': navbar_category,
        'categories': categories,
        'subcategories': subcategories,
    }
    return render(request, 'medapp/navbar_category_detail.html', context)


def category_detail(request, navbar_slug, category_slug):
    category = get_object_or_404(Category, slug=category_slug, navbar_category__slug=navbar_slug)
    subcategories = category.subcategories.all()
    products = category.products.all()
    
    context = {
        'navbar_category': category.navbar_category,
        'category': category,
        'subcategories': subcategories,
        'products': products,
    }
    return render(request, 'medapp/category_detail.html', context)


def subcategory_detail(request, navbar_slug, category_slug, subcategory_slug):
    subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category__slug=category_slug, category__navbar_category__slug=navbar_slug)
    products = subcategory.products.all()
    
    context = {
        'subcategory': subcategory,
        'products': products,
    }
    return render(request, 'medapp/subcategory_detail.html', context)


def product_detail(request, navbar_slug, category_slug, subcategory_slug, product_slug):
    product = get_object_or_404(
        Product,
        slug=product_slug,
        sub_categories__slug=subcategory_slug,
        sub_categories__category__slug=category_slug,
        sub_categories__category__navbar_category__slug=navbar_slug
    )
    context = {
        'product': product,
    }
    return render(request, 'medapp/product_detail.html', context)


@login_required
def add_to_cart(request, product_slug):
    if not request.user.is_patient:
        messages.error(request, 'Only patients can add to cart')
        return redirect('home')
    
    product = get_object_or_404(Product, slug=product_slug)
    patient = get_object_or_404(Patient, user=request.user)
    
    # Check if the product is in any completed orders for this patient
    completed_orders = Order.objects.filter(patient=patient, status='completed')
    if completed_orders.filter(orderitem__product=product).exists():
        messages.error(request, 'This product has already been ordered and cannot be added to cart again.')
        return redirect('product_detail', slug=product_slug)
    
    # Get or create cart for the patient
    cart, created = Cart.objects.get_or_create(patient=patient)
    
    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart')
    return redirect('view_cart')


@login_required
def view_cart(request):
    # Get the patient associated with the logged-in user
    patient = get_object_or_404(Patient, user=request.user)
    
    # Get the cart for this patient
    cart = Cart.objects.get(patient=patient)
    
    # Get cart items
    items = cart.items.all()
    
    # Calculate total
    total = sum(item.total_price() for item in items)
    
    context = {
        'items': items,
        'total': total
    }
    
    return render(request, 'medapp/cart.html', context)


def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"[DEBUG] Authenticated user: {user.username}, is_doctor: {user.is_doctor}")
            if user.is_doctor:
                login(request, user)
                print("[DEBUG] Redirecting to doctor_profile...")
                return redirect('doctor_profile')
            else:
                messages.error(request, 'This account is not a doctor account.')
        else:
            messages.error(request, 'Invalid credentials.')
    
    return render(request, 'medapp/doctor_login.html')

def patient_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_patient:
            login(request, user)
            return redirect('patient_profile')  # Redirect to patient profile if exists
        else:
            messages.error(request, 'Invalid credentials or not a patient account')
    
    return render(request, 'medapp/patient_login.html')


def create_patient_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to create a profile.')
        return redirect('patient_login')

    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user
            patient.save()
            messages.success(request, 'Profile created successfully!')
            return redirect('patient_profile')
    else:
        form = PatientForm()

    return render(request, 'medapp/create_patient_profile.html', {'form': form})


def create_doctor_profile(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        messages.error(request, 'Only admin users can create doctor profiles.')
        return redirect('home')

    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.user = request.user  # Associate the doctor profile with the logged-in user
            doctor.save()
            
            # Update the user's is_doctor flag
            user = request.user
            user.is_doctor = True
            user.save()
            
            messages.success(request, 'Doctor profile created successfully!')
            return redirect('doctor_profile')
    else:
        form = DoctorForm()
    return render(request, 'medapp/create_doctor_profile.html', {'form': form})


def create_appointment(request):
    if not request.user.is_authenticated or not request.user.is_patient:
        messages.error(request, 'You need to be logged in as a patient to create an appointment.')
        return redirect('patient_login')

    doctors = Doctor.objects.filter(is_active=True)  # Get active doctors
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user.patient_profile  # Set the logged-in patient
            appointment.save()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('home')  # Redirect to a success page
    else:
        form = AppointmentForm()

    return render(request, 'medapp/create_appointment.html', {'form': form, 'doctors': doctors})


def register_patient(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a Patient profile for the new user
            patient = Patient.objects.create(
                user=user,
                email=user.email,  # Get email directly from the User instance
                full_name=form.cleaned_data['full_name'],  # Get full name from the form
                # You can add other fields if needed
            )
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('patient_login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'medapp/patient_register.html', {'form': form})


def patient_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to view your profile.')
        return redirect('patient_login')  # Redirect to the login page if not authenticated

    try:
        patient = Patient.objects.get(user=request.user)  # Get the logged-in patient's profile
    except Patient.DoesNotExist:
        # If no Patient profile exists, redirect to a profile creation page
        messages.error(request, 'No patient profile found. Please create one.')
        return redirect('create_patient_profile')  # Redirect to a profile creation page

    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)  # Bind the form to the patient instance
        if form.is_valid():
            form.save()  # Save the updated profile
            messages.success(request, 'Profile updated successfully!')
            return redirect('patient_profile')  # Redirect to the same profile page
    else:
        form = PatientForm(instance=patient)  # Pre-fill the form with the patient's current data

    patient_email = patient.email or patient.user.email

    return render(request, 'medapp/patient_profile.html', {'form': form, 'patient': patient, 'patient_email': patient_email})


def doctor_profile(request):
    if not request.user.is_authenticated or not request.user.is_doctor:
        messages.error(request, 'You need to be logged in as a doctor to access this page.')
        return redirect('doctor_login')

    try:
        doctor_profile = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('create_doctor_profile')

    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('doctor_profile')
    else:
        form = DoctorForm(instance=doctor_profile)

    return render(request, 'medapp/doctor_profile.html', {'doctor': doctor_profile, 'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to home or login page after logout


def doctor_appointments(request):
    if not request.user.is_authenticated or not request.user.is_doctor:
        messages.error(request, 'You need to be logged in as a doctor to access this page.')
        return redirect('doctor_login')

    appointments = Appointment.objects.filter(doctor__user=request.user)

    return render(request, 'medapp/doctor_appointments.html', {'appointments': appointments})


def update_appointment(request, appointment_id):
    if not request.user.is_authenticated or not request.user.is_doctor:
        messages.error(request, 'You need to be logged in as a doctor to access this page.')
        return redirect('doctor_login')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        reason = request.POST.get('reason')

        if status in ['confirmed', 'cancelled']:
            appointment.status = status
            appointment.save()
            if status == 'cancelled':
                messages.info(request, 'The appointment has been cancelled.')
            else:
                messages.success(request, 'Appointment status updated successfully!')
            return redirect('doctor_appointments')
        else:
            messages.error(request, 'Invalid status selected.')

    return render(request, 'medapp/update_appointment.html', {'appointment': appointment})


def patient_appointments(request):
    if not request.user.is_authenticated or not request.user.is_patient:
        messages.error(request, 'You need to be logged in as a patient to view your appointments.')
        return redirect('patient_login')

    appointments = Appointment.objects.filter(patient__user=request.user)

    return render(request, 'medapp/patient_appointments.html', {'appointments': appointments})


@login_required
def update_cart_item(request, item_id):
    if not request.user.is_patient:
        messages.error(request, 'Only patients can update cart items')
        return redirect('home')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__patient__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0 and quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart item updated successfully')
        else:
            messages.error(request, 'Invalid quantity')
    
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    if not request.user.is_patient:
        messages.error(request, 'Only patients can remove cart items')
        return redirect('home')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__patient__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    
    return redirect('view_cart')

@login_required
def process_payment(request):
    if request.method == 'POST':
        try:
            # Get the patient's cart
            patient = get_object_or_404(Patient, user=request.user)
            cart = Cart.objects.get(patient=patient)
            
            # Calculate total price
            total_price = cart.total_price()
            
            # Get payment method and UPI ID
            payment_method = request.POST.get('payment_method')
            upi_id = request.POST.get('upi_id', None)
            
            # Create a new order in your system
            order = Order.objects.create(
                patient=patient,
                total_amount=total_price,
                upi_id=upi_id if payment_method == 'upi' else None,
                status='completed' if payment_method == 'upi' else 'pending',
                expected_delivery_time=timezone.now() + timedelta(days=3)  # Example: 3 days from now
            )
            
            # Create OrderItems for each cart item
            cart_items = list(cart.items.all())  # Create a list to avoid QuerySet modification
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Completely clear the cart
            cart.items.all().delete()
            
            # Update product stock
            for cart_item in cart_items:
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
            
            # Store the order ID in the session
            request.session['order_id'] = order.id
            
            messages.success(request, 'Payment processed successfully!')
            return redirect('payment_success')
            
        except Exception as e:
            logger.error(f"Payment process error: {str(e)}")
            messages.error(request, f"Payment processing failed: {str(e)}")
            return redirect('checkout')

@login_required
def checkout(request):
    patient = get_object_or_404(Patient, user=request.user)
    cart = Cart.objects.get(patient=patient)
    items = cart.items.all()
    total_price = sum(item.total_price() for item in items)

    context = {
        'patient': patient,
        'cart': cart,
        'items': items,
        'total': total_price,
    }
    return render(request, 'medapp/checkout.html', context)

@login_required
def payment_success(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    context = {
        'order': order,
    }
    return render(request, 'medapp/payment_success.html', context)

def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order_id': order.id,
        'payment_status': order.status,  # Assuming 'status' is the field for payment status
        'order': order,
    }
    return render(request, 'medapp/order_details.html', context)

def continue_order(request):
    # Logic to continue the order goes here
    # For now, we'll just redirect to the order details page or another page
    return redirect('order_details', order_id=1)  # Replace 1 with the actual order ID logic

@login_required
def my_orders(request):
    # Get the Patient instance associated with the logged-in user
    patient = get_object_or_404(Patient, user=request.user)
    
    # Now filter orders using the Patient instance
    orders = Order.objects.filter(patient=patient)
    
    context = {
        'orders': orders,
    }
    return render(request, 'medapp/my_orders.html', context)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, patient__user=request.user)
    
    if order.status not in ['completed', 'cancelled']:
        order.cancel_order()
        messages.success(request, 'Order has been cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('my_orders')
    products = category.products.all()
    
    context = {
        'navbar_category': category.navbar_category,
        'category': category,
        'subcategories': subcategories,
        'products': products,
    }
    return render(request, 'medapp/category_detail.html', context)


def subcategory_detail(request, navbar_slug, category_slug, subcategory_slug):
    subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category__slug=category_slug, category__navbar_category__slug=navbar_slug)
    products = subcategory.products.all()
    
    context = {
        'subcategory': subcategory,
        'products': products,
    }
    return render(request, 'medapp/subcategory_detail.html', context)


def product_detail(request, navbar_slug, category_slug, subcategory_slug, product_slug):
    product = get_object_or_404(
        Product,
        slug=product_slug,
        sub_categories__slug=subcategory_slug,
        sub_categories__category__slug=category_slug,
        sub_categories__category__navbar_category__slug=navbar_slug
    )
    context = {
        'product': product,
    }
    return render(request, 'medapp/product_detail.html', context)


@login_required
def add_to_cart(request, product_slug):
    if not request.user.is_patient:
        messages.error(request, 'Only patients can add to cart')
        return redirect('home')
    
    product = get_object_or_404(Product, slug=product_slug)
    patient = get_object_or_404(Patient, user=request.user)
    
    # Check if the product is in any completed orders for this patient
    completed_orders = Order.objects.filter(patient=patient, status='completed')
    if completed_orders.filter(orderitem__product=product).exists():
        messages.error(request, 'This product has already been ordered and cannot be added to cart again.')
        return redirect('product_detail', slug=product_slug)
    
    # Get or create cart for the patient
    cart, created = Cart.objects.get_or_create(patient=patient)
    
    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart')
    return redirect('view_cart')


@login_required
def view_cart(request):
    # Get the patient associated with the logged-in user
    patient = get_object_or_404(Patient, user=request.user)
    
    # Get the cart for this patient
    cart = Cart.objects.get(patient=patient)
    
    # Get cart items
    items = cart.items.all()
    
    # Calculate total
    total = sum(item.total_price() for item in items)
    
    context = {
        'items': items,
        'total': total
    }
    
    return render(request, 'medapp/cart.html', context)


def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            print(f"[DEBUG] Authenticated user: {user.username}, is_doctor: {user.is_doctor}")
            if user.is_doctor:
                login(request, user)
                print("[DEBUG] Redirecting to doctor_profile...")
                return redirect('doctor_profile')
            else:
                messages.error(request, 'This account is not a doctor account.')
        else:
            messages.error(request, 'Invalid credentials.')
    
    return render(request, 'medapp/doctor_login.html')

def patient_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_patient:
            login(request, user)
            return redirect('patient_profile')  # Redirect to patient profile if exists
        else:
            messages.error(request, 'Invalid credentials or not a patient account')
    
    return render(request, 'medapp/patient_login.html')


def create_patient_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to create a profile.')
        return redirect('patient_login')

    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user
            patient.save()
            messages.success(request, 'Profile created successfully!')
            return redirect('patient_profile')
    else:
        form = PatientForm()

    return render(request, 'medapp/create_patient_profile.html', {'form': form})


def create_doctor_profile(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        messages.error(request, 'Only admin users can create doctor profiles.')
        return redirect('home')

    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.user = request.user  # Associate the doctor profile with the logged-in user
            doctor.save()
            
            # Update the user's is_doctor flag
            user = request.user
            user.is_doctor = True
            user.save()
            
            messages.success(request, 'Doctor profile created successfully!')
            return redirect('doctor_profile')
    else:
        form = DoctorForm()
    return render(request, 'medapp/create_doctor_profile.html', {'form': form})


def create_appointment(request):
    if not request.user.is_authenticated or not request.user.is_patient:
        messages.error(request, 'You need to be logged in as a patient to create an appointment.')
        return redirect('patient_login')

    doctors = Doctor.objects.filter(is_active=True)  # Get active doctors
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user.patient_profile  # Set the logged-in patient
            appointment.save()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('home')  # Redirect to a success page
    else:
        form = AppointmentForm()

    return render(request, 'medapp/create_appointment.html', {'form': form, 'doctors': doctors})


def register_patient(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a Patient profile for the new user
            patient = Patient.objects.create(
                user=user,
                email=user.email,  # Get email directly from the User instance
                full_name=form.cleaned_data['full_name'],  # Get full name from the form
                # You can add other fields if needed
            )
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('patient_login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'medapp/patient_register.html', {'form': form})


def patient_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to view your profile.')
        return redirect('patient_login')  # Redirect to the login page if not authenticated

    try:
        patient = Patient.objects.get(user=request.user)  # Get the logged-in patient's profile
    except Patient.DoesNotExist:
        # If no Patient profile exists, redirect to a profile creation page
        messages.error(request, 'No patient profile found. Please create one.')
        return redirect('create_patient_profile')  # Redirect to a profile creation page

    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)  # Bind the form to the patient instance
        if form.is_valid():
            form.save()  # Save the updated profile
            messages.success(request, 'Profile updated successfully!')
            return redirect('patient_profile')  # Redirect to the same profile page
    else:
        form = PatientForm(instance=patient)  # Pre-fill the form with the patient's current data

    patient_email = patient.email or patient.user.email

    return render(request, 'medapp/patient_profile.html', {'form': form, 'patient': patient, 'patient_email': patient_email})


def doctor_profile(request):
    if not request.user.is_authenticated or not request.user.is_doctor:
        messages.error(request, 'You need to be logged in as a doctor to access this page.')
        return redirect('doctor_login')

    try:
        doctor_profile = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('create_doctor_profile')

    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('doctor_profile')
    else:
        form = DoctorForm(instance=doctor_profile)

    return render(request, 'medapp/doctor_profile.html', {'doctor': doctor_profile, 'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')  # Redirect to home or login page after logout


def doctor_appointments(request):
    if not request.user.is_authenticated or not request.user.is_doctor:
        messages.error(request, 'You need to be logged in as a doctor to access this page.')
        return redirect('doctor_login')

    appointments = Appointment.objects.filter(doctor__user=request.user)

    return render(request, 'medapp/doctor_appointments.html', {'appointments': appointments})


def update_appointment(request, appointment_id):
    if not request.user.is_authenticated or not request.user.is_doctor:
        messages.error(request, 'You need to be logged in as a doctor to access this page.')
        return redirect('doctor_login')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        reason = request.POST.get('reason')

        if status in ['confirmed', 'cancelled']:
            appointment.status = status
            appointment.save()
            if status == 'cancelled':
                messages.info(request, 'The appointment has been cancelled.')
            else:
                messages.success(request, 'Appointment status updated successfully!')
            return redirect('doctor_appointments')
        else:
            messages.error(request, 'Invalid status selected.')

    return render(request, 'medapp/update_appointment.html', {'appointment': appointment})


def patient_appointments(request):
    if not request.user.is_authenticated or not request.user.is_patient:
        messages.error(request, 'You need to be logged in as a patient to view your appointments.')
        return redirect('patient_login')

    appointments = Appointment.objects.filter(patient__user=request.user)

    return render(request, 'medapp/patient_appointments.html', {'appointments': appointments})


@login_required
def update_cart_item(request, item_id):
    if not request.user.is_patient:
        messages.error(request, 'Only patients can update cart items')
        return redirect('home')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__patient__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0 and quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart item updated successfully')
        else:
            messages.error(request, 'Invalid quantity')
    
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    if not request.user.is_patient:
        messages.error(request, 'Only patients can remove cart items')
        return redirect('home')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__patient__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    
    return redirect('view_cart')

@login_required
def process_payment(request):
    if request.method == 'POST':
        try:
            # Get the patient's cart
            patient = get_object_or_404(Patient, user=request.user)
            cart = Cart.objects.get(patient=patient)
            
            # Calculate total price
            total_price = cart.total_price()
            
            # Get payment method and UPI ID
            payment_method = request.POST.get('payment_method')
            upi_id = request.POST.get('upi_id', None)
            
            # Create a new order in your system
            order = Order.objects.create(
                patient=patient,
                total_amount=total_price,
                upi_id=upi_id if payment_method == 'upi' else None,
                status='completed' if payment_method == 'upi' else 'pending',
                expected_delivery_time=timezone.now() + timedelta(days=3)  # Example: 3 days from now
            )
            
            # Create OrderItems for each cart item
            cart_items = list(cart.items.all())  # Create a list to avoid QuerySet modification
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Completely clear the cart
            cart.items.all().delete()
            
            # Update product stock
            for cart_item in cart_items:
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
            
            # Store the order ID in the session
            request.session['order_id'] = order.id
            
            messages.success(request, 'Payment processed successfully!')
            return redirect('payment_success')
            
        except Exception as e:
            logger.error(f"Payment process error: {str(e)}")
            messages.error(request, f"Payment processing failed: {str(e)}")
            return redirect('checkout')

@login_required
def checkout(request):
    patient = get_object_or_404(Patient, user=request.user)
    cart = Cart.objects.get(patient=patient)
    items = cart.items.all()
    total_price = sum(item.total_price() for item in items)

    context = {
        'patient': patient,
        'cart': cart,
        'items': items,
        'total': total_price,
    }
    return render(request, 'medapp/checkout.html', context)

@login_required
def payment_success(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    context = {
        'order': order,
    }
    return render(request, 'medapp/payment_success.html', context)

def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order_id': order.id,
        'payment_status': order.status,  # Assuming 'status' is the field for payment status
        'order': order,
    }
    return render(request, 'medapp/order_details.html', context)

def continue_order(request):
    # Logic to continue the order goes here
    # For now, we'll just redirect to the order details page or another page
    return redirect('order_details', order_id=1)  # Replace 1 with the actual order ID logic

@login_required
def my_orders(request):
    # Get the Patient instance associated with the logged-in user
    patient = get_object_or_404(Patient, user=request.user)
    
    # Now filter orders using the Patient instance
    orders = Order.objects.filter(patient=patient)
    
    context = {
        'orders': orders,
    }
    return render(request, 'medapp/my_orders.html', context)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, patient__user=request.user)
    
    if order.status not in ['completed', 'cancelled']:
        order.cancel_order()
        messages.success(request, 'Order has been cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('my_orders')

