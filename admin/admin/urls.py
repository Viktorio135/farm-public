from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('panel/', include('panel.urls')),
    path('api/', include('api.urls')),
    # Стандартная форма входа Django
    path('login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    # Стандартная форма выхода Django
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)