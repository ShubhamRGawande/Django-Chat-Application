from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect  # ✅ Add this import

urlpatterns = [
    path('', lambda request: redirect('login/', permanent=False)),  # Redirect root to login page
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='chat/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
