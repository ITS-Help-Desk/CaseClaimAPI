from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/ping/', include('ping.urls')),
    path('api/activeclaim/', include('activeclaim.urls')),
    path('api/completeclaim/', include('completeclaim.urls')),
    path('api/reviewedclaim/', include('reviewedclaim.urls'))
]
