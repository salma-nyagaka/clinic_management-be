from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, VisitViewSet, MedicalHistoryViewSet

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'visits', VisitViewSet, basename='visit')
router.register(r'medical-history', MedicalHistoryViewSet, basename='medical-history')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]