from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('caseflow-admin/', admin.site.urls),
    path('api/user/', include('user.urls')),
    path('api/activeclaim/', include('activeclaim.urls')),
    path('api/completeclaim/', include('completeclaim.urls')),
    path('api/reviewedclaim/', include('reviewedclaim.urls')),
    path('api/parentcase/', include('parentcase.urls'))
]

# Serve static CSS for admin page
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)