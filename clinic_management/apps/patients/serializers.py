from rest_framework import serializers
from .models import Patient, Visit, MedicalHistory


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient model
    """
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'patient_id',
            'first_name',
            'last_name',
            'full_name',
            'date_of_birth',
            'age',
            'gender',
            'phone_number',
            'email',
            'address',
            'insurance_provider',
            'insurance_number',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'blood_group',
            'allergies',
            'chronic_conditions',
            'current_medications',
            'status',
            'registration_date',
            'last_visit_date',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'patient_id', 'registration_date', 'created_at', 'updated_at']
    
    def get_age(self, obj):
        """Calculate and return patient's age"""
        return obj.get_age()
    
    def get_full_name(self, obj):
        """Return patient's full name"""
        return obj.get_full_name()
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with country code (e.g., +254)")
        return value


class PatientListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for patient list view
    """
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'patient_id',
            'full_name',
            'age',
            'gender',
            'phone_number',
            'status',
            'last_visit_date',
        ]
    
    def get_age(self, obj):
        return obj.get_age()
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class VisitSerializer(serializers.ModelSerializer):
    """
    Serializer for Visit model
    """
    patient_name = serializers.SerializerMethodField()
    patient_id_number = serializers.SerializerMethodField()
    
    class Meta:
        model = Visit
        fields = [
            'id',
            'patient',
            'patient_name',
            'patient_id_number',
            'visit_type',
            'visit_date',
            'appointment_time',
            'reason_for_visit',
            'doctor_assigned',
            'notes',
            'checked_in',
            'triage_completed',
            'consultation_completed',
            'lab_completed',
            'pharmacy_completed',
            'billing_completed',
            'visit_completed',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'visit_date', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        """Return patient's full name"""
        return obj.patient.get_full_name()
    
    def get_patient_id_number(self, obj):
        """Return patient ID"""
        return obj.patient.patient_id


class MedicalHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for Medical History model
    """
    patient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalHistory
        fields = [
            'id',
            'patient',
            'patient_name',
            'visit',
            'date',
            'diagnosis',
            'treatment',
            'prescription',
            'doctor_notes',
            'follow_up_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'date', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        """Return patient's full name"""
        return obj.patient.get_full_name()


class PatientDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer with related data
    """
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    visits = VisitSerializer(many=True, read_only=True)
    medical_history = MedicalHistorySerializer(many=True, read_only=True)
    total_visits = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'patient_id',
            'first_name',
            'last_name',
            'full_name',
            'date_of_birth',
            'age',
            'gender',
            'phone_number',
            'email',
            'address',
            'insurance_provider',
            'insurance_number',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'blood_group',
            'allergies',
            'chronic_conditions',
            'current_medications',
            'status',
            'registration_date',
            'last_visit_date',
            'notes',
            'total_visits',
            'visits',
            'medical_history',
            'created_at',
            'updated_at',
        ]
    
    def get_age(self, obj):
        return obj.get_age()
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_total_visits(self, obj):
        """Return total number of visits"""
        return obj.visits.count()