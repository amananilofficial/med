from .models import NavbarCategory

def navbar_categories(request):
    return {
        'navbar_categories': NavbarCategory.objects.all()
    } 