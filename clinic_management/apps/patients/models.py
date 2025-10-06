from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings


class Patient(models.Model):
    """
    Patient model for storing patient information
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    VISIT_TYPE_CHOICES = [
        ('WALKIN', 'Walk-in'),
        ('APPOINTMENT', 'Scheduled Appointment'),
        ('EMERGENCY', 'Emergency'),
        ('FOLLOWUP', 'Follow-up'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('DECEASED', 'Deceased'),
    ]
    
    INSURANCE_PROVIDER_CHOICES = [
        ('NHIF', 'NHIF'),
        ('AAR', 'AAR Insurance'),
        ('BRITAM', 'Britam'),
        ('JUBILEE', 'Jubilee Insurance'),
        ('MADISON', 'Madison Insurance'),
        ('OTHER', 'Other'),
        ('NONE', 'No Insurance'),
    ]
    
    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+254700000000'. Up to 15 digits allowed."
    )
    
    # Basic Information
    patient_id = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        help_text="Auto-generated patient ID"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Contact Information
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17,
        help_text="Format: +254700000000"
    )
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Insurance Information
    insurance_provider = models.CharField(
        max_length=20, 
        choices=INSURANCE_PROVIDER_CHOICES,
        default='NONE'
    )
    insurance_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )
    emergency_contact_relationship = models.CharField(max_length=100, blank=True, null=True)
    
    # Medical Information
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    allergies = models.TextField(
        blank=True, 
        null=True,
        help_text="List of known allergies"
    )
    chronic_conditions = models.TextField(
        blank=True,
        null=True,
        help_text="List of chronic conditions"
    )
    current_medications = models.TextField(
        blank=True,
        null=True,
        help_text="List of current medications"
    )
    
    # Status and Metadata
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    last_visit_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.patient_id} - {self.get_full_name()}"
    
    def get_full_name(self):
        """Return the patient's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        """Calculate patient's age"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate patient_id"""
        if not self.patient_id:
            # Get the last patient ID
            last_patient = Patient.objects.all().order_by('id').last()
            if last_patient and last_patient.patient_id:
                # Extract number from last patient_id (e.g., P-2024-001 -> 1)
                last_id_num = int(last_patient.patient_id.split('-')[-1])
                new_id_num = last_id_num + 1
            else:
                new_id_num = settings.PATIENT_ID_START
            
            # Format: P-2024-001
            from datetime import date
            year = date.today().year
            self.patient_id = f"P-{year}-{new_id_num:03d}"
        
        super().save(*args, **kwargs)


class Visit(models.Model):
    """
    Model to track patient visits
    """
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE,
        related_name='visits'
    )
    visit_type = models.CharField(
        max_length=20,
        choices=Patient.VISIT_TYPE_CHOICES
    )
    visit_date = models.DateTimeField(auto_now_add=True)
    appointment_time = models.TimeField(blank=True, null=True)
    reason_for_visit = models.TextField()
    doctor_assigned = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Status tracking
    checked_in = models.BooleanField(default=False)
    triage_completed = models.BooleanField(default=False)
    consultation_completed = models.BooleanField(default=False)
    lab_completed = models.BooleanField(default=False)
    pharmacy_completed = models.BooleanField(default=False)
    billing_completed = models.BooleanField(default=False)
    visit_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date']
        indexes = [
            models.Index(fields=['patient', '-visit_date']),
            models.Index(fields=['visit_type']),
        ]
    
    def __str__(self):
        return f"Visit {self.id} - {self.patient.get_full_name()} on {self.visit_date.strftime('%Y-%m-%d')}"


class MedicalHistory(models.Model):
    """
    Model to store patient medical history
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_history'
    )
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='medical_records',
        blank=True,
        null=True
    )
    date = models.DateField(auto_now_add=True)
    diagnosis = models.TextField()
    treatment = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Medical histories'
    
    def __str__(self):
        return f"Medical Record - {self.patient.get_full_name()} - {self.date}"