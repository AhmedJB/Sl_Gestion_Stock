from django.urls import path, include
from rest_framework import routers
from .views import (
    FiscalYearViewSet,
    StockSnapshotViewSet,
    AccountingInvoiceViewSet,
    PaymentViewSet,
    AccountingStatsView,
)

router = routers.SimpleRouter()
router.register('fiscal-years', FiscalYearViewSet, basename='fiscal-year')
router.register('snapshots', StockSnapshotViewSet, basename='stock-snapshot')
router.register('invoices', AccountingInvoiceViewSet, basename='accounting-invoice')
router.register('payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', AccountingStatsView.as_view(), name='accounting-stats'),
]
