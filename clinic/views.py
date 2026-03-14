import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from .models import Patient, Appointment, Attendance, SMSLog
from .forms import PatientForm, AppointmentForm


# ── Auth ────────────────────────────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. Welcome!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})







# ── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    total_patients = Patient.objects.count()
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=timezone.now(),
        status='Scheduled'
    ).order_by('appointment_date')[:5]

    total_scheduled = Appointment.objects.filter(status='Scheduled').count()
    total_completed = Appointment.objects.filter(status='Completed').count()
    total_missed = Appointment.objects.filter(status='Missed').count()
    sms_sent = SMSLog.objects.filter(status='Sent').count()
    sms_failed = SMSLog.objects.filter(status='Failed').count()

    context = {
        'total_patients': total_patients,
        'upcoming_appointments': upcoming_appointments,
        'total_scheduled': total_scheduled,
        'total_completed': total_completed,
        'total_missed': total_missed,
        'sms_sent': sms_sent,
        'sms_failed': sms_failed,
    }
    return render(request, 'dashboard.html', context)


# ── Patient (Mother Enrolment) ─────────────────────────────────────────────

@login_required
def patient_list(request):
    patients = Patient.objects.all().order_by('name')
    return render(request, 'patient_list.html', {'patients': patients})


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    appointments = patient.appointments.all().order_by('-appointment_date')
    return render(request, 'patient_detail.html', {'patient': patient, 'appointments': appointments})


@login_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient registered successfully.")
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'patient_form.html', {'form': form, 'action': 'Register'})


@login_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"Patient '{patient.name}' updated successfully.")
            return redirect('patient_list')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patient_form.html', {'form': form, 'action': 'Edit', 'patient': patient})


@staff_member_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        name = patient.name
        patient.delete()
        messages.success(request, f"Patient '{name}' deleted.")
        return redirect('patient_list')
    return render(request, 'patient_confirm_delete.html', {'patient': patient})


# ── Appointments ─────────────────────────────────────────────────────────────

@login_required
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-appointment_date').select_related('patient')
    return render(request, 'appointment_list.html', {'appointments': appointments})


@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment scheduled successfully.")
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'appointment_form.html', {'form': form, 'action': 'Schedule'})


@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated.")
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointment_form.html', {'form': form, 'action': 'Edit', 'appointment': appointment})


@login_required
def appointment_complete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'Completed'
    appointment.save()
    # Record attendance as Attended
    Attendance.objects.update_or_create(
        appointment=appointment,
        defaults={'status': 'Attended'}
    )
    messages.success(request, f"Appointment marked as completed.")
    return redirect('appointment_list')


@staff_member_required
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, "Appointment cancelled.")
        return redirect('appointment_list')
    return render(request, 'appointment_confirm_cancel.html', {'appointment': appointment})


@login_required
def appointment_miss(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'Missed'
    appointment.save()
    Attendance.objects.update_or_create(
        appointment=appointment,
        defaults={'status': 'Missed'}
    )
    messages.warning(request, "Appointment marked as missed.")
    return redirect('appointment_list')


# ── Attendance ────────────────────────────────────────────────────────────────

@login_required
def attendance_list(request):
    records = Attendance.objects.all().order_by('-recorded_at').select_related(
        'appointment__patient'
    )
    return render(request, 'attendance_list.html', {'records': records})


@login_required
def record_attendance(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        if status in ('Attended', 'Missed'):
            Attendance.objects.update_or_create(
                appointment=appointment,
                defaults={'status': status, 'notes': notes}
            )
            appointment.status = 'Completed' if status == 'Attended' else 'Missed'
            appointment.save()
            messages.success(request, f"Attendance recorded: {status}.")
        return redirect('attendance_list')
    return render(request, 'record_attendance.html', {'appointment': appointment})


# ── SMS Logs ──────────────────────────────────────────────────────────────────

@login_required
def sms_log_list(request):
    logs = SMSLog.objects.all().order_by('-sent_at').select_related('appointment__patient')
    return render(request, 'sms_log_list.html', {'logs': logs})


# ── Send SMS to Patient ─────────────────────────────────────────────────────

@login_required
def send_sms_to_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        custom_message = request.POST.get('message', '').strip()
        if not custom_message:
            custom_message = (
                f"Dear {patient.name}, this is a reminder from the Antenatal Clinic. "
                f"Please ensure you attend all your scheduled clinic visits. "
                f"Contact us if you need to reschedule."
            )
        from .sms_service import send_sms
        success = send_sms(patient.phone_number, custom_message)

        # Log it — link to the most recent upcoming appointment if available
        appointment = patient.appointments.filter(status='Scheduled').order_by('appointment_date').first()
        if appointment:
            SMSLog.objects.create(
                appointment=appointment,
                message_content=custom_message,
                status='Sent' if success else 'Failed',
                phone_number=patient.phone_number,
            )

        if success:
            messages.success(request, f"SMS sent successfully to {patient.name} ({patient.phone_number}).")
        else:
            messages.error(request, f"Failed to send SMS to {patient.name}. Check the phone number format.")
        return redirect('patient_detail', pk=pk)
    return render(request, 'send_sms_patient.html', {'patient': patient})

    
# ── Reports ───────────────────────────────────────────────────────────────────

@login_required
def reports(request):
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    total_completed = Appointment.objects.filter(status='Completed').count()
    total_missed = Appointment.objects.filter(status='Missed').count()
    total_scheduled = Appointment.objects.filter(status='Scheduled').count()
    total_cancelled = Appointment.objects.filter(status='Cancelled').count()
    sms_sent = SMSLog.objects.filter(status='Sent').count()
    sms_failed = SMSLog.objects.filter(status='Failed').count()

    attendance_rate = 0
    finished = total_completed + total_missed
    if finished > 0:
        attendance_rate = round((total_completed / finished) * 100, 1)

    recent_logs = SMSLog.objects.order_by('-sent_at')[:10].select_related('appointment__patient')

    context = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_completed': total_completed,
        'total_missed': total_missed,
        'total_scheduled': total_scheduled,
        'total_cancelled': total_cancelled,
        'sms_sent': sms_sent,
        'sms_failed': sms_failed,
        'attendance_rate': attendance_rate,
        'recent_logs': recent_logs,
    }
    return render(request, 'reports.html', context)


@staff_member_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="appointments_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Patient Name', 'Phone Number', 'ID Number',
        'Appointment Date', 'Status', 'Attendance Status',
        'SMS Sent', 'Notes'
    ])

    appointments = Appointment.objects.select_related('patient').prefetch_related(
        'attendance', 'sms_logs'
    ).order_by('-appointment_date')

    for appt in appointments:
        attendance_status = ''
        try:
            attendance_status = appt.attendance.status
        except Attendance.DoesNotExist:
            pass

        sms_status = appt.sms_logs.filter(status='Sent').exists()

        writer.writerow([
            appt.patient.name,
            appt.patient.phone_number,
            appt.patient.id_number,
            appt.appointment_date.strftime('%Y-%m-%d %H:%M'),
            appt.status,
            attendance_status,
            'Yes' if sms_status else 'No',
            appt.notes or '',
        ])

    return response


from django.http import JsonResponse
from .sms import send_bulk_sms



def test_bulk_sms(request):

    numbers = [
        "+254700000001"
    ]

    message = "Hello from Django using Africa's Talking Sandbox"

    response = send_bulk_sms(numbers, message)

    return JsonResponse(response, safe=False)