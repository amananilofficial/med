from django.urls import path
from . import views
from .views import (
    doctor_appointments,
    update_appointment,
    patient_appointments,
    view_cart
)

urlpatterns = [
    path('', views.home, name='home'),
    path('consultation/', views.consultation, name='consultation'),
    path('contact/', views.contact, name='contact'),
    path('doctor/create/', views.create_doctor_profile, name='create_doctor_profile'),
    path('patient/create/', views.create_patient_profile, name='create_patient_profile'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('check-contact-exists/', views.check_contact_exists, name='check_contact_exists'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),
    path('patient-login/', views.patient_login, name='patient_login'),
    path('patient-register/', views.register_patient, name='register_patient'),
    path('patient/appointment/create/', views.create_appointment, name='create_appointment'),
    path('doctor-login/', views.doctor_login, name='doctor_login'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('logout/', views.user_logout, name='logout'),
    path('doctor/appointments/', doctor_appointments, name='doctor_appointments'),
    path('doctor/appointments/update/<int:appointment_id>/', update_appointment, name='update_appointment'),
    path('patient/appointments/', patient_appointments, name='patient_appointments'),
    path('cart/', view_cart, name='view_cart'),
    path('add-to-cart/<slug:product_slug>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('order/<int:order_id>/', views.order_details, name='order_details'),
    path('continue-order/', views.continue_order, name='continue_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('<slug:navbar_slug>/', views.navbar_category_detail, name='navbar_category_detail'),
    path('<slug:navbar_slug>/<slug:category_slug>/', views.category_detail, name='navbar_category_detail'),
    path('<slug:navbar_slug>/<slug:category_slug>/<slug:subcategory_slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('<slug:navbar_slug>/<slug:category_slug>/<slug:subcategory_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]
