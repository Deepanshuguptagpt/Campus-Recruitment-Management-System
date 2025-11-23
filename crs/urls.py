from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # All routing inside campus app
    path('', include('campus.urls')),
]
