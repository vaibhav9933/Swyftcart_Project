from django.shortcuts import render, get_object_or_404
from .models import Product, ReviewRating,ProductGallery, Variation
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from django.shortcuts import redirect
from orders.models import OrderProduct
from datetime import datetime
from django.shortcuts import render


# Create your views here.

def store(request, category_slug = None ):
    categories = None
    products = None

    if category_slug is not None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)
def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    orderproduct = None
    if request.user.is_authenticated:
        orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery':product_gallery,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword)| Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count':product_count,
    }
    return render(request,'store/store.html',context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "⚠️ Please login to submit a review.")
            return redirect(url)

        subject = request.POST.get('subject')
        review_text = request.POST.get('review')
        rating = request.POST.get('rating')

        if not rating:
            messages.error(request, "⚠️ Please select a rating.")
            return redirect(url)

        try:
            review = ReviewRating.objects.get(user=request.user, product_id=product_id)
            review.subject = subject
            review.review = review_text
            review.rating = rating
            review.save()
            messages.success(request, "✅ Your review has been updated.")
        except ReviewRating.DoesNotExist:
            review = ReviewRating.objects.create(
                product_id=product_id,
                user=request.user,
                subject=subject,
                review=review_text,
                rating=rating,
                ip=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, "✅ Thank you! Your review has been submitted.")

        return redirect(url)

    messages.error(request, "⚠️ Invalid request method.")
    return redirect(url)


def store(request, category_slug=None):
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # --- size filter ---
    selected_size = request.GET.get('size')
    if selected_size:
        products = products.filter(
            variation__variation_category='size',
            variation__variation_value=selected_size
        ).distinct()

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    sizes = Variation.objects.filter(
        variation_category='size', is_active=True
    ).values_list('variation_value', flat=True).distinct()

    context = {
        'products': paged_products,
        'product_count': product_count,
        'sizes': sizes,
        'selected_size': selected_size,
    }
    return render(request, 'store/store.html', context)


