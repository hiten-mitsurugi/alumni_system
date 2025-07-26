from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def api_root(request):
    return JsonResponse({"message": "Welcome to the Alumni Management System API"})

urlpatterns = [
    path('', api_root),  # 👈 Root path responds with JSON
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
