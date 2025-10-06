from django.contrib import admin
from .models import Patient, Visit, MedicalHistory


@admin.register(Patient)
class PatientsAdmin(admin.ModelAdmin):
    """
    Admin configuration for Patient model
    """
    list_display = [
        'patient_id',
        'get_full_name',
        'date_of_birth',
        'gender',
        'phone_number',
        'status',
        'registration_date',
    ]
    list_filter = [
        'status',
        'gender',
        'insurance_provider',
        'registration_date',
    ]
    search_fields = [
        'patient_id',
        'first_name',
        'last_name',
        'phone_number',
        'email',
    ]
    readonly_fields = [
        'patient_id',
        'registration_date',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'patient_id',
                'first_name',
                'last_name',
                'date_of_birth',
                'gender',
            )
        }),
        ('Contact Information', {
            'fields': (
                'phone_number',
                'email',
                'address',
            )
        }),
        ('Insurance Information', {
            'fields': (
                'insurance_provider',
                'insurance_number',
            )
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact_name',
                'emergency_contact_phone',
                'emergency_contact_relationship',
            )
        }),
        ('Medical Information', {
            'fields': (
                'blood_group',
                'allergies',
                'chronic_conditions',
                'current_medications',
            )
        }),
        ('Status and Metadata', {
            'fields': (
                'status',
                'registration_date',
                'last_visit_date',
                'notes',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    """
    Admin configuration for Visit model
    """
    list_display = [
        'id',
        'get_patient_name',
        'visit_type',
        'visit_date',
        'checked_in',
        'visit_completed',
    ]
    list_filter = [
        'visit_type',
        'visit_completed',
        'checked_in',
        'visit_date',
    ]
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'patient__patient_id',
        'doctor_assigned',
    ]
    readonly_fields = [
        'visit_date',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Visit Information', {
            'fields': (
                'patient',
                'visit_type',
                'visit_date',
                'appointment_time',
                'reason_for_visit',
                'doctor_assigned',
                'notes',
            )
        }),
        ('Workflow Status', {
            'fields': (
                'checked_in',
                'triage_completed',
                'consultation_completed',
                'lab_completed',
                'pharmacy_completed',
                'billing_completed',
                'visit_completed',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_patient_name(self, obj):
        return obj.patient.get_full_name()
    get_patient_name.short_description = 'Patient Name'


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Medical History model
    """
    list_display = [
        'id',
        'get_patient_name',
        'date',
        'diagnosis',
        'follow_up_date',
    ]
    list_filter = [
        'date',
        'follow_up_date',
    ]
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'patient__patient_id',
        'diagnosis',
        'treatment',
    ]
    readonly_fields = [
        'date',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Patient Information', {
            'fields': (
                'patient',
                'visit',
                'date',
            )
        }),
        ('Medical Details', {
            'fields': (
                'diagnosis',
                'treatment',
                'prescription',
                'doctor_notes',
                'follow_up_date',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_patient_name(self, obj):
        return obj.patient.get_full_name()
    get_patient_name.short_description = 'Patient Name'