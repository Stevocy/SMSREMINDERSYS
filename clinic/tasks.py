from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Appointment, SMSLog
from .sms_service import send_sms
from django.core.management import call_command


@shared_task
def send_appointment_reminders():
    """
    Daily task that sends SMS reminders for appointments scheduled exactly 2 days from today.
    Runs automatically every day at 08:00 EAT (East Africa Time).
    """
    print(f"[REMINDER TASK] Started at {timezone.now()} (EAT)")

    # Calculate the target date: exactly 2 days from today (midnight to midnight)
    today = timezone.localdate()                       # current date in EAT
    target_date = today + timedelta(days=2)

    print(f"[REMINDER TASK] Looking for appointments scheduled on: {target_date}")

    # Find all scheduled appointments on that exact future date
    appointments = Appointment.objects.filter(
        appointment_date__date=target_date,             # exact date match
        status='Scheduled',
        # reminder_sent=False                           # Uncomment after adding field
    ).select_related('patient')

    count = appointments.count()
    print(f"[REMINDER TASK] Found {count} matching appointments on {target_date}")

    if count == 0:
        print("[REMINDER TASK] No appointments found for that date → nothing to send")
        return

    sent_count = 0
    for appt in appointments:
        # Format appointment time nicely for the message
        appt_time = appt.appointment_date.astimezone(timezone.get_current_timezone())
        time_str = appt_time.strftime('%Y-%m-%d %H:%M')

        message = (
            f"Dear {appt.patient.name},\n\n"
            f"This is a friendly reminder from the Antenatal Clinic.\n"
            f"Your appointment is scheduled in 2 days on {time_str}.\n"
            f"Please make sure to attend or contact us if you need to reschedule.\n\n"
            f"Thank you!"
        )

        print(f"[REMINDER TASK] Sending to {appt.patient.phone_number} (Appointment ID {appt.id})")

        success = send_sms(appt.patient.phone_number, message)

        SMSLog.objects.create(
            appointment=appt,
            message_content=message,
            status='Sent' if success else 'Failed',
            phone_number=appt.patient.phone_number,
        )

        print(f"[REMINDER TASK] → {'Success' if success else 'Failed'}")
        sent_count += 1

    print(f"[REMINDER TASK] Completed. Sent {sent_count} messages.")

@shared_task
def daily_anc_sync():
    print("[ANC SYNC] Starting automatic hospital sync...")
    call_command('sync_anc_patients')
    print("[ANC SYNC] Completed!")