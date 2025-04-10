from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    ContactMessage,
    NewsletterSubscriber,
    NavbarCategory,
    Category,
    SubCategory,
    Product,
    Patient,
    Doctor,
    Appointment,
    Cart,
    CartItem,
    Order,
    VideoChatRequest
)

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'is_doctor', 'is_patient', 'is_admin', 'is_staff', 'is_active')
    list_filter = ('is_doctor', 'is_patient', 'is_admin', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('is_doctor', 'is_patient', 'is_admin')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('is_doctor', 'is_patient', 'is_admin')}),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'date_of_birth', 'phone', 'email', 'blood_group', 'is_verified')
    search_fields = ('full_name', 'email', 'phone')
    list_filter = ('gender', 'is_verified', 'blood_group')

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'date_of_birth', 'specialization', 'experience_years', 'phone', 'email', 'is_active')
    search_fields = ('full_name', 'email', 'phone')
    list_filter = ('specialization', 'is_active', 'gender')

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'whatsapp', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('whatsapp',)

class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'whatsapp', 'subscribed_at')
    search_fields = ('name', 'email')
    list_filter = ('whatsapp',)

class NavbarCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug')
    search_fields = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'navbar_category', 'slug')
    search_fields = ('name',)

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'navbar_category', 'slug')
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_available', 'is_featured')
    search_fields = ('name',)
    list_filter = ('is_available', 'is_featured')

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'consultation_type')
    list_filter = ('status', 'appointment_date', 'doctor')
    search_fields = ('patient__full_name', 'doctor__full_name', 'symptoms')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('added_at', 'total_price')
    fields = ('product', 'quantity', 'total_price', 'added_at')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('patient', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('patient__full_name',)
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_at')
    list_filter = ('cart__patient', 'added_at')
    search_fields = ('product__name', 'cart__patient__full_name')
    readonly_fields = ('added_at', 'total_price')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('patient', 'total_amount', 'status', 'created_at', 'expected_delivery_time')
    list_filter = ('status',)
    search_fields = ('patient__full_name',)

class VideoChatRequestAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'status', 'requested_at', 'scheduled_time', 'completed_at')
    list_filter = ('status', 'doctor', 'patient')
    search_fields = ('patient__full_name', 'doctor__full_name')

admin.site.register(User, UserAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)
admin.site.register(NavbarCategory, NavbarCategoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(VideoChatRequest, VideoChatRequestAdmin)
