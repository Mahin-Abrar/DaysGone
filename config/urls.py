from django.contrib import admin
from django.urls import include, path

from config.pwa_views import install_guide, service_worker
from config.views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sw.js", service_worker, name="service-worker"),
    path("install/", install_guide, name="install-guide"),
    path("", dashboard, name="dashboard"),
    path("accounts/", include("accounts.urls")),
    path("routines/", include("routines.urls")),
    path("expenses/", include("expenses.urls")),
    path("planner/", include("planner.urls")),
    path("rewards/", include("rewards.urls")),
    path("drafts/", include("drafts.urls")),
]
