from rest_framework.routers import DefaultRouter
from .views import (
    VendorAccessViewSet,
    VendorDeleteViewSet,
    VendorStatsViewSet,
    VendorVisitCreateViewSet,
    VendorViewSet,
)
from .dashboard_views import ProductVendorDashboardViewSet, VendorDashboardViewSet

router = DefaultRouter()
router.register(r"products", ProductVendorDashboardViewSet, basename="vendors-products")
router.register(r"delete", VendorDeleteViewSet, basename="vendors-delete")
# TODO: To remove
router.register(r"visits", VendorVisitCreateViewSet, basename="vendors-visits")
router.register(r"stats", VendorStatsViewSet, basename="vendors-stats")
router.register(r"access", VendorAccessViewSet, basename="vendors-access")
router.register(r"dashboard", VendorDashboardViewSet, basename="vendors-stats")
router.register(r"", VendorViewSet, basename="vendors")
urlpatterns = router.urls
