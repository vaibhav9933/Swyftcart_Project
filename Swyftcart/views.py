from django.shortcuts import render
from store.models import Product, ReviewRating

def home (request):
    products =  Product.objects.all().filter(is_available=True).order_by('created_date')[:12]

    for product in products:

        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews':reviews,
    }
    return render(request, 'home.html',context)

    
def about_us(request):
    return render(request, 'about_us.html')

def contact_us(request):
    return render(request, 'contact_us.html')