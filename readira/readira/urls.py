"""
URL configuration for readira project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language
from library.views import MainPage, search_view
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout


def redirect_to_user_language(request):
    lang = request.COOKIES.get('django_language', 'en')
    return HttpResponseRedirect(f'/{lang}/')
    

urlpatterns = [
    path('', MainPage.as_view(), name='main_page'),
    path('set_language/', set_language, name = 'set_language'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns +=i18n_patterns (
    path('admin/', admin.site.urls),
    path('library/', include('library.urls', namespace='library')),
    path('user/', include('user_account.urls', namespace='user_account')),
    path('search/', search_view, name='search'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root= settings.STATIC_ROOT)
