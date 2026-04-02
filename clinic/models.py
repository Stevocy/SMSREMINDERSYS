from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    id_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    registration_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField()
    address = models.CharField(max_length=200, blank=True, null=True)
    gestational_age_weeks = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Missed', 'Missed'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.name} - {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"
    reminder_sent = models.BooleanField(default=False)

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Attended', 'Attended'),
        ('Missed', 'Missed'),
    ]

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='attendance')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.appointment.patient.name} - {self.status}"


class SMSLog(models.Model):
    STATUS_CHOICES = [
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='sms_logs')
    sent_at = models.DateTimeField(auto_now_add=True)
    message_content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"SMS to {self.appointment.patient.name} - {self.status} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"


class Notification(models.Model):
    TYPES = [
        ('check_in', 'Patient Check-In'),
        ('appointment', 'Appointment Update'),
        ('system', 'System'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPES, default='check_in')
    title = models.CharField(max_length=200)
    message = models.TextField()
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.recipient.username} ({'Read' if self.is_read else 'Unread'})"
