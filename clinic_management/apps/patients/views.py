from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Patient, Visit, MedicalHistory
from .serializers import (
    PatientSerializer,
    PatientListSerializer,
    PatientDetailSerializer,
    VisitSerializer,
    MedicalHistorySerializer
)


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Patient model
    Provides CRUD operations and custom actions
    """
    queryset = Patient.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'gender', 'insurance_provider']
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone_number', 'email']
    ordering_fields = ['created_at', 'last_visit_date', 'first_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return PatientListSerializer
        elif self.action == 'retrieve':
            return PatientDetailSerializer
        return PatientSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new patient and optionally create a visit"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()
        
        # If visit data is provided, create a visit
        visit_data = request.data.get('visit')
        if visit_data:
            visit_data['patient'] = patient.id
            visit_serializer = VisitSerializer(data=visit_data)
            if visit_serializer.is_valid():
                visit_serializer.save()
                patient.last_visit_date = timezone.now()
                patient.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    @action(detail=True, methods=['get'])
    def visits(self, request, pk=None):
        """Get all visits for a patient"""
        patient = self.get_object()
        visits = patient.visits.all()
        serializer = VisitSerializer(visits, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def medical_history(self, request, pk=None):
        """Get medical history for a patient"""
        patient = self.get_object()
        history = patient.medical_history.all()
        serializer = MedicalHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in a patient for a visit"""
        patient = self.get_object()
        
        # Create a new visit
        visit_data = {
            'patient': patient.id,
            'visit_type': request.data.get('visit_type', 'WALKIN'),
            'reason_for_visit': request.data.get('reason_for_visit', 'General consultation'),
            'checked_in': True
        }
        
        visit_serializer = VisitSerializer(data=visit_data)
        if visit_serializer.is_valid():
            visit = visit_serializer.save()
            patient.last_visit_date = timezone.now()
            patient.save()
            
            return Response({
                'message': 'Patient checked in successfully',
                'visit': visit_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(visit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get patient statistics"""
        total_patients = Patient.objects.count()
        active_patients = Patient.objects.filter(status='ACTIVE').count()
        inactive_patients = Patient.objects.filter(status='INACTIVE').count()
        
        # Recent registrations (last 30 days)
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_registrations = Patient.objects.filter(
            registration_date__gte=thirty_days_ago
        ).count()
        
        return Response({
            'total_patients': total_patients,
            'active_patients': active_patients,
            'inactive_patients': inactive_patients,
            'recent_registrations': recent_registrations,
            'gender_distribution': {
                'male': Patient.objects.filter(gender='M').count(),
                'female': Patient.objects.filter(gender='F').count(),
                'other': Patient.objects.filter(gender='O').count(),
            }
        })


class VisitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Visit model
    """
    queryset = Visit.objects.all()
    serializer_class = VisitSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'visit_type', 'visit_completed']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    ordering_fields = ['visit_date', 'created_at']
    ordering = ['-visit_date']
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update visit workflow status"""
        visit = self.get_object()
        
        # Update status fields
        status_field = request.data.get('status_field')
        status_value = request.data.get('status_value', True)
        
        if status_field in ['checked_in', 'triage_completed', 'consultation_completed', 
                           'lab_completed', 'pharmacy_completed', 'billing_completed']:
            setattr(visit, status_field, status_value)
            
            # Auto-complete visit if all stages are done
            if all([
                visit.checked_in,
                visit.triage_completed,
                visit.consultation_completed,
                visit.billing_completed
            ]):
                visit.visit_completed = True
            
            visit.save()
            serializer = self.get_serializer(visit)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Invalid status field'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def today_visits(self, request):
        """Get all visits for today"""
        from datetime import date
        today = date.today()
        visits = Visit.objects.filter(visit_date__date=today)
        serializer = self.get_serializer(visits, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_visits(self, request):
        """Get all active (incomplete) visits"""
        visits = Visit.objects.filter(visit_completed=False)
        serializer = self.get_serializer(visits, many=True)
        return Response(serializer.data)


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Medical History model
    """
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'visit']
    search_fields = ['patient__first_name', 'patient__last_name', 'diagnosis']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Get medical history for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response(
                {'error': 'patient_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = MedicalHistory.objects.filter(patient_id=patient_id)
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)