from django.contrib import admin
from django.urls import include, path
from  .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name ='home'),
    path('store/', include('store.urls')),
    path('cart/',include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('about_us/', views.about_us, name='about_us'),
    path('contact_us/', views.contact_us, name='contact_us'),

    #ORDERS
    path('orders/',include('orders.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
