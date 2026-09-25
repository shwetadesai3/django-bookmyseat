
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import login_view
from django.shortcuts import render


def contact(request):
    return render(request, 'contact.html')


urlpatterns = [
    path('', login_view, name='home'),

    path('admin/', admin.site.urls),

    path('users/', include('users.urls')),

    path('movies/', include('movies.urls')),

    path('contact/', contact, name='contact'),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )