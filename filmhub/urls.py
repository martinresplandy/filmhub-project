from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static

from api.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),

    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),

    re_path(r'^(?:.*)/?$', index),
]