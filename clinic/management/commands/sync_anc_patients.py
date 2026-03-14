from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db import connections
from clinic.models import Patient, Appointment   # your models

class Command(BaseCommand):
    help = 'Sync ANC patients and visit dates from hospital database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting ANC sync from hospital database...'))

        with connections['hospital'].cursor() as cursor:
            # ←←← CUSTOMIZE THIS QUERY WITH YOUR HOSPITAL TABLE NAMES ←←←
            cursor.execute("""
                SELECT 
                    p.id_number, 
                    p.name, 
                    p.phone_number, 
                    v.visit_date,
                    v.visit_type
                FROM patients p
                JOIN anc_visits v ON p.id = v.patient_id
                WHERE v.visit_date >= %s 
                  AND v.status = 'Scheduled'
                ORDER BY v.visit_date
            """, [timezone.now().date()])

            rows = cursor.fetchall()

            created_count = 0
            updated_count = 0

            for row in rows:
                id_number, name, phone, visit_date, visit_type = row

                # 1. Get or create Patient
                patient, patient_created = Patient.objects.get_or_create(
                    id_number=id_number,
                    defaults={
                        'name': name,
                        'phone_number': phone or '',
                    }
                )
                if patient_created:
                    self.stdout.write(f"→ New patient created: {name}")

                # 2. Create Appointment if it doesn't already exist for this date
                appointment, appt_created = Appointment.objects.get_or_create(
                    patient=patient,
                    appointment_date=visit_date,
                    defaults={
                        'status': 'Scheduled',
                        'notes': f"Auto-synced ANC visit - {visit_type or 'Routine'}"
                    }
                )

                if appt_created:
                    created_count += 1
                    self.stdout.write(f"✓ Appointment created for {name} on {visit_date.date()}")
                else:
                    updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"Sync completed! New patients: {created_count} | Appointments: {created_count + updated_count}"
            ))