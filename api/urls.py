from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('caseflow-admin/', admin.site.urls),
    path('api/ping/', include('ping.urls')),
    path('api/user/', include('user.urls')),
    path('api/activeclaim/', include('activeclaim.urls')),
    path('api/completeclaim/', include('completeclaim.urls')),
    path('api/reviewedclaim/', include('reviewedclaim.urls')),
    path('api/parentcase/', include('parentcase.urls'))
]
