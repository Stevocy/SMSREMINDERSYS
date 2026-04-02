from django import forms
from .models import Patient, Appointment

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'name', 'phone_number', 'id_number',
            'date_of_birth', 'expected_delivery_date',
            'address', 'gestational_age_weeks'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }


def clean_phone_number(self):
    phone = self.cleaned_data.get('phone_number')

    if not phone:
        return phone

    # Remove spaces and dashes
    phone = phone.replace(" ", "").replace("-", "")

    # Convert Kenyan formats to E.164
    if phone.startswith("0"):
        phone = "+254" + phone[1:]
    elif phone.startswith("254"):
        phone = "+" + phone
    elif phone.startswith("7") and len(phone) == 9:
        phone = "+254" + phone
    elif phone.startswith("+254"):
        pass
    else:
        raise forms.ValidationError(
            "Enter a valid Kenyan phone number (e.g. 0712345678)"
        )

    # Final validation
    if not phone[1:].isdigit():
        raise forms.ValidationError("Phone number must contain digits only.")

    if len(phone) != 13:
        raise forms.ValidationError("Invalid Kenyan phone number.")

    return phone

class AppointmentForm(forms.ModelForm):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all().order_by('name'),
        empty_label="--- Select Patient ---",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'appointment_date', 'notes']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
